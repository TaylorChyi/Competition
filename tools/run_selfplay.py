#!/usr/bin/env python3
"""Evaluate small strategy variants against the last released Bot, then hold out."""
import argparse
from contextlib import contextmanager
from functools import partial
import hashlib
import importlib
import json
import os
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'CoreGeek/src')]
from agent.brain import decide
from agent.targeting import BASELINE
from lab.arena import Arena, TEAMS

MIXED = ('gatling', 'railgun', 'rocket')
SPLASH = {'name': 'defense_splash', 'mode': 'splash', 'threatWeight': 3,
          'killBonus': 15, 'reserveDamage': True}
CANDIDATES = {
    'filter_only': {'loadout': MIXED, 'rocket_policy': BASELINE, 'cover': False},
    'covered_mixed': {'loadout': MIXED, 'rocket_policy': BASELINE, 'cover': True},
    'covered_two_rockets': {'loadout': ('rocket', 'railgun', 'rocket'), 'rocket_policy': SPLASH, 'cover': True},
    'covered_three_rockets': {'loadout': ('rocket', 'rocket', 'rocket'), 'rocket_policy': SPLASH, 'cover': True},
}


@contextmanager
def previous_bot(commit):
    git = '/Library/Developer/CommandLineTools/usr/bin/git'
    if not Path(git).is_file():
        git = shutil.which('git')
    with tempfile.TemporaryDirectory(prefix='competition-baseline-') as folder:
        destination = Path(folder) / 'baseline_agent'
        destination.mkdir()
        names = subprocess.check_output([git, 'ls-tree', '--name-only', commit+':CoreGeek/src/agent'], cwd=ROOT, text=True).splitlines()
        for name in names:
            if name.endswith('.py'):
                raw = subprocess.check_output([git, 'show', commit+':CoreGeek/src/agent/'+name], cwd=ROOT)
                (destination/name).write_bytes(raw)
        sys.path.insert(0, folder)
        yield importlib.import_module('baseline_agent.brain').decide
        sys.path.remove(folder)


def summarize(rows):
    profiles = sorted({row['profile'] for row in rows})
    return {
        'matches': len(rows),
        'twoNightSurvival': statistics.mean(row['ours']['survivedTwoNights'] for row in rows),
        'worstProfileTwoNightSurvival': min(statistics.mean(row['ours']['survivedTwoNights']
            for row in rows if row['profile'] == profile) for profile in profiles),
        'meanSurvivedNights': statistics.mean(row['ours']['survivedNights'] for row in rows),
        'meanSurvivalRounds': statistics.mean(row['ours']['survivalRounds'] for row in rows),
        'meanFinalBaseHp': statistics.mean(row['ours']['nightHp'][-1] for row in rows),
        'meanNightHp': [statistics.mean(row['ours']['nightHp'][i] for row in rows) for i in range(3)],
        'meanNightOperators': [statistics.mean(row['ours']['nightOperators'][i] for row in rows) for i in range(3)],
        'foreignOnlyShots': sum(row['ours']['foreignOnlyShots'] for row in rows),
        'invalidCommands': sum(row['ours']['invalidCommands'] for row in rows),
        'p95DecisionMsMax': max(row['ours']['p95DecisionMs'] for row in rows),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true', help='One training scenario per candidate; no promotion')
    args = parser.parse_args()
    # No inherited experimental override may change the archived baseline.
    os.environ.pop('COMPETITION_ROCKET_POLICY', None)
    spec = json.loads((ROOT/'lab/selfplay.json').read_text())
    started, count = time.monotonic(), 0
    output = ROOT/'lab/selfplay-results.json'
    with previous_bot(spec['baselineCommit']) as old:
        def play(name, seed, profile, seat):
            nonlocal count
            if count >= spec['maxMatches'] or time.monotonic()-started >= spec['maxSeconds']:
                raise RuntimeError('Self-play budget reached; no partial result promoted')
            our_team = TEAMS[seat]
            game = Arena(seed, profile['wave'], profile['priority'], spec['nights'])
            policies = dict.fromkeys(TEAMS, old)
            policies[our_team] = partial(decide, **CANDIDATES[name])
            metrics = game.run(policies)
            count += 1
            row = {'candidate': name, 'seed': seed, 'profile': profile['name'], 'seat': our_team,
                   'ours': metrics[our_team], 'opponent': metrics[TEAMS[1-seat]]}
            print(json.dumps({'match': count, 'candidate': name, 'seed': seed, 'profile': profile['name'],
                              'seat': our_team, 'ourHp': row['ours']['nightHp'], 'opponentHp': row['opponent']['nightHp'],
                              'foreignOnlyShots': [row['ours']['foreignOnlyShots'], row['opponent']['foreignOnlyShots']],
                              'invalid': row['ours']['invalidCommands']}, ensure_ascii=False), flush=True)
            if time.monotonic()-started >= spec['maxSeconds']:
                raise RuntimeError('Self-play time budget reached; no result promoted')
            return row

        def evaluate(name, seeds):
            profiles = spec['profiles'][:1] if args.pilot else spec['profiles']
            seats = (0,) if args.pilot else (0,1)
            return [play(name, seed, profile, seat) for seed in seeds for profile in profiles for seat in seats]

        training = {name: evaluate(name, spec['trainSeeds'][:1] if args.pilot else spec['trainSeeds']) for name in CANDIDATES}
        summaries = {name: summarize(rows) for name,rows in training.items()}
        if args.pilot:
            print(json.dumps({'pilot': summaries, 'seconds': round(time.monotonic()-started, 2)}, indent=2))
            return
        # Freeze selection using only training results, then evaluate held-out seeds.
        winner = max(CANDIDATES, key=lambda name: tuple(summaries[name][key] for key in spec['selection']))
        frozen = json.dumps(CANDIDATES[winner], sort_keys=True)
        holdout = {name: evaluate(name, spec['holdoutSeeds']) for name in dict.fromkeys(('filter_only', winner))}
        assert json.dumps(CANDIDATES[winner], sort_keys=True) == frozen
        hashes = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                  for path in [ROOT/'lab/arena.py', ROOT/'lab/selfplay.json', Path(__file__),
                               *sorted((ROOT/'CoreGeek/src/agent').glob('*.py'))]}
        held_summary = {name: summarize(rows) for name,rows in holdout.items()}
        def score(summary):
            return tuple(summary[key] for key in spec['selection'])
        passes = (score(held_summary[winner]) >= score(held_summary['filter_only']) and
                  all(summarize([r for r in holdout[winner] if r['profile'] == p['name']])['twoNightSurvival'] >=
                      summarize([r for r in holdout['filter_only'] if r['profile'] == p['name']])['twoNightSurvival']
                      for p in spec['profiles']))
        promoted = winner if passes else 'filter_only'
        report = {'spec': spec, 'matches': count, 'elapsedSeconds': round(time.monotonic()-started, 2),
                  'sourceHashes': hashes, 'candidates': CANDIDATES, 'training': training,
                  'trainingSummary': summaries, 'selected': winner, 'selectedPolicy': CANDIDATES[winner],
                  'holdout': holdout, 'holdoutSummary': held_summary,
                  'promoted': promoted, 'promotedPolicy': CANDIDATES[promoted], 'promotionPassed': passes}
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
        print(json.dumps({'selected': winner, 'holdout': report['holdoutSummary'], 'seconds': report['elapsedSeconds']}, indent=2))


if __name__ == '__main__':
    main()
