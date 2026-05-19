"""
scrape_trade.py
Fetches trade, export and market access content from official websites.
Run:  python3 scrape_trade.py
"""

import urllib.request
import re
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "documents"
DOCS_DIR.mkdir(exist_ok=True)

SOURCES = {
    "keproba_about_what_we_do.txt":
        "https://www.makeitkenya.go.ke/about-keproba/what-we-do",
    "keproba_trade_advisory.txt":
        "https://makeitkenya.go.ke/about-keproba/",
    "eac_msmes_ecommerce.txt":
        "https://www.eac.int/trade/msmes-and-e-commerce",
    "eac_trade_agreements.txt":
        "https://www.eac.int/trade/international-trade/trade-agreements",
    "eac_afcfta.txt":
        "https://www.eac.int/trade/trade-documents/category/african-continental-free-trade-area-afcfta-trade",
    "kenya_trade_agreements_overview.txt":
        "https://www.trade.gov/country-commercial-guides/kenya-trade-agreements",
    "doing_business_kenya_export.txt":
        "https://www.doingbusinesskenya.go.ke/launch-your-business/",
    "kippra_afcfta_kenya.txt":
        "https://kippra.or.ke/unlocking-opportunities-for-kenyas-industrialization-through-the-african-continental-free-trade-area-2/",
    "comesa_tfta_2024.txt":
        "https://www.comesa.int/comesa-eac-sadc-tripartite-free-trade-area-to-come-into-force-on-25th-july-2024/",
    "eac_tfta_press_release.txt":
        "https://www.eac.int/press-releases/157-trade/3141-comesa-eac-sadc-tripartite-trade-area-to-come-into-force-25th-july,-2024",
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
print("  Market Access & Trade Scraper")
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
