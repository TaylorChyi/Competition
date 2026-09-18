# Frozen-candidate interface and wallet audit

Read-only runtime audit; no .py edited and no new tuning/matches executed. Official sources: docs/接口文档.md sections2.2/2.3 and docs/任务书.md shop/consumables sections.

## Summon protocol
- Alpha/Beta current runtime economy modules contain no RobotSummonOrder purchase/use path.
- Gamma buys exactly SmallRobotSummonOrder or MiddleRobotSummonOrder, matching official English names and observed weaponShopList price. `num:1` is an integer. `use` includes the exact carried item name and omits num, correctly using one item.
- `use` without targetPos is consistent with interface2.3: only some items require targetPos. Summon effect explicitly targets the opposing next night with no coordinate requirement. The generic targetPos table marks field optional; its one-position statement does not make every use coordinate-mandatory. Bomb/Dizzy/upgrade coordinate requirements cannot be generalized to summons.
- Gamma only the single official pioneer issues summon use, in ten unique daily phases6,12,...60. No night summons. A role already assigned use is skipped by later phases. Thus <=10 per day even if inventory externally contains10+ orders, independent of persistent memory.
- Narrow buy window48..50 plus inventory order_stock==0 means <=1 successful purchase/day from ordinary play: no summon use phase inside49..50, so a just-bought order prevents another buy. Stock aggregates all controllable living roles; carried orders/vouchers cost nothing again at use.

## Shared wallet
- All three develop() functions recompute budget=observed team gold minus already-issued non-wall builds (25 each) and every buy command price*num. Purchases do not credit planned same-turn sales. Multiple worker medicine purchases therefore reserve sequentially, and the final pioneer purchase uses remaining budget.
- All three _worker_day() functions deduct existing purchases and pending tower builds before another tower build. Wall builds consume carried stone, not coins.
- Normal voucher purchases cap num by needed targets, budget//price and backpack room. Only designated courier purchases vouchers, so stock not including pending purchases does not produce duplicate courier purchases. If pioneer dies, fallback courier is exactly one worker.
- urgent_refit() checks raw turn.gold rather than budget, but current call ordering makes it safe under official one-pioneer roster: daytime urgent-refit pass precedes any worker build/buy; carried-use pass spends no coins. Later workers see that buy and reserve it. Nighttime only pioneer urgent_refit can buy; no worker shop purchase path executes. Do not move this helper later in the phase or permit multiple pioneers without adding reservations.
- Gamma's attack branch runs inside courier develop() after budget reservation and returns immediately. Existing repair/order stock never adds money, and existing orders prevent another order purchase. No route was found where summon+other purchases exceed observed gold in one normal decide invocation.

## Bounded caveats found
- Shared inherited low-health Medicine branch lacks backpack_full guard, and urgent_refit lacks a capacity guard. Full inventory can therefore cause a legal-shaped purchase command to fail inventory validation. This is an execution-failure risk, not free income, and must not be credited as a successful purchase. No runtime fix applied while frozen.
- Cap proof relies on documented single pioneer and130-round day. It is not a claim for arbitrarily altered game rules.
- Source audit establishes code reservations, not official judge acceptance. Main's unified arena must reject unaffordable or full-bag buys.

## Evidence boundary
Gamma/opponents copies are developer snapshot materials only, copied while peers iterated. Development scores and causal speculation are not the final tournament result. Formal comparative conclusions must use root's unified frozen candidates, shared rules, swapped sides and held-out evaluation.

## Round3 superseding notes
Runtime changed only after explicit round3 authorization, then frozen again. Both previously identified full-backpack purchase risks are fixed and synthetic checked. Gamma now uses only final10 day slots under an observed enemy level3/<900 condition; Middle purchase requires150 spare coins. Shared-wallet reservation order remains the same. Medicine additionally reserves next repair voucher cost unless voucher already held.
