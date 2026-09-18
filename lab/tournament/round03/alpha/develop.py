import json
from lab.arena import Arena
from lab.tournament.round03.alpha.brain import decide
from lab.tournament.round02.alpha.brain import decide as parent
from tools.run_league import half_winner,score
results=[]
for seed,mode in ((22001,'operators'),(22002,'advance')):
 for seat in (0,1):
  keys=('challenger','defender') if seat==0 else ('defender','challenger')
  r=Arena(seed,'field',mode,10,commerce=True).run({keys[0]:decide,keys[1]:parent})
  results.append({'seed':seed,'mode':mode,'seat':seat,'results':r,'outcome':half_winner(r[keys[0]],r[keys[1]])})
  print(seed,mode,seat,[(score(r[k]),r[k]['survivalRounds'],r[k]['income'],r[k]['invalidCommands'],r[k]['upgrades']) for k in keys],flush=True)
open('lab/tournament/round03/alpha/combined.json','w').write(json.dumps(results,indent=2))
