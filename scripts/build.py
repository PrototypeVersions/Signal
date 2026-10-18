#!/usr/bin/env python3
"""Build Signal's static publication. Python standard library only."""
import html, json, math, re, shutil
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlparse
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
BASE = 'https://prototypeversions.github.io/Signal'
e = lambda s: html.escape(str(s), quote=True)

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

def shell(content, edition, title='Signal — A clearer view of a changing world', prefix='./', canonical='', payload=True, description='A finite daily briefing on the world and the AI frontier. What changed, why it matters, and the evidence behind it.'):
    stamp = date.fromisoformat(edition['date']).strftime('%A, %d %B %Y')
    metadata = dict(edition=edition, editions=[{'date': x['date'], 'number': x['number'], 'count': len(x['stories'])} for x in EDITIONS], prefix=prefix)
    serialized = json.dumps(metadata, ensure_ascii=False).replace('<', '\\u003c')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(title)}</title><meta name="description" content="{e(description)}"><meta name="theme-color" content="#f5f3ed"><link rel="canonical" href="{BASE}/{canonical}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:type" content="website"><meta property="og:url" content="{BASE}/{canonical}"><link rel="icon" type="image/svg+xml" href="{prefix}assets/signal.svg"><link rel="stylesheet" href="{prefix}assets/style.css"><link rel="alternate" type="application/rss+xml" title="Signal editions" href="{prefix}feed.xml"></head>
    <body><a class="skip" href="#main">Skip to the briefing</a><div class="progress" aria-hidden="true"></div><header class="wrap"><div class="topline eyebrow"><span class="status"><i class="status-dot"></i> An independent daily briefing</span><span>{e(stamp)}</span><span class="timezone">A global perspective</span></div><div class="masthead"><a class="wordmark" href="{prefix}" aria-label="Signal home">SIGNAL<span class="signal-mark" aria-hidden="true"><i></i><i></i><i></i><i></i></span></a><div class="masthead-note"><p>The world, considered.<br><em>Once a day.</em></p><div class="edition-stamp">Volume 01<br>Edition {edition['number']:03}<br>Est. 2026</div></div></div><nav class="navigation" aria-label="Main navigation"><div class="navlinks"><a href="{prefix}#edition">The edition</a><a href="{prefix}#ai-frontier">AI frontier</a><a href="{prefix}archive/">Archive</a><a class="about-nav" href="{prefix}about/">Our approach</a></div><div class="nav-actions"><button class="catchup" data-dialog="catchup-dialog">Catch me up ↗</button><button class="theme" aria-label="Switch color theme" title="Switch color theme">◐</button></div></nav></header>
    {content}
    <footer class="footer"><div class="wrap"><a class="footer-brand" href="{prefix}">SIGNAL</a><p>AI-assisted. Evidence-linked. Open to correction.<br>An independent publication by Blake Myers.</p><div class="footer-links"><a href="{prefix}about/">Our approach</a><a href="{prefix}archive/">Archive</a><a href="{prefix}feed.xml">RSS ↗</a><a href="https://github.com/PrototypeVersions/Signal/issues/new?labels=correction&amp;title=Correction%3A%20" target="_blank" rel="noopener noreferrer">Corrections ↗</a></div></div></footer>
    <dialog id="story-dialog" aria-labelledby="story-dialog-title"><button class="close" aria-label="Close dialog">×</button><div id="story-dialog-content"></div></dialog>
    <dialog id="catchup-dialog" aria-labelledby="catchup-title"><button class="close" aria-label="Close dialog">×</button><div class="eyebrow">The thread, picked up</div><h2 id="catchup-title">Away for a few days?</h2><p>Choose the last edition you read. We’ll gather the developments published since then, grouped by story.</p><label for="since-date">Last edition read</label><select id="since-date" class="catchup-select"><option value="all">I’m new here</option>{''.join(f'<option value="{x["date"]}">{pretty(x["date"])}</option>' for x in reversed(EDITIONS))}</select><div id="catchup-results" aria-live="polite"></div></dialog>
    <div class="toast" role="status" hidden></div><script id="signal-data" type="application/json">{serialized}</script><script src="{prefix}assets/app.js" defer></script></body></html>'''

def home(edition, prefix='./', archived=False):
    world = [s for s in edition['stories'] if s['section'] == 'world']
    ai = [s for s in edition['stories'] if s['section'] == 'ai']
    still = [s for s in edition['stories'] if s['section'] == 'still']
    count = len(world) + len(ai)
    words = sum(len((s['body'] + s['whatChanged']).split()) for s in edition['stories'])
    minutes = max(3, math.ceil(words / 200))
    stamp = pretty(edition['date'])
    art = '''<div class="globe-scene"><canvas id="globe" role="img" aria-label="A slowly turning, illustrated globe"></canvas><span class="globe-tag top">A world in motion</span><span class="globe-tag bottom">A moment of clarity</span><span class="orbit-note">01 / A WIDER PERSPECTIVE</span></div>'''
    archive_note = f'<div class="latest-link">You’re reading an archived edition. <a href="{prefix}"><u>Read the latest →</u></a></div>' if archived else ''
    rc = edition.get('realityCheck')
    reality = f'''<div class="reality-check"><div class="eyebrow">The reality check ↗</div><p><strong>{e(rc['title'])}.</strong> {e(rc['text'])} <a href="{e(rc['url'])}" target="_blank" rel="noopener noreferrer"><u>Read the research ↗</u></a></p></div>''' if rc else ''
    still_html = ''.join(f'''<article class="still-card"><span class="eyebrow">{e(s['region'])}</span><h3>{e(s['title'])}</h3><p>{e(s['body'])}</p><button class="card-more" data-story="{s['id']}">Evidence & context ↗</button></article>''' for s in still)
    watch = ''.join(f'<div class="watch-item"><span>{i:02}</span><div><h3>{e(w["title"])}</h3><p>{e(w["text"])}</p></div></div>' for i,w in enumerate(edition['watch'],1))
    return archive_note + f'''<main id="main" class="wrap">{corrections(edition)}<section class="hero"><div class="hero-copy"><div class="eyebrow">Less noise. More understanding.</div><h1>A clearer view of<br>a <em>changing world.</em></h1><p>The developments worth your attention.<br>What changed. Why it matters. What comes next.</p><div class="hero-links"><a class="button" href="#edition">Read the edition <span>↓</span></a><a class="textlink" href="{prefix}about/">How we choose</a></div></div>{art}</section>
    <section class="issue-intro" id="edition"><div><div class="eyebrow">The daily edition / {edition['number']:03}</div><h2>{e(stamp)}</h2><div class="edition-meta"><span>{count} developments</span><span>≈ {minutes} min read</span><span>Sources checked {e(edition['cutoffLabel'])}</span></div></div><div><p class="opening">{e(edition['opening'])}</p><p style="margin-top:7px">{e(edition['note'])}</p></div></section><div class="stale-note" id="stale-note" hidden></div>
    <div class="toolbar"><div class="filters" aria-label="Filter the edition"><button data-filter="all" aria-pressed="true">All signals <span>{count}</span></button><button data-filter="world" aria-pressed="false">World <span>{len(world)}</span></button><button data-filter="ai" aria-pressed="false">AI <span>{len(ai)}</span></button></div><div class="reading-toggle" aria-label="Reading depth"><button data-mode="briefing" aria-pressed="true">Full briefing</button><button data-mode="quick" aria-pressed="false">Quick scan</button></div></div>
    <section class="story-grid world-grid" aria-label="World developments">{''.join(card(s,i+1,prefix,i==0) for i,s in enumerate(world))}</section>
    <section class="ai-section" id="ai-frontier"><div class="section-head"><div><div class="eyebrow">The next chapter / Artificial intelligence</div><h2>At the frontier.</h2></div><p>What AI can do. What it actually did.<br>And the distance between the two.</p></div><div class="story-grid">{''.join(card(s,len(world)+i+1,prefix) for i,s in enumerate(ai))}</div>{reality}</section>
    <div class="below"><section><div class="eyebrow">Beyond the news cycle</div><h2>Still matters.</h2>{still_html or '<p>No continuing-priority entry in this edition.</p>'}</section><section><div class="eyebrow">The next signals</div><h2>What we’re watching.</h2>{watch}</section></div>
    <section class="endnote"><div><h2>You’re caught up. <em>Go live your day.</em></h2><p>One considered edition. A natural place to stop.</p></div><div class="endnote-actions"><button class="textlink" id="share-edition">Share this edition ↗</button><a class="textlink" href="{prefix}archive/">Explore the archive →</a></div></section></main>'''

def article(s, edition, history):
    timeline = ''.join(f'<div class="archive-row"><div><a href="../../editions/{x["date"]}/#{s["id"]}">{pretty(x["date"])}</a><p>{e(item["whatChanged"])}</p></div></div>' for x,item in history)
    return f'''<main class="wrap" id="main"><article class="article-page"><a class="article-back" href="../../">← Back to the latest edition</a><div class="eyebrow">{e(s['region'])} / {e(s['category'])}</div><h1>{e(s['title'])}</h1><p class="source-note">Published in Signal on {pretty(edition['date'])} · Event: {e(s['eventDate'])}</p><p class="article-summary">{e(s['body'])}</p><h2>What changed</h2><p>{e(s['whatChanged'])}</p><h2>Why it matters</h2><p class="source-note">Editorial assessment</p><p>{e(s['whyMatters'])}</p><h2>What remains uncertain</h2><p>{e(s['uncertainty'])}</p><h2>Watch next</h2><p>{e(s['watchNext'])}</p>{corrections(edition,s["id"])}<h2>Sources & evidence</h2>{evidence(s)}<h2>The story so far</h2>{timeline}<p class="source-note">Each dated edition preserves what we reported at the time. Corrections are recorded explicitly.</p></article></main>'''

ABOUT = '''<main class="wrap" id="main"><article class="article-page"><div class="eyebrow">The editorial promise</div><h1>Attention is finite.<br><em>Spend it well.</em></h1><p class="article-summary">Signal is an independent, AI-assisted briefing by Blake Myers. It follows consequential changes in the world and at the AI frontier, in one finite daily edition.</p><h2>Change, with context</h2><p>We ask what is new, how strong the evidence is, and what the development could change. A quieter day can mean a shorter edition. An enduring crisis can deserve attention even when there is no fresh headline.</p><h2>Evidence before certainty</h2><p>Every item links to its sources. We prioritize primary documents and established reporting, seek independent corroboration, and distinguish an announcement from a demonstrated result. Sources repeating the same original account are not independent confirmation. Company research is labeled as such.</p><h2>Facts and judgments</h2><p>The report and “What changed” describe available evidence. “Why it matters” and “Watch next” are editorial assessments. We show uncertainties instead of manufacturing precise importance scores or unsupported probabilities.</p><h2>A publication with a memory</h2><p>Daily editions are retained in the archive. Continuing stories use stable identifiers so their developments can be followed across editions. The first edition starts that record; it does not invent a past.</p><h2>How this prototype is produced</h2><p>Research, synthesis and source checks use AI assistance. AI checks can miss errors. The publication is an early editorial experiment, not a substitute for original reporting. Follow the linked sources for their full reporting and context. During the trial, subsequent editions are drafted for review before publication.</p><h2>Corrections belong in the open</h2><p>If a claim is wrong, we correct it and record what changed. We do not silently erase mistakes from the historical record. <a href="https://github.com/PrototypeVersions/Signal/issues/new?labels=correction&amp;title=Correction%3A%20" target="_blank" rel="noopener noreferrer">Report an error on GitHub ↗</a></p><h2>Your reading stays yours</h2><p>This prototype has no advertising or analytics scripts. Theme preferences are saved only in your browser. Catch-up is based on the edition you select. Google Fonts supplies the typography; source links take you to their respective publishers. Your browser and hosting provider may retain ordinary access logs.</p><h2>Read at your own pace</h2><p>Use Quick scan for the changes alone, Full briefing for summaries and assessments, or Evidence & context for the full source trail. Subscribe through the <a href="../feed.xml">RSS feed</a> to follow new editions.</p></article></main>'''

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
        write(f'editions/{edition["date"]}/index.html',shell(home(edition,'../../',True),edition,f'Signal — {pretty(edition["date"])}','../../',f'editions/{edition["date"]}/'))
    index = {}
    for edition in EDITIONS:
        for s in edition['stories']: index.setdefault(s['id'],[]).append((edition,s))
    for slug,history in index.items():
        edition,s = history[-1]
        write(f'stories/{slug}/index.html',shell(article(s,edition,history),edition,s['title']+' — Signal','../../',f'stories/{slug}/',description=s['body']))
    rows = ''.join(f'<div class="archive-row"><a href="../editions/{x["date"]}/">{pretty(x["date"])}</a><span>Edition {x["number"]:03} · {len(x["stories"])} stories ↗</span></div>' for x in reversed(EDITIONS))
    write('archive/index.html',shell(f'<main class="wrap" id="main"><div class="eyebrow" style="margin-top:45px">The record, kept</div><h1 class="archive-title">A world in chapters.</h1><p>Every edition, preserved. A little perspective over time.</p><div class="archive-list">{rows}</div></main>',latest,'The archive — Signal','../','archive/'))
    write('about/index.html',shell(ABOUT,latest,'Our approach — Signal','../','about/'))
    write('data/history.json',json.dumps(EDITIONS,ensure_ascii=False))
    items=''.join(f'<item><title>{xml_escape("Signal — "+pretty(x["date"]))}</title><link>{BASE}/editions/{x["date"]}/</link><guid>{BASE}/editions/{x["date"]}/</guid><description>{xml_escape(x["opening"])}</description></item>' for x in reversed(EDITIONS))
    write('feed.xml',f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Signal</title><link>{BASE}/</link><description>A clearer view of a changing world.</description><language>en</language>{items}</channel></rss>')
    paths=['','archive/','about/']+[f'stories/{s}/' for s in index]+[f'editions/{x["date"]}/' for x in EDITIONS]
    write('sitemap.xml','<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{BASE}/{x}</loc></url>' for x in paths)+'</urlset>')
    write('robots.txt',f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n')
    write('.nojekyll','')
    write('404.html',shell('<main class="wrap article-page" id="main"><h1>This page hasn’t made the edition.</h1><p><a href="/Signal/">Return to Signal →</a></p></main>',latest,'Page not found — Signal','/Signal/'))
    print(f'Built {len(EDITIONS)} edition(s), {len(index)} story pages and {len(paths)} indexed pages.')
