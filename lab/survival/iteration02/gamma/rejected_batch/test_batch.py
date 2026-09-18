import unittest
from unittest.mock import patch
from lab.survival.iteration02.gamma.rejected_batch.protocol import Pos,Unit,Turn
from lab.survival.iteration02.gamma.rejected_batch.economy import develop
class BatchSalesTest(unittest.TestCase):
 def choose(self,count,gold=0,baselevel=3):
  worker=Unit(1,Pos(10,10),'worker',220,1,0,0,40,('copper',)*count)
  pioneer=Unit(3,Pos(7,10),'pioneer',200,1,0,0,40,())
  base=Unit(2,Pos(5,10),'station',1500*baselevel,baselevel,0,0,40,())
  mine=Pos(15,10);vendor=Pos(12,10)
  turn=Turn(10,True,gold,41,32,{mine:'copper',vendor:'vendor',Pos(25,20):'weaponShop'},(worker,pioneer,base),(),(),'defender',{'copper':5},{'StationUpgradeVoucher1':100})
  with patch('lab.survival.iteration02.gamma.rejected_batch.economy.walk',return_value=True) as w:
   develop(turn,worker,set(),{})
   return w.call_args.args[2]
 def test_small_nonurgent_load_keeps_mining(self):self.assertEqual(self.choose(4),[Pos(15,10)])
 def test_existing_fifty_coin_batch_still_sells(self):self.assertEqual(self.choose(10),[Pos(12,10)])
 def test_small_load_unlocking_upgrade_still_sells(self):self.assertEqual(self.choose(4,gold=80,baselevel=1),[Pos(12,10)])
if __name__=='__main__':unittest.main()
