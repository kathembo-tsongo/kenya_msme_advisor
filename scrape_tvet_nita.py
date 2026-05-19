"""
scrape_tvet_nita.py
Fetches TVETA and NITA training content from official websites.
Run:  python3 scrape_tvet_nita.py
"""

import urllib.request
import re
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "documents"
DOCS_DIR.mkdir(exist_ok=True)

SOURCES = {
    "tveta_about_tvet_system.txt":
        "https://www.tveta.go.ke/",
    "tveta_tvet_courses_list.txt":
        "https://www.tveta.go.ke/tvet-courses/",
    "tveta_accredited_institutions.txt":
        "https://www.tveta.go.ke/accredited-tvet-institutions/",
    "tveta_tvet_standards.txt":
        "https://www.tveta.go.ke/tvet-standards/",
    "nita_levy_inspectorate.txt":
        "https://www.nita.go.ke/our-services/levy-inspectorate.html",
    "nita_catalogue_curricula.txt":
        "https://www.nita.go.ke/careers/9-explore/325-catalogue-of-nita-curricula.html",
    "nita_industrial_training_levy.txt":
        "https://www.nita.go.ke/media-centre/downloads/industrial-training-levy.html",
    "nita_training_reimbursement.txt":
        "https://nita.go.ke/component/edocman/guidelines-for-training-and-reimbursement.html",
    "nita_current_training_programs.txt":
        "https://www.nita.go.ke/index.php/84-national-industrial-vocational-training-centre-nivtc/241-current-training-programs",
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
print("  TVET Authority & NITA Scraper")
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
