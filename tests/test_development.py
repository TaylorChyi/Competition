"""Economy and survival regressions reproduced while debugging long matches."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT),str(ROOT/'CoreGeek/src')]
from agent.brain import decide, _tower_sites
from agent.economy import develop
from agent.guard import safer_step
from agent.grid import next_step
from agent.protocol import Pos, Turn, distance
from lab.arena import Arena, Piece, TEAMS, wave_counts
from test_baseline import state, unit


def market_state(gold=100):
    payload = state(150,gold,roles=[unit(10013,'station',10,10),
                                  unit(10011,'pioneer',19,10),unit(40000,'railgun',12,10)])
    payload['teamOur']['roles'][0]['health']=300
    payload['mapInfo']['zones']=[{'pos':{'x':20,'y':10},'neutralType':'weaponShop'},
                               {'pos':{'x':20,'y':16},'neutralType':'vendor'}]
    payload['vendorShopList']=[{'name':'copper','price':5}]
    payload['weaponShopList']=[{'name':'WeaponUpgradeVoucher1','price':100},
                              {'name':'StationUpgradeVoucher1','price':100},
                              {'name':'StationUpgradeVoucher2','price':150}]
    return payload


class DevelopmentChecks(unittest.TestCase):
    def test_funded_base_purchase_finishes_at_sunset_and_early_night(self):
        for number in (200,201):
            payload=market_state();payload['roundNo']=number
            payload['teamOur']['roles'].append(unit(1,'worker',13,11))
            commands=decide(payload)
            self.assertEqual(commands['10011'],{'action':'buy','name':'StationUpgradeVoucher1','num':1})
            self.assertFalse(any(c['action']=='build' for c in commands.values()))

    def test_carried_weapon_upgrade_can_be_used_at_night(self):
        payload=market_state(0);payload['roundNo']=201
        role=payload['teamOur']['roles'][1]
        role['pos']={'x':13,'y':10};role['backpack']=['WeaponUpgradeVoucher1']
        self.assertEqual(decide(payload)['10011'],{'action':'use','name':'WeaponUpgradeVoucher1',
                                                  'targetPos':[{'x':12,'y':10}]})

    def test_miner_prefers_income_it_can_collect_and_sell_before_competitor(self):
        payload=market_state(0)
        payload['teamOur']['roles'].append(unit(1,'worker',18,16))
        payload['teamEnemy']={'roles':[unit(20010,'worker',26,16)]}
        payload['mapInfo']['zones'] += [
            {'pos':{'x':25,'y':16},'neutralType':'copper'},
            {'pos':{'x':20,'y':21},'neutralType':'iron'}]
        payload['vendorShopList'].append({'name':'iron','price':3})
        turn=Turn.load(payload);commands={};claimed=set()
        develop(turn,turn.workers()[0],claimed,commands)
        self.assertIn(Pos(20,21),claimed)
        self.assertNotIn(Pos(25,16),claimed)

    def test_active_miner_keeps_its_mine_when_another_worker_arrives(self):
        payload=market_state(0)
        payload['teamOur']['roles'] += [unit(1,'worker',15,10),unit(2,'worker',17,10)]
        payload['mapInfo']['zones'] += [
            {'pos':{'x':18,'y':10},'neutralType':'copper'},
            {'pos':{'x':15,'y':8},'neutralType':'copper'}]
        turn=Turn.load(payload);commands={};claimed=set()
        for role in turn.workers():
            develop(turn,role,claimed,commands)
        self.assertEqual(commands[2],{'action':'collect','targetPos':[{'x':18,'y':10}]})

    def test_operator_steps_behind_tower_when_targeted_robot_approaches(self):
        payload=state(71,roles=[unit(1,'worker',4,5),unit(2,'railgun',5,5)])
        robot=unit(30000,'bossRobot',4,2)
        payload['robot']['roles']=[robot]
        turn=Turn.load(payload)
        step=safer_step(turn,turn.workers()[0],turn.weapons()[0],set())
        self.assertIsNotNone(step)
        self.assertGreater(distance(step,Pos(4,2)),distance(Pos(4,5),Pos(4,2)))
        self.assertLessEqual(distance(step,Pos(5,5)),1)
        robot['targetTeam']='defender'
        turn=Turn.load(payload)
        self.assertIsNone(safer_step(turn,turn.workers()[0],turn.weapons()[0],set()))

    def test_rebuild_replaces_damaged_tower_with_paid_level_one_tower(self):
        g=Arena(1,commerce=True);g.number=20
        g.pieces.append(Piece(40000,'railgun',Pos(9,22),80,'challenger',2))
        worker=next(p for p in g.pieces if p.uid==10010);worker.pos=Pos(10,22)
        g.next_build['challenger']=40001;g.gold['challenger']=25
        g.settle({'challenger':{str(worker.uid):{'action':'build','name':'railgun',
                   'targetPos':[{'x':9,'y':22}]}},'defender':{}})
        towers=[p for p in g.living() if p.kind=='railgun']
        self.assertEqual([(p.hp,p.level) for p in towers],[(1000,1)])
        self.assertEqual(g.gold['challenger'],0)

    def test_last_ore_race_is_counted_as_failure_and_resource_conflict(self):
        g=Arena(1,commerce=True);g.number=20;mine=Pos(20,10)
        g.mines={mine:1};g.mine_kinds={mine:'copper'}
        commands={}
        for team,uid,pos in [('challenger',10010,Pos(19,10)),('defender',20010,Pos(21,10))]:
            worker=next(p for p in g.pieces if p.uid==uid);worker.pos=pos
            commands[team]={str(uid):{'action':'collect','targetPos':[mine.dump()]}}
        g.settle(commands)
        self.assertEqual(g.metrics['defender']['resourceConflicts'],1)
        self.assertEqual(g.metrics['defender']['invalidCommands'],1)
        self.assertFalse(g.results['defender']['20010'])

    def test_saves_for_damaged_base_instead_of_cheaper_weapon(self):
        payload=market_state()
        payload['teamOur']['roles'][0]['level']=2
        turn=Turn.load(payload);commands={}
        develop(turn,turn.controllable()[0],set(),commands)
        self.assertEqual(commands,{})

    def test_purchase_uses_current_shop_price(self):
        payload=market_state(120)
        payload['weaponShopList'][1]['price']=120
        command=decide(payload)['10011']
        self.assertEqual(command,{'action':'buy','name':'StationUpgradeVoucher1','num':1})

    def test_pioneer_can_cross_planned_wall_line_to_reach_shop(self):
        payload=market_state()
        payload['teamOur']['roles'][1]['pos']={'x':13,'y':10}
        command=decide(payload)['10011']
        self.assertEqual(command['action'],'move')
        self.assertGreater(command['targetPos'][0]['x'],13)

    def test_uses_upgrade_even_on_last_daylight_turn(self):
        payload=market_state(0);payload['roundNo']=200
        role=payload['teamOur']['roles'][1]
        role['pos']={'x':9,'y':10};role['backpack']=['StationUpgradeVoucher1']
        self.assertEqual(decide(payload)['10011'],{'action':'use','name':'StationUpgradeVoucher1',
                                                   'targetPos':[{'x':10,'y':10}]})

    def test_night_repair_moves_into_range_when_base_is_critical(self):
        payload=market_state(0);payload['roundNo']=201
        role=payload['teamOur']['roles'][1]
        role['pos']={'x':8,'y':10};role['backpack']=['StationUpgradeVoucher1']
        command=decide(payload)['10011']
        self.assertEqual(command['action'],'move')
        self.assertEqual(command['targetPos'][0]['x'],9)

    def test_failed_move_tries_another_first_step(self):
        payload=state(30,roles=[unit(1,'worker',1,1)])
        turn=Turn.load(payload)
        original=next_step(turn,turn.workers()[0],Pos(5,5))
        payload['lastRoundRoleActionResults']={'1':False}
        retry=Turn.load(payload)
        self.assertNotEqual(next_step(retry,retry.workers()[0],Pos(5,5)),original)

    def test_front_towers_leave_separate_operating_cells(self):
        for x,y in ((7,24),(32,8)):
            turn=Turn.load(state(roles=[unit(1,'station',x,y)]))
            sites=_tower_sites(turn)
            self.assertEqual(len(sites),3)
            self.assertTrue(all(distance(a,b)>=2 for i,a in enumerate(sites) for b in sites[i+1:]))
            self.assertTrue(all((p.x>=x) if x<20 else (p.x<=x+1) for p in sites))

    def test_small_threat_is_cleared_before_high_hp_boss(self):
        payload=state(71,roles=[unit(1,'worker',1,1),unit(2,'railgun',2,2)])
        boss=unit(30000,'bossRobot',4,4);boss['health']=800
        small=unit(30001,'smallRobot',5,2);small['health']=10
        payload['robot']['roles']=[boss,small]
        self.assertEqual(decide(payload)['2']['targetPos'],[{'x':5,'y':2}])

    def test_upgrade_heals_and_consumes_exactly_one_purchased_voucher(self):
        g=Arena(1,commerce=True);g.number=150
        base=g.base('challenger');base.hp=120
        worker=next(p for p in g.pieces if p.uid==10010)
        worker.pos=Pos(base.pos.x-1,base.pos.y)
        worker.backpack=['StationUpgradeVoucher1']
        command={str(worker.uid):{'action':'use','name':'StationUpgradeVoucher1','targetPos':[base.pos.dump()]}}
        g.settle({'challenger':command,'defender':{}})
        self.assertEqual((base.level,base.hp,worker.backpack),(2,3000,[]))
        g.settle({'challenger':command,'defender':{}})
        self.assertFalse(g.results['challenger'][str(worker.uid)])
        self.assertEqual(base.level,2)

    def test_resource_refresh_never_occupies_a_moved_unit(self):
        g=Arena(7,commerce=True);g.number=10
        g.mines={Pos(1,1):0};g.mine_kinds={Pos(1,1):'copper'}
        class Choose:
            def choice(self,free):
                occupied={c for p in g.living() for c in p.cells()}
                self_test.assertFalse(occupied.intersection(free))
                return free[0]
        self_test=self;g.rng=Choose()
        worker=next(p for p in g.pieces if p.uid==10010)
        dest=Pos(worker.pos.x-1,worker.pos.y)
        g.settle({'challenger':{str(worker.uid):{'action':'move','targetPos':[dest.dump()]}},'defender':{}})
        self.assertNotIn(dest,g.mines)

    def test_long_wave_extension_preserves_first_three_waves_and_increases(self):
        self.assertEqual(wave_counts('heavy',1),(20,10,2,0))
        self.assertEqual(wave_counts('heavy',9),(52,28,5,2))
        self.assertTrue(all(b>=a for a,b in zip(wave_counts('heavy',8),wave_counts('heavy',9))))


if __name__=='__main__':
    unittest.main()
