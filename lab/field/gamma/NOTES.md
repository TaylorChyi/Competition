# Independent field audit

No arena or frozen-league Python files edited. Only this note and tests/test_field_arena.py authored. Evidence sources: current official repository docs and code; user's play summary is a partial account, not a turn-by-turn replay.

## Most consequential calibration gaps

1. **Wave pressure mismatch (confirmed code vs reported observation, not a newly proved official constant).** arena heavy first night=14 small+6 middle+1 large=21 per team; user's field summary incoming35,total70. The35 mix/positions are not supplied. The historical two-night success percentages tested a substantially smaller first wave and cannot certify this observed field wave. Central rectangular spawn distribution, movement tie-break, and seeded counts are assumptions, not documented official spawn specifications. Minimum action: preserve old tests and add separate field-calibrated35-per-camp scenario with openly labeled unknown composition/positions. Never call the guessed mixture the official35 wave.

2. **Operator targeting/cover model is not official.** guard previously discounts incoming damage90% when any healthier building is strictly closer. Official task4.7.3 only says robots attack units obstructing movement; no nearest-building protection, wall projectile blocking, single-target tie-break, or guaranteed station-first choice is promised. arena nearest/advance picks one victim; that does not cover an operator-focused hypothesis. Beta is removing the false protection assumption. Add distinct adversarial priority profiles for testing; do not silently rewrite unknown robot behavior into an asserted official rule.

3. **Base footprint is definitely2x2, not3x3.** Interface113 says2*2, pos=top-left. protocol footprint uses correct four cells for upward-increasingy. Arena attack separation uses minimum distance to footprint, but upgrade use and economy use-carried use only anchor distance<=1. Task shop instructions say around the target building one cell. Right-edge example base(7,24), pioneer(9,23) is adjacent to occupied(8,23) but anchor distance2. The new regression fails because arena rejects the voucher. Minimal patch: use building-footprint separation for interaction range, retain canonical anchor as command target; adjust economy approach goals/adjacency consistently. This is an unnecessarily restrictive strategy/simulator geometry mismatch, not proof the particular169 summary position failed: field base anchor was not supplied.

## Official-rule regressions and current result

`python3 -m unittest discover -s tests -p test_field_arena.py -v`:3 tests,2 pass/1 fail.
- PASS explicit2x2/top-left footprint.
- PASS first-night death at92 remains dead at150, revives151 with original backpack. Matches both task4.5.2 and user's92/151 report. Therefore no evidence of an off-by-one error in that reported death.
- FAIL station upgrade from legal footprint-adjacent right edge: remains level1 instead of becoming2/full3000HP.

Additional resurrection limitation: arena begin revives every dead role at phase20 without remembering death round/day. A death during a later day's first20 rounds would incorrectly revive that same day rather than the following day. Current arena has no ordinary daytime combat that can create that state, so it is not a demonstrated cause of this field failure and no fabricated combat-rule regression was added. Minimum future fix if daytime damage becomes modeled: record death day and require next day's phase20. Base-destruction respawn eligibility is also not settled by the supplied excerpt.

## Settlement aspects that are consistent / unresolved

- Nights71–130 and201–260; respawn151. Current modulo timing matches these boundaries.
- Docs explicitly say all attacked damage settles at turn end. Keeping a robot's attack on the turn it is lethally hit is consistent; do not make instant-death suppression a free defensive improvement.
- Attack range3 and Chebyshev distance are explicit. Multiple robot targets, shots through walls, and target priority are not specified in available prose. No tests asserting these unknown mechanics were added.
- Official team.type and robot.targetTeam are challenger/defender. User labels teamB do not justify changing targetTeam filtering. All70 robots should remain observable while our incoming set is35 only when labels support that.
- Summary claims no voucher use but later1820 baseHP. Original base has1500 maximum and upgrade sets3000, so1820 is compatible with successful upgrade followed by damage. These two summary claims cannot establish failed delivery. Need lastRoundRoleActionResults and level fields around161–201 before asserting non-use.
- Four official task points obstruct movement; arena omits them. Real geometry can delay mining and return routes compared with shared local samples. This compounds income/transport optimism but requires actual map positions for field replay.

## Peer counterexamples sent

Alpha: urgent_refit return-deadline check can be bypassed by develop's general shop path (especially an unpaired courier with no tower-return assignment); unify all new shopping trip admission. Also make base interaction distance consistent with2x2 footprint. Existing vouchers must still be delivered.

Beta: new guard's legal retreat candidates all retain current-tower adjacency. A lowHP operator with all gun-ring cells lethal but an escape one cell beyond the ring gets no escape and can die firing. Consider emergency off-station retreat only under mortality risk, while keeping usual firepower. Fire_control urgency currently ranks only distance to base and may deprioritize a robot beside a fragile operator farther from base; include survival threats to operating roles without pretending the target rule is known.

