import unittest
from dataclasses import replace
from lab.tournament.round06.beta.protocol import Pos, Unit, Robot, Turn
from lab.tournament.round06.beta.fire_control import targets, joint_railgun_targets
from lab.tournament.round06.gamma.economy import develop

class PeerCounterexamples(unittest.TestCase):
    def test_rocket_first_can_take_only_railgun_target(self):
        rocket=Unit(1,Pos(5,6),'rocket',1000,1,0,0,None,())
        rail=Unit(2,Pos(1,6),'railgun',1000,1,0,0,None,())
        base=Unit(9,Pos(5,5),'station',1500,1,0,0,None,())
        x=Robot(101,Pos(6,6),10,'challenger')
        y=Robot(102,Pos(13,12),10,'challenger')
        turn=Turn(71,False,0,20,20,{},(base,), (x,y),(),'challenger')
        reserved={}
        rocket_first=targets(turn,rocket,reserved)
        self.assertGreaterEqual(reserved.get(101),10)
        self.assertEqual(joint_railgun_targets(turn,[rail],reserved)[2],[])
        self.assertNotIn(102,reserved)
        better={}
        self.assertEqual(targets(turn,rail,better),[x.pos])
        self.assertTrue(targets(turn,rocket,better))
        self.assertGreaterEqual(better[101],10)
        self.assertGreaterEqual(better[102],10)

    def test_opportunity_medicine_spends_gun_upgrade_cash(self):
        role=Unit(1,Pos(25,19),'worker',125,1,0,0,100,())
        base=Unit(9,Pos(32,8),'station',4500,3,0,0,None,())
        gun=Unit(20,Pos(31,8),'railgun',1000,1,0,0,None,())
        turn=Turn(161,True,100,41,32,{Pos(25,20):'weaponShop',Pos(20,16):'vendor'},
                  (base,role,gun),(),(),'defender',{'copper':5},
                  {'Medicine':10,'WeaponUpgradeVoucher1':100})
        commands={}
        self.assertTrue(develop(turn,role,set(),commands))
        self.assertEqual(commands[1]['name'],'Medicine')
        self.assertLess(turn.gold-10,turn.shop_prices['WeaponUpgradeVoucher1'])

if __name__=='__main__':unittest.main()
