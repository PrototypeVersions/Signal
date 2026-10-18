# The Signal editorial instructions

## Promise
The publication is named **The Signal**. Use the full name in reader-facing copy. The repository remains `PrototypeVersions/Signal`.

One finite daily edition about consequential changes in the world and the frontiers of AI and science. Aim for about five full World stories, five to eight shorter “More that changed” items, two to four Frontiers items, and a continuing-priority item when justified; publish fewer when evidence is weak. Relevance, human consequence, novelty and evidence guide selection. Geographic diversity guides discovery without forcing quotas. Include consequential positive developments when supported; do not equate significance with conflict.

## Research and comparison
Read recent `data/editions/` files before researching. Reuse a stable story ID for the same continuing event and state the actual change relative to prior reporting. Search current reporting broadly and open sources. Check event dates inside articles; search freshness alone is not sufficient. Do not infer that no news found means nothing happened. Cite the original source behind syndicated reporting and do not count repeats as independent evidence.

Primary documents verify what an institution says or does, not automatically every underlying claim. Distinguish company claims, independent replication and availability. Prefer two genuinely independent accounts for contested factual claims. A single primary announcement is allowed if clearly attributed and its limits stated. Flag unresolved contradictions, exclude unsupported claims, and never fill a quiet day with invented stories. Respect source quotation and summary limits; use original concise prose and direct URLs.

## Schema
Use the first published JSON as the schema reference. Top level: `date` (America/Chicago edition date), `number` (prior + 1), `cutoff` (actual UTC timestamp), `cutoffLabel` (readable Central time), `opening`, optional `note`, `stories`, `watch`, optional `realityCheck`, optional `corrections`, optional `cover`, and `leadStoryId`. Omit `note` on ordinary days. Include it only when readers need to know something unusual about the edition, in one or two plain sentences: for example that it was published in the evening because the morning run failed, that a major story is still developing and key facts may change, or that a usual section is missing. When present it appears as a short note near the end of the page. The `opening` is a 30–50 word synthesis of the selected developments, written as a factual, concise opening paragraph; avoid invented causal connections.

Each story: `id` (stable safe slug), optional `threadId`, `threadTitle`, and `threadSummary`, `section` (`world`, `more`, `frontiers`, `still`; legacy `ai` is supported), `title`, `category`, `region`, `status`, `eventDate` (ISO dates such as `2026-10-17` or `2026-10-16 / 2026-10-18` are shown to readers as October 16–18, 2026), `body` (70–100 words), `whatChanged`, `whyMatters`, `uncertainty`, `watchNext`, `sources`, `keyFacts` and `report`. Use 'Major development', 'Meaningful update', 'This week', 'Research result', or 'Still matters' as appropriate. Each source has `publisher`, `title`, exact `url`, `publishedAt` (state undated when appropriate), and `kind` (primary, reporting, company announcement, analysis etc.). No tool citation syntax belongs in JSON.

## Page layout
The home page runs: the day in view (`opening`), then **The world / In focus** (`section: world`, about five full cards), then **More that changed** (`section: more`), then **Frontiers**, then the regions map, Still matters and What we’re watching. There is no separate lead block: the `leadStoryId` story is shown first and larger inside its own section.

`more` items are shorter world stories that still matter today. Each needs `id`, `section: "more"`, `title`, `category`, `region`, `regions`, `status`, `eventDate`, `whatChanged` (one sentence, shown as the line under the headline), `body` (2–4 sentences, shown when the reader opens “More”) and `sources`. `whyMatters`, `uncertainty`, `watchNext`, `keyFacts`, `report`, `visual` and `image` are optional; if a `more` item has a `report`, the site links its full report. Order `stories` as they appear: world, then more, then frontiers, then still. A story that drops from World to More keeps its id and thread.

## Full reports
Every World, Frontiers and Still story carries a full report for its article page, so readers who want more than the card can click through to it.

