#!/usr/bin/env python3
"""Three evolving policies, one frozen judge, paired games and held-out seeds."""
import argparse
from collections import defaultdict
import hashlib
import importlib
import importlib.util
from itertools import combinations
import json
import os
from pathlib import Path
import statistics
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'CoreGeek/src')]
from lab.arena import Arena, TEAMS


def score(result):
    return result['killPoints']+sum(10*day for day,hp in enumerate(result['nightHp'],1) if hp>0)


def half_winner(first,second):
    death1,death2=first['baseDeathRound'],second['baseDeathRound']
    if death1!=death2:
        return 1 if (death1 or float('inf'))>(death2 or float('inf')) else -1
    difference=score(first)-score(second)
    return (difference>0)-(difference<0)


def fixture_winner(halves):
    wins=sum(h['outcome']==1 for h in halves)
    losses=sum(h['outcome']==-1 for h in halves)
    if wins!=losses:
        return (wins>losses)-(wins<losses)
    difference=sum(h['scores'][0]-h['scores'][1] for h in halves)
    return (difference>0)-(difference<0)


def load_bot(path,label):
    # New module identity every half: no in-process policy memory leaks between
    # roles, opponents or matches, even if a future policy uses local state.
    prefix='_league_'+label
    spec=importlib.util.spec_from_file_location(prefix,path/'__init__.py',
                                               submodule_search_locations=[str(path)])
    module=importlib.util.module_from_spec(spec)
    sys.modules[prefix]=module
    spec.loader.exec_module(module)
    return importlib.import_module(prefix+'.brain').decide


def source_hashes(paths):
    files={ROOT/'lab/arena.py',ROOT/'lab/night_sim.py',ROOT/'lab/league.json',Path(__file__),
           ROOT/'CoreGeek/src/agent/protocol.py',ROOT/'CoreGeek/src/agent/targeting.py'}
    for path in paths.values():
        files.update(path.glob('*.py'))
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}


