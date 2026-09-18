# Round 01 Alpha — cash flow and shared mining

Inherited all nine base modules and retained the field delivery, emergency-voucher, collision reroute, night shopping, operator-exclusion and survival fixes. Runtime changes are confined to economy.py.

## Two bounded changes

1. Workers already adjacent to a deposit may both collect, including the shared final extraction, as supported by the documented simultaneous-mining rule. Distant workers still reserve travel destinations rather than piling onto an occupied mine.
2. When not adjacent to ore, low-value inventory alone triggers a sale only at value `max(15, 2 × vendor travel distance)`. This avoids long trips just to sell three copper. Existing immediate sale cases remain: already at vendor, value >=50, upgrade cash unlock, full backpack, or approaching sunset. The distance estimate is a lower bound; it does not claim precise realized trip profitability.

## Development evidence, not tournament results

Fixed opponent is tournament/base. Authorized development seeds, Alpha in challenger seat:
- 22001 field-nearest: both survive ten nights; Alpha score 974 vs 957, income 728 vs 584, zero illegal commands.
- 22002 field-advance: Alpha score 418 vs 114, survives 852 vs 351 rounds, income 601 vs 220, zero illegal commands. Alpha still fails ten-night survival.

These are two diagnostic halves, not swapped fixtures or a 100% claim. Full results are DEVELOPMENT.json. Fair formal ten-fixture matches remain the root owner's responsibility.

Two focused economy regressions plus all sixteen inherited field-economy regression methods pass against this candidate. The copied regression file changes only its import target. No regression was removed.

## Peer review

Sent Beta a concrete risk: applying kill-point rewards to partial damage can overweight a high-HP boss instead of a nearby lethal small attacker; test that corner before treating it as immediate score. Sent Gamma a counterexample: base-focused fire at low HP must not sacrifice the final operator, or all guns lose control. Gamma notes that excessive second station-voucher spending can delay damage upgrades; Alpha does not add such pre-purchasing.

Known limitations: shared extraction can make deposits respawn farther away; vendor distance is geometric rather than a route cost; a short development advantage is not stable match superiority. No seed, opponent identity, or hidden simulator-priority branches exist.
