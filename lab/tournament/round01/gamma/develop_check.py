import json
from lab.arena import Arena
from lab.tournament.round01.gamma.brain import decide
from lab.tournament.base.brain import decide as baseline
rows=[]
for seed,priority in [(22001,'operators'),(22002,'advance')]:
 for seat in ('challenger','defender'):
  a=Arena(seed,wave='field',priority=priority,nights=10,commerce=True)
  other='defender' if seat=='challenger' else 'challenger'
  r=a.run({seat:decide,other:baseline})
  def summary(v):
   return {'score':v['killPoints']+sum(10*(i+1) for i,h in enumerate(v['nightHp']) if h>0),'rounds':v['survivalRounds'],'invalid':v['invalidCommands'],'nightHp':v['nightHp']}
  x={'seed':seed,'priority':priority,'seat':seat,'gamma':summary(r[seat]),'base':summary(r[other])}
  rows.append(x);print(x,flush=True)
open('lab/tournament/round01/gamma/development.json','w').write(json.dumps(rows,indent=2))
