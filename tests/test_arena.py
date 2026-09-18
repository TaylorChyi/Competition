"""Micro-scenarios verifying the local simulator's declared settlement rules."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'CoreGeek/src')]
from agent.brain import decide
from agent.protocol import Pos
from lab.arena import Arena, Piece, TEAMS, ray_hits


class ArenaChecks(unittest.TestCase):
    def test_robot_attacks_its_declared_camp_not_nearer_rival(self):
        game = Arena(1)
        game.pieces = [Piece(10013, 'station', Pos(5,5), 1500, 'challenger'),
                       Piece(20013, 'station', Pos(8,5), 1500, 'defender'),
                       Piece(30000, 'smallRobot', Pos(7,5), 40, 'challenger')]
        game.number = 71
        game.settle(dict.fromkeys(TEAMS, {}))
        self.assertEqual(game.base('challenger').hp, 1495)
        self.assertEqual(game.base('defender').hp, 1500)

    def test_lethal_robot_attack_still_settles_and_rocket_cools_down(self):
        game = Arena(1)
        game.pieces = [Piece(10013, 'station', Pos(0,5), 1500, 'challenger'),
                       Piece(20013, 'station', Pos(35,5), 1500, 'defender'),
                       Piece(1, 'worker', Pos(2,4), 220, 'challenger'),
                       Piece(2, 'rocket', Pos(3,5), 1000, 'challenger'),
                       Piece(30000, 'smallRobot', Pos(5,5), 20, 'challenger')]
        game.number = 71
        attack = {'2': {'action': 'attack', 'controllerId': '1', 'targetPos': [{'x':5,'y':5}]}}
        game.settle({'challenger': attack, 'defender': {}})
        self.assertEqual(game.pieces[-1].hp, 0)
        self.assertEqual(game.pieces[3].hp, 995)
        self.assertEqual(game.pieces[3].ready, 75)
        self.assertEqual(game.metrics['challenger']['kills'], 1)
        game.number = 72
        game.settle({'challenger': attack, 'defender': {}})
        self.assertFalse(game.results['challenger']['2'])

    def test_dawn_preserves_building_damage_and_revives_only_later(self):
        game = Arena(1)
        game.base('challenger').hp = 500
        game.pieces.append(Piece(40001, 'rocket', Pos(6,22), 75, 'challenger'))
        game.pieces.append(Piece(30000, 'smallRobot', Pos(10,10), 40, 'challenger'))
        worker = next(p for p in game.pieces if p.uid == 10010)
        worker.hp = 0
        game.number = 130
        game.begin()
        self.assertFalse(any(p.kind == 'smallRobot' for p in game.pieces))
        self.assertEqual(game.base('challenger').hp, 500)
        self.assertEqual(game.pieces[-1].hp, 75)
        self.assertEqual(worker.hp, 0)
        game.number = 150
        game.begin()
        self.assertEqual(worker.hp, 220)

    def test_mine_rng_does_not_change_scheduled_wave(self):
        a, b = Arena(123), Arena(123)
        for _ in range(57):
            b.rng.random()
        a.spawn(0)
        b.spawn(0)
        self.assertEqual([(p.kind,p.pos,p.team) for p in a.pieces],
                         [(p.kind,p.pos,p.team) for p in b.pieces])

    def test_ray_hits_foreign_blocker_before_intended_robot(self):
        robots = [Piece(1,'smallRobot',Pos(4,1),40,'defender'),
                  Piece(2,'smallRobot',Pos(7,1),40,'challenger')]
        self.assertEqual([p.uid for p in ray_hits(Pos(1,1),Pos(7,1),robots)], [1,2])

    def test_first_day_builds_from_real_wallet_without_free_equipment(self):
        game = Arena(11)
        for _ in range(70):
            game.begin()
            game.settle({team: decide(game.observation(team)) for team in TEAMS})
        for team in TEAMS:
            towers = [p for p in game.pieces if p.team == team and p.kind in ('gatling','railgun','rocket')]
            self.assertEqual(len(towers), 3)
            self.assertTrue(all(p.level == 1 for p in towers))
            self.assertEqual(game.gold[team], 0)
            self.assertEqual(game.metrics[team]['invalidCommands'], 0)


if __name__ == '__main__':
    unittest.main()
