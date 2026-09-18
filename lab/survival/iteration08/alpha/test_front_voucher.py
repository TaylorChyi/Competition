import unittest
from dataclasses import replace
from . import test_one_front
from .economy import use_carried
from .protocol import Pos

class FrontVoucher(unittest.TestCase):
    def world(self,name='WeaponUpgradeVoucher1',levels=(1,1,1)):
        t,u=test_one_front.BalancedUpgrades().world()
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

if __name__=='__main__':unittest.main()
