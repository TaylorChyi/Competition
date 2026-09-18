import json
from collections import defaultdict
from lab.arena import Arena
import lab.tournament.round03.alpha.economy as ec
import lab.tournament.round03.alpha.brain as br
from lab.tournament.round01.beta.brain import decide as rival
from tools.run_league import score,half_winner
original_repair=ec.repair_upgrade
original_sell=ec.sell_at_vendor_for_upgrade
results=[]
for seat in (0,1):
 events=defaultdict(set)
 def repair(t,c):
  r=original_repair(t,c)
  if r:events['fundedRepair'].add(t.round_no)
  return r
 def sell(t,r,c):
  v=original_sell(t,r,c)
  if v:events['prioritySale'].add(t.round_no)
  return v
 ec.repair_upgrade=br.repair_upgrade=repair
 br.sell_at_vendor_for_upgrade=sell
 keys=('challenger','defender') if seat==0 else ('defender','challenger')
 result=Arena(26007,'field','operators',10,commerce=True).run({keys[0]:br.decide,keys[1]:rival})
 row={'seed':26007,'priority':'operators','alphaSeat':keys[0],'events':{k:sorted(v) for k,v in events.items()},'results':result,'outcome':half_winner(result[keys[0]],result[keys[1]])}
 results.append(row)
 print(seat,row['events'],[(score(result[k]),result[k]['survivalRounds'],result[k]['income'],result[k]['invalidCommands']) for k in keys],flush=True)
open('lab/tournament/round03/alpha/known_failure.json','w').write(json.dumps(results,indent=2))
