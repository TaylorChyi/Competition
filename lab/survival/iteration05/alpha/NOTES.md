# Iteration05 Alpha — rocket upgrade-order diagnosis, rejected

COMPLETE / REJECTED. Top-level nine runtime files restored byte-for-byte to18-wall three-railgun full_ring_exits. No mixed rocket candidate from this stage is approved. PARENT.json records the experimental initial source(iteration04 rocket); RUNTIME.json records the final restored fallback. The rejected complete nine-module prototype and its31 tests are preserved in rejected_balanced/ with its own RUNTIME.json.

Only revealed former validation cases36007challenger and36002challenger were inspected, explicitly reclassified as development regressions. No other360xx,380xx or390xx results used. Existing iteration04 candidate remains unchanged and rejected for survival qualification.

## Matched failure evidence

Same seed, seat, field/nearest10nights, R5Alpha fixed background:

-36007: original rocket dies1017, three-rail parent survives1300. Rocket2 at172, rocket3 at581. By590 cash4;650 only one living operator and a210HP front railgun;720 still cash4,12walls and that damaged gun, without25 to rebuild. Cash stays4 until946. Station695 at780,450 at910, and destroys1017. Three-rail counterpart has95gold at650, rebuilds to3guns/17walls by720 and holds station1240 through1300.
-36002: original rocket dies1039, three-rail survives1300. Rocket2 at327; at720 cash100 while front railgun345HP remains level1. The special priority waits for150 rather than buying100 first-level gun upgrade. At960 it buys Weapon2 and cash becomes0; rocket3 at976. Entry into night8 has13walls and two level1 front guns; by1030 both front guns and two workers are gone, station destroys1039. Parent upgraded its station at715 and survives with3000HP.

These are observable resource/upgrade consequences, not proof that cash priority is the sole cause; changing upgrades also changes enemy kills, worker survival and later economic routes. Full650-onward per-round commands, cash, equipment, walls, bags, roles and incoming robots are in failure-counterfactual.json(36007) and failure-counterfactual-36002.json. diagnose_failure.py explicitly imports frozen iteration04 rocket and three-rail parent, so active top-level fallback does not silently change the opponent being diagnosed.

## Exactly one attempted correction

Delete only the two-line special rule placing WeaponUpgradeVoucher2 first whenever a level2rocket exists. Keep urgent station priority and otherwise use inherited ascending gun levels: upgrade existing level1guns first, then level2guns. Keep18walls, mixed loadout, original fire/guard/geometry, real wallet/capacity/delivery checks. No thresholds swept.

Causal counterfactual:36007 now front railgun2 at433 instead of rocket3 at581, survives1300 with1500stationHP.36002 front railgun2 at808 instead of rocket3 at976, survives1300 after station2 at1108; night8 station only265HP. Both revealed failures are rescued, but the original development22000challenger now dies910. In that new failure, rocket2 at308 and railgun2 at698; both workers/pioneer suffer deaths before the7th night collapse. This is not an acceptable general repair.

## Full scheduled8+2 result

|seed|seat|corrected survival rounds|
|---|---|---:|
|36007|challenger|1300|
|36002|challenger|1300|
|22000|challenger|910 — new failure|
|22000|defender|1300|
|22001|challenger|1300|
|22001|defender|1300|
|22002|challenger|1300|
|22002|defender|1300|
|26006|challenger|1300|
|26006|defender|1300|

7/8 original development +2/2 revealed regressions =9/10, so rejected. All ten zero illegal commands. Full records balanced-upgrades.json; develop.py explicitly targets rejected_balanced so reproducing does not run the restored top-level fallback by accident.31 prototype regression tests pass, demonstrating that action correctness and local purchase ordering do not imply survival.

No second correction attempted. Root instructed reverting to18-wall three-rail; done. Future lower-cost wall/mixed-gun combinations need separately authorized and independently checked evidence, never an assumed additive benefit.
