# Field economy correction — Alpha

Source: copied the currently published `CoreGeek/src/agent` package into this isolated field candidate; only `economy.py` is changed. Frozen league candidates remain untouched. This work prioritizes a deliverable voucher and staffed night defenses over the league experiments' delayed-healing optimization.

## What is established and what is uncertain

- The user summary says team B bought StationUpgradeVoucher1 at round 161, transported it during 162–169 toward (30,11), and lost its base at round 249. It also says no use occurred, yet describes 1820 base HP during night two. These statements do not establish that the voucher was never used: a level-one base has a 1500 maximum, while level two has 3000. The summary is internally inconsistent without raw round observations/actions. We do not claim a reproduced missed-use incident.
- Original economy immediately uses adjacent station vouchers in daytime, but at night skips them while station health exceeds half maximum. Original urgent_refit can send a nearby pioneer toward the shop at night, and treats workers' unsold ore as available funds during daylight. Original injured-role medicine buying lacks a backpack-full check.
- Official interface says station size is 2×2 and `pos` is its top-left corner (接口文档 line 113): anchor (x,y), (x+1,y), (x,y-1), (x+1,y-1). Task specification gives station HP 1500/3000/4500, and says upgrades restore full HP and require use within one square of the building.
- Exact engine treatment of the entire footprint versus anchor distance is not proven by the available engine implementation. At the main owner's direction, this patch conservatively routes to distance ≤1 from the canonical anchor and passes that anchor as targetPos. Those positions are a known legal subset of surrounding-building positions; it may travel farther than necessary, but does not invent a wider use range. It never treats a station as 3×3.

## Chosen corrections

1. A carried station voucher returns to its matching station and is consumed as soon as the courier reaches the conservative valid range, during day or night and without waiting for a low-health threshold. This removes the need to predict incoming damage accurately, and immediately gains the next level's maximum HP. Medicine for an already injured operator still has priority.
2. No new shop purchase or shop trip begins at night. Both urgent_refit and regular develop share the same purchase-route admission check, so a regular courier or injured role cannot bypass the night/sunset restriction.
3. Shop admission requires an observed traversable route to the shop plus a traversable return route to the base, a purchase/use margin of three turns, and enough remaining daylight. This is a conservative current-observation check, not a future path guarantee; moving units can still obstruct later turns.
4. Spending uses current shared cash minus other already issued purchases and tower builds. Unsold ore is not cash. Full backpacks cannot buy medicine or a station voucher.
5. Medicine keeps the observed next station-voucher cost (including 150 gold at level two) when that voucher is not already carried. An operator below 50 HP is an explicit immediate-survival exception. Precautionary medicine is bought only while already beside the shop; it does not create a separate long procurement trip.

## Verification

`PYTHONPATH=CoreGeek/src:. python3 -m unittest discover -s tests -p test_field_economy.py -v`

All 11 deterministic regressions pass: transport from the reported (30,11) location followed by use, no night half-health delay, conservative 2×2 anchor use, no night urgent shopping, unsold-ore cash rejection, prior-build budget reservation, full backpacks, next-voucher medicine reserve, sunset urgent-trip rejection, ordinary develop sunset bypass rejection, and ordinary develop night purchase rejection.

These are focused behavior checks, not a replay of the official match or proof of second-night survival. The actual loss also involved dead operators and revival; operator control is being handled by the other owner and must be integrated before end-to-end acceptance.

## Narrow follow-up for review: medicine versus potentially lethal base damage

Reproduced before the change: night, base HP 40 at anchor (32,8), adjacent pioneer HP 100 at (31,9) carrying Medicine and StationUpgradeVoucher1, incoming boss at (32,5). `use_carried` issued Medicine first. The boss is within three cells of the base footprint and has 40 potential attack damage; if it attacks the base this round, medicine does not prevent the team's loss. The observed robot does not prove its target lock, so this is explicitly a potential-lethal-risk counterexample, not a guaranteed damage claim.

Only the medicine-first branch now checks this exception: nighttime; living non-max-level base; matching carried voucher; valid conservative anchor adjacency; no already-issued use at the same base; summed incoming robot potential damage within footprint distance three at least current base HP. It then uses the base voucher before medicine. All other medicine behavior is unchanged. Unknown robot types contribute zero rather than an invented attack value.

Three additional test methods cover the positive example and negative cases: nonlethal damage, distant robots, robots assigned to the opponent, invalid anchor range, wrong-level voucher, and an already-issued base upgrade. Total 14 tests pass. Only the Alpha owner copy and its regression file changed; the integrated candidate was not edited. This is ready for the main owner's decision before any next development build.

## Vendor-entry collision correction

The synthetic `field-failure-trace.json` supplied by the main owner reproduces worker 20010 at (19,14) repeatedly failing to enter (19,15). This is a locally generated diagnostic, not the official match replay. The default closest vendor service cell is itself the one-step goal; blocking that step makes a same-goal reroute impossible, and the old route function accepted the original colliding move without considering another service cell.

`economy.route` now obtains the ordinary route without grid's single-goal retry. When the actor has a failed prior action and the ordinary path is nonempty, it excludes that first step and searches across all legal service goals. Already-adjacent actors keep their empty route and can sell. If no alternative exists at all, the original valid path is retained rather than fabricating a move. The method uses only the current observation and failed-action IDs, with no seed switch or cross-match state.

Two added regressions cover a failed one-step vendor entry changing to another legal entry, then selling all seven copper, plus an already-adjacent worker preserving its sell location. All 16 regression methods pass. Read-only replay of trace observations now returns different entries: round 172 uses (18,15) then (19,16); rounds 180 and 185 use (20,15), rather than retrying (19,15). Whole-match improvement remains for the main owner's integrated development run.
