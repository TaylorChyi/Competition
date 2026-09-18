#!/usr/bin/env python3
"""Paired field-informed scenarios. This is not an official match replay."""
import argparse
import hashlib
from itertools import combinations
import json
import os
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'CoreGeek/src')]
from lab.arena import Arena, TEAMS
from tools.run_league import load_bot, score, half_winner, fixture_winner, table


def fingerprints(paths):
    files={ROOT/'lab/arena.py',ROOT/'lab/night_sim.py',ROOT/'lab/field/experiment.json',
           Path(__file__),ROOT/'tools/run_league.py',ROOT/'CoreGeek/src/agent/protocol.py',
           ROOT/'CoreGeek/src/agent/targeting.py'}
    for path in paths.values():
        files.update(path.glob('*.py'))
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage',choices=('development','holdout'),required=True)
    args=parser.parse_args()
    os.environ.pop('COMPETITION_ROCKET_POLICY',None)
    base=ROOT/'lab/field'
    config=json.loads((base/'experiment.json').read_text())
    paths={name:ROOT/path for name,path in config['candidates'].items()}
    selected=config['holdoutCandidate']
    hashes=fingerprints(paths)
    if args.stage=='holdout':
        dev=json.loads((base/'development-results.json').read_text())
        assert dev['complete'] and hashes==dev['sourceHashes'],'Candidate or judge changed after development'
        pairs=[(selected,name) for name in paths if name!=selected]
        seeds=config['holdoutSeeds']
    else:
        pairs=list(combinations(paths,2));seeds=config['developmentSeeds']
    report={'stage':args.stage,'spec':config,'sourceHashes':hashes,'fixtures':[],
            'complete':False,'candidate':selected}
    started=time.monotonic()
    output=base/(args.stage+'-results.json')
    def save():
        assert hashes==fingerprints(paths),'Judge or candidate changed during evaluation'
        report['elapsedSeconds']=round(time.monotonic()-started,2)
        output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    for first,second in pairs:
        for seed in seeds:
            for profile in config['profiles']:
                fixture={'players':[first,second],'seed':seed,'profile':profile['name'],'halves':[]}
                for seat in (0,1):
                    bots={name:load_bot(paths[name],f'field_{args.stage}_{len(report["fixtures"])}_{seat}_{name.replace("-","_")}')
                          for name in (first,second)}
                    game=Arena(seed,profile['wave'],profile['priority'],config['nights'],commerce=True)
                    result=game.run({TEAMS[seat]:bots[first],TEAMS[1-seat]:bots[second]})
                    values=[result[TEAMS[seat]],result[TEAMS[1-seat]]]
                    fixture['halves'].append({'firstSeat':TEAMS[seat],'results':values,
                                             'scores':[score(v) for v in values],'outcome':half_winner(*values)})
                fixture['outcome']=fixture_winner(fixture['halves'])
                report['fixtures'].append(fixture);save()
                print(json.dumps({'fixture':len(report['fixtures']),'players':fixture['players'],
                    'seed':seed,'profile':profile['name'],'outcome':fixture['outcome'],
                    'nights':[[v['survivedNights'] for v in h['results']] for h in fixture['halves']]},ensure_ascii=False),flush=True)
    report['table']=table(report['fixtures'])
    direct=[]
    for f in report['fixtures']:
        if set(f['players'])=={selected,'released'}:
            i=f['players'].index(selected)
            direct.append((f,i))
    wins=sum(f['outcome']*(1 if i==0 else -1)==1 for f,i in direct)
    losses=sum(f['outcome']*(1 if i==0 else -1)==-1 for f,i in direct)
    survival=[sum(h['results'][i if j==0 else 1-i]['survivedTwoNights']
                  for f,i in direct for h in f['halves']) for j in (0,1)]
    report['gate']={'passed':wins>losses and survival[0]>=survival[1]
                   and report['table'][selected]['invalidCommands']==0,
                   'winsAgainstReleased':wins,'lossesAgainstReleased':losses,
                   'twoNightSurvivalsCandidateReleased':survival}
    report['complete']=True;save()
    print(json.dumps({'table':report['table'],'gate':report['gate']},ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':
    main()
