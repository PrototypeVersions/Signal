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

The subscription-based ChatGPT Work task researches and prepares draft JSON under `drafts/`. Drafts do not trigger publication. Review the draft, then copy the approved edition to `data/editions/YYYY-MM-DD.json`. The push triggers validation and GitHub Pages publication. No OpenAI API key is used by this repository.

Read [EDITORIAL.md](EDITORIAL.md) for the commissioning prompt and evidence rules. The first edition demonstrates the full schema. Keep story IDs stable when updating an ongoing story; the site assembles its history automatically. Every edition is dated and has an evidence cutoff. Do not invent prior editions.

The initial trial runs for fourteen mornings. Scheduled runs consume included ChatGPT plan usage and depend on connected-app access. The research task's notification is the place to review results; the public site only reflects approved published editions.

## Corrections

Open a GitHub issue with the story, disputed claim and source. Correct the relevant edition and add a dated `corrections` entry documenting the original claim, replacement and reason. Preserve the Git history. No story-level forecasts or numeric importance scores are generated.

## Hosting

GitHub Pages is the prototype host. The build is portable to other static hosts; update `BASE` in `scripts/build.py` when changing the public URL. There is no account system, analytics, newsletter subscription collection, live AI backend or per-visitor AI expense. Google Fonts is the only typography dependency; system fonts are fallbacks.

## Visual identity

The publication name is **The Signal**. Its Modern Journal design uses warm paper, ink, and yellow; a lead-story cover; numbered daily briefs; an illustrated geographic story index; and a distinct AI Frontier section. The full name appears in the masthead, page metadata, article attribution, RSS, and catch-up view. The existing repository and public URL are retained.

Approved edition-specific cover art is optional. Without it, the build creates a dated typographic cover. Story `locations` are optional; editions without geographic information omit the map. See `EDITORIAL.md` for these fields. The first cover is a clearly labeled AI-generated conceptual illustration, not documentary photography.
