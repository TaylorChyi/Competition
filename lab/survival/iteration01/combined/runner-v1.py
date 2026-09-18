#!/usr/bin/env python3
"""Gate ten-night survival before resuming agent-vs-agent tournaments."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'CoreGeek/src')]
from lab.arena import Arena, TEAMS
from tools.run_league import load_bot

RUNTIME = ('__init__.py', 'brain.py', 'economy.py', 'fire_control.py', 'grid.py',
           'guard.py', 'protocol.py', 'server.py', 'targeting.py')
PLAN = ROOT / 'lab/survival/plan.json'


def hashes(candidate, opponent):
    files = [PLAN, Path(__file__), ROOT / 'tools/run_league.py', ROOT / 'lab/arena.py',
             ROOT / 'lab/night_sim.py', ROOT / 'CoreGeek/src/agent/protocol.py',
             ROOT / 'CoreGeek/src/agent/targeting.py']
    files += [directory / name for directory in (candidate, opponent) for name in RUNTIME]
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(set(files))}


def passed(result, nights):
    hp = result['nightHp']
    return (result['baseDeathRound'] is None and len(hp) == nights and all(h > 0 for h in hp)
            and result['survivedNights'] == nights and result['invalidCommands'] == 0
            and result['foreignOnlyShots'] == 0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', required=True, help='Frozen package directory under repository')
    parser.add_argument('--stage', choices=('development', 'validation'), default='development')
    parser.add_argument('--output', required=True)
    parser.add_argument('--development-report', help='Required for validation; exact same source hashes')
    args = parser.parse_args()
    os.environ.pop('COMPETITION_ROCKET_POLICY', None)
    candidate = (ROOT / args.candidate).resolve()
    plan = json.loads(PLAN.read_text())
    opponent = ROOT / plan['opponent']
    source_hashes = hashes(candidate, opponent)
    cases = [(case, seat) for case in plan[args.stage] for seat in plan['seats']]
    if args.stage == 'validation':
        assert args.development_report, 'Pass the development gate before running reserved validation'
        dev = json.loads(Path(args.development_report).read_text())
        assert dev['stage'] == 'development' and dev['complete'] and dev['passed']
        assert dev['sourceHashes'] == source_hashes, 'Candidate/judge changed after development'
        assert len(dev['episodes']) == len(plan['development']) * len(plan['seats'])
        assert all(passed(e['candidate'], plan['nights']) for e in dev['episodes'])
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        report = json.loads(output.read_text())
        assert report['sourceHashes'] == source_hashes, 'Frozen sources changed; use a new report'
        assert report['stage'] == args.stage
    else:
        report = {'plan': plan, 'stage': args.stage, 'candidatePath': str(candidate.relative_to(ROOT)),
                  'sourceHashes': source_hashes, 'episodes': [], 'complete': False, 'passed': False,
                  'pvpAllowed': False, 'elapsedSeconds': 0}
    started, previous = time.monotonic(), report['elapsedSeconds']

    def save():
        assert hashes(candidate, opponent) == source_hashes, 'Source changed during evaluation'
        report['elapsedSeconds'] = round(previous + time.monotonic() - started, 3)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')

    for index, (case, seat) in enumerate(cases):
        if index < len(report['episodes']):
            continue
        other = next(team for team in TEAMS if team != seat)
        policy = load_bot(candidate, f'survival_{args.stage}_{index}_candidate')
        fixed = load_bot(opponent, f'survival_{args.stage}_{index}_background')
        arena = Arena(case['seed'], plan['wave'], case['priority'], plan['nights'], plan['commerce'])
        results = arena.run({seat: policy, other: fixed})
        record = {'seed': case['seed'], 'priority': case['priority'], 'seat': seat,
                  'candidate': results[seat], 'background': results[other]}
        report['episodes'].append(record)
        save()
        print(json.dumps({'episode': index + 1, 'of': len(cases), **case, 'seat': seat,
                          'survivedNights': results[seat]['survivedNights'],
                          'deathRound': results[seat]['baseDeathRound'],
                          'passed': passed(results[seat], plan['nights'])}), flush=True)
    report['complete'] = len(report['episodes']) == len(cases)
    report['survivedTenNights'] = sum(passed(e['candidate'], plan['nights']) for e in report['episodes'])
    report['passed'] = report['complete'] and report['survivedTenNights'] == len(cases)
    report['pvpAllowed'] = args.stage == 'validation' and report['passed']
    save()
    print(json.dumps({k: report[k] for k in ('stage', 'complete', 'survivedTenNights', 'passed',
                                            'pvpAllowed', 'elapsedSeconds')}), flush=True)


if __name__ == '__main__':
    main()
