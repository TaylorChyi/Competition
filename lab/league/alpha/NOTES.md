# Alpha — economic defense candidate

Scope: standalone candidate in this directory; no production or release changes. All experiments below are DEVELOPMENT data, using only 22001 and 22002. No holdout inspected.

## Current candidate v4
Three railguns and four forward walls. Pre-purchase the next station voucher, but hold it until station health is at most 40% of its current maximum, during day or night. This preserves the two finite full-heal opportunities and reduces emergency cross-map purchase risk. Candidate is frozen for peer review after the v4 runs below.

## Trials and failures
- v1: two rockets, one railgun, zero default walls, advance 22001: Alpha 507 rounds vs baseline 472; both three full nights. Alpha income 397, zero invalid commands.
- v2: weapon upgrades before station reserve and one-item purchases, advance 22001: died at 235; rejected.
- v1 nearest 22002: died 387, two operators lost during night two. Baseline 1300. Removing walls exposes operators; rejected.
- v3: double rockets plus four walls, nearest 22002: died 633; baseline 1300. Four walls improve survival but double rockets still lose sustained close defense. Rejected.
- v4 nearest 22002: survives all ten nights / 1300 rounds, final base HP 890, zero invalid commands. Baseline also survives with HP 2990. This is local survival evidence, not a win or official-judge proof.

- v4 advance 22001: 745 rounds / five full nights versus baseline 499 / three nights. Income 490, station heals at rounds 238 and 375, two railgun upgrades at 551 and 704, zero invalid commands. Still fails ten-night target.

## Weaknesses and proposed peer attacks
Three railguns offer limited area damage against growing simultaneous waves. Healing without additional weapon damage only postpones defeat under advance pressure. Summons can expose this by concentrating attackers just after finite healing is consumed. However nearest-priority waves make a small wall screen valuable for protecting operators, so simply removing wall expenditure is unsafe. Peer double-rocket variants should be attacked with close dispersed robots during cooldown windows. These are hypotheses for review, not verified matchup wins.

JSON files preserve per-night HP, operators, income, upgrades, and illegal-command totals. Simulator is a local bounded model and was being amended by the main owner; formal competition strength remains unproven.

## Round 2 — revised local judge, cross-candidate development
Round 1 source saved under `round1/`. Current candidate adds a visible-DPS return deadline for held station vouchers, dusk return buffer, legal shared tail mining eligibility, a minimum 25 gold before an upgrade-unlock alone triggers a sale, and night economic work only after all incoming robots are cleared.

- Versus Beta, seed 22001 heavy advance: Alpha 745 rounds / five nights, Beta 477 / three; income 437 vs 259, both zero invalid. Alpha issued 898 day moves, 117 collections, 22 sales, 819 night shots. This run preceded the dusk-return and 25-gold-sale refinement.
- Versus Gamma, seed 22002 heavy advance: Alpha 494 rounds / three nights, Gamma 647 / four; income 215 vs 345, both zero invalid. Alpha issued 605 day moves, 59 collections, seven sales, 471 night shots. Only one base upgrade happened (round 316). Current candidate loses this development half.
- Night mining actually issued zero actions in both crosses: the safety gate never cleared because incoming robots persisted. This is not an observed income improvement.
- Bottleneck: movement dominates collection by about 8–10 times; income purchases finite station healing while little remains for sustained damage upgrades. Under stronger attacks the team cannot clear the wave to unlock safe night harvesting. Alpha does not yet solve ten-night advance pressure.

Peer review sent directly: Beta night refill departure risks temporarily unmanning towers; Gamma early summon purchases risk crowding out station upgrades. Received valid critiques: Alpha fixed 40% threshold ignored courier travel and future night spawn. The current deadline and dusk return address timing, but do not make future waves predictable or guarantee survival.

## Round 3 final candidate

Round 2 runtime files preserved in `round2/`. No seed or simulator-profile information is inspected by the policy. One economic hypothesis plus a limited safety follow-up were tested, not a parameter sweep.

Changes:
- A completely healthy station no longer preempts weapon upgrades; observed station damage puts its next voucher first. This releases first-day cash when the base has not demonstrated a repair need.
- Retain the existing separate return/consumption thresholds and dusk return buffer.
- Urgent refill refuses full backpacks, no longer counts unsold ore as immediately spendable cash, accounts for prior purchase commands, and refuses a new shop detour that cannot fit a simple daylight round trip.
- Both low-health and opportunity medicine buying check backpack room. Opportunity medicine requires cash left for the observed price of the next station voucher (150 at level two), rather than always retaining only 100.

Fixed adversary: `beta/round2`, never the actively edited Beta. Development evidence:
- Economic hypothesis plus initial medicine reserve: 22001 nearest left score 948–902 (win), right 849–965 (loss); fixture loses on total points. Both sides survive ten nights. This improves one half but does not solve the nearest matchup.
- Same hypothesis 22002 advance left score 159–145, survival 494–489; right score 309–159, survival 757–490. Both halves win by survival, but Alpha still fails ten nights.
- Dynamic next-voucher medicine reserve follow-up, 22002 advance both seats: same scores and survival outcomes, income left 233 and right 403. Both halves zero illegal commands. This final follow-up did not remove the favorable advance development result.
- All six development halves had zero illegal commands. No holdout read or used. JSON files retain each match result.

Focused safety calls verified full-backpack injured workers do not buy medicine and full-backpack pioneers do not enter urgent refill. The final candidate remains a locally evaluated economic defense strategy, not a universal winner. Main owner will decide by the uniform third-round league and separate holdout.
