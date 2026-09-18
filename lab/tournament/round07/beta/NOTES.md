# Round07 Beta — retain exact18-wall parent

Final top-level9runtime files are unchanged from lab/survival/iteration03/beta/full_ring_exits, verified against PARENT.json hashes. Both stone-batch variants are rejected. This is an identical-strategy candidate and may produce duplicate-strategy ties; root should deduplicate rather than claim three independent strategies.

## Bounded experiments

Default adjacent-stone batch remains min(4,needed). batch10/ tests min(10,needed) immediately. after_screen/ tests min(10,needed) only after at least4live walls exist, otherwise keeps4. Both preserve18walls/two exits, dusk return, and immediate construction when the adjacent mine vanishes and stone is already carried. No new-mine trip merely to top up10. No third variant.

8development episodes per variant, all nearest, seeds22000/22001/22002/26006, both seats, fixed frozen R5Alpha background, ten nights. Reserved370xx and independent360xx not read or used.

|variant|ten-night survival|invalid commands|total income|dedicated stone travel moves|mean first gun upgrade round|
|---|---:|---:|---:|---:|---:|
|parent|8/8|0|3140|1736|286.625|
|batch10|8/8|0|2894|1934|379.250|
|after_screen|8/8|0|2861|1600|317.750|

All24cases have identical full1300-round duration, so these total-income comparisons do not confound early death. Shared ore depletion/routes can still change trajectories; this is measured policy behavior, not proof a particular step caused every gold difference.

## Case-level upgrade and opening-wall effects

|seed/seat|parent first upgrade|batch10 first upgrade|after_screen first upgrade|first-night walls(parent /batch10 /after_screen)|
|---|---:|---:|---:|---|
|22000/0|304|428|305|7 / 9 / 6|
|22000/1|192|301|290|4 / 7 / 4|
|22001/0|432|297|418|7 / 9 / 6|
|22001/1|175|292|175|3 / 7 / 3|
|22002/0|421|418|570|7 / 9 / 6|
|22002/1|295|690|295|4 / 7 / 4|
|26006/0|288|300|303|8 / 9 / 7|
|26006/1|186|308|186|2 / 5 / 2|

The simple batch10 proposal raises first-night wall count in these cases but spends more later mining travel and delays first upgrades overall. The conditional batch saves136stone-travel moves yet loses279income and delays average first upgrade by31.125rounds. Hence neither supports the intended economic/firepower improvement; survival alone does not establish a benefit over the already-qualified parent.

## Regressions and evidence

check_batch.py proves each added branch actually triggers, the conditional version retains its initial4wall condition, no adjacent ore plus carried stone returns toward construction without calling a new mining trip, and round70 return preempts collection. development.jsonl has all24 complete records with per-night wall/base/role/equipment HP, cash, income, upgrade events and labor. Variants remain intact as failed experiments; no runtime was copied into final default.

Cross-review sent to Alpha/Gamma: a1HP closer wall only guarantees the current attack target, not next-turn safety. Alpha adopted robust-wall health>total nearby potential damage for its bonus filter. Gamma was advised to distinguish immediate targeting from approaching risk when a closer wall can break.
