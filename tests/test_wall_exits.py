"""A completed wall layout must not permanently trap its own operators."""
from dataclasses import replace
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'CoreGeek/src'))
from agent.brain import _tower_sites, _wall_order
from agent.grid import shortest_path
from agent.protocol import Pos, Turn
from test_baseline import state, unit


class WallExitChecks(unittest.TestCase):
    def test_every_inner_operator_position_can_exit_on_both_sides(self):
        for bx, by, rx, ry in ((9, 22, 10, 20), (30, 10, 30, 11)):
            payload = state(70, gold=0, roles=[
                unit(1, 'worker', rx, ry), unit(2, 'station', bx, by),
            ])
            turn = Turn.load(payload)
            walls, guns = _wall_order(turn), _tower_sites(turn)
            self.assertEqual(len(walls), 12)
            self.assertEqual(len(set(walls)), 12)
            payload['teamOur']['roles'] += [
                unit(10 + i, 'wall', pos.x, pos.y) for i, pos in enumerate(walls)
            ] + [unit(50 + i, 'railgun', pos.x, pos.y) for i, pos in enumerate(guns)]
            turn = Turn.load(payload)
            worker = turn.controllable()[0]
            destination = Pos(bx + 5, by)
            self.assertIsNotNone(shortest_path(turn, worker, destination, set()))
            for x in range(bx - 1, bx + 3):
                for y in range(by - 2, by + 2):
                    pos = Pos(x, y)
                    if pos in turn.occupied_cells():
                        continue
                    actor = replace(worker, pos=pos)
                    local = replace(turn, ours=tuple(
                        actor if other.unit_id == actor.unit_id else other
                        for other in turn.ours
                    ))
                    with self.subTest(base=(bx, by), operator=pos):
                        self.assertIsNotNone(shortest_path(local, actor, destination, set()))


if __name__ == '__main__':
    unittest.main()
