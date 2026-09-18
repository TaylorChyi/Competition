import unittest
from dataclasses import replace
from .protocol import Pos,Unit,Turn
from .economy import develop

class FirstFirepower(unittest.TestCase):
    def world(self,hp=1400,gold=112,level=1):
        role=Unit(1,Pos(25,19),'pioneer',200,1,0,0,40,('Medicine',))
        base=Unit(9,Pos(30,10),'station',hp,2,0,0,None,())
        guns=tuple(Unit(i,Pos(28+i-20,11),'railgun',1000,level,0,0,None,()) for i in (20,21,22))
        turn=Turn(300,True,gold,41,32,{Pos(25,20):'weaponShop',Pos(20,16):'vendor'},
                  (base,role)+guns,(),(),'defender',{'copper':5},
                  {'Medicine':10,'WeaponUpgradeVoucher1':100,'WeaponUpgradeVoucher2':150,'StationUpgradeVoucher2':150})
        return turn,role

    def test_112_cash_can_buy_first_gun_when_station_costs_150(self):
        turn,role=self.world();commands={}
        self.assertTrue(develop(turn,role,set(),commands))
        self.assertEqual(commands[1]['name'],'WeaponUpgradeVoucher1')

    def test_affordable_station_remains_first(self):
        turn,role=self.world(gold=150);commands={};develop(turn,role,set(),commands)
        self.assertEqual(commands[1]['name'],'StationUpgradeVoucher2')

    def test_critical_base_and_already_upgraded_gun_keep_reserve(self):
        for hp,level in ((749,1),(1400,2)):
            turn,role=self.world(hp=hp,level=level);commands={};develop(turn,role,set(),commands)
            self.assertFalse(any(c.get('action')=='buy' for c in commands.values()))

    def test_prior_shared_cash_order_prevents_unfunded_purchase(self):
        turn,role=self.world();commands={2:{'action':'buy','name':'Medicine','num':2}}
        develop(turn,role,set(),commands)
        self.assertNotEqual(commands.get(1,{}).get('action'),'buy')

if __name__=='__main__':unittest.main()
