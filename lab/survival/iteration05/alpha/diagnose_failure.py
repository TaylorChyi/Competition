import json,sys
from pathlib import Path
from lab.arena import Arena,ROBOT_STATS
from lab.survival.iteration04.alpha.brain import decide
from lab.survival.iteration03.beta.full_ring_exits.brain import decide as parent
from lab.tournament.round05.alpha.brain import decide as background

class Trace(Arena):
 def __init__(self,*a,**kw):super().__init__(*a,**kw);self.trace=[]
 def settle(self,commands):
  super().settle(commands)
  if self.number>=650 or self.number%130 in (0,70):
   team='challenger'
   self.trace.append({'round':self.number,'gold':self.gold[team],'commands':commands[team],
      'units':[{'id':p.uid,'kind':p.kind,'hp':p.hp,'level':p.level,'pos':[p.pos.x,p.pos.y],'backpack':list(p.backpack)} for p in self.pieces if p.team==team and p.kind not in ROBOT_STATS],
      'incoming':[{'id':p.uid,'kind':p.kind,'hp':p.hp,'pos':[p.pos.x,p.pos.y]} for p in self.pieces if p.team==team and p.kind in ROBOT_STATS and p.hp>0]})

seed=int(sys.argv[1]) if len(sys.argv)>1 else 36007
out={}
for name,policy in (('rocket',decide),('three_rail',parent)):
 a=Trace(seed,'field','nearest',10,commerce=True)
 r=a.run({'challenger':policy,'defender':background})['challenger']
 out[name]={'result':r,'trace':a.trace}
 print(name,r['survivalRounds'],r['nightHp'],r['upgrades'],flush=True)
Path(f'lab/survival/iteration05/alpha/failure-counterfactual-{seed}.json').write_text(json.dumps(out,indent=2))
