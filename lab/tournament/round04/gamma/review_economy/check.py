import json,hashlib,shutil
from pathlib import Path
from lab.arena import Arena,TEAMS
from tools.run_league import load_bot,score
root=Path.cwd(); out=root/'lab/tournament/round04/gamma/review_economy'; parent=root/'lab/tournament/round03/gamma'
a=out/'ablation';a.mkdir(exist_ok=True)
for p in parent.glob('*.py'): shutil.copy2(p,a/p.name)
p=a/'economy.py';s=p.read_text();s=s.replace('base.health<.75*1500*base.level or\n            (base.level==1 and turn.round_no>130 and base.health<1500)','base.health<.75*1500*base.level').replace('base.health<.75*1500*base.level or\n                                 (base.level==1 and turn.round_no>130 and base.health<1500)','base.health<.75*1500*base.level');p.write_text(s)
old=json.loads((root/'lab/tournament/round03/results.json').read_text())
hashes={k:hashlib.sha256((root/k).read_bytes()).hexdigest()==v for k,v in old['sourceHashes'].items() if k in ['lab/arena.py','lab/night_sim.py','CoreGeek/src/agent/protocol.py','CoreGeek/src/agent/targeting.py']}
report={'judgeHashesMatchR3':hashes,'seed':28002,'priority':'advance','seat':'defender','runs':{}}
for label,path in [('baseline',parent),('ablation',a)]:
 game=Arena(28002,'field','advance',10,commerce=True)
 bots={'challenger':load_bot(root/'lab/tournament/round03/alpha',label+'alpha'),'defender':load_bot(path,label+'gamma')}
 events=[]
 for _ in range(1300):
  game.begin();b=game.base('defender');before={'cash':game.gold['defender'],'hp':b.hp,'level':b.level,'income':game.metrics['defender']['income']}
  commands={t:bots[t](game.observation(t)) if game.base(t).hp>0 else {} for t in TEAMS}
  game.settle(commands);after={'cash':game.gold['defender'],'hp':b.hp,'level':b.level,'income':game.metrics['defender']['income']}
  special={k:v for k,v in commands['defender'].items() if v.get('action') in ('buy','sell','use','build')}
  if before['cash']!=after['cash'] or special or game.number%130==0 or (before['hp']>0 and after['hp']<=0):
   events.append({'round':game.number,'before':before,'after':after,'commands':special,'guns':[[p.uid,p.level,p.hp] for p in game.pieces if p.team=='defender' and p.kind in ('railgun','rocket') and p.hp>0],'operators':[[p.uid,p.hp] for p in game.pieces if p.team=='defender' and p.kind in ('pioneer','worker')],'shots':game.metrics['defender']['shots']})
 report['runs'][label]={'metrics':game.metrics['defender'],'score':score(game.metrics['defender']),'events':events}
 (out/'results.json').write_text(json.dumps(report,indent=2))
 print(label,game.metrics['defender']['baseDeathRound'],game.metrics['defender']['nightHp'],game.metrics['defender']['upgrades'],flush=True)
