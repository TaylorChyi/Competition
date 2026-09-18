#!/usr/bin/env python3
"""Run nearest-only paired tournaments after exact, current survival qualification."""
import argparse
from itertools import combinations
import hashlib
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'CoreGeek/src')]
from lab.arena import Arena, TEAMS
from tools import run_survival_gate as gate
from tools.run_league import load_bot, score, half_winner, fixture_winner, table
from tools.run_tournament import leaders

RULES = ROOT / 'lab/tournament/qualified-rules.json'


def require(value, reason):
    if not value:
        raise ValueError(reason)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_hashes(path):
    return {name: digest(path / name) for name in gate.RUNTIME}


def verify_stage(report, plan, stage):
    require(report['plan'] == plan, 'Qualification plan differs from current plan')
    require(report['stage'] == stage and report['complete'] and report['passed'],
            f'{stage} gate has not passed')
    expected = [(c['seed'], c['priority'], seat) for c in plan[stage] for seat in plan['seats']]
    require(len(expected) == (8 if stage == 'development' else 20), 'Gate must contain 8+20 episodes')
    require(len(set(expected)) == len(expected), 'Duplicate planned qualification scenario')
    actual = [(e['seed'], e['priority'], e['seat']) for e in report['episodes']]
    require(actual == expected and len(set(actual)) == len(actual),
            'Qualification cases incomplete, duplicated or out of order')
    require(all(gate.passed(e['candidate'], plan['nights']) and
                e['candidate'].get('survivalRounds') == 1300 for e in report['episodes']),
            'Qualification contains a failed episode')
    if stage == 'validation':
        require(report.get('pvpAllowed') is True, 'Validation does not allow PvP')


def qualify(candidate, references, plan):
    paths = {s: (ROOT / references[s]).resolve() for s in ('development', 'validation')}
    reports = {s: json.loads(p.read_text()) for s, p in paths.items()}
    for stage, report in reports.items():
        verify_stage(report, plan, stage)
    dev, val = reports['development'], reports['validation']
    require(dev['candidatePath'] == val['candidatePath'], 'Qualification candidate paths differ')
    require(dev['sourceHashes'] == val['sourceHashes'], 'Gate stage source hashes differ')
    tested = (ROOT / dev['candidatePath']).resolve()
    require(dev['sourceHashes'] == gate.hashes(tested, ROOT / plan['opponent']),
            'Qualification runtime/judge/helper/gate/plan is stale')
    tested_hashes = runtime_hashes(tested)
    require(runtime_hashes(candidate) == tested_hashes, 'Candidate runtime differs from qualified runtime')
    return {'reports': {s: {'path': str(p.relative_to(ROOT)), 'sha256': digest(p)}
                        for s, p in paths.items()},
            'testedCandidate': str(tested.relative_to(ROOT)),
            'candidate': str(candidate.relative_to(ROOT)),
            'byteIdentityVerified': True, 'runtimeHashes': tested_hashes,
            'sourceHashes': dev['sourceHashes']}


def indistinguishable(names, identities):
    return len(names) > 1 and all(identities[n] == identities[names[0]] for n in names[1:])


def block_equivalent_tie(report, names, identities):
    if not indistinguishable(names, identities):
        return False
    report['blockedReason'] = 'Tied leaders have byte-identical runtimes; overtime cannot distinguish them'
    report['structurallyEquivalentLeaders'] = names
    report['complete'], report['champion'] = False, None
    return True


def scheduled_cases(round_no, stage, rules):
    count = rules['fixturesPerPair'] if stage == 0 else rules['overtimeFixturesPerPair']
    # Keep successive rounds disjoint even if a tie never separates statistically.
    require(stage * rules['seedStageStride'] + count <= rules['seedRoundStride'],
            'Overtime exhausted this round seed range; round remains incomplete')
    base = rules['seedBaseOffset'] + round_no * rules['seedRoundStride'] + stage * rules['seedStageStride']
    return [{'seed': base + i, 'profile': 'field-nearest'} for i in range(count)]


