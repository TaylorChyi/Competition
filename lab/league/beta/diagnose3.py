import json
from lab.arena import Arena, TEAMS
from lab.league.beta.round2.brain import decide
from lab.league.baseline.brain import decide as opponent
for seat in (0,1):
 a=Arena(22002,'heavy','advance',10,True);team=TEAMS[seat]
 def tracked(obs):
  cmd=decide(obs)
  if 390<=obs['roundNo']<=500 and (obs['roundNo']%5==0 or any(c.get('action') in ('use','buy','sell') for c in cmd.values())):
   roles=obs['teamOur']['roles']; print(json.dumps({'seat':seat,'round':obs['roundNo'],'gold':obs['teamOur']['goldNum'],'roles':[r for r in roles if r['roleType'] in ('station','worker','pioneer')],'commands':cmd}),flush=True)
  return cmd
 a.run({team:tracked,TEAMS[1-seat]:opponent})
