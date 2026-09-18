# Iteration04 Alpha — one rear rocket behind18 walls

READY / frozen for root independent qualification. Exact parent: lab/survival/iteration03/beta/full_ring_exits. Only brain.py TOWER_LOADOUT changes from three railguns to(railgun,railgun,rocket). Total3 guns, initial75gold, same positions and18-wall double-exit construction. All other eight runtime modules unchanged. No R7 threat-weight port, extra buying rule, late conversion, guard change, or judge modification.

## Mechanism / causal hypothesis

Current nearest-target robots stop to attack closer walls, forming persistent clusters outside the defensive enclosure. This creates a different AOE opportunity from the rejected open-defense/advance rocket experiments. Third existing gun is the side-rear location selected by inherited _tower_sites; replacing it preserves both forward railguns. Level1 rocket range10 covers the wall ring despite rear placement. Levels1/2/3 fire1/2/3 missiles; each20 center/10 neighboring8 cells, overlapping damage stacks, with three empty cooldown turns (minimum volley spacing4 rounds). The official ray mechanism and this judge intercept robots, not static walls; walls do not block friendly railgun rays. Rocket explosions do not damage own walls in the model.

Inherited economy already prefers delivering weapon coupons to rocket, and prioritizes Weapon2 when a rocket reaches2. This is unchanged behavior newly exercised by the loadout, not a new purchase policy. Inherited rocket-first mixed allocation still has the known constrained-rail target opportunity-cost counterexample; it was intentionally not changed so this is a loadout-only experiment.

## Eight allowed development episodes

Field10nights, nearest, fixed R5Alpha background, both seats. All8/8 survive1300, zero invalid commands and zero foreign-only shots. No validation360xx or formal370xx results read.

|seed|seat|parent kill points|rear rocket points|final stationHP|first rocket2 round|rocket3 round|
|---|---|---:|---:|---:|---:|---:|
|22000|challenger|370|470|1180|308|—|
|22000|defender|371|456|1240|193|—|
|22001|challenger|355|420|3000|455|—|
|22001|defender|397|552|1500|175|836|
|22002|challenger|349|503|1430|310|1073|
|22002|defender|358|474|1380|297|1212|
|26006|challenger|385|523|1500|296|1090|
|26006|defender|321|432|2880|701|—|

Total3830 vs2906 (+924) on these allowed development episodes, with survival retained. Parent reference is round07/alpha/baseline.json, whose policy imports this exact full_ring_exits source and uses the same judge/background/seeds. This is a controlled development observation, not proof of unseen survival or official superiority. Lower finalHP in several halves is retained, not hidden. No second variant attempted: first configuration meets the allowed development gate and has material scoring effect, so independent validation is preferable to more tuning.

## Damage and cooldown diagnostics

All observed rocket volley gaps are at least4 rounds. Observer-estimated incoming raw damage181250; same-turn own-shot overkill2180 (1.20%). These are calculated from observed robotHP and our emitted valid attack commands, aggregated across railguns and rocket. They do not include later enemy movement, damage caused by the fixed background, or authoritative engine attribution; they are not a claim of exact official damage. Raw per-night quantities, every rocket volley round, actual upgrades, final/nightHP, equipment, operator counts and income are in rear-rocket.json. Highest observed p95 decision time30.2ms.

## Verification / peer challenge

27 tests pass:24 inherited regressions and3 loadout/AOE/ray checks. Cluster example: a level2 rocket firing twice into four adjacent100HP robots exceeds80 effective damage, greater than a same-level railgun's4-turn80 damage upper bound. Beta's partial-wall project was challenged with the case where a0-direct-damage rear wall still prevents bypass after a front-wall breach; measured wall damage alone is not causal redundancy. Conversely, reducing walls may reduce the clustering that produces rocket benefit. No wall changes merged.

Nine-module hashes in RUNTIME.json; PARENT.json gives parent hashes. Sole delta brain.py SHA617ecc3cf32aacc8e0722b8ddf24ae5a3b67d7f853cf4cd5a3a0e1c6ed12bc79. R7 runtime remains untouched. Root owns independent gate, adoption, packaging and publication.
