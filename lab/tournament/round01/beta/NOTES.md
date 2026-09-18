# Round01 Beta — frozen candidate

Source: root's integrated tournament/base. Only runtime change is fire_control.py. Operator protection, mirror-aware daytime posture, economic emergency handling and incoming-only targeting remain inherited unchanged.

## Strategy

Add a small official kill-point component to damage allocation: `(observed threat + 0.5 × robot points) × (useful damage / remaining HP + kill bonus)`. The existing damage reservation is retained: multiple guns may legitimately focus one robot until its expected HP is exhausted. Bonus is disabled when station health is <=75% of observed level capacity, leaving inherited threat-only fire allocation under distress. This is observation-based; no seed, simulator priority or hidden state is accessed.

## Independent development evidence

Only22001/22002, field profile, ten nights, commerce, fixed base opponent. These are development samples, not formal ten-fixture tournament results.

- Base threat-only on22001/operators/challenger:10 nights,416 kill points. Final0.5:10 nights,417 vs opponent412.
- Final0.5 reverse seat:10 nights,424 vs opponent427. Combined kill-point margin+2, one half win/one loss, paired score win in this tiny sample.
- Base threat-only on22002/advance/challenger:853 rounds,210 kill points. Final0.5:852 rounds,207 points vs opponent350 rounds/82 points. Still wins this half but loses one survival round and three kill points; not uniformly better.
- Weight2 improved22001/operators to435 points but reduced22002/advance to758 rounds; weight6 to752 rounds. Rejected as too much survival disturbance.
- Weight0.25 preserved22002/advance853 but reduced22001/operators to379 points. Rejected.
- No invalid commands in the reported development runs.

Raw data: development.jsonl, development-gated.jsonl, development-small.jsonl and development-small-reverse.json. Development scripts intentionally expose test weights only in the standalone harness; the exported `decide(observation)` uses fixed0.5 with no extra config.

## Mutual audit and deterministic check

Alpha warned that high-point full-health Boss damage can distract from a near lethal small robot. `check_targeting.py` verifies the near10HP small robot is selected instead of a distant800HP Boss; bonus is normalized by remaining health.

Gamma warned that points cannot precede base survival. Distressed-station test verifies exact target parity with inherited threat-only policy at station100HP. Adopted the healthy-station gate; it does not erase all earlier trajectory effects, as the measured one-round survival loss shows.

No claim of100% or full-game official equivalence. Root owns formal pairwise ten-group tournament, ties, release and subsequent inheritance.
