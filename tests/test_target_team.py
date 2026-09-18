"""Regression for the platform feedback: don't clear the opponent's wave."""
import copy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'CoreGeek/src'))
from agent.brain import decide
from agent.protocol import Turn, Pos
from test_baseline import state, unit


class TargetTeamChecks(unittest.TestCase):
    def scenario(self, kind='rocket', own='challenger'):
        payload = state(71, roles=[unit(1, 'worker', 9, 9), unit(2, kind, 10, 10)])
        payload['teamOur']['type'] = own
        other = 'defender' if own == 'challenger' else 'challenger'
        payload['robot']['roles'] = [
            unit(30001, 'bossRobot', 11, 10, targetTeam=other),
            unit(30002, 'smallRobot', 13, 10, targetTeam=own),
        ]
        return payload

    def test_both_teams_and_all_weapons_skip_closer_foreign_robot(self):
        for team in ('challenger', 'defender'):
            for weapon in ('gatling', 'railgun', 'rocket'):
                with self.subTest(team=team, weapon=weapon):
                    payload = self.scenario(weapon, team)
                    command = decide(payload)['2']
                    self.assertEqual(command['targetPos'], [{'x': 13, 'y': 10}])

    def test_splash_scores_only_our_incoming_wave(self):
        payload = self.scenario()
        payload['robot']['roles'] += [unit(31000+i, 'smallRobot', x, y, targetTeam='defender')
                                      for i, (x, y) in enumerate([(10, 11), (11, 11), (12, 11), (10, 12)])]
        policy = {'mode': 'splash', 'threatWeight': 0, 'killBonus': 0, 'reserveDamage': True}
        self.assertEqual(decide(payload, rocket_policy=policy)['2']['targetPos'], [{'x': 13, 'y': 10}])

    def test_no_foreign_or_unlabelled_target_even_if_nothing_else_visible(self):
        payload = self.scenario()
        payload['robot']['roles'] = payload['robot']['roles'][:1]
        self.assertEqual(decide(payload), {})
        payload['robot']['roles'][0].pop('targetTeam')
        self.assertEqual(decide(payload), {})
        payload = self.scenario()
        payload['teamOur'].pop('type')
        self.assertEqual(decide(payload), {})

    def test_foreign_robots_still_block_movement(self):
        turn = Turn.load(self.scenario())
        self.assertEqual(len(turn.robots), 2)
        self.assertEqual([r.robot_id for r in turn.incoming_robots()], [30002])
        self.assertIn(Pos(11, 10), turn.blocked(turn.workers()[0]))

    def test_each_request_uses_current_team_label_without_cross_match_state(self):
        payload = self.scenario()
        other = copy.deepcopy(payload)
        other['teamOur']['type'] = 'defender'
        self.assertEqual(decide(other)['2']['targetPos'], [{'x': 11, 'y': 10}])
        self.assertEqual(decide(payload)['2']['targetPos'], [{'x': 13, 'y': 10}])


if __name__ == '__main__':
    unittest.main()
