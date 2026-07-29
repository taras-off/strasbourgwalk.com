#!/usr/bin/env python3
"""Compose /guides/ and the legal pages from the EN master's shared shell."""
import re, os, pathlib

M = open('public/index.html', encoding='utf-8').read()
CSS    = re.search(r'<style>.*?</style>', M, re.S).group(0)
HEADER = re.search(r'<!-- ═+ HEADER ═+ -->\s*(<header class="site">.*?</header>)', M, re.S).group(1)
FOOTER = re.search(r'<!-- ═+ FOOTER ═+ -->\s*(<footer class="site">.*?</footer>)', M, re.S).group(1)

TB = ("https://touringbee.com/product/city-tour-of-strasbourg/?wpam_id=42"
      "&amp;utm_source=strasbourgwalk&amp;utm_medium=referral&amp;utm_campaign={c}&amp;utm_content={p}")

def page(slug, title, desc, body, hreflang=True, noindex=False):
    canon = f'https://strasbourgwalk.com/{slug}/' if slug else 'https://strasbourgwalk.com/'
    alts = ''
    if hreflang:
        for l in ['en','fr','de','es','it','pt','pl','ru']:
            href = f'https://strasbourgwalk.com/{"" if l=="en" else l+"/"}{slug+"/" if slug else ""}'
            alts += f'\n<link rel="alternate" hreflang="{l}" href="{href}">'
        alts += f'\n<link rel="alternate" hreflang="x-default" href="https://strasbourgwalk.com/{slug+"/" if slug else ""}">'
    # header with the current page marked in the lang nav stays EN for the master
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">{'<meta name="robots" content="noindex,follow">' if noindex else ''}{alts}
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/favicon-180.png">
{CSS}
</head>
<body>
{HEADER}
<main>
{body}
</main>
{FOOTER}
</body>
</html>
'''

def write(slug, html):
    d = pathlib.Path('public')/slug if slug else pathlib.Path('public')
    d.mkdir(parents=True, exist_ok=True)
    (d/'index.html').write_text(html, encoding='utf-8')
    print('wrote', d/'index.html')

# ─────────────────────────── /guides/ ───────────────────────────
GUIDES = [
 ("one-day-in-strasbourg","One Day in Strasbourg: The Perfect Walking Itinerary","Morning to evening on the Grande Île, built around a route that actually works on foot."),
 ("strasbourg-walking-tour","Strasbourg Walking Tour: A Self-Guided Route","The old town on your own schedule — the full route, stop by stop, with what to look at."),
 ("strasbourg-cathedral","Strasbourg Cathedral: What to See Inside and Out","The facade, the nave, the 330-step climb — and why the second tower was never built."),
 ("strasbourg-astronomical-clock","The Astronomical Clock: Times, Tickets and Meaning","12:30 every day, €3, same-day tickets only. How the queue works and what you are watching."),
 ("petite-france-strasbourg","Petite France: What to See and Where to Walk","The tanners' quarter: the best bridges, the right light, and the name's grim origin."),
 ("things-to-do-in-strasbourg","Best Things to Do in Strasbourg","Ranked by what is actually worth your morning — not by what sells the most tickets."),
 ("strasbourg-old-town-grande-ile","Strasbourg Old Town: Grande Île on Foot","The UNESCO island end to end, and the streets most visitors never turn into."),
 ("is-strasbourg-worth-visiting","Is Strasbourg Worth Visiting?","The honest answer, including who will not enjoy it."),
 ("how-many-days-in-strasbourg","How Many Days Do You Need in Strasbourg?","One for the island, two with museums, three if you want Colmar or the wine route."),
 ("strasbourg-christmas-market","Strasbourg Christmas Market Guide","Europe's oldest, running since 1570 — the eight market squares and how to survive the crowds."),
 ("strasbourg-boat-tour","Boat Tour vs Walking Tour: Which Is Better?","Batorama's circuits compared — plus the 2026 pontoon change and why timed tickets catch people out."),
 ("strasbourg-food","What to Eat in Strasbourg: 15 Alsatian Dishes","Flammekueche, baeckeoffe, kougelhopf — what they are and where the locals actually go."),
 ("strasbourg-history","Strasbourg History: Why It Looks French and German","Free city, Louis XIV, the Kaiser, and back again — the short version that explains the buildings."),
 ("strasbourg-dancing-plague","The Dancing Plague of 1518: What Really Happened?","Four hundred people danced until they dropped. The city's response made it worse."),
 ("strasbourg-european-parliament","The European Parliament: Is It Worth Visiting?","Free, but there is one document rule that turns people away at the door."),
 ("strasbourg-to-colmar","Strasbourg to Colmar: Train, Car and a Day-Trip Plan","30 minutes by train, and how to spend the day once you are there."),
]
LIVE = {'one-day-in-strasbourg'}
def card(s, t, d):
    if s in LIVE:
        return (f'      <div class="tile"><div class="t">\n'
                f'        <h3><a href="/{s}/">{t}</a></h3><p>{d}</p>\n'
                f'      </div></div>')
    return (f'      <div class="tile"><div class="t">\n'
            f'        <span class="badge">Coming soon</span>\n'
            f'        <h3>{t}</h3><p>{d}</p>\n'
            f'      </div></div>')
cards = '\n'.join(card(s, t, d) for s, t, d in GUIDES)

write('guides', page('guides',
  'All Strasbourg Guides | TouringBee',
  'Every guide on Strasbourg Walk: the cathedral, the Christmas market, Petite France, getting there and where to stay — all fact-checked for 2026.',
  f'''<section>
  <div class="wrap">
    <h1 style="font-size:clamp(28px,4vw,38px)">All Strasbourg Guides</h1>
    <p class="lede">Detailed, fact-checked guides to visiting Strasbourg. New ones are added every week — each verified against the official source for the current year.</p>
    <div class="grid3">
{cards}
    </div>
    <div class="ticketbox" style="margin-top:34px">
      <span class="tag">Start here</span>
      <h3>Not sure where to begin?</h3>
      <p style="color:var(--ink2);margin:8px 0 16px">The pillar guide covers the whole city in one page: what to see, what it costs, how long you need and when to come.</p>
      <div class="btnrow">
        <a class="btn" href="/">Read the complete guide to Strasbourg</a>
        <a class="btn outline" href="{TB.format(c='guides', p='guides_cta')}" target="_blank" rel="noopener sponsored">Get the audio tour</a>
      </div>
    </div>
  </div>
