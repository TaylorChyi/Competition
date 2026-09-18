# Iteration03 Alpha — confirmed nearest-target fire weighting

READY / independent candidate frozen, NOT survival-gate passed. Nine runtime modules inherited from frozen R5 Alpha; only fire_control.py differs. No combined transport/fallback or late rocket change carried forward. No protocol, judge, production or older directory changed in this stage.

## One change

Keep inherited base-distance urgency. Remove an operator proximity bonus only when a strictly nearer living static friendly structure exists: wall, station (actual2x2 footprint), railgun, gatling or rocket. Equidistant operators remain possible targets. Living1HP structures still exist for simultaneous attack resolution; dead structures do not shield. Moving controllable actors are not used as guaranteed cover for another actor, because their old positions may differ from same-turn actions. This follows confirmed nearest-unit targeting, while retaining conservative handling of ties and future threats. It does not encode the simulator's unit-ID tie breaker.

Gamma identified the moving-actor caveat during review; an initial all-living-unit draft was narrowed to static structures before freeze. Both drafts had identical survival/HP in this six-case development. The initial run is retained as nearest-threat-first-review.json, not promoted as a separate optimization variant.

## Own survival evaluation

Fixed R5 Alpha opponent; field waves10 nights; nearest priority for all six seed-seat episodes. No candidate-vs-candidate wins or rankings. Late-wave composition remains synthetic.

| Seed | Baseline rounds challenger/defender | Candidate rounds |
|---|---:|---:|
|22000|1300/1300|1300/1300|
|22001|1300/1300|1300/1300|
|22002|1289/1161|1289/1161|

Both pass4/6 ten nights. Candidate22001challenger final stationHP1360 versus baseline1340; every other nightHP matches. No proven survival improvement. All candidate actions legal; no foreign-only shots. This is a bounded consistency change for combined review, not evidence of100% survival or official acceptance. No validation runs were attempted because development is not6/6.

Raw baseline.json / nearest-threat.json include nightly stationHP, operators, equipment, upgrades, start/end-night units/bags/cash/income/shots/incoming counts. 22002 baseline later failures involve repeated operator deaths and maintenance costs: defender at980 has three level1 guns and only5gold, then two operators die993/1002; challenger enters final night with260 baseHP and125gold, below150 final station coupon. This weight change alone does not resolve those failures.

## Tests and cross-review

29 regression tests pass (24 inherited +5 nearest-threat tests): nearer wall suppresses bonus, ties preserve it, station footprint matters, dead/live1HP wall distinction, and another movable operator cannot guarantee cover. Gamma guard read-only audit found no blocking defect: strictly nearer in-range static structure removes risk, ties remain risky, and distance4 approach risk is removed only when structure is already attackable. Suggested explicit out-of-range structure regression. No guard code merged.

RUNTIME.json records all nine final hashes; PARENT.json records R5 source. Root owns gate adjudication and publication.
