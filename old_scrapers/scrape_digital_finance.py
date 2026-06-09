"""
scrape_digital_finance.py
Fetches digital finance, M-Pesa and eTIMS content from official websites.
Run:  python3 scrape_digital_finance.py
"""

import urllib.request
import re
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "documents"
DOCS_DIR.mkdir(exist_ok=True)

SOURCES = {
    "kra_etims_what_is.txt":
        "https://www.kra.go.ke/business/etims-electronic-tax-invoice-management-system/learn-about-etims/what-is-etims",
    "kra_etims_how_to_onboard.txt":
        "https://www.kra.go.ke/business/etims-electronic-tax-invoice-management-system/learn-about-etims/how-to-onboard-on-etims",
    "kra_etims_install.txt":
        "https://www.kra.go.ke/business/etims-electronic-tax-invoice-management-system/learn-about-etims/install-etims",
    "kra_etims_noticefaq.txt":
        "https://www.kra.go.ke/news-center/public-notices/2077-electronic-tax-invoicing-for-non-vat-registered-persons",
    "cbk_digital_credit_supervision.txt":
        "https://www.centralbank.go.ke/bank-supervision/",
    "cbk_digital_credit_licensing_page.txt":
        "https://www.centralbank.go.ke/2022/03/21/central-bank-of-kenya-digital-credit-providers-regulations-2022/",
    "safaricom_mpesa_business_main.txt":
        "https://www.safaricom.co.ke/business/sme/mpesa",
    "safaricom_mpesa_paybill.txt":
        "https://www.safaricom.co.ke/business/sme/mpesa/lipa-na-mpesa/paybill",
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
print("  Digital Finance & M-Pesa Scraper")
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
