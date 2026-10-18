#!/usr/bin/env python3
"""Build The Signal's static publication. Python standard library only."""
import html, json, math, re, shutil, hashlib
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlparse
from xml.sax.saxutils import escape as xml_escape
from visuals import COUNTRY_IDS, prepare_visuals

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
BASE = 'https://prototypeversions.github.io/Signal'
e = lambda s: html.escape(str(s), quote=True)
ASSET_VERSION = hashlib.sha256(((ROOT/'assets/style.css').read_text() + (ROOT/'assets/app.js').read_text()).encode()).hexdigest()[:12]

def validate_image(image):
    asset = image['asset']
    assert re.fullmatch(r'assets/(?:[a-zA-Z0-9_-]+/)*[a-zA-Z0-9_-]+\.(jpg|jpeg|png|webp|svg)', asset), 'Unsafe image path'
    assert (ROOT / asset).is_file(), f'Missing image: {asset}'
    assert image['alt'].strip() and image['credit'].strip(), 'Images need alt text and credit'

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
        assert s['section'] in ('world', 'ai', 'frontiers', 'still')
        if s.get('field'): assert s['field'] in ('AI', 'Science', 'Medicine', 'Space', 'Energy')
        if s['section'] == 'frontiers': assert s.get('field'), 'Frontiers stories need a field tag'
        if 'hook' in s: assert isinstance(s['hook'], str) and s['hook'].strip()
        for field in ('title', 'body', 'whatChanged', 'whyMatters', 'uncertainty', 'watchNext', 'eventDate', 'category', 'region', 'status'):
            assert isinstance(s[field], str) and s[field].strip(), f'Missing {field}'
        assert s['sources'], 'Every story needs sources'
        for source in s['sources']:
            assert urlparse(source['url']).scheme == 'https' and urlparse(source['url']).netloc
            assert source['title'] and source['publisher'] and source['publishedAt']
        if s.get('image'): validate_image(s['image'])
        if 'report' in s:
            assert isinstance(s['report'], list) and s['report'], 'report must be a list of sections'
            for section in s['report']:
                assert isinstance(section.get('heading'), str) and section['heading'].strip(), 'Report sections need a heading'
                assert isinstance(section.get('paragraphs'), list) and section['paragraphs'], 'Report sections need paragraphs'
                assert all(isinstance(x, str) and x.strip() for x in section['paragraphs'])
        for update in s.get('updates', []):
            stamp = datetime.fromisoformat(update['at'].replace('Z', '+00:00'))
            assert stamp.tzinfo is not None, 'Update times need a timezone'
            assert isinstance(update.get('text'), str) and update['text'].strip(), 'Updates need text'
            for source in update.get('sources', []):
                assert urlparse(source['url']).scheme == 'https' and source['title'] and source['publisher'] and source['publishedAt']
        if 'keyFacts' in s:
            assert isinstance(s['keyFacts'], list) and 2 <= len(s['keyFacts']) <= 6, 'keyFacts needs 2 to 6 items'
            assert all(isinstance(x, str) and x.strip() for x in s['keyFacts'])
        if s.get('threadId'): assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', s['threadId']), 'Unsafe thread slug'
        for field in ('threadTitle','threadSummary'):
            if field in s: assert isinstance(s[field],str) and s[field].strip()
        if s.get('visual'):
            visual=s['visual']
            assert visual['type'] in ('map','bars')
            assert visual['title'] and visual['alt'] and visual['caption']
            if visual['type']=='map':
                west,south,east,north=visual['bounds']
                assert -180<=west<east<=180 and -90<=south<north<=90
                assert all(str(code) in COUNTRY_IDS for code in visual.get('countries',[])), 'Unknown country code'
                for point in visual.get('labels',[]):
                    assert west<=point['lon']<=east and south<=point['lat']<=north and point['label']
            else:
                assert visual['sourceUrl'] in [x['url'] for x in s['sources']], 'Chart must cite a story source'
                assert visual['measure'] and visual['unit'] and 1<=len(visual['values'])<=4
                assert all(isinstance(x['value'],(int,float)) and math.isfinite(x['value']) and x['value']>=0 and x['label'] for x in visual['values'])
    if edition.get('updatedAt'):
        assert datetime.fromisoformat(edition['updatedAt'].replace('Z', '+00:00')).tzinfo is not None, 'updatedAt needs a timezone'
        assert edition.get('updatedLabel'), 'updatedAt needs a readable updatedLabel'
    assert edition['watch'], 'Missing watch list'
    if edition.get('leadStoryId'): assert edition['leadStoryId'] in ids, 'Lead must reference an edition story'
    if edition.get('cover'):
        cover = edition['cover']
        assert cover['storyId'] in ids, 'Cover must reference an edition story'
        assert cover['storyId'] == lead_story(edition)['id'], 'Cover must match the selected lead'
        validate_image(cover)
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


