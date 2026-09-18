"""Independent comparison of released round01 champion with b471f44."""
import hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'CoreGeek/src')]
from lab.arena import Arena,TEAMS
from tools.run_league import load_bot,score,half_winner,fixture_winner,table
paths={'champion':ROOT/'lab/tournament/round01/alpha','released':ROOT/'lab/league/baseline'}
files=[ROOT/'lab/arena.py',ROOT/'lab/night_sim.py',ROOT/'tools/run_league.py',Path(__file__)]
for p in paths.values():files.extend(p.glob('*.py'))
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
report={'purpose':'Independent release comparison; not tournament selection or official replay','sourceHashes':hashes,'fixtures':[],'complete':False}
output=ROOT/'lab/validation/round01-vs-b471f44.json'
for seed,priority in ((23011,'nearest'),(23012,'operators'),(23013,'advance')):
 f={'players':['champion','released'],'seed':seed,'profile':'field-'+priority,'halves':[]}
 for seat in (0,1):
  bots={n:load_bot(p,f'comparison_{seed}_{seat}_{n}') for n,p in paths.items()}
  r=Arena(seed,'field',priority,10,commerce=True).run({TEAMS[seat]:bots['champion'],TEAMS[1-seat]:bots['released']})
  values=[r[TEAMS[seat]],r[TEAMS[1-seat]]]
  f['halves'].append({'firstSeat':TEAMS[seat],'results':values,'scores':[score(v) for v in values],'outcome':half_winner(*values)})
 f['outcome']=fixture_winner(f['halves']);report['fixtures'].append(f)
 output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(seed,priority,f['outcome'],[h['scores'] for h in f['halves']],flush=True)
report.update(complete=True,table=table(report['fixtures']))
assert hashes=={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report['table'],ensure_ascii=False,indent=2),flush=True)
