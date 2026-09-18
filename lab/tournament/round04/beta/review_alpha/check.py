import json,time
from unittest.mock import patch
from lab.tournament.round04.alpha.protocol import Turn,Pos
from lab.tournament.round04.alpha.fire_control import targets,joint_railgun_targets
from lab.tournament.round04.alpha.brain import decide

def u(i,k,x,y,h=1000,**kw):return dict(id=i,roleType=k,pos={'x':x,'y':y},health=h,level=1,**kw)
def state(roles,robots):return {'roundNo':71,'mapInfo':{'width':41,'height':32,'zones':[]},'teamOur':{'type':'challenger','goldNum':0,'roles':roles},'teamEnemy':{'roles':[]},'robot':{'roles':robots}}
def r(i,x,y,h=10,team='challenger'):return u(i,'smallRobot',x,y,h,targetTeam=team)
# Same official level1 range6, different geometry: A reaches two, B only common.
p=state([u(1,'railgun',5,5),u(2,'railgun',0,5),u(3,'station',3,3)], [r(10,4,5),r(11,10,10)])
t=Turn.load(p);res={};old={gun.unit_id:targets(t,gun,res) for gun in sorted(t.weapons(),key=lambda x:x.unit_id)};assert len([v for v in old.values() if v])==1,old
res={};plan=joint_railgun_targets(t,sorted(t.weapons(),key=lambda x:x.unit_id),res);assert all(plan.values()),plan
assert res=={10:10,11:10},res
# One common target cannot be counted repeatedly as kills or gain damage>health utility.
t=Turn.load(state([u(1,'railgun',5,5),u(2,'railgun',0,5)],[r(10,4,5)]));res={};plan=joint_railgun_targets(t,t.weapons(),res)
assert len([x for x in plan.values() if x])==1 and res=={10:10}
# Foreign-target blocker absorbs energy; no incoming damage is reserved.
t=Turn.load(state([u(1,'railgun',5,5)],[r(10,9,5),r(11,7,5,500,'defender')]));res={};assert joint_railgun_targets(t,t.weapons(),res)=={1:[]};assert res=={}
# An existing reservation is not added again across six candidate orders.
t=Turn.load(p);res={10:10};plan=joint_railgun_targets(t,t.weapons(),res);assert res=={10:10,11:10},res
# Actual brain: busy operator and cooling tower never enter the optimizer.
p=state([u(1,'worker',4,5,220),u(2,'worker',0,4,220),u(3,'pioneer',8,8,300),u(20,'railgun',5,5),u(21,'railgun',0,5,cooldown=1),u(22,'railgun',9,8)],[r(10,8,5,100)])
seen=[]
def busy(turn,role,claimed,commands,**kw):
 if role.unit_id==1:commands[1]={'action':'use','name':'Medicine'};return True
 return False
def capture(turn,towers,res):seen.extend(x.unit_id for x in towers);return {}
with patch('lab.tournament.round04.alpha.brain.use_carried',side_effect=busy),patch('lab.tournament.round04.alpha.brain.safer_step',return_value=None),patch('lab.tournament.round04.alpha.brain.joint_railgun_targets',side_effect=capture):decide(p)
assert seen==[22],seen
# Stress bounded three-gun enumeration; timings are local, not official SLA proof.
perf=[]
for n in (36,100,200):
 robots=[r(100+i,8+i%6,8+(i//6)%6,40) for i in range(n)]
 t=Turn.load(state([u(1,'railgun',5,5),u(2,'railgun',5,6),u(3,'railgun',6,5)],robots))
 begin=time.perf_counter();joint_railgun_targets(t,t.weapons(),{});ms=(time.perf_counter()-begin)*1000;perf.append([n,round(ms,2)])
print(json.dumps({'checks':'six adversarial cases pass','three_guns_ms':perf}))
