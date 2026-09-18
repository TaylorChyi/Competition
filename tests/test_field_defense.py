"""Deterministic regressions from field-review mechanisms, not a guessed replay."""
import unittest
from pathlib import Path
import sys
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parents[1]/"CoreGeek/src")]
from unittest.mock import patch
from agent.protocol import Turn, Pos
from agent.brain import decide, _tower_pairs
from agent.guard import exposure, safer_step, station_side_rank
from agent.fire_control import targets


def unit(uid,kind,x,y,hp=220,level=1,**extras):
    return dict(id=uid,roleType=kind,pos={'x':x,'y':y},health=hp,level=level,**extras)


def state(roles,robots=(),round_no=71):
    return {'roundNo':round_no,'mapInfo':{'width':41,'height':32,'zones':[]},
            'teamOur':{'type':'challenger','goldNum':0,'roles':roles},
            'teamEnemy':{'roles':[]},'robot':{'roles':list(robots)}}


def robot(uid,x,y,hp=40,kind='smallRobot',team='challenger'):
    return unit(uid,kind,x,y,hp,targetTeam=team)


class FieldDefenseChecks(unittest.TestCase):
    def test_closer_building_does_not_discount_operator_damage(self):
        turn=Turn.load(state([unit(1,'worker',5,5),unit(2,'railgun',6,5,1000)],
                             [robot(10,8,5,500,'largeRobot')]))
        self.assertEqual(exposure(turn,Pos(5,5),approaching=False),20)

    def test_healthy_operator_keeps_firing_instead_of_minor_sidesteps(self):
        payload=state([unit(1,'worker',5,5),unit(2,'railgun',6,5,1000)],
                      [robot(10,8,5)])
        commands=decide(payload)
        self.assertNotIn('1',commands)
        self.assertEqual(commands['2']['action'],'attack')

    def test_mortally_exposed_operator_moves_but_retains_control_range(self):
        turn=Turn.load(state([unit(1,'worker',6,5,30),unit(2,'railgun',5,5,1000)],
                             [robot(10,9,5,800,'bossRobot')]))
        step=safer_step(turn,turn.controllable()[0],turn.weapons()[0],set())
        self.assertIsNotNone(step)
        self.assertLess(exposure(turn,step),exposure(turn,Pos(6,5)))
        self.assertLessEqual(max(abs(step.x-5),abs(step.y-5)),1)

    def test_preparation_moves_to_station_side_before_night(self):
        payload=state([unit(1,'worker',9,5),unit(2,'railgun',8,5,1000),
                       unit(3,'station',6,5,1500)],round_no=66)
        cmd=decide(payload,economy=False)['1']
        self.assertEqual(cmd['action'],'move')
        self.assertLess(cmd['targetPos'][0]['x'],9)

    def test_equal_base_distance_preparation_respects_both_camp_orientations(self):
        for mirrored in (False,True):
            def point(x,y):
                return (40-x,31-y) if mirrored else (x,y)
            bx,by=(9,22) if mirrored else (30,10)
            tx,ty=point(29,11);rx,ry=point(29,10);sx,sy=point(30,11)
            turn=Turn.load(state([unit(1,'worker',rx,ry),unit(2,'railgun',tx,ty,1000),
                                 unit(3,'station',bx,by,1500)],round_no=66))
            role=turn.controllable()[0];tower=turn.weapons()[0]
            self.assertLess(station_side_rank(turn,Pos(sx,sy),tower.pos),
                            station_side_rank(turn,role.pos,tower.pos))
            step=safer_step(turn,role,tower,set(),preparing=True)
            self.assertEqual(step,Pos(sx,sy))

    def test_missing_operators_use_stronger_adjacent_ready_gun(self):
        turn=Turn.load(state([unit(1,'pioneer',5,5),unit(2,'railgun',4,5,1000),
                             unit(3,'railgun',6,5,2000,level=3)], [robot(10,8,5,500)]))
        pair=_tower_pairs(turn)
        self.assertEqual(pair[0][1].unit_id,3)

    def test_busy_operator_excluded_before_assignment(self):
        turn=Turn.load(state([unit(1,'pioneer',5,5),unit(4,'worker',6,6),
                             unit(2,'railgun',4,5,1000),unit(3,'railgun',6,5,2000,level=3)],
                             [robot(10,8,5,500)]))
        pair=_tower_pairs(turn,excluded={1})
        self.assertEqual([(r.unit_id,t.unit_id) for r,t in pair],[(4,3)])

    def test_mortal_risk_can_escape_one_step_beyond_tower_control(self):
        turn=Turn.load(state([unit(1,'worker',6,5,30),unit(2,'railgun',5,5,1000)],
                             [robot(10,3,5,800,'bossRobot')]))
        step=safer_step(turn,turn.controllable()[0],turn.weapons()[0],set())
        self.assertIsNotNone(step)
        self.assertGreater(max(abs(step.x-5),abs(step.y-5)),1)
        self.assertLess(exposure(turn,step,approaching=False),30)

    def test_survivable_escape_beats_large_but_still_lethal_reduction(self):
        turn=Turn.load(state([unit(1,'worker',6,5,20),unit(2,'railgun',5,5,1000)]))
        def danger(_turn,pos,**kwargs):
            return 100 if pos==Pos(6,5) else 0 if pos.x==7 else 50
        with patch('agent.guard.exposure',side_effect=danger):
            step=safer_step(turn,turn.controllable()[0],turn.weapons()[0],set())
        self.assertEqual(step.x,7)

    def test_escaped_operator_does_not_walk_back_into_lethal_range(self):
        payload=state([unit(1,'worker',7,5,30),unit(2,'railgun',5,5,1000)],
                      [robot(10,3,5,800,'bossRobot')])
        commands=decide(payload)
        # Waiting and continuing a safe retreat are both acceptable. The
        # business requirement is not to re-enter the boss's lethal range.
        if commands:
            self.assertEqual(set(commands),{'1'})
            command=commands['1']
            self.assertEqual(command['action'],'move')
            target=Pos.load(command['targetPos'][0])
            self.assertEqual(max(abs(target.x-7),abs(target.y-5)),1)
            self.assertGreater(max(abs(target.x-3),abs(target.y-5)),3)

    def test_operator_threat_is_not_ignored_because_base_is_farther(self):
        turn=Turn.load(state([unit(1,'worker',6,6,30),unit(2,'railgun',6,5,1000),
                             unit(3,'station',0,1,1500)],
                             [robot(10,8,7),robot(11,3,2)]))
        self.assertEqual(targets(turn,turn.weapons()[0],{}),[Pos(8,7)])

    def test_three_guns_may_legitimately_focus_same_high_hp_target(self):
        turn=Turn.load(state([unit(2,'railgun',4,5,1000),unit(3,'railgun',5,5,1000),
                             unit(4,'railgun',6,5,1000)], [robot(10,8,5,500,'largeRobot')]))
        reserved={}
        aimed=[targets(turn,t,reserved) for t in turn.weapons()]
        self.assertEqual(aimed,[[Pos(8,5)]]*3)
        self.assertEqual(reserved[10],30)

    def test_rocket_counts_all_same_cell_robot_ids(self):
        turn=Turn.load(state([unit(2,'rocket',4,5,1000)],
                             [robot(10,8,5),robot(11,8,5)]))
        reserved={};targets(turn,turn.weapons()[0],reserved)
        self.assertEqual(reserved,{10:20,11:20})

    def test_foreign_robot_alone_does_not_trigger_fire_or_evasion(self):
        payload=state([unit(1,'worker',5,5,20),unit(2,'railgun',6,5,1000)],
                      [robot(10,8,5,800,'bossRobot','defender')])
        self.assertEqual(decide(payload),{})

    def test_no_target_in_range_can_legitimately_produce_empty_night_command(self):
        payload=state([unit(1,'worker',5,5),unit(2,'railgun',6,5,1000)],
                      [robot(10,30,20)])
        self.assertEqual(decide(payload),{})

if __name__=='__main__':
    unittest.main()
