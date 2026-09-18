#!/usr/bin/env python3
"""Ten paired fixtures per pair; tied leaders play five-fixture tie-breaks."""
import argparse
from fractions import Fraction
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


def hashes(paths):
    files={ROOT/'lab/arena.py',ROOT/'lab/night_sim.py',ROOT/'lab/tournament/rules.json',
           Path(__file__),ROOT/'tools/run_league.py',ROOT/'CoreGeek/src/agent/protocol.py',
           ROOT/'CoreGeek/src/agent/targeting.py'}
    for path in paths.values():
        files.update(path.glob('*.py'))
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}


def leaders(fixtures,names):
    rows=table(fixtures)
    rates={n:Fraction(rows[n]['wins'],rows[n]['fixtures']) for n in names}
    best=max(rates.values())
    return [n for n in names if rates[n]==best]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--round',type=int,required=True)
    args=parser.parse_args()
    assert args.round>0
    os.environ.pop('COMPETITION_ROCKET_POLICY',None)
    rules=json.loads((ROOT/'lab/tournament/rules.json').read_text())
    directory=ROOT/'lab/tournament'/f'round{args.round:02d}'
    names=rules['agents']
    paths={name:directory/name for name in names}
    for path in paths.values():
        assert (path/'brain.py').is_file(),f'Missing candidate {path}'
    source_hashes=hashes(paths)
    output=directory/'results.json'
    if output.exists():
        report=json.loads(output.read_text())
        assert report['sourceHashes']==source_hashes,'Frozen sources changed; preserve the old round before restarting'
        if report['complete']:
            print(json.dumps({'champion':report['champion'],'table':report['table']},ensure_ascii=False,indent=2));return
    else:
        report={'round':args.round,'rules':rules,'sourceHashes':source_hashes,'stages':[],
                'complete':False,'champion':None,'elapsedSeconds':0}
    started=time.monotonic();previous_elapsed=report['elapsedSeconds']
    def save():
        assert hashes(paths)==source_hashes,'Candidate or judge changed during the round'
        report['elapsedSeconds']=round(previous_elapsed+time.monotonic()-started,2)
        output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    eligible=names
    stage_index=0
    while len(eligible)>1:
        count=rules['fixturesPerPair'] if stage_index==0 else rules['overtimeFixturesPerPair']
        if len(report['stages'])<=stage_index:
            report['stages'].append({'number':stage_index,'kind':'main' if stage_index==0 else 'overtime',
                                     'players':eligible,'fixtures':[],'complete':False})
        stage=report['stages'][stage_index]
        assert stage['players']==eligible
        cases=[{'seed':25000+args.round*1000+stage_index*20+i,
                'profile':'field-'+('nearest','operators','advance')[i%3],
                'priority':('nearest','operators','advance')[i%3]} for i in range(count)]
        index=0
        for first,second in combinations(eligible,2):
            for case in cases:
                index+=1
                if index<=len(stage['fixtures']):continue
                fixture={'players':[first,second],'seed':case['seed'],
                         'profile':case['profile'],'halves':[]}
                for seat in (0,1):
                    bots={n:load_bot(paths[n],f'tournament_{args.round}_{stage_index}_{index}_{seat}_{n}')
                          for n in (first,second)}
                    game=Arena(case['seed'],'field',case['priority'],rules['nights'],commerce=True)
                    result=game.run({TEAMS[seat]:bots[first],TEAMS[1-seat]:bots[second]})
                    values=[result[TEAMS[seat]],result[TEAMS[1-seat]]]
                    fixture['halves'].append({'firstSeat':TEAMS[seat],'results':values,
                        'scores':[score(v) for v in values],'outcome':half_winner(*values)})
                fixture['outcome']=fixture_winner(fixture['halves'])
                stage['fixtures'].append(fixture);save()
                print(json.dumps({'round':args.round,'stage':stage_index,'fixture':index,
                    'players':[first,second],'seed':case['seed'],'profile':case['profile'],
                    'outcome':fixture['outcome'],
                    'nights':[[v['survivedNights'] for v in h['results']] for h in fixture['halves']]},ensure_ascii=False),flush=True)
        eligible=leaders(stage['fixtures'],eligible)
        stage.update(table=table(stage['fixtures']),leaders=eligible,complete=True);save()
        stage_index+=1
    report.update(champion=eligible[0],table=report['stages'][0]['table'],complete=True)
    champion_row=report['table'][eligible[0]]
    report['target100Percent']=champion_row['wins']==champion_row['fixtures']
    report['overtimeStages']=len(report['stages'])-1
    save()
    print(json.dumps({'champion':report['champion'],'target100Percent':report['target100Percent'],
                      'table':report['table'],'overtimeStages':report['overtimeStages']},ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':
    main()
