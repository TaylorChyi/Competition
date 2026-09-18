import json,sys,hashlib
from pathlib import Path
from lab.arena import Arena
from lab.tournament.round07.alpha.brain import decide
from lab.survival.iteration03.beta.full_ring_exits.brain import decide as parent
from lab.tournament.round05.alpha.brain import decide as background
name=sys.argv[1]
policy=parent if name=='baseline' else decide
out={'variant':name,'judgeSha256':hashlib.sha256(Path('lab/arena.py').read_bytes()).hexdigest(),'halves':[]}
for seed in (22000,22001,22002,26006):
 for seat in ('challenger','defender'):
  other='defender' if seat=='challenger' else 'challenger'
  result=Arena(seed,'field','nearest',10,commerce=True).run({seat:policy,other:background})[seat]
  out['halves'].append({'seed':seed,'seat':seat,'self':result})
  print(name,seed,seat,result['survivalRounds'],result['killPoints'],result['nightHp'][-1],result['invalidCommands'],flush=True)
Path('lab/tournament/round07/alpha/'+name+'.json').write_text(json.dumps(out,indent=2))
