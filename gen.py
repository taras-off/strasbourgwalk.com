#!/usr/bin/env python3
"""Build the 7 localized landings from the EN master + tr_<lang>.json text maps.

Usage:  python3 gen.py fr de es it pt pl ru
"""
import json, re, sys, pathlib, html as ihtml
from bs4 import BeautifulSoup

MASTER = 'public/index.html'
DOMAIN = 'https://strasbourgwalk.com'

OG_LOCALE = {'en':'en_US','fr':'fr_FR','de':'de_DE','es':'es_ES',
             'it':'it_IT','pt':'pt_PT','pl':'pl_PL','ru':'ru_RU'}

# TouringBee Strasbourg product, per language (all 8 verified on WordPress)
PRODUCT = {
 'en':'https://touringbee.com/product/city-tour-of-strasbourg/',
 'fr':'https://touringbee.com/fr/product/city-tour-of-strasbourg-fr/',
 'de':'https://touringbee.com/de/product/city-tour-of-strasbourg-de/',
 'es':'https://touringbee.com/es/product/visita-a-la-ciudad-de-estrasburgo/',
 'it':'https://touringbee.com/product/city-tour-of-strasbourg-it/',
 'pt':'https://touringbee.com/product/passeio-pela-cidade-de-estrasburgo/',
 'pl':'https://touringbee.com/pl/product/city-tour-of-strasbourg-pl/',
 'ru':'https://touringbee.com/ru/product/city-tour-of-strasbourg-ru/',
}

SHOP = {
 'en':'https://touringbee.com/shop-tbee/',
 'fr':'https://touringbee.com/fr/shop-tbee-fr/',
 'de':'https://touringbee.com/de/shop-tbee-de/',
 'es':'https://touringbee.com/es/shop-tbee-es/',
 'it':'https://touringbee.com/shop-tbee/',
 'pt':'https://touringbee.com/shop-tbee/',
 'pl':'https://touringbee.com/pl/shop-tbee-pl/',
 'ru':'https://touringbee.com/ru/shop-tbee-ru/',
}

# Cross-sell products. Where a language has no localized product it falls back to EN.
XSELL = json.load(open('xsell.json', encoding='utf-8')) if pathlib.Path('xsell.json').exists() else {}
EXTRA = json.load(open('tr_extra.json', encoding='utf-8')) if pathlib.Path('tr_extra.json').exists() else {}

SNCF_GENERAL = 'track.effiliation.com/servlet/effi.click?id_compteur=22682146'
SNCF_FR      = 'track.effiliation.com/servlet/effi.click?id_compteur=22721666'

CLUSTER = ['guides']   # legal pages stay English-only for now, so they must not gain a prefix

LD_RE  = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)
NAV_RE = re.compile(r'<nav class="lang">.*?</nav>', re.S)


def build_schema(en_ld: str, page_html: str, lang: str) -> str:
    """Rebuild the JSON-LD for one language.

    The FAQ block is regenerated from the localized page itself, so the schema can
    never drift from what the visitor actually reads. The remaining prose fields
    come from the tr_extra map.
    """
    data = json.loads(en_ld)
    extra = EXTRA.get(lang, {})

    soup = BeautifulSoup(page_html, 'lxml')
    qa = []
    for d in soup.select('details.faq'):
        a = d.select_one('.a')
        if not (d.summary and a):
            continue
        qa.append({"@type": "Question",
                   "name": d.summary.get_text(' ', strip=True),
                   "acceptedAnswer": {"@type": "Answer",
                                      "text": a.get_text(' ', strip=True)}})

    def tr(v):
        return extra.get(v, v)

    for node in data['@graph']:
        t = node.get('@type')
        if t == 'FAQPage' and qa:
            node['mainEntity'] = qa
        elif t == 'WebSite':
            node['inLanguage'] = lang
        elif t == 'Product':
            node['name']        = tr(node['name'])
            node['description'] = tr(node['description'])
            node['category']    = tr(node['category'])
            node['offers']['url'] = PRODUCT[lang]
        elif t == 'TouristAttraction':
            node['description'] = tr(node['description'])
        elif t == 'Person':
            node['jobTitle']    = tr(node['jobTitle'])
            node['description'] = tr(node['description'])
        elif t == 'BreadcrumbList':
            node['itemListElement'][0]['item'] = f'{DOMAIN}/{lang}/'
    return json.dumps(data, ensure_ascii=False)


