#!/usr/bin/env python3
"""Fresh survival holdout; earlier development/validation are regression prerequisites."""
import argparse
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'CoreGeek/src')]
from lab.arena import Arena, TEAMS
from tools import run_survival_gate as gate
from tools.run_league import load_bot
from tools.run_qualified_tournament import qualify, require, digest

SPEC = Path(__file__).with_name('holdout-plan.json')


def validate(report, cases, complete=False):
    actual = [(e['seed'], e['priority'], e['seat']) for e in report['episodes']]
    require(len(set(actual)) == len(actual) and actual == cases[:len(actual)],
            'Holdout episodes duplicated, reordered or outside plan')
    if complete:
        require(len(actual) == len(cases), 'Incomplete holdout')


def survived(result):
    return gate.passed(result, 10) and result.get('survivalRounds') == 1300


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('candidate', 'development-report', 'validation-report', 'output'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    os.environ.pop('COMPETITION_ROCKET_POLICY', None)
    candidate = (ROOT / args.candidate).resolve()
    spec, regression_plan = json.loads(SPEC.read_text()), json.loads(gate.PLAN.read_text())
    require(spec['seeds'] == list(range(56000,56010)) and spec['seats'] == list(TEAMS)
            and spec['priority'] == 'nearest' and spec['nights'] == 10
            and spec['wave'] == 'field' and spec['commerce'] is True
            and spec['opponent'] == 'lab/tournament/round05/alpha', 'Unexpected holdout spec')
    require(not (set(spec['seeds']) & {c['seed'] for stage in ('development','validation')
                                    for c in regression_plan[stage]}), 'Holdout overlaps regression')
    references = {'development': args.development_report, 'validation': args.validation_report}
    provenance = qualify(candidate, references, regression_plan)
    cases = [(seed, 'nearest', seat) for seed in spec['seeds'] for seat in spec['seats']]
    opponent = ROOT / spec['opponent']
    def snapshot():
        values = gate.hashes(candidate, opponent)
        for path in (Path(__file__), SPEC, ROOT / 'tools/run_qualified_tournament.py',
                     (ROOT / args.development_report).resolve(), (ROOT / args.validation_report).resolve()):
            values[str(path.relative_to(ROOT))] = digest(path)
        return values
    source_hashes = snapshot()
    output = Path(args.output).resolve()
    require(output not in {(ROOT / name).resolve() for name in source_hashes} and
            output not in {candidate / name for name in gate.RUNTIME} and
            output not in {(ROOT / args.development_report).resolve(),
                           (ROOT / args.validation_report).resolve(), SPEC, Path(__file__)},
            'Output cannot overwrite runtime, spec, script or regression inputs')
    if output.exists():
        report = json.loads(output.read_text())
        require(report['stage'] == 'fresh-holdout' and report['candidatePath'] == str(candidate.relative_to(ROOT))
                and report['sourceHashes'] == source_hashes and report['spec'] == spec
                and report['regressionQualifications'] == provenance, 'Frozen holdout inputs changed')
        validate(report, cases, complete=report['complete'])
    else:
        report = {'stage': 'fresh-holdout', 'spec': spec, 'candidatePath': str(candidate.relative_to(ROOT)),
                  'regressionQualifications': provenance, 'sourceHashes': source_hashes,
                  'episodes': [], 'complete': False, 'passed': False, 'elapsedSeconds': 0,
                  'pvpAllowed': False, 'manualReviewRequired': True}
    started, previous = time.monotonic(), report['elapsedSeconds']
    def save():
        require(snapshot() == source_hashes and qualify(candidate, references, regression_plan) == provenance,
                'Holdout sources or regression inputs changed during run')
        validate(report, cases, complete=report['complete'])
        report['elapsedSeconds'] = round(previous + time.monotonic() - started, 3)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    for index, (seed, priority, seat) in enumerate(cases):
        if index < len(report['episodes']): continue
        other = next(team for team in TEAMS if team != seat)
        policies = {seat: load_bot(candidate, f'fresh_{index}_candidate'),
                    other: load_bot(opponent, f'fresh_{index}_background')}
        result = Arena(seed, 'field', priority, 10, commerce=True).run(policies)
        report['episodes'].append({'seed': seed, 'priority': priority, 'seat': seat,
                                  'candidate': result[seat], 'background': result[other]})
        save()
        print(json.dumps({'episode': index + 1, 'passed': survived(result[seat])}), flush=True)
    report['complete'] = True
    report['survivedTenNights'] = sum(survived(e['candidate']) for e in report['episodes'])
    report['passed'] = report['survivedTenNights'] == len(cases)
    save()
    print(json.dumps({k: report[k] for k in ('stage','complete','passed','survivedTenNights','manualReviewRequired')}))


if __name__ == '__main__':
    main()
