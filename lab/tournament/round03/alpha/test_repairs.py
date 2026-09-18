import unittest
from dataclasses import replace
from .protocol import Pos,Turn,Unit
from .economy import repair_upgrade,develop,sell_at_vendor_for_upgrade
from .brain import _worker_day


def unit(uid,kind,pos,hp,level=1,bag=()):
    return Unit(uid,Pos(*pos),kind,hp,level,0,0,40,tuple(bag))


def scene():
    roles=(unit(9,'station',(32,8),1500),unit(1,'worker',(30,9),220),
           unit(2,'pioneer',(24,20),200),unit(3,'railgun',(31,8),125,2),
           unit(4,'railgun',(33,9),1000),unit(5,'railgun',(34,7),1000))
    return Turn(161,True,150,41,32,{Pos(25,20):'weaponShop',Pos(20,16):'vendor',Pos(12,10):'stone'},
                roles,(),(),'defender',{'stone':1,'copper':5},
                {'WeaponUpgradeVoucher1':100,'WeaponUpgradeVoucher2':150,
                 'StationUpgradeVoucher1':100,'StationUpgradeVoucher2':150,'Medicine':10})


class RepairCases(unittest.TestCase):
    def test_funded_repair_preserves_advanced_tower_and_buys_correct_voucher(self):
        t=scene();w=t.workers()[0]
        self.assertEqual(repair_upgrade(t,{}),'WeaponUpgradeVoucher2')
        commands={};_worker_day(t,w,(),[],[],set(),commands,('railgun',)*3,True,0)
        self.assertFalse(any(c['action']=='build' for c in commands.values()))
        pioneer=next(r for r in t.controllable() if r.kind=='pioneer')
        commands={};develop(t,pioneer,set(),commands)
        self.assertEqual(commands[pioneer.unit_id],{'action':'buy','name':'WeaponUpgradeVoucher2','num':1})

    def test_unfunded_or_urgent_base_or_too_late_does_not_wait(self):
        t=scene()
        for changed in (replace(t,gold=149),replace(t,round_no=199),
                        replace(t,ours=(replace(t.ours[0],health=100),)+t.ours[1:])):
            self.assertIsNone(repair_upgrade(changed,{}))

    def test_adjacent_inventory_unlocks_base_before_optional_maintenance(self):
        t=scene();worker=replace(t.workers()[0],pos=Pos(19,15),backpack=('copper',)*7)
        t=replace(t,gold=65,ours=(replace(t.ours[0],health=900),worker)+t.ours[2:])
        commands={};_worker_day(t,worker,(),[],[],set(),commands,('railgun',)*3,True,4)
        self.assertEqual(commands[worker.unit_id],{'action':'sell','name':'copper','num':7})

    def test_cannot_unlock_in_one_sale_keeps_other_work(self):
        t=scene();worker=replace(t.workers()[0],pos=Pos(19,15),backpack=('copper',)*7)
        t=replace(t,gold=0,ours=(replace(t.ours[0],health=900),worker)+t.ours[2:])
        self.assertFalse(sell_at_vendor_for_upgrade(t,worker,{}))

if __name__=='__main__':unittest.main()
