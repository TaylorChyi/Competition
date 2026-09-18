from .protocol import Turn,Pos
from .brain import decide
from .guard import joint_positions

def unit(uid,kind,x,y,hp=220):
 return dict(id=uid,roleType=kind,pos={'x':x,'y':y},health=hp,level=1)
roles=[unit(1,'worker',6,5,70),unit(2,'worker',5,5),unit(3,'railgun',5,6,1000),unit(4,'railgun',4,5,1000)]
zones=[{'pos':{'x':x,'y':y},'neutralType':'stone'} for x,y in [(5,4),(6,4),(7,4),(7,5),(7,6),(6,6)]]
payload={'roundNo':71,'teamOur':{'type':'challenger','goldNum':0,'roles':roles},'teamEnemy':{'roles':[]},'mapInfo':{'width':41,'height':32,'zones':zones},'robot':{'roles':[dict(unit(10,'bossRobot',9,5,800),targetTeam='challenger')]}}
out=decide(payload)
assert out['1']['action']=='move' and out['1']['targetPos']==[{'x':5,'y':5}],out
assert out['2']['action']=='move' and out['2']['targetPos']!=[{'x':6,'y':5}],out
assert out['1']['targetPos']!=out['2']['targetPos']
# Healthy operators should retain inherited firing, not plan cosmetic shifts.
roles[0]['health']=220
out=decide(payload);assert not any(c['action']=='move' for c in out.values()),out
# A role already using an item remains a static obstacle.
turn=Turn.load(payload);pairs=((turn.controllable()[0],turn.weapons()[0]),)
# Healthy roles bypass the coordinator entirely.
assert joint_positions(turn,pairs,set()) is None
print('dangerous worker follows vacating healthy worker without swap; healthy case keeps firing')
