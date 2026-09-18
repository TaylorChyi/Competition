import json,hashlib
from pathlib import Path
from collections import defaultdict
from lab.arena import Arena
from lab.survival.iteration07.alpha.brain import decide
from lab.survival.iteration07.alpha.protocol import Turn,Pos
from lab.survival.iteration07.alpha.fire_control import ray_hits
from lab.survival.iteration07.alpha.targeting import splash_damage
from lab.tournament.round05.alpha.brain import decide as opponent
out={'judgeSha256':hashlib.sha256(Path('lab/arena.py').read_bytes()).hexdigest(),'halves':[]}
for seed in (22000,22001,22002,26006,36002,36007,46003):
 for seat in (('defender',) if seed==46003 else ('challenger',) if seed in (36002,36007) else ('challenger','defender')):
  waste=defaultdict(lambda:{'incomingRaw':0,'incomingEffective':0,'incomingOverkill':0,'rocketVolleys':[]})
  def measured(payload):
   turn=Turn.load(payload);commands=decide(payload)
   if not turn.is_day:
    allocated=defaultdict(int)
    for tower in turn.weapons():
     cmd=commands.get(str(tower.unit_id),{})
     if cmd.get('action')!='attack':continue
     if tower.kind=='rocket':waste[(turn.round_no-1)//130+1]['rocketVolleys'].append(turn.round_no)
     for target in cmd['targetPos']:
      p=Pos.load(target)
      if tower.kind=='rocket':hits=[(r,splash_damage(p,r.pos)) for r in turn.robots]
      else:
       hits=[];energy=10*tower.level
       for r in ray_hits(tower.pos,p,turn.robots):
        hit=min(energy,r.health);hits.append((r,hit));energy-=hit
        if not energy:break
      for r,hit in hits:allocated[r.robot_id]+=hit
    raw=sum(allocated[r.robot_id] for r in turn.incoming_robots())
    effective=sum(min(r.health,allocated[r.robot_id]) for r in turn.incoming_robots())
    bucket=waste[(turn.round_no-1)//130+1]
    bucket['incomingRaw']+=raw;bucket['incomingEffective']+=effective;bucket['incomingOverkill']+=raw-effective
   return commands
  other='defender' if seat=='challenger' else 'challenger'
  r=Arena(seed,'field','nearest',10,commerce=True).run({seat:measured,other:opponent})[seat]
  out['halves'].append({'seed':seed,'seat':seat,'self':r,'snapshotDamageByNight':dict(waste)})
  print(seed,seat,r['survivalRounds'],r['killPoints'],r['nightHp'][-1],r['invalidCommands'],flush=True)
Path('lab/survival/iteration07/alpha/one_front_first.json').write_text(json.dumps(out,indent=2))