def story_image(s, prefix, link=False):
    image = s.get('image')
    if not image: return ''
    img = f'<img src="{prefix}{e(image["asset"])}" alt="{e(image["alt"])}" width="1200" height="800" loading="lazy" decoding="async">'
    if link: img = f'<a href="{prefix}stories/{s["id"]}/">{img}</a>'
    visual=s.get('visual',{})
    credit=e(image['credit'])
    if visual.get('type')=='map': credit=f'{e(visual["caption"])} · <a href="https://www.naturalearthdata.com/" target="_blank" rel="noopener noreferrer">Natural Earth ↗</a>'
    elif visual.get('type')=='bars': credit=f'{e(visual["caption"])} <a href="{e(visual["sourceUrl"])}" target="_blank" rel="noopener noreferrer">Source ↗</a>'
    return f'<figure class="story-art visual-{e(visual.get("type","art"))}">{img}<figcaption>{credit}</figcaption></figure>'

def thread_key(s): return s.get('threadId',s['id'])

def update_label(u):
    return u.get('label') or 'Evening update'

def updates_inline(s):
    ups = s.get('updates', [])
    if not ups: return ''
    return '<div class="story-updates">' + ''.join(f'<p><strong>{e(update_label(u))}</strong> {e(u["text"])}</p>' for u in ups) + '</div>'

def updates_full(s):
    ups = s.get('updates', [])
    if not ups: return ''
    items = ''
    for u in ups:
        src = ''.join(f'<div class="evidence"><a href="{e(x["url"])}" target="_blank" rel="noopener noreferrer">{e(x["title"])} ↗</a><small>{e(x["publisher"])} · {e(x["publishedAt"])} · {e(x.get("kind","reporting"))}</small></div>' for x in u.get('sources', []))
        items += f'<div class="update-item"><span class="eyebrow">{e(update_label(u))}</span><p>{e(u["text"])}</p>{src}</div>'
    return f'<section class="article-updates" id="updates" aria-label="Updates"><h2>Since this morning</h2>{items}</section>'

def report_words(s):
    words = len(s['body'].split())
    for section in s.get('report', []): words += sum(len(p.split()) for p in section['paragraphs'])
    return words

def read_label(s):
    return f'{max(1, math.ceil(report_words(s) / 220))} min read' if s.get('report') else 'Summary'

def key_facts(s):
    if not s.get('keyFacts'): return ''
    return '<aside class="key-facts" aria-label="Key facts"><span class="eyebrow">Key facts</span><ul>' + ''.join(f'<li>{e(x)}</li>' for x in s['keyFacts']) + '</ul></aside>'

def full_report(s):
    if not s.get('report'): return ''
    parts = ''.join(f'<h2>{e(sec["heading"])}</h2>' + ''.join(f'<p>{e(p)}</p>' for p in sec['paragraphs']) for sec in s['report'])
    return f'<section class="full-report" id="full-report" aria-label="Full report">{parts}</section>'

def thread_link(s,prefix): return f'{prefix}threads/{thread_key(s)}/'

def lead_story(edition):
    if edition.get('leadStoryId'):
        return next(s for s in edition['stories'] if s['id'] == edition['leadStoryId'])
    return next((s for s in edition['stories'] if s['section'] == 'world'), edition['stories'][0])

def frontier_card(s, n, prefix):
    return f'''<article class="story-card frontier-card" id="{e(s['id'])}" data-section="frontiers">
    {story_image(s,prefix,True)}<div class="kicker"><span class="eyebrow">{e(s.get('field','AI'))} / {e(s['category'])}</span><span class="number">{n:02}</span></div>
    <h3><a href="{prefix}stories/{s['id']}/">{e(s['title'])}</a></h3>
    <div class="frontier-hook"><span class="eyebrow">This changes the picture</span><p>{e(s.get('hook',s['whyMatters']))}</p></div>{updates_inline(s)}
    <div class="card-foot"><span class="badge">Editorial assessment</span><a class="card-more" href="{prefix}stories/{s['id']}/" aria-label="Full report: {e(s['title'])}">Full report <span>→</span></a></div></article>'''

