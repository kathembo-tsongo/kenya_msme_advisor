"""
scrape_insurance_climate.py
Fetches insurance and climate resilience content for Kenyan MSMEs.
Run:  python3 scrape_insurance_climate.py
"""

import urllib.request
import re
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "documents"
DOCS_DIR.mkdir(exist_ok=True)

SOURCES = {
    "ira_about_insurance_regulation.txt":
        "https://www.ira.go.ke/",
    "ira_msme_insurance_survey_circular.txt":
        "https://www.ira.go.ke/index.php/circular-2023",
    "ira_insurance_downloads.txt":
        "https://www.ira.go.ke/downloads/",
    "ira_consumer_education_insurance.txt":
        "https://www.ira.go.ke/index.php/consumer-education",
    "ndma_drought_resilience.txt":
        "https://ndma.go.ke/drought-resilience/",
    "ndma_about_mandate.txt":
        "https://ndma.go.ke/about-ndma/",
    "kenya_nap_climate_adaptation.txt":
        "https://napcentral.org/nap-summaries/kenya",
    "mercy_corps_msme_climate_resilience_kenya.txt":
        "https://medium.com/mercy-corps-social-venture-fund/understanding-msme-resilience-to-climate-change-cd50355bd31b",
    "kenya_national_climate_change_action_plan.txt":
        "https://unfccc.int/sites/default/files/resource/Kenya_NAP.pdf",
    "aki_insurance_kenya_msme.txt":
        "https://www.akinsurance.org/",
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
print("  Insurance & Climate Resilience Scraper")
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
