import json
from pathlib import Path
from lab.arena import Arena,ROBOT_STATS
from lab.survival.iteration06.alpha.brain import decide
from lab.tournament.round05.alpha.brain import decide as background
class Trace(Arena):
 def __init__(self,*a,**kw):super().__init__(*a,**kw);self.trace=[]
 def settle(self,commands):
  super().settle(commands)
  if self.number%130 not in (0,70):return
  self.trace.append({'round':self.number,'gold':self.gold['challenger'],
   'units':[{'id':p.uid,'kind':p.kind,'hp':p.hp,'level':p.level,'pos':[p.pos.x,p.pos.y],'backpack':list(p.backpack)} for p in self.pieces if p.team=='challenger' and p.kind not in ROBOT_STATS and p.hp>0]})
out={}
for seed in (36002,36007):
 a=Trace(seed,'field','nearest',10,commerce=True)
 r=a.run({'challenger':decide,'defender':background})['challenger']
 out[str(seed)]={'result':r,'trace':a.trace}
 print(seed,r['survivalRounds'],flush=True)
Path('lab/survival/iteration06/alpha/revealed-trace.json').write_text(json.dumps(out,indent=2))
