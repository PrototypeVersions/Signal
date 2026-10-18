#!/usr/bin/env python3
"""Build The Signal's static publication. Python standard library only."""
import html, json, math, re, shutil, hashlib
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlparse
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
BASE = 'https://prototypeversions.github.io/Signal'
e = lambda s: html.escape(str(s), quote=True)
ASSET_VERSION = hashlib.sha256(((ROOT/'assets/style.css').read_text() + (ROOT/'assets/app.js').read_text()).encode()).hexdigest()[:12]

def validate(edition):
    date.fromisoformat(edition['date'])
    assert isinstance(edition['number'], int) and edition['number'] > 0
    cutoff = datetime.fromisoformat(edition['cutoff'].replace('Z', '+00:00'))
    assert cutoff.tzinfo is not None, 'Cutoff must include a timezone'
    assert len(edition['stories']) >= 1, 'An edition needs verified stories'
    ids = set()
    for s in edition['stories']:
        assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', s['id']), 'Unsafe story slug'
        assert s['id'] not in ids, 'Duplicate story id'
        ids.add(s['id'])
        assert s['section'] in ('world', 'ai', 'still')
        for field in ('title', 'body', 'whatChanged', 'whyMatters', 'uncertainty', 'watchNext', 'eventDate', 'category', 'region', 'status'):
            assert isinstance(s[field], str) and s[field].strip(), f'Missing {field}'
        assert s['sources'], 'Every story needs sources'
        for source in s['sources']:
            assert urlparse(source['url']).scheme == 'https' and urlparse(source['url']).netloc
            assert source['title'] and source['publisher'] and source['publishedAt']
    assert edition['watch'], 'Missing watch list'
    if edition.get('cover'):
        cover = edition['cover']
        assert cover['storyId'] in ids, 'Cover must reference an edition story'
        assert re.fullmatch(r'assets/[a-zA-Z0-9._-]+\.(jpg|jpeg|png|webp|svg)', cover['asset'])
        assert (ROOT / cover['asset']).is_file(), 'Missing cover image'
        assert cover['alt'] and cover['credit']
    for s in edition['stories']:
        for point in s.get('locations', []):
            assert -180 <= point['lon'] <= 180 and -90 <= point['lat'] <= 90
            assert point['label']

def write(path, content):
    target = OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding='utf-8')

def pretty(d):
    return date.fromisoformat(d).strftime('%B %d, %Y').replace(' 0', ' ')

def source_links(s):
    return '<div class="sources-inline">' + ''.join(f'<a href="{e(x["url"])}" target="_blank" rel="noopener noreferrer">{e(x["publisher"])} ↗</a>' for x in s['sources']) + '</div>'

def evidence(s):
    return ''.join(f'<div class="evidence"><a href="{e(x["url"])}" target="_blank" rel="noopener noreferrer">{e(x["title"])} ↗</a><small>{e(x["publisher"])} · {e(x["publishedAt"])} · {e(x["kind"])}</small></div>' for x in s['sources'])


def corrections(edition, story_id=None):
    items = [c for c in edition.get('corrections', []) if story_id is None or c['storyId'] == story_id]
    if not items: return ''
    return '<aside class="stale-note"><strong>Corrections to this edition</strong>' + ''.join(f'<p>{e(c["date"])} · Previously: {e(c["original"])}<br>Corrected: {e(c["replacement"])}<br>{e(c["reason"])}</p>' for c in items) + '</aside>'


def card(s, n, prefix, lead=False):
    badge = ' major' if s['status'] == 'Major development' else ''
    return f'''<article class="story-card{' lead' if lead else ''}" id="{e(s['id'])}" data-section="{e(s['section'])}">
    <div class="kicker"><span class="eyebrow">{e(s['region'])} / {e(s['category'])}</span><span class="number">{n:02}</span></div>
    <h3><a href="{prefix}stories/{s['id']}/">{e(s['title'])}</a></h3>
    <p class="summary">{e(s['body'])}</p>
    <div class="change"><p><strong>What changed</strong><br>{e(s['whatChanged'])}</p></div>
    <div class="context"><p><strong>Why it matters · our assessment</strong><br>{e(s['whyMatters'])}</p><p><strong>Still uncertain</strong><br>{e(s['uncertainty'])}</p>{source_links(s)}</div>
    <div class="card-foot"><span class="badge{badge}">{e(s['status'])}</span><button class="card-more" data-story="{e(s['id'])}" aria-label="Evidence and context: {e(s['title'])}">Evidence & context <span>↗</span></button></div>
    </article>'''

