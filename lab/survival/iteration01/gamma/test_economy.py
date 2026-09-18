import unittest
from unittest.mock import patch
from lab.survival.iteration01.gamma.protocol import Pos,Unit,Turn
from lab.survival.iteration01.gamma.economy import develop
class SaleCostTest(unittest.TestCase):
 def test_far_vendor_mine_loses_to_faster_complete_cash_trip(self):
  worker=Unit(1,Pos(10,10),'worker',220,1,0,0,40,())
  base=Unit(2,Pos(5,10),'station',1500,1,0,0,40,())
  near_worker=Pos(8,10);near_vendor=Pos(15,10)
  turn=Turn(10,True,0,41,32,{near_worker:'copper',near_vendor:'copper',Pos(20,10):'vendor',Pos(25,20):'weaponShop'},(worker,base),(),(),'defender',{'copper':5},{'StationUpgradeVoucher1':100})
  with patch('lab.survival.iteration01.gamma.economy.walk',return_value=True) as walk:
   self.assertTrue(develop(turn,worker,set(),{}))
   self.assertEqual(walk.call_args.args[2],[near_vendor])
if __name__=='__main__':unittest.main()
