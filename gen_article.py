#!/usr/bin/env python3
"""Build /<lang>/<slug>/ from the EN article + the shared and article text maps.

Usage: python3 gen_article.py one-day-in-strasbourg
"""
import json, re, sys, pathlib, html as ihtml
from bs4 import BeautifulSoup
from gen import DOMAIN, PRODUCT, SHOP, SNCF_GENERAL, SNCF_FR, NAV_RE, SENTINELS

LANGS = ['fr', 'de', 'es', 'it', 'pt', 'pl', 'ru']
CLUSTER_SLUGS = ['guides', 'one-day-in-strasbourg', 'strasbourg-walking-tour',
                 'strasbourg-cathedral', 'strasbourg-food', 'how-many-days-in-strasbourg',
                 'is-strasbourg-worth-visiting', 'things-to-do-in-strasbourg',
                 'petite-france-strasbourg', 'strasbourg-christmas-market',
                 'strasbourg-boat-tour', 'strasbourg-to-colmar',
                 'strasbourg-old-town-grande-ile', 'strasbourg-astronomical-clock']
LD_RE = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)


def rebuild_ld(en_ld, page_html, lang, slug):
    data = json.loads(en_ld)
    soup = BeautifulSoup(page_html, 'lxml')
    qa = [{"@type": "Question", "name": d.summary.get_text(' ', strip=True),
           "acceptedAnswer": {"@type": "Answer",
                              "text": d.select_one('.a').get_text(' ', strip=True)}}
          for d in soup.select('details.faq') if d.summary and d.select_one('.a')]
    h1 = soup.select_one('h1').get_text(' ', strip=True)
    desc = soup.select_one('meta[name=description]')['content']
    url = f'{DOMAIN}/{lang}/{slug}/'
    for n in data['@graph']:
        t = n.get('@type')
        if t == 'Article':
            n.update({'headline': h1, 'description': desc,
                      'inLanguage': lang, 'mainEntityOfPage': url})
        elif t == 'FAQPage' and qa:
            n['mainEntity'] = qa
        elif t == 'BreadcrumbList':
            items = n['itemListElement']
            items[0]['item'] = f'{DOMAIN}/{lang}/'
            items[1]['item'] = f'{DOMAIN}/{lang}/guides/'
            items[2].update({'name': h1, 'item': url})
    return json.dumps(data, ensure_ascii=False)


def localize(master, lang, slug, shared, art):
    h = master
    NAV, LD = '<!--LANGNAV-->', '<!--JSONLD-->'
    original_nav = NAV_RE.search(h).group(0)
    h = NAV_RE.sub(NAV, h)
    m = LD_RE.search(h)
    en_ld = m.group(2)
    h = h[:m.start()] + LD + h[m.end():]

    table = {k: v for k, v in {**shared, **art}.items() if v}
    parked = original_nav + en_ld
    # only the article's own keys must match; the shared landing map legitimately
    # contains strings this page does not use
    missing = [k for k in art if k not in h and k not in parked]
    pattern = re.compile('|'.join(re.escape(k) for k in sorted(table, key=len, reverse=True)))
    h = pattern.sub(lambda mm: table[mm.group(0)], h)

    # head
    h = h.replace('<html lang="en">', f'<html lang="{lang}">', 1)
    h = h.replace(f'href="{DOMAIN}/{slug}/" rel="canonical"',
                  f'href="{DOMAIN}/{lang}/{slug}/" rel="canonical"')
    h = h.replace(f'<meta content="{DOMAIN}/{slug}/" property="og:url"/>',
                  f'<meta content="{DOMAIN}/{lang}/{slug}/" property="og:url"/>')
    h = h.replace('<meta content="en_US" property="og:locale"/>',
                  f'<meta content="{lang}_{lang.upper()}" property="og:locale"/>')

    # money layer
    h = h.replace(PRODUCT['en'], PRODUCT[lang]).replace(SHOP['en'], SHOP[lang])
    if lang == 'fr':
        h = h.replace(SNCF_GENERAL, SNCF_FR)

    # ★ the page now sits two folders deep, so body images need one more level up
    h = h.replace('src="../img/', 'src="../../img/')

    # internal links gain the language prefix
    for s in CLUSTER_SLUGS:
        h = h.replace(f'href="/{s}/"', f'href="/{lang}/{s}/"')
    h = h.replace('href="/"', f'href="/{lang}/"')

    nav = original_nav.replace(' class="on"', '')
    nav = nav.replace(f'<a href="/{lang}/">', f'<a class="on" href="/{lang}/">')
    h = h.replace(NAV, nav)
    h = h.replace(LD, '<script type="application/ld+json">'
                      + rebuild_ld(en_ld, h, lang, slug) + '</script>')
    return h, missing


def main(slug):
    master = open(f'public/{slug}/index.html', encoding='utf-8').read()
    art_all = json.load(open(f'tr_{slug}.json', encoding='utf-8'))
    for lang in LANGS:
        shared = json.load(open(f'tr_{lang}.json', encoding='utf-8'))
        out, missing = localize(master, lang, slug, shared, art_all[lang])
        d = pathlib.Path('public') / lang / slug
        d.mkdir(parents=True, exist_ok=True)
        (d / 'index.html').write_text(out, encoding='utf-8')

        body = re.search(r'<article>(.*?)</article>', out, re.S).group(1)
        text = ihtml.unescape(re.sub(r'<[^>]+>', ' ', body))
        left = [w for w in SENTINELS if w in text.lower()]
        print(f'  {"OK " if not (left or missing) else "!! "}{lang}/{slug}/  '
              f'no-match={len(missing)} english-left={left if left else "none"}')
        for k in missing[:4]:
            print(f'        > {k[:76]}')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'one-day-in-strasbourg')