</section>'''))

# ─────────────────────────── legal ───────────────────────────
write('privacy-policy', page('privacy-policy',
  'Privacy Policy | Strasbourg Walk',
  'How Strasbourg Walk handles data: what we collect, what we do not, and the third parties involved.',
  '''<section><div class="wrap" style="max-width:760px">
<h1>Privacy Policy</h1>
<p class="lede">Last updated 28 July 2026.</p>
<h3>Who we are</h3>
<p>Strasbourg Walk (strasbourgwalk.com) is an independent travel guide published as part of the TouringBee project. Touringbee Limited is registered in the Republic of Ireland, company number 660321. Contact: <a href="mailto:info@touringbee.com">info@touringbee.com</a>.</p>
<h3>What we collect</h3>
<p>We do not ask you to create an account, and we do not collect names, email addresses or payment details on this website. There is no newsletter sign-up and no contact form.</p>
<p>Our hosting provider (Cloudflare Pages) processes standard server request data — IP address, browser type, referring page and the time of the request — for security and to keep the site running. This is normal web-server logging and is not used to profile you.</p>
<h3>Cookies</h3>
<p>This website sets no advertising or analytics cookies of its own. If you click through to a partner (GetYourGuide, Booking.com, Tiqets, SNCF or TouringBee), that partner will set its own cookies on its own domain, including an affiliate-tracking cookie that records that you arrived from us. Those cookies are governed by the partner's privacy policy, not this one.</p>
<h3>Affiliate links</h3>
<p>Some outbound links on this site are affiliate links. See our <a href="/affiliate-disclosure/">Affiliate Disclosure</a> for the full list of partners and how it works.</p>
<h3>Embedded content</h3>
<p>Audio previews are served from this domain. We do not embed third-party video players, social media widgets, comment systems or tracking pixels.</p>
<h3>Your rights</h3>
<p>Under the GDPR you may request access to, correction of, or erasure of any personal data we hold about you. Because we hold no personal data beyond server logs, such a request will normally be answered by confirming that there is nothing on file. Write to <a href="mailto:info@touringbee.com">info@touringbee.com</a>.</p>
<h3>Changes</h3>
<p>If this policy changes we will update the date at the top of this page.</p>
</div></section>''', hreflang=False))

write('affiliate-disclosure', page('affiliate-disclosure',
  'Affiliate Disclosure | Strasbourg Walk',
  'Which links on Strasbourg Walk earn a commission, how much it costs you (nothing), and how it affects what we recommend (it does not).',
  '''<section><div class="wrap" style="max-width:760px">
<h1>Affiliate Disclosure</h1>
<p class="lede">Last updated 28 July 2026.</p>
<h3>The short version</h3>
<p>Some links on this site earn us a commission if you buy through them. You pay exactly the same price. It never changes what we recommend, and we do not accept payment for coverage.</p>
<h3>Who we work with</h3>
<ul class="ticks">
<li><strong>TouringBee</strong> — the Strasbourg audio tour is our own product, made by the company that publishes this site. We say so wherever we link to it.</li>
<li><strong>GetYourGuide</strong> — boat cruises, walking tours and Alsace day trips.</li>
<li><strong>Booking.com</strong> — hotels and car hire.</li>
<li><strong>Tiqets</strong> — attraction tickets, used on our Colmar and Alsace pages.</li>
<li><strong>SNCF</strong> (via Effiliation) — train tickets.</li>
</ul>
<h3>What we will not do</h3>
<p>We do not sell tickets that do not exist. Strasbourg Cathedral's astronomical clock and tower platform are sold on site only, on the day, and no operator anywhere can give you skip-the-line entry to either. Where the honest answer is "you cannot book this, just turn up early", that is what this site says — even though a booking link would earn more.</p>
<h3>How links are marked</h3>
<p>Every commercial outbound link carries <code>rel="sponsored"</code> and opens in a new tab, and every section containing them carries a visible disclosure line.</p>
<h3>Questions</h3>
<p>Write to <a href="mailto:info@touringbee.com">info@touringbee.com</a>.</p>
</div></section>''', hreflang=False))
