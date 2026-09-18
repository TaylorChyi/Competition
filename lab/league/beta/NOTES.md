# Beta first candidate — development evidence only

Scope: weapon mix, target allocation and ten-night survival. All runs use only development seeds 22001/22002, heavy waves, nearest/advance priority, commerce enabled, ten nights. These are local model results, not official win-rate evidence. No holdout inspected.

## Changes

- Rocket splash coverage retains every robot at a position instead of silently replacing earlier robots with the last one. Target generation remains restricted to incoming robots through `targetTeam` filtering.
- When buying weapon vouchers for a rocket, purchase one at a time, allowing the existing rocket-first application and level-two-first upgrade ordering to complete its range upgrade before funding all other towers.
- Default remains three railguns, four screening walls. The tests do **not** justify replacing it with rockets or gatlings for an unknown opponent. No free heals, free weapons or external policy/configuration added.

## Measured development results

22001 / heavy / nearest (challenger side, versus original default):

| Loadout | Nights alive | Final base HP |
|---|---:|---:|
| 3 railgun | 10 | 2565 |
| rocket + 2 railgun | 8 | 0 |
| 2 rocket + railgun | 5 | 0 |
| 3 rocket | 5 | 0 |
| gatling + 2 railgun | 10 | 3000 |
| 2 gatling + railgun | 10 | 2735 |
| 3 gatling | 10 | 4195 |

The gatling + 2 railgun case reached ten nights with one station upgrade, but did worse against advance. Three gatlings required two station upgrades and are not a reliable winner.

22002 / heavy / advance:

- Three railguns with no walls: four nights; 8/12 walls: three nights.
- Gatling + 2 railgun with default walls: three nights.
- Two or three gatlings with default walls: one night.
- Focused rocket purchasing + rocket/railgun/railgun + no walls: two nights.

## Failures and limitations

Advance defeats every tested configuration. Economic throughput, delayed upgrades and loss of operators remain the bottlenecks. All experiments were started before confirmation of the parent arena resource-claim fix; exact results must be regenerated against its final rule revision. These runs compare one side and do not establish wins after side swaps or survive adversarial summons. Raw metrics and scripts are retained in this directory under `development-*` and `develop*.py`.

## Opponent attack ideas for mutual review

- Early summons timed before the opponent buys/applies its first voucher exploit railgun low initial DPS and low-level rocket cooldown.
- Advance targeting bypasses the nearest-defense strategy's screen and forces station voucher spending, delaying weapon upgrades.
- A gatling-heavy rival has a large approach blind zone; dispersed ranged robots and attacks outside level-one range undermine its apparent nearest-wave success.
- An all-rocket rival can be pressured in the three-round cooldown gap and by separating incoming robots to deny splash value.
- Shared deposit contests and shop-route congestion can delay global-range rocket upgrades; evaluate only with the corrected simultaneous resource allocation.

# Round 2 candidate (current default)

Round-one Python snapshot: `round1/`. Final implementation changes are in `economy.py`; default remains 3 railguns / 4 walls.

- Adapted Alpha's delayed station voucher consumption: save the finite full-heal until <=40% station health.
- Separated the return and consumption thresholds: at night, a courier with a station voucher returns next to the station even when it is too healthy to consume the voucher. Daytime keeps the existing mining/shopping and sunset-return behavior.
- Opportunistically buy one Medicine when already beside the shop, backpack has room, and the actual wallet still retains 100 gold after purchase. Existing use-at-65%-health consumes it. No detour for healthy roles and no invented income.
- Rejected unconditional station pre-purchase: it delayed weapon investment and lost nearest-wave survival. Rejected all-day voucher guarding: it idled the courier for entire days.

## Final matched development comparison

All below use corrected arena, baseline round-one opponent, challenger seat, heavy / commerce / ten nights, only allowed development seeds. No holdout. Final raw data: `development-round2c.jsonl`; action traces: `development-round2c-actions.jsonl`.

| Seed / target policy | Round1 nights / rounds | Round2 nights / rounds | Kill points before → after |
|---|---|---|---|
| 22001 nearest | 10 / 1300 | 10 / 1300 | 424 → 441 |
| 22001 advance | 4 / 636 | 5 / 730 | 145 → 157 |
| 22002 nearest | 10 / 1300 | 10 / 1300 | 414 → 402 |
| 22002 advance | 3 / 494 | 3 / 494 | 94 → 94 |

