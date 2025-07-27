"""
Utility functions for loading compliance rules and comparing them against
the contents of uploaded medical documents.  The comparison logic in this
module deliberately errs on the side of simplicity: each rule is searched
within the document text, and a basic similarity ratio is calculated using
Python's built‑in `difflib` module.  This approach is meant for a minimal
viable product and should be replaced with more robust NLP techniques in
future iterations (e.g. spaCy, HuggingFace transformers or GPT models).
"""

from __future__ import annotations

from typing import Iterable, List, Dict, Any
import difflib

def load_rules(path: str = "rules.txt") -> List[str]:
    """Load compliance rules from a plain‑text file.

    Each non‑empty line in the file represents a separate rule.  Leading
    and trailing whitespace is stripped.

    Parameters
    ----------
    path : str
        Path to the rules file.

    Returns
    -------
    List[str]
        A list of rule strings.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            rules = [line.strip() for line in f.readlines() if line.strip()]
        return rules
    except FileNotFoundError:
        # If the file is missing, return an empty list rather than raising
        return []


def check_rules(text: str, rules: Iterable[str], threshold: float = 0.5) -> List[Dict[str, Any]]:
    """Check whether each rule appears in the given document text.

    A rule is considered **found** if either the rule (lowercased) is a
    substring of the document (lowercased), or the quick similarity ratio
    computed by `difflib.SequenceMatcher` exceeds the supplied threshold.
    
    Parameters
    ----------
    text : str
        The text of the uploaded document to analyse.
    rules : Iterable[str]
        A sequence of compliance rules to search for.
    threshold : float, optional
        Minimum similarity ratio for a rule to be considered present if
        substring matching fails.  Values range from 0 to 1.  Higher
        values require a closer match.  Defaults to 0.5.

    Returns
    -------
    List[Dict[str, Any]]
        A list of dictionaries, each containing the original rule, a
        boolean indicating whether it was found, and the similarity score.
    """
    text_lower = text.lower()
    results: List[Dict[str, Any]] = []
    for rule in rules:
        rule_lower = rule.lower()
        ratio = difflib.SequenceMatcher(None, rule_lower, text_lower).quick_ratio()
        found = (rule_lower in text_lower) or (ratio >= threshold)
        results.append({
            "rule": rule,
            "found": found,
            "similarity": ratio,
        })
    return results


def summarize_missing(results: Iterable[Dict[str, Any]]) -> List[str]:
    """Extract a list of rules that were not found in the document.

    Parameters
    ----------
    results : Iterable[Dict[str, Any]]
        The result dictionaries returned by `check_rules`.

    Returns
    -------
    List[str]
        A list of rule strings that were not found.
    """
    missing: List[str] = []
    for result in results:
        if not result.get("found"):
            missing.append(result.get("rule", ""))
    return missing
