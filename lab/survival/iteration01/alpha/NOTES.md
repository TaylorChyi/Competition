# Survival iteration01 Alpha — first-gun research candidate

READY / frozen for root combination only. NOT PASSED:4/6 ten-night self-survivals. No peer ranking or tournament win-rate comparison. Root owns production, packaging and release under AGENTS.md; this isolated experimental package is not a release.

## Rules and diagnosis

Read docs/任务书.md sections4.5 and weapon mechanics: gatling10 damage per bullet with level1/2/3 bullets, range3/5/7, pairwise directions<=90 degrees; railgun energy10/20/30, range6/8/10, original-health ray penetration; rocket20 center/10 splash and three-turn cooldown. All use observed target information only. User confirmed robots move OR attack each turn. Shared judge frozen SHA91691bc4fee6b6905709e8f57ef6c44876a43fda56700acff40c9a8f85ede231; no modifications here. Wave population/type proportions beyond user's partial report remain synthetic assumptions.

Baseline advance defender: before third night, round330, all three operators full HP and all three level1 guns1000HP, station1400HP(level2), cash112. Only upgrade was station2 at194. Policy refuses100 gun voucher while waiting for150 station voucher. Dies350 with112 unspent. This is not primarily operator death. Challenger first gun upgrade only581, after station upgrades189/458; dies756. Third stress wave has3380 total HP; three level1 guns at perfect60-round availability can deal at most1800 damage. That does not prove survival impossible (robots can be delayed), but explains why same-DPS substitutions alone do not resolve sustained deficit.

## Exactly two variants

1. Front first gun Gatling, other two railguns, unchanged economy. Local two10HP noncollinear targets in90-degree cone prove level2 Gatling can kill2 where one railgun kills1. Against full-health targets same total damage but much shorter range. Rejected: advance survival736/338 versus baseline756/350, and no increase in ten-night passes. Preserved brain in rejected/front_gatling_brain.py, full results front-gatling.json.
2. Restore all three railguns. economy.develop may skip an unaffordable StationUpgradeVoucher2 only when base is level2 and at least25% of its maximum HP, all standing guns level1, no carried matching station/first-gun voucher, no same-turn station purchase, and real remaining shared cash can pay100 first-gun voucher but not150 station voucher. Existing fullbag/daylight/route/cash checks remain. If station upgrade is affordable, it remains first. Critical lower-health station retains reserve. No future ore value is spendable. Threshold is a declared heuristic, not verified time-to-death.

## Own survival only, fixed R5 Alpha opponent

Each case uses field waves10 nights, commerce, both seats. No score-based selection.

| seed / mode | baseline challenger/defender rounds | front Gatling | selected first-gun fallback |
|---|---:|---:|---:|
|22000 nearest|1300/1300|1300/1300|1300/1300|
|22001 operators|1300/1300|1300/1300|1300/1300|
|22002 advance|756/350|736/338|894/354|

All18 policy-halves produced zero invalid commands. All variants remain4/6 ten-night; no100% claim. Fallback other four halves have exactly baseline nightHP, while advance weak side improves just4 rounds. Strong side first gun upgrade581→442, but station3 delays458→584, leaving just345 baseHP after fourth night; later dies894. Weak side gun actually upgrades311,112cash→12, but still dies354. Thus this is a causal firepower improvement with substantial healing-timing risk, not a completed survival solution.

All baseline/variant JSON include own per-nightHP/equipment/operator counts/upgrades plus start/end-night snapshots of both teams' units, bags, cash, cumulative shots/income, and remaining incoming robots. Opponent stays fixed round05.alpha.brain.decide; no peer comparison. Baseline was rerun once after fixing audit-only backpack snapshots to copy lists; outcome was identical. Failed variant records remain intact. Current develop.py runs the selected fallback; historical variant files must be restored in an isolated package to reproduce older named variants.

## Regression and peer review

30 tests pass:24 inherited regressions plus2 Gatling mechanics tests and4 fallback cash/priority tests. Beta supplied short-range early-contact counterexample, supporting rejection of initial Gatling. Gamma identified the same112/150 budget lock and confirmed independent economy scope. Gamma transport edit audit: only .4*selling→selling, does not change return/purchase/stock safeguards. It fully weights geometric sell distance, not actual obstacle-aware route or complete home journey; adjacent non-stone mines still override the income score. No new safety defect identified. No peer changes merged.

Current nine runtime hashes: RUNTIME.json. Only economy.py differs from frozen R5 parent, recorded in PARENT.json. Retained independently for root to combine with transport research, explicitly below the10-night gate.