All eight runs have zero invalid commands. 22001 advance actually delays station upgrade uses from turns 182/333 to 230/422, gaining 94 survival turns. 22002 nearest actually buys two Medicine and uses one. 22001 nearest has all three operators alive at every night end (round1 lost operators on nights 3 and 7). Medicine buying in 22001 advance occurred but it was not consumed, so no medicine benefit is claimed there.

Nearest final base HP is lower (22001: 2565→1345; 22002:3000→700), with an unused station voucher held rather than spent. No HP-based score advantage is claimed. The official scoring excerpt uses survival and robot kill points, not base HP. 22002 nearest loses 12 kill points: the candidate is not uniformly superior and requires round-robin evaluation.

## Mutual audit sent directly

Alpha: 40% threshold applied before return can strand a courier at the distant shop until too late. Example: station601→590HP triggers a 20-step return while40DPS destroys the base in15 steps. Separate approach from use thresholds.

Gamma: early first-three-day LargeRobotSummonOrder priority can spend the first100 gold on offense while all towers remain level1, sacrificing the first defensive voucher. A summon-pressure opponent can force its own advance-wave collapse. Recommend preserving the full urgent voucher price before offense. Current Beta incoming filtering already includes opposing summoned robots through their observed targetTeam; delayed station heals are a defensive countermeasure but have not yet been validated against Gamma's final summons.

# Round 3 final candidate — frozen

Round-two running package snapshot is `round2/`. Final running default is trial3c (original worker order); runtime imports only the package's normal relative modules. No seed, priority, opponent name or external configuration branches were introduced.

## Final changes

1. Station voucher consumption forecasts nearby incoming robots: sum their documented attack power within four cells of the station footprint, then heal when health is at most `max(200 × station level, 3 × observed nearby attack power)`. This preserves three turns of observed pressure as a margin while avoiding the old fixed40% consumption on a lightly pressured base. Only incoming targetTeam robots count. Returning home at night remains separate from consuming the voucher.
2. Opportunistic Medicine purchase preserves the actual next station voucher price (100 or150) when the station is damaged, instead of always reserving100.
3. urgent_refit only spends actual observed gold, never treats workers' unsold ore as ready cash.
4. Medicine purchasing and urgent_refit return to normal logic on a full backpack. In-memory full-backpack check confirms no purchase and no urgent_refit command.

## Diagnosis and rejected variants

The22002advance losses primarily lacked the second station voucher: income was insufficient, and a worker could still carry50 gold of copper at sunset. At round450 on the other seat, a healthy pioneer held an unused Medicine after spending10 gold while the150-gold voucher was unfunded. Fixed40% was therefore not the sole cause.

- 3a: economy guards plus always processing high-value backpacks first. Some advance outcomes regressed.
- 3b: added forecast-based healing. Some22002advance outcomes improved, but nearest versus baseline lost both seats on both development seeds (kill-point differences−19/−14 and−27/−11). Rejected because it sacrificed established nearest wins.
- 3c: removed worker reordering, retained economy guards and forecast healing. Selected.
- 3d: reorder workers only when a distressed base's next voucher can be funded by carried ore. Did not improve the target cases; rejected to keep the implementation smaller.

## Final3c fixed-opponent matched evidence

Opponents are frozen baseline and Alpha round2. All runs ten nights/heavy/commerce, only22001/22002. No holdout read. Side0 is challenger; side1 is defender.

| Seed / profile / opponent | Challenger survival beta:opponent | Defender survival beta:opponent |
|---|---|---|
|22001 nearest baseline|1300:1300|1300:1300|
|22002 nearest baseline|1300:1300|1300:1300|
|22001 advance baseline|869:499|509:376|
|22002 advance baseline|498:999|501:626|
|22002 advance Alpha round2|497:757|501:494|

Nearest score differences are+17/−14 on22001 and+32/−11 on22002, retaining both paired wins and ten-night survival. The22001advance matchup wins both seats. Against baseline on22002, round2 Beta survival494/477 becomes498/501; against Alpha,490/486 becomes497/501. These are modest survival improvements, not a resolution of the losing paired fixtures.

All ten final3c half-games have zero Beta invalid commands. Raw final evidence is `development-round3c.jsonl` plus only the3c rows of `development-round3-regression.jsonl`. Failed variants and diagnostic role/command traces remain in their separately named development files. No100% claim is supported; the final uniform tournament determines selection.
