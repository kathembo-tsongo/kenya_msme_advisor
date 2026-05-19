"""
scrape_sector_studies.py
Fetches KEPSA, KIPPRA and Strathmore MSME research content.
Run:  python3 scrape_sector_studies.py
"""

import urllib.request
import re
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "documents"
DOCS_DIR.mkdir(exist_ok=True)

SOURCES = {
    "kepsa_msme_financing_gateway.txt":
        "https://kepsa.or.ke/smeshub/msme-financing-gateway",
    "kepsa_sme_conference_2024.txt":
        "https://kepsa.or.ke/kepsanews/kepsa-hosts-the-inaugural-annual-sme-conference-awards-and-exhibition",
    "kepsa_msme_big_four_agenda.txt":
        "https://kepsa.or.ke/growing-an-inclusive-economy-creating-linkages-for-msmes-within-the-big-four-agenda/",
    "kepsa_investor_readiness_msme.txt":
        "https://kepsa.or.ke/kepsanews/kepsa-conducts-investor-readiness-business-training-for-sme-trainers",
    "kippra_nurturing_small_businesses.txt":
        "https://kippra.or.ke/14355-2/",
    "kippra_unlock_msme_potential.txt":
        "https://kippra.or.ke/unlock-the-potential-of-micro-small-and-medium-enterprises-in-kenya/",
    "kippra_msme_credit_guarantee.txt":
        "https://kippra.or.ke/characteristics-of-kenyan-msmes-relevant-to-the-proposed-kenya-credit-guarantee-scheme/",
    "kippra_digital_needs_msme.txt":
        "https://kippra.or.ke/supporting-the-digital-needs-for-micro-and-small-enterprises-in-kenya/",
    "kippra_ict_msme_innovations.txt":
        "https://kippra.or.ke/leveraging-on-ict-to-promote-innovations-amongst-msmes-in-kenya/",
    "strathmore_kenya_sbdc_kba_partnership.txt":
        "https://sbs.strathmore.edu/kenya-small-business-development-centers-kenya-sbdc-and-kenya-bankers-association-partner-to-empower-msmes-and-foster-financial-inclusion/",
    "strathmore_enterprise_development_centre.txt":
        "https://sbs.strathmore.edu/centers/center-for-entrepreneurship/",
    "strathmore_sbs_about.txt":
        "https://sbs.strathmore.edu/about-sbs/",
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
print("  Sector Studies Scraper — KEPSA, KIPPRA, Strathmore")
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
