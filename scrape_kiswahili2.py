"""
scrape_kiswahili2.py — Fixed version with SSL bypass for KRA
"""

import urllib.request
import urllib.error
import ssl
import re
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "documents"
DOCS_DIR.mkdir(exist_ok=True)

# Create SSL context that bypasses certificate verification
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

SOURCES = {
    "kra_sw_kodi_mauzo_tot.txt":
        "https://www.kra.go.ke/sw/mtu-binafsi/kufungua-kulipa/aina-za-ushuru/kodi-ya-mauzo",
    "kra_sw_aina_ushuru.txt":
        "https://www.kra.go.ke/sw/biashara/ushirika-wa-makampuni/Ubia-wa-makampuni-huweka-kodi/Ubia-wa-kampuni-aina-za-kodi",
    "kra_sw_kodi_mapato.txt":
        "https://www.kra.go.ke/sw/individual/filing-paying/types-of-taxes/individual-income-tax",
    "kra_sw_kodi_awamu.txt":
        "https://www.kra.go.ke/sw/individual/filing-paying/types-of-taxes/installment-tax",
    "kra_sw_faq_ushuru.txt":
        "https://www.kra.go.ke/sw/helping-tax-payers/faqs",
    "kra_sw_faq_ushuru2.txt":
        "https://www.kra.go.ke/sw/helping-tax-payers/faqs?start=40",
    "kra_sw_tot_biashara_ndogo.txt":
        "https://www.kra.go.ke/sw/kituo-cha-habari/blog/Kodi-ya-mauzo-ya-1511-iliyoundwa-kufanya-biashara-ndogo-kutii-zaidi",
    "kra_sw_app_huduma.txt":
        "https://www.kra.go.ke/sw/kituo-cha-habari/vyombo-vya-habari-ya-kutolewa/939-shughuli-za-ushuru,-utiifu-umerahisishwa-kupitia-programu-ya-simu",
    "kra_sw_dijitali_biashara.txt":
        "https://www.kra.go.ke/sw/kituo-cha-habari/blog/953-kodi-ya-huduma-ya-kidijitali-kiashirio-cha-kubadilisha-michakato-ya-biashara-nchini-kenya",
    "kra_sw_kodi_zuio.txt":
        "https://www.kra.go.ke/sw/individual/filing-paying/types-of-taxes/withholding-tax",
    "kra_sw_vat_ushuru.txt":
        "https://www.kra.go.ke/sw/individual/filing-paying/types-of-taxes/value-added-tax",
    "kra_sw_paye_mishahara.txt":
        "https://www.kra.go.ke/sw/individual/filing-paying/types-of-taxes/paye",
    "kra_sw_pin_usajili.txt":
        "https://www.kra.go.ke/sw/individual/individual-pin-registration/learn-about-pin/about-pin",
    "kra_sw_biashara_kukua.txt":
        "https://www.kra.go.ke/sw/biashara",
}

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "sw,en-US;q=0.7,en;q=0.3",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

def clean_text(html):
    text = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    for ent, rep in [('&nbsp;',' '),('&amp;','&'),('&lt;','<'),('&gt;','>'),('&#39;',"'")]:
        text = text.replace(ent, rep)
    text = re.sub(r'\s+', ' ', text)
    lines = [l.strip() for l in text.split('.') if len(l.strip()) > 30]
    return '\n'.join(lines)

print("=" * 60)
print("  Kiswahili KRA Scraper — SSL bypass version")
print("=" * 60)

success, failed = 0, 0
for filename, url in SOURCES.items():
    print(f"\n  Fetching: {filename} ...", end=" ", flush=True)
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
            raw = resp.read()
            # Try UTF-8 first, fall back to latin-1
            try:
                html = raw.decode("utf-8")
            except UnicodeDecodeError:
                html = raw.decode("latin-1", errors="ignore")
        text = clean_text(html)
        if len(text) < 200:
            print(f"⚠  Too short ({len(text)} chars), skipped")
            failed += 1
            continue
        out = DOCS_DIR / filename
        out.write_text(f"SOURCE: {url}\n\n{text}", encoding="utf-8")
        print(f"✓  ({len(text):,} chars)")
        success += 1
    except urllib.error.HTTPError as e:
        print(f"✗  HTTP {e.code}: {e.reason}")
        failed += 1
    except Exception as e:
        print(f"✗  {e}")
        failed += 1

print(f"\n{'='*60}")
print(f"  Done: {success} saved, {failed} failed")
print(f"  Now run: python3 src/ingest.py")
