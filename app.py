"""
FastAPI backend for the RegiMed MVP.

This application exposes a minimal API allowing clients to:

1. Upload a medical document (PDF or plain‑text) to check it against a set of
   compliance rules defined in `rules.txt`.  The `/upload` endpoint returns
   a JSON report detailing which rules were found and which were missing.
2. Retrieve the current list of rules via the `/rules` endpoint.
3. Read the latest scraped HIPAA regulations from `regulations.json` via
   the `/regulations` endpoint.

To run the server locally, install the dependencies listed in
`requirements.txt` and start the application with uvicorn:

    uvicorn app:app --reload

During development you can experiment with the API using tools like curl or
Postman.  For example, to upload a file:

    curl -X POST -F "file=@path/to/document.pdf" http://localhost:8000/upload

Note: This application is intentionally simplified to demonstrate core
concepts.  In a production environment you would add authentication,
input validation, error handling, logging and possibly integrate more
sophisticated NLP models.
"""

from __future__ import annotations

import os
from typing import List, Dict, Any

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

import fitz  # PyMuPDF

# Import comparison utilities.  When this module is executed from within the
# package (e.g. via `uvicorn regimed_mvp_project.app:app`), relative imports
# will succeed.  When run as a standalone script (e.g. `python app.py`),
# fallback to absolute imports.
try:
    from .compare import load_rules, check_rules, summarize_missing  # type: ignore[import-not-found]
except ImportError:
    from compare import load_rules, check_rules, summarize_missing


app = FastAPI(title="RegiMed MVP API", description="Minimal API for HIPAA compliance checking", version="0.1.0")


def extract_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file given its bytes.

    Parameters
    ----------
    file_bytes : bytes
        Raw bytes of the PDF file.

    Returns
    -------
    str
        The concatenated text of all pages in the PDF.
    """
    text = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text


@app.get("/rules", response_model=List[str])
async def get_rules() -> List[str]:
    """Return the list of compliance rules currently defined in `rules.txt`."""
    rules_path = os.environ.get("REGIMED_RULES_FILE", os.path.join(os.path.dirname(__file__), "rules.txt"))
    rules = load_rules(rules_path)
    return rules


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> JSONResponse:
    """Accept a PDF or plain‑text document and return a compliance report.

    Parameters
    ----------
    file : UploadFile
        The uploaded document.  Must be a `.pdf` or `.txt` file.  PDFs are
        parsed using PyMuPDF; plain‑text files are read directly.

    Returns
    -------
    JSONResponse
        A JSON object summarising which rules were found and which were
        missing.  Includes a boolean `compliant` flag.
    """
    filename = file.filename or ""
    extension = os.path.splitext(filename)[-1].lower()
    if extension not in {".pdf", ".txt"}:
        raise HTTPException(status_code=400, detail="Only .pdf and .txt files are supported")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    # Extract text depending on file type
    if extension == ".pdf":
        try:
            text = extract_pdf(file_bytes)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Could not parse PDF: {exc}")
    else:
        # decode as UTF‑8; ignore errors to avoid raising for binary bytes in text file
        try:
            text = file_bytes.decode("utf-8", errors="ignore")
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Could not read text file: {exc}")

    # Load rules and check against document text
    rules_path = os.environ.get("REGIMED_RULES_FILE", os.path.join(os.path.dirname(__file__), "rules.txt"))
    rules = load_rules(rules_path)
    results = check_rules(text, rules)
    missing = summarize_missing(results)
    response: Dict[str, Any] = {
        "filename": filename,
        "total_rules": len(rules),
        "rules_found": len(rules) - len(missing),
        "rules_missing": len(missing),
        "missing_rules": missing,
        "details": results,
        "compliant": len(missing) == 0,
    }
    return JSONResponse(content=response)


@app.get("/regulations")
async def get_regulations() -> JSONResponse:
    """Return the scraped HIPAA regulation pages stored in `regulations.json`.

    The scraper script writes a JSON array with entries containing `url`
    and `content`.  This endpoint simply reads the file and returns it
    directly.  If the file does not exist, an empty array is returned.
    """
    path = os.environ.get("REGIMED_REGULATIONS_FILE", os.path.join(os.path.dirname(__file__), "regulations.json"))
    if not os.path.exists(path):
        return JSONResponse(content=[])
    try:
        import json
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return JSONResponse(content=data)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Could not read regulations file: {exc}")
