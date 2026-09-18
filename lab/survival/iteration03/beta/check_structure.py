from .full_ring.brain import _wall_order,_tower_sites
from .full_ring.protocol import Turn,Pos
from .full_ring.grid import shortest_path

def u(i,k,x,y,h=1000):return dict(id=i,roleType=k,pos={'x':x,'y':y},health=h,level=1)
for bx,by,rx,ry in [(9,22,10,20),(30,10,30,11)]:
 p={'roundNo':70,'mapInfo':{'width':41,'height':32,'zones':[]},'teamOur':{'type':'challenger','goldNum':0,'roles':[u(1,'worker',rx,ry,220),u(2,'station',bx,by,1500)]},'teamEnemy':{'roles':[]},'robot':{'roles':[]}}
 t=Turn.load(p);walls=_wall_order(t);guns=_tower_sites(t)
 assert len(walls)==len(set(walls))==19
 assert (Pos(bx+3,by-2) if bx<20 else Pos(bx-2,by+1)) not in walls
 p['teamOur']['roles'] += [u(10+i,'wall',pos.x,pos.y) for i,pos in enumerate(walls)]
 p['teamOur']['roles'] += [u(50+i,'railgun',pos.x,pos.y) for i,pos in enumerate(guns)]
 t=Turn.load(p);path=shortest_path(t,t.controllable()[0],Pos(bx+5,by),set())
 assert path is not None,(bx,by)
 print('base',bx,by,'19 walls, exit path length',len(path))
