import unittest
from dataclasses import replace
from .protocol import Pos,Unit,Robot,Turn
from .fire_control import targets

class FirepowerMechanism(unittest.TestCase):
    def test_gatling_only_improves_noncollinear_low_hp_finishing(self):
        gun=Unit(1,Pos(5,5),'railgun',1500,2,0,0,None,())
        robots=(Robot(101,Pos(7,5),10,'challenger'),Robot(102,Pos(5,7),10,'challenger'))
        base=Unit(9,Pos(4,4),'station',3000,2,0,0,None,())
        turn=Turn(71,False,0,20,20,{},(base,),robots,(),'challenger')
        rail={};targets(turn,gun,rail)
        gatling={};shots=targets(turn,replace(gun,kind='gatling'),gatling)
        self.assertEqual(len(rail),1)
        self.assertEqual(len(gatling),2)
        self.assertEqual(len(shots),2)
        self.assertGreaterEqual((shots[0].x-5)*(shots[1].x-5)+(shots[0].y-5)*(shots[1].y-5),0)

    def test_level_one_gatling_loses_early_shooting_window(self):
        gun=Unit(1,Pos(5,5),'railgun',1000,1,0,0,None,())
        robot=Robot(101,Pos(9,5),40,'challenger')
        turn=Turn(71,False,0,20,20,{},(),(robot,),(),'challenger')
        self.assertTrue(targets(turn,gun,{}))
        self.assertEqual(targets(turn,replace(gun,kind='gatling'),{}),[])

if __name__=='__main__':unittest.main()
