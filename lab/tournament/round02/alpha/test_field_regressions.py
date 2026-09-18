"""Deterministic field regressions; no simulated win-rate claims."""
import unittest
from dataclasses import replace

from lab.tournament.round02.alpha.economy import develop, route, urgent_refit, use_carried
from lab.tournament.round02.alpha.protocol import Pos, Robot, Turn, Unit, distance, station_footprint


def unit(uid, kind, pos, health, level=1, backpack=(), capacity=40):
    return Unit(uid,Pos(*pos),kind,health,level,0,0,capacity,tuple(backpack))


def observation(role, *, day=True, base_health=900, base_level=1, gold=150, extra=()):
    base=unit(20013,'station',(32,8),base_health,base_level)
    return Turn(161 if day else 231,day,gold,41,32,
                {Pos(25,20):'weaponShop',Pos(20,16):'vendor'},
                (base,role)+tuple(extra),(),(), 'defender',
                {'copper':5,'iron':3,'stone':1},
                {'StationUpgradeVoucher1':100,'StationUpgradeVoucher2':150,'Medicine':10})


class FieldEconomyTests(unittest.TestCase):
    def test_carried_voucher_returns_from_reported_position_then_uses(self):
        role=unit(20011,'pioneer',(30,11),200,backpack=('StationUpgradeVoucher1',))
        turn=observation(role,day=False,base_health=1400)
        for _ in range(12):
            commands={}
            self.assertTrue(use_carried(turn,role,set(),commands,night=True))
            cmd=commands[role.unit_id]
            if cmd['action']=='use':
                self.assertLessEqual(distance(role.pos,turn.station().pos),1)
                self.assertEqual(cmd['targetPos'],[{'x':32,'y':8}])
                break
            self.assertEqual(cmd['action'],'move')
            role=replace(role,pos=Pos.load(cmd['targetPos'][0]))
            turn=replace(turn,ours=(turn.station(),role))
        else:
            self.fail('voucher failed to reach the station')

    def test_night_upgrade_is_not_delayed_until_half_health(self):
        role=unit(20011,'pioneer',(31,9),200,backpack=('StationUpgradeVoucher1',))
        turn=observation(role,day=False,base_health=1500)
        commands={}
        self.assertTrue(use_carried(turn,role,set(),commands,night=True))
        self.assertEqual(commands[role.unit_id]['action'],'use')

    def test_footprint_corner_uses_conservative_anchor_adjacency(self):
        role=unit(20011,'pioneer',(34,7),200,backpack=('StationUpgradeVoucher1',))
        turn=observation(role)
        self.assertEqual(station_footprint(turn.station().pos),
                         (Pos(32,8),Pos(33,8),Pos(32,7),Pos(33,7)))
        commands={};use_carried(turn,role,set(),commands)
        self.assertEqual(commands[role.unit_id]['action'],'move')

    def test_night_near_shop_never_purchases_or_departs(self):
        role=unit(20011,'pioneer',(24,20),200)
        commands={}
        self.assertFalse(urgent_refit(observation(role,day=False),role,set(),commands))
        self.assertEqual(commands,{})

    def test_unsold_ore_is_not_cash(self):
        role=unit(20011,'pioneer',(24,20),200)
        worker=unit(20010,'worker',(20,15),220,backpack=('copper',)*20)
        self.assertFalse(urgent_refit(observation(role,gold=0,extra=(worker,)),role,set(),{}))

    def test_prior_build_reserves_cash(self):
        role=unit(20011,'pioneer',(24,20),200)
        commands={20010:{'action':'build','name':'railgun'}}
        self.assertFalse(urgent_refit(observation(role,gold=100),role,set(),commands))

    def test_full_backpack_does_not_buy_medicine_or_voucher(self):
        role=unit(20011,'pioneer',(24,20),40,backpack=('copper',),capacity=1)
        turn=observation(role,gold=500)
        self.assertFalse(urgent_refit(turn,role,set(),{}))
        commands={};develop(turn,role,set(),commands)
        self.assertFalse(any(c['action']=='buy' for c in commands.values()))

    def test_level_two_station_reserves_150_before_precautionary_medicine(self):
        role=unit(20011,'pioneer',(24,20),100)
        turn=observation(role,gold=150,base_level=2,base_health=1800)
        commands={};develop(turn,role,set(),commands)
        self.assertEqual(commands[role.unit_id]['name'],'StationUpgradeVoucher2')

    def test_sunset_does_not_start_unfinishable_refill_trip(self):
        role=unit(20011,'pioneer',(31,9),200)
        turn=replace(observation(role),round_no=200)
        self.assertFalse(urgent_refit(turn,role,set(),{}))

    def test_regular_develop_cannot_bypass_sunset_purchase_deadline(self):
        role=unit(20011,'pioneer',(24,20),200)
        turn=replace(observation(role),round_no=200)
        commands={};develop(turn,role,set(),commands)
        self.assertEqual(commands,{})

    def test_regular_develop_never_buys_at_night(self):
        role=unit(20011,'pioneer',(24,20),40)
        commands={};develop(observation(role,day=False),role,set(),commands)
        self.assertEqual(commands,{})

    def test_lethal_nearby_base_risk_preempts_operator_medicine(self):
        role=unit(20011,'pioneer',(31,9),100,backpack=('Medicine','StationUpgradeVoucher1'))
        turn=replace(observation(role,day=False,base_health=40),
                     robots=(Robot(30001,Pos(32,5),100,'defender','bossRobot'),))
        commands={};use_carried(turn,role,set(),commands,night=True)
        self.assertEqual(commands[role.unit_id]['name'],'StationUpgradeVoucher1')
        self.assertEqual(commands[role.unit_id]['targetPos'],[{'x':32,'y':8}])

    def test_nonlethal_or_distant_or_foreign_risk_keeps_medicine_first(self):
        role=unit(20011,'pioneer',(31,9),100,backpack=('Medicine','StationUpgradeVoucher1'))
        for hp,pos,team in ((41,Pos(32,5),'defender'),(40,Pos(32,3),'defender'),
                            (40,Pos(32,5),'challenger')):
            with self.subTest(hp=hp,pos=pos,team=team):
                turn=replace(observation(role,day=False,base_health=hp),
                             robots=(Robot(30001,pos,100,team,'bossRobot'),))
                commands={};use_carried(turn,role,set(),commands,night=True)
                self.assertEqual(commands[role.unit_id]['name'],'Medicine')

    def test_lethal_risk_requires_valid_anchor_range_and_unused_voucher(self):
        for pos,items,previous in (((30,9),('Medicine','StationUpgradeVoucher1'),{}),
                                  ((31,9),('Medicine','StationUpgradeVoucher2'),{}),
                                  ((31,9),('Medicine','StationUpgradeVoucher1'),
                                   {20010:{'action':'use','name':'StationUpgradeVoucher1',
                                           'targetPos':[{'x':32,'y':8}]}})):
            role=unit(20011,'pioneer',pos,100,backpack=items)
            turn=replace(observation(role,day=False,base_health=40),
                         robots=(Robot(30001,Pos(32,5),100,'defender','bossRobot'),))
            commands=dict(previous);use_carried(turn,role,set(),commands,night=True)
            self.assertEqual(commands[role.unit_id]['name'],'Medicine')

    def test_failed_one_step_vendor_entry_changes_entry_then_sells(self):
        role=unit(20010,'worker',(19,14),220,backpack=('copper',)*7)
        enemy=unit(10012,'worker',(18,14),220)
        turn=replace(observation(role,gold=0),enemies=(enemy,))
        original=route(turn,role,[Pos(20,16)],set())
        self.assertEqual(original[0],Pos(19,15))
        turn=replace(turn,failed_actions=frozenset({role.unit_id}))
        alternative=route(turn,role,[Pos(20,16)],set())
        self.assertNotEqual(alternative[0],original[0])
        self.assertLessEqual(distance(role.pos,alternative[0]),1)
        self.assertTrue(turn.land(alternative[0]))
        self.assertNotIn(alternative[0],turn.blocked(role))
        self.assertLessEqual(distance(alternative[-1],Pos(20,16)),1)
        # Repeated identical failed observations do not retry the contested
        # default entry; no process-global or seed-dependent state is needed.
        self.assertEqual(route(turn,role,[Pos(20,16)],set()),alternative)
        role=replace(role,pos=alternative[-1])
        turn=replace(turn,ours=(turn.station(),role),failed_actions=frozenset())
        commands={};develop(turn,role,set(),commands)
        self.assertEqual(commands[role.unit_id],{'action':'sell','name':'copper','num':7})

    def test_already_adjacent_vendor_needs_no_reroute_after_failed_action(self):
        role=unit(20010,'worker',(20,15),220,backpack=('copper',)*7)
        turn=replace(observation(role),failed_actions=frozenset({role.unit_id}))
        self.assertEqual(route(turn,role,[Pos(20,16)],set()),())


if __name__=='__main__':
    unittest.main()
