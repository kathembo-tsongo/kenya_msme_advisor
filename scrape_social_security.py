"""
scrape_social_security.py
Fetches NSSF, SHA/SHIF and NITA content from official websites.
Run:  python3 scrape_social_security.py
"""

import urllib.request
import re
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "documents"
DOCS_DIR.mkdir(exist_ok=True)

SOURCES = {
    "nssf_new_contribution_rates.txt":
        "https://www.nssf.or.ke/new-contribution-rates",
    "nssf_employer_notice_2024.txt":
        "https://www.nssf.or.ke/notice-to-employers-on-the-updated-nssf-rates",
    "nssf_registration_forms.txt":
        "https://www.nssf.or.ke/download-category/application-and-registration-forms",
    "nssf_faq.txt":
        "https://www.nssf.or.ke/faq",
    "sha_employer_portal_terms.txt":
        "https://employers.sha.go.ke/terms-and-conditions",
    "sha_about_shif.txt":
        "https://sha.go.ke/",
    "nita_levy_inspectorate.txt":
        "https://www.nita.go.ke/our-services/levy-inspectorate.html",
    "nita_industrial_training_levy.txt":
        "https://www.nita.go.ke/media-centre/downloads/16-industrial-training-levy-procedures.html",
    "nita_training_reimbursement_guidelines.txt":
        "https://nita.go.ke/component/edocman/guidelines-for-training-and-reimbursement.html",
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
print("  Social Security & Insurance Scraper")
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