def validate_history(report, rules):
    """Recheck every saved fixture, half ordering and statistic before resuming."""
    eligible = rules['agents']
    for stage_index, stage in enumerate(report['stages']):
        require(stage['number'] == stage_index and stage['players'] == eligible, 'Stage order changed')
        expected = [(a, b, c) for a, b in combinations(eligible, 2)
                    for c in scheduled_cases(report['round'], stage_index, rules)]
        require(len(stage['fixtures']) <= len(expected), 'Extra saved fixtures')
        for fixture, (a, b, case) in zip(stage['fixtures'], expected):
            require(fixture['players'] == [a, b] and fixture['seed'] == case['seed'] and
                    fixture['profile'] == case['profile'], 'Fixture order/case changed')
            require(len(fixture['halves']) == 2, 'Incomplete paired fixture')
            for seat, half in enumerate(fixture['halves']):
                values = half['results']
                require(half['firstSeat'] == TEAMS[seat] and len(values) == 2,
                        'Half seat/results order changed')
                require(half['scores'] == [score(v) for v in values] and
                        half['outcome'] == half_winner(*values), 'Half statistic mismatch')
            require(fixture['outcome'] == fixture_winner(fixture['halves']), 'Fixture statistic mismatch')
        if stage['complete']:
            require(len(stage['fixtures']) == len(expected), 'Completed stage is missing fixtures')
            eligible = leaders(stage['fixtures'], eligible)
            require(stage['leaders'] == eligible and stage['table'] == table(stage['fixtures']),
                    'Stage standings mismatch')
        else:
            require(stage_index == len(report['stages']) - 1, 'Incomplete stage before later stage')
    if report['complete']:
        require(report['table'] == report['stages'][0]['table'], 'Main table mismatch')
        require(report['stages'] and report['stages'][-1]['complete'] and len(eligible) == 1 and
                report['champion'] == eligible[0], 'Invalid completed champion')
    return eligible


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--round', type=int, required=True)
    parser.add_argument('--qualifications', required=True,
                        help='JSON mapping each agent to development and validation report paths')
    args = parser.parse_args()
    require(args.round >= 7, 'Qualified tournaments start at round7')
    os.environ.pop('COMPETITION_ROCKET_POLICY', None)
    rules = json.loads(RULES.read_text())
    plan = json.loads(gate.PLAN.read_text())
    require((rules['fixturesPerPair'], rules['halvesPerFixture'], rules['overtimeFixturesPerPair']) == (10,2,5),
            'Require ten paired fixtures and five paired overtime fixtures')
    require((rules['seedBaseOffset'], rules['seedRoundStride'], rules['seedStageStride']) == (30000,1000,20),
            'Unexpected official seed schedule')
    require(rules['priority'] == 'nearest' and rules['nights'] == plan['nights'] == 10 and
            plan['seats'] == list(TEAMS) and all(c['priority'] == 'nearest'
                for stage in ('development', 'validation') for c in plan[stage]), 'Only nearest ten-night plan is supported')
    require(not ({c['seed'] for c in plan['development']} &
                 {c['seed'] for c in plan['validation']}), 'Development and validation overlap')
    directory = ROOT / 'lab/tournament' / f'round{args.round:02d}'
    names = rules['agents']
    references = json.loads(Path(args.qualifications).read_text())
    require(set(references) == set(names), 'Supply exactly one qualification reference for each agent')
    paths = {n: directory / n for n in names}
    provenance = {n: qualify(paths[n], references[n], plan) for n in names}
    identities = {n: provenance[n]['runtimeHashes'] for n in names}
    require(not indistinguishable(names, identities), 'All candidate runtimes identical; no meaningful tournament')
    def snapshot():
        sources = {str(p.relative_to(ROOT)): digest(p) for p in
                   (Path(__file__), RULES, ROOT / 'tools/run_tournament.py')}
        for n in names:
            sources.update(gate.hashes(paths[n], ROOT / plan['opponent']))
        return sources
    source_hashes = snapshot()
    output = directory / 'qualified-results.json'
    if output.exists():
        report = json.loads(output.read_text())
        require(report['round'] == args.round and report['rules'] == rules and
                report['sourceHashes'] == source_hashes and report['qualifications'] == provenance,
                'Frozen sources or qualification references changed')
        eligible = validate_history(report, rules)
        if report['complete']:
            print(json.dumps({'champion': report['champion'], 'table': report['table']})); return
    else:
        report = {'round': args.round, 'rules': rules, 'sourceHashes': source_hashes,
                  'qualifications': provenance, 'stages': [], 'complete': False,
                  'champion': None, 'elapsedSeconds': 0}
        eligible = names
    started, previous = time.monotonic(), report['elapsedSeconds']
    def save():
        require(snapshot() == source_hashes, 'Frozen source changed during tournament')
        require({n: qualify(paths[n], references[n], plan) for n in names} == provenance,
                'Qualification references changed during tournament')
        validate_history(report, rules)
        report['elapsedSeconds'] = round(previous + time.monotonic() - started, 3)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    stage_index = len(report['stages'])
    if report['stages'] and not report['stages'][-1]['complete']:
        stage_index -= 1
    while len(eligible) > 1:
        if block_equivalent_tie(report, eligible, identities):
            save(); print(report['blockedReason']); return
        cases = scheduled_cases(args.round, stage_index, rules)
        if len(report['stages']) <= stage_index:
            report['stages'].append({'number': stage_index, 'kind': 'main' if stage_index == 0 else 'overtime',
                                     'players': eligible, 'fixtures': [], 'complete': False})
        stage = report['stages'][stage_index]
        index = 0
        for first, second in combinations(eligible, 2):
            for case in cases:
                index += 1
                if index <= len(stage['fixtures']): continue
                fixture = {'players': [first, second], **case, 'halves': []}
                for seat in (0, 1):
                    bots = {n: load_bot(paths[n], f'qualified_{args.round}_{stage_index}_{index}_{seat}_{n}')
                            for n in (first, second)}
                    results = Arena(case['seed'], 'field', 'nearest', 10, commerce=True).run(
                        {TEAMS[seat]: bots[first], TEAMS[1-seat]: bots[second]})
                    values = [results[TEAMS[seat]], results[TEAMS[1-seat]]]
                    fixture['halves'].append({'firstSeat': TEAMS[seat], 'results': values,
                                             'scores': [score(v) for v in values], 'outcome': half_winner(*values)})
                fixture['outcome'] = fixture_winner(fixture['halves'])
                stage['fixtures'].append(fixture); save()
                print(json.dumps({'stage': stage_index, 'fixture': index, 'players': [first, second],
                                  **case, 'outcome': fixture['outcome']}), flush=True)
        eligible = leaders(stage['fixtures'], eligible)
        stage.update(table=table(stage['fixtures']), leaders=eligible, complete=True); save()
        stage_index += 1
    report.update(champion=eligible[0], table=report['stages'][0]['table'], complete=True)
    row = report['table'][eligible[0]]
    report['target100Percent'] = row['wins'] == row['fixtures']
    report['overtimeStages'] = len(report['stages']) - 1
    save()


if __name__ == '__main__':
    main()
