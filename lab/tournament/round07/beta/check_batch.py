import importlib
from unittest.mock import patch

def u(i,k,x,y,h=1000,**kw):return dict(id=i,roleType=k,pos={'x':x,'y':y},health=h,level=1,**kw)
def payload(wall_count=0,round_no=30,ore=True):
 roles=[u(1,'worker',4,23,220,backpack=['stone']*4),u(2,'pioneer',10,23,200),u(3,'worker',10,20,220),u(10,'station',9,22,1500),u(20,'railgun',11,20),u(21,'railgun',11,22),u(22,'railgun',8,22)]
 roles += [u(30+i,'wall',x,y) for i,(x,y) in enumerate([(12,19),(11,19),(10,19),(9,19)][:wall_count])]
 return {'roundNo':round_no,'mapInfo':{'width':41,'height':32,'zones':[{'pos':{'x':4,'y':24},'neutralType':'stone'}] if ore else []},'teamOur':{'type':'challenger','goldNum':0,'roles':roles},'teamEnemy':{'roles':[]},'robot':{'roles':[]},'weaponShopList':[{'name':'WeaponUpgradeVoucher1','price':100}]}
def worker_action(bot,p):
 t=bot.Turn.load(p);role=t.workers()[0];commands={}
 bot._worker_day(t,role,bot._tower_sites(t),[],[],set(),commands,bot.TOWER_LOADOUT,True,19)
 return commands.get(1)
base=importlib.import_module('lab.tournament.round07.beta.parent.brain')
large=importlib.import_module('lab.tournament.round07.beta.batch10.brain')
screen=importlib.import_module('lab.tournament.round07.beta.after_screen.brain')
assert worker_action(base,payload())['action']!='collect'
assert worker_action(large,payload())['action']=='collect'
assert worker_action(screen,payload())['action']!='collect'
assert worker_action(screen,payload(4))['action']=='collect'
for bot in (large,screen):
 with patch.object(bot,'_mine',side_effect=AssertionError('must not seek a new mine with carried stone')):
  assert worker_action(bot,payload(4,ore=False))['action']!='collect'
 assert bot.decide(payload(4,round_no=70)).get('1',{}).get('action')!='collect'
print('batch enlargement triggers; initial screen retained; empty mine returns to wall; dusk return preempts collecting')
