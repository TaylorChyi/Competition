# Iteration02 Beta independent review

No candidate/runtime/root/judge edits. Own negative-test code only.

## Survival gate

Current plan is3development seeds×2seats=6cases, then10reserved seeds×2seats=20cases, ten nights; opponent is frozen R5Alpha shared-map background. No W/L computed. Success requires no base death, exactly10 positive nightHP values, survivedNights10, zero invalid commands and zero foreign-only shots. Source hashes cover the nine candidate modules, nine opponent modules, plan, gate/loader, arena/night_sim and runtime protocol/targeting used by judge. Current candidate dependency graph stays within these files plus stdlib.

Found a completeness bug in resume/dev-report validation: only episode count is checked, not exact(seed,priority,seat) sequence. Six copies of one passing record are accepted as complete development. Same issue applies to validation/resume. Repro review_gate.py constructs a SYNTHETIC invalid temporary report, invokes the gate without running any arena or reserved seeds, observes passed=true, and removes the temporary report. This is not survival evidence. Reported to root for fix; required fix validates exact case prefix on resume and complete exact sequence at development handoff. Explicit exceptions recommended instead of assert for invocation with Python optimization.

The gate's pass predicate and source fingerprints otherwise meet the requested rule for the current module graph. Future imports of extra local modules would need hash coverage or rejection. Label-per-episode module loading isolates normal relative-import state across episodes; repeated main invocations in one process reuse labels, so fresh-process CLI use remains the tested path.

## Alpha funded conversion review

Read iteration02/alpha/diagnose.py and diagnosis.json. Existing windows: advance challenger only826/827,25cash, carriedWeapon1, route5/4, base1755level3; advance defender zero windows. Therefore this branch cannot be presented as a solution to the defender's third-night death merely by finding a late challenger opportunity.

Concrete mutation hazard sent to Alpha: if use_carried upgrades the old railgun before a neighboring worker builds the replacement rocket in the same command batch, build replaces the upgraded gun withlevel1rocket. The100voucher is lost and night firepower regresses. Conversion must be selected before issuing that upgrade; defer use until the new rocket is observed, or atomically plan a compatible command batch. Also subtract purchases already committed by other roles from the25build cash, exclude busy builder/carrier roles, preserve daylight return/upgrade actions, and never overwrite upgraded weapons without an explicit affordable restoration plan.

Known mixed fire-control counterexample from prior independent Alpha review remains: rocket(5,6) and rail(1,6),10HP targetsX(6,6)/Y(13,12). Rocket-first consumes commonX leavingrail idle; rail-firstX thenrocketY kills both. Reservation arithmetic can be internally correct while fixed ordering wastes available damage.

No unsupported new strategy variant proposed. A read-only Bomb check on prior advance-right death approach found best3×3 immediate effective damage220–280, costing100; this does not establish a better long-term use than a gun upgrade and gives no reason to add a speculative consumable variant.

## Follow-up: implemented Alpha conversion

The implementation rejects same-batch use targeting the old gun, excludes already-using voucher carriers, deducts pending purchases/builds, restricts original gun tolevel1, and keeps3turn daylight slack. These address the initial batch-order objections.

New reproducible defect: two adjacent workers,50cash, one carriedWeapon1 and no currently observed rocket allow two rocket builds in the same command batch. late_rocket_refit checks existing rocket only, not pending rocket builds. Both conversions reuse the same voucher as proof of a funded upgrade. Own review_refit.py reproduces two build commands. Sent to Alpha/root: reject any pending rocket build at helper entry, keeping exactly one conversion. Natural observed25cash windows do not trigger this counterexample, but the generic guarantee is still invalid without that guard.
