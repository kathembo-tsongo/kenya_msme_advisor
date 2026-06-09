"""
scrape_county_permits.py
Fetches real county business permit content from official government websites
and saves them as text files in the documents/ folder.
Run:  python3 scrape_county_permits.py
"""

import urllib.request
import re
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "documents"
DOCS_DIR.mkdir(exist_ok=True)

SOURCES = {
    "nairobi_unified_business_permit.txt":
        "https://nairobi.go.ke/nairobi-city-county-government-unified-business-permit-ubp-permit-process",
    "nairobi_ubp_usage.txt":
        "https://nairobi.go.ke/unified-business-permit-ubp-usage",
    "nairobi_county_laws_business.txt":
        "https://nairobi.go.ke/county-laws",
    "nairobi_faqs_help_desks.txt":
        "https://nairobi.go.ke/faqs-and-help-desks",
    "mombasa_business_permit_procedure.txt":
        "https://eprocedures.investkenya.go.ke/procedure/print/206/140/step/0?showRecourses=true&showCertification=false&l=en",
    "mombasa_county_finance_act_2024.txt":
        "https://www.mombasaassembly.go.ke/wp-content/uploads/2024/11/The_Mombasa_County_Finance_Bill-2024.pdf",
    "kisumu_business_permit_faq.txt":
        "http://www.eservices.kisumu.go.ke/index.php/help/faq",
    "kisumu_business_licensing.txt":
        "http://eservices.kisumu.go.ke/index.php?id=2",
    "kenya_single_business_permit_guide.txt":
        "https://eprocedures.investkenya.go.ke/media/Single_Business_Permit.2.pdf",
    "doing_business_kenya_launch.txt":
        "https://www.doingbusinesskenya.go.ke/launch-your-business/",
}

headers = {"User-Agent": "Mozilla/5.0 (compatible; research bot)"}

def clean_text(html):
    text = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'\s+', ' ', text)
    lines = [l.strip() for l in text.split('.') if len(l.strip()) > 30]
    return '\n'.join(lines)

print("=" * 60)
print("  County Business Permit Scraper")
print("=" * 60)

success, failed = 0, 0
for filename, url in SOURCES.items():
    print(f"\n  Fetching: {filename} ...", end=" ", flush=True)
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read()
            html = raw.decode("utf-8", errors="ignore")
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