def table(fixtures):
    rows={}
    for fixture in fixtures:
        for index,name in enumerate(fixture['players']):
            row=rows.setdefault(name,{'fixtures':0,'wins':0,'draws':0,'losses':0,'points':0,
                'halves':0,'halfWins':0,'halfDraws':0,'halfLosses':0,'twoNightSurvivals':0,
                'tenNightSurvivals':0,'survivedNights':[],'scores':[], 'invalidCommands':0,
                'foreignOnlyShots':0,'summonsUsed':0,'profilePoints':defaultdict(list)})
            sign=1 if index==0 else -1
            outcome=fixture['outcome']*sign
            row['fixtures']+=1
            row['wins' if outcome==1 else 'draws' if outcome==0 else 'losses']+=1
            points=3 if outcome==1 else 1 if outcome==0 else 0
            row['points']+=points
            row['profilePoints'][fixture['profile']].append(points)
            for half in fixture['halves']:
                result=half['results'][index]
                row['halves']+=1
                half_outcome=half['outcome']*sign
                row['halfWins' if half_outcome==1 else 'halfDraws' if half_outcome==0 else 'halfLosses']+=1
                row['twoNightSurvivals']+=result['survivedTwoNights']
                row['tenNightSurvivals']+=result['survivedNights']==10
                row['survivedNights'].append(result['survivedNights'])
                row['scores'].append(score(result))
                row['invalidCommands']+=result['invalidCommands']
                row['foreignOnlyShots']+=result['foreignOnlyShots']
                row['summonsUsed']+=len(result.get('summons',[]))
    for row in rows.values():
        row['winRate']=row['wins']/row['fixtures']
        row['meanSurvivedNights']=statistics.mean(row['survivedNights'])
        row['meanScore']=statistics.mean(row['scores'])
        row['worstProfilePointsRate']=min(statistics.mean(v)/3 for v in row['profilePoints'].values())
        del row['survivedNights'];del row['scores']
    return rows


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage',choices=('round1','round2','round3','holdout'),required=True)
    args=parser.parse_args()
    os.environ.pop('COMPETITION_ROCKET_POLICY',None)
    config=json.loads((ROOT/'lab/league.json').read_text())
    names=('baseline','alpha','beta','gamma')
    base=ROOT/'lab/league'
    archive=args.stage if args.stage in ('round1','round2') else ''
    paths={name:base/name/(archive if name!='baseline' else '') for name in names}
    for path in paths.values():
        if not (path/'brain.py').is_file():
            raise SystemExit('Missing candidate: '+str(path))
    if args.stage=='holdout':
        development=json.loads((base/'round3-results.json').read_text())
        selected=development['selected']
        # Require exact candidates and judge that generated the selection.
        assert development['sourceHashes']==source_hashes(paths),'Candidate changed after selection'
        pairs=[(selected,name) for name in names if name!=selected]
        seeds=config['holdoutSeeds']
    else:
        pairs=list(combinations(names,2))
        seeds=config['developmentSeeds'][:1] if args.stage=='round1' else config['developmentSeeds']
        selected=None
    hashes=source_hashes(paths)
    started=time.monotonic()
    report={'stage':args.stage,'spec':config,'sourceHashes':hashes,'fixtures':[],
            'selected':selected,'complete':False}
    output=base/(args.stage+'-results.json')
    def save():
        assert hashes==source_hashes(paths),'Judge or frozen policy changed during tournament'
        report['elapsedSeconds']=round(time.monotonic()-started,2)
        output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    for first,second in pairs:
        for seed in seeds:
            for profile in config['profiles']:
                fixture={'players':[first,second],'seed':seed,'profile':profile['name'],'halves':[]}
                for seat in (0,1):
                    bots={name:load_bot(paths[name],args.stage+'_'+str(len(report['fixtures']))+'_'+str(seat)+'_'+name)
                          for name in (first,second)}
                    game=Arena(seed,profile['wave'],profile['priority'],config['nights'],commerce=True)
                    result=game.run({TEAMS[seat]:bots[first],TEAMS[1-seat]:bots[second]})
                    values=[result[TEAMS[seat]],result[TEAMS[1-seat]]]
                    fixture['halves'].append({'firstSeat':TEAMS[seat],'results':values,
                        'scores':[score(v) for v in values], 'outcome':half_winner(*values)})
                fixture['outcome']=fixture_winner(fixture['halves'])
                report['fixtures'].append(fixture);save()
                print(json.dumps({'fixture':len(report['fixtures']),'players':[first,second],
                    'seed':seed,'profile':profile['name'],'outcome':fixture['outcome'],
                    'nights':[[v['survivedNights'] for v in h['results']] for h in fixture['halves']],
                    'scores':[h['scores'] for h in fixture['halves']]},ensure_ascii=False),flush=True)
    report['table']=table(report['fixtures'])
    if args.stage!='holdout':
        report['selected']=max(names,key=lambda name:tuple(report['table'][name][key] for key in
            ('points','worstProfilePointsRate','meanSurvivedNights','meanScore')))
    else:
        direct=[f for f in report['fixtures'] if 'baseline' in f['players']]
        # Holdout pairs put the previously selected policy first. A failed gate
        # cannot choose a different challenger using these held-out outcomes.
        wins=sum(f['outcome']==1 for f in direct)
        losses=sum(f['outcome']==-1 for f in direct)
        survival=[sum(h['results'][i]['survivedTwoNights'] for f in direct for h in f['halves']) for i in (0,1)]
        passed=(selected!='baseline' and wins>losses and survival[0]>=survival[1]
                and report['table'][selected]['invalidCommands']==0)
        report['promotion']={'passed':passed,'candidate':selected,
            'promoted':selected if passed else 'baseline','baselineFixtures':len(direct),
            'winsAgainstBaseline':wins,'lossesAgainstBaseline':losses,
            'candidateAndBaselineTwoNightSurvivals':survival}
    report['complete']=True;save()
    print(json.dumps({'selected':report['selected'],'table':report['table'],
                      'elapsedSeconds':report['elapsedSeconds']},ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':
    main()
