import json
from lab.arena import Arena,TEAMS
from lab.league.beta.brain import decide
from lab.league.beta.round2.brain import decide as prior
from lab.league.baseline.brain import decide as baseline
from lab.league.alpha.round2.brain import decide as alpha
for name,op in [('baseline',baseline),('alpha',alpha)]:
 for seat in (0,1):
  a=Arena(22002,'heavy','advance',10,True)
  r=a.run({TEAMS[seat]:decide,TEAMS[1-seat]:op})
  print(json.dumps({'opponent':name,'seat':seat,'beta':r[TEAMS[seat]],'other':r[TEAMS[1-seat]]}),flush=True)
