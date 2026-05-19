"""
scrape_cultural.py
Fetches cultural context content — chama, Jua Kali, informal sector,
local business networks and language resources for Kenyan MSMEs.
Run:  python3 scrape_cultural.py
"""

import urllib.request
import re
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "documents"
DOCS_DIR.mkdir(exist_ok=True)

SOURCES = {
    "jua_kali_digital_skills_nairobi_2024.txt":
        "https://files.eric.ed.gov/fulltext/EJ1417302.pdf",
    "jua_kali_sustainability_challenges_nairobi.txt":
        "https://www.researchsquare.com/article/rs-4330945/v1",
    "chama_rosca_kenya_commitment.txt":
        "https://www.journals.uchicago.edu/doi/10.1086/508716",
    "kenya_informal_sector_msme_culture.txt":
        "https://kippra.or.ke/nurturing-small-businesses-in-the-informal-sector-in-kenya/",
    "kenya_jua_kali_associations_msme.txt":
        "https://kippra.or.ke/supporting-the-digital-needs-for-micro-and-small-enterprises-in-kenya/",
    "kenya_women_chama_entrepreneurship.txt":
        "https://eujournal.org/index.php/esj/article/download/15615/15554",
    "kenya_informal_sector_skills_survey.txt":
        "https://www.knbs.or.ke/wp-content/uploads/2023/09/2016-Micro-Small-and-Medium-Enterprises-Basic-Report.pdf",
    "kenya_cultural_business_trust_networks.txt":
        "https://msea.go.ke/",
    "kenya_informal_economy_formalization.txt":
        "https://sdgs.un.org/sites/default/files/2022-03/Policy%20guidelines%20for%20the%20formalization%20of%20MSMEs%20in%20Kenya.pdf",
    "kenya_jua_kali_federation_msme.txt":
        "https://kippra.or.ke/unlock-the-potential-of-micro-small-and-medium-enterprises-in-kenya/",
    "kenya_msme_gender_culture_2024.txt":
        "https://wef.go.ke/",
    "kenya_community_financing_msme.txt":
        "https://www.fsdkenya.org/blogs-publications/blog/insights-from-the-2024-finaccess-sector-reports/",
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
print("  Cultural Context Scraper")
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