- `keyFacts`: three to five short, sourced facts (one line each) that a reader could quote. Numbers, dates, names.
- `report`: two to four sections, each `{"heading": "...", "paragraphs": ["...", "..."]}`, 200–450 words in total. Typical headings: what happened, the response or reaction, background or context, what comes next. Write original, concise prose; do not copy sentences from sources. Every claim in the report must be supported by a listed source. Attribute contested claims and give both sides when accounts conflict. Do not repeat the card's `whatChanged` and `whyMatters` word for word; the report adds detail and context.

`watch` contains three items with `title` and `text`. Optional `realityCheck` has `title`, `text`, `url`; it must be sourced and separate claims from demonstrations. It appears as the last card in Frontiers, labelled Reality check, so include one only when a prominent claim in the news genuinely needs testing against the evidence; omit it on other days. All public text should be reader-facing, not model workflow instructions. Dates must be precise and relative weekdays resolved. Avoid unsupported probabilities, invented measurements, unverifiable counts of reviewed sources, and fabricated human review labels.

## Visual edition fields
`cover` is no longer used: the home page has no separate cover or lead block, so omit it. Artwork must be visibly labeled as illustration. Use the reader-facing caption Editorial illustration; do not add generation-method disclosures to the public site. Actual news photography requires a verified source and reuse rights.

Optional story `locations` is a list of objects with `label`, `lon`, and `lat`. Include only relevant, well-established reporting locations. These represent approximate locations on an illustrated world overview, not exact incident coordinates, disputed borders, or measurements. Omit when location is immaterial or uncertain. Story maps use these locations; the home-page overview is organized by region instead (see Regions).

## Regions
The home page's "The world, by region" map has seven numbered regions, and each has its own page at `regions/<slug>/`. The slugs are `north-america`, `latin-america` (Mexico, Central and South America, the Caribbean), `europe` (including Russia and Ukraine), `africa` (including Egypt and Sudan), `middle-east` (the Gulf, Levant, Iran, Iraq, Yemen, Israel and the Palestinian territories), `asia` (including South and Central Asia) and `oceania` (Australia, New Zealand and the Pacific islands).

1. Give every world and continuing story a `regions` list of one or two slugs, e.g. `"regions": ["europe"]`. A US policy toward Russia can be `["north-america", "europe"]`. Frontiers stories get `"regions": []` unless a story is really about a place. If `regions` is missing, the build guesses from the `region` label, so set it explicitly.
2. Add a top-level `regions` object with an entry for each of the seven slugs: `{"summary": "One or two plain sentences on the region today.", "briefs": [ ... ]}`.
3. `briefs` are extra regional items that did not make the main edition: one to three per region when verified news is available. Each is `{"title", "text", "eventDate", "sources"}`, where `text` is 2–4 sentences of paraphrased, sourced facts and `sources` uses the normal source fields (`title`, `publisher`, `url`, `publishedAt`). Open and read every source; do not rely on search snippets. Prefer the last 48 hours. Do not repeat a main-page story (World, More that changed, Frontiers or Still) as a brief; mention a genuinely new development in it only if the main story does not already cover it. If nothing clears the bar for a region, leave `briefs` empty and the site says so; never pad.
4. In the evening update, refresh a region's `summary` if the picture changed, and you may add a brief for a major regional development that does not warrant a main story.

## Publication
Editions are produced each morning (about 5:57 AM Central) by a scheduled Claude (Opus 5.5) task, and updated each evening (see Evening update) and published directly; there is no draft or manual review step. The task:

1. Clones or pulls `PrototypeVersions/Signal` and reads this file and the latest edition.
2. Works out today's edition date in America/Chicago. If `data/editions/<date>.json` already exists, it stops and reports.
3. Researches with web search, opening and reading the actual articles, and writes `data/editions/<date>.json` following this guide, including `keyFacts` and `report` for every story, and the `regions` tags and seven region entries.
4. Runs `python3 scripts/build.py` and fixes any validation error in the data. It never edits application code, styles, workflows, `data/site.json` or this file as part of a routine edition.
5. Commits and pushes to `main` with the message `Edition <N>: <date>`. The push triggers the Actions workflow, which validates and deploys to GitHub Pages.
6. Reports a short summary: lead story, items included, anything left out because it could not be verified, and any problem.

