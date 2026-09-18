import json
from lab.arena import Arena
from . import brain
from .guard import exposure
from lab.tournament.round01.alpha.brain import decide as parent
original=brain.safer_step
events=[]
def tracked(turn,role,tower,claimed,**kwargs):
 step=original(turn,role,tower,claimed,**kwargs)
 if not turn.is_day and step is not None and role.health>max(2*exposure(turn,role.pos,approaching=False),3*exposure(turn,role.pos)):
  events.append({'round':turn.round_no,'health':role.health,'from':role.pos.dump(),'to':step.dump()})
 return step
brain.safer_step=tracked
result=Arena(22002,'field','advance',10,True).run({'challenger':brain.decide,'defender':parent})
print(json.dumps({'events':events,'result':result}))
