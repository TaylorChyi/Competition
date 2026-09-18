# Gamma first candidate

Scope: copied self-contained agent package, modified only economy.py. Default decide(observation), no external state or configuration. All targetTeam filtering remains unchanged.

## Strategy
- Add legal LargeRobotSummonOrder purchase/use. Large has 500 HP per 100 coins (5 HP/coin), Boss 800/200 (4); this is pressure-efficiency reasoning, not proof of win value.
- Require three surviving towers, station at least 85% health, one carried order maximum. First three days allow a 100-coin pressure purchase before optional upgrades; later require every tower level >=2 and 25 coins remaining. Buy only before day phase55.
- Only the pioneer uses orders, at phases6,12,...60. Ten possible commands per day establish the official ten-use cap with no memory dependence. Existing medicine priority remains above summons. Injured-base upgrade handling remains unchanged.

## Development evidence (bounded simulator, not official judge)
- Seeds restricted to22001/22002; heavy waves, 10 nights, commerce enabled.
- dev-first.json predates arena consumable extension: nearest22001 both survive10, no summons, Gamma invalid0.
- dev-attack.json: old conservative threshold never summons. nearest22001 both survive10; advance22002 Gamma dies494 (3 completed nights), baseline999 (7 completed). This exposes baseline position/economy sensitivity; not fixed by claims about offense.
- dev-pressure.json: 125-coin minimum never triggers because upgrade shopping spends at100.
- dev-pressure-final.json (current candidate): nearest22001 legal Large summoned at round167 for night2; invalid0. Both survive10. Gamma endingHP4485/income684; opponentHP4500/income574. More opponent repairs are observable but not a demonstrated win. No win-rate claim.
- Python compileall completed for candidate.

## Opponent weaknesses / limitations
- Baseline spends at100; reserve125 makes attacks dead code in low-income openings. Attack competes directly with first tower upgrade and must be evaluated, not assumed beneficial.
- Alpha's observed first draft buys station voucher early and delays use until <=40%HP: capital tied up, but substantial healing reserve means single-Large pressure is unlikely decisive. Need concentrated damage or sustained waves; base-heal reserve is a genuine counter.
- Beta had no brain difference at first audit; await frozen cross-play candidate instead of inferring unfinished strategy.
- advance22002 survives only three nights on Gamma's inherited defense. Do not select this candidate as universal survivor without improvement/cross-play.
- Task reward/news/official wave behavior still absent or hypothetical in shared arena; no official100% guarantee.

## Round 2 final candidate (ready to freeze)
- Round1 runtime Python saved in round1/ before editing.
- Direct peer audit exchanged with Alpha and Beta. Both correctly identified early Large consuming first repair fund. Gamma identified fixed low-health thresholds starting travel too late; Beta confirmed splitting return and use thresholds.
- First base voucher is now purchased before optional weapon upgrades. A carried voucher returns toward base at night regardless of health; use threshold is max(600*level, (distance+4)*visible incoming DPS within6).
- Large removed from purchases. Small20 pressure, Middle30 only if an observed enemy base has <900HP. Attack requires first base upgrade already purchased/carried or applied (base>=2), base>=65% maxHP, three towers, real available wallet. Purchase only phases48..50 and no carried order: at most one purchase/day. Use remains fixed ten legal daytime slots.
- Experimental broader purchase windows sent25 Small and sometimes reduced own survival to6 nights; rejected. First repair requirement preserved, but no25 spare-cash requirement once first repair is funded, because that made all advance attacks unreachable.

Opponent provenance: runtime .py copied once from peers' then-current working directories into gamma/opponents/alpha and gamma/opponents/beta before four-game runner. These are local preserved snapshots from peers mid-iteration, not peer final freeze and not official win-rate evaluation. check_round2.py records only developer seeds. Main's later same-arena swapped-side frozen evaluation is authoritative. Arena was maintained concurrently by main; the runner is exploratory evidence and its exact arena revision is not frozen here.

Final dev-round2.json (Gamma always challenger; score=killPoints+sum(10*day for survived nights), task points omitted):

| Opponent snapshot | seed / priority | Gamma score | Opponent score | Gamma / opponent death round | Summons | Result |
|---|---|---:|---:|---|---:|---|
| Alpha |22001 nearest|963|863|alive1300 / alive1300|3 Small|win|
| Alpha |22002 advance|156|91|482 /386|1 Small at315|win|
| Beta |22001 nearest|890|878|alive1300 / alive1300|4 Small+2 Middle|win|
| Beta |22002 advance|152|519|484 /989|1 Small at315|loss|

All four Gamma runs invalidCommands=0. Both requested seeds have actual summons. The20-coin attack did not fix Gamma's advance survival: approximately3 completed nights, with death earlier than the no-summon intermediate482/484 vs490/509. Large100 was not adopted because it consumed upgrade budget; cheap pressure remains a tradeoff, not a universal improvement. Three of four unpaired development wins are not a general win-rate claim; shared-map, spawn randomness and peer snapshot changes confound causal attribution. Gamma ready for main frozen swapped-side tournament; no more runtime edits planned.

## Round 3 final (ready)

Main's authoritative results supersede developer scores: round1 Large candidate0W6L; round2 low-price candidate4W8L,64 actual summons, only9/24 ten-night survival observations versus baseline12/24 and Beta12/24. This disproves the broad offensive allocation. It is not hidden by the earlier exploratory3/4 wins.

Saved prior runtime .py into round2/. The reused developer runner accidentally overwrote the full-detail dev-round2.json; its recorded score/death/summon summary is preserved from terminal output and NOTES in round2/summary.json, and the new detail file is explicitly dev-round3.json. Main's frozen official results are unaffected.

Final changes:
- No normal Small purchases. Buy Middle only if a visible enemy base is level3 and health<900, meaning no further upgrade heal remains. Our base must be>=80%HP, three towers each>=level2, next repair already held or base maxed, and real budget must cover order plus150 reserve. No observed eligible situation occurred in developer matches:0 summons. This is deliberately effectively defensive in ordinary states.
- Hold existing orders until final10 daytime slots and enemy remains visibly level3/<900. One pioneer caps10 uses/day; inventory and narrow purchase window remain constrained.
- Restrict reactive repair threat to attackers within3 cells, not6, and use threshold max(600*level,4*visibleDPS). Existing night-voucher return rule retained.
- Full inventory now prevents both Medicine purchase and urgent_refit. Medicine budget additionally reserves the actual next Station voucher100/150 unless already carried, preventing a10-coin medicine from consuming the final repair budget.

Developer checks against the same preserved mid-round2 opponent snapshots, not new peer finals:

| Opponent | seed / priority | Gamma / opponent score | Gamma / opponent survival round | Result |
|---|---|---|---|---|
| Alpha snapshot |22001 nearest|959 /851|1300 /1300|win|
| Alpha snapshot |22002 advance|159 /309|490 /757|loss|
| Beta snapshot |22001 nearest|950 /840|1300 /1300|win|
| Beta snapshot |22002 advance|160 /140|509 /477|win|

All Gamma invalidCommands0, summons0. Adding the funded-repair Medicine reserve left these four developer outcomes unchanged. Full-bag synthetic check with500 real observation gold,50HP pioneer and40 iron: urgent_refit false, develop emits no buy; PASS. This validates inventory guards, not official deployment. Advance survival remains approximately3 nights; carrying copper through congestion and second-voucher income are unresolved shared weaknesses. No universal-win claim. Candidate runtime frozen for root's third unified tournament and independent holdout; peer development snapshots are not formal standings.
