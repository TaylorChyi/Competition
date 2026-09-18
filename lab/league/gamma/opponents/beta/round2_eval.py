import json
from lab.arena import Arena
from lab.league.beta.brain import decide
from lab.league.beta.round1.brain import decide as prior
for seed in (22001,22002):
 for priority in ('nearest','advance'):
  for name,policy in [('round1',prior),('round2',decide)]:
   a=Arena(seed,wave='heavy',priority=priority,nights=10,commerce=True)
   r=a.run({'challenger':policy,'defender':prior})
   print(json.dumps({'seed':seed,'priority':priority,'policy':name,'result':r}),flush=True)
