import json
from lab.arena import Arena,TEAMS
from lab.tournament.round01.beta.brain import decide
from lab.tournament.round01.beta import fire_control
from lab.tournament.base.brain import decide as baseline
for weight in (0,2,6):
 fire_control.KILL_REWARD=weight
 for seed,priority in [(22001,'operators'),(22002,'advance')]:
  a=Arena(seed,'field',priority,10,True);r=a.run({'challenger':decide,'defender':baseline})
  print(json.dumps({'weight':weight,'seed':seed,'priority':priority,'result':r}),flush=True)
