"""Keep front-line upgrades available and carried coupons legal in mixed defense."""
import unittest
from dataclasses import replace
from agent.protocol import Pos,Unit,Turn
from agent.economy import develop,use_carried

class BalancedUpgrades(unittest.TestCase):
    def world(self,base_hp=1320,rail_level=1,gold=100):
        role=Unit(1,Pos(25,19),'pioneer',200,1,0,0,40,('Medicine',))
        base=Unit(9,Pos(30,10),'station',base_hp,1,0,0,None,())
        guns=(Unit(20,Pos(29,11),'railgun',345,rail_level,0,0,None,()),
              Unit(21,Pos(31,11),'railgun',1000,rail_level,0,0,None,()),
              Unit(22,Pos(32,9),'rocket',1500,2,0,0,None,()))
        t=Turn(300,True,gold,41,32,{Pos(25,20):'weaponShop',Pos(20,16):'vendor'},
               (role,base)+guns,(),(),'defender',{'copper':5},
               {'Medicine':10,'WeaponUpgradeVoucher1':100,'WeaponUpgradeVoucher2':150,'StationUpgradeVoucher1':100})
        return t,role
    def test_100_cash_upgrades_front_gun_instead_of_waiting_for_150(self):
        t,u=self.world();c={};develop(t,u,set(),c)
        self.assertEqual(c[u.unit_id],{'action':'buy','name':'WeaponUpgradeVoucher1','num':1})
    def test_even_150_cash_does_not_skip_existing_level_one_guns(self):
        t,u=self.world(gold=150);c={};develop(t,u,set(),c)
        self.assertEqual(c[u.unit_id]['name'],'WeaponUpgradeVoucher1')
    def test_urgent_station_still_first(self):
        t,u=self.world(base_hp=1100);c={};develop(t,u,set(),c)
        self.assertEqual(c[u.unit_id]['name'],'StationUpgradeVoucher1')
    def test_one_level_two_allows_rocket_three(self):
        t,u=self.world(gold=150)
        t=replace(t,ours=tuple(replace(x,level=2) if x.unit_id==20 else x for x in t.ours))
        c={};develop(t,u,set(),c)
        self.assertEqual(c[u.unit_id]['name'],'WeaponUpgradeVoucher2')
    def test_all_level_two_still_allows_rocket_three(self):
        t,u=self.world(rail_level=2,gold=150);c={};develop(t,u,set(),c)
        self.assertEqual(c[u.unit_id]['name'],'WeaponUpgradeVoucher2')


class FrontVoucher(unittest.TestCase):
    def world(self,name='WeaponUpgradeVoucher1',levels=(1,1,1)):
        t,u=BalancedUpgrades().world()
        u=replace(u,pos=Pos(30,10),backpack=(name,))
        guns=tuple(replace(x,level=levels[x.unit_id-20],health=1000) if x.unit_id in (20,21,22) else u if x.unit_id==u.unit_id else x for x in t.ours)
        return replace(t,ours=guns),u
    def test_first_voucher_front_even_rocket_nearby(self):
        t,u=self.world();c={};self.assertTrue(use_carried(t,u,set(),c))
        self.assertEqual(c[u.unit_id],{'action':'use','name':'WeaponUpgradeVoucher1','targetPos':[{'x':29,'y':11}]})
    def test_second_front_precedes_level_one_rocket(self):
        t,u=self.world(levels=(2,1,1));c={};use_carried(t,u,set(),c)
        self.assertEqual(c[u.unit_id]['targetPos'],[{'x':31,'y':11}])
    def test_after_fronts_rocket_gets_first_tier(self):
        t,u=self.world(levels=(2,2,1));u=replace(u,pos=Pos(31,10));t=replace(t,ours=tuple(u if x.unit_id==u.unit_id else x for x in t.ours))
        c={};use_carried(t,u,set(),c)
        self.assertEqual(c[u.unit_id]['targetPos'],[{'x':32,'y':9}])
    def test_second_tier_still_prioritizes_rocket(self):
        t,u=self.world('WeaponUpgradeVoucher2',(2,2,2));u=replace(u,pos=Pos(31,10));t=replace(t,ours=tuple(u if x.unit_id==u.unit_id else x for x in t.ours))
        c={};use_carried(t,u,set(),c)
        self.assertEqual(c[u.unit_id]['targetPos'],[{'x':32,'y':9}])

    def test_night_uses_only_adjacent_weapon_without_walking_to_front(self):
        t,u=self.world()
        u=replace(u,pos=Pos(32,8));t=replace(t,is_day=False,ours=tuple(u if x.unit_id==u.unit_id else x for x in t.ours))
        c={};self.assertTrue(use_carried(t,u,set(),c,night=True))
        self.assertEqual(c[u.unit_id],{'action':'use','name':'WeaponUpgradeVoucher1','targetPos':[{'x':32,'y':9}]})
        u=replace(u,pos=Pos(20,0));t=replace(t,ours=tuple(u if x.unit_id==u.unit_id else x for x in t.ours))
        c={};self.assertFalse(use_carried(t,u,set(),c,night=True));self.assertEqual(c,{})
