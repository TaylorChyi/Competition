"""Small scenarios prompted by the supplied log, not a replay of game state."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'CoreGeek' / 'src'))
from agent.brain import decide
from agent.protocol import Pos, Turn, distance
from test_baseline import state, unit


class DefenseChecks(unittest.TestCase):
    def test_worker_arrives_before_first_night_attack(self):
        payload = state(65, gold=0, roles=[
            unit(10010, 'worker', 0, 5),
            unit(10040, 'rocket', 7, 5),
        ])
        worker = payload['teamOur']['roles'][0]
        for number in range(65, 71):
            payload['roundNo'] = number
            command = decide(payload).get('10010')
            if command:
                self.assertEqual(command['action'], 'move')
                before, after = Pos.load(worker['pos']), Pos.load(command['targetPos'][0])
                self.assertEqual(distance(before, after), 1)
                turn = Turn.load(payload)
                self.assertTrue(turn.land(after))
                self.assertNotIn(after, turn.blocked(turn.workers()[0]))
                worker['pos'] = after.dump()
        self.assertLessEqual(distance(Pos.load(worker['pos']), Pos(7, 5)), 1)
        payload['roundNo'] = 71
        payload['robot']['roles'] = [unit(30001, 'smallRobot', 15, 5)]
        command = decide(payload)['10040']
        self.assertEqual(command['action'], 'attack')
        self.assertEqual(command['controllerId'], '10010')

    def test_early_day_still_collects(self):
        payload = state(10, gold=0, roles=[
            unit(10010, 'worker', 0, 5), unit(10040, 'rocket', 7, 5),
            unit(10013, 'station', 9, 5),
        ])
        payload['mapInfo']['zones'] = [{'pos': {'x': 0, 'y': 6}, 'neutralType': 'stone'}]
        self.assertEqual(decide(payload)['10010']['action'], 'collect')

    def test_pioneer_does_not_park_on_a_planned_wall(self):
        payload = state(20, gold=0, roles=[
            unit(10011, 'pioneer', 8, 23), unit(10020, 'gatling', 9, 23),
            unit(10013, 'station', 10, 24),
        ])
        command = decide(payload)['10011']
        self.assertEqual(command['action'], 'move')
        pos = Pos.load(command['targetPos'][0])
        self.assertEqual(distance(pos, Pos(8, 23)), 1)
        self.assertEqual(distance(pos, Pos(9, 23)), 1)
        self.assertGreaterEqual(pos.x, 9)

    def test_nearby_operators_fire_without_crossing_to_id_assigned_towers(self):
        payload = state(71, roles=[
            unit(10010, 'worker', 8, 24), unit(10012, 'worker', 8, 22),
            unit(10020, 'gatling', 9, 22), unit(10040, 'rocket', 9, 24),
        ])
        payload['robot']['roles'] = [unit(30001, 'smallRobot', 11, 23)]
        commands = decide(payload)
        self.assertEqual(set(commands), {'10020', '10040'})
        self.assertEqual(commands['10020']['controllerId'], '10012')
        self.assertEqual(commands['10040']['controllerId'], '10010')

    def test_surviving_operator_uses_tower_that_can_fire(self):
        payload = state(210, roles=[
            unit(10011, 'pioneer', 0, 0),
            unit(10020, 'gatling', 1, 0), unit(10040, 'rocket', 1, 1),
        ])
        dead = unit(10010, 'worker', 0, 1)
        dead['health'] = 0
        payload['teamOur']['roles'].append(dead)
        payload['robot']['roles'] = [unit(30001, 'smallRobot', 8, 1)]
        commands = decide(payload)
        self.assertEqual(set(commands), {'10040'})
        self.assertEqual(commands['10040']['controllerId'], '10011')
        payload['teamOur']['roles'][2]['cooldown'] = 3
        payload['robot']['roles'][0]['pos'] = {'x': 2, 'y': 1}
        self.assertEqual(set(decide(payload)), {'10020'})


if __name__ == '__main__':
    unittest.main()
