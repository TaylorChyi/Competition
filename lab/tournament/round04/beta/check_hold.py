from .holdshot.protocol import Turn
from .holdshot.brain import decide
from .holdshot.guard import shot_relieves_threat
from .holdshot.fire_control import targets

def state(hp=8,enemy_hp=10):
 def u(i,k,x,y,h):return dict(id=i,roleType=k,pos={'x':x,'y':y},health=h,level=1)
 return {'roundNo':71,'mapInfo':{'width':41,'height':32,'zones':[]},'teamOur':{'type':'challenger','goldNum':0,'roles':[u(1,'worker',6,5,hp),u(2,'railgun',5,5,1000)]},'teamEnemy':{'roles':[]},'robot':{'roles':[dict(u(10,'smallRobot',9,5,enemy_hp),targetTeam='challenger')]}}
p=state();t=Turn.load(p);reserved={};preview=dict(reserved);targets(t,t.weapons()[0],preview)
assert reserved=={} and preview=={10:10}
assert shot_relieves_threat(t,t.controllable()[0],reserved,preview)
assert decide(p)['2']['action']=='attack' and '1' not in decide(p)
# Not enough health for current damage: no magical same-round cancellation.
assert decide(state(hp=5))['1']['action']=='move'
# Cannot finish threat: preserve retreat and do not reserve preview damage.
assert decide(state(enemy_hp=40))['1']['action']=='move'
assert not shot_relieves_threat(t,t.controllable()[0],{10:10},{10:10})
print('actual hold-shot branch fires; lethal-current / unfinished target retreat; preview isolated')
# Foreign-team robot still physically absorbs a railgun shot.
p=state();p['robot']['roles'].append(dict(id=11,roleType='largeRobot',pos={'x':7,'y':5},health=500,level=1,targetTeam='defender'))
assert decide(p)['1']['action']=='move'
print('foreign-team intervening robot prevents a false guaranteed kill')