All these are sent to peers/root for review. Root owns arena implementation and final official/stress-test distinctions.

## Root patch verification and interpretation boundary

Root added died_round, field35/36 profile, operators priority, and reported-elimination cleanup. Expanded suite now8 tests; at audit time7 passed and only footprint-edge use test failed, pending root's deliberate documentary-interpretation patch. New lifecycle tests confirm same-day death waits until following day, settlement records actual death round, and inventory remains intact. Hypothesis-profile checks are explicitly separate from official-rule tests.

The edge-use test is renamed test_doc_interpretation_upgrade_from_station_footprint_edge: it encodes the reading of “building within one cell” plus2x2, not verified official engine behavior. Root deliberately retains the bot's conservative anchor-adjacent interaction subset; no claim of a field-proven failed/accepted edge use is made.

Beta follow-up: initial emergency escape patch could return a60%-improved but still lethal gun-ring cell before considering a truly safe off-ring escape. Concrete abstract exposure: current100,HP20,ringbest50,offring0. Sent fix request to prioritize nonlethal alternatives whenever current exposure is lethal. Fire-control operator exposure and avoidance of walking from safe into lethal cells cover the earlier reported counterexamples. Static guard thresholds normally require <=60% exposure plus>=5 improvement and low enough roleHP, limiting casual movement, but repeated dynamic-wave repositioning remains a stress-test question, not a proof of no lost-firepower problem.

Alpha follow-up observed purchase_route now shared by urgent_refit and ordinary voucher shopping. This closes the cited ordinary-shopping deadline bypass in current source. Original voucher delivery still uses conservative anchor-adjacent range by root's decision.

## Merged v1 failure / documentary ambiguity audit (read only)

Reviewed iteration1-results.json, field-failure-trace.json, current Beta defense, Alpha route retry, and draft docs/第二晚实战修复.md. No files outside this note changed; no new matches.

### Robot movement plus attack is unresolved

Task177 single-action sentence immediately follows4.4 player-role command table. It restricts those controllable roles, not explicitly autonomous robots. Section4.7.3 says robots attack blocking units but does not say movement and attack are mutually exclusive. Neither sentence proves that a robot cannot move one cell then attack in the same turn. Arena currently uses either/or in all three priority models. This is an important shared hypothesis: operators priority does not independently cover the action-timing uncertainty. A distance4 robot could enter distance3 and shoot under a move-then-attack model. Beta immediate exposure excludes distance4 and approaching exposure discounts it to0.35; its nonlethal-retreat characterization must be read under current-position damage estimates, not as an official survival guarantee. Root and Beta informed. No official-rule test or model change invented from this ambiguity.

### What the actual local failure trace proves

This is the generated local trace, not the user's missing game replay:
- At160, field defender cash65, worker20010 carries7 copper; at170 through185 that worker remains(19,14) and repeatedly tries(19,15), with repeated lastRoundRoleActionResults=False.
- Other worker sells4 copper, raising cash to85 by175. Seven copper remain unsold through200 and death.
- At200 all three roles are alive, cash85, baselevel1/1030HP. At220 and226 all roles still fullHP and all three towers issue attacks.
- Request227 has20 baseHP; settlement227 destroys base, request228 shows base and roles0. This local failure is a liquidity/route failure with live operators until elimination, not evidence reproducing the user's early-worker-death chain.
- Counterfactual7 copper sale would add35 to85, enough for the100 first voucher, but that arithmetic alone does not prove timely successful delivery or survival. Alpha's route fix must be checked by root's frozen rerun.

Current Alpha route explicitly attempts alternate service goals after a failed one-step path, rather than repeatedly attempting an unavoidably blocked final goal. It addresses the visible repeated(19,15) symptom. Current Beta prioritizes nonlethal escape candidates before accepting merely lower but lethal risk, fixing the prior100→50 vs safe0 counterexample. No observed code-level bypass of that new ordering remains. Neither establishes field acceptance.

### Draft documentation corrections sent to root

Overall draft correctly separates incomplete user summary, local scenarios and official rules. Retain those boundaries. Recommended corrections:
1. “把未售矿当现金等确定性缺陷” is too strong if read as unaffordable purchase: old urgent_refit used gold+ore to decide travel but actual buy required real gold>=price. Describe speculative travel based on unliquidated ore, which consumes return time, rather than implying fabricated money/overspending.
2. Explicitly list move/attack either-or among unresolved robot mechanics. Three target-priority modes do not test this independent uncertainty.
3. v1 has22/24 second-night survival vs released24/24 and fails promotion despite8/12 wins. Mark implementation as an unpromoted candidate until gate passes; do not imply it is already a deployed repaired release.
4. Keep field-failure-trace labeled synthetic diagnostic and distinguish227 local loss from user's249 official reported loss. Actual level/use results around161–201 remain absent, so voucher non-use is unproven.
