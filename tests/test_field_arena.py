"""Document-backed field regressions; no inferred spawn or target-priority rules."""
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'CoreGeek/src')]
from agent.protocol import Pos, station_footprint
from lab.arena import Arena, Piece, TEAMS, wave_counts


class FieldArenaRules(unittest.TestCase):
    def test_station_is_two_by_two_from_top_left(self):
        # Interface Role note: size2*2, reported pos is top-left; y grows upward.
        self.assertEqual(set(station_footprint(Pos(7,24))),
                         {Pos(7,24),Pos(8,24),Pos(7,23),Pos(8,23)})

    def test_doc_interpretation_upgrade_from_station_footprint_edge(self):
        # Documentary interpretation, NOT field-engine acceptance evidence.
        # Task4.6: use within one cell of target building. Interface: base2*2.
        # (9,23) touches right edge(8,23), while anchor(7,24) is two cells away.
        game = Arena(22001, commerce=True)
        game.number = 169
        base = game.base('challenger')
        base.hp = 500
        pioneer = next(p for p in game.pieces if p.team=='challenger' and p.kind=='pioneer')
        pioneer.pos = Pos(base.pos.x+2,base.pos.y-1)
        pioneer.backpack = ['StationUpgradeVoucher1']
        commands = {team:{} for team in TEAMS}
        commands['challenger'][str(pioneer.uid)] = {
            'action':'use','name':'StationUpgradeVoucher1','targetPos':[base.pos.dump()]}
        game.settle(commands)
        self.assertEqual(base.level,2)
        self.assertEqual(base.hp,3000)
        self.assertEqual(pioneer.backpack,[])

    def test_night_death_revives_next_day_twenty_with_inventory(self):
        # Task4.5.2 explicit death/respawn timing and backpack retention.
        game = Arena(22001)
        worker = next(p for p in game.pieces if p.team=='challenger' and p.kind=='worker')
        game.number=92
        worker.hp=0
        worker.backpack=['iron','StationUpgradeVoucher1']
        game.number=149
        game.begin()
        self.assertEqual(worker.hp,0)
        game.begin()
        self.assertEqual(game.number,151)
        self.assertEqual(worker.hp,220)
        self.assertEqual(worker.backpack,['iron','StationUpgradeVoucher1'])

class FieldLifecycleRules(unittest.TestCase):
    def test_death_day_blocks_same_day_respawn(self):
        game=Arena(22001)
        worker=next(p for p in game.pieces if p.kind=='worker' and p.team=='challenger')
        worker.hp=0
        worker.died_round=140
        worker.backpack=['copper']
        game.number=150
        game.begin()
        self.assertEqual(worker.hp,0)
        game.number=280
        game.begin()
        self.assertEqual(worker.hp,220)
        self.assertEqual(worker.backpack,['copper'])

    def test_settlement_records_role_death_round(self):
        game=Arena(22001)
        worker=Piece(10010,'worker',Pos(10,10),5,'challenger')
        game.pieces=[Piece(10013,'station',Pos(1,25),1500,'challenger'),
                     Piece(20013,'station',Pos(35,25),1500,'defender'),worker,
                     Piece(30000,'smallRobot',Pos(10,11),40,'challenger')]
        game.number=92
        game.settle({t:{} for t in TEAMS})
        self.assertEqual(worker.hp,0)
        self.assertEqual(worker.died_round,92)


class FieldHypothesisProfiles(unittest.TestCase):
    """Configuration checks only; these mechanics are NOT all official facts."""
    def test_field_profile_matches_reported_totals_not_claimed_composition(self):
        self.assertEqual(sum(wave_counts('field',0)),35)
        self.assertEqual(sum(wave_counts('field',1)),36)

    def test_operators_profile_exercises_adversarial_target_priority(self):
        game=Arena(22001,priority='operators')
        worker=Piece(10010,'worker',Pos(10,10),220,'challenger')
        wall=Piece(40000,'wall',Pos(11,11),1000,'challenger')
        game.pieces=[Piece(10013,'station',Pos(1,25),1500,'challenger'),
                     Piece(20013,'station',Pos(35,25),1500,'defender'),worker,wall,
                     Piece(30000,'smallRobot',Pos(12,12),40,'challenger')]
        game.number=71
        game.settle({t:{} for t in TEAMS})
        self.assertEqual(worker.hp,215)
        self.assertEqual(wall.hp,1000)

    def test_reported_base_elimination_removes_team_units(self):
        game=Arena(22001)
        own=game.base('challenger')
        own.hp=5
        game.pieces.append(Piece(30000,'smallRobot',Pos(own.pos.x+2,own.pos.y),40,'challenger'))
        game.number=71
        game.settle({t:{} for t in TEAMS})
        self.assertEqual(own.hp,0)
        self.assertTrue(all(p.hp==0 for p in game.pieces
                            if p.team=='challenger' and p.kind!='smallRobot'))
        self.assertGreater(game.base('defender').hp,0)


if __name__=='__main__':
    unittest.main()
