"""
scrape_cultural_geo.py — Improves KB #2 (Cultural) and KB #7 (Geospatial)
"""
import urllib.request, ssl, re
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "documents"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

SOURCES = {
    # KB #2 — Cultural context
    "kenya_entrepreneurship_africa_culture_2024.txt":
        "https://www.tandfonline.com/doi/full/10.1080/23322373.2024.2350861",
    "kenya_chama_microfinance_health_women.txt":
        "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7216653/",
    "kenya_ubuntu_entrepreneurship_culture.txt":
        "https://kippra.or.ke/nurturing-small-businesses-in-the-informal-sector-in-kenya/",
    "kenya_socio_cultural_business_environment.txt":
        "https://hrmars.com/papers_submitted/2013/The_Impact_of_Socio-cultural_Business_Environment_on_Entrepreneurial_Intention_A_Conceptual_Approach.pdf",
    # KB #7 — Geospatial context
    "kenya_gross_county_product_all47.txt":
        "https://statskenya.co.ke/at-stats-kenya/about/gross-county-product-county-gdp/45/",
    "kenya_county_government_structure.txt":
        "https://icma.org/articles/article/county-government-structure-kenya",
    "kenya_county_data_portal.txt":
        "https://kenya.opendataforafrica.org/",
    "kenya_meru_county_economy.txt":
        "https://meru.go.ke/",
    "kenya_nakuru_county_business.txt":
        "https://nakuru.go.ke/",
    "kenya_eldoret_uasin_gishu_economy.txt":
        "https://uasingo.go.ke/",
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

print("="*60)
print("  Cultural & Geospatial Scraper")
print("="*60)

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
