# Round06 Beta — rejected rocket variant, exact champion retained

Started from R5 Alpha exact9runtime (PARENT.json). Tested only changing TOWER_LOADOUT from three railguns to two railguns plus rocket, preserving positions so the third side-rear site becomes rocket. No escape carryover or economy changes. After failures, restored default; all9runtime files byte-identical to R5 Alpha. Rejected runtime preserved in rocket_trial/.

## Rules and integration check

Local official taskbook: rocket levels1/2/3 have range10/15/global and1/2/3 missiles; each missile20 center,10 around8 cells, overlapping damage accumulates, three-round cooldown window. Railgun energy10/20/30 and range6/8/10. Rocket not blocked by intervening units.

Inherited fire_control uses splash coverage and per-robot cumulative reservations. brain._night defers ready railguns, issues rocket first, and joint_railgun_targets starts each order from a copy of its real rocket reservation. It caps utility per incoming robot, not per shot. Cooling or busy/uncontrolled weapons do not emit attacks. Existing upgrade logic prioritizes rocket: this actually triggered in development, not merely theoretical support.

check_mixed.py passes: rocket reservation retained into railgun planning; level3 triple center hit accumulates60; cooling rocket silent. No timing or hidden-profile assumptions added.

## Six development halves vs fixed R5 Alpha

Field10nights, commerce;22001 operators,22002 advance,26006 nearest. No reserved310xx access. All commands legal.

|seed/mode|seat|rocket / parent survival|point difference|two nights survived|
|---|---:|---:|---:|---|
|22001 operators|0|1300 /1300|+119|yes|
|22001 operators|1|1295 /1300|+7|yes|
|22002 advance|0|627 /350|+71|yes|
|22002 advance|1|127 /750|-149|no|
|26006 nearest|0|643 /1300|-88|yes|
|26006 nearest|1|241 /1300|-347|no|

The1295 half loses by earlier base destruction despite positive points. 22001 rockets reached level3 at436/458. 26006 defender upgraded rocket tolevel2 at67, yet died241. Advance defender died first night127. These are substantive early-survival regressions, satisfying the rejection rule. No speculative cooldown movement change was attempted after this failure.

Default is unchanged champion, not a new distinct strategy. Raw failed results retained in development-rocket.jsonl. No100% or broad rocket superiority claim.