def shell(content, edition, title='The Signal — The world, considered. Once a day.', prefix='./', canonical='', payload=True, description='A finite daily briefing on the world and the AI frontier. What changed, why it matters, and the evidence behind it.'):
    stamp = date.fromisoformat(edition['date']).strftime('%A, %d %B %Y')
    metadata = dict(edition=edition, editions=[{'date': x['date'], 'number': x['number'], 'count': len(x['stories'])} for x in EDITIONS], prefix=prefix)
    serialized = json.dumps(metadata, ensure_ascii=False).replace('<', '\\u003c')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(title)}</title><meta name="description" content="{e(description)}"><meta name="theme-color" content="#f5f3ed"><link rel="canonical" href="{BASE}/{canonical}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:site_name" content="The Signal"><meta property="og:type" content="website"><meta property="og:url" content="{BASE}/{canonical}"><link rel="icon" type="image/svg+xml" href="{prefix}assets/signal.svg"><link rel="stylesheet" href="{prefix}assets/style.css?v={ASSET_VERSION}"><link rel="alternate" type="application/rss+xml" title="The Signal editions" href="{prefix}feed.xml"></head>
    <body><a class="skip" href="#main">Skip to the briefing</a><div class="progress" aria-hidden="true"></div><header class="wrap"><div class="topline eyebrow"><span class="status"><i class="status-dot"></i> An independent daily briefing</span><span>{e(stamp)}</span><span class="timezone">A global perspective</span></div><div class="masthead"><a class="wordmark" href="{prefix}" aria-label="The Signal home"><span class="wordmark-the">THE</span><span>SIGNAL</span><span class="signal-mark" aria-hidden="true"><i></i><i></i><i></i><i></i></span></a><div class="masthead-note"><p>The world, considered.<br><em>Once a day.</em></p><div class="edition-stamp">Volume 01<br>Edition {edition['number']:03}<br>Est. 2026</div></div></div><nav class="navigation" aria-label="Main navigation"><div class="navlinks"><a href="{prefix}#edition">The edition</a><a href="{prefix}#ai-frontier">AI frontier</a><a href="{prefix}archive/">Archive</a><a class="about-nav" href="{prefix}about/">Our approach</a></div><div class="nav-actions"><button class="catchup" data-dialog="catchup-dialog">Catch me up ↗</button><button class="theme" aria-label="Switch color theme" title="Switch color theme">◐</button></div></nav></header>
    {content}
    <footer class="footer"><div class="wrap"><a class="footer-brand" href="{prefix}"><span>THE</span> SIGNAL</a><p>AI-assisted. Evidence-linked. Open to correction.<br>An independent publication by Blake Myers.</p><div class="footer-links"><a href="{prefix}about/">Our approach</a><a href="{prefix}archive/">Archive</a><a href="{prefix}feed.xml">RSS ↗</a><a href="https://github.com/PrototypeVersions/Signal/issues/new?labels=correction&amp;title=Correction%3A%20" target="_blank" rel="noopener noreferrer">Corrections ↗</a></div></div></footer>
    <dialog id="story-dialog" aria-labelledby="story-dialog-title"><button class="close" aria-label="Close dialog">×</button><div id="story-dialog-content"></div></dialog>
    <dialog id="catchup-dialog" aria-labelledby="catchup-title"><button class="close" aria-label="Close dialog">×</button><div class="eyebrow">The thread, picked up</div><h2 id="catchup-title">Away for a few days?</h2><p>Choose the last edition you read. We’ll gather the developments published since then, grouped by story.</p><label for="since-date">Last edition read</label><select id="since-date" class="catchup-select"><option value="all">I’m new here</option>{''.join(f'<option value="{x["date"]}">{pretty(x["date"])}</option>' for x in reversed(EDITIONS))}</select><div id="catchup-results" aria-live="polite"></div></dialog>
    <div class="toast" role="status" hidden></div><script id="signal-data" type="application/json">{serialized}</script><script src="{prefix}assets/app.js?v={ASSET_VERSION}" defer></script></body></html>'''

def atlas(edition):
    # Generalized continental silhouettes, deliberately not political boundaries.
    land = [
        [(-168,70),(-145,70),(-125,60),(-110,69),(-80,74),(-53,53),(-68,44),(-81,25),(-99,18),(-112,29),(-126,49),(-151,60)],
        [(-81,12),(-68,11),(-48,-1),(-35,-10),(-47,-27),(-67,-55),(-75,-45),(-70,-18)],
        [(-54,60),(-45,59),(-20,78),(-41,84),(-62,78)],
        [(-17,36),(1,36),(12,38),(32,30),(43,12),(51,10),(39,-13),(31,-31),(18,-35),(12,-18),(4,5),(-15,12)],
        [(-10,36),(-9,44),(5,49),(9,58),(28,71),(45,69),(60,57),(92,76),(123,73),(175,60),(150,48),(139,35),(123,25),(108,5),(97,10),(81,8),(72,24),(51,27),(42,12),(33,30),(23,39)],
        [(112,-11),(129,-12),(137,-10),(154,-24),(146,-39),(130,-33),(114,-34)],
        [(47,-13),(50,-17),(47,-25),(44,-22)],[(130,31),(140,44),(146,45),(141,35)],
        [(-8,50),(-6,59),(1,58),(2,51)],[(165,-34),(176,-40),(172,-46),(166,-45)]
    ]
    project=lambda lon,lat: ((lon+180)*2.2,(84-lat)*2.45)
    paths=''.join('<path d="M'+' L'.join(f'{project(lon,lat)[0]:.1f},{project(lon,lat)[1]:.1f}' for lon,lat in poly)+' Z"/>' for poly in land)
    located=[(i,s) for i,s in enumerate(edition['stories'],1) if s.get('locations')]
    if not located: return ''
    pins=''
    for number,story in located:
        for point in story['locations']:
            x,y=project(point['lon'],point['lat'])
            pins+=f'<a href="#{e(story["id"])}" class="map-pin" data-atlas-id="{e(story["id"])}" aria-label="{e(point["label"])}: {e(story["title"])}"><circle cx="{x:.1f}" cy="{y:.1f}" r="15"/><text x="{x:.1f}" y="{y+4:.1f}" text-anchor="middle">{number:02}</text></a>'
    first=located[0][1]
    return f'''<section class="atlas" aria-labelledby="atlas-heading"><div class="atlas-top"><div class="eyebrow">The observatory / Reporting locations</div><span class="atlas-instruction">Choose a numbered location ↘</span></div><div class="atlas-layout"><div class="atlas-map"><h2 id="atlas-heading">A wider <em>perspective.</em></h2><svg viewBox="0 0 800 355" role="group" aria-label="Illustrated world map with story locations"><defs><pattern id="atlas-grid" width="44" height="44" patternUnits="userSpaceOnUse"><path d="M44 0H0V44" fill="none" stroke="#363c39" stroke-width=".6"/></pattern><pattern id="atlas-dots" width="5" height="5" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r=".8" fill="#82877b"/></pattern></defs><rect width="800" height="355" fill="url(#atlas-grid)"/><g fill="url(#atlas-dots)" stroke="#73796c" stroke-width=".5">{paths}</g>{pins}</svg><p class="atlas-caption">Selected locations · illustrated geography · numbers follow the edition</p></div><aside class="atlas-detail" aria-live="polite"><span class="eyebrow" id="atlas-region">{e(first['region'])}</span><h3 id="atlas-title">{e(first['title'])}</h3><p id="atlas-change">{e(first['whatChanged'])}</p><button class="atlas-read" data-story="{e(first['id'])}">Explore the story <span>↗</span></button></aside></div></section>'''

def home(edition, prefix='./', archived=False):
    world = [s for s in edition['stories'] if s['section'] == 'world']
    ai = [s for s in edition['stories'] if s['section'] == 'ai']
    still = [s for s in edition['stories'] if s['section'] == 'still']
    count = len(world) + len(ai)
    words = sum(len((' '.join(s[k] for k in ('body','whatChanged','whyMatters','uncertainty'))).split()) for s in edition['stories']) + sum(len(w['text'].split()) for w in edition['watch'])
    minutes = max(3, math.ceil(words / 200))
    lead=(world+ai)[0] if world or ai else still[0]
    cover=edition.get('cover')
    if cover and cover['storyId']==lead['id']:
        art=f'<figure class="cover-art"><img src="{prefix}{e(cover["asset"])}" alt="{e(cover["alt"])}" width="1536" height="1024" fetchpriority="high"><figcaption><span>{e(cover.get("caption","The daily cover"))}</span><span>{e(cover["credit"])}</span></figcaption></figure>'
    else:
        art=f'<div class="cover-art cover-typographic" role="img" aria-label="Typographic cover for edition {edition["number"]}"><span class="eyebrow">The daily cover</span><div class="cover-orbit" aria-hidden="true"></div><strong>{edition["number"]:03}</strong><span class="eyebrow">{e(pretty(edition["date"]))} / The Signal</span></div>'
    brief_choices=([s for s in world if s['id']!=lead['id']][:2]+[s for s in ai if s['id']!=lead['id']][:1])[:3]
    brief=''.join(f'<a class="brief-item" href="{prefix}stories/{item["id"]}/"><span>{edition["stories"].index(item)+1:02}</span><h3>{e(item["title"])}</h3><span class="brief-arrow">↗</span></a>' for item in brief_choices)
    archive_note = f'<div class="latest-link">You’re reading an archived edition. <a href="{prefix}"><u>Read the latest →</u></a></div>' if archived else ''
    rc = edition.get('realityCheck')
    reality = f'''<div class="reality-check"><div class="eyebrow">The reality check ↗</div><p><strong>{e(rc['title'])}.</strong> {e(rc['text'])} <a href="{e(rc['url'])}" target="_blank" rel="noopener noreferrer"><u>Read the research ↗</u></a></p></div>''' if rc else ''
    still_html = ''.join(f'''<article class="still-card" id="{s['id']}"><span class="eyebrow">{e(s['region'])}</span><h3>{e(s['title'])}</h3><p>{e(s['body'])}</p><button class="card-more" data-story="{s['id']}">Evidence & context ↗</button></article>''' for s in still)
    watch = ''.join(f'<div class="watch-item"><span>{i:02}</span><div><h3>{e(w["title"])}</h3><p>{e(w["text"])}</p></div></div>' for i,w in enumerate(edition['watch'],1))
    lead_number=edition['stories'].index(lead)+1
    world_cards=''.join(card(s,edition['stories'].index(s)+1,prefix) for s in world if s['id']!=lead['id'])
    ai_cards=''.join(card(s,edition['stories'].index(s)+1,prefix) for s in ai if s['id']!=lead['id'])
    return archive_note + f'''<main id="main" class="wrap">{corrections(edition)}
    <section class="issue-intro" id="edition"><div><div class="eyebrow">The daily edition / {edition['number']:03}</div><h2>{e(pretty(edition['date']))}</h2></div><div class="edition-meta"><span>{count} developments</span><span>≈ {minutes} min read</span><span>Checked {e(edition['cutoffLabel'])}</span></div></section><div class="stale-note" id="stale-note" hidden></div>
    <div class="toolbar"><div class="filters" aria-label="Filter the edition"><button data-filter="all" aria-pressed="true">All signals <span>{count}</span></button><button data-filter="world" aria-pressed="false">World <span>{len(world)}</span></button><button data-filter="ai" aria-pressed="false">AI <span>{len(ai)}</span></button></div><div class="reading-toggle" aria-label="Reading depth"><button data-mode="briefing" aria-pressed="true">Full briefing</button><button data-mode="quick" aria-pressed="false">Quick scan</button></div></div>
    <section class="lead-story" id="{lead['id']}" data-section="{lead['section']}" aria-labelledby="lead-title"><div class="cover-visual">{art}<div class="daily-brief"><div class="eyebrow">Also in this edition</div>{brief}</div></div><div class="cover-copy"><div class="kicker"><span class="eyebrow">The lead / {e(lead['category'])}</span><span class="number">{lead_number:02}</span></div><h1 id="lead-title"><a href="{prefix}stories/{lead['id']}/">{e(lead['title'])}</a></h1><p class="lead-region eyebrow">{e(lead['region'])}</p><p class="summary">{e(lead['body'])}</p><div class="change"><span class="change-arrow" aria-hidden="true">↳</span><p><strong>What changed</strong><br>{e(lead['whatChanged'])}</p></div><div class="lead-context context"><p><strong>Why it matters · our assessment</strong><br>{e(lead['whyMatters'])}</p><p><strong>Still uncertain</strong><br>{e(lead['uncertainty'])}</p></div><div class="lead-actions"><button class="button" data-story="{lead['id']}">Evidence & context <span>↗</span></button>{source_links(lead)}</div></div></section>
    <div class="edition-note"><span class="eyebrow">The editorial note</span><p>{e(edition['note'])}</p></div>
    <section class="world-grid-section"><div class="section-title"><div><span class="eyebrow">The world / In focus</span><h2>Across the world.</h2></div><span class="section-number">01 — {len(world):02}</span></div><div class="story-grid world-grid" aria-label="World developments">{world_cards}</div></section>
    {atlas(edition)}
    <section class="ai-section" id="ai-frontier"><div class="section-head"><div><div class="eyebrow">The next chapter / Artificial intelligence</div><h2>At the <em>frontier.</em></h2></div><div class="frontier-symbol" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></div><p>What AI can do. What it actually did.<br>And the distance between the two.</p></div><div class="story-grid">{ai_cards}</div>{reality}</section>
    <div class="below"><section><div class="eyebrow">Beyond the news cycle</div><h2>Still matters.</h2>{still_html or '<p>No continuing-priority entry in this edition.</p>'}</section><section><div class="eyebrow">The next signals</div><h2>What we’re watching.</h2>{watch}</section></div>
    <section class="endnote"><div class="endnote-mark" aria-hidden="true">✳</div><div><h2>You’re caught up.<br><em>Go live your day.</em></h2><p>One considered edition. A natural place to stop.</p></div><div class="endnote-actions"><button class="textlink" id="share-edition">Share this edition ↗</button><a class="textlink" href="{prefix}archive/">Explore the archive →</a></div></section></main>'''

def article(s, edition, history):
    timeline = ''.join(f'<div class="archive-row"><div><a href="../../editions/{x["date"]}/#{s["id"]}">{pretty(x["date"])}</a><p>{e(item["whatChanged"])}</p></div></div>' for x,item in history)
    return f'''<main class="wrap" id="main"><article class="article-page"><a class="article-back" href="../../">← Back to the latest edition</a><div class="eyebrow">{e(s['region'])} / {e(s['category'])}</div><h1>{e(s['title'])}</h1><p class="source-note">Published in The Signal on {pretty(edition['date'])} · Event: {e(s['eventDate'])}</p><p class="article-summary">{e(s['body'])}</p><h2>What changed</h2><p>{e(s['whatChanged'])}</p><h2>Why it matters</h2><p class="source-note">Editorial assessment</p><p>{e(s['whyMatters'])}</p><h2>What remains uncertain</h2><p>{e(s['uncertainty'])}</p><h2>Watch next</h2><p>{e(s['watchNext'])}</p>{corrections(edition,s["id"])}<h2>Sources & evidence</h2>{evidence(s)}<h2>The story so far</h2>{timeline}<p class="source-note">Each dated edition preserves what we reported at the time. Corrections are recorded explicitly.</p></article></main>'''

ABOUT = '''<main class="wrap" id="main"><article class="article-page"><div class="eyebrow">The editorial promise</div><h1>Attention is finite.<br><em>Spend it well.</em></h1><p class="article-summary">The Signal is an independent, AI-assisted briefing by Blake Myers. It follows consequential changes in the world and at the AI frontier, in one finite daily edition.</p><h2>Change, with context</h2><p>We ask what is new, how strong the evidence is, and what the development could change. A quieter day can mean a shorter edition. An enduring crisis can deserve attention even when there is no fresh headline.</p><h2>Evidence before certainty</h2><p>Every item links to its sources. We prioritize primary documents and established reporting, seek independent corroboration, and distinguish an announcement from a demonstrated result. Sources repeating the same original account are not independent confirmation. Company research is labeled as such.</p><h2>Facts and judgments</h2><p>The report and “What changed” describe available evidence. “Why it matters” and “Watch next” are editorial assessments. We show uncertainties instead of manufacturing precise importance scores or unsupported probabilities.</p><h2>A publication with a memory</h2><p>Daily editions are retained in the archive. Continuing stories use stable identifiers so their developments can be followed across editions. The first edition starts that record; it does not invent a past.</p><h2>How this prototype is produced</h2><p>Research, synthesis and source checks use AI assistance. AI checks can miss errors. The publication is an early editorial experiment, not a substitute for original reporting. Follow the linked sources for their full reporting and context. During the trial, subsequent editions are drafted for review before publication.</p><h2>Corrections belong in the open</h2><p>If a claim is wrong, we correct it and record what changed. We do not silently erase mistakes from the historical record. <a href="https://github.com/PrototypeVersions/Signal/issues/new?labels=correction&amp;title=Correction%3A%20" target="_blank" rel="noopener noreferrer">Report an error on GitHub ↗</a></p><h2>Your reading stays yours</h2><p>This prototype has no advertising or analytics scripts. Theme preferences are saved only in your browser. Catch-up is based on the edition you select. Google Fonts supplies the typography; source links take you to their respective publishers. Your browser and hosting provider may retain ordinary access logs.</p><h2>Read at your own pace</h2><p>Use Quick scan for the changes alone, Full briefing for summaries and assessments, or Evidence & context for the full source trail. Subscribe through the <a href="../feed.xml">RSS feed</a> to follow new editions.</p></article></main>'''

if __name__ == '__main__':
    EDITIONS = [json.loads(p.read_text()) for p in sorted((ROOT/'data/editions').glob('*.json'))]
    assert EDITIONS, 'No editions to publish'
    for edition in EDITIONS: validate(edition)
    assert len({x['date'] for x in EDITIONS}) == len(EDITIONS)
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT/'assets',OUT/'assets')
    latest = EDITIONS[-1]
    write('index.html',shell(home(latest),latest))
    for edition in EDITIONS:
        write(f'editions/{edition["date"]}/index.html',shell(home(edition,'../../',True),edition,f'The Signal — {pretty(edition["date"])}','../../',f'editions/{edition["date"]}/'))
    index = {}
    for edition in EDITIONS:
        for s in edition['stories']: index.setdefault(s['id'],[]).append((edition,s))
    for slug,history in index.items():
        edition,s = history[-1]
        write(f'stories/{slug}/index.html',shell(article(s,edition,history),edition,s['title']+' — The Signal','../../',f'stories/{slug}/',description=s['body']))
    rows = ''.join(f'<div class="archive-row"><a href="../editions/{x["date"]}/">{pretty(x["date"])}</a><span>Edition {x["number"]:03} · {len(x["stories"])} stories ↗</span></div>' for x in reversed(EDITIONS))
    write('archive/index.html',shell(f'<main class="wrap" id="main"><div class="eyebrow" style="margin-top:45px">The record, kept</div><h1 class="archive-title">A world in chapters.</h1><p>Every edition, preserved. A little perspective over time.</p><div class="archive-list">{rows}</div></main>',latest,'The archive — The Signal','../','archive/'))
    write('about/index.html',shell(ABOUT,latest,'Our approach — The Signal','../','about/'))
    write('data/history.json',json.dumps(EDITIONS,ensure_ascii=False))
    items=''.join(f'<item><title>{xml_escape("The Signal — "+pretty(x["date"]))}</title><link>{BASE}/editions/{x["date"]}/</link><guid>{BASE}/editions/{x["date"]}/</guid><description>{xml_escape(x["opening"])}</description></item>' for x in reversed(EDITIONS))
    write('feed.xml',f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>The Signal</title><link>{BASE}/</link><description>A clearer view of a changing world.</description><language>en</language>{items}</channel></rss>')
    paths=['','archive/','about/']+[f'stories/{s}/' for s in index]+[f'editions/{x["date"]}/' for x in EDITIONS]
    write('sitemap.xml','<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{BASE}/{x}</loc></url>' for x in paths)+'</urlset>')
    write('robots.txt',f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n')
    write('.nojekyll','')
    write('404.html',shell('<main class="wrap article-page" id="main"><h1>This page hasn’t made the edition.</h1><p><a href="/Signal/">Return to The Signal →</a></p></main>',latest,'Page not found — The Signal','/Signal/'))
    print(f'Built {len(EDITIONS)} edition(s), {len(index)} story pages and {len(paths)} indexed pages.')
