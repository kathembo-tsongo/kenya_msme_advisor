"""
scrape_research.py
Fetches World Bank, FSD Kenya, FinAccess and KNBS content.
Run:  python3 scrape_research.py
"""

import urllib.request
import re
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "documents"
DOCS_DIR.mkdir(exist_ok=True)

SOURCES = {
    "worldbank_kenya_overview.txt":
        "https://www.worldbank.org/en/country/kenya/overview",
    "worldbank_kenya_msme_support.txt":
        "https://www.msme.go.ke/world-banks-support-kenyas-msme-development-agenda",
    "fsd_kenya_finaccess_2024_topline.txt":
        "https://www.fsdkenya.org/blogs-publications/the-2024-finaccess-household-survey/",
    "fsd_kenya_finaccess_2024_insights.txt":
        "https://www.fsdkenya.org/blogs-publications/2024-finaccess-household-survey-key-insights-into-kenyas-financial-landscape/",
    "fsd_kenya_financial_inclusion_health.txt":
        "https://www.fsdkenya.org/blogs-publications/financial-inclusion-and-health-a-balancing-act-for-kenyas-future/",
    "fsd_kenya_finaccess_sector_reports.txt":
        "https://www.fsdkenya.org/blogs-publications/blog/insights-from-the-2024-finaccess-sector-reports/",
    "knbs_economic_surveys_page.txt":
        "https://www.knbs.or.ke/economic-surveys/",
    "knbs_home_statistics.txt":
        "https://www.knbs.or.ke/",
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
print("  Research Reports Scraper")
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
