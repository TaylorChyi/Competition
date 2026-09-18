import importlib,json
from collections import Counter
from pathlib import Path
from lab.arena import Arena,TEAMS
from lab.tournament.round05.alpha.brain import decide as background
out=Path(__file__).parent
for label,package in [('parent','lab.survival.iteration07.beta'),('adjacent_repair','lab.survival.iteration07.beta.adjacent_repair')]:
 bot=importlib.import_module(package+'.brain')
 for seed in (22000,22001,22002,26006):
  for seat in (0,1):
   team=TEAMS[seat];labor=Counter();snapshots=[];full_round=None;maxwalls=0;wall_damage=Counter();wall_builds=Counter()
   original_build,original_mine=bot._build_or_walk,bot._mine
   def build(turn,role,target,name,claimed,commands):
    original_build(turn,role,target,name,claimed,commands)
    if name=='wall' and commands.get(role.unit_id,{}).get('action')=='move':labor['wall_travel_moves']+=1
   def mine(turn,role,claimed,commands):
    result=original_mine(turn,role,claimed,commands)
    if commands.get(role.unit_id,{}).get('action')=='move':labor['dedicated_stone_travel_moves']+=1
    return result
   bot._build_or_walk=build;bot._mine=mine
   def policy(payload):
    commands=bot.decide(payload);turn=bot.Turn.load(payload)
    for c in commands.values():
     if c.get('action')=='build' and c.get('name')=='wall':labor['wall_build_commands']+=1
     if c.get('action')=='collect' and c.get('targetPos'):
      pos=bot.Pos.load(c['targetPos'][0])
      if turn.zones.get(pos)=='stone':labor['all_stone_collect_commands']+=1
    return commands
   class ObservedArena(Arena):
    def settle(self,commands):
     global full_round,maxwalls
     before={p.uid:(p.pos,p.hp) for p in self.pieces if p.team==team and p.kind=='wall' and p.hp>0}
     super().settle(commands)
     if (self.number-1)%130>=70:
      for p in self.pieces:
       if p.uid in before:
        pos,hp=before[p.uid];wall_damage[f'{pos.x},{pos.y}']+=max(0,hp-p.hp)
     for p in self.pieces:
      if p.team==team and p.kind=='wall' and p.hp>0 and p.uid not in before:
       wall_builds[f'{p.pos.x},{p.pos.y}']+=1
     own=[p for p in self.pieces if p.team==team and p.kind not in ('smallRobot','middleRobot','largeRobot','bossRobot')]
     walls=[p for p in own if p.kind=='wall' and p.hp>0]
     maxwalls=max(maxwalls,len(walls))
     if len(walls)==12 and full_round is None:full_round=self.number
     if self.number%130==0:
      snapshots.append({'night':self.number//130,'cash':self.gold[team],'wallCount':len(walls),'wallHP':sum(p.hp for p in walls),'baseHP':self.base(team).hp,'roles':[[p.uid,p.hp,p.pos.x,p.pos.y] for p in own if p.kind in ('worker','pioneer')],'equipment':[[p.uid,p.kind,p.level,p.hp] for p in own if p.kind in ('station','railgun','rocket','gatling')],'labor':dict(labor),'income':self.metrics[team]['income']})
   a=ObservedArena(seed,'field','nearest',10,True);res=a.run({team:policy,TEAMS[1-seat]:background})[team]
   bot._build_or_walk,bot._mine=original_build,original_mine
   record={'variant':label,'seed':seed,'seat':seat,'result':res,'nights':snapshots,'labor':dict(labor),'firstFullRingRound':full_round,'maxWallCount':maxwalls,'wallDamage':dict(wall_damage),'wallBuilds':dict(wall_builds),'firstGunUpgrade':next((x[0] for x in res['upgrades'] if x[1] in ('railgun','rocket','gatling')),None)}
   print(json.dumps(record),flush=True)
