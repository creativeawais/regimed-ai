"""
🤖 RegiMed AI - HIPAA Auto Scraper

Yeh script automatically U.S. government ki HIPAA privacy aur security pages ko download karta hai,
unka plain text extract karta hai, aur ek JSON file (`regulations.json`) me save karta hai.

Yeh automation tools ke sath schedule par chal sakta hai:
- GitHub Actions (har 6 ghantay)
- Local cron jobs
- Cloud Functions

📁 Output:
  regulations.json file jisme har scraped page ka URL aur uska plain text hoga:
  
  [
    {
      "url": "https://example.com",
      "content": "Extracted plain text..."
    },
    ...
  ]

🚀 Run karne ka tareeqa:
    python scraper.py
"""

from __future__ import annotations
import json
import logging
from typing import List, Dict
import requests
from bs4 import BeautifulSoup

# 🎯 URLs jahan se HIPAA rules scrape karne hain
HIPAA_URLS: List[str] = [
    "https://www.hhs.gov/hipaa/for-professionals/privacy/index.html",
    "https://www.hhs.gov/hipaa/for-professionals/security/guidance/index.html",
]

def fetch_page(url: str, timeout: int = 10) -> str | None:
    """Ek URL se HTML page download karta hai"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text
    except Exception as exc:
        logging.warning("❌ Failed to fetch %s: %s", url, exc)
        return None

def extract_text(html: str) -> str:
    """HTML content me se readable plain text nikaalta hai"""
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    return " ".join(text.split())

def scrape() -> List[Dict[str, str]]:
    """Saare URLs se data scrape karta hai"""
    entries: List[Dict[str, str]] = []
    for url in HIPAA_URLS:
        html = fetch_page(url)
        if html is None:
            continue
        text = extract_text(html)
        entries.append({"url": url, "content": text})
    return entries

def save(entries: List[Dict[str, str]], path: str = "regulations.json") -> None:
    """Extracted data ko JSON file me save karta hai"""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

def main() -> None:
    """Program ka entry point"""
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    logging.info("🚀 Starting HIPAA regulations scraper…")
    entries = scrape()
    if entries:
        save(entries)
        logging.info("✅ Scraped %d pages and saved to regulations.json", len(entries))
    else:
        logging.warning("⚠️ No pages scraped; nothing saved.")

if __name__ == "__main__":
    main()
