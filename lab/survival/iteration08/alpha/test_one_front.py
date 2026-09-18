import unittest
from dataclasses import replace
from .protocol import Pos,Unit,Turn
from .economy import develop

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

if __name__=='__main__':unittest.main()
