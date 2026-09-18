import unittest
from dataclasses import replace
from .protocol import Pos,Unit,Turn,Robot
from .economy import late_rocket_refit
from .fire_control import targets,joint_railgun_targets

class LateRocket(unittest.TestCase):
    def world(self):
        worker=Unit(1,Pos(5,6),'worker',220,1,0,0,100,())
        carrier=Unit(2,Pos(10,6),'pioneer',200,1,0,0,40,('WeaponUpgradeVoucher1',))
        base=Unit(9,Pos(5,8),'station',1755,3,0,0,None,())
        guns=tuple(Unit(i,Pos(5+(i-20)*2,5),'railgun',1000,1,0,0,None,()) for i in (20,21,22))
        turn=Turn(826,True,25,20,20,{},(worker,carrier,base)+guns,(),(),'challenger',{}, {'Medicine':10})
        return turn,worker,carrier

    def test_funded_carried_upgrade_can_convert_only_one(self):
        turn,worker,_=self.world();cmd={};claimed=set()
        self.assertTrue(late_rocket_refit(turn,worker,claimed,cmd))
        self.assertEqual(cmd[1],{'action':'build','name':'rocket','targetPos':[{'x':5,'y':5}]})
        self.assertFalse(late_rocket_refit(turn,worker,claimed,cmd))

    def test_prior_upgrade_of_old_gun_is_not_destroyed(self):
        turn,worker,carrier=self.world()
        cmd={carrier.unit_id:{'action':'use','name':'WeaponUpgradeVoucher1','targetPos':[{'x':5,'y':5}]}}
        self.assertFalse(late_rocket_refit(turn,worker,set(),cmd))

    def test_cash_busy_night_and_dusk_are_rejected(self):
        turn,worker,_=self.world()
        for t,cmd in ((turn,{3:{'action':'buy','name':'Medicine','num':1}}),
                      (turn,{worker.unit_id:{'action':'collect'}}),
                      (replace(turn,is_day=False),{}),(replace(turn,round_no=850),{})):
            self.assertFalse(late_rocket_refit(t,worker,set(),cmd))

    def test_two_or_higher_guns_are_not_downgraded(self):
        turn,worker,_=self.world()
        units=tuple(replace(u,level=2) if u.kind=='railgun' else u for u in turn.units)
        self.assertFalse(late_rocket_refit(replace(turn,units=units),worker,set(),{}))

    def test_mixed_joint_order_preserves_constrained_rail_target(self):
        rocket=Unit(1,Pos(5,6),'rocket',1000,1,0,0,None,())
        rail=Unit(2,Pos(1,6),'railgun',1000,1,0,0,None,())
        base=Unit(9,Pos(5,5),'station',1500,1,0,0,None,())
        x,y=Robot(101,Pos(6,6),10,'challenger'),Robot(102,Pos(13,12),10,'challenger')
        turn=Turn(71,False,0,20,20,{},(base,),(x,y),(),'challenger')
        greedy={};targets(turn,rocket,greedy);self.assertFalse(targets(turn,rail,greedy))
        reserved={};plan=joint_railgun_targets(turn,[rocket,rail],reserved)
        self.assertTrue(plan[1]);self.assertTrue(plan[2])
        self.assertGreaterEqual(reserved[101],10);self.assertGreaterEqual(reserved[102],10)

if __name__=='__main__':unittest.main()
