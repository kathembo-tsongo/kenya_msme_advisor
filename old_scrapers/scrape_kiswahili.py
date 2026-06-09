"""
scrape_kiswahili.py
Fetches Kiswahili language business, tax and entrepreneurship content
from official Kenyan government websites.
Run:  python3 scrape_kiswahili.py
"""

import urllib.request
import re
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "documents"
DOCS_DIR.mkdir(exist_ok=True)

SOURCES = {
    "kra_kiswahili_kodi_mauzo_tot.txt":
        "https://www.kra.go.ke/sw/mtu-binafsi/kufungua-kulipa/aina-za-ushuru/kodi-ya-mauzo",
    "kra_kiswahili_aina_ushuru_biashara.txt":
        "https://www.kra.go.ke/sw/biashara/ushirika-wa-makampuni/Ubia-wa-makampuni-huweka-kodi/Ubia-wa-kampuni-aina-za-kodi",
    "kra_kiswahili_kufungua_kulipa_kodi.txt":
        "https://www.kra.go.ke/sw/biashara/ushirika-wa-makampuni/Ubia-wa-makampuni-huweka-kodi/malipo-ya-faili-ya-ushirika-wa-kampuni",
    "kra_kiswahili_kodi_mapato_mtu.txt":
        "https://kra.go.ke/sw/individual/filing-paying/types-of-taxes/individual-income-tax",
    "kra_kiswahili_kodi_awamu.txt":
        "https://www.kra.go.ke/sw/individual/filing-paying/types-of-taxes/installment-tax",
    "kra_kiswahili_msaada_walipakodi_faq.txt":
        "https://www.kra.go.ke/sw/helping-tax-payers/faqs",
    "kra_kiswahili_tot_biashara_ndogo.txt":
        "https://kra.go.ke/sw/kituo-cha-habari/blog/Kodi-ya-mauzo-ya-1511-iliyoundwa-kufanya-biashara-ndogo-kutii-zaidi",
    "kra_kiswahili_app_huduma_biashara.txt":
        "https://kra.go.ke/sw/kituo-cha-habari/vyombo-vya-habari-ya-kutolewa/939-shughuli-za-ushuru,-utiifu-umerahisishwa-kupitia-programu-ya-simu",
    "kra_kiswahili_dijitali_biashara.txt":
        "https://kra.go.ke/sw/kituo-cha-habari/blog/953-kodi-ya-huduma-ya-kidijitali-kiashirio-cha-kubadilisha-michakato-ya-biashara-nchini-kenya",
    "kra_kiswahili_ushuru_msaada.txt":
        "https://www.kra.go.ke/sw/helping-tax-payers/faqs?start=40",
    "hustlerfund_kiswahili_mkopo.txt":
        "https://www.hustlerfund.go.ke/sw/personal-loan",
    "hustlerfund_kiswahili_biashara.txt":
        "https://www.hustlerfund.go.ke/sw/",
    "biashara_kenya_kiswahili_maoni.txt":
        "https://joon.co.ke/sw/maoni-ya-biashara-ambayo-hayajafungwa/",
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
print("  Kiswahili Language Resources Scraper")
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
