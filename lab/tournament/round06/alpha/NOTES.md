# R6 Alpha incumbent and peer audit

READY/frozen. All nine runtime files match PARENT.json/R5 Alpha champion byte-for-byte; review/runtime-parent-check.json records the checks. No strategy change, no310xx viewed, no new match results claimed. All24 inherited causal/regression tests pass against this round's modules.

## Beta mixed-gun concrete counterexample

A level1 rocket at(5,6) and railgun at(1,6), base(5,5), incoming10HP X(6,6), Y(13,12). Current pending-railgun execution fires rocket first: its preferred nearby splash kills X, reservation makes railgun idle, Y survives. Railgun→X then rocket→Y kills both. Tested using Beta's default actual fire_control.targets, not an external rocket policy. This is fixed cross-type order opportunity cost, not a reservation double-count or illegal command. It does not occur in Alpha's shipped three-railgun loadout, so no champion change is justified. Sent exact counterexample to Beta.

Existing safeguards remain: cooling, guard-moving and medicine/voucher-busy roles are filtered before eligible railguns; operator IDs stay paired, and all observed robots participate in railgun interception. Per-order reserved copies commit only winner. No deterministic defect found in the incumbent joint-three-railgun implementation.

## Gamma medicine economic counterexample

Full-health level3 base, pioneer absent,125HP worker is courier, at weapon-shop neighbor with100 cash and a level1 gun requiring100 upgrade voucher. New opportunity branch spends10 on medicine, leaving90 and preventing gun upgrade that turn; inherited branch would not buy medicine at HP>=100 with budget below110. Reproduced and sent to Gamma. This is a real tradeoff against gun growth, not illegal spending or evidence that healing is always worse.

The added branch preserves current cash after existing orders and the full next-base-voucher reserve when applicable, requires daytime, existing shop adjacency and inherited purchase_route, and rejects full backpacks. Existing paired-worker return timing runs before develop, so no direct new night departure defect was identified. A role without assigned gun is a separate inherited scheduling edge case, not demonstrated here.

Both peer counterexamples pass in review/check.py. It imports peers' current candidate modules, so it documents the audited state and may need its corresponding snapshot if peers revert candidates; it is not part of the frozen nine runtime modules. No peer implementation was modified or merged. Root owns formal tournament and publication.
