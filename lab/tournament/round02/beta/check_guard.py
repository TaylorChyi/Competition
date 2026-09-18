from .protocol import Turn,Pos
from .guard import safer_step
from lab.tournament.round01.alpha.protocol import Turn as ParentTurn
from lab.tournament.round01.alpha.guard import safer_step as parent_step

def entity(uid,kind,x,y,hp):
 return dict(id=uid,roleType=kind,pos={'x':x,'y':y},health=hp,level=1)
payload={'roundNo':71,'teamOur':{'type':'challenger','goldNum':0,'roles':[entity(1,'worker',6,5,220),entity(2,'railgun',5,5,1000)]},'teamEnemy':{'roles':[]},'mapInfo':{'width':41,'height':32,'zones':[]},'robot':{'roles':[dict(entity(10,'largeRobot',9,5,500),targetTeam='challenger')]}}
turn=Turn.load(payload);parent=ParentTurn.load(payload)
assert parent_step(parent,parent.controllable()[0],parent.weapons()[0],set()) is None
step=safer_step(turn,turn.controllable()[0],turn.weapons()[0],set());assert step is not None and step.x==5
payload['robot']['roles'][0].update(roleType='smallRobot',health=10)
turn=Turn.load(payload);assert safer_step(turn,turn.controllable()[0],turn.weapons()[0],set()) is None
print('healthy worker pre-empts sustained large-robot fire; keeps ready small-robot finishing shot')
