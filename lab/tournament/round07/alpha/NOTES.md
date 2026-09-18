# Round07 Alpha — durable nearest cover fire weighting

READY / nine runtime modules frozen. Exact shared parent: lab/survival/iteration03/beta/full_ring_exits. All18 walls and both exits retained; brain, economy, guard, protocol and all other runtime files match parent. Only fire_control.py changes. No production/judge/history changes. No370xx formal or360xx validation results read.

## Two bounded variants

V1 ported iteration03's nearest-threat rule unchanged: suppress the operator bonus when a strictly closer living static building will take the current hit; retain ties and base urgency, never use movable actors' old positions as guaranteed cover.

V2 adds the concrete imminent-breach caveat independently raised by Beta and Gamma: a1HP nearer wall prevents this turn's damage but can vanish before the next attack. Only suppress operator urgency if some strictly closer static building has HP strictly greater than the sum of all incoming robots' potential attack damage within3 of its footprint. This is a conservative sufficient condition for that building surviving the current volley, not an assertion all robots actually target it. Do not subtract robots our guns expect to kill: damage settles simultaneously. Base uses2x2 footprint, ties remain unsafe, dead buildings never shield. No thresholds from seeds or hidden target locks.

Concrete counterexample: robot(5,5), wall(6,5),50HP worker(7,5). At1000wallHP the operator bonus is falsely urgent; at1wallHP the worker is safe this turn but exposed after breach, so V2 retains the inherited bonus. Fixed base urgency remains in both cases. Joint shot allocation/reservation and ray interception are unchanged.

## Eight development self-survival cases

Nearest field10nights,22000/22001/22002/26006 in both seats, fixed round05Alpha background. Baseline and both candidates survive1300 rounds in all8/8, with zero illegal commands and zero foreign-only shots.

|Seed|Parent kill points C/D|V1 C/D|Final V2 C/D|
|---|---:|---:|---:|
|22000|370/371|370/358|370/358|
|22001|355/397|366/388|366/388|
|22002|349/358|337/357|337/357|
|26006|385/321|375/341|375/341|

Parent total2906, both variants2892 (-14). V1 and V2 have identical measured survival/kill points/baseHP; V2 is retained for its conservative imminent-breach behavior, not measured aggregate improvement. Candidate22000defender finishes1055baseHP versus parent1500. All other final baseHP equal parent. Therefore neither port nor follow-up establishes an overall scoring improvement. This is an independently motivated candidate for formal adjudication, with an explicitly negative aggregate development score observation; no universal superiority or100% official survival claim. Full raw records baseline.json, nearest-threat.json, durable-nearest.json remain intact; V1 source preserved in variants/nearest_v1_fire_control.py.

## Verification / review

30 regressions pass:24 inherited plus6 nearest/durable-cover tests, including current-volley damage summed across multiple attackers. The old1HP-wall test intentionally changes its expected future-priority behavior for V2, while preserving tie/dead-cover/footprint/movable-role tests. Gamma reviewed the durability condition and emphasized not subtracting same-turn kills. Beta independently gave the1HP-wall next-attack counterexample. Alpha warned Beta's larger stone batch to preserve return deadlines and handle exhausted shared deposits without idle mining. No peer code merged.

Parent manifest PARENT.json and final nine-module RUNTIME.json record exact hashes. Only fire_control.py SHA10c7a74c1916e2840e3d50bffd66d6923e4a6f699ecd98771cbd1771c2e2cfa3 differs. Root owns validation, ranking and release.
