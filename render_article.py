#!/usr/bin/env python3
"""Render one article draft (Markdown) into a site-styled HTML page.

Usage: python3 render_article.py ../drafts/02-one-day.md
The draft's SEO BLOCK supplies slug, title tag, meta description and keywords.
"""
import re, sys, json, pathlib, html as ihtml
from bs4 import BeautifulSoup

DOMAIN = 'https://strasbourgwalk.com'
LANDING = 'public/index.html'
LANGS = ['en', 'fr', 'de', 'es', 'it', 'pt', 'pl', 'ru']

PRODUCT_EN = 'https://touringbee.com/product/city-tour-of-strasbourg/'
GYG        = 'https://www.getyourguide.com/strasbourg-l293/?partner_id=0M4BUCG&utm_medium=travel_agent'

def tb(pos):
    return (PRODUCT_EN + f'?wpam_id=42&utm_source=strasbourgwalk&utm_medium=referral'
                         f'&utm_campaign=article&utm_content={pos}')

ICON = {
 'wifi':  '<path d="M2 8a15 15 0 0 1 20 0M5 12a10 10 0 0 1 14 0M8.5 15.5a5 5 0 0 1 7 0"/><circle cx="12" cy="19" r=".6"/>',
 'pin':   '<path d="M12 21s7-5.4 7-11a7 7 0 1 0-14 0c0 5.6 7 11 7 11z"/><circle cx="12" cy="10" r="2.6"/>',
 'globe': '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a15 15 0 0 1 0 18a15 15 0 0 1 0-18"/>',
 'phone': '<rect x="7" y="2.5" width="10" height="19" rx="2.2"/><path d="M11 18.6h2"/>',
 'clock': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.2 2"/>',
 'ticket':'<path d="M3 9V6.5A1.5 1.5 0 0 1 4.5 5h15A1.5 1.5 0 0 1 21 6.5V9a3 3 0 0 0 0 6v2.5a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 17.5V15a3 3 0 0 0 0-6z"/><path d="M15 5v14"/>',
 'boat':  '<path d="M3 17.5s2-1 4.5-1 4.5 1 4.5 1 2-1 4.5-1 4.5 1 4.5 1"/><path d="M5 14l1.6-5.2A2 2 0 0 1 8.5 7.3h7a2 2 0 0 1 1.9 1.5L19 14"/><path d="M12 7.3V4"/>',
 'check': '<path d="M4 12.5l5 5L20 6.5"/>',
}

def frow(icon, text):
    return (f'<div class="frow"><svg viewBox="0 0 24 24" aria-hidden="true">{ICON[icon]}</svg>'
            f'<span>{text}</span></div>')

AUDIO_CARD = (
 '<div class="pcard"><div class="grid">'
 '<img src="../img/tour-promo-card.webp" alt="The TouringBee app showing the Strasbourg route on an offline map" width="600" height="800" loading="lazy">'
 '<div class="in">'
 '<div class="rate"><b>★</b> 4.7 on the App Store &amp; Google Play · 4,664 travellers have listened</div>'
 '<h3>Strasbourg Self-Guided Audio Tour <span class="pill">Instant access</span></h3>'
 '<div class="from">From €9.99 <small>· 1 year access</small></div>'
 + frow('wifi',  '100% offline — no Wi-Fi or data needed')
 + frow('pin',   'Offline GPS map — you start each track yourself at the spot')
 + frow('globe', '8 languages, real voice narration')
 + frow('phone', 'Works on iOS &amp; Android')
 + frow('clock', '33 stops, around 2.5 hours at your own pace')
 + f'<a class="btn block" href="{tb("product_card")}" target="_blank" rel="noopener sponsored">'
   'Buy the Audio Guide — from €9.99</a>'
 '</div></div></div>')

