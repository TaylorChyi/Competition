#!/usr/bin/env python3
"""Freeze a long-match candidate on development seeds, then run untouched seeds."""
from functools import partial
import hashlib
import json
import os
from pathlib import Path
import statistics
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'CoreGeek/src')]
from agent.brain import decide
from lab.arena import Arena, TEAMS
from tools.run_selfplay import previous_bot


def summary(records, field='ours'):
    values=[r[field] for r in records]
    return {'campOutcomes':len(values),
            'twoNightSurvival':statistics.mean(v['survivedTwoNights'] for v in values),
            'tenNightSurvival':statistics.mean(v['survivedNights']==10 for v in values),
            'meanSurvivedNights':statistics.mean(v['survivedNights'] for v in values),
            'minSurvivedNights':min(v['survivedNights'] for v in values),
            'meanFinalBaseHp':statistics.mean(v['nightHp'][-1] for v in values),
            'invalidCommands':sum(v['invalidCommands'] for v in values),
            'resourceConflicts':sum(v['resourceConflicts'] for v in values),
            'invalidExcludingResourceConflicts':sum(v['invalidCommands']-v['resourceConflicts'] for v in values),
            'foreignOnlyShots':sum(v['foreignOnlyShots'] for v in values),
            'p95DecisionMsMax':max(v['p95DecisionMs'] for v in values)}


def main():
    os.environ.pop('COMPETITION_ROCKET_POLICY',None)
    spec=json.loads((ROOT/'lab/survival.json').read_text())
    sources=[ROOT/'lab/arena.py',ROOT/'lab/survival.json',Path(__file__),
             *sorted((ROOT/'CoreGeek/src/agent').glob('*.py'))]
    fingerprint=lambda:{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    hashes=fingerprint();started=time.monotonic();count=0
    report={'spec':spec,'sourceHashes':hashes,'training':{},'holdout':[],'selfplay':[]}
    output=ROOT/'lab/survival-results.json'
    def save():
        assert hashes==fingerprint(),'Policy or simulator changed while experiment was running'
        report.update(matches=count,elapsedSeconds=round(time.monotonic()-started,2))
        output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    with previous_bot(spec['baselineCommit']) as old:
        def play(name,config,seed,profile,seat,selfplay=False):
            nonlocal count
            assert count<spec['maxMatches']
            bot=partial(decide,**config);team=TEAMS[seat]
            policies=dict.fromkeys(TEAMS,bot if selfplay else old);policies[team]=bot
            g=Arena(seed,profile['wave'],profile['priority'],spec['nights'],commerce=True)
            result=g.run(policies);count+=1
            row={'candidate':name,'seed':seed,'profile':profile['name'],'seat':team,
                 'ours':result[team],'opponent':result[TEAMS[1-seat]],'selfplay':selfplay}
            print(json.dumps({'match':count,'candidate':name,'seed':seed,'profile':profile['name'],
                  'seat':team,'selfplay':selfplay,'ourHp':result[team]['nightHp'],
                  'opponentHp':result[TEAMS[1-seat]]['nightHp']},ensure_ascii=False),flush=True)
            return row
        for name,config in spec['candidates'].items():
            report['training'][name]=[play(name,config,seed,profile,seat)
                 for seed in spec['trainSeeds'] for profile in spec['profiles'] for seat in (0,1)]
            save()
        report['trainingSummary']={n:summary(v) for n,v in report['training'].items()}
        chosen=max(spec['candidates'],key=lambda n:tuple(report['trainingSummary'][n][k] for k in spec['selection']))
        config=spec['candidates'][chosen]
        report.update(selected=chosen,selectedPolicy=config,stage='holdout');save()
        print('FROZEN '+chosen+' '+json.dumps(config),flush=True)
        for seed in spec['holdoutSeeds']:
            for profile in spec['profiles']:
                for seat in (0,1):
                    report['holdout'].append(play(chosen,config,seed,profile,seat));save()
                report['selfplay'].append(play(chosen,config,seed,profile,0,True));save()
        report['holdoutSummary']={p['name']:{'candidate':summary([r for r in report['holdout'] if r['profile']==p['name']]),
           'previousRelease':summary([r for r in report['holdout'] if r['profile']==p['name']],'opponent')}
           for p in spec['profiles']}
        report['selfplaySummary']={p['name']:summary([dict(r,ours=r[field]) for r in report['selfplay']
          if r['profile']==p['name'] for field in ('ours','opponent')]) for p in spec['profiles']}
        report['stage']='complete';save()
        print(json.dumps({k:report[k] for k in ('selected','matches','trainingSummary','holdoutSummary','selfplaySummary')},indent=2))


if __name__=='__main__':
    main()
