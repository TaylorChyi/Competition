import json
from lab.arena import Arena,TEAMS
from agent.brain import decide as baseline
from lab.field.beta.brain import decide
for priority in ('nearest','operators','advance'):
 for seat in (0,1):
  arena=Arena(22001,'field',priority,2,True)
  r=arena.run({TEAMS[seat]:decide,TEAMS[1-seat]:baseline})
  print(json.dumps({'priority':priority,'seat':seat,'beta':r[TEAMS[seat]],'baseline':r[TEAMS[1-seat]]}),flush=True)
