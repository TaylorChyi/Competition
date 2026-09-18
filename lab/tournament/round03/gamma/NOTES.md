# Gamma round03 — two forward guns, one side-rear gun

Inherited exact Alpha round02 winner. Final change only `_tower_sites` in brain.py. Keep the first two original spaced forward gun positions. For the third, consider legal ring1 cells at least2 Chebyshev cells from both; take the second-farthest from map center (fallback to available last candidate). This moves the gun off the three-exposed-front arrangement, but one cell forward from the maximally rear corner to retain earlier firing coverage. No future robots, seed, arena internals, wall shielding, or economic changes.

Field layout examples from observed bases:
- challenger: (11,20),(11,22),(8,22)
- defender: (29,11),(29,9),(32,9)
These are geometric mirrors. Both fit ring1 around documented2x2 base. Static check including inherited four planned front walls found3 distinct reachable free adjacent operating cells. Every map cell within distance3 of any base footprint cell is within range6 of all3 guns. These are geometric properties, not guarantees that dynamic occupation or actual robot priority preserves operators.

## Two focused variants, same6 development halves

Only developer seeds22001 nearest/operators and22002 advance, each swapped sides vs frozen round02 Alpha winner. Ten nights, commerce. Root's reserved28000–28009 unseen.

1. Maximally rear corner: source saved attempts/rear_brain.py, details rear-development.json. nearest pair1942:1955 loss, operators1942:1955 loss, advance360:272 win. Excellent strong-side operator retention (all3 through10 nights) but early coverage loss/weak-side kill score made it unbalanced. Not final.
2. Final side-rear cell: side-development.json. nearest1928:1917 win, operators1928:1928 tie, advance452:452 tie. Each comparison has one half win/one half loss, so totals decide. Three fixtures1W2D0L, six halves3W0D3L. All invalid0; both candidates second-night survival6/6. Four nearest/operators halves survive10 nights. Advance Gamma survives756(left)/350(right), opponent351(right)/757(left): still unresolved side-dependent weakness, not a universal improvement.

Final individual score pairs: nearest1002:943 and926:974; operators1002:954 and926:974; advance336:115 and116:337. Operator series and shot/income evidence saved. Final nearest strong side loses operators late (night8 only1), unlike maximally rear corner; the extra reach has a genuine protection cost. Candidate chosen for no paired developer loss across the three distinct profiles, not for claiming formal win rate. Formal root10-group round may reverse this small-sample result.

## Peer adversarial exchange

Beta reminded that three individually controllable guns can share the same only-safe cell; static distinct-cell feasibility was checked with planned walls. Gamma warned its joint repositioning may move the only ready shooter away from a base-saving shot while assigning the saved operator to a cooling/no-target gun; joint scoring must preserve real executable fire, not only health.

Alpha adjusted repair-voucher travel estimates through actual shop and chosen gun-neighbor cell after Gamma warned base arrival does not guarantee rear gun operation. Its warning about rear choke occupancy and shot loss is reflected in recorded shot/operator series. Existing base voucher immediate-use and incoming filtering retained.

READY/FROZEN. No changes to round01/round02 or public judge/tests. Official100% is not claimed; only finite root-recorded20/20 could meet the requested observed target.
