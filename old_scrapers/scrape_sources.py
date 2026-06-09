"""
scrape_sources.py
Fetches real content from official Kenyan government websites
and saves them as text files in the documents/ folder.
Run once:  python3 scrape_sources.py
"""

import urllib.request
import re
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "documents"
DOCS_DIR.mkdir(exist_ok=True)

SOURCES = {
    "kra_turnover_tax.txt": "https://www.kra.go.ke/individual/filing-paying/types-of-taxes/turnover-tax-tot",
    "kra_vat.txt": "https://www.kra.go.ke/individual/filing-paying/types-of-taxes/value-added-tax",
    "kra_paye.txt": "https://www.kra.go.ke/individual/filing-paying/types-of-taxes/paye",
    "kra_income_tax.txt": "https://www.kra.go.ke/individual/filing-paying/types-of-taxes/individual-income-tax",
    "kra_pin_registration.txt": "https://www.kra.go.ke/individual/individual-pin-registration/learn-about-pin/about-pin",
    "kra_rental_income_tax.txt": "https://www.kra.go.ke/individual/filing-paying/types-of-taxes/residential-rental-income",
    "kra_tax_compliance.txt": "https://www.kra.go.ke/individual/filing-paying/types-of-taxes/tax-compliance",
    "kra_business_types_of_taxes.txt": "https://www.kra.go.ke/business/companies-partnerships/companies-partnerships-pin-taxes/company-partnerships-types-of-taxes",
    "kra_offences_penalties.txt": "https://www.kra.go.ke/business/business-compliance-penalties/business-how-to-file/business-offences-penalties",
    "hustlerfund_personal_loan.txt": "https://www.hustlerfund.go.ke/personal-loan",
    "hustlerfund_group_loan.txt": "https://www.hustlerfund.go.ke/group-loan-product",
    "hustlerfund_background.txt": "https://www.hustlerfund.go.ke/fund",
    "yedf_about.txt": "http://www.youthfund.go.ke/",
    "wef_about.txt": "https://wef.go.ke/",
    "msme_state_dept.txt": "https://www.msme.go.ke/hustler-inclusion-fund",
}

headers = {"User-Agent": "Mozilla/5.0 (compatible; research bot)"}

def clean_text(html):
    """Strip HTML tags and clean whitespace."""
    text = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'\s+', ' ', text)
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    return '\n'.join(lines)

print("=" * 60)
print("  Kenya MSME Advisor — Official Source Scraper")
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
