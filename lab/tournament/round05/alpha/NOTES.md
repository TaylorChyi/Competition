# R5 Alpha: narrow economy + conservative joint fire

READY / runtime frozen. Only this owner directory changed. Inherited R4 Gamma exactly, then applied two independently named deltas. No300xx read, no judge or production changes.

## Exact change

Economy is byte-identical to the frozen R5 Gamma rejected prototype at `lab/tournament/round05/gamma/rejected_economy/economy.py` (sha256 dfb3d1153ce765d0d02d4130215ff784819843e77bc1cdb18fb3b6387eb387c9): remove only the two round>130, level1, any-damage forced-station-first exceptions in urgent_refit/develop. The below75% station priority, eventual station purchase, real cash, complete return budget, capacity, collision and immediate carried-voucher use remain. This does NOT prohibit buying station vouchers above75%; it puts weapon upgrades before station in that nonurgent case.

Fire control is R4 Alpha's conservative joint allocation: at most3 ready adjacent railguns and6 permutations, all robots retain original-health ray interception, only incoming robots contribute utility; relative to baseline order effective damage must not decrease, kill count must strictly increase, and threat utility must strictly increase. Otherwise preserve original order. Busy/guard-moving/cooling operators are excluded before planning. R4 Alpha tied regular wins with Gamma and lost overtime1W2D2L, so this is not established generally superior fire control.

Causal example retained: flexible gun A can shoot X or Y, constrained gun B only X; greedy A→X leaves B idle, whereas B→X and A→Y kills both. This proves a local opportunity, not aggregate superiority.

## Bounded development

One combination variant; no additional thresholds or search. Field wave, ten nights, two seats each, scores aggregated across seat swaps:

| Opponent | 22001 operators | 22002 advance | 28002 advance |
|---|---:|---:|---:|
| frozen R4 Gamma |1999:1965|452:452|342:345|
| frozen Gamma rejected_economy prototype |1946:1959|452:452|343:343|

Raw records combo-vs-parent.json and combo-vs-economy.json contain all12 halves. Every half has zero invalid commands. Operators sides all survive1300 rounds. Advance22002 strong/weak sides survive756/350 rounds. Advance28002 combo survives599 left and339 right; parent right352. The previous983-round single-opponent anecdote does not reproduce and is rejected as promotion evidence.

Against parent, operators improves34 points; against economy alone it loses13. The pairwise interaction prevents claiming a universal positive increment from joint fire. This candidate is an independently plausible combination for formal adjudication, not a100% or robustly superior policy. Gamma separately reported economy-only vs parent operators1970:2007, advance452:452 and342:345; that peer report does not replace our direct combination data.

## Tests and review

24 deterministic tests pass: four inherited joint-fire counterexamples,18 inherited field/economy regressions, and two new purchase-order cases (1490HP level1 chooses available gun upgrade,1124HP preserves station priority in both entry points). Test roles already hold Medicine to isolate purchase ordering from the unchanged opportunistic medicine branch.

Gamma confirmed the two economy edits and byte equality at development time; the matching implementation is now preserved in `gamma/rejected_economy`, while top-level Gamma has reverted to the parent. Alpha warned Beta of the opportunity cost when emergency repositioning silences a ready gun that could kill the only nearby attacker; no peer runtime was changed. R4 Beta's independent ray/reservation/busy/cooldown audit remains applicable because the joint-fire implementation is unchanged.

## Reproduction provenance correction

The unchanged historical `develop_vs_economy.py` imports mutable top-level `round05.gamma`; rerunning it now would select a different opponent and overwrite the historical JSON. Do not use that entry point to reproduce this evidence. Use `evidence_review/reproduce.py`, which explicitly imports `round05.gamma.rejected_economy.brain.decide`, writes only new audit artifacts, and compares every recorded field except `p95DecisionMs`. The original six-half JSON and frozen top-level Python files remain unchanged.

Audit completed: all six historical halves exactly reproduced against the frozen rejected_economy prototype, excluding only p95DecisionMs. Per-field comparisons, fresh outputs and source hashes are in evidence_review/. No original result or frozen top-level Python file was modified.
