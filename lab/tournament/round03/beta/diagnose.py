import json
from lab.arena import Arena
from lab.tournament.round02.alpha.brain import decide as parent
from .protocol import Turn,Pos,distance
from .guard import exposure,joint_positions
from .brain import _tower_pairs
records=[]
def traced(obs):
 t=Turn.load(obs);cmd=parent(obs)
 if 71<=t.round_no<=130:
  danger=[r for r in t.controllable() if 3*exposure(t,r.pos,approaching=False)>=r.health]
  if danger:
   records.append({'round':t.round_no,'danger':[(r.unit_id,r.health,r.pos.dump(),exposure(t,r.pos,approaching=False)) for r in danger],
    'operators':[(r.unit_id,r.health,r.pos.dump()) for r in t.controllable()],
    'incoming':[(r.kind,r.health,r.pos.dump()) for r in t.incoming_robots() if any(distance(r.pos,u.pos)<=4 for u in danger)],
    'parent':cmd,'joint':str(joint_positions(t,_tower_pairs(t),set()))})
 return cmd
r=Arena(26006,'field','nearest',2,True).run({'challenger':parent,'defender':traced})
print(json.dumps({'records':records,'result':r}))
