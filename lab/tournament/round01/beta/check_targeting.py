from .protocol import Turn,Pos
from .fire_control import targets

def entity(uid,kind,x,y,hp,**kwargs):
 return dict(id=uid,roleType=kind,pos={'x':x,'y':y},health=hp,level=1,**kwargs)
roles=[entity(1,'worker',5,5,100),entity(2,'railgun',6,5,1000),entity(3,'station',3,5,1500)]
payload={'roundNo':71,'teamOur':{'type':'challenger','goldNum':0,'roles':roles},'teamEnemy':{'roles':[]},'mapInfo':{'width':41,'height':32,'zones':[]},'robot':{'roles':[entity(10,'smallRobot',8,5,10,targetTeam='challenger'),entity(11,'bossRobot',12,10,800,targetTeam='challenger')]}}
turn=Turn.load(payload);assert targets(turn,turn.weapons()[0],{})==[Pos(8,5)]
# On a damaged station the scoring must exactly match the base threat policy.
from lab.tournament.base.protocol import Turn as BaseTurn
from lab.tournament.base.fire_control import targets as base_targets
roles[-1]['health']=100
turn=Turn.load(payload);base=BaseTurn.load(payload)
assert [p.dump() for p in targets(turn,turn.weapons()[0],{})]==[p.dump() for p in base_targets(base,base.weapons()[0],{})]
print('near lethal small robot beats full-health distant boss; distressed base retains base scoring')
