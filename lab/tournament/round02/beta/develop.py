import json
from lab.arena import Arena,TEAMS
from lab.tournament.round02.beta.brain import decide
from lab.tournament.round01.alpha.brain import decide as parent
for seed,priority in [(22001,'nearest'),(22001,'operators'),(22002,'advance')]:
 for seat in (0,1):
  a=Arena(seed,'field',priority,10,True);r=a.run({TEAMS[seat]:decide,TEAMS[1-seat]:parent})
  print(json.dumps({'seed':seed,'priority':priority,'seat':seat,'beta':r[TEAMS[seat]],'parent':r[TEAMS[1-seat]]}),flush=True)
