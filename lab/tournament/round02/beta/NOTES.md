# Round02 Beta — frozen

Inherited exactly the Round01 Alpha champion runtime package (PARENT.json), not the former Beta package. No old kill-point weight was carried forward. Only runtime change is guard.py.

## Change

Pre-empt sustained incoming exposure while keeping control of the same gun when:

- the operator is already below65% HP, or observed immediate incoming fire is at least20;
- one adjacent-to-gun step leaves the observed3-cell robot firing range and reduces approaching exposure to at most35% of current immediate exposure;
- the sole threatening robot cannot be finished by a ready in-range volley.

The inherited emergency escape, no-lethal-return behavior, daytime mirror-aware positioning and incoming filter remain unchanged. This is not a claim that the next turn is guaranteed safe: robot movement/target rules are partly unknown.

## Focused variants

1. Initially considered requiring literally zero approaching exposure. Rejected as ineffective: one step from range3 reaches at most range4, which the conservative model scores at35%; the six development games matched the inherited policy. The raw result is retained as development-safe-step.jsonl, not represented as a success.
2. Final sustained-fire pre-emption above. No third variant needed. No seed/priority/hidden state branches.

## Deterministic check and actual trigger

check_guard.py verifies a healthy worker can step away from sustained500HP large-robot fire while the parent waits, but does not abandon a ready shot at a10HP small robot.

A separate trace on22002/field/advance/challenger observed the new early branch at turns335 and467, both at220HP. It therefore is not dead code. Candidate fires536 shots versus the unchanged-case535, rather than losing ongoing fire in that observed half. Trace saved in preempt-trace.json.

## Paired development evidence

Only development22001/22002, ten nights, field profile, commerce, fixed Round01 Alpha champion; no official Round02 reserved seeds read.

- 22001 nearest: both seats still10 nights, kill-point margins+17/−17; identical to inherited self-play, paired draw.
- 22001 operators: same results and paired draw. No general operator-survival improvement demonstrated here.
- 22002 advance: candidate challenger499 rounds vs350, compared with inherited496 vs350; reverse candidate350 vs496 unchanged survival. Kill-point margins+18/−15, giving a small paired score win instead of inherited self-play's draw. Operators still die before10 nights.
- All six final candidate half-games have zero invalid commands.

These tiny development gains are not a100% or general improvement claim. The formal round's fresh ten cases and overtime determine the champion.

## Direct mutual review

Gamma warned that moving instead of delivering a ready finishing shot can prolong threats; final code exempts a sole enemy within the ready gun's volley damage and range. Alpha warned about oscillation and loss of shots; final trigger requires a full departure from current firing range, retains same-gun access, and the observed trace did not reduce total shots. The latter is a limited observation, not proof for all battle states.
