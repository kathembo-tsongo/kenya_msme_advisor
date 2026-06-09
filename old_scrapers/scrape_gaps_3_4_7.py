"""
scrape_gaps_3_4_7.py
Fetches content to improve challenges 3 (infrastructure),
4 (management skills) and 7 (human capital).
"""
import urllib.request, ssl, re
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "documents"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

SOURCES = {
    # Challenge 3 — Infrastructure
    "epra_electricity_regulation.txt":
        "https://www.epra.go.ke/electricity",
    "kplc_sme_connection_procedures.txt":
        "https://kplc.co.ke/customer-support",
    "kenya_energy_cost_msme_tracker.txt":
        "https://www.stimatracker.com/",
    # Challenge 4 — Management Skills
    "kenya_sme_business_plan_guide_2025.txt":
        "https://serrarigroup.com/business-strategy-and-operating-plan-kenya-sme-guide-2026/",
    "kenya_sme_financial_planning_guide.txt":
        "https://serrarigroup.com/business-financial-planning-kenya-sme-guide-2026/",
    "kenya_business_plan_how_to_write.txt":
        "https://nextconsulting.co.ke/how-to-develop-a-business-plan-kenya/",
    "kenya_sbdc_strathmore_msme_training.txt":
        "https://sbs.strathmore.edu/kenya-small-business-development-centers-kenya-sbdc-and-kenya-bankers-association-partner-to-empower-msmes-and-foster-financial-inclusion/",
    # Challenge 7 — Human Capital
    "fke_skills_needs_survey_report.txt":
        "https://www.fke-kenya.org/media-center/news/unveiling-future-work-fke-launches-skills-needs-survey-report",
    "fke_skilling_kenya_msme.txt":
        "https://www.fke-kenya.org/index.php/media-center/opinion-pieces/federation-kenya-employers-footprints-skilling-kenya",
    "kenya_labour_market_information_system.txt":
        "https://www.labourmarket.go.ke/",
    "kenya_labour_market_resources.txt":
        "https://labourmarket.go.ke/resources/",
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
print("  Gaps 3, 4 & 7 Scraper")
print("=" * 60)

success, failed = 0, 0
for filename, url in SOURCES.items():
    print(f"\n  Fetching: {filename} ...", end=" ", flush=True)
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        text = clean_text(html)
        if len(text) < 200:
            print(f"⚠  Too short, skipped")
            failed += 1
            continue
        (DOCS_DIR / filename).write_text(f"SOURCE: {url}\n\n{text}", encoding="utf-8")
        print(f"✓  ({len(text):,} chars)")
        success += 1
    except Exception as e:
        print(f"✗  {e}")
        failed += 1

print(f"\n{'='*60}")
print(f"  Done: {success} saved, {failed} failed")