BOAT_CARD = (
 '<div class="pcard"><div class="grid">'
 '<img src="../img/a-peaceful-autumn-view-along-the-river-ill-wide.webp" alt="A sightseeing boat on the river Ill in Strasbourg" width="1024" height="683" loading="lazy">'
 '<div class="in">'
 '<h3>Strasbourg Boat Cruise on the Ill <span class="pill">Timed entry</span></h3>'
 '<div class="sub">Circuit Rouge · 1 h 10 · mobile ticket</div>'
 '<div class="from">From €16.20 <small>· adult · book the morning slot</small></div>'
 + frow('ticket','Departures are timed — slots go hours ahead in summer')
 + frow('boat',  'Round the Grande Île, through two locks, out to the European quarter')
 + frow('check', 'Free cancellation on most options')
 + f'<a class="btn block" href="{GYG}" target="_blank" rel="noopener sponsored">'
   'Check availability &amp; book on GetYourGuide →</a>'
 '</div></div></div>')

READY = (
 '<div class="ready"><div class="top">'
 '<h3>Ready to walk it?</h3>'
 '<p>Be on Pont Kuss at 08:30 and the rest of the day builds itself.</p></div>'
 '<div class="btns">'
 f'<a class="btn solid" href="{tb("conclusion")}" target="_blank" rel="noopener sponsored">'
 'Get the Strasbourg audio guide — from €9.99</a>'
 f'<a class="btn outline" href="{GYG}" target="_blank" rel="noopener sponsored">'
 'Browse Strasbourg tours &amp; cruises →</a>'
 '</div></div>')


# ─────────────────────────── markdown ───────────────────────────
def inline(t: str) -> str:
    t = ihtml.escape(t, quote=False)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)\s*\{sponsored\}',
               lambda m: f'<a href="{m.group(2).replace("&","&amp;")}" target="_blank" '
                         f'rel="noopener sponsored">{m.group(1)}</a>', t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
               lambda m: f'<a href="{m.group(2).replace("&","&amp;")}">{m.group(1)}</a>', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', t)
    return t


def md_to_blocks(md: str):
    """Yield (kind, payload) blocks from the article body."""
    lines = md.split('\n')
    i, out = 0, []
    while i < len(lines):
        ln = lines[i]
        if ln.startswith('## '):
            out.append(('h2', ln[3:].strip())); i += 1
        elif ln.startswith('### '):
            out.append(('h3', ln[4:].strip())); i += 1
        elif ln.startswith('> '):
            buf = []
            while i < len(lines) and lines[i].startswith('>'):
                buf.append(lines[i].lstrip('>').strip()); i += 1
            out.append(('callout', [b for b in buf if b]))
        elif re.match(r'^[-*] ', ln):
            buf = []
            while i < len(lines) and re.match(r'^[-*] ', lines[i]):
                buf.append(lines[i][2:].strip()); i += 1
            out.append(('ul', buf))
        elif ln.strip() in ('', '---'):
            i += 1
        elif ln.startswith('**Lead**') or ln.startswith('**Intro**'):
            i += 1
        else:
            buf = []
            while i < len(lines) and lines[i].strip() and not lines[i].startswith(('#', '>', '- ', '* ')):
                buf.append(lines[i].strip()); i += 1
            out.append(('p', ' '.join(buf)))
    return out


def parse_draft(path):
    raw = open(path, encoding='utf-8').read()
    meta = {}
    for k, pat in [('slug', r'- Slug:\s*(\S+)'),
                   ('title', r'- Title tag[^:]*:\s*(.+)'),
                   ('desc', r'- Meta description[^:]*:\s*(.+)'),
                   ('kw', r'- Primary keyword:\s*(.+)')]:
        m = re.search(pat, raw)
        meta[k] = m.group(1).strip() if m else ''
    h1 = re.search(r'^# (.+)$', raw, re.M).group(1).strip()
    body = raw.split('\n---\n', 1)[1]        # everything after the SEO block
    body = re.split(r'\*\*BUILD NOTES\*\*', body)[0]
    body = re.split(r'\*\*Disclosure\*\*', body)[0]
    return meta, h1, body


