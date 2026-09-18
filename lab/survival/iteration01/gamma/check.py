import json
from pathlib import Path
from lab.arena import Arena,TEAMS
from tools.run_league import load_bot
out=Path('lab/survival/iteration01/gamma');parent=Path('lab/tournament/round05/alpha')
allrows=[]
for label,path in [('parent',parent),('full_sale_cost',out)]:
 for seed,priority in [(22000,'nearest'),(22001,'operators'),(22002,'advance')]:
  for seat in TEAMS:
   bots={t:load_bot(path if t==seat else parent,f'{label}_{seed}_{seat}_{t}') for t in TEAMS}
   g=Arena(seed,'field',priority,10,commerce=True);events=[]
   for _ in range(1300):
    g.begin();before=g.gold[seat];income=g.metrics[seat]['income'];b=g.base(seat)
    cmds={t:bots[t](g.observation(t)) if g.base(t).hp>0 else {} for t in TEAMS}
    g.settle(cmds)
    special={k:v for k,v in cmds[seat].items() if v.get('action') in ('buy','sell','use')}
    if special or g.number%130==0:
     events.append({'round':g.number,'cashBefore':before,'cashAfter':g.gold[seat],'incomeDelta':g.metrics[seat]['income']-income,'hp':b.hp,'level':b.level,'actions':special,'equipment':[[p.kind,p.level,p.hp] for p in g.pieces if p.team==seat and p.kind in ('railgun','rocket') and p.hp>0]})
   m=g.metrics[seat];m.pop('decisionMs',None)
   row={'variant':label,'seed':seed,'profile':priority,'seat':seat,'passed10':all(h>0 for h in m['nightHp']),'metrics':m,'events':events};allrows.append(row)
   (out/'development.json').write_text(json.dumps(allrows,indent=2))
   print(label,seed,seat,row['passed10'],m['baseDeathRound'],m['income'],m['upgrades'],flush=True)