If sources or access are insufficient, publish fewer items rather than weaker ones; if a usable edition cannot be produced, leave the latest edition in place and report the problem. Never add API credentials or spend paid API credits. Do not send email or social posts.

## Evening update
A second scheduled task runs each evening (about 5:57 PM Central) and updates that day's edition in place. It does not create a second edition.

1. Read today's edition, recent editions and this guide. If today's edition does not exist (the morning run failed), produce a full edition instead, following the publication steps above, and say in `note` that it was published in the evening.
2. Research what has happened since the morning `cutoff` for every story in the edition, every dated item in `watch`, and any major new development.
3. For each story that materially moved, append to its `updates` list: `{"at": "<ISO time with zone>", "label": "Evening update · 5:55 PM CT", "text": "One to three sentences on what changed since this morning.", "sources": [ ...same source fields as stories... ]}`. Do not rewrite the morning's `title`, `body`, `whatChanged` or `report` unless they contain an error, in which case add a `corrections` entry. You may add a short paragraph to the end of a `report` section when the update needs more space, and update `keyFacts` when a figure has changed (state the time, e.g. "as of Sunday evening").
4. Add at most two new stories, only for major new developments, in the normal schema. Change `leadStoryId` only if a new development clearly outranks the morning lead.
5. Set top-level `updatedAt` (ISO time with zone) and `updatedLabel` (for example `5:55 PM CT`). Leave `cutoff` as the morning value. Rewrite `opening` only if the day's picture changed.
6. Run `python3 scripts/build.py`, then commit and push to `main` with the message `Edition <N> evening update: <date>`.
7. Report which stories were updated, any new stories, and anything left out because it could not be verified. If nothing material happened, still set `updatedAt` and say so.

## Corrections
Published corrections are explicit. Add `corrections` objects with `storyId`, `date`, `original`, `replacement`, and `reason` to the affected edition. The build displays these notices. Do not silently rewrite published claims. Story pages show the latest published account and link to dated editions; a daily archive is the historical snapshot.