def localize(master: str, lang: str, tr: dict):
    h = master
    NAV, LD = '<!--LANGNAV-->', '<!--JSONLD-->'

    # 1. park the switcher and the JSON-LD: neither may be touched by the text map
    original_nav = NAV_RE.search(h).group(0)
    h = NAV_RE.sub(NAV, h)
    m = LD_RE.search(h)
    en_ld = m.group(2)
    h = h[:m.start()] + LD + h[m.end():]

    # 2. text map first, while the keys still match the master verbatim.
    #    Longest key first so a short label cannot clobber a longer string it prefixes.
    missing = []
    for src in sorted(tr, key=len, reverse=True):
        dst = tr[src]
        if not dst:
            missing.append(('empty', src))
        elif src not in h:
            missing.append(('nomatch', src))
        else:
            h = h.replace(src, dst)
    for src, dst in EXTRA.get(lang, {}).items():
        h = h.replace(src, dst)

    # 3. head: lang, canonical, og
    h = h.replace('<html lang="en">', f'<html lang="{lang}">', 1)
    h = h.replace(f'href="{DOMAIN}/" rel="canonical"', f'href="{DOMAIN}/{lang}/" rel="canonical"')
    h = h.replace(f'<meta content="{DOMAIN}/" property="og:url"/>',
                  f'<meta content="{DOMAIN}/{lang}/" property="og:url"/>')
    h = h.replace('<meta content="en_US" property="og:locale"/>',
                  f'<meta content="{OG_LOCALE[lang]}" property="og:locale"/>')

    # 4. product, shop and cross-sell URLs in the page language
    h = h.replace(PRODUCT['en'], PRODUCT[lang])
    h = h.replace(SHOP['en'], SHOP[lang])
    for urls in XSELL.values():
        if urls.get('en') and urls.get(lang):
            h = h.replace(urls['en'], urls[lang])

    # 5. audio preview, 6. Booking locale, 7. SNCF counter for the French page
    h = h.replace('/audio/strasbourgt1_en_intro.mp3', f'/audio/strasbourgt1_{lang}_intro.mp3')
    h = h.replace('booking.com/searchresults.html', f'booking.com/searchresults.{lang}.html')
    if lang == 'fr':
        h = h.replace(SNCF_GENERAL, SNCF_FR)

    # 8. internal links gain the language prefix
    for slug in CLUSTER:
        h = h.replace(f'href="/{slug}/"', f'href="/{lang}/{slug}/"')
    h = h.replace('href="/"', f'href="/{lang}/"')

    # 9. restore the switcher with this language active, then the rebuilt schema
    nav = original_nav.replace(' class="on"', '')
    nav = nav.replace(f'<a href="/{lang}/">', f'<a class="on" href="/{lang}/">')
    h = h.replace(NAV, nav)
    h = h.replace(LD, '<script type="application/ld+json">'
                      + build_schema(en_ld, h, lang) + '</script>')
    return h, missing


SENTINELS = [' the ', ' and ', ' with ', ' your ', ' from the ', ' book ']

def main(langs):
    master = open(MASTER, encoding='utf-8').read()
    for lang in langs:
        p = pathlib.Path(f'tr_{lang}.json')
        if not p.exists():
            print(f'  -- {lang}: no tr_{lang}.json, skipped'); continue
        out, missing = localize(master, lang, json.load(open(p, encoding='utf-8')))
        d = pathlib.Path('public')/lang
        d.mkdir(parents=True, exist_ok=True)
        (d/'index.html').write_text(out, encoding='utf-8')

        text = re.sub(r'<script.*?</script>', ' ', out, flags=re.S)
        text = ihtml.unescape(re.sub(r'<[^>]+>', ' ', text))
        left = [w for w in SENTINELS if w in text.lower()]
        empty   = [k for kind,k in missing if kind == 'empty']
        nomatch = [k for kind,k in missing if kind == 'nomatch']
        ok = not (empty or nomatch or left)
        print(f'  {"OK " if ok else "!! "}{lang}: empty={len(empty)} no-match={len(nomatch)} '
              f'english-left={left if left else "none"}')
        for k in (empty + nomatch)[:6]:
            print(f'        > {k[:78]}')


if __name__ == '__main__':
    main(sys.argv[1:] or ['fr','de','es','it','pt','pl','ru'])
