import unittest
from dataclasses import replace
from .protocol import Pos,Unit,Robot,Turn
from .fire_control import threat_weights

class NearestThreat(unittest.TestCase):
    def turn(self,units):
        robot=Robot(101,Pos(5,5),40,'challenger')
        return Turn(71,False,0,20,20,{},tuple(units),(robot,),(),'challenger')
    def unit(self,uid,kind,pos,hp=220):
        return Unit(uid,Pos(*pos),kind,hp,1,0,0,None,())
    def weight(self,units):return threat_weights(self.turn(units),Pos(15,15))[101]

    def test_strictly_nearer_wall_removes_operator_bonus(self):
        role=self.unit(1,'worker',(7,5),50);wall=self.unit(2,'wall',(6,5),1000)
        self.assertEqual(self.weight((role,wall)),self.weight((wall,)))
        self.assertGreater(self.weight((role,)),self.weight(()))

    def test_tied_wall_and_operator_keep_conservative_bonus(self):
        role=self.unit(1,'worker',(7,5),50);wall=self.unit(2,'wall',(5,7),1000)
        self.assertGreater(self.weight((role,wall)),self.weight((wall,)))

    def test_station_footprint_not_anchor_blocks(self):
        role=self.unit(1,'worker',(3,5),50)
        # Anchor at(6,7) is distance2, footprint cell(6,6) distance1.
        base=self.unit(2,'station',(6,7),1500)
        self.assertEqual(self.weight((role,base)),self.weight((base,)))

    def test_dead_wall_does_not_shield_and_one_hp_live_wall_does(self):
        role=self.unit(1,'worker',(7,5),50);wall=self.unit(2,'wall',(6,5),0)
        self.assertEqual(self.weight((role,wall)),self.weight((role,)))
        self.assertEqual(self.weight((role,replace(wall,health=1))),self.weight((replace(wall,health=1),)))

    def test_other_operator_old_position_is_not_reliable_shield(self):
        role=self.unit(1,'worker',(7,5),50)
        moving=self.unit(2,'worker',(6,5),220)
        self.assertGreater(self.weight((role,moving)),self.weight((moving,)))

if __name__=='__main__':unittest.main()
