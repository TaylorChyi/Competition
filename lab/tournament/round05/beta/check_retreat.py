from .protocol import Turn, Pos, distance
from .guard import safer_step, retreat_step, exposure
from .brain import decide

def unit(i,k,x,y,hp):
 return dict(id=i,roleType=k,pos={'x':x,'y':y},health=hp,level=1)
def state(roles,robots):
 return {'roundNo':71,'mapInfo':{'width':41,'height':32,'zones':[]},'teamOur':{'type':'challenger','goldNum':0,'roles':roles},'teamEnemy':{'roles':[]},'robot':{'roles':robots}}
robot=dict(unit(10,'bossRobot',3,5,800),targetTeam='challenger')
payload=state([unit(1,'worker',7,5,30),unit(2,'railgun',5,5,1000)],[robot])
t=Turn.load(payload);role=t.controllable()[0]
step=retreat_step(t,role,set());assert step and exposure(t,step)<exposure(t,role.pos)
assert distance(step,t.incoming_robots()[0].pos)>3
command=decide(payload)['1'];assert command['action']=='move'
# Danger gone: retreat releases control to ordinary tower return routing.
payload['robot']['roles']=[];t=Turn.load(payload)
assert retreat_step(t,t.controllable()[0],set()) is None
assert decide(payload)['1']['action']=='move'
# An omitted/busy operator is still an obstacle for the single-role planner.
from .guard import joint_positions
from .check_joint import payload as chain
chain['teamOur']['roles'][0]['health']=70
t=Turn.load(chain);r=t.controllable()[0]
plan=joint_positions(t,((r,t.weapons()[0]),),set())
assert plan is None or plan[1].get(r.unit_id)!=Pos(5,5)
print('continued retreat lowers exposure; no-threat returns to gun; busy role remains blocked')
