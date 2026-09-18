import json,sys
from functools import partial
from lab.arena import Arena
from lab.league.beta.brain import decide
from agent.brain import decide as baseline
loads=[('gatling','railgun','railgun'),('gatling','gatling','railgun'),('gatling','gatling','gatling')]
for load in loads:
 a=Arena(22002,wave='heavy',priority='advance',nights=10,commerce=True)
 r=a.run({'challenger':partial(decide,loadout=load),'defender':baseline})
 print(json.dumps({'load':load,'result':r}),flush=True)
