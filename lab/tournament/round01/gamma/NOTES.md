# Gamma tournament round01 — base retained after adverse experiment

Candidate: the complete runnable copied latest merged base, with no final algorithm delta. This is an intentional competitive incumbent retention, not a weakened opponent. User permits retaining base if small experiments fail; prior widespread summon versions lost durability, so no unfunded summons added.

## Independent trial

Changed only fire_control: multiply base-proximity threat by1+min(4,max(0,1500/baseHP-1)), while retaining operator protection. Hypothesis: alpha/beta may spend shots guarding healthy operators when the station is near death. Rejected implementation preserved in rejected/low_base_pressure.py. Four10-night commerce field trials against base used only developer22001/22002 with swapped seats; raw outcomes in development.json.

| seed / mode | Gamma seat | Gamma score / survival round | Base score / survival round |
|---|---|---|---|
|22001 operators|challenger|966 /1300|954 /1300|
|22001 operators|defender|954 /1300|966 /1300|
|22002 advance|challenger|417 /852|112 /350|
|22002 advance|defender|113 /350|420 /853|

All invalid0. Operators outcomes exactly mirror and show no gain. Advance trial's strong-side survival852 vs incumbent853 is a regression, and the paired scores530 vs532 also do not support adoption. Side asymmetry dominates each individual win, so individual2W2L must not be called useful improvement. Restored fire_control byte-for-byte from tournament/base after trial; all final runtime modules match competitive incumbent. No final claim derives from rejected trial.

## Peer adversarial exchange

- Warned Beta that unconditional kill-score chasing can lose a nearly dead base before securing survival; official earlier base death determines loss even if local kill score increases. Beta reported its constant weights2/6 reduced survival853→758/752 and is now testing healthy-base gating.
- Alpha warned Gamma base-focus must preserve last remaining operator. This reinforces rejecting an unproven generic base multiplier. Gamma sent Alpha warning against repeatedly prioritizing second base voucher ahead of all DPS growth; Alpha confirmed healthy level2 still upgrades guns first.
- Alpha mining sharing/distance policy may face ore-refresh and obstacle-detour tradeoffs; no access to future map states or seeds in decision code.

Scope: developer scenarios only, hypothetical field composition/robot priorities. Root's10 paired groups and any5-group tie-break define this round's recorded win rate and champion. No official100% guarantee. Candidate is READY/FROZEN.
