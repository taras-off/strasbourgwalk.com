#!/usr/bin/env python3
"""Build /<lang>/guides/ from the EN guides page + the shared and guides text maps."""
import json, re, sys, pathlib, html as ihtml
from gen import (DOMAIN, OG_LOCALE, PRODUCT, SHOP, CLUSTER, NAV_RE,
                 SNCF_GENERAL, SNCF_FR, SENTINELS)

MASTER = 'public/guides/index.html'
GUIDES = json.load(open('tr_guides.json', encoding='utf-8'))


def localize(master, lang):
    tr = dict(json.load(open(f'tr_{lang}.json', encoding='utf-8')))
    tr.update(GUIDES[lang])                       # page-specific keys win
    h = master
    NAV = '<!--LANGNAV-->'
    original_nav = NAV_RE.search(h).group(0)
    h = NAV_RE.sub(NAV, h)

    missing = []
    for src in sorted(tr, key=len, reverse=True):
        dst = tr[src]
        if not dst or src not in h:
            continue                              # shared map covers both pages; misses are expected
        h = h.replace(src, dst)

    h = h.replace('<html lang="en">', f'<html lang="{lang}">', 1)
    h = h.replace(f'href="{DOMAIN}/guides/" rel="canonical"',
                  f'href="{DOMAIN}/{lang}/guides/" rel="canonical"')
    h = h.replace(PRODUCT['en'], PRODUCT[lang]).replace(SHOP['en'], SHOP[lang])
    h = h.replace('booking.com/searchresults.html', f'booking.com/searchresults.{lang}.html')
    if lang == 'fr':
        h = h.replace(SNCF_GENERAL, SNCF_FR)
    for slug in CLUSTER:
        h = h.replace(f'href="/{slug}/"', f'href="/{lang}/{slug}/"')
    h = h.replace('href="/"', f'href="/{lang}/"')

    nav = original_nav.replace(' class="on"', '')
    nav = nav.replace(f'<a href="/{lang}/">', f'<a class="on" href="/{lang}/">')
    h = h.replace(NAV, nav)
    return h


def main(langs):
    master = open(MASTER, encoding='utf-8').read()
    for lang in langs:
        out = localize(master, lang)
        d = pathlib.Path('public') / lang / 'guides'
        d.mkdir(parents=True, exist_ok=True)
        (d / 'index.html').write_text(out, encoding='utf-8')
        text = ihtml.unescape(re.sub(r'<[^>]+>', ' ', re.sub(r'<script.*?</script>', ' ', out, flags=re.S)))
        left = [w for w in SENTINELS if w in text.lower()]
        print(f'  {"OK " if not left else "!! "}{lang}/guides/  english-left={left if left else "none"}')


if __name__ == '__main__':
    main(sys.argv[1:] or ['fr', 'de', 'es', 'it', 'pt', 'pl', 'ru'])
