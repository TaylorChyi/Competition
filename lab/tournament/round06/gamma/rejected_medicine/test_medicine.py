import unittest
from lab.tournament.round06.gamma.rejected_medicine.economy import develop,urgent_refit,use_carried
from lab.tournament.round06.gamma.rejected_medicine.protocol import Pos,Unit,Turn

def unit(uid,kind,pos,hp,items=()):
 return Unit(uid,Pos(*pos),kind,hp,1,0,0,40,tuple(items))
def setup(hp=1430,gold=100,items=(),near_base=False):
 role=unit(20011,'pioneer',(31,8) if near_base else (24,20),200,items)
 base=unit(20013,'station',(32,8),hp)
 gun=unit(41000,'railgun',(29,11),1000)
 turn=Turn(161,True,gold,41,32,{Pos(25,20):'weaponShop',Pos(20,16):'vendor'},(base,role,gun),(),(),'defender',{'copper':5},{'StationUpgradeVoucher1':100,'StationUpgradeVoucher2':150,'WeaponUpgradeVoucher1':100,'Medicine':10})
 return turn,role
from dataclasses import replace
class MedicineTests(unittest.TestCase):
 def case(self,gold=110,hp=125,pos=None,commands=None):
  turn,role=setup(gold=gold)
  role=replace(role,kind='worker',health=hp,pos=pos or role.pos)
  turn=replace(turn,ours=(turn.station(),role)+tuple(turn.weapons()))
  commands={} if commands is None else commands
  develop(turn,role,set(),commands)
  return commands.get(role.unit_id,{})
 def test_125_worker_at_shop_buys_with_base_reserve(self):
  self.assertEqual(self.case(),{'action':'buy','name':'Medicine','num':1})
 def test_base_reserve_and_prior_expense(self):
  self.assertNotEqual(self.case(gold=100).get('name'),'Medicine')
  self.assertNotEqual(self.case(commands={20010:{'action':'buy','name':'Medicine','num':1}}).get('name'),'Medicine')
 def test_no_added_detour(self):
  self.assertNotEqual(self.case(pos=Pos(23,20)).get('name'),'Medicine')
 def test_healthy_old_stocking_retained(self):
  self.assertEqual(self.case(gold=250,hp=220).get('name'),'Medicine')
if __name__=='__main__':unittest.main()
