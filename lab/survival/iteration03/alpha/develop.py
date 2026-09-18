import json,hashlib,sys
from pathlib import Path
from lab.arena import Arena,ROBOT_STATS
from lab.survival.iteration03.alpha.brain import decide
from lab.tournament.round05.alpha.brain import decide as opponent

class RecordedArena(Arena):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.snapshots=[]
    def settle(self,commands):
        super().settle(commands)
        if self.number%130 in (0,70):
            self.snapshots.append({'round':self.number,'teams':{team:{
                'gold':self.gold[team],
                'units':[{'id':p.uid,'kind':p.kind,'hp':p.hp,'level':p.level,'pos':[p.pos.x,p.pos.y],'backpack':list(p.backpack)} for p in self.pieces if p.team==team and p.kind not in ROBOT_STATS and p.hp>0],
                'incoming':[{'kind':p.kind,'hp':p.hp,'pos':[p.pos.x,p.pos.y]} for p in self.pieces if p.team==team and p.kind in ROBOT_STATS and p.hp>0],
                'upgrades':self.metrics[team]['upgrades'][:],
                'shots':self.metrics[team]['shots'],'income':self.metrics[team]['income']
            } for team in ('challenger','defender')}})

name=sys.argv[1]
if name=='baseline':decide=opponent
out={'variant':name,'judgeSha256':hashlib.sha256(Path('lab/arena.py').read_bytes()).hexdigest(),'halves':[]}
for seed,mode in ((22000,'nearest'),(22001,'nearest'),(22002,'nearest')):
    for seat in ('challenger','defender'):
        other='defender' if seat=='challenger' else 'challenger'
        arena=RecordedArena(seed,'field',mode,10,commerce=True)
        results=arena.run({seat:decide,other:opponent})
        out['halves'].append({'seed':seed,'mode':mode,'seat':seat,'self':results[seat],'snapshots':arena.snapshots})
        print(seed,mode,seat,'survival',results[seat]['survivalRounds'],'nightHp',results[seat]['nightHp'],'invalid',results[seat]['invalidCommands'],flush=True)
Path('lab/survival/iteration03/alpha/'+name+'.json').write_text(json.dumps(out,indent=2))
