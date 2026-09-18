# Round 02 Alpha — incumbent retained after two rejected experiments

Final candidate is byte-identical to the nine runtime modules of the published Round01 Alpha champion. PARENT.json remains untouched. All field fixes, shared mining, and cash-flow behavior are retained. This is a competitive incumbent control, not an intentionally weakened opponent.

## Why ten-night survival is incomplete

Read only the completed Round01 main stage. Alpha failed ten nights in 15 of 40 halves. Several nearest/operators failures lose two operators during the first night, cutting production and firepower. Advance failures often reach level-three base with only two or three level-two guns: income 531–756 funds finite base healing but does not create enough sustained damage. Thus a small purchasing threshold change alone is unlikely to eliminate the main failure modes.

## Two bounded rejected hypotheses

Both experiments used only development seeds 22001/operators and 22002/advance, field profile, ten nights, commerce, against frozen Round01 Alpha. Each case was tested from both seats. No Round02 formal seeds were read or used.

### 1. Eight forward walls instead of four

Tested via `decide(..., fortify=8)` without changing other behavior. Hypothesis: a broader opening screen protects the early operators whose loss cripples the economy.

- 22001 operators: Alpha scores 971/954, incumbent 969/999. Paired total 1925–1968 loses; all survive ten nights. Income 554/569 versus 728/732 is substantially lower.
- 22002 advance: Alpha survival 499/350 versus 349/496; split halves and paired score 269–272 loses. Neither side achieves ten nights.
- All commands valid. Extra stone collection reduced income without dependable survival gain. Rejected; final default remains four walls.

Raw record: walls8.json.

### 2. Choose shortest traversable service route across all shop/vendor neighbor cells

Hypothesis: the old first geometrically closest reachable goal can require a longer path around obstacles than another legal service cell. Kept failed-first-step avoidance and zero-step service behavior. A concrete geometry shows a five-step old route versus four-step alternative, but this local route property does not guarantee a better full game.

- 22001 operators: scores 990/952 versus 972/980; paired total 1942–1952 loses. Both survive ten nights.
- 22002 advance: survival 497/350 versus 350/496; split halves, total score 270–272 loses.
- All commands valid. No ten-night improvement; rejected. Runtime economy.py restored byte-for-byte from parent. Rejected implementation retained under rejected/shortest_service_economy.py and raw record shortest_service.json.

The development harness imports the current candidate, so rerunning it after restoration measures the incumbent. For rejected-route reproduction, use the archived economy implementation in an isolated copy. The wall experiment only overrides fortify to 8. Historical JSON records reflect the actual tested variants.

## Peer adversarial exchange

- Beta proposes earlier movement to a nearby unexposed operating square. Warned that currently zero exposure does not cover robots' next moves and can create repeated repositioning; compare night movement/shot totals and preserve control of the last operator.
- Gamma tested two opening walls, the opposite economic tradeoff, and also rejected it. Its final independent delta keeps four opening walls and reduces later repair burden. Warned that fewer maintained walls can cost scarce operators despite improving immediate income.
- Gamma reminded shortest-service selection must preserve an already-adjacent empty path and failed-action rerouting; the attempted implementation preserved both, but full-game evidence still rejected it.

## Final validation and boundary

All nine runtime modules equal the champion byte-for-byte. Eighteen inherited field/economy regression methods pass against the Round02 Alpha import target. No test removed, no hidden-state or seed branch introduced, no simulator changed. Ready/frozen for the root's fresh ten-group formal round. Retaining the incumbent does not promise a win or 100% survival.
