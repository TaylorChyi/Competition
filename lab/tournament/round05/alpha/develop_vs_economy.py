import json
from lab.arena import Arena
from lab.tournament.round05.alpha.brain import decide
from lab.tournament.round05.gamma.brain import decide as parent
from tools.run_league import score,half_winner
out=[]
for seed,mode in ((22001,'operators'),(22002,'advance'),(28002,'advance')):
 for seat in (0,1):
  sides=('challenger','defender') if not seat else ('defender','challenger')
  r=Arena(seed,'field',mode,10,commerce=True).run({sides[0]:decide,sides[1]:parent})
  out.append({'seed':seed,'mode':mode,'alphaSeat':sides[0],'results':r,'outcome':half_winner(r[sides[0]],r[sides[1]])})
  print(seed,mode,seat,[(score(r[k]),r[k]['survivalRounds'],r[k]['income'],r[k]['invalidCommands'],r[k]['nightOperators']) for k in sides],flush=True)
open('lab/tournament/round05/alpha/combo-vs-economy.json','w').write(json.dumps(out,indent=2))
