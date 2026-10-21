# ChatGPT publication automation

Recurring publication for this repository is owned by ChatGPT/OpenAI automation.

## Morning edition
Follow `EDITORIAL.md` exactly, especially the editorial promise, research and comparison rules, story-selection standards, schema, report lengths, regional coverage, story-thread continuity, visuals, evidence standards, corrections policy, and the steps under **Publication (morning run)**. The references to Claude in `EDITORIAL.md` describe the previous operator; ChatGPT now performs that role.

Publish one new edition each morning. If today's edition already exists, do not replace it unless correcting a documented factual error under the corrections rules.

## Afternoon update
Each afternoon, update that day's edition in place using the rules under **Evening update** in `EDITORIAL.md`, even though that section currently says the task is switched off. Treat it as the active afternoon-update specification.

Use labels of the form `Afternoon update · <time> CT` rather than `Evening update · <time> CT`. Research what materially changed after the morning cutoff; update existing stories first and add at most two genuinely major new stories. Do not rewrite the morning record merely for style. Set `updatedAt` and `updatedLabel`, rebuild, validate, commit, and push.

## Editorial continuity
Preserve the same standards used by the prior Claude runs: consequential-change selection rather than volume, concise original prose, the existing story lengths and report structure, direct source URLs, careful attribution and uncertainty, stable thread IDs, geographic discovery without quotas, and the existing Night Observatory visual system. Every World and Frontiers story must keep the required map, chart, or original SVG illustration. Do not use stock imagery, paid image APIs, or invented documentary scenes.

Do not alter application code, styles, workflows, `data/site.json`, `README.md`, `EDITORIAL.md`, or this file during routine news runs.
