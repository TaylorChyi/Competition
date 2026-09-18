import json,sys
from functools import partial
from lab.arena import Arena
from lab.league.beta.brain import decide
from agent.brain import decide as baseline
loads=[('railgun','railgun','railgun'),('rocket','railgun','railgun'),('rocket','rocket','railgun'),('rocket','rocket','rocket')]
for load in loads:
 a=Arena(22001,wave='heavy',priority='nearest',nights=10,commerce=True)
 r=a.run({'challenger':partial(decide,loadout=load),'defender':baseline})
 print(json.dumps({'load':load,'result':r}),flush=True)
