#!/usr/bin/env python3
"""Pull the article-only translatable strings (shared header/footer keys excluded)."""
import json, re, sys
from bs4 import BeautifulSoup

path = sys.argv[1]
slug = path.split('/')[-2]
raw = open(path, encoding='utf-8').read()
open(path,'w',encoding='utf-8').write(str(BeautifulSoup(raw,'lxml')))   # normalise once
soup = BeautifulSoup(open(path, encoding='utf-8').read(), 'lxml')

shared = set(json.load(open('strings_en.json', encoding='utf-8')))
out, seen = [], set()
def add(s):
    s = s.strip()
    if not s or s in seen or s in shared: return
    if not re.search(r'[A-Za-z]{2}', s): return
    seen.add(s); out.append(s)

add(soup.title.get_text())
for sel, at in [('meta[name=description]','content'), ('meta[property="og:title"]','content'),
                ('meta[property="og:description"]','content')]:
    el = soup.select_one(sel)
    if el: add(el[at])

for tag in soup.select('article, .ahero'):
    for t in tag.find_all(['h1','h2','h3','p','li','summary','span','div','a']):
        if t.find(['h1','h2','h3','p','li','summary']): continue
        if 'btn' in (t.get('class') or []) or t.name == 'a':
            add(t.decode_contents()); continue
        add(t.decode_contents())
for img in soup.select('article img, .ahero img'):
    if img.get('alt'): add(img['alt'])

json.dump({s:'' for s in out}, open(f'strings_{slug}_en.json','w',encoding='utf-8'),
          ensure_ascii=False, indent=1)
words = sum(len(re.sub(r'<[^>]+>','',s).split()) for s in out)
print(f'{len(out)} article strings, ~{words} words -> strings_{slug}_en.json')
