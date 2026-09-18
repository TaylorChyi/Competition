from .partial12.brain import _wall_order,_tower_sites
from .partial12.protocol import Turn,Pos
from .partial12.grid import shortest_path

def u(i,k,x,y,h=1000):return dict(id=i,roleType=k,pos={'x':x,'y':y},health=h,level=1)
for bx,by,rx,ry in [(9,22,10,20),(30,10,30,11)]:
 p={'roundNo':70,'mapInfo':{'width':41,'height':32,'zones':[]},'teamOur':{'type':'challenger','goldNum':0,'roles':[u(1,'worker',rx,ry,220),u(2,'station',bx,by,1500)]},'teamEnemy':{'roles':[]},'robot':{'roles':[]}}
 t=Turn.load(p);walls=_wall_order(t);guns=_tower_sites(t)
 assert len(walls)==len(set(walls))==12
 assert (Pos(bx+3,by-2) if bx<20 else Pos(bx-2,by+1)) not in walls
 p['teamOur']['roles'] += [u(10+i,'wall',pos.x,pos.y) for i,pos in enumerate(walls)]
 p['teamOur']['roles'] += [u(50+i,'railgun',pos.x,pos.y) for i,pos in enumerate(guns)]
 t=Turn.load(p);path=shortest_path(t,t.controllable()[0],Pos(bx+5,by),set())
 assert path is not None,(bx,by)
 for x in range(bx-1,bx+3):
  for y in range(by-2,by+2):
   pos=Pos(x,y)
   if pos in t.occupied_cells():continue
   from dataclasses import replace
   actor=replace(t.controllable()[0],pos=pos)
   # Replace the old actor too: it must not remain a phantom obstacle.
   local=replace(t,ours=tuple(actor if z.unit_id==actor.unit_id else z for z in t.ours))
   assert shortest_path(local,actor,Pos(bx+5,by),set()) is not None,(bx,by,pos)
 print('base',bx,by,'12 walls, every free inner-ring cell can exit')