def card(s, n, prefix, lead=False):
    badge = ' major' if s['status'] == 'Major development' else ''
    return f'''<article class="story-card{' lead' if lead else ''}" id="{e(s['id'])}" data-section="{e(s['section'])}">
    {story_image(s, prefix, True)}
    <div class="kicker"><span class="eyebrow">{e(s['region'])} / {e(s['category'])}</span><span class="number">{n:02}</span></div>
    <h3><a href="{prefix}stories/{s['id']}/">{e(s['title'])}</a></h3>
    <div class="change"><p><strong>What changed</strong><br>{e(s['whatChanged'])}</p></div>{updates_inline(s)}
    <div class="context"><p><strong>Why it matters · our assessment</strong><br>{e(s['whyMatters'])}</p></div>
    <details class="card-details"><summary>Uncertainty &amp; sources</summary><div class="context"><p><strong>Still uncertain</strong><br>{e(s['uncertainty'])}</p><p><strong>What to watch</strong><br>{e(s['watchNext'])}</p>{source_links(s)}</div></details>
    <div class="card-foot"><span class="badge{badge}">{e(s['status'])}</span><span class="card-links"><a class="card-thread" href="{thread_link(s,prefix)}" aria-label="Follow this story: {e(s['title'])}">Follow</a><a class="card-more" href="{prefix}stories/{s['id']}/" aria-label="Full report: {e(s['title'])}">Full report <span>→</span></a></span></div>
    </article>'''

