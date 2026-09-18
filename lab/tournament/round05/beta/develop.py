import json
from lab.arena import Arena,TEAMS
from .brain import decide as combined
from .economy_only.brain import decide as economy
from lab.tournament.round04.gamma.brain import decide as parent
for label,first,second in [('economy_parent',economy,parent),('combined_parent',combined,parent),('combined_economy',combined,economy)]:
 for seed,priority in [(22001,'operators'),(22002,'advance'),(26006,'nearest')]:
  for seat in (0,1):
   a=Arena(seed,'field',priority,10,True);r=a.run({TEAMS[seat]:first,TEAMS[1-seat]:second})
   print(json.dumps({'variant':label,'seed':seed,'priority':priority,'seat':seat,'candidate':r[TEAMS[seat]],'opponent':r[TEAMS[1-seat]]}),flush=True)
