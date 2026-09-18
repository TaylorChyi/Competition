from unittest.mock import patch
from .stoploss.brain import decide
from .stoploss.protocol import Turn,Pos
from .stoploss.guard import safer_step

def u(i,k,x,y,h=220):return dict(id=i,roleType=k,pos={'x':x,'y':y},health=h,level=1)
def payload(hp):return {'roundNo':71,'mapInfo':{'width':41,'height':32,'zones':[]},'teamOur':{'type':'challenger','goldNum':0,'roles':[u(1,'worker',5,5),u(2,'railgun',6,5,1000),u(3,'station',4,4,hp)]},'teamEnemy':{'roles':[]},'robot':{'roles':[]}}
# Emergency is the inherited exact 75% strict boundary, not a new tuned number.
for hp,expect in [(1124,False),(1125,True)]:
 seen=[]
 def guard(*args,**kw):seen.append(kw['anticipate']);return None
 with patch('lab.tournament.round05.beta.stoploss.brain.safer_step',side_effect=guard),patch('lab.tournament.round05.beta.stoploss.brain.joint_positions',return_value=None) as joint:
  decide(payload(hp))
 assert seen==[expect],seen
 assert joint.call_count==int(expect)
# Disabling anticipation retains best-effort escape under immediate mortality.
p=payload(1000);p['teamOur']['roles'][0]=u(1,'worker',6,5,20);p['teamOur']['roles'][1]=u(2,'railgun',5,5,1000)
t=Turn.load(p)
def danger(turn,pos,**kw):return 100 if pos==Pos(6,5) else 0 if pos.x==7 else 50
with patch('lab.tournament.round05.beta.stoploss.guard.exposure',side_effect=danger):
 step=safer_step(t,t.controllable()[0],t.weapons()[0],set(),anticipate=False)
assert step and step.x==7
print('base emergency suppresses only new anticipatory planning; original lethal escape remains')
