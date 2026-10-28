"""Record each recent edition as a spoken MP3 with chapter marks.

Runs in the publish workflow after scripts/build.py. For every edition from the last
--days days it writes <out>/audio/<date>.mp3 and <out>/audio/<date>.json (duration and
chapters). Recordings are kept in --cache keyed by a fingerprint of the script and the
voice, so an unchanged edition is never recorded twice; the newest editions go first and
the run stops starting new recordings once --budget minutes have passed.

Needs: kokoro-onnx (pip), the Kokoro v1.0 model files in --models, and ffmpeg.
"""
import argparse, json, shutil, subprocess, sys, tempfile, time, wave
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from narration import LANG, SPEED, VOICE, fingerprint, script  # noqa: E402

PAUSE_AFTER_TITLE = 0.45
PAUSE_PARAGRAPH = 0.6
PAUSE_CHAPTER = 1.1

def record(kokoro, style, chapters, wav_path):
    import numpy as np
    rate = None; pieces = []; marks = []; length = 0
    for ci, chapter in enumerate(chapters):
        marks.append(length)
        for pi, text in enumerate(chapter['paragraphs']):
            audio, rate = kokoro.create(text, voice=style, speed=SPEED, lang=LANG)
            pieces.append(audio); length += len(audio)
            last = pi == len(chapter['paragraphs']) - 1
            gap = PAUSE_CHAPTER if last else (PAUSE_AFTER_TITLE if len(text.split()) < 30 else PAUSE_PARAGRAPH)
            silence = np.zeros(int(gap * rate), dtype=audio.dtype)
            pieces.append(silence); length += len(silence)
    audio = np.concatenate(pieces)
    peak = float(np.abs(audio).max()) or 1.0
    audio = audio * min(1.0, 0.95 / peak)
    with wave.open(str(wav_path), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
        w.writeframes((np.clip(audio, -1, 1) * 32767).astype('<i2').tobytes())
    return [m / rate for m in marks], length / rate

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='dist')
    ap.add_argument('--cache', default='.audio-cache')
    ap.add_argument('--models', default='.kokoro')
    ap.add_argument('--days', type=int, default=30)
    ap.add_argument('--budget', type=float, default=40, help='minutes after which no new recording starts')
    args = ap.parse_args()
    started = time.time()
    out = Path(args.out) / 'audio'; out.mkdir(parents=True, exist_ok=True)
    cache = Path(args.cache); cache.mkdir(parents=True, exist_ok=True)
    editions = sorted((json.loads(p.read_text()) for p in (ROOT / 'data/editions').glob('*.json')), key=lambda e: e['date'], reverse=True)
    latest = date.fromisoformat(editions[0]['date'])
    editions = [e for e in editions if (latest - date.fromisoformat(e['date'])).days < args.days]
    kokoro = style = None; keep = set(); made = skipped = 0
    for edition in editions:
        chapters = script(edition)
        fp = fingerprint(chapters); stem = f'{edition["date"]}-{fp}'
        mp3, meta = cache / f'{stem}.mp3', cache / f'{stem}.json'
        if not (mp3.exists() and meta.exists()):
            if (time.time() - started) / 60 > args.budget:
                print(f'{edition["date"]}: skipped, time budget used (next run records it)'); skipped += 1; continue
            if kokoro is None:
                from kokoro_onnx import Kokoro
                kokoro = Kokoro(str(Path(args.models) / 'kokoro-v1.0.onnx'), str(Path(args.models) / 'voices-v1.0.bin'))
                style = sum(weight * kokoro.get_voice_style(name) for name, weight in VOICE.items()) if isinstance(VOICE, dict) else VOICE
            t0 = time.time()
            with tempfile.TemporaryDirectory() as tmp:
                wav = Path(tmp) / 'edition.wav'
                marks, duration = record(kokoro, style, chapters, wav)
                subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', str(wav), '-ac', '1', '-c:a', 'libmp3lame', '-b:a', '56k',
                                '-metadata', f'title=The Signal, {edition["date"]}', '-metadata', 'artist=The Signal',
                                '-metadata', f'track={edition["number"]}', str(mp3)], check=True)
            meta.write_text(json.dumps({
                'date': edition['date'], 'number': edition['number'], 'duration': round(duration, 2), 'fingerprint': fp,
                'chapters': [{'t': round(t, 2), 'id': c['id'], 'section': c['section'], 'title': c['title']} for c, t in zip(chapters, marks)],
            }, ensure_ascii=False))
            made += 1
            print(f'{edition["date"]}: recorded {duration/60:.1f} min in {(time.time()-t0)/60:.1f} min')
        keep.update({mp3.name, meta.name})
        shutil.copyfile(mp3, out / f'{edition["date"]}.mp3')
        info = json.loads(meta.read_text()); info['src'] = f'{edition["date"]}.mp3?v={fp}'
        (out / f'{edition["date"]}.json').write_text(json.dumps(info, ensure_ascii=False))
    for stale in cache.iterdir():
        if stale.name not in keep: stale.unlink()
    print(f'audio: {made} recorded, {len(keep)//2 - made} reused, {skipped} waiting, {(time.time()-started)/60:.1f} min')

if __name__ == '__main__':
    main()