# ─────────────────────────── page shell ───────────────────────────
def shell():
    soup = BeautifulSoup(open(LANDING, encoding='utf-8').read(), 'lxml')
    css = str(soup.find('style'))
    header = str(soup.find('header', class_='site'))
    footer = str(soup.find('footer', class_='site'))
    sticky = str(soup.find('div', class_='sticky'))
    return css, header, footer, sticky


ARTICLE_CSS = """
/* ---------- ARTICLE ---------- */
.crumb{font-size:13.5px;color:var(--ink3);padding:16px 0 0}
.crumb a{color:var(--ink2)}
article{max-width:760px;margin:0 auto;padding:0 20px 20px}
article h1{font-size:clamp(29px,4.4vw,42px);margin:14px 0 18px}
article .meta-line{font-size:14px;color:var(--ink3);margin-bottom:26px;
  padding-bottom:22px;border-bottom:1px solid var(--line)}
article h2{font-size:clamp(22px,2.9vw,28px);margin:40px 0 12px}
article h3{font-size:19px;margin:26px 0 8px}
article p{margin:0 0 18px}
article ul{margin:0 0 20px;padding-left:22px}
article li{margin:7px 0}
article figure{margin:26px 0}
article figure img{width:100%;border-radius:var(--rl)}
article figcaption{font-size:13.5px;color:var(--ink3);margin-top:8px;text-align:center}
.callout{border:2px solid var(--blue-soft);background:linear-gradient(180deg,#fff,var(--blue-soft));
  border-radius:var(--rl);padding:22px 24px;margin:28px 0}
.callout p{margin:0 0 10px;font-size:16px}
.callout p:last-child{margin:0}
.prod{border:1px solid var(--line);border-radius:var(--rl);background:#fff;
  padding:24px;margin:32px 0;box-shadow:var(--shadow)}
.prod h3{margin:8px 0 10px;font-size:21px}
.quote{border-left:3px solid var(--sand);padding:2px 0 2px 16px;margin:18px 0;
  font-size:15.5px;color:var(--ink2);font-style:italic}
.next{background:var(--soft);border-radius:var(--rl);padding:22px 24px;margin:32px 0}
.next ul{list-style:none;padding:0;margin:0}
.next li{margin:10px 0;font-size:15.5px}
.authorbox{display:flex;gap:18px;align-items:flex-start;border-top:1px solid var(--line);
  padding-top:26px;margin-top:40px}
.authorbox img{width:76px;height:76px;border-radius:50%;flex:0 0 auto;object-fit:cover}
.authorbox p{font-size:15px;color:var(--ink2);margin:0 0 8px}
.discl{font-size:13.5px;color:var(--ink3);border-top:1px solid var(--line);
  padding-top:18px;margin-top:28px;line-height:1.55}

/* article hero (dark photo, like the MSM abbey page) */
.ahero{position:relative;background:var(--navy);color:#fff;overflow:hidden}
.ahero img.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:.72}
.ahero .scrim{position:absolute;inset:0;
  background:linear-gradient(180deg,rgba(14,28,43,.80) 0%,rgba(14,28,43,.66) 45%,rgba(14,28,43,.94) 100%)}
.ahero .inner{position:relative;max-width:820px;margin:0 auto;padding:26px 20px 44px}
.ahero .crumb{color:#a9c2d8;padding:0 0 14px}
.ahero .crumb a{color:#cfe0ee}
.ahero h1{font-size:clamp(28px,4.4vw,44px);margin:0 0 16px;max-width:20ch}
.ahero .lede{color:#c8d9e8;font-size:19px;max-width:56ch;margin:0 0 18px}
.byline{font-size:14px;color:#9fb6c9;margin:0 0 24px}
.byline strong{color:#dbe8f4;font-weight:600}

/* full-width inline CTA button under a section */
.inline-cta{margin:22px 0 26px}

/* OTA / product card, icon rows with dividers */
.pcard{border:1px solid var(--line);border-radius:var(--rl);background:#fff;
  box-shadow:var(--shadow);overflow:hidden;margin:32px 0}
.pcard .grid{display:grid;grid-template-columns:minmax(0,38%) 1fr}
.pcard .grid>img{width:100%;height:100%;object-fit:cover;min-height:240px}
.pcard .in{padding:24px}
.pcard .rate{font-size:14px;color:var(--ink2);margin-bottom:12px}
.pcard .rate b{color:var(--sand)}
.pcard h3{font-size:21px;margin:0 0 6px;display:flex;flex-wrap:wrap;align-items:center;gap:10px}
.pill{background:var(--green-soft,#e3f5ee);color:#0d6b4f;font-size:12px;font-weight:700;
  padding:3px 10px;border-radius:20px;letter-spacing:.3px}
.pcard .sub{font-size:14.5px;color:var(--ink3);margin:0 0 12px}
.pcard .from{font-size:22px;font-weight:700;margin:0 0 16px}
.pcard .from small{font-size:15px;font-weight:500;color:var(--ink2)}
.frow{display:flex;gap:12px;align-items:flex-start;padding:11px 0;border-top:1px solid var(--line);
  font-size:15px}
.frow:first-of-type{border-top:0}
.frow svg{flex:0 0 auto;width:19px;height:19px;stroke:var(--blue);fill:none;
  stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;margin-top:2px}
.pcard .btn{margin-top:18px}

/* closing "Ready to …" banner */
.ready{border-radius:var(--rl);overflow:hidden;margin:36px 0;border:1px solid var(--line);
  box-shadow:var(--shadow)}
.ready .top{background:linear-gradient(135deg,#1974d1,#1668c1);color:#fff;padding:24px 26px}
.ready .top h3{margin:0 0 6px;font-size:22px;color:#fff}
.ready .top p{margin:0;color:#dbe9f8;font-size:16px}
.ready .btns{background:#fff;padding:20px 26px 24px;display:flex;flex-direction:column;gap:11px}
.ready .btns .btn{width:100%}
.ready .btns .btn.solid{background:#12558f;border-color:#12558f}
@media(max-width:700px){.pcard .grid{grid-template-columns:1fr}}
"""


