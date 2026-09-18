import json,sys
from pathlib import Path
from lab.arena import Arena,TEAMS
from .brain import decide
from .protocol import Turn,distance
from .fire_control import POWER
from lab.tournament.round05.alpha.brain import decide as parent
label=sys.argv[1] if len(sys.argv)>1 else 'baseline'
out=Path(__file__).parent
for seed,priority in [(22000,'nearest'),(22001,'operators'),(22002,'advance')]:
 for seat in (0,1):
  trace=[]
  def observed(payload):
   commands=decide(payload);turn=Turn.load(payload);base=turn.station()
   if not turn.is_day or turn.round_no%130 in (1,70):
    trace.append({'round':turn.round_no,'gold':turn.gold,'base':None if not base else [base.health,base.level],
     'roles':[[u.unit_id,u.kind,u.pos.x,u.pos.y,u.health,list(u.backpack)] for u in turn.controllable()],
     'guns':[[u.unit_id,u.pos.x,u.pos.y,u.health,u.level,u.cooldown] for u in turn.weapons()],
     'pressure':sum(POWER.get(r.kind,5) for r in turn.incoming_robots() if base and min(distance(r.pos,p) for p in turn.footprint(base))<=3),
     'robots':[[r.robot_id,r.kind,r.pos.x,r.pos.y,r.health] for r in turn.incoming_robots()], 'commands':commands})
   return commands
  a=Arena(seed,'field',priority,10,True);res=a.run({TEAMS[seat]:observed,TEAMS[1-seat]:parent})
  (out/(label+'-'+str(seed)+'-'+str(seat)+'.json')).write_text(json.dumps(trace))
  print(json.dumps({'seed':seed,'mode':priority,'seat':seat,'own':res[TEAMS[seat]]}),flush=True)
