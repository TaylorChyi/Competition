import json
from lab.arena import Arena,TEAMS
from lab.league.beta.brain import decide as current
from lab.league.beta.trial3b.brain import decide as ordered
from lab.league.baseline.brain import decide as baseline
for name,policy in [('3b',ordered),('3c',current)]:
 for seed,priority in [(22001,'nearest'),(22002,'nearest'),(22001,'advance')]:
  for seat in (0,1):
   a=Arena(seed,'heavy',priority,10,True);r=a.run({TEAMS[seat]:policy,TEAMS[1-seat]:baseline})
   print(json.dumps({'variant':name,'seed':seed,'priority':priority,'seat':seat,'beta':r[TEAMS[seat]],'other':r[TEAMS[1-seat]]}),flush=True)
