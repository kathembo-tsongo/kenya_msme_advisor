"""
scrape_ecommerce.py
Fetches e-commerce and digital business content for Kenyan MSMEs.
Run:  python3 scrape_ecommerce.py
"""

import urllib.request
import re
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "documents"
DOCS_DIR.mkdir(exist_ok=True)

SOURCES = {
    "icta_about_digital_economy.txt":
        "https://icta.go.ke/",
    "icta_business_enterprise.txt":
        "https://www.icta.go.ke/page?q=12&type=business",
    "icta_kdeap_components.txt":
        "https://kdeap.icta.go.ke/components/",
    "icta_kdeap_overview.txt":
        "https://kdeap.icta.go.ke/",
    "kenya_ecommerce_guide_us_trade.txt":
        "https://www.trade.gov/country-commercial-guides/kenya-ecommerce",
    "kenya_ecommerce_overview_2024.txt":
        "https://brinasolutions.com/2024/11/22/all-you-need-to-know-about-e-commerce-in-kenya/",
    "kenya_ecommerce_platforms_guide.txt":
        "https://avada.io/blog/online-selling-platforms-in-kenya/",
    "kenya_ecommerce_future_trends_2025.txt":
        "https://www.cysparkstechnologies.com/post/the-future-of-e-commerce-in-kenya-trends-challenges-and-opportunities",
    "jumia_seller_guide_kenya.txt":
        "https://www.jumia.co.ke/sp-help/",
    "kenya_digital_economy_msme_2023.txt":
        "https://techweez.com/2023/07/31/kbc-ajira-jitume-digital-id-ict-ministry/",
    "kenya_data_protection_act_guide.txt":
        "https://www.odpc.go.ke/dpa-act/",
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
print("  E-Commerce & Digital Business Scraper")
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
