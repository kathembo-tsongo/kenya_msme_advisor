"""
scrape_sector_regulations.py
Fetches sector-specific regulatory content from official Kenyan websites.
Run:  python3 scrape_sector_regulations.py
"""

import urllib.request
import re
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "documents"
DOCS_DIR.mkdir(exist_ok=True)

SOURCES = {
    "kebs_food_safety_management.txt":
        "https://kebs.org/fsms/",
    "ppb_premises_licensing_guide.txt":
        "https://web.pharmacyboardkenya.org/download/guidelines-for-registration-and-licensing-of-premises/",
    "ppb_registration_enrollment.txt":
        "https://web.pharmacyboardkenya.org/registration-and-enrollment/",
    "ca_licensing_procedures.txt":
        "https://www.ca.go.ke/licensing-procedures",
    "ca_licensing_overview.txt":
        "https://www.ca.go.ke/licensing-overview",
    "ca_license_fees.txt":
        "https://www.ca.go.ke/license-application-forms-fees",
    "ca_market_structure.txt":
        "https://www.ca.go.ke/market-structure",
    "ktb_tourism_licensing.txt":
        "https://www.tourism.go.ke/",
    "doing_business_kenya_sectors.txt":
        "https://www.doingbusinesskenya.go.ke/launch-your-business/",
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
print("  Sector-Specific Regulations Scraper")
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
