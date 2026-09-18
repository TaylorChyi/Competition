from .protocol import Turn,Pos
from .fire_control import targets,joint_railgun_targets
from .brain import decide,_tower_sites

def u(i,k,x,y,h=1000,**kw):return dict(id=i,roleType=k,pos={'x':x,'y':y},health=h,level=kw.pop('level',1),**kw)
def state(roles,robots):return {'roundNo':71,'mapInfo':{'width':41,'height':32,'zones':[]},'teamOur':{'type':'challenger','goldNum':0,'roles':roles},'teamEnemy':{'roles':[]},'robot':{'roles':robots}}
def r(i,x,y,h):return u(i,'smallRobot',x,y,h,targetTeam='challenger')
# Rocket kills common low HP robot; railgun must seek a remaining live target.
p=state([u(1,'rocket',5,5),u(2,'railgun',5,7)],[r(10,8,5,20),r(11,8,8,40)])
t=Turn.load(p);res={};rocket=next(x for x in t.weapons() if x.kind=='rocket');rail=next(x for x in t.weapons() if x.kind=='railgun')
a=targets(t,rocket,res);before=dict(res);b=joint_railgun_targets(t,[rail],res)
assert a and b[rail.unit_id]
assert all(res.get(i,0)>=v for i,v in before.items())
# Three level3 missiles accumulate damage, with no blocking by foreign robots.
p=state([u(1,'rocket',5,5,level=3)],[r(10,10,10,100)])
t=Turn.load(p);res={};a=targets(t,t.weapons()[0],res);assert len(a)==3 and res[10]==60,(a,res)
# A cooling rocket never emits an attack; healthy adjacent crew doesn't move.
p=state([u(1,'worker',4,5,220),u(2,'rocket',5,5,cooldown=2)],[r(10,10,5,100)])
assert decide(p)=={},decide(p)
print('mixed reservation retained; level3 three missiles=60 center damage; cooling rocket silent')
