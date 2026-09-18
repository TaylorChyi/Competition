from lab.survival.iteration02.alpha.protocol import Turn
from lab.survival.iteration02.alpha.economy import late_rocket_refit

def u(i,k,x,y,h=1000,**kw):return dict(id=i,roleType=k,pos={'x':x,'y':y},health=h,level=kw.pop('level',1),**kw)
p={'roundNo':800,'mapInfo':{'width':41,'height':32,'zones':[]},'teamOur':{'type':'challenger','goldNum':50,'roles':[u(1,'worker',9,10,220),u(2,'worker',9,12,220),u(3,'pioneer',15,10,200,backpack=['WeaponUpgradeVoucher1']),u(10,'station',10,10,4000,level=3),u(20,'railgun',9,9),u(21,'railgun',9,11),u(22,'railgun',12,9)]},'teamEnemy':{'roles':[]},'robot':{'roles':[]}}
t=Turn.load(p);commands={};claimed=set()
for r in t.workers():late_rocket_refit(t,r,claimed,commands)
print(commands)
print('rocket_builds',sum(c.get('name')=='rocket' for c in commands.values()),'carried_vouchers',1)
