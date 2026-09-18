#!/usr/bin/env python3
"""Bounded parameter search + untouched holdout, with a standalone replay page."""
import hashlib
import itertools
import json
import platform
from pathlib import Path
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'CoreGeek' / 'src')]
from agent.targeting import BASELINE
from lab.night_sim import Night, PROFILES


def aggregate(rows):
    return {'episodes': len(rows),
            'survivalRate': sum(r['survived'] for r in rows) / len(rows),
            'meanBaseHp': statistics.mean(r['baseHp'] for r in rows),
            'meanKills': statistics.mean(r['kills'] for r in rows),
            'meanKillPoints': statistics.mean(r['killPoints'] for r in rows)}


def export_viewer(report, output):
    template = (ROOT / 'lab' / 'viewer.html').read_text()
    payload = json.dumps(report, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    (output / 'index.html').write_text(template.replace('__DEMO_DATA__', payload))


def main():
    spec = json.loads((ROOT / 'lab' / 'experiment.json').read_text())
    output = ROOT / 'night-demo'
    output.mkdir(exist_ok=True)
    started = time.perf_counter()
    count = 0
    fingerprint = {}
    for name in ['lab/experiment.json', 'lab/night_sim.py',
                 'CoreGeek/src/agent/targeting.py', 'CoreGeek/src/agent/protocol.py']:
        fingerprint[name] = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    if '--render-only' in sys.argv:
        report = json.loads((output / 'results.json').read_text())
        # Recorded experiment provenance keeps its historical source paths.
        recorded = {name.replace('bot/', 'CoreGeek/', 1): value
                    for name, value in report['sourceHashes'].items()}
        if recorded != fingerprint:
            raise RuntimeError('Numerical sources changed; existing results cannot be reused')
        export_viewer(report, output)
        print('Re-rendered recorded results; no simulations executed')
        return
    candidates = [dict(BASELINE)]
    grid = spec['candidateGrid']
    for i, (threat, kill, reserve) in enumerate(itertools.product(
            grid['threatWeight'], grid['killBonus'], grid['reserveDamage'])):
        candidates.append({'name': f'candidate_{i}', 'mode': 'splash',
                           'threatWeight': threat, 'killBonus': kill, 'reserveDamage': reserve})

    def evaluate(policy, seed, profile, mirror=False, record=False):
        nonlocal count
        if count >= spec['budget']['maxEpisodes'] or time.perf_counter() - started >= spec['budget']['maxSeconds']:
            raise RuntimeError('Experiment budget reached; no partial result promoted')
        game = Night(seed, profile, mirror)
        result = game.run(policy, record)
        count += 1
        if time.perf_counter() - started >= spec['budget']['maxSeconds']:
            raise RuntimeError('Experiment time budget exceeded; no result promoted')
        return result, game.frames

    training = []
    for policy in candidates:
        rows = [evaluate(policy, seed, profile)[0]
                for seed in spec['trainSeeds'] for profile in spec['profiles']]
        training.append({'policy': policy, 'summary': aggregate(rows), 'rows': rows})
        print('search', policy['name'], json.dumps(training[-1]['summary']), flush=True)
    # Choice is frozen here, before reading or simulating ANY holdout outcome.
    winner = max(training, key=lambda t: tuple(t['summary'][key] for key in spec['selection']))
    selected = dict(winner['policy'])
    frozen = json.dumps(selected, sort_keys=True)
    default = {'name': 'splash_default', 'mode': 'splash',
               'threatWeight': 0, 'killBonus': 0, 'reserveDamage': True}
    policies = {'nearest': dict(BASELINE), 'splash_default': default, 'selected': selected}
    held = {name: [] for name in policies}
    replays = []
    scenarios = list(itertools.product(spec['holdoutSeeds'], spec['profiles'], [False, True]))
    for index, (seed, profile, mirror) in enumerate(scenarios):
        replay = {'seed': seed, 'profile': profile, 'label': PROFILES[profile]['label'],
                  'mirror': mirror, 'runs': {}}
        for name, policy in policies.items():
            record = index < 2 and name in ('nearest', 'selected')
            result, frames = evaluate(policy, seed, profile, mirror, record)
            held[name].append(result)
            if record:
                replay['runs'][name] = {'result': result, 'frames': frames}
        if index < 2:
            replays.append(replay)
    assert json.dumps(selected, sort_keys=True) == frozen
    report = {'schema': 1, 'scope': spec['scope'], 'sourceHashes': fingerprint,
              'executionGeneratorSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'python': platform.python_version(), 'platform': platform.platform(),
              'elapsedSeconds': round(time.perf_counter() - started, 3), 'episodes': count,
              'totalEpisodesIncludingDiagnostic': count + spec.get('previousDiagnosticEpisodes', 0),
              'spec': spec, 'training': training, 'selectedPolicy': selected,
              'holdout': {name: {'summary': aggregate(rows), 'rows': rows} for name, rows in held.items()},
              'replays': replays}
    (output / 'results.json').write_text(json.dumps(report, ensure_ascii=False, separators=(',', ':')) + '\n')
    (output / 'selected-policy.json').write_text(json.dumps(selected, ensure_ascii=False, indent=2) + '\n')
    export_viewer(report, output)
    print(json.dumps({'episodes': count, 'elapsedSeconds': report['elapsedSeconds'],
                      'selected': selected, 'holdout': {n: aggregate(r) for n, r in held.items()}},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
