# The Signal editorial instructions

## Promise
The publication is named **The Signal**. Use the full name in reader-facing copy. The repository remains `PrototypeVersions/Signal`.

One finite daily edition about consequential changes in the world and the AI frontier. Aim for 8–10 items including a continuing-priority item when justified; publish fewer when evidence is weak. Relevance, human consequence, novelty and evidence guide selection. Geographic diversity guides discovery without forcing quotas. Include consequential positive developments when supported; do not equate significance with conflict.

## Research and comparison
Read recent `data/editions/` files before researching. Reuse a stable story ID for the same continuing event and state the actual change relative to prior reporting. Search current reporting broadly and open sources. Check event dates inside articles; search freshness alone is not sufficient. Do not infer that no news found means nothing happened. Cite the original source behind syndicated reporting and do not count repeats as independent evidence.

Primary documents verify what an institution says or does, not automatically every underlying claim. Distinguish company claims, independent replication and availability. Prefer two genuinely independent accounts for contested factual claims. A single primary announcement is allowed if clearly attributed and its limits stated. Flag unresolved contradictions, exclude unsupported claims, and never fill a quiet day with invented stories. Respect source quotation and summary limits; use original concise prose and direct URLs.

## Schema
Use the first published JSON as the schema reference. Top level: `date` (America/Chicago edition date), `number` (prior + 1), `cutoff` (actual UTC timestamp), `cutoffLabel` (readable Central time), `opening`, `note`, `stories`, `watch`, optional `realityCheck`, optional `corrections`, optional `cover`.

Each story: `id` (stable safe slug), `section` (`world`, `ai`, `still`), `title`, `category`, `region`, `status`, `eventDate`, `body` (70–100 words), `whatChanged`, `whyMatters`, `uncertainty`, `watchNext`, `sources`. Use 'Major development', 'Meaningful update', 'This week', 'Research result', or 'Still matters' as appropriate. Each source has `publisher`, `title`, exact `url`, `publishedAt` (state undated when appropriate), and `kind` (primary, reporting, company announcement, analysis etc.). No tool citation syntax belongs in JSON.

`watch` contains three items with `title` and `text`. Optional `realityCheck` has `title`, `text`, `url`; it must be sourced and separate claims from demonstrations. All public text should be reader-facing, not model workflow instructions. Dates must be precise and relative weekdays resolved. Avoid unsupported probabilities, invented measurements, unverifiable counts of reviewed sources, and fabricated human review labels.

## Visual edition fields
Optional `cover`: `storyId`, `asset` (an existing local `assets/` image), `alt`, `caption`, and `credit`. The cover story is the first world story, or the first AI story when no world stories exist. Never copy a prior cover onto an unrelated story. When no approved cover exists, omit `cover`; the site creates a distinct dated typographic cover automatically. Artwork must be visibly labeled as illustration, including AI-generated artwork. Actual news photography requires a verified source and reuse rights.

Optional story `locations` is a list of objects with `label`, `lon`, and `lat`. Include only relevant, well-established reporting locations. These represent approximate locations on an illustrated world overview, not exact incident coordinates, disputed borders, or measurements. Omit when location is immaterial or uncertain. Numbering and the map are assembled automatically from available locations.

## Publication and review
For the fourteen-day trial, create `drafts/YYYY-MM-DD.json` and notify the owner with a concise editorial summary, uncertainty flags and a link to the draft. Do not place drafts under `data/editions/`. A later explicit publish instruction promotes the reviewed JSON. If sources or access are insufficient, report the problem and leave the latest edition intact.

On promotion, validate with `python3 scripts/build.py` where execution is available. The Actions workflow must pass before deployment. Never modify application code or permissions as part of a routine edition task. Never add API credentials or spend paid API credits. Do not send email or social posts.

## Corrections
Published corrections are explicit. Add `corrections` objects with `storyId`, `date`, `original`, `replacement`, and `reason` to the affected edition. The build displays these notices. Do not silently rewrite published claims. Story pages show the latest published account and link to dated editions; a daily archive is the historical snapshot.
