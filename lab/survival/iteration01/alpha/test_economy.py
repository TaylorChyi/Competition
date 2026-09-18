import unittest
from unittest.mock import patch
from dataclasses import replace
from .economy import develop
from .protocol import Pos,Turn,Unit


def actor(uid,pos,items=()):
    return Unit(uid,Pos(*pos),'worker',220,1,0,0,100,tuple(items))


def world(roles,zones):
    base=Unit(9,Pos(7,24),'station',1500,1,0,0,None,())
    pioneer=Unit(8,Pos(7,25),'pioneer',200,1,0,0,40,())
    return Turn(20,True,0,41,32,zones,(base,pioneer)+tuple(roles),(),(),'challenger',
                {'stone':1,'iron':3,'copper':5},{'StationUpgradeVoucher1':100})


class EconomicChanges(unittest.TestCase):
    def test_adjacent_workers_share_the_same_mine(self):
        one,two=actor(1,(21,25)),actor(2,(22,25))
        mine=Pos(22,26)
        t=world((one,two),{mine:'copper',Pos(20,16):'vendor',Pos(25,20):'weaponShop'})
        commands={};claimed=set()
        develop(t,one,claimed,commands);develop(t,two,claimed,commands)
        self.assertEqual([commands[x]['action'] for x in (1,2)],['collect','collect'])
        self.assertEqual(commands[1]['targetPos'],commands[2]['targetPos'])

    def test_distant_small_inventory_collects_before_long_sell_trip(self):
        one=actor(1,(4,25),('copper',)*3)
        t=world((one,),{Pos(7,25):'copper',Pos(20,16):'vendor',Pos(25,20):'weaponShop'})
        with patch(__package__+'.economy.walk',return_value=True) as walk:
            develop(t,one,set(),{})
            self.assertEqual(walk.call_args.args[2],[Pos(7,25)])
        # Existing urgent sell remains intact when cash unlocks an upgrade.
        t=replace(t,gold=85)
        with patch(__package__+'.economy.walk',return_value=True) as walk:
            develop(t,one,set(),{})
            self.assertEqual(walk.call_args.args[2],[Pos(20,16)])

if __name__=='__main__': unittest.main()