def render(draft_path):
    meta, h1, body = parse_draft(draft_path)
    slug = meta['slug'].strip('/')
    css, header, footer, sticky = shell()

    blocks = md_to_blocks(body)

    # split off the trailing sections we render as custom components
    html, faq, nxt = [], [], []
    mode = 'body'
    for kind, payload in blocks:
        if kind == 'h2':
            low = payload.lower()
            if low.startswith('frequently asked'): mode = 'faq'; continue
            if low.startswith('continue exploring'): mode = 'next'; continue
            if low.startswith('the audio guide'): mode = 'prod'; html.append(('prod_open', payload)); continue
            mode = 'body'
        if mode == 'faq': faq.append((kind, payload))
        elif mode == 'next': nxt.append((kind, payload))
        else: html.append((kind, payload))

    IMG = {  # section heading -> image
        '09:45': ('half-timbered-houses-and-canals-in-petite-france',
                  'Half-timbered tanners’ houses along a canal in Petite France, Strasbourg'),
        '12:30': ('stained-glass-windows-inside-strasbourg-cathedral',
                  'Medieval stained glass inside Strasbourg Cathedral'),
        '16:30': ('img20221220201422', 'Strasbourg Cathedral lit at night, seen from the square'),
    }

    lede = next((inline(p) for k, p in html if k == 'p'), '')
    html = [(k, p) for k, p in html if not (k == 'p' and inline(p) == lede)]
    mins = max(1, round(len(re.sub(r'<[^>]+>', ' ', body).split()) / 230))
    out, seen_glance = [], False
    for kind, p in html:
        if kind == 'prod_open':
            out.append(f'<h2>{inline(p)}</h2>')      # keep the written section, Eugene preferred it
            continue
        if kind == 'h2':
            out.append(f'<h2>{inline(p)}</h2>')
            if p.startswith('08:30'):
                out[-1] = f'<h2 id="route">{inline(p)}</h2>'
            if p.startswith('13:15'):
                out.append(BOAT_CARD)                # the boat card sits with the boat warning
            if p.startswith('16:30'):
                out.append(AUDIO_CARD)               # the audio card sits mid-article, far from the closing banner
            for key, (f, alt) in IMG.items():
                if p.startswith(key):
                    out.append(f'<figure><img src="../img/{f}-wide.webp" alt="{alt}" '
                               f'width="1024" height="683" loading="lazy"></figure>')
        elif kind == 'h3': out.append(f'<h3>{inline(p)}</h3>')
        elif kind == 'ul':
            out.append('<ul>' + ''.join(f'<li>{inline(x)}</li>' for x in p) + '</ul>')
            if not seen_glance:
                seen_glance = True
                out.append(f'<div class="inline-cta"><a class="btn block" href="{GYG}" '
                           'target="_blank" rel="noopener sponsored">'
                           'Compare Strasbourg tours &amp; cruises →</a></div>')
        elif kind == 'callout':
            items = [x for x in p if not x.startswith('**TICKET CALLOUT**')]
            out.append('<div class="callout">' + ''.join(f'<p>{inline(x)}</p>' for x in items) + '</div>')
        elif kind == 'p':
            if p.startswith('"') or p.startswith('“'):
                out.append(f'<p class="quote">{inline(p)}</p>')
            else:
                out.append(f'<p>{inline(p)}</p>')

    # FAQ
    faq_html, faq_ld, q = [], [], None
    def strip(x): return ihtml.unescape(re.sub('<[^>]+>', '', inline(x)))
    for kind, p in faq:
        if kind != 'p':
            continue
        m = re.fullmatch(r'\*\*(.+?)\*\*\s*(.*)', p.strip(), re.S)
        if m and not m.group(2):          # a question on its own line
            q = m.group(1).strip(); continue
        if m and m.group(2):              # question and answer on one line
            q, a = m.group(1).strip(), m.group(2).strip()
        elif q:                           # answer paragraph following the question
            a = p.strip()
        else:
            continue
        faq_html.append(f'<details class="faq"><summary>{inline(q)}</summary>'
                        f'<div class="a"><p>{inline(a)}</p></div></details>')
        faq_ld.append({"@type": "Question", "name": strip(q),
                       "acceptedAnswer": {"@type": "Answer", "text": strip(a)}})
        q = None

    next_html = ''.join(f'<li>{inline(x)}</li>' for k, p in nxt if k == 'ul' for x in p)

    alts = '\n'.join(
        f'<link rel="alternate" hreflang="{l}" href="{DOMAIN}/{"" if l=="en" else l+"/"}{slug}/">'
        for l in LANGS)
    alts += f'\n<link rel="alternate" hreflang="x-default" href="{DOMAIN}/{slug}/">'

    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Article", "headline": h1, "description": meta['desc'],
         "inLanguage": "en", "datePublished": "2026-07-29", "dateModified": "2026-07-29",
         "image": f"{DOMAIN}/img/half-timbered-houses-and-canals-in-petite-france-wide.webp",
         "author": {"@type": "Person", "name": "Eugene",
                    "description": "16 years in France, former tour guide, author of the TouringBee Strasbourg audio tour."},
         "publisher": {"@type": "Organization", "name": "Strasbourg Walk",
                       "logo": {"@type": "ImageObject", "url": f"{DOMAIN}/img/logo.webp"}},
         "mainEntityOfPage": f"{DOMAIN}/{slug}/"},
        {"@type": "FAQPage", "mainEntity": faq_ld},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Strasbourg Walk", "item": f"{DOMAIN}/"},
            {"@type": "ListItem", "position": 2, "name": "Guides", "item": f"{DOMAIN}/guides/"},
            {"@type": "ListItem", "position": 3, "name": h1, "item": f"{DOMAIN}/{slug}/"}]}]}

    page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{meta['title']}</title>
