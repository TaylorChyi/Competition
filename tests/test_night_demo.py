import copy
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'bot' / 'src')]
from agent.brain import decide
from agent.protocol import Pos, Robot
from agent.targeting import BASELINE, rocket_targets, splash_damage
from lab.night_sim import Entity, Night, make_scenario, resolve_moves, choose_robot_step

SPLASH = {'name': 'test', 'mode': 'splash', 'threatWeight': 0,
          'killBonus': 0, 'reserveDamage': True}


class RocketRules(unittest.TestCase):
    def test_center_neighbor_outside(self):
        self.assertEqual(splash_damage(Pos(3, 3), Pos(3, 3)), 20)
        self.assertEqual(splash_damage(Pos(3, 3), Pos(4, 4)), 10)
        self.assertEqual(splash_damage(Pos(3, 3), Pos(5, 3)), 0)

    def test_salvo_reserves_damage_across_rockets(self):
        robots = (Robot(1, Pos(6, 5), 20), Robot(2, Pos(10, 5), 20))
        reserved = {}
        first = rocket_targets(Pos(5, 5), 10, 1, robots, Pos(0, 0), SPLASH, reserved)
        second = rocket_targets(Pos(5, 5), 10, 1, robots, Pos(0, 0), SPLASH, reserved)
        self.assertEqual(first, [Pos(6, 5)])
        self.assertEqual(second, [Pos(10, 5)])
        self.assertEqual(robots[0].health, 20)

    def test_empty_center_can_hit_more_robots(self):
        robots = tuple(Robot(i, p, 100) for i, p in enumerate(
            [Pos(5, 5), Pos(5, 7), Pos(7, 5), Pos(7, 7)]))
        target = rocket_targets(Pos(1, 1), 10, 1, robots, Pos(0, 0), SPLASH, {})
        self.assertEqual(target, [Pos(6, 6)])

    def test_targets_obey_map_range_and_level(self):
        robots = (Robot(1, Pos(0, 0), 5), Robot(2, Pos(40, 31), 800))
        targets = rocket_targets(Pos(0, 1), 3, 3, robots, Pos(0, 0), SPLASH, {})
        self.assertEqual(len(targets), 3)
        self.assertTrue(all(0 <= p.x <= 3 and 0 <= p.y <= 4 for p in targets))
        self.assertEqual(rocket_targets(Pos(20, 20), 3, 1, robots, Pos(0, 0), SPLASH, {}), [])

    def test_live_bot_upgraded_targets_and_policy_integration(self):
        import json, tempfile
        payload = {'roundNo': 71, 'mapInfo': {'width': 41, 'height': 32, 'zones': []},
                   'teamOur': {'roles': [
                       {'id': 1, 'roleType': 'worker', 'pos': {'x': 4, 'y': 5}, 'health': 220},
                       {'id': 2, 'roleType': 'rocket', 'pos': {'x': 5, 'y': 5}, 'health': 1500, 'level': 2},
                   ]}, 'robot': {'roles': [{'id': 3, 'pos': {'x': 8, 'y': 5}, 'health': 40}]}}
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(len(decide(payload)['2']['targetPos']), 2)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'policy.json'
            path.write_text(json.dumps(SPLASH))
            with patch.dict(os.environ, {'COMPETITION_ROCKET_POLICY': str(path)}):
                result = decide(payload)['2']
                self.assertEqual(result['controllerId'], '1')
                self.assertEqual(len(result['targetPos']), 2)


class EngineRules(unittest.TestCase):
    def make_micro_game(self, robot_hp=800):
        game = Night(1)
        game.entities = [
            Entity(1, 'station', Pos(0, 2), 1500, 1500),
            Entity(2, 'rocket', Pos(2, 2), 1000, 1000, controller=3),
            Entity(3, 'worker', Pos(2, 1), 220, 220),
            Entity(4, 'bossRobot', Pos(5, 2), robot_hp, robot_hp),
        ]
        return game

    def test_fire_then_three_idle_turns(self):
        game = self.make_micro_game()
        fire = []
        for turn in range(1, 6):
            if game.step(BASELINE):
                fire.append(turn)
        self.assertEqual(fire, [1, 5])

    def test_lethally_hit_robot_still_attacks_before_end_settlement(self):
        game = self.make_micro_game(robot_hp=20)
        game.step(BASELINE)
        tower = next(e for e in game.entities if e.uid == 2)
        self.assertEqual(tower.hp, 960)
        self.assertEqual(game.kills, 1)
        self.assertEqual(game.kill_points, 10)
        self.assertEqual(game.effective_damage, 20)

    def test_same_target_and_swap_moves_cancel(self):
        robots = [Entity(1, 'smallRobot', Pos(0, 0), 40, 40),
                  Entity(2, 'smallRobot', Pos(2, 0), 40, 40)]
        self.assertEqual(resolve_moves({1: Pos(1, 0), 2: Pos(1, 0)}, robots), {})
        self.assertEqual(resolve_moves({1: Pos(2, 0), 2: Pos(0, 0)}, robots), {})

    def test_dead_operator_prevents_fire(self):
        game = self.make_micro_game()
        game.entities[2].hp = 0
        self.assertEqual(game.step(BASELINE), [])

    def test_seed_and_mirror_preserve_equipment_and_unique_occupancy(self):
        a, b = make_scenario(101), make_scenario(101, True)
        self.assertEqual([e.dump() for e in a], [e.dump() for e in make_scenario(101)])
        occupied = [p for e in a for p in e.cells()]
        self.assertEqual(len(occupied), len(set(occupied)))
        for left, right in zip(a, b):
            self.assertEqual({Pos(40-p.x, p.y) for p in left.cells()}, set(right.cells()))
            self.assertEqual(left.hp, right.hp)

    def test_equal_distance_choice_can_change_after_collision(self):
        robot = Entity(30001, 'smallRobot', Pos(20, 16), 40, 40)
        base = Entity(1, 'station', Pos(7, 16), 1500, 1500)
        options = [Pos(19, 15), Pos(19, 16), Pos(19, 17)]
        choices = {choose_robot_step(robot, options, base, turn, 1101, False)
                   for turn in range(1, 9)}
        self.assertGreater(len(choices), 1)

    def test_same_policy_same_scenario_same_result(self):
        first = Night(101).run(BASELINE, record=False)
        second = Night(101).run(copy.deepcopy(BASELINE), record=False)
        self.assertEqual(first, second)


if __name__ == '__main__':
    unittest.main()
