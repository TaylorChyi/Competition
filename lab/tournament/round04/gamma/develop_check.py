import json
from lab.arena import Arena
from lab.tournament.round04.gamma.brain import decide
from lab.tournament.round03.gamma.brain import decide as champion
rows=[]
for seed,priority in [(22001,'nearest'),(22001,'operators'),(22002,'advance')]:
 for seat in ('challenger','defender'):
  a=Arena(seed,wave='field',priority=priority,nights=10,commerce=True)
  other='defender' if seat=='challenger' else 'challenger'
  r=a.run({seat:decide,other:champion})
  def summary(v):
   return {'score':v['killPoints']+sum(10*(i+1) for i,h in enumerate(v['nightHp']) if h>0),'rounds':v['survivalRounds'],'invalid':v['invalidCommands'],'nightHp':v['nightHp'],'income':v['income'],'shots':v['shots'],'operators':v['nightOperators'],'summons':v.get('summons',[])}
  x={'seed':seed,'priority':priority,'seat':seat,'gamma':summary(r[seat]),'champion':summary(r[other])}
  rows.append(x);print(x,flush=True)
open('lab/tournament/round04/gamma/pressure-development.json','w').write(json.dumps(rows,indent=2))