def shell(content, edition, title='The Signal — The world, considered. Once a day.', prefix='./', canonical='', payload=True, description='A finite daily briefing on the world, AI, and consequential scientific advances. What changed, why it matters, and the evidence behind it.'):
    stamp = date.fromisoformat(edition['date']).strftime('%A, %d %B %Y')
    metadata = dict(edition=edition, editions=[{'date': x['date'], 'number': x['number'], 'count': len(x['stories'])} for x in EDITIONS], prefix=prefix)
    serialized = json.dumps(metadata, ensure_ascii=False).replace('<', '\\u003c')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(title)}</title><meta name="description" content="{e(description)}"><meta name="theme-color" content="#09131d"><link rel="canonical" href="{BASE}/{canonical}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:site_name" content="The Signal"><meta property="og:type" content="website"><meta property="og:url" content="{BASE}/{canonical}"><link rel="icon" type="image/svg+xml" href="{prefix}assets/signal.svg?v={ASSET_VERSION}"><link rel="stylesheet" href="{prefix}assets/style.css?v={ASSET_VERSION}"><link rel="alternate" type="application/rss+xml" title="The Signal editions" href="{prefix}feed.xml"></head>
    <body><a class="skip" href="#main">Skip to the briefing</a><div class="progress" aria-hidden="true"></div><header class="wrap"><div class="topline eyebrow"><span class="status"><i class="status-dot"></i> An independent daily briefing</span><span>{e(stamp)}</span><span class="timezone">A global perspective</span></div><div class="masthead"><a class="wordmark" href="{prefix}" aria-label="The Signal home"><span class="wordmark-the">The</span><span>Signal</span></a><div class="masthead-note"><p>The world, considered.<br><em>Once a day.</em></p><div class="edition-stamp"><span>Nº</span><strong>{edition['number']:03}</strong><small>The daily edition</small></div></div></div><nav class="navigation" aria-label="Main navigation"><div class="navlinks"><a href="{prefix}#edition">The edition</a><a href="{prefix}#frontiers">Frontiers</a><a href="{prefix}threads/">Threads</a><a class="archive-nav" href="{prefix}archive/">Archive</a><a class="about-nav" href="{prefix}about/">Our approach</a></div><div class="nav-actions"><button class="catchup" data-dialog="catchup-dialog">Catch me up ↗</button></div></nav></header>
    {content}
    <footer class="footer"><div class="wrap"><a class="footer-brand" href="{prefix}"><span>The</span> Signal</a><p>Evidence-linked. Open to correction.</p><div class="footer-links"><a href="{prefix}about/">Our approach</a><a href="{prefix}threads/">Threads</a><a href="{prefix}archive/">Archive</a><a href="https://github.com/PrototypeVersions/Signal/issues/new?labels=correction&amp;title=Correction%3A%20" target="_blank" rel="noopener noreferrer">Corrections ↗</a></div></div></footer>
    <dialog id="catchup-dialog" aria-labelledby="catchup-title"><button class="close" aria-label="Close dialog">×</button><div class="eyebrow">The thread, picked up</div><h2 id="catchup-title">Away for a few days?</h2><p>Choose the last edition you read. We’ll gather the developments published since then, grouped by story.</p><label for="since-date">Last edition read</label><select id="since-date" class="catchup-select"><option value="all">I’m new here</option>{''.join(f'<option value="{x["date"]}">{pretty(x["date"])}</option>' for x in reversed(EDITIONS))}</select><div id="catchup-results" aria-live="polite"></div></dialog>
    <div class="toast" role="status" hidden></div><script id="signal-data" type="application/json">{serialized}</script><script src="{prefix}assets/app.js?v={ASSET_VERSION}" defer></script></body></html>'''

def atlas(edition, prefix='./'):
    # Same projection as the sourced Natural Earth overview generated at build time.
    project=lambda lon,lat: ((lon+180)*2.2,(84-lat)*2.45)
    located=[(i,s) for i,s in enumerate(edition['stories'],1) if s.get('locations')]
    if not located: return ''
    # One pin per story, at its first (most representative) location; nudge pins apart so none overlap.
    placed=[]
    for number,story in located:
        point=story['locations'][0]
        x,y=project(point['lon'],point['lat'])
        for _ in range(40):
            clash=next(((px,py) for _,_,px,py,_ in placed if math.hypot(x-px,y-py)<32),None)
            if not clash: break
            dx,dy=x-clash[0],y-clash[1]
            dist=math.hypot(dx,dy) or 1.0
            if dist<1: dx,dy,dist=1.0,-1.0,1.4
            x+=dx/dist*6; y+=dy/dist*6
        placed.append((number,story,x,y,point))
    pins=''
    for number,story,x,y,point in placed:
        pins+=f'<a href="#{e(story["id"])}" class="map-pin" data-atlas-id="{e(story["id"])}" aria-label="{e(point["label"])}: {e(story["title"])}"><circle cx="{x:.1f}" cy="{y:.1f}" r="15"/><text x="{x:.1f}" y="{y+4:.1f}" text-anchor="middle">{number:02}</text></a>'
    first=located[0][1]
    return f'''<section class="atlas" aria-labelledby="atlas-heading"><div class="atlas-top"><div class="eyebrow">The observatory / Reporting locations</div><span class="atlas-instruction">Choose a numbered location ↘</span></div><div class="atlas-layout"><div class="atlas-map"><h2 id="atlas-heading">A wider <em>perspective.</em></h2><svg viewBox="0 0 800 355" role="group" aria-label="World overview with approximate reporting locations"><defs><pattern id="atlas-grid" width="44" height="44" patternUnits="userSpaceOnUse"><path d="M44 0H0V44" fill="none" stroke="#263c50" stroke-width=".6"/></pattern><pattern id="atlas-dots" width="5" height="5" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r=".8" fill="#59768d"/></pattern></defs><rect width="800" height="355" fill="url(#atlas-grid)"/><image href="{prefix}assets/visuals/world-overview.svg" width="800" height="355"/>{pins}</svg><p class="atlas-caption">Approximate reporting locations · map data: Natural Earth</p></div><aside class="atlas-detail" aria-live="polite"><span class="eyebrow" id="atlas-region">{e(first['region'])}</span><h3 id="atlas-title">{e(first['title'])}</h3><p id="atlas-change">{e(first['whatChanged'])}</p><a class="atlas-read" href="{thread_link(first,prefix)}">Follow this story <span>→</span></a></aside></div></section>'''

def home(edition, prefix='./', archived=False):
    world = [s for s in edition['stories'] if s['section'] == 'world']
    ai = [s for s in edition['stories'] if s['section'] in ('ai','frontiers')]
    still = [s for s in edition['stories'] if s['section'] == 'still']
    count = len(world) + len(ai)
    words = sum(len((' '.join(s[k] for k in ('body','whatChanged','whyMatters','uncertainty'))).split()) for s in edition['stories']) + sum(len(w['text'].split()) for w in edition['watch'])
    minutes = max(3, math.ceil(words / 200))
    lead=lead_story(edition)
    cover=edition.get('cover') or ({'storyId':lead['id'],**lead['image']} if lead.get('image') else None)
    if cover and cover['storyId']==lead['id']:
        art=f'<img class="hero-image" src="{prefix}{e(cover["asset"])}" alt="{e(cover["alt"])}" width="1536" height="1024" fetchpriority="high">'
        credit=e(cover['credit'])
    else:
        art=f'<div class="cover-typographic" aria-hidden="true"><div class="cover-orbit"></div><strong>{edition["number"]:03}</strong></div>'
        credit='The Signal / The daily edition'
    brief_choices=([s for s in world if s['id']!=lead['id']][:2]+[s for s in ai if s['id']!=lead['id']][:1])[:3]
    brief=''.join(f'<a class="brief-item" href="{prefix}stories/{item["id"]}/"><span>{edition["stories"].index(item)+1:02}</span><h3>{e(item["title"])}</h3><span class="brief-arrow">↗</span></a>' for item in brief_choices)
    archive_note = f'<div class="latest-link">You’re reading an archived edition. <a href="{prefix}"><u>Read the latest →</u></a></div>' if archived else ''
    rc = edition.get('realityCheck')
    reality = f'''<div class="reality-check"><div class="eyebrow">The reality check ↗</div><p><strong>{e(rc['title'])}.</strong> {e(rc['text'])} <a href="{e(rc['url'])}" target="_blank" rel="noopener noreferrer"><u>Read the research ↗</u></a></p></div>''' if rc else ''
    still_html = ''.join(f'''<article class="still-card" id="{s['id']}">{story_image(s,prefix,True)}<span class="eyebrow">{e(s['region'])}</span><h3><a href="{prefix}stories/{s['id']}/">{e(s['title'])}</a></h3><p>{e(s['body'])}</p><a class="card-more" href="{prefix}stories/{s['id']}/" aria-label="Full report: {e(s['title'])}">Full report <span>→</span></a></article>''' for s in still if s['id'] != lead['id'])
    watch = ''.join(f'<div class="watch-item"><span>{i:02}</span><div><h3>{e(w["title"])}</h3><p>{e(w["text"])}</p></div></div>' for i,w in enumerate(edition['watch'],1))
    lead_number=edition['stories'].index(lead)+1
    world_cards=''.join(card(s,edition['stories'].index(s)+1,prefix) for s in world if s['id']!=lead['id'])
    ai_cards=''.join(frontier_card(s,edition['stories'].index(s)+1,prefix) for s in ai if s['id']!=lead['id'])
    return archive_note + f'''<main id="main" class="wrap">{corrections(edition)}
    <section class="issue-intro" id="edition"><div><div class="eyebrow">The daily edition / {edition['number']:03}</div><h2>{e(pretty(edition['date']))}</h2></div><div class="edition-meta"><span>{count} developments</span><span>≈ {minutes} min read</span><span>Checked {e(edition['cutoffLabel'])}</span>{f'<span class="updated-stamp">Updated {e(edition["updatedLabel"])}</span>' if edition.get('updatedAt') else ''}</div></section><div class="stale-note" id="stale-note" hidden></div>
    <section class="opening-note" aria-label="Today in brief"><span class="eyebrow">The day, in view</span><p>{e(edition['opening'])}</p></section>
    <div class="toolbar"><div class="filters" aria-label="Filter the edition"><button data-filter="all" aria-pressed="true">All signals <span>{count}</span></button><button data-filter="world" aria-pressed="false">World <span>{len(world)}</span></button><button data-filter="frontiers" aria-pressed="false">Frontiers <span>{len(ai)}</span></button></div><div class="reading-toggle" aria-label="Reading depth"><button data-mode="briefing" aria-pressed="true">Full briefing</button><button data-mode="quick" aria-pressed="false">Quick scan</button></div></div>
    <section class="lead-story" id="{lead['id']}" data-section="{'frontiers' if lead['section'] in ('ai','frontiers') else lead['section']}" aria-labelledby="lead-title"><div class="cover-stage {"map-cover" if lead.get("visual",{}).get("type")=="map" else ""}">{art}<div class="cover-copy"><div class="eyebrow">The lead / {e(lead['category'])}</div><h1 id="lead-title"><a href="{prefix}stories/{lead['id']}/">{e(lead['title'])}</a></h1><p class="hero-deck">{e(lead['whatChanged'])}</p><a class="hero-read" href="{prefix}stories/{lead['id']}/">Read the full report · {e(read_label(lead))} <span>↗</span></a></div><div class="cover-credit">{credit}</div></div><div class="lead-details"><div class="lead-report"><p class="lead-region eyebrow">{e(lead['region'])} / {lead_number:02}</p>{updates_inline(lead)}<p class="summary">{e(lead['body'])}</p><div class="lead-actions"><a class="button" href="{prefix}stories/{lead['id']}/" aria-label="Full report: {e(lead['title'])}">Full report <span>→</span></a><a class="textlink" href="{thread_link(lead,prefix)}">Follow this story</a>{source_links(lead)}</div></div><div class="lead-context context"><p><strong>Why it matters · our assessment</strong><br>{e(lead['whyMatters'])}</p><p><strong>Still uncertain</strong><br>{e(lead['uncertainty'])}</p></div></div></section>
    <details class="edition-note"><summary>About this edition</summary><p>{e(edition['note'])}</p></details>
    <section class="world-grid-section" {"hidden" if not world_cards else ""}><div class="section-title"><div><span class="eyebrow">The world / In focus</span><h2>Across the <em>world.</em></h2></div><span class="section-number">01 — {len(world):02}</span></div><div class="story-grid world-grid" aria-label="World developments">{world_cards}</div></section>
    <section class="ai-section" id="frontiers" {"hidden" if not ai_cards else ""}><span id="ai-frontier" aria-hidden="true"></span><div class="section-head"><div><div class="eyebrow">AI · Science · Medicine · Space · Energy</div><h2><em>Frontiers.</em></h2></div><p>What’s changing the future.<br>And the evidence behind it.</p></div><div class="story-grid">{ai_cards}</div>{reality}</section>
    {atlas(edition,prefix)}
    <div class="below"><section><div class="eyebrow">Beyond the news cycle</div><h2><em>Still</em> matters.</h2>{still_html or '<p>No continuing-priority entry in this edition.</p>'}</section><section><div class="eyebrow">The next signals</div><h2>What we’re watching.</h2>{watch}</section></div>
    <section class="endnote"><div class="endnote-mark" aria-hidden="true">✳</div><div><h2>You’re caught up.<br><em>Go live your day.</em></h2><p>One considered edition. A natural place to stop.</p></div><div class="endnote-actions"><button class="textlink" id="share-edition">Share this edition ↗</button><a class="textlink" href="{prefix}threads/">Follow the story threads →</a><a class="textlink" href="{prefix}archive/">Explore the archive →</a></div></section></main>'''

def threads_index(threads):
    rows=''
    for slug,history in sorted(threads.items(),key=lambda item:item[1][-1][0]['date'],reverse=True):
        edition,story=history[-1]
        rows+=f'<article class="thread-index-card"><div class="eyebrow">{e(story.get("field",story["category"]))}</div><h2><a href="{slug}/">{e(story.get("threadTitle",story["title"]))} <span>↗</span></a></h2><p>{e(story.get("threadSummary",story["whatChanged"]))}</p><div class="thread-meta">{len(history)} report{"s" if len(history)!=1 else ""} · Updated {e(pretty(edition["date"]))}</div></article>'
    return f'<main class="wrap" id="main"><header class="threads-intro"><span class="eyebrow">The longer view</span><h1>Stories, <em>followed.</em></h1><p>Developments belong to a bigger story. Follow the evidence and the changes, edition by edition.</p></header><div class="thread-index">{rows}</div></main>'

def thread_page(history):
    edition,current=history[-1]
    timeline=''
    for published,story in reversed(history):
        timeline+=f'''<article class="thread-update"><div class="thread-date"><a href="../../editions/{published['date']}/#{story['id']}">{e(pretty(published['date']))}</a><span>{e(story['status'])}</span></div><h2><a href="../../stories/{story['id']}/">{e(story['title'])} ↗</a></h2><div class="change"><p><strong>What changed</strong><br>{e(story['whatChanged'])}</p></div>{updates_inline(story)}<div class="context"><p><strong>Why it matters · our assessment</strong><br>{e(story['whyMatters'])}</p><p><strong>Still uncertain</strong><br>{e(story['uncertainty'])}</p></div><details class="thread-sources"><summary>Sources & evidence ({len(story['sources'])})</summary>{evidence(story)}</details></article>'''
    return f'''<main class="wrap" id="main"><article class="article-page thread-page"><a class="article-back" href="../">← All story threads</a><span class="eyebrow">The story, in context</span><h1>{e(current.get('threadTitle',current['title']))}</h1><p class="article-summary">{e(current.get('threadSummary',current['whatChanged']))}</p><div class="thread-meta">{len(history)} report{'s' if len(history)!=1 else ''} · First tracked {e(pretty(history[0][0]['date']))} · Updated {e(pretty(edition['date']))}</div><h2 class="timeline-heading" id="timeline">The story so far</h2><div class="thread-timeline">{timeline}</div><p class="source-note">Dated editions preserve what was reported at the time. New developments are added here as the story continues.</p></article></main>'''

def article(s, edition, history):
    thread_history=THREADS.get(thread_key(s),history)
    timeline=''.join(f'<div class="archive-row"><div><a href="../../editions/{x["date"]}/#{item["id"]}">{pretty(x["date"])}</a><h3>{e(item["title"])}</h3><p>{e(item["whatChanged"])}</p></div></div>' for x,item in reversed(thread_history))
    return f'''<main class="wrap" id="main"><article class="article-page"><a class="article-back" href="../../">← Back to the latest edition</a><div class="eyebrow">{e(s['region'])} / {e(s['category'])}</div><h1>{e(s['title'])}</h1><p class="source-note">Published in The Signal on {pretty(edition['date'])} · Event: {e(s['eventDate'])} · {e(read_label(s))}</p><div class="article-thread"><span>Part of <a href="{thread_link(s,'../../')}">{e(s.get('threadTitle',s['title']))}</a></span><a href="{thread_link(s,'../../')}">Follow the thread →</a></div><nav class="article-sections" aria-label="Story sections">{'<a href="#full-report">Full report</a>' if s.get('report') else ''}<a href="#assessment">Our assessment</a><a href="#sources-evidence">Sources & evidence</a><a href="#story-history">Story timeline ↓</a></nav>{story_image(s,"../../")}{updates_full(s)}<p class="article-summary">{e(s['body'])}</p>{key_facts(s)}{full_report(s)}<h2 id="assessment">What changed</h2><p>{e(s['whatChanged'])}</p><h2>Why it matters</h2><p class="source-note">Editorial assessment</p><p>{e(s['whyMatters'])}</p><h2>What remains uncertain</h2><p>{e(s['uncertainty'])}</p><h2>Watch next</h2><p>{e(s['watchNext'])}</p>{corrections(edition,s["id"])}<h2 id="sources-evidence">Sources & evidence</h2>{evidence(s)}<h2 id="story-history">The story so far</h2>{timeline}<p class="source-note">Each dated edition preserves what we reported at the time. Corrections are recorded explicitly.</p></article></main>'''

ABOUT = '''<main class="wrap" id="main"><article class="article-page"><div class="eyebrow">The editorial promise</div><h1>Attention is finite.<br><em>Spend it well.</em></h1><p class="article-summary">The Signal is an independent daily briefing. It follows consequential changes in the world and at the frontiers of AI and science, in one finite daily edition.</p><h2>Change, with context</h2><p>We ask what is new, how strong the evidence is, and what the development could change. A quieter day can mean a shorter edition. An enduring crisis can deserve attention even when there is no fresh headline.</p><h2>Evidence before certainty</h2><p>Every item links to its sources. We prioritize primary documents and established reporting, seek independent corroboration, and distinguish an announcement from a demonstrated result. Sources repeating the same original account are not independent confirmation. Company research is labeled as such.</p><h2>Facts and judgments</h2><p>The report and “What changed” describe available evidence. “Why it matters” and “Watch next” are editorial assessments. We show uncertainties instead of manufacturing precise importance scores or unsupported probabilities.</p><h2>A publication with a memory</h2><p>Daily editions are retained in the archive. Continuing stories use stable identifiers so their developments can be followed across editions. The first edition starts that record; it does not invent a past.</p><h2>How each edition is produced</h2><p>Each morning, the edition is researched and assembled from the linked reporting, and each evening it is updated where stories have moved, with context, evidence limitations, and a clear point at which to stop. Follow those sources for their full reporting.</p><h2>Corrections belong in the open</h2><p>If a claim is wrong, we correct it and record what changed. We do not silently erase mistakes from the historical record. <a href="https://github.com/PrototypeVersions/Signal/issues/new?labels=correction&amp;title=Correction%3A%20" target="_blank" rel="noopener noreferrer">Report an error on GitHub ↗</a></p><h2>Images as editorial interpretation</h2><p>Our original illustrations use simple visual metaphors for each story. They are labeled as illustrations, not photographs of the reported events, and are not evidence for the reporting. Maps locate the reporting; charts show sourced figures; illustrations provide a visual interpretation. Each edition uses the form that best explains the story.</p><h2>Your reading stays yours</h2><p>This prototype has no advertising or analytics scripts. Catch-up is based on the edition you select. Google Fonts supplies the typography; source links take you to their respective publishers. Your browser and hosting provider may retain ordinary access logs.</p><h2>Read at your own pace</h2><p>Use Quick scan for the changes alone and Full briefing for summaries and assessments. Every story has a full report with key facts, background, sources and a dated timeline; Follow this story opens the whole thread across editions.</p></article></main>'''

if __name__ == '__main__':
    EDITIONS = [json.loads(p.read_text()) for p in sorted((ROOT/'data/editions').glob('*.json'))]
    assert EDITIONS, 'No editions to publish'
    for edition in EDITIONS: validate(edition)
    assert len({x['date'] for x in EDITIONS}) == len(EDITIONS)
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT/'assets',OUT/'assets')
    for edition in EDITIONS: prepare_visuals(edition,OUT)
    latest = EDITIONS[-1]
    THREADS = {}
    for edition in EDITIONS:
        for story in edition['stories']: THREADS.setdefault(thread_key(story),[]).append((edition,story))
    write('index.html',shell(home(latest),latest))
    for edition in EDITIONS:
        write(f'editions/{edition["date"]}/index.html',shell(home(edition,'../../',True),edition,f'The Signal — {pretty(edition["date"])}','../../',f'editions/{edition["date"]}/'))
    index = {}
    for edition in EDITIONS:
        for s in edition['stories']: index.setdefault(s['id'],[]).append((edition,s))
    write('threads/index.html',shell(threads_index(THREADS),latest,'Story threads — The Signal','../','threads/'))
    for slug,history in THREADS.items():
        current=history[-1][1]
        write(f'threads/{slug}/index.html',shell(thread_page(history),latest,current.get('threadTitle',current['title'])+' — The Signal','../../',f'threads/{slug}/'))
    for slug,history in index.items():
        edition,s = history[-1]
        write(f'stories/{slug}/index.html',shell(article(s,edition,history),edition,s['title']+' — The Signal','../../',f'stories/{slug}/',description=s['body']))
    rows = ''.join(f'<div class="archive-row"><a href="../editions/{x["date"]}/">{pretty(x["date"])}</a><span>Edition {x["number"]:03} · {len(x["stories"])} stories ↗</span></div>' for x in reversed(EDITIONS))
    write('archive/index.html',shell(f'<main class="wrap" id="main"><div class="eyebrow" style="margin-top:45px">The record, kept</div><h1 class="archive-title">A world in chapters.</h1><p>Every edition, preserved. A little perspective over time.</p><div class="archive-list">{rows}</div></main>',latest,'The archive — The Signal','../','archive/'))
    write('about/index.html',shell(ABOUT,latest,'Our approach — The Signal','../','about/'))
    write('data/history.json',json.dumps(EDITIONS,ensure_ascii=False))
    items=''.join(f'<item><title>{xml_escape("The Signal — "+pretty(x["date"]))}</title><link>{BASE}/editions/{x["date"]}/</link><guid>{BASE}/editions/{x["date"]}/</guid><description>{xml_escape(x["opening"])}</description></item>' for x in reversed(EDITIONS))
    write('feed.xml',f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>The Signal</title><link>{BASE}/</link><description>A clearer view of a changing world.</description><language>en</language>{items}</channel></rss>')
    paths=['','archive/','about/','threads/']+[f'threads/{slug}/' for slug in THREADS]+[f'stories/{s}/' for s in index]+[f'editions/{x["date"]}/' for x in EDITIONS]
    write('sitemap.xml','<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{BASE}/{x}</loc></url>' for x in paths)+'</urlset>')
    write('robots.txt',f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n')
    write('.nojekyll','')
    write('404.html',shell('<main class="wrap article-page" id="main"><h1>This page hasn’t made the edition.</h1><p><a href="/Signal/">Return to The Signal →</a></p></main>',latest,'Page not found — The Signal','/Signal/'))
    print(f'Built {len(EDITIONS)} edition(s), {len(index)} story pages and {len(paths)} indexed pages.')
