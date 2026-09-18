"""Qualification and resume failures, without running tournament episodes."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools import run_qualified_tournament as q


def plan():
    return {'nights': 10, 'seats': ['challenger', 'defender'], 'opponent': 'opponent',
            'development': [{'seed': n, 'priority': 'nearest'} for n in range(4)],
            'validation': [{'seed': n, 'priority': 'nearest'} for n in range(10, 20)]}


def report(stage, candidate='tested'):
    p = plan()
    result = {'nightHp': [1]*10, 'baseDeathRound': None, 'survivedNights': 10,
              'survivalRounds': 1300, 'invalidCommands': 0, 'foreignOnlyShots': 0}
    return {'plan': p, 'stage': stage, 'complete': True, 'passed': True,
            'pvpAllowed': stage == 'validation', 'candidatePath': candidate, 'sourceHashes': {},
            'episodes': [{'seed': c['seed'], 'priority': c['priority'], 'seat': seat,
                          'candidate': copy.deepcopy(result)} for c in p[stage] for seat in p['seats']]}


class QualificationTests(unittest.TestCase):
    def test_duplicate_validation_episode_rejected_even_when_marked_passed(self):
        r = report('validation'); r['episodes'][-1] = copy.deepcopy(r['episodes'][0])
        with self.assertRaisesRegex(ValueError, 'duplicated'):
            q.verify_stage(r, plan(), 'validation')

    def test_failed_episode_rejected_despite_aggregate_passed_flag(self):
        r = report('development'); r['episodes'][0]['candidate']['nightHp'][-1] = 0
        with self.assertRaisesRegex(ValueError, 'failed episode'):
            q.verify_stage(r, plan(), 'development')

    def test_byte_identical_report_reuse_and_runtime_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            for name in ('tested', 'candidate'):
                (root/name).mkdir()
                for module in q.gate.RUNTIME:
                    (root/name/module).write_text('# qualified\n')
            for stage in ('development', 'validation'):
                (root/(stage+'.json')).write_text(json.dumps(report(stage)))
            refs = {s: s+'.json' for s in ('development', 'validation')}
            with patch.object(q, 'ROOT', root), patch.object(q.gate, 'hashes', return_value={}):
                result = q.qualify(root/'candidate', refs, plan())
                self.assertTrue(result['byteIdentityVerified'])
                self.assertEqual(result['testedCandidate'], 'tested')
                (root/'candidate/brain.py').write_text('# altered\n')
                with self.assertRaisesRegex(ValueError, 'runtime differs'):
                    q.qualify(root/'candidate', refs, plan())

    def test_stale_judge_hash_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            for stage in ('development', 'validation'):
                (root/(stage+'.json')).write_text(json.dumps(report(stage)))
            refs = {s: s+'.json' for s in ('development', 'validation')}
            with patch.object(q, 'ROOT', root), patch.object(q.gate, 'hashes', return_value={'judge':'changed'}):
                with self.assertRaisesRegex(ValueError, 'stale'):
                    q.qualify(root/'candidate', refs, plan())

    def test_identical_tied_leaders_detected_without_all_candidates_identical(self):
        identities = {'alpha': {'brain.py':'new'}, 'beta': {'brain.py':'old'}, 'gamma': {'brain.py':'old'}}
        self.assertFalse(q.indistinguishable(['alpha','beta','gamma'], identities))
        self.assertTrue(q.indistinguishable(['beta','gamma'], identities))
        self.assertFalse(q.indistinguishable(['alpha'], identities))
        saved = {'complete': False, 'champion': None}
        self.assertTrue(q.block_equivalent_tie(saved, ['beta','gamma'], identities))
        self.assertFalse(saved['complete'])
        self.assertIsNone(saved['champion'])
        self.assertEqual(saved['structurallyEquivalentLeaders'], ['beta','gamma'])

    def test_round7_schedule_and_saved_half_tampering(self):
        rules = json.loads(q.RULES.read_text())
        self.assertEqual([c['seed'] for c in q.scheduled_cases(7,0,rules)], list(range(37000,37010)))
        self.assertEqual([c['seed'] for c in q.scheduled_cases(7,1,rules)], list(range(37020,37025)))
        result = {'baseDeathRound': None, 'killPoints': 1, 'nightHp': [1]*10}
        halves = [{'firstSeat': seat, 'results':[result,result], 'scores':[551,551], 'outcome':0}
                  for seat in q.TEAMS]
        fixture = {'players':['alpha','beta'], 'seed':37000, 'profile':'field-nearest',
                   'halves':halves,'outcome':0}
        saved = {'round':7,'complete':False,'champion':None,'stages':[
            {'number':0,'players':rules['agents'],'fixtures':[fixture],'complete':False}]}
        q.validate_history(saved,rules)
        halves[1]['firstSeat'] = halves[0]['firstSeat']
        with self.assertRaisesRegex(ValueError, 'Half seat'):
            q.validate_history(saved,rules)


if __name__ == '__main__':
    unittest.main()
