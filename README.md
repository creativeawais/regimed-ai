# RegiMed MVP

This repository contains a simple proof‑of‑concept for the **RegiMed** Minimum Viable Product (MVP).  
It follows the high‑level outline described in the accompanying PDF.  

The goal of this project is to provide a small, working demonstration of how an automated compliance checker for medical documents might be built.  
The system consists of three main components:

1. **Regulation scraper (`scraper.py`)** – a script that downloads HIPAA regulation pages from the Health and Human Services (HHS) website and stores the plain‑text content to a JSON file.  
   This script runs periodically (e.g. via a cron job or GitHub Action) to keep the local copy of regulations up to date.
2. **Document comparison library (`compare.py`)** – utility functions to load a list of compliance rules and compare them against uploaded documents.  
   The comparison logic is deliberately simple to make the MVP easy to understand: each rule from `rules.txt` is searched within the uploaded document, and the results are aggregated into a compliance report.
3. **Backend API (`app.py`)** – a FastAPI application that exposes endpoints for uploading documents, retrieving the current compliance rules, and reading the scraped regulations.  
   Uploaded files can be either PDFs or plain‑text.  PDFs are parsed into text using the `PyMuPDF` library.  The API returns a JSON response summarising which rules were found and which were missing.

## Getting Started

1. Create a Python virtual environment and install the required packages:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Populate the `rules.txt` file with the clauses you want to check.  A few example HIPAA statements are provided by default.

3. Run the regulation scraper to download the latest HIPAA rules:

   ```bash
   python scraper.py
   ```

   This command fetches the contents of several HHS web pages and writes them into a JSON file called `regulations.json`.  You can adjust the list of URLs inside `scraper.py` as needed.

4. Start the FastAPI application:

   ```bash
   uvicorn app:app --reload
   ```

   With the server running, you can POST a document to the `/upload` endpoint using `curl` or any HTTP client.  The server returns a JSON report showing which compliance rules were satisfied and which were missing.

## File Overview

| File | Purpose |
|------|---------|
| `rules.txt` | A list of compliance clauses to search for in uploaded documents. Each line represents one rule. |
| `scraper.py` | Downloads HIPAA regulation pages and saves the text content to `regulations.json`. |
| `compare.py` | Utility functions to load rules and compare them against document text using simple string matching. |
| `app.py` | FastAPI application exposing endpoints to upload documents, list rules, and read scraped regulations. |
| `requirements.txt` | Python dependency list needed to run the project. |
| `regulations.json` | (Generated) JSON file containing the scraped content from the HIPAA pages. |

## Limitations

This MVP is intentionally lightweight and omits many features you would expect in a production system:

- **Authentication and user management** – there is no login system.  In practice you would integrate Firebase Auth or another identity provider.
- **Advanced comparison logic** – real compliance checking typically requires natural‑language processing and contextual understanding.  This example uses simple substring checks to keep the demonstration easy to follow.
- **Database storage** – the scraped regulations are saved to a local JSON file.  A production implementation could store this data in a cloud database (e.g. Firebase or MongoDB Atlas).
- **Frontend** – there is no web UI in this repository.  For the MVP, you can use tools like React with Vercel or Bubble.io to build a user interface that consumes the API defined in `app.py`.

Despite these simplifications, the code here forms a solid foundation for further development and demonstrates how the various components of the MVP fit together.
