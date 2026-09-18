import json
from functools import partial
from lab.arena import Arena
from lab.league.beta.brain import decide
from agent.brain import decide as baseline
for fortify in (0,8,12):
 a=Arena(22002,wave='heavy',priority='advance',nights=10,commerce=True)
 r=a.run({'challenger':partial(decide,fortify=fortify),'defender':baseline})
 print(json.dumps({'fortify':fortify,'result':r}),flush=True)
