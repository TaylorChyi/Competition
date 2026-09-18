import json
from collections import Counter
from lab.arena import Arena
from lab.league.beta.brain import decide
from lab.league.beta.round1.brain import decide as prior
for seed,priority in [(22001,'advance'),(22002,'nearest')]:
 actions=Counter()
 def policy(obs):
  out=decide(obs)
  for cmd in out.values():
   if cmd['action'] in ('use','buy','build'):
    actions[(cmd['action'],cmd.get('name',''))]+=cmd.get('num',1)
  return out
 a=Arena(seed,wave='heavy',priority=priority,nights=10,commerce=True)
 result=a.run({'challenger':policy,'defender':prior})
 print(json.dumps({'seed':seed,'priority':priority,'actions':{str(k):v for k,v in actions.items()},'result':result}),flush=True)
