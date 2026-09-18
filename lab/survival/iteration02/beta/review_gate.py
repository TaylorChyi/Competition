"""Negative test: do not use its synthetic payload as survival evidence."""
from pathlib import Path
from unittest.mock import patch
import contextlib,io,json,tempfile
from tools import run_survival as gate
root=gate.ROOT
candidate=root/'lab/tournament/round05/alpha'
plan=json.loads(gate.PLAN.read_text())
result={'baseDeathRound':None,'nightHp':[1]*10,'survivedNights':10,'invalidCommands':0,'foreignOnlyShots':0}
episode={'seed':22000,'priority':'nearest','seat':'challenger','candidate':result,'background':result}
report={'plan':plan,'stage':'development','candidatePath':str(candidate.relative_to(root)),
 'sourceHashes':gate.hashes(candidate,candidate),'episodes':[episode]*6,'complete':False,'passed':False,'pvpAllowed':False,'elapsedSeconds':0}
with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
 out=Path(tmp)/'SYNTHETIC-INVALID.json';out.write_text(json.dumps(report))
 argv=['run_survival.py','--candidate',str(candidate.relative_to(root)),'--stage','development','--output',str(out)]
 try:
  with patch('sys.argv',argv),patch.object(gate,'Arena',side_effect=AssertionError('should not run')):
   with contextlib.redirect_stdout(io.StringIO()):gate.main()
 except ValueError as exc:
  print(json.dumps({'synthetic_duplicate_cases':True,'correctly_rejected':str(exc)}))
 else:
  raise AssertionError('Invalid duplicate-case report was accepted')
