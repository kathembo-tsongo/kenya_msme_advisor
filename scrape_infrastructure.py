"""
scrape_infrastructure.py
Fetches KPLC and KRB infrastructure content from official websites.
Run:  python3 scrape_infrastructure.py
"""

import urllib.request
import re
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "documents"
DOCS_DIR.mkdir(exist_ok=True)

SOURCES = {
    "kplc_tariff_faq.txt":
        "https://kplc.co.ke/faq/tariff",
    "kplc_customer_support.txt":
        "https://kplc.co.ke/customer-support",
    "kplc_electricity_tariff_reduction_2024.txt":
        "https://newsroom.kplc.co.ke/articles/strengthening-of-kenya-shilling-and-drop-in-the-cost-of-fuel-leads-to-reduction-in-the-price-of-electricity",
    "kplc_sme_connection_guide.txt":
        "https://kplc.co.ke/",
    "krb_strategic_plan.txt":
        "https://krb.go.ke/strategic-plan-2/",
    "krb_about_what_we_do.txt":
        "https://krb.go.ke/what-we-do/",
    "krb_organogram_functions.txt":
        "https://krb.go.ke/krb-organogram/",
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
print("  Infrastructure Scraper — KPLC & Kenya Roads Board")
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
