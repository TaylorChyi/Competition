import json
from pathlib import Path
from lab.arena import Arena,ROBOT_STATS
from lab.survival.iteration07.alpha.brain import decide as rocket
from lab.tournament.round09.beta.brain import decide as parent
from lab.tournament.round05.alpha.brain import decide as background
class Trace(Arena):
 def __init__(self,*a,**kw):super().__init__(*a,**kw);self.trace=[]
 def settle(self,commands):
  super().settle(commands)
  if self.number>=650 or self.number%130 in (0,70):
   self.trace.append({'round':self.number,'gold':self.gold['defender'],'commands':commands['defender'],
    'units':[{'id':p.uid,'kind':p.kind,'hp':p.hp,'level':p.level,'pos':[p.pos.x,p.pos.y],'backpack':list(p.backpack)} for p in self.pieces if p.team=='defender' and p.kind not in ROBOT_STATS],
    'incoming':[{'id':p.uid,'kind':p.kind,'hp':p.hp,'pos':[p.pos.x,p.pos.y]} for p in self.pieces if p.team=='defender' and p.kind in ROBOT_STATS and p.hp>0]})
out={}
for name,policy in (('one_front_first',rocket),):
 a=Trace(46003,'field','nearest',10,commerce=True)
 r=a.run({'defender':policy,'challenger':background})['defender']
 out[name]={'result':r,'trace':a.trace}
 print(name,r['survivalRounds'],r['nightHp'],r['upgrades'],flush=True)
Path('lab/survival/iteration07/alpha/fixed-counterfactual.json').write_text(json.dumps(out,indent=2))
