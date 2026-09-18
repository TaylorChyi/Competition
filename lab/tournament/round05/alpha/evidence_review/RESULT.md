# Historical economy comparison audit

All six halves reproduce exactly, excluding only the nondeterministic `p95DecisionMs` field. Every other nested field, including outcome, score components, survival, operator counts, purchases, income and invalid commands, matched the existing `combo-vs-economy.json`; differences arrays are empty.

Opponent is explicitly `lab.tournament.round05.gamma.rejected_economy.brain.decide`. Top-level Gamma is not the historical opponent now. The old development entry point remains unchanged and should not be rerun for this record because it imports that mutable location and overwrites the old JSON.

Use `PYTHONPATH=CoreGeek/src:. python3 lab/tournament/round05/alpha/evidence_review/reproduce.py` from repository root. See `comparison.json` for each checked seed/seat and historical artifact hash, `reproduced.json` for fresh complete results, and `runtime-hashes.json` for both nine-module source manifests. Original JSON and frozen top-level scripts/runtime were not modified. This audit establishes historical reproducibility, not general superiority or official-engine equivalence.
