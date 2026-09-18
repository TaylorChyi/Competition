import json
from pathlib import Path
from lab.arena import Arena,ROBOT_STATS
from lab.survival.iteration08.alpha.brain import decide as rocket
from lab.tournament.round09.beta.brain import decide as parent
from lab.tournament.round05.alpha.brain import decide as background
import sys
seed=int(sys.argv[1]);seat=sys.argv[2]
class Trace(Arena):
 def __init__(self,*a,**kw):super().__init__(*a,**kw);self.trace=[]
 def settle(self,commands):
  super().settle(commands)
  if self.number>=650 or self.number%130 in (0,70):
   self.trace.append({'round':self.number,'gold':self.gold[seat],'commands':commands[seat],
    'units':[{'id':p.uid,'kind':p.kind,'hp':p.hp,'level':p.level,'pos':[p.pos.x,p.pos.y],'backpack':list(p.backpack)} for p in self.pieces if p.team==seat and p.kind not in ROBOT_STATS],
    'incoming':[{'id':p.uid,'kind':p.kind,'hp':p.hp,'pos':[p.pos.x,p.pos.y]} for p in self.pieces if p.team==seat and p.kind in ROBOT_STATS and p.hp>0]})
out={}
for name,policy in (('front_voucher_first',rocket),):
 a=Trace(seed,'field','nearest',10,commerce=True)
 r=a.run({seat:policy,('challenger' if seat=='defender' else 'defender'):background})[seat]
 out[name]={'result':r,'trace':a.trace}
 print(name,r['survivalRounds'],r['nightHp'],r['upgrades'],flush=True)
Path(f'lab/survival/iteration08/alpha/fixed-trace-{seed}-{seat}.json').write_text(json.dumps(out,indent=2))
