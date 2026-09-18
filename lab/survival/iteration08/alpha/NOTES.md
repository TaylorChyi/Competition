# Iteration08 Alpha: revealed failure diagnosis

Status: READY frozen pending independent qualification. Started from exact R9 Beta champion and carried forward iteration07 rear-rocket loadout and one-front-before-rocket3 purchasing. Last authorized mechanism changes only WeaponUpgradeVoucher1 usage target preference: both level1 railguns before level1 rocket. Weapon2 remains rocket-first. iteration07 remains frozen/rejected.

Only revealed36004 defender and36008 challenger were inspected. Both original candidate and R9 champion rerun with field/nearest/commerce/10 nights and fixed R5Alpha background. Full commands, visible state and results in trace-36004-defender.json / trace-36008-challenger.json. Other validation seeds and fresh560xx were not read.

## 36004 defender
Iteration07 dies1278; champion1300. Candidate upgrades station2 at303, rocket2 at560, rail2 at829. It never buys a rocket3 voucher. At1040 it has54 gold, one front rail dead and other level2 rail200HP. It spends50 rebuilding both by1110. Station2270, only4walls remain; workers cannot replenish the wall ring, both front guns die again by1150. Further cash54 is available on next day, but only one gun is built; workers die1246 and1256, station dies1278. Champion finishes with1320HP.

Candidate firing actions per nights7/8/9/10:116/93/62/23 vs champion120/169/123/104. Different weapons naturally have different cadence, so action count alone is not damage equivalence. More diagnostic: candidate wall-build actions2/2/0/0 vs champion2/4/4/1. The ongoing failure combines missing sustained front fire, deaths and maintenance collapse; immediate cash starvation does not explain it.

## 36008 challenger
Iteration07 dies1161; champion1300 with1500 stationHP throughout. Candidate upgrades rocket2 at187, rail2 at450, rocket3 at826. The150 purchase809 leaves3 cash, but cash is28 by850; a destroyed front rail is rebuilt the following day, another rebuilt next day. Candidate wall count falls12→8→4→3 while worker/pioneer deaths accumulate905/906/1012/1022/1113/1143. Thus the150 purchase may contribute to opportunity cost, but lack of25 reconstruction cash is not the observed common proximate cause.

## Candidate screen
Requiring two upgraded rails before rocket3 cannot change36004's trajectory: prior to829 no rail2, and after829 cash never reaches100 (max54), so neither Weapon1 nor Weapon2 can be purchased. A universal25 weapon reserve would instead delay the only front-upgrade purchase at820 (exact100 cash), with no demonstrated reason this repairs the wall/operator collapse. Neither proposed rule is justified as a common direct repair. Avoid a seed-driven or blind threshold experiment.

No claim of a successful rocket repair or official100% is made. The two unsupported purchase fixes were not implemented. Root instead authorized the single usage-target fix below; no threshold sweep or third variant.


## Last authorized mechanism and observed effect
Keep all purchase ordering, base emergency priority, carried voucher use, full-bag guards, shared-wallet accounting, vendor rerouting and dusk return guards. Only the Weapon1 target sort changes to railgun-first; Weapon2 remains rocket-first. This responds to both failures' under-upgraded front line before sustained wall/operator losses, not an assumed universal cash shortage.

36004: first front rail2 at560 instead of rocket2; second rail2 at708 instead of first rail2 at829. Rebuilt rail upgraded again1103, rocket remainslevel1. Station ends2760, wall maintenance can continue. 36008: front upgrades184/566, rocket2 delayed841; station stays1500. Those are causal policy counterfactuals within the same synthetic simulator, not proof of all official scenarios.

## Development qualification
All13 episodes survive1300, zero invalid commands. Original8 points4091 vs champion3186; all13 points6421 vs5060. Every episode improves points over the fixed background champion comparison. Reduced early rocket level sacrifices score relative to unsafe iteration07 (original8 4371→4091), explicitly accepted for observed survival.

Champion13 provenance: first11 from iteration07/champion.json using exact same R9 runtime and verified unchanged judge SHA; two newly revealed episodes rerun here. See champion-13.json. No fresh holdout read or run by Alpha.

| Episode | Candidate points | Champion points | Final station HP |
|---|---:|---:|---:|
| 22000 challenger | 496 | 415 | 1500 |
| 22000 defender | 605 | 459 | 1500 |
| 22001 challenger | 527 | 418 | 3000 |
| 22001 defender | 542 | 412 | 1500 |
| 22002 challenger | 490 | 408 | 1500 |
| 22002 defender | 490 | 331 | 1500 |
| 26006 challenger | 538 | 397 | 1500 |
| 26006 defender | 403 | 346 | 3000 |
| 36002 challenger | 378 | 345 | 3000 |
| 36007 challenger | 491 | 346 | 1500 |
| 46003 defender | 459 | 389 | 1500 |
| 36004 defender | 442 | 389 | 2760 |
| 36008 challenger | 560 | 405 | 1500 |


33 tests pass:24 inherited field/economy/joint fire tests,5 prior purchasing regressions and4 new target-order regressions (first front, remaining front, then rocket, Weapon2 unchanged). Reproduce candidate with `PYTHONPATH=CoreGeek/src:. python3 -m lab.survival.iteration08.alpha.develop`. diagnose.py explicitly imports frozen07; diagnose_fixed.py imports frozen08. Nine SHA entries in RUNTIME_SHA256.json. Only brain/economy differ from R9; economy only one target sort differs from07. Root independent qualification still required; previous failures show development passes are insufficient for official safety claims.
