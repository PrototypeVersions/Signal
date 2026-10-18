# The Signal editorial instructions

## Promise
The publication is named **The Signal**. Use the full name in reader-facing copy. The repository remains `PrototypeVersions/Signal`.

One finite daily edition about consequential changes in the world and the frontiers of AI and science. Aim for 8–10 items including a continuing-priority item when justified; publish fewer when evidence is weak. Relevance, human consequence, novelty and evidence guide selection. Geographic diversity guides discovery without forcing quotas. Include consequential positive developments when supported; do not equate significance with conflict.

## Research and comparison
Read recent `data/editions/` files before researching. Reuse a stable story ID for the same continuing event and state the actual change relative to prior reporting. Search current reporting broadly and open sources. Check event dates inside articles; search freshness alone is not sufficient. Do not infer that no news found means nothing happened. Cite the original source behind syndicated reporting and do not count repeats as independent evidence.

Primary documents verify what an institution says or does, not automatically every underlying claim. Distinguish company claims, independent replication and availability. Prefer two genuinely independent accounts for contested factual claims. A single primary announcement is allowed if clearly attributed and its limits stated. Flag unresolved contradictions, exclude unsupported claims, and never fill a quiet day with invented stories. Respect source quotation and summary limits; use original concise prose and direct URLs.

## Schema
Use the first published JSON as the schema reference. Top level: `date` (America/Chicago edition date), `number` (prior + 1), `cutoff` (actual UTC timestamp), `cutoffLabel` (readable Central time), `opening`, `note`, `stories`, `watch`, optional `realityCheck`, optional `corrections`, optional `cover`, and `leadStoryId`. The `opening` is a 30–50 word synthesis of the selected developments, written as a factual, concise opening paragraph; avoid invented causal connections.

Each story: `id` (stable safe slug), optional `threadId`, `threadTitle`, and `threadSummary`, `section` (`world`, `frontiers`, `still`; legacy `ai` is supported), `title`, `category`, `region`, `status`, `eventDate`, `body` (70–100 words), `whatChanged`, `whyMatters`, `uncertainty`, `watchNext`, `sources`. Use 'Major development', 'Meaningful update', 'This week', 'Research result', or 'Still matters' as appropriate. Each source has `publisher`, `title`, exact `url`, `publishedAt` (state undated when appropriate), and `kind` (primary, reporting, company announcement, analysis etc.). No tool citation syntax belongs in JSON.

`watch` contains three items with `title` and `text`. Optional `realityCheck` has `title`, `text`, `url`; it must be sourced and separate claims from demonstrations. All public text should be reader-facing, not model workflow instructions. Dates must be precise and relative weekdays resolved. Avoid unsupported probabilities, invented measurements, unverifiable counts of reviewed sources, and fabricated human review labels.

## Visual edition fields
Optional `cover`: `storyId`, `asset` (an existing local `assets/` image), `alt`, `caption`, and `credit`. The cover story must match the selected `leadStoryId`, with the legacy fallback described below. Never copy a prior cover onto an unrelated story. When no approved cover exists, omit `cover`; the site creates a distinct dated typographic cover automatically. Artwork must be visibly labeled as illustration. Use the reader-facing caption Editorial illustration; do not add generation-method disclosures to the public site. Actual news photography requires a verified source and reuse rights.

Optional story `locations` is a list of objects with `label`, `lon`, and `lat`. Include only relevant, well-established reporting locations. These represent approximate locations on an illustrated world overview, not exact incident coordinates, disputed borders, or measurements. Omit when location is immaterial or uncertain. Numbering and the map are assembled automatically from available locations.

## Publication and review
For the fourteen-day trial, create `drafts/YYYY-MM-DD.json` and notify the owner with a concise editorial summary, uncertainty flags and a link to the draft. Do not place drafts under `data/editions/`. A later explicit publish instruction promotes the reviewed JSON and its approved artwork together. If sources or access are insufficient, report the problem and leave the latest edition intact.

