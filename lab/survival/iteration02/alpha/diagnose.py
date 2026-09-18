import json,hashlib
from pathlib import Path
from dataclasses import replace
from lab.arena import Arena
from lab.survival.iteration02.alpha.protocol import Turn,distance
from lab.survival.iteration02.alpha.economy import route
from lab.survival.iteration02.alpha.fire_control import targets
from lab.survival.iteration02.alpha.brain import decide
from lab.tournament.round05.alpha.brain import decide as opponent

out=[]
for seed,mode in ((22000,'nearest'),(22001,'operators'),(22002,'advance')):
 for seat in ('challenger','defender'):
  windows=[];damage=[];budgets=[]
  def measured(payload):
   turn=Turn.load(payload)
   if turn.is_day:
    vouchers=[u for u in turn.controllable() if 'WeaponUpgradeVoucher1' in u.backpack]
    if vouchers:
     budgets.append({'round':turn.round_no,'cash':turn.gold,'baseHP':turn.station().health,
                     'baseLevel':turn.station().level,'carriers':[u.unit_id for u in vouchers]})
    if turn.gold>=25 and vouchers:
     for tower in turn.weapons():
      if tower.kind!='railgun' or tower.level!=1:continue
      builders=[u for u in turn.workers() if distance(u.pos,tower.pos)<=1]
      routes=[route(turn,u,[tower.pos],set()) for u in vouchers]
      paths=[p for p in routes if p is not None]
      daylight=70-(turn.round_no-1)%130
      if builders and paths and min(map(len,paths))+3<=daylight:
       windows.append({'round':turn.round_no,'cash':turn.gold,'tower':tower.unit_id,'towerHP':tower.health,'baseHP':turn.station().health,'baseLevel':turn.station().level,'returnSteps':min(map(len,paths))})
   elif seed==22002 and turn.round_no>=331:
    for gun in turn.weapons():
     if gun.kind!='railgun':continue
     for level in (1,2,3):
      trial=replace(gun,kind='rocket',level=level,attack_range=0)
      reserved={};targets(turn,trial,reserved)
      actual=sum(min(r.health,reserved.get(r.robot_id,0)) for r in turn.incoming_robots())
      damage.append({'round':turn.round_no,'tower':gun.unit_id,'level':level,'burstDamage':actual})
   return decide(payload)
  arena=Arena(seed,'field',mode,10,commerce=True)
  other='defender' if seat=='challenger' else 'challenger'
  result=arena.run({seat:measured,other:opponent})[seat]
  record={'seed':seed,'mode':mode,'seat':seat,'result':result,'conversionWindows':windows,'carriedVoucherBudgets':budgets,'hypotheticalRocketBursts':damage}
  out.append(record)
  print(seed,seat,'survival',result['survivalRounds'],'windows',len(windows),'voucherTurns',len(budgets),flush=True)
Path('lab/survival/iteration02/alpha/diagnosis.json').write_text(json.dumps(out,indent=2))
