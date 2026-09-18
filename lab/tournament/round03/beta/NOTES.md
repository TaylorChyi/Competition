# Round 03 Beta — frozen

Exact Alpha round02 inheritance, provenance in PARENT.json. Runtime changes only brain.py / guard.py. No economy, gun layout, point weighting, seed branches or hidden-state access.

## Selected mechanism

Emergency joint planning enumerates up to three operators' legal one-step positions and distinct gun assignments. It preserves busy roles as obstacles, rejects swaps and destination conflicts, accounts for ready-gun fire, and only intervenes for a useful vacating chain. Healthy crews keep shooting. Broad independent reshuffling was rejected.

A still-surviving endangered operator may leave the control ring one turn before potentially fatal accumulation. New-position risk is compared with health after subtracting present-position potential damage. Potential damage is an upper bound, not confirmed target selection: inherited best-effort escape remains available even when potential damage exceeds health. Once outside control range, the operator continues a substantially safer retreat instead of waiting for approaching robots; danger disappearing releases it back to ordinary gun-return routing.

## Causal local evidence

Published development failure 26006 nearest, defender parent: round87 worker HP45 / potential30 fires; round88 HP15 moves and dies. Second role round113 HP50 / potential30 fires; round114 HP20 moves and dies. Judge chooses robot victims before player movement, so movement does not cancel already-scheduled damage. Exact official robot/player ordering remains unproven.

Early escape alone delayed deaths to89/115, not a cure, despite base reaching1033. Completing continued retreat eliminates both first-night deaths; final first death is230. Final defender base still dies776: improved survival is bounded and does not solve later nights.

## Focus variants and failures retained

1. Broad emergency joint plan: development-joint.jsonl; operators paired points -30. Rejected.
2. Fatal-only coordination: development-fatal-only.jsonl; too late, operators paired points -22. Rejected.
3. Anticipatory escape plus narrow coordination: development-anticipate.jsonl; incomplete escape path only delays first deaths. Completed same mechanism, retaining development-final.jsonl and final fallback-restored development-frozen.jsonl. No further parameter sweep.

## Frozen development evidence

Fixed opponent lab.tournament.round02.alpha, field waves, commerce, ten nights; six halves only. Not a formal win-rate claim. R3 reserved seeds untouched.

|seed/mode|Beta seat|survival Beta/parent|kill-point difference|Beta deaths|Beta shots|
|---|---:|---:|---:|---:|---:|
|22001 operators|0|1300/1300|17|1|1299|
|22001 operators|1|1300/1300|-14|0|1199|
|22002 advance|0|496/350|17|0|535|
|22002 advance|1|350/496|-17|0|386|
|26006 nearest|0|1300/508|370|0|1259|
|26006 nearest|1|776/1300|-264|8|646|

All six invalidCommands=0, incoming-only shots, p95 decision 1.55–3.284ms. Advance remains unresolved and asymmetric. The shared economy makes the opponent's trajectory change, so cross-run parent survival is not an isolated treatment measurement.

## Checks

Candidate package aliased as agent: all15 public test_field_defense.py regressions pass after root corrected the old forced-wait assertion to permit safe retreat. Own check_joint.py / check_retreat.py pass: vacating chain without swap, healthy crew keeps firing, busy operator remains blocked, outside-gun retreat reduces exposure, danger gone resumes return.

Safety limitations: exposure sums possible incoming attacks, not actual target locks; distance4 is an approach heuristic. Future robot movement may invalidate a locally safer square. Gun opportunity cost can still increase when saving an endangered operator. No guaranteed ten-night or100% claim.
