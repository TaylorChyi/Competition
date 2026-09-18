import json
from lab.arena import Arena
from lab.league.gamma.brain import decide
from lab.league.gamma.opponents.alpha.brain import decide as alpha
from lab.league.gamma.opponents.beta.brain import decide as beta
out=[]
for name,opponent in [('alpha',alpha),('beta',beta)]:
 for seed,priority in [(22001,'nearest'),(22002,'advance')]:
  a=Arena(seed,wave='heavy',priority=priority,nights=10,commerce=True)
  r=a.run({'challenger':decide,'defender':opponent})
  scores={k:v['killPoints']+sum(10*(i+1) for i,h in enumerate(v['nightHp']) if h>0) for k,v in r.items()}
  out.append({'opponent':name,'seed':seed,'priority':priority,'scores':scores,'results':r})
  print(name,seed,priority,scores,{k:{n:v.get(n) for n in ('survivalRounds','summons','invalidCommands')} for k,v in r.items()},flush=True)
  open('lab/league/gamma/dev-round3.json','w').write(json.dumps(out,indent=2))
