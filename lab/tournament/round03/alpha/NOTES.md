# Round03 Alpha — narrow repair and cash-unlock correctness candidate

Parent is the exact Round02 champion. Runtime changes only brain.py/economy.py. All eighteen inherited field/economy regression methods remain, plus four targeted methods. Twenty-two tests pass. No Round03 retained seeds were inspected.

## Two concrete changes

1. Before covering a damaged level-two gun with a new level-one gun, determine whether a matching level-three upgrade is already affordable from actual cash after reserved commands, a capable courier has backpack room, no urgent base refit takes priority, and current paths permit shop purchase plus delivery to the actual target gun before dusk. If so, preserve the gun and prioritize WeaponUpgradeVoucher2 purchase. Delivery checks the same health/type target ordering as carried-voucher use; a healthy target selected ahead of the damaged gun disables this plan. Missing funds, a critically injured/full courier, base emergency, inaccessible route, or insufficient time keeps the prior replacement fallback. Precautionary medicine cannot consume this repair budget.
2. After required initial tower building but before optional damaged-tower/wall maintenance, a worker already adjacent to the vendor can sell one ore batch if that single action closes the cash gap for the next needed upgrade. Base emergency remains first. No speculative sale income is spent before it is in the actual wallet, and no detour is added.

The first correction prevents a deterministic example: 125HP level-two railgun, 150 cash, healthy base, ready courier beside the shop, ample day time. The old policy overwrites the investment for25 and returns to level one; the new policy buys the150 level-three voucher and leaves the gun for full-health upgrading. The second regression covers seven copper beside the vendor plus65 cash funding a100 base voucher before optional wall work.

## Bounded development — no demonstrated matchup improvement

Combined candidate versus fixed Round02 Alpha, field ten-night games, both seats:
- 22001 operators: candidate974/957 scores, parent957/974; both ten nights. Paired total1931–1931 draws.
- 22002 advance: candidate159/112 scores, parent112/159; survival496/350 versus350/496. Paired total271–271 draws. Still fails ten nights.
- All four halves zero invalid actions. Raw combined.json.

Known published Round01 failure26007/operators against frozen Round01 Beta, both seats:
- Challenger:953 points,1300 rounds,income473 versus717/1251/446.
- Defender:708 points,1283 rounds,income508 versus915/1300/532.
- These results exactly match the recorded Round01 fixture. The sell-priority condition fired on four/two rounds, but ordinary processing already produced equivalent outcomes. The affordable repair condition never fired. Raw known_failure.json records trigger rounds.

This is an important negative result: the documented125HP level-two gun downgrade was not prevented because the actual state lacked enough timely cash for the more expensive upgrade. A deterministic correctness improvement is not evidence of a stronger match policy. No parameter sweep or speculative cash-based waiting was added to manufacture a gain. No rejected third variant exists; the one combined bounded hypothesis was assessed honestly.

## Peer audit

Gamma's rear-gun layout prompted an additional exact target-delivery check: merely arriving at the station is not equivalent to reaching the gun before night. Alpha warned Gamma that rear geometry can create joint-standing congestion and needs operator/shot metrics.

Beta's joint evacuation was challenged with a role already committed to medicine/voucher: such a role must stay a blocking cell and cannot be reassigned. Beta confirmed exclusion preserves its occupancy and added a regression. Beta noted same-turn upgrade and multishot legality; this candidate retains the inherited all-railgun loadout and does not change volley count midturn.

## Freeze decision boundary

Ready for root review and the uniform formal round as a narrowly corrected candidate, with no claim of improved win rate or ten-night survival. The parent remains an equally justified competitive choice on observed match evidence. No shared judge, frozen prior round, production package or public tests were changed.