On promotion, validate with `python3 scripts/build.py` where execution is available. The Actions workflow must pass before deployment. Never modify application code or permissions as part of a routine edition task. Never add API credentials or spend paid API credits. Do not send email or social posts.

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

When an illustration is appropriate, use a fresh, simple, story-specific composition: one strong object or a few shapes, quiet negative space, subtle grain, and no lettering or fake data. Avoid generic robots and metaphors that need a paragraph to explain. Never create fictional documentary scenes, officials, identifiable victims, or scientific plots. The available included image-generation capability may be used. If unavailable, create a simpler original self-contained SVG with shapes and paths when useful, without scripts, external references, or third-party imagery. No paid API calls, API credentials, or stock purchases. If no useful visual can be produced, omit it and explain the decision in the review notification.

For artwork use optional `image: {asset, alt, credit}`. An asset is a local path such as `assets/editions/YYYY-MM-DD/story-id.jpg` or `.svg`. Use descriptive alt text and `Editorial illustration` as the public credit; do not add generation-method disclosures to the site. Prefer landscape 3:2 compositions and optimized files below 250 KB. Maps/charts should use `visual` instead of `image`. Do not put generated map/chart file paths into the source JSON: the build creates them. If the lead has `visual`, omit `cover`; the lead visual becomes the cover. For artwork, an optional cover must reference the selected lead. Without an approved visual, the site supplies a dated typographic cover.

Save unpublished artwork only under `draft-assets/YYYY-MM-DD/`, with a small manifest mapping draft files to their intended `assets/editions/YYYY-MM-DD/` paths. The manifest should also list stories using built-in maps/charts and deliberate visual omissions. Draft JSON references intended public paths for artwork; promotion copies reviewed files and JSON together. Maps and charts require only their reviewed JSON. Drafts and draft assets do not trigger publication and are not included in the build output.

## Story threads
Each story should have `threadId` (a stable topic slug), `threadTitle` (short reader-facing topic), and `threadSummary` (one factual sentence explaining the ongoing situation). Reuse existing thread IDs when a new development belongs to the same situation. Several different story IDs may belong to one thread, including several reports in one edition. For example a sanctions decision and a Black Sea security update can both belong to `russia-ukraine-security`.

The site builds `/threads/` and a dated timeline for each thread directly from published editions. Never invent past entries, claim historical coverage that does not exist, or backfill unsourced context. Article titles open the specific report; Follow this story opens its full thread. Legacy editions without thread fields use each story ID as its thread ID. Related reports retain their original dates and source trails.

## Frontiers and the lead
Frontiers combines AI with selective science, medicine, space, and energy developments. AI remains central to the publication's coverage. Do not force a daily number of AI or science stories: publish only material changes with adequate evidence. Science and medicine should distinguish a preprint, peer-reviewed result, trial stage, regulatory approval, and real-world deployment; avoid turning an early result into a promise of a cure or commercial breakthrough. Include independent evaluation and relevant limitations.

Use `section: frontiers` for new items and a `field` of `AI`, `Science`, `Medicine`, `Space`, or `Energy`. Legacy `section: ai` editions remain supported. A field describes the subject; `category` describes the specific development. An optional `hook` is one concise, supportable sentence explaining why the development changes the picture. It is editorial assessment, not an additional factual claim. Otherwise the site uses `whyMatters`. Frontiers cards show the image, field, headline, and hook; Read more links directly to the full article with reporting, uncertainty, sources, and a dated story timeline. The underlying story and article page retain the full schema.

Set top-level `leadStoryId` to the most consequential development of the day, regardless of section. An AI, scientific, or continuing-priority story may lead when justified. `cover.storyId` must match it. For legacy editions without an explicit lead, the first world item is used, or the first available story. The lead appears once on the homepage and its field remains part of the edition. Do not add a markets strip or daily market quotes to routine editions.
