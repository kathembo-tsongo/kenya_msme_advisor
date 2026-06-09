"""
scrape_geospatial.py
Fetches geospatial and county-level market data for Kenyan MSMEs.
Run:  python3 scrape_geospatial.py
"""

import urllib.request
import re
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "documents"
DOCS_DIR.mkdir(exist_ok=True)

SOURCES = {
    "knbs_county_statistical_abstracts.txt":
        "https://www.knbs.or.ke/county-statistical-abstracts/",
    "knbs_msme_survey_2016_overview.txt":
        "https://statistics.knbs.or.ke/nada/index.php/catalog/69",
    "knbs_publications_all.txt":
        "https://www.knbs.or.ke/publications/",
    "kenya_nairobi_county_msme_profile.txt":
        "https://nairobi.go.ke/",
    "kenya_mombasa_county_economy.txt":
        "https://www.mombasa.go.ke/",
    "kenya_kisumu_county_economy.txt":
        "http://eservices.kisumu.go.ke/index.php?id=2",
    "kenya_rural_urban_msme_distribution.txt":
        "https://www.knbs.or.ke/",
    "kenya_county_market_data_portal.txt":
        "https://kenya.opendataforafrica.org/data",
    "kenya_msme_county_business_survey.txt":
        "https://msea.go.ke/wp-content/uploads/2023/06/MSME-Policy-2020.pdf",
    "kenya_peri_urban_msme_markets.txt":
        "https://kippra.or.ke/characteristics-of-kenyan-msmes-relevant-to-the-proposed-kenya-credit-guarantee-scheme/",
    "kenya_vision2030_county_development.txt":
        "https://www.vision2030.go.ke/",
    "kenya_devolution_county_economic_profiles.txt":
        "https://www.devolution.go.ke/",
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
print("  Geospatial & County Market Context Scraper")
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
