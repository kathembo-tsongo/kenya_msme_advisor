"""
scrape_international.py
Fetches IFC, GSMA, UN international benchmark content.
Run:  python3 scrape_international.py
"""

import urllib.request
import re
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "documents"
DOCS_DIR.mkdir(exist_ok=True)

SOURCES = {
    "ifc_msme_finance_overview.txt":
        "https://www.ifc.org/en/what-we-do/sector-expertise/financial-institutions/msme-finance",
    "ifc_msme_day_2024.txt":
        "https://www.ifc.org/en/what-we-do/msme-day",
    "ifc_msme_platform_launch_2024.txt":
        "https://www.ifc.org/en/pressroom/2024/ifc-to-help-financial-institutions-support-small-businesses-through-new-global-msme-financing-platform",
    "gsma_msme_mobile_money_ssa.txt":
        "https://www.gsma.com/solutions-and-impact/connectivity-for-good/mobile-for-development/programme/mobile-money/addressing-the-financial-services-needs-of-msmes-in-sub-saharan-africa/",
    "un_msme_day_overview.txt":
        "https://sdgs.un.org/topics/capacity-development/msmes",
    "un_kenya_annual_report_2024.txt":
        "https://kenya.un.org/en/291858-un-kenya-2024-annual-results-report",
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
print("  International Benchmarks Scraper")
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
