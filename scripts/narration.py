"""Turn an edition into a spoken script: an ordered list of chapters, each a list of paragraphs.

Stdlib only, so the build can use it too. scripts/narrate.py turns the script into audio.
The order follows the front page: the day in view, World, More that changed, Frontiers,
Still matters and What we're watching.
"""
import hashlib, json, re
from datetime import date
from pathlib import Path

# The narrator: George, a British male voice. A single voice name or a blend such as
# {'bm_lewis': 0.65, 'bm_george': 0.35} both work. Changing the voice, speed or RECIPE
# re-records every edition still on the site.
VOICE = 'bm_george'
SPEED = 0.94
LANG = 'en-gb'
RECIPE = 4  # bump when the script or the synthesis changes in a way that should re-record

ONES = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve',
        'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen']
TENS = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
ORD = {'one': 'first', 'two': 'second', 'three': 'third', 'five': 'fifth', 'eight': 'eighth', 'nine': 'ninth', 'twelve': 'twelfth'}

def words(n):
    if n < 20: return ONES[n]
    if n < 100: return TENS[n // 10] + ('-' + ONES[n % 10] if n % 10 else '')
    if n < 1000: return ONES[n // 100] + ' hundred' + (' and ' + words(n % 100) if n % 100 else '')
    return words(n // 1000) + ' thousand' + ((' and ' if n % 1000 < 100 else ' ') + words(n % 1000) if n % 1000 else '')

def ordinal(n):
    w = words(n); head, _, last = w.rpartition('-')
    last = ORD.get(last, last[:-1] + 'ieth' if last.endswith('y') else last + 'th')
    return (head + '-' if head else '') + last

def spoken_date(iso):
    d = date.fromisoformat(iso)
    return f'{d.strftime("%A")}, the {ordinal(d.day)} of {d.strftime("%B")}'

# The speech engine reads most acronyms well in context; these it gets wrong.
FIXES = {'IAEA': 'I A E A', 'U.S.': 'US', 'U.K.': 'UK', 'U.N.': 'UN', 'Mr.': 'Mr', 'Mrs.': 'Mrs', 'Ms.': 'Ms', 'Dr.': 'Dr', 'St.': 'St', 'vs.': 'versus', 'e.g.': 'for example', 'i.e.': 'that is', 'Jr.': 'Junior', 'Inc.': 'Inc', 'Co.': 'Co', 'No.': 'number'}
ROMAN = {'II': 2, 'III': 3, 'IV': 4, 'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'XI': 11, 'XII': 12, 'XIII': 13, 'XIV': 14, 'XV': 15, 'XVI': 16}
CURRENCY = {'$': 'dollars', '£': 'pounds', '€': 'euros', '¥': 'yen'}
SCALE = {'bn': 'billion', 'billion': 'billion', 'm': 'million', 'million': 'million', 'trillion': 'trillion', 'tn': 'trillion', 'k': 'thousand'}

def speakable(text):
    t = ' '.join(str(text).split())
    t = t.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    for a, b in FIXES.items(): t = re.sub(r'(?<![\w.])' + re.escape(a) + r'(?![\w])', b, t)
    t = re.sub(r'\b([A-Z][a-z]+) (' + '|'.join(ROMAN) + r')\b', lambda m: f'{m.group(1)} {ROMAN[m.group(2)]}', t)
    t = re.sub(r'\b([ap])\.m\.', lambda m: f'{m.group(1)} m', t)
    # money: $1.16 billion -> 1.16 billion dollars; £600 -> 600 pounds; €70bn -> 70 billion euros
    def money(m):
        sym, num, scale = m.group(1), m.group(2), (m.group(3) or '').lower()
        scale = SCALE.get(scale, '')
        whole, _, cents = num.partition('.')
        if cents and not scale and len(cents) == 2:
            return f'{whole} {CURRENCY[sym]}' + (f' {int(cents)}' if int(cents) else '')
        return f'{num} {scale + " " if scale else ""}{CURRENCY[sym]}'
    t = re.sub(r'([$£€¥])\s?(\d[\d,]*(?:\.\d+)?)(?:\s?(bn|tn|billion|million|trillion|m|k)\b)?', money, t)
    t = re.sub(r'(?<=\d),(?=\d{3}\b)', '', t)
    t = re.sub(r'(\d+)\.(\d+)', lambda m: m.group(1) + ' point ' + ' '.join(m.group(2)), t)
    t = re.sub(r'(\d)\s?%', r'\1 percent', t)
    t = re.sub(r'(\d)\s?[–-]\s?(\d)', r'\1 to \2', t)
    t = re.sub(r'(\d)\s?km/h\b', r'\1 kilometres an hour', t)
    t = re.sub(r'(\d)\s?mph\b', r'\1 miles an hour', t)
    t = re.sub(r'\b1\s?mm\b', '1 millimetre', t)
    t = re.sub(r'(\d)\s?mm\b', r'\1 millimetres', t)
    t = re.sub(r'\b1\s?km\b', '1 kilometre', t)
    t = re.sub(r'(\d)\s?km\b', r'\1 kilometres', t)
    t = re.sub(r'(\d)\s?°C\b', r'\1 degrees Celsius', t)
    t = re.sub(r'(\d)\s?°F\b', r'\1 degrees Fahrenheit', t)
    t = re.sub(r'(\d):(\d\d)\b', r'\1 \2', t)
    t = re.sub(r'\s*[—–]\s*', ', ', t)
    t = re.sub(r'\s*[·/]\s*', ', ', t)
    t = t.replace('&', ' and ').replace('~', 'about ').replace('+', ' plus ')
    t = re.sub(r'\s+([,.;:!?])', r'\1', t)
    return ' '.join(t.split())

def sentence(text):
    text = speakable(text).strip()
    return text if not text or text[-1] in '.!?"\'' else text + '.'

def story_paragraphs(s, frontier=False):
    paras = [sentence(s['title']), sentence(s['body'])]
    for u in s.get('updates', []):
        paras.append(sentence('Since this morning: ' + u['text']))
    why = s.get('hook') or s.get('whyMatters') if frontier else s.get('whyMatters')
    if why:
        paras.append(sentence('Why it matters: ' + why))
    return paras

def script(edition):
    stories = edition['stories']
    lead = next((s for s in stories if s['id'] == edition.get('leadStoryId')), None)
    first = lambda items: sorted(items, key=lambda s: not (lead and s['id'] == lead['id']))
    world = first([s for s in stories if s['section'] == 'world'])
    more = [s for s in stories if s['section'] == 'more']
    frontiers = first([s for s in stories if s['section'] in ('ai', 'frontiers')])
    still = [s for s in stories if s['section'] == 'still']
    chapters = [{'id': 'intro', 'section': f'Edition {edition["number"]}', 'title': 'The day, in view', 'paragraphs': [
        sentence(f'This is The Signal, for {spoken_date(edition["date"])}'),
        sentence(edition['opening'])]}]
    def add(section, intro, items, frontier=False):
        for i, s in enumerate(items):
            paras = story_paragraphs(s, frontier)
            if frontier and s.get('field'):
                paras[0] = sentence(f'In {s["field"]}: ' + s['title'])
            if i == 0 and intro:
                paras.insert(0, intro)
            chapters.append({'id': s['id'], 'section': section, 'title': s['title'], 'paragraphs': paras})
    add('Across the world', 'Across the world.', world)
    add('More that changed', 'More that changed.', more)
    add('Frontiers', 'Frontiers: what is changing the future.', frontiers, frontier=True)
    add('Still matters', 'Beyond the news cycle: still matters.', still)
    if edition.get('watch'):
        paras = ["What we're watching."] + [sentence(w['title']) + ' ' + sentence(w['text']) for w in edition['watch']]
        paras.append("That's the edition. You're caught up. Go live your day.")
        chapters.append({'id': 'watch', 'section': "What we're watching", 'title': "What we're watching", 'paragraphs': paras})
    else:
        chapters[-1]['paragraphs'].append("That's the edition. You're caught up. Go live your day.")
    return chapters

# How the narrator says names the speech engine gets wrong: data/pronunciations.json.
PRONOUNCE = json.loads((Path(__file__).resolve().parents[1] / 'data/pronunciations.json').read_text())['words']
_PRON_RE = re.compile(r"(?<![\w'-])(" + '|'.join(re.escape(w) for w in sorted(PRONOUNCE, key=len, reverse=True)) + r")('s|s'|')?(?![\w])") if PRONOUNCE else None

def phonemes(text, phonemize):
    """Phonemes for a paragraph, using the pronunciation list where it applies.

    `phonemize(text)` is the speech engine's own phonemizer; returns None when no listed word occurs,
    so the caller can pass the plain text instead."""
    if not _PRON_RE or not _PRON_RE.search(text):
        return None
    out, pos = [], 0
    for m in _PRON_RE.finditer(text):
        before = text[pos:m.start()].strip('-')
        if before.strip(): out.append(phonemize(before))
        say = PRONOUNCE[m.group(1)]
        ipa = say[1:-1] if say.startswith('/') and say.endswith('/') else phonemize(say)
        if m.group(2) == "'s": ipa += 'z' if ipa[-1:] not in 'sʃʒzfθptk' else ('ɪz' if ipa[-1:] in 'sʃʒz' else 's')
        out.append(ipa); pos = m.end()
    if text[pos:].strip('- '): out.append(phonemize(text[pos:].strip('-')))
    joined = ' '.join(x.strip() for x in out if x and x.strip())
    return re.sub(r'\s+([,.;:!?…])', r'\1', joined)

def fingerprint(chapters):
    return hashlib.sha256(json.dumps([VOICE, SPEED, LANG, RECIPE, PRONOUNCE, chapters], ensure_ascii=False).encode()).hexdigest()[:16]

if __name__ == '__main__':
    import sys
    e = json.load(open(sys.argv[1]))
    chs = script(e)
    for c in chs:
        print(f'## [{c["section"]}] {c["title"]}')
        for p in c['paragraphs']: print('  ' + p)
    print(sum(len(p.split()) for c in chs for p in c['paragraphs']), 'words', fingerprint(chs))
