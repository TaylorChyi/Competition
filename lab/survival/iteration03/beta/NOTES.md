# Iteration03 Beta structural survival comparison

**Result provenance: see EVIDENCE_INDEX.md. `results.jsonl` is an interrupted old-exit prototype run, not the final19wall report. Use `default-results.jsonl`, `full_ring19-final-results.jsonl`, `opportunistic-results.jsonl`, and `exits-results.jsonl` for the four final rows of comparison.**

Recommended integrable candidate: **full_ring_exits/** (18 walls, two exits). The earlier19-wall full_ring is rejected for trapping some operators. Top-level9runtime remain the clean R5Alpha baseline for the control. Only full_ring_exits/brain.py differs from baseline. opportunistic/ is rejected. All simulations use nearest targeting, fixed R5Alpha other side, field10nights and commerce. No opponent scores or inter-agent ranking used.

## Final corrected candidate:18walls with two exits

19walls with only one exit statically trapped a single worker even without teammates: challenger station(9,22),worker(10,23); defender station(30,10),worker(30,8). The station and three guns divide the interior into separate pockets. Initial one-start path regression was insufficient. **Do not integrate the19wall candidate.**

full_ring_exits removes both opposite perimeter exit cells. check_all_exits.py enumerates every unoccupied inner-ring cell, places the sole actor there and proves a path to outside in both mirrors with all18walls and3guns present. This checks actual geometry, not just the presence of a missing wall. Temporary teammate congestion remains possible; no permanent structural enclosure is accepted.

|seed/seat|survival|first18wall round|first gun upgrade|total income|
|---|---:|---:|---:|---:|
|22000/0|1300|1094|304|403|
|22000/1|1300|434|192|416|
|22001/0|1300|297|432|359|
|22001/1|1300|1171|175|465|
|22002/0|1300|432|421|360|
|22002/1|1300|564|295|310|

All six corrected cases survive1300 with zero invalid commands and actually reach18live walls. Raw data including every night wallHP/count, role/baseHP, equipment, cash/income and wall labor: exits-results.jsonl. Income is no longer structurally trapped;22000challenger increases288→403 versus19walls while retaining survival. Root will run the8case gate and reserved validation; this six-case result alone is not release acceptance.

The runtime patch only changes fortify default4→19 (the actual legal target list has18cells), prioritizes missing perimeter walls, removes opening-distance/low-base-HP suppression for the assigned wall worker, and opens both exit cells. Existing3gun layout, economic rules, role return, target control and upgrade logic remain inherited.

## Earlier control and rejected-variant definitions

- Default: inherited4front walls, with distant-opening-stone and low-base-HP suppressions.
- Full ring: one dedicated worker expands19legal perimeter cells, missing cells before repairs, without those suppressions. Preserves day return and existing economy/upgrade priorities. The opening is mirrored for defender so the completed19walls and3guns do not trap the crew.
- Opportunistic: only place already-carried stone while adjacent to a front site; no dedicated stone journey or wall-maintenance trip. In these cases no such opportunity occurred, so it empirically means zero walls. This is documented rather than called a tested partial wall screen.

## Actual outcomes and timing

|structure|seed/seat|survival rounds|first19wall round|max walls|first gun upgrade|total income|wall builds|wall travel|stone travel|stone collections|
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|default|22000/0|1300|never|4|185|580|18|102|135|18|
|default|22000/1|1300|never|4|169|585|15|120|136|15|
|default|22001/0|1300|never|4|185|716|18|82|100|19|
|default|22001/1|1300|never|4|179|520|15|48|66|15|
|default|22002/0|1289|never|4|188|620|11|33|37|11|
|default|22002/1|1161|never|4|183|430|13|74|124|13|
|full_ring|22000/0|1300|1096|19|304|288|38|207|223|38|
|full_ring|22000/1|1300|438|19|192|477|34|172|153|36|
|full_ring|22001/0|1300|300|19|555|300|41|225|229|45|
|full_ring|22001/1|1300|1187|19|175|465|31|222|239|31|
|full_ring|22002/0|1300|434|19|421|205|38|238|200|38|
|full_ring|22002/1|1300|566|19|295|350|37|181|227|37|
|opportunistic|22000/0|376|never|0|181|208|0|0|0|0|
|opportunistic|22000/1|513|never|0|175|267|0|0|0|0|
|opportunistic|22001/0|1027|never|0|181|700|0|0|0|0|
|opportunistic|22001/1|754|never|0|172|310|0|0|0|0|
|opportunistic|22002/0|499|never|0|185|233|0|0|0|0|
|opportunistic|22002/1|623|never|0|187|335|0|0|0|0|

Ten-night survival: default4/6, full_ring6/6, opportunistic0/6. These are own survival counts, not win rates. Full ring is not validated on unseen cases yet; root runs the8development gate including26006 before reserved validation. No100% general claim.

## Formation and maintenance evidence

All six full-ring cases actually reached19simultaneous live walls, at300–1187. First-night wall counts are7/4/7/3/7/4; benefits start before a complete enclosure. Walls are destroyed/repaired later, so reaching19does not mean the ring remains complete permanently. Per-night wall count/HP, station and role HP, cash, gun levels/HP, cumulative income and labor are all in variants-results.jsonl.

Total income is lifetime-dependent and must not be interpreted as equal-duration earning efficiency when a candidate dies early. Wall labor counters are issued wall-build commands, moves from wall-placement helpers, dedicated stone-travel moves and all stone collect commands (the latter may include economic stone gathering). They are not an inferred idle-time count.

## Geometry correction and checks

Initial full-ring attempt exposed a real exit problem: inherited fixed right-upper entrance is disconnected from the defender lower interior by its station and gun placements once all19walls exist. Stopped that exploratory run; its partial rows remain in results.jsonl but are excluded from the final comparison. Final full_ring uses mirrored defender opening(28,11), challenger opening(12,20). check_structure.py checks19unique cells and actual path from inner operator to outside with3guns for both mirrors.

15public field-defense regressions pass with full_ring aliased as agent. All18final evaluation episodes have zero invalid commands. Full-ring local p95 decision15.2–55.0ms; no official timing guarantee.

## Interpretation and limitations

Under the user-confirmed nearest-unit/obstruction targeting, extra outer walls provide1000HP targets that attract nearby attacks. They are not modeled or described as projectile shields. No wall upgrades were introduced. Firepower-only opportunity walls produced slightly earlier first upgrades in some seats but all6bases died before10nights; a recommendation to drop walls is unsupported by this data.

Full-ring construction delays gun growth and spends substantial worker actions: e.g.22001challenger first gun upgrade185→555. It still survived these ten nights; this tradeoff may fail with different maps/pressure. Candidate must pass root broader gate before deployment acceptance.
