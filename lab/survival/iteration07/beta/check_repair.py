from dataclasses import replace
from unittest.mock import patch
from .adjacent_repair import brain as b
from .adjacent_repair.protocol import Turn,Pos

def u(i,k,x,y,h=1000,**kw):return dict(id=i,roleType=k,pos={'x':x,'y':y},health=h,level=1,**kw)
p={'roundNo':140,'mapInfo':{'width':41,'height':32,'zones':[]},'teamOur':{'type':'challenger','goldNum':0,'roles':[u(1,'worker',9,19,220,backpack=['stone']),u(2,'station',9,22,1500)]},'teamEnemy':{'roles':[]},'robot':{'roles':[]}}
t=Turn.load(p);order=b._wall_order(t)
p['teamOur']['roles'] += [u(10+i,'wall',q.x,q.y,100 if q in (Pos(10,19),Pos(12,19)) else 1000) for i,q in enumerate(order)]
t=replace(Turn.load(p),shop_prices={'Medicine':10})
def selected(turn):
 chosen=[]
 with patch.object(b,'_build_or_walk',side_effect=lambda *args:chosen.append(args[2])):
  b._worker_day(turn,turn.workers()[0],[],[],[],set(),{},b.TOWER_LOADOUT,True,19)
 return chosen
assert selected(t)==[Pos(10,19)]
# A missing front cell remains more important than adjacent repairs.
t=replace(t,ours=tuple(x for x in t.ours if x.pos!=Pos(12,19)))
assert selected(t)==[Pos(12,19)]
print('adjacent repair trigger and missing-wall priority passed')
