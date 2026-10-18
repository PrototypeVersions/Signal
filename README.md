# The Signal

A finite daily briefing: what changed, why it matters, and the evidence behind it.

Public site: https://prototypeversions.github.io/Signal/

## Development

No packages or API keys are needed to build the site. Python 3.9+ is sufficient:

```sh
python3 scripts/build.py
python3 -m http.server 8000 --directory dist
```

`assets/` contains the visual design and browser interactions. `data/editions/` contains the published record. `scripts/build.py` validates the data and creates the homepage, dated editions, persistent story pages, archive, RSS and sitemap. Generated output lives in `dist/` and is deployed by GitHub Actions.

## Daily editions

A scheduled Claude task (Opus 5.5) produces each edition every morning, Central time, and a second task updates it each evening with what changed during the day. It researches the day's developments, writes `data/editions/YYYY-MM-DD.json` following [EDITORIAL.md](EDITORIAL.md), validates it with `scripts/build.py`, and pushes to `main`; the push triggers validation and GitHub Pages publication. Every story includes key facts and a full report shown on its article page, and each edition has a page for each of seven world regions with extra regional news. No API key is used by this repository.

Keep story IDs stable when updating an ongoing story; the site assembles its history automatically. Every edition is dated and has an evidence cutoff. Do not invent prior editions.

## Corrections

Open a GitHub issue with the story, disputed claim and source. Correct the relevant edition and add a dated `corrections` entry documenting the original claim, replacement and reason. Preserve the Git history. No story-level forecasts or numeric importance scores are generated.

## Hosting

GitHub Pages is the prototype host. The build is portable to other static hosts; update `BASE` in `scripts/build.py` when changing the public URL. There is no account system, analytics, newsletter subscription collection, live AI backend or per-visitor AI expense. Google Fonts is the only typography dependency; system fonts are fallbacks.

## Visual identity

The publication name is **The Signal**. Its Night Observatory design uses midnight navy, pale ice-blue typography, copper details, an illustrated lead, and story-specific maps, sourced charts, or simple original illustrations. Images are visibly labeled as Editorial illustrations and are not documentary evidence. The same artwork appears on the article page. The site always uses the night theme.

The compact **Frontiers** section keeps AI central and selectively includes science, medicine, space, and energy breakthroughs. Its cards show a field tag, headline, and concise editorial hook, with Full report linking directly to the article. Follow this story links open the topic thread, including dated updates across different reports. The `leadStoryId` field lets the most consequential story lead regardless of section. Legacy editions and `section: ai` remain supported.

Each story's optional `image` has `asset`, `alt`, and `credit`. The optional edition `cover` must match the selected lead. Without a cover, the build supplies a dated typographic illustration. Optional story `locations` power the geographic index. See [EDITORIAL.md](EDITORIAL.md) for the schema, art direction, research requirements, and image-review workflow.

## Useful visuals and story threads

The opening paragraph summarizes the day before the lead. Larger reading text and concise world cards keep the edition scannable while retaining assessment and uncertainty. Full reports remain on article pages.

Optional `visual` objects render maps from bundled Natural Earth country geometry or bar comparisons from explicit, sourced values. These SVGs are created in `dist/assets/visuals/` during the build, with no map service, API key, or browser requests to a mapping provider. See `scripts/data/README.md` and `EDITORIAL.md` for provenance, visual schemas, and location limits. Artwork remains available when a metaphor is useful; it is not required for every article.

`threadId`, `threadTitle`, and `threadSummary` group related reports across editions. The archive’s “By story” list and each thread timeline (`/threads/<id>/`) are built from the published record. Multiple story IDs may belong to a thread. Existing story URLs and dated archives remain available; legacy editions fall back to their story IDs. No prior history is fabricated.

## Email signups and visitor counts

Both are off until `data/site.json` is filled in:

- `newsletter.username`: your Buttondown username. A signup form then appears at the end of each edition and on the Our approach page. Buttondown can send each morning's edition automatically from the site's feed (`feed.xml`) with its RSS-to-email feature.
- `analytics.goatcounter`: your GoatCounter site code (the part before `.goatcounter.com`). A cookie-free visit counter is then added to every page, and the privacy section of Our approach updates to say so.

Rebuild and push after changing it; routine edition runs never edit this file.

