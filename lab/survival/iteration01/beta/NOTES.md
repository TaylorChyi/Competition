# Survival iteration01 Beta: retain parent

Root AGENTS reviewed. Owner scope is experimental only; production packaging/release belongs to root. Inherited frozen round05/alpha9runtime files exactly. Final default remains byte-identical to that parent. No previous Beta retreat logic was carried over. No tournament or judge files edited.

## Goal and evaluation

Only own ten-night survival is evaluated. Fixed opponent round05.alpha.brain.decide; development22000 nearest,22001 operators,22002 advance, each both seats, field waves10nights/commerce. No inter-agent win rate. Parent itself survives4/6 of these cases, so100% gate is not met.

Detailed per-night/per-turn evidence is preserved in baseline-<seed>-<seat>.json and front_arc-<seed>-<seat>.json: cash, roleHP/backpacks/coordinates, gunHP/level/cooldown, visible incoming robots, commands and potential base pressure. Corresponding results.jsonl retain every night's HP, equipment, operator deaths and other judge metrics. Trace observations are before that round's actions; summary nightHP is after the round.

## Causal diagnosis: advance weak side

Parent defender starts night3 round331 with station1400HP/level2, cash112 (next station voucher150), three guns all level1/1000HP, and all three operators at full health. Round350 station50HP and potential base contact damage110; all3 guns shoot and operators remain full health. Base dies350. Thus the immediate cause is sustained base damage and insufficient clearing, not operator death, retreat, or an empty defense crew.

The side-rear gun(32,9) cannot shoot the observed round331 robot atx25 (distance7, level1 rail range6); the two front guns can. This justified testing earlier gun coverage.

Observed incoming new HP across first three waves is1980/2020/3380. Three level1 railguns have theoretical maximum1800 own damage per60-round night, before range/collision/opportunity losses. This is a full-clearing capacity comparison, not a proof survival is impossible: opponents may contribute damage and some robots never reach base. It does show why repeated station upgrades without gun growth cannot be assumed to solve later waves.

Walls are at station footprint ring2, while robots can shoot station from distance3. A wall does not guarantee blocking a robot's already-in-range base attack. No building-absorbs-damage or line-of-sight assumption was introduced. User has confirmed robots move OR attack in a turn.

## One reasoned layout experiment, rejected

Preserve the first two front guns and restore the third forward-arc site instead of side-rear. Defender third site(31,11) instead of(32,9), mirrored for challenger. Same economy/loadout/guard/fire control. Runtime snapshot in front_arc/; final default restored parent.

|case|parent survival|front arc survival|
|---|---:|---:|
|22000 nearest seat0|1300|901|
|22000 nearest seat1|1300|1264|
|22001 operators seat0|1300|1300|
|22001 operators seat1|1300|1300|
|22002 advance seat0|756|757|
|22002 advance seat1|350|351|

Ten-night survival falls4/6→2/6. Advance gains only one round each; nearest loses both successful cases. Rejected; no second arbitrary coordinate sweep. Adv right shots377→396 without fixing survival. Operator damage risk on other modes outweighs the small earlier coverage.

## Cross review

Alpha's gatling two90-degree10HP targets example is valid forlevel2 split shots. Counterexample sent: front level1 gun(29,11), incoming(25,10) is4 away, outside gatling3 but inside rail6. Advance may reach station attack range before enough shots; first-night base damage must be checked, not only eventual kills. Gamma informed of the112 cash/150 voucher and all-level1 night3 bottleneck.

## Outcome

No strategy patch recommended from this branch. Preserve parent, retain failed experiment and causal traces for integration with independently validated economic/firepower improvements. Local checks do not establish official or unseen-wave survival;100% has not been reached.
