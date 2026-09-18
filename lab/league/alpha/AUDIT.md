# Read-only freeze audit

No Python source changed. Reviewed tools/run_league.py, alpha/economy.py and its protocol loading boundary against the task specification chapters 6–8. No holdout results read.

## League adjudication

No observed draw-as-win or base-HP-as-score defect.

- `score` (lines 21–22) adds kill points and 10 × day for each completed surviving night. Remaining base HP magnitude does not enter the score.
- `half_winner` (25–30) prefers later base destruction, treating a surviving base as infinite survival; same death round or both alive compares scores and returns zero for exact equality.
- `fixture_winner` (33–39) compares half wins first and total score when half wins tie. Split wins and equal summed scores produce a draw.
- Swapped halves remap results into `[first, second]` order before storing scores and outcomes; table accumulation uses the matching sign.
- `winRate` is wins / all fixtures; draws earn one league point but do not become wins.

Read-only synthetic checks passed: both survive equal scores → draw; same death round equal scores → draw; later death with fewer points → win; split halves with equal summed scores → fixture draw.

### Boundaries

1. The score excludes chapter 6 task-completion points (`score_1`). This is accurate for the current task-free local model, not a full official match scorer. If task results are later added, they must enter score before official-equivalence claims.
2. One win plus one draw is assigned a fixture win. Chapter 7 explicitly describes two wins and split wins but does not expressly specify this combination. This is a reasonable convention, not a verified official adjudicator behavior.
3. The runner relies on Arena result validity; official response-error disqualification and task handling are not established by these scoring functions.

## Alpha missing-field safety

Read-only actual `decide` calls with a development observation, individually omitting vendorShopList, weaponShopList, robot, teamEnemy, or lastRoundRoleActionResults, all completed without exception. Missing/null whole market lists load as empty; economy declines market activity. Missing station/empty workers are guarded in economy. Backpack/capacity defaults exist in protocol.

### Actionable robustness risks (frozen, not patched)

- A market list entry with a missing `price` throws `KeyError` in `protocol.Turn.load`; malformed or null price can also throw on integer conversion. Omitted entire list is safe, omitted individual mandatory entry fields is not. Reproduced with `weaponShopList=[{'name':'WeaponUpgradeVoucher1'}]`.
- Missing `teamOur.type` or robot `targetTeam` yields no recognized incoming robots. Alpha's night clear-wave economic branch can then leave defensive posts despite observed unidentified robots. This does not crash, but it is not behaviorally safe under incomplete external identity fields. Normal documented observations include these labels.
- Core required fields such as roundNo/mapInfo/teamOur and unit pos/health/roleType are direct parser accesses, so arbitrary partial payloads are not supported. This is an interface contract assumption, not a claim of full missing-field tolerance.

The economic functions are robust to absent optional market/enemy data after successful parsing, but the end-to-end policy is not robust to every malformed or identity-incomplete observation.
