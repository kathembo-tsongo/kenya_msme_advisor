"""
scrape_microfinance.py
Fetches KWFT, Faulu and SMEP loan product content from official websites.
Run:  python3 scrape_microfinance.py
"""

import urllib.request
import re
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "documents"
DOCS_DIR.mkdir(exist_ok=True)

SOURCES = {
    "kwft_about_products.txt":
        "https://kwftbank.com/",
    "kwft_loan_products.txt":
        "https://kwftbank.com/personal/loans/",
    "kwft_business_loans.txt":
        "https://kwftbank.com/business/",
    "faulu_about.txt":
        "https://www.faulukenya.com/about-us",
    "faulu_msme_banking.txt":
        "https://www.faulukenya.com/",
    "faulu_biashara_sme_loan.txt":
        "https://www.faulukenya.com/business-banking/biashara-SME-loan/",
    "faulu_micro_unsecured_loan.txt":
        "https://www.faulukenya.com/business-banking/faulu-micro-unsecured-loan/",
    "faulu_micro_secured_loan.txt":
        "https://www.faulukenya.com/business-banking/faulu-micro-secured-loan/",
    "faulu_women_products.txt":
        "https://www.faulukenya.com/about-us/media/faulu-bank-expands-its-customized-financial-solutions-to-empower-women-in-kenya/",
    "smep_about.txt":
        "https://smep.co.ke/about-us",
    "smep_loan_products.txt":
        "https://www.smep.co.ke/loan",
    "smep_sme_loans.txt":
        "https://smep.co.ke/sme-loans",
    "smep_business_products.txt":
        "https://smep.co.ke/for-your-business",
    "smep_trade_finance.txt":
        "https://smep.co.ke/trade_finance/loan",
    "microfinance_banks_kenya_2024.txt":
        "https://www.businessradar.co.ke/blog/2024/10/18/full-list-of-all-licensed-microfinance-banks-in-kenya/",
}

headers = {"User-Agent": "Mozilla/5.0 (compatible; research bot)"}

def clean_text(html):
    text = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    for ent, rep in [('&nbsp;',' '),('&amp;','&'),('&lt;','<'),('&gt;','>')]:
        text = text.replace(ent, rep)
    text = re.sub(r'\s+', ' ', text)
    lines = [l.strip() for l in text.split('.') if len(l.strip()) > 30]
    return '\n'.join(lines)

print("=" * 60)
print("  Microfinance Institutions Scraper")
print("=" * 60)

success, failed = 0, 0
for filename, url in SOURCES.items():
    print(f"\n  Fetching: {filename} ...", end=" ", flush=True)
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        text = clean_text(html)
        if len(text) < 200:
            print(f"⚠  Too short ({len(text)} chars), skipped")
            failed += 1
            continue
        out = DOCS_DIR / filename
        out.write_text(f"SOURCE: {url}\n\n{text}", encoding="utf-8")
        print(f"✓  ({len(text):,} chars)")
        success += 1
    except Exception as e:
        print(f"✗  {e}")
        failed += 1

print(f"\n{'='*60}")
print(f"  Done: {success} saved, {failed} failed")
print(f"  Now run: python3 src/ingest.py")
