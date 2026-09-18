# R5 Beta frozen: economy + full escape

Inherited exact R4 Gamma (PARENT.json). Explicitly copied Gamma's two deletions of the level1 slightly-damaged-base forced upgrade rule; retained75% emergency priority and immediate carried-voucher use. Explicitly combined R4 Beta joint vacating chains / anticipatory escape / continued off-gun self-rescue. Runtime changes: economy.py, brain.py, guard.py. Champion tower layout remains. No reserved30000–30009 use.

## Incremental development evidence

Field10nights, commerce; each row summarizes two swapped halves. Opponent names refer to frozen R4 Gamma or local economy_only snapshot (the same two deletions, no escape enhancement). Positive point difference favors candidate. Survival takes precedence over points; this table is not an official win-rate table.

|candidate / opponent|22001 operators paired point diff|22002 advance paired point diff|26006 nearest paired point diff|
|---|---:|---:|---:|
|economy only / R4Gamma|-37|0|0|
|full combination / R4Gamma|-83|0|+223|
|full combination / economy only|-32|0|+223|
|rejected75% stoploss / R4Gamma|-84|0|+162|
|rejected75% stoploss / economy only|-33|0|+162|

Raw results: development.jsonl18 halves, development-stoploss.jsonl12 halves. All30 invalidCommands zero. Opponent trajectories can change because resource economy is shared; direct comparisons are provided instead of pretending cross-run comparisons isolate every mechanism.

### Clear benefit and cost

Nearest26006 right: economy-only base dies629,5 operator deaths,563 shots. Full combination survives1300,0 deaths,1450 shots, including against economy-only. Left full combination survives1300 and fires1211 shots. This is the principal verified benefit.

Operators22001 right versus R4Gamma: economy-only survives1300,2 deaths,1292 shots, base upgrade809. Full combination dies1273,3 deaths,1189 shots, base upgrade840. This is a real regression, not a universally improved candidate. Against economy-only both full-combination seats survive1300 but lose paired points32; right4 deaths and1222 shots.

Advance22002 unchanged: candidate left756 vs350, right350 vs756, regardless of additions. Escape does not solve this failure mode.

## Only additional stoploss tested, rejected

When base HP<75% maximum, disable new joint shifts / anticipatory off-gun escape, preserving original best-effort imminent-death escape and continued retreat for already-displaced roles. This reused existing economic threshold; no new fitted number.

It did not rescue operators right (still1273 death,1185 shots). It worsened nearest right from0 to3 deaths and1450 to1189 shots, paired-point gain223 to162. Rejected and restored full_escape snapshot. Rejected runtime preserved in stoploss/; its deterministic check now explicitly tests that snapshot. No further tuning.

## Validation and limitations

15 public field-defense regressions pass with default package aliased as agent. check_retreat.py/check_joint.py pass: vacating-chain collision legality, healthy shooters retained, busy-role obstacle, continued retreat, danger-cleared return. check_stoploss.py verifies rejected experiment's strict75% boundary and preservation of imminent-death fallback.

Incoming-only danger and targeting remain. Exposure sums possible attacks rather than known target locks; advance robots may ignore operators. Thus retreat can sacrifice useful fire, and shared economy/role travel can delay base upgrades. Official exact robot movement/attack timing remains unproven. No claim of full survival or100% wins. Full combination is a falsifiable tradeoff candidate selected over the worse stoploss variant, not declared better than champion across all modes.
