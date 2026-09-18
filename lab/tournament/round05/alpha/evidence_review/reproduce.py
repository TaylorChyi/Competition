"""Reproduce historical economy-only opponent without mutable Gamma imports.

Run from repository root with PYTHONPATH=CoreGeek/src:.
Writes only evidence_review outputs; preserves historical JSON and scripts.
"""
import hashlib
import json
from pathlib import Path
from lab.arena import Arena
from lab.tournament.round05.alpha.brain import decide
from lab.tournament.round05.gamma.rejected_economy.brain import decide as opponent
from tools.run_league import half_winner

HERE = Path(__file__).resolve().parent
OWNER = HERE.parent

def without_timing(value):
    if isinstance(value, dict):
        return {k: without_timing(v) for k, v in value.items() if k != 'p95DecisionMs'}
    if isinstance(value, list):
        return [without_timing(v) for v in value]
    return value


def differences(old, new, path=''):
    if type(old) is not type(new):
        return [{'path': path, 'old': old, 'new': new}]
    if isinstance(old, dict):
        result=[]
        for k in sorted(old.keys() | new.keys()):
            if k not in old or k not in new:
                result.append({'path':path+'/'+k,'old':old.get(k),'new':new.get(k)})
            else:
                result.extend(differences(old[k],new[k],path+'/'+k))
        return result
    if isinstance(old,list):
        if len(old)!=len(new):
            return [{'path':path,'old_length':len(old),'new_length':len(new)}]
        return [d for i,(a,b) in enumerate(zip(old,new)) for d in differences(a,b,path+'/'+str(i))]
    return [] if old==new else [{'path':path,'old':old,'new':new}]

historical=json.loads((OWNER/'combo-vs-economy.json').read_text())
records=[]
checks=[]
for old in historical:
    seat=old['alphaSeat']
    other='defender' if seat=='challenger' else 'challenger'
    results=Arena(old['seed'],'field',old['mode'],10,commerce=True).run({seat:decide,other:opponent})
    new={'seed':old['seed'],'mode':old['mode'],'alphaSeat':seat,'results':results,
         'outcome':half_winner(results[seat],results[other])}
    records.append(new)
    diff=differences(without_timing(old),without_timing(new))
    check={'seed':old['seed'],'mode':old['mode'],'alphaSeat':seat,'exactExcludingP95':not diff,'differences':diff}
    checks.append(check)
    print(json.dumps(check),flush=True)
(HERE/'reproduced.json').write_text(json.dumps(records,indent=2))
report={'opponent':'lab.tournament.round05.gamma.rejected_economy.brain.decide',
        'excludedFields':['p95DecisionMs'],'allExact':all(c['exactExcludingP95'] for c in checks),
        'historicalSha256':hashlib.sha256((OWNER/'combo-vs-economy.json').read_bytes()).hexdigest(),
        'checks':checks}
(HERE/'comparison.json').write_text(json.dumps(report,indent=2))
