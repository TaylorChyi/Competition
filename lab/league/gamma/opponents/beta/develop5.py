import json,sys
from functools import partial
from lab.arena import Arena
from lab.league.beta.brain import decide
from agent.brain import decide as baseline
loads=[('railgun','railgun','railgun'),('rocket','railgun','railgun')]
for load in loads:
 a=Arena(22002,wave='heavy',priority='advance',nights=10,commerce=True)
 r=a.run({'challenger':partial(decide,loadout=load,fortify=0),'defender':baseline})
 print(json.dumps({'load':load,'result':r}),flush=True)
