"""
scrape_ajira.py
Fetches Ajira Digital programme content from official and partner websites.
Run:  python3 scrape_ajira.py
"""

import urllib.request
import re
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "documents"
DOCS_DIR.mkdir(exist_ok=True)

SOURCES = {
    "ajira_digital_main_portal.txt":
        "https://ajiradigital.go.ke/",
    "ajira_digital_trainer_portal.txt":
        "https://www.trainer.ajiradigital.go.ke/",
    "ajira_digital_blog_partners.txt":
        "https://blog.ajiradigital.go.ke/index.php/2020/09/15/spotlight-on-partners/",
    "ajira_digital_blog_economy.txt":
        "https://blog.ajiradigital.go.ke/index.php/2020/10/23/realizing-the-digital-economy/",
    "ajira_digital_mastercard_overview.txt":
        "https://mastercardfdn.org/en/what-we-do/our-programs/ajira-digital-program/",
    "ajira_digital_emobilis_programme.txt":
        "https://emobilis.ac.ke/ajira",
    "ajira_digital_eaa_observatory_2024.txt":
        "https://admin-policyhub-beta.educationaboveall.org/index.php/solution/ajira-digital",
    "ajira_digital_ict_ministry_scorecard_2023.txt":
        "https://techweez.com/2023/07/31/kbc-ajira-jitume-digital-id-ict-ministry/",
    "ajira_digital_youth_stats_2024.txt":
        "https://www.the-star.co.ke/news/corridors-of-power/2024-03-08-weve-trained-390968-youth-on-digital-skills-mwaura",
    "ajira_digital_ps_interview_nation.txt":
        "https://nation.africa/kenya/news/ict-ps-1-9m-youth-working-on-digitally-enabled-jobs-annually-3859748",
    "ajira_digital_kenya_news_agency.txt":
        "https://www.kenyanews.go.ke/ajira-digital-programme-helping-youth-to-earn-a-living/",
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
print("  Ajira Digital Programme Scraper")
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