## Night Observatory and useful visuals
Use midnight navy (#09131d), pale ice blue, slate, and restrained copper. Choose a visual because it explains the particular story. A new artistic illustration is not mandatory for every item. Maps locate reporting, charts show sourced comparisons, and illustrations help when a simple visual metaphor is understandable. Do not force artwork onto a story when it contributes only decoration.

Maps and charts are rendered by the publication from structured `visual` data. They need no uploaded image and no image-generation call. The renderer uses bundled public-domain Natural Earth geography in `scripts/data/world-110m.json`; see its README for provenance. Do not invent country outlines, boundaries, paths, or coordinates with an image model. Locations are approximate reporting locations. Never imply an entire country is affected when evidence concerns a particular area; country highlighting means context, not an incident footprint. Do not add attack paths, territorial-control claims, or trade flows without sourced data. Country boundaries are generalized context.

For a map use:
```
"visual": {
  "type": "map", "title": "Romania & the Black Sea",
  "bounds": [18, 38, 44, 52], "countries": ["642"],
  "labels": [{"label": "Black Sea", "lon": 35, "lat": 44, "kind": "water"}],
  "alt": "Describe the highlighted places and the location uncertainty.",
  "caption": "Romania and its neighbors · approximate reporting location"
}
```
Bounds are west, south, east, north. `countries` contains three-digit country IDs present in the bundled data, for example Romania 642, Brazil 076, United States 840, Russia 643. Verify names, IDs, bounds, and labels; do not guess. `labels` is optional. Markers use the story's `locations`; their optional `mapLabel` gives a shorter display label. A point is not an exact incident coordinate unless explicitly verified.

For a simple comparison chart use `visual` with `type: bars`, `title`, `measure`, `unit`, one to four `values` containing `label` and nonnegative numeric `value`, `alt`, `caption`, and `sourceUrl`. The source URL must match one of the story's sources. Supply the actual units, denominator, and dates or periods; disclose missing baseline dates rather than inventing them. Compare like quantities. Do not turn uncertainty into a measured number or fabricate a data series. The renderer starts bar axes at zero. A chart is optional when the source does not support a useful comparison.

An illustration must visibly match its story. Before drawing one, write down in a single sentence the concrete thing from the story it shows: an object, place, mechanism or action a reader would recognize from the headline (solar panels for solar export controls; an elliptic curve and a clock for curve seeds recovered from timestamps; doorways for outside evaluators getting inside access). If you cannot name such a thing, use a map or chart, or omit the visual; do not fall back on a generic abstract shape. The alt text states what is shown and how it connects to the story. Check each finished image against its headline: a reader who sees only the picture and the headline should see the connection.

When an illustration is appropriate, use a fresh, simple, story-specific composition: one strong object or a few shapes, quiet negative space, subtle grain, and no lettering or fake data. Avoid generic robots and metaphors that need a paragraph to explain. Never create fictional documentary scenes, officials, identifiable victims, or scientific plots. Image generation is not part of the daily run. When an illustration would genuinely help, create a simple original self-contained SVG with shapes and paths when useful, without scripts, external references, or third-party imagery. No paid API calls, API credentials, or stock purchases. If no useful visual can be produced, omit it and mention the decision in the run report.

For artwork use optional `image: {asset, alt, credit}`. An asset is a local path such as `assets/editions/YYYY-MM-DD/story-id.jpg` or `.svg`. Use descriptive alt text and `Editorial illustration` as the public credit; do not add generation-method disclosures to the site. Prefer landscape 3:2 compositions and optimized files below 250 KB. Maps/charts should use `visual` instead of `image`. Do not put generated map/chart file paths into the source JSON: the build creates them. Do not add `cover`; the lead's own map, chart or illustration appears in its card. `more` items show no image on the home page.

Save any SVG artwork under `assets/editions/YYYY-MM-DD/` in the same commit as the edition. In practice most stories should use a built-in map or chart; prefer those to artwork.

## Story threads
Every story, including `more` items, should have `threadId` (a stable topic slug, named for the situation rather than the day's headline), `threadTitle` (short reader-facing topic), and `threadSummary` (one factual sentence explaining the ongoing situation). Reuse existing thread IDs when a new development belongs to the same situation. Several different story IDs may belong to one thread, including several reports in one edition. For example a sanctions decision and a Black Sea security update can both belong to `russia-ukraine-security`.

The site builds `/threads/` and a dated timeline for each thread directly from published editions. Never invent past entries, claim historical coverage that does not exist, or backfill unsourced context. Article titles open the specific report; Follow this story opens its full thread. Legacy editions without thread fields use each story ID as its thread ID. Related reports retain their original dates and source trails.

## Frontiers and the lead
Frontiers combines AI with selective science, medicine, space, and energy developments. AI remains central to the publication's coverage. Do not force a daily number of AI or science stories: publish only material changes with adequate evidence. Science and medicine should distinguish a preprint, peer-reviewed result, trial stage, regulatory approval, and real-world deployment; avoid turning an early result into a promise of a cure or commercial breakthrough. Include independent evaluation and relevant limitations.

Use `section: frontiers` for new items and a `field` of `AI`, `Science`, `Medicine`, `Space`, or `Energy`. Legacy `section: ai` editions remain supported. A field describes the subject; `category` describes the specific development. An optional `hook` is one concise, supportable sentence explaining why the development matters, shown under "Why it matters". Keep it proportionate: say plainly when a development is a modest step rather than a breakthrough. It is editorial assessment, not an additional factual claim. Otherwise the site uses `whyMatters`. Frontiers cards show the image, field, headline, and hook; Read more links directly to the full article with reporting, uncertainty, sources, and a dated story timeline. The underlying story and article page retain the full schema.

Set top-level `leadStoryId` to the most consequential development of the day, regardless of section. A World or Frontiers story may lead when justified. For legacy editions without an explicit lead, the first world item is used, or the first available story. The lead appears first, as a larger card, in its own section (World or Frontiers); a `more` or `still` story cannot be the lead. Do not add a markets strip or daily market quotes to routine editions.
