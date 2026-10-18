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

## Daily trial

The subscription-based ChatGPT Work task researches and prepares draft JSON under `drafts/` and fresh story illustrations under `draft-assets/`. Drafts do not trigger publication. Review the draft and images, then copy the approved edition to `data/editions/YYYY-MM-DD.json` and its artwork to the matching `assets/editions/YYYY-MM-DD/` paths in one commit. The artwork manifest lists the intended paths. The push triggers validation and GitHub Pages publication. No OpenAI API key is used by this repository.

Read [EDITORIAL.md](EDITORIAL.md) for the commissioning prompt and evidence rules. The first edition demonstrates the full schema. Keep story IDs stable when updating an ongoing story; the site assembles its history automatically. Every edition is dated and has an evidence cutoff. Do not invent prior editions.

The initial trial runs for fourteen mornings. Scheduled runs depend on available ChatGPT capabilities, usage limits, and connected-app access. Image generation uses the included capability when available; a simple original SVG can be used when generation is unavailable. Missing artwork is flagged for review. The research task's notification is the place to review results; the public site only reflects approved published editions.

## Corrections

Open a GitHub issue with the story, disputed claim and source. Correct the relevant edition and add a dated `corrections` entry documenting the original claim, replacement and reason. Preserve the Git history. No story-level forecasts or numeric importance scores are generated.

## Hosting

GitHub Pages is the prototype host. The build is portable to other static hosts; update `BASE` in `scripts/build.py` when changing the public URL. There is no account system, analytics, newsletter subscription collection, live AI backend or per-visitor AI expense. Google Fonts is the only typography dependency; system fonts are fallbacks.

## Visual identity

The publication name is **The Signal**. Its Night Observatory design uses midnight navy, pale ice-blue typography, copper details, a cinematic lead image, and simple original illustrations for each article. Images are visibly labeled as Editorial illustrations and are not documentary evidence. The same artwork appears on the article page. A light reading theme is available through the masthead control.

The compact **Frontiers** section keeps AI central and selectively includes science, medicine, space, and energy breakthroughs. Its cards show a field tag, headline, and concise editorial hook, with Read more linking directly to the full article. Follow this story links open the persistent article page, including sources and its dated update history. The `leadStoryId` field lets the most consequential story lead regardless of section. Legacy editions and `section: ai` remain supported.

Each story's optional `image` has `asset`, `alt`, and `credit`. The optional edition `cover` must match the selected lead. Without a cover, the build supplies a dated typographic illustration. Optional story `locations` power the geographic index. See [EDITORIAL.md](EDITORIAL.md) for the schema, art direction, research requirements, and image-review workflow.
