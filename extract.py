#!/usr/bin/env python3
"""Pull every translatable string out of the EN master into a JSON skeleton."""
import json, re
from bs4 import BeautifulSoup

BLOCK = {'p','h1','h2','h3','li','dt','dd','summary','figcaption','title','span','div','a','b','strong','td','th'}
# elements whose inner HTML we take whole (they hold inline markup we must preserve)
TAKE  = ['h1','h2','h3','p','li','dt','dd','summary','figcaption']

soup = BeautifulSoup(open('public/index.html', encoding='utf-8').read(), 'lxml')

strings, seen = [], set()
def add(s):
    s = s.strip()
    if not s or s in seen: return
    if not re.search(r'[A-Za-z]{2}', s): return
    seen.add(s); strings.append(s)

# <head> meta
add(soup.title.get_text())
for sel, attr in [('meta[name=description]','content'),
                  ('meta[property="og:title"]','content'),
                  ('meta[property="og:description"]','content')]:
    el = soup.select_one(sel)
    if el: add(el[attr])

# body blocks
for tag in soup.find_all(TAKE):
    if tag.find(TAKE):            # skip wrappers that contain other blocks
        continue
    add(tag.decode_contents())

# standalone bits that are not in a block tag
for sel in ['.chip', '.badge', '.plabel', '.tag', '.price', '.ratingline b',
            '.ratingline span', '.rev .s', '.step b', '.hl b', '.hl span',
            '.sticky span', '.brand span', '.menu > summary', '.fbot',
            '.avatar', '.meta', '.disc', 'a.btn', '.drop a', 'nav.lang a']:
    for el in soup.select(sel):
        if el.name == 'img': continue
        add(el.decode_contents())

# alt text
for img in soup.find_all('img'):
    if img.get('alt'): add(img['alt'])

out = {s: '' for s in strings}
json.dump(out, open('strings_en.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'{len(out)} translatable strings -> strings_en.json')
words = sum(len(re.sub(r'<[^>]+>','',s).split()) for s in strings)
print(f'~{words} words to localise per language')
