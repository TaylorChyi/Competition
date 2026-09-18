import unittest
from lab.tournament.round05.gamma.rejected_economy.economy import develop,urgent_refit,use_carried
from lab.tournament.round05.gamma.rejected_economy.protocol import Pos,Unit,Turn

def unit(uid,kind,pos,hp,items=()):
 return Unit(uid,Pos(*pos),kind,hp,1,0,0,40,tuple(items))
def setup(hp=1430,gold=100,items=(),near_base=False):
 role=unit(20011,'pioneer',(31,8) if near_base else (24,20),200,items)
 base=unit(20013,'station',(32,8),hp)
 gun=unit(41000,'railgun',(29,11),1000)
 turn=Turn(161,True,gold,41,32,{Pos(25,20):'weaponShop',Pos(20,16):'vendor'},(base,role,gun),(),(),'defender',{'copper':5},{'StationUpgradeVoucher1':100,'StationUpgradeVoucher2':150,'WeaponUpgradeVoucher1':100,'Medicine':10})
 return turn,role
class EconomyTests(unittest.TestCase):
 def test_light_damage_first_cash_upgrades_gun(self):
  turn,role=setup();commands={}
  self.assertFalse(urgent_refit(turn,role,set(),commands))
  self.assertTrue(develop(turn,role,set(),commands))
  self.assertEqual(commands[role.unit_id],{'action':'buy','name':'WeaponUpgradeVoucher1','num':1})
 def test_heavy_damage_base_priority_in_both_paths(self):
  for function in (urgent_refit,develop):
   turn,role=setup(hp=1000);commands={}
   self.assertTrue(function(turn,role,set(),commands))
   self.assertEqual(commands[role.unit_id]['name'],'StationUpgradeVoucher1')
 def test_carried_base_voucher_used_even_light_damage(self):
  turn,role=setup(items=('StationUpgradeVoucher1',),near_base=True);commands={}
  self.assertTrue(use_carried(turn,role,set(),commands))
  self.assertEqual(commands[role.unit_id]['action'],'use')
  self.assertEqual(commands[role.unit_id]['name'],'StationUpgradeVoucher1')
 def test_real_cash_short_and_reserved_cash_cannot_buy(self):
  for hp in (1000,1430):
   turn,role=setup(hp=hp,gold=99,items=('copper',)*10);commands={}
   urgent_refit(turn,role,set(),commands);develop(turn,role,set(),commands)
   self.assertNotEqual(commands.get(role.unit_id,{}).get('action'),'buy')
   turn,role=setup(hp=hp,gold=100);commands={20010:{'action':'buy','name':'Medicine','num':1}}
   urgent_refit(turn,role,set(),commands);develop(turn,role,set(),commands)
   self.assertNotEqual(commands.get(role.unit_id,{}).get('action'),'buy')
if __name__=='__main__':unittest.main()