<meta name="description" content="{meta['desc']}">
<link rel="canonical" href="{DOMAIN}/{slug}/">
{alts}
<meta property="og:type" content="article">
<meta property="og:url" content="{DOMAIN}/{slug}/">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="{h1}">
<meta property="og:description" content="{meta['desc']}">
<meta property="og:image" content="{DOMAIN}/img/half-timbered-houses-and-canals-in-petite-france-wide.webp">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/favicon-180.png">
<style>{css[7:-8]}{ARTICLE_CSS}</style>
</head>
<body>
{header}
<main>
<div class="ahero">
<img class="bg" src="../img/golden-reflections-in-the-canals-of-petite-france-hero-1152.webp" alt="" width="1140" height="855">
<div class="scrim"></div>
<div class="inner">
<div class="crumb"><a href="/">Home</a> › <a href="/guides/">Guides</a> › One Day in Strasbourg</div>
<h1>{h1}</h1>
<p class="lede">{lede}</p>
<div class="byline">By <strong>Eugene</strong> · Updated <strong>July 2026</strong> · <strong>{mins}-minute read</strong></div>
<div class="btnrow">
<a class="btn" href="{tb('hero')}" target="_blank" rel="noopener sponsored">Get the audio guide — €9.99</a>
<a class="btn dark" href="{GYG}" target="_blank" rel="noopener sponsored">Tours &amp; cruises</a>
<a class="btn ghost" href="#route">Jump to the route</a>
</div>
</div></div>
<article>
{''.join(out)}
{READY}\n<h2>Frequently asked questions</h2>
{''.join(faq_html)}
<div class="next"><h2 style="margin-top:0">Continue exploring</h2><ul>{next_html}</ul></div>
<div class="authorbox">
<img src="../img/author-eugene.webp" alt="Eugene, the author of this guide" width="76" height="76" loading="lazy">
<div><p><strong>Eugene</strong> has lived in France for 16 years and worked as a tour guide before founding the travel-content network paris10.travel. He wrote the TouringBee audio tour of Strasbourg.</p>
<p style="margin:0">Every price and opening time on this page is checked against the official source for the current year. Where a fact is not yet published, we say so instead of guessing.</p></div>
</div>
<p class="discl">Some links on this page are affiliate links (GetYourGuide, Booking.com, SNCF). If you book through them we may earn a small commission at no extra cost to you. It never affects what we recommend.</p>
</article>
</main>
{footer}
{sticky}
<script>
(function(){{var s=document.getElementById('sticky');
window.addEventListener('scroll',function(){{s.classList.toggle('on',window.scrollY>760);}},{{passive:true}});}})();
</script>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</body>
</html>'''

    # internal links to articles that are not published yet would be 404s;
    # send them to /guides/, where the card says "coming soon". Re-running the
    # renderer after a new article ships restores the direct link automatically.
    def relink(m):
        target = m.group(1)
        if target == slug or pathlib.Path(f'public/{target}/index.html').exists():
            return m.group(0)
        return 'href="/guides/"'
    page = re.sub(r'href="/([a-z0-9-]+)/"', relink, page)

    d = pathlib.Path('public') / slug
    d.mkdir(parents=True, exist_ok=True)
    (d / 'index.html').write_text(str(BeautifulSoup(page, 'lxml')), encoding='utf-8')
    print(f'  wrote public/{slug}/index.html  ({len(re.sub(chr(60)+"[^"+chr(62)+"]*"+chr(62),"",page).split())} words, {len(faq_ld)} FAQ)')


if __name__ == '__main__':
    for p in sys.argv[1:]:
        render(p)
