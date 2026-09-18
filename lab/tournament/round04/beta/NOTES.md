# Round04 Beta — frozen combined candidate

## Inheritance and final choice

Started from exact Round03 Gamma champion (PARENT.json). Preserve its two-front/one-side-rear tower coordinates and all inherited economy. Runtime edits only brain.py / guard.py: explicitly reintroduce Round03 Beta's emergency vacating-chain coordination, anticipatory off-gun escape and continued self-rescue. No changes to old frozen rounds or reserved29000–29009 seeds.

Two focused variants were tested. Selected **combined/** snapshot, also current default. Rejected extra **holdshot/** logic from default because its six development outcomes exactly match combined and establish no incremental benefit. Keep its synthetic tests and snapshot for later investigation. Default uses no new state, environment or configuration.

## Development, not official performance

Fixed opponent Round03 Gamma champion, field ten nights, commerce on. Results in development-combined.jsonl and development-hold-shot.jsonl. Six halves per variant, identical metrics below:

|seed/mode|seat|Beta / opponent survival|point difference|Beta deaths|shots|night moves|
|---|---:|---:|---:|---:|---:|---:|
|22001 operators|0|1300 /1300|+1|0|1207|10|
|22001 operators|1|1300 /1300|-59|1|1326|85|
|22002 advance|0|756 /350|+100|0|855|0|
|22002 advance|1|350 /756|-100|0|377|0|
|26006 nearest|0|1300 /629|+274|0|1211|16|
|26006 nearest|1|1300 /1300|-51|0|1450|54|

All invalidCommands zero; combined p95 decision 1.902–2.894ms. Advance seat disadvantage remains. Operators loses the paired points comparison. Known26006 defender now survives ten nights with zero deaths versus Round03 Beta survival776; this is a layout/defense interaction across versions, not an isolated causal estimate. Do not claim general100% win rate.

Movement totals are finite and no illegal moves appear. Healthy/no-threat deterministic tests prove no needless healthy coordination and release back to gun-return behavior after danger clears. These checks do not rule out every multi-turn oscillation under changing enemy geometry; full path-cycle analysis was not performed.

## Rejected hold-shot experiment

Only considered ready railguns with an operator who would otherwise move. defense_targets computes into a copied reserved map. Only the current gun's incremental predicted damage sufficient to kill the robot's full observed HP counts; previously reserved damage cannot manufacture this guarantee. Actual ray_hits includes foreign-target robots as physical interceptors. Current complete potential enemy damage is deducted before judging surviving threats. Trial reservations are committed only if a real firing command is sent.

Synthetic check_hold.py proves the branch actually fires for8HP operator /5damage near small /10HP target, retreats if current damage is lethal or target cannot be finished, and does not count a foreign-team blocker as transparent. Six development halves show no observable incremental effect; natural branch frequency was not instrumented, so no claim of zero natural triggers. Rejected from delivered default.

## Validation

- Candidate aliased as agent:15 public test_field_defense.py checks pass.
- check_retreat.py (also imports check_joint.py): endangered worker follows a vacating teammate without swap; healthy crew keeps shooting; busy role remains blocked; continued retreat lowers exposure; danger gone resumes return.
- check_hold.py tests the rejected holdshot snapshot and passes, including foreign-team obstruction.

## Remaining risks

Exposure is an upper bound, not a known target lock. Movement does not promise to cancel already scheduled attacks. Official robot/player exact timing remains uncertain. Escape can sacrifice needed gunfire when robots actually attack buildings; no profile or hidden state is consulted. Joint planning preserves executable fire as a cost but prioritizes reducing imminent operator mortality. Later geometry can invalidate a currently safe square.
