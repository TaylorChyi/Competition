# Round04 Alpha — retain Gamma champion after medical experiments

Final nine runtime files are byte-identical to the inherited Round03 Gamma champion, including its side/rear tower layout. No Round03 Alpha repair/sale delta was added. No Round04 retained seeds were inspected.

## Hypothesis and safety design

The current parent can leave a125HP worker untreated because proactive shop trips require below50HP, nearby purchases generally require below100HP, and a healthy station's future voucher reserves100/150 gold. Medicine costs10 and restores full health per task specification. Tested a daytime injured-operator policy, not a new HP assumption:
- Treat only below65% of the role's actual200/220HP capacity; never newly stock medicine for healthy roles.
- Require real shared cash after issued purchases/builds and backpack space. A base below75% of its current maximum retains its next voucher cost unless that voucher is already carried.
- Require shop travel, buy/use action margin, and return before darkness. Variant2/3 also check return to the furthest reachable current gun, not just the base anchor, and bank inventory if already adjacent to a vendor before a critical medical trip.
- Night purchases and medicine-plus-shooting remain prohibited. Existing emergency-base-voucher priority is preserved.

Eight new branch regressions passed along with all eighteen inherited regressions (26 total) on the final medical prototype before it was rejected. They cover125HP treatment with only10 real cash, subsequent use, urgent100/150 base reserves, no future ore cash, healthy/no-night/full-bag gates, medical priority before optional stone maintenance, vendor-first cash, excessive detours, and rear-tower timing.

## Three bounded variants and paired development

Fixed adversary: inherited Round03 Gamma. Only22001 field-operators and22002 field-advance, commerce, ten nights, both seats. Each prototype had zero illegal commands in four halves.

| Medical prototype | Operators candidate / parent paired score | Advance paired score | Decision |
|---|---|---|---|
| V1 proactive daylight trips for every eligible injured role |1877 /1960|452 /452|Reject|
| V2 noncritical shop route at most6 steps, vendor/actual-gun return safeguards |1883 /1960|452 /452|Reject|
| V3 noncritical treatment only when already next to shop; below50HP may travel |1934 /1949|452 /452|Reject|

All operators halves survive ten nights. Advance outcomes are identical side mirrors: strong seat756 rounds and336 score, weak seat350 rounds and116 score. Therefore none improved ten-night advance survival. V3 reduces V1/V2's operators regression but still loses the paired fixture. No fourth threshold was tried.

These are combined policy prototypes: relative to the parent, both low-health routing and healthy-role medicine stocking changed. The data do not isolate a universal causal claim that medicine or every detour is bad. They only fail to support promoting these tested variants over the current champion. Formal new-seed results may differ, but the incumbent is the evidence-backed conservative final choice.

Raw records: medical-broad.json, medical-nearby.json, medical-opportunity.json. Rejected economy implementations and common brain are in variants/. Medical-only regression source is retained as variants/medical_regressions.py.txt for running against an isolated restored prototype; it is not a shipped runtime or an incumbent test. No inherited regression was removed. Development harness currently imports the final restored incumbent; historical JSON refers to the named rejected prototype.

## Peer audit

Gamma pointed out selling seven copper beside the vendor can be more urgent than starting another medical trip and that returning to the anchor is not necessarily returning to a rear gun. Adopted both as prototype safety constraints. Alpha reminded Beta that a role busy using medicine/voucher must remain physically blocking while excluded from active joint relocation and gun assignment.

## Final verification

All nine runtime modules match inherited Round03 Gamma byte-for-byte. All eighteen incumbent field/economy regression methods pass. Ready/frozen. No claim of stronger win rate,100%, or formal-match medical validation.

## Reopened fire-control candidate — supersedes incumbent freeze above

Root reopened Alpha because Gamma already represents the exact incumbent. Medical variants remain rejected. Final runtime differs only in brain.py and fire_control.py; economy and all inherited field fixes remain unchanged.

Concrete counterexample: ready level-1 railguns A=(5,6), B=(1,6), 10HP incoming X=(6,6), Y=(8,12), base=(5,5). Original order assigns A to X and leaves B idle. B→X, A→Y legally kills both. Ray interception continues using all observed robots and their original health, including other-team blockers; damage reservation cannot erase an intervening body.

Final V2 enumerates at most six orders of the at most three ready, adjacent, unoccupied railguns after inherited guard/use/cooldown checks. Each alternative copies reservations; only the chosen result is committed. Every incoming robot contributes capped total predicted damage and a single kill bonus. Original order wins ties. An alternative must additionally preserve total effective damage and strictly increase total kills over original order, as well as improve threat utility. This is predicted simultaneous damage under the inherited ray model, not a claim of authoritative target-lock. More than three guns safely falls back to original greedy order. Controller IDs remain paired with their own eligible actors.

Two bounded fire variants, development only, field waves ten nights against frozen Round03 Gamma:

| Variant | 22001 operators paired scores (Alpha:parent) | 22002 advance paired scores |
|---|---:|---:|
| V1 unrestricted higher threat utility, rejected | 1966:2008 | 458:452 |
| V2 damage nondecrease + strictly more kills, selected | 1995:1933 | 452:452 |

V2 individual halves: operators 1017:949 and 978:984, all sides survived1300 rounds; advance336:116 and116:336, strong side756 rounds and weak side350 on both policies. All four halves zero illegal commands. Alpha p95 decision latency11.086/8.561/4.545/2.279ms versus parent's2.420/2.595/1.900/2.119ms. This is one paired operators gain and an advance tie, not statistical proof or full-night survival improvement. No290xx data read.

Artifacts: joint-fire.json (V1), joint-fire-conservative.json (V2), variants/joint_v1_fire_control.py. The development harness now runs final V2. Four new causal tests cover the constrained gun opportunity, original-health blocker, one-gun equivalence, and equal-result original-order preservation; with inherited economy/field regressions,22 tests pass. Beta independently checked six allocation/blocker/busy/cooldown/reservation cases with no blocking defect, and measured200-robot synthetic stress around116ms (not official latency acceptance).

Final V2 ready/frozen after regression. Root owns formal matches and publication; no100% claim.
