# Iteration07 Alpha: one front rail before rocket3

## Frozen candidate
Exact nine-module parent: `lab/tournament/round09/beta` (12-wall champion). Parent SHA in PARENT.json; final runtime SHA in RUNTIME_SHA256.json. Only brain.py (third opening gun becomes rocket) and economy.py (rocket2 special Weapon2 purchase priority requires at least one railgun level>=2) differ. Other seven modules exactly match parent. No second variant, judge or seed-specific policy changes.

## Revealed failure and causal counterfactual
Only revealed seed46003 defender was traced, using fixed R5Alpha background. Original iteration06 rocket dies1154; champion survives1300 with station1500 throughout. Original rocket2 at289, rocket3 at960; at720 cash100 but both front guns level1. Weapon2 purchased950 uses150 and leaves0; front gun later275HP cannot be rebuilt for25, destroyed1129, station dies1154.

The single changed priority purchases a front rail upgrade used696, delays rocket3 until1204. Station remains1500 every night. At950 cash110, at1110 cash135; a destroyed level1 rail is rebuilt before1110. The result supports early sustained front fire/health and retained repair liquidity together; it does not establish that cash alone caused failure. Runtime uses observed gun levels, never seed/round identifiers.

Prior rejected iteration05 required all level1 guns upgraded first and introduced a development death; that stronger rule is not revived. This rule only requires one rail>=2. Beta review notes that a badly damaged sole level2 rail can still leave the formation vulnerable after a later150 purchase; no universal safety guarantee is claimed.

## Fixed development, not independent qualification
Nearest, field assumed waves, 10 nights, commerce, fixed R5Alpha background. Original eight plus explicitly revealed36002/36007 challenger and46003 defender. Candidate11/11 and parent11/11 survive1300; zero invalid commands. Candidate original8 kill points4371 vs champion3186; all11 5887 vs4266. All11 improve points individually. Scores are against the fixed background, not a three-agent win-rate tournament. Remaining station health is often lower than champion, so higher score is not a safety proof.

| Episode | Candidate rounds | Candidate points | Champion points | Candidate final base HP |
|---|---:|---:|---:|---:|
| 22000 challenger | 1300 | 573 | 415 | 580 |
| 22000 defender | 1300 | 575 | 459 | 1185 |
| 22001 challenger | 1300 | 595 | 418 | 1500 |
| 22001 defender | 1300 | 555 | 412 | 1500 |
| 22002 challenger | 1300 | 592 | 408 | 1380 |
| 22002 defender | 1300 | 518 | 331 | 1330 |
| 26006 challenger | 1300 | 510 | 397 | 960 |
| 26006 defender | 1300 | 453 | 346 | 3000 |
| 36002 challenger | 1300 | 441 | 345 | 3000 |
| 36007 challenger | 1300 | 531 | 346 | 3000 |
| 46003 defender | 1300 | 544 | 389 | 1500 |

## Regression and review
29 tests pass:24 inherited economy/field/joint-fire/combination tests plus5 causal priority regressions:100 cash funds front upgrade,150 still front if none upgraded, emergency station remains first, one upgraded rail permits rocket3, all upgraded rails permits rocket3. Beta independently reviewed emergency priority, current inventory, capacity, shared cash and return-time guards: no new bypass. Existing possible full-bag shopping walk was not changed.

Reproduce with PYTHONPATH=CoreGeek/src:. python3 -m lab.survival.iteration07.alpha.develop (candidate) or .baseline (champion). diagnose.py imports frozen iteration06; diagnose_fixed.py imports current frozen candidate. JSON preserved. Root must independently qualify exact hashes before publication; no official100% claim.
