import unittest
from dataclasses import replace
from lab.tournament.round07.gamma.rejected_nearest.protocol import Pos,Unit,Turn,Robot
from lab.tournament.round07.gamma.rejected_nearest.guard import exposure

def building(pos,hp=1000,kind='wall'):
 return Unit(2,Pos(*pos),kind,hp,1,0,0,40,())
def turn(*units):
 return Turn(71,False,0,41,32,{},units,(Robot(9,Pos(10,10),40,'defender'),),(),'defender')
class NearestGuardTests(unittest.TestCase):
 def test_strict_nearer_building_but_tie_unsafe(self):
  self.assertEqual(exposure(turn(building((11,10))),Pos(13,10)),0)
  self.assertEqual(exposure(turn(building((13,11))),Pos(13,10)),5)
 def test_dying_wall_counts_current_round_dead_wall_not_next(self):
  self.assertEqual(exposure(turn(building((11,10),1)),Pos(13,10)),0)
  self.assertEqual(exposure(turn(building((11,10),0)),Pos(13,10)),5)
 def test_base_footprint_not_only_anchor(self):
  # Anchor distance2, nearest footprint cell(11,10) distance1.
  self.assertEqual(exposure(turn(building((11,11),1500,'station')),Pos(12,10)),0)
 def test_in_range_building_stops_distance_four_approach(self):
  self.assertEqual(exposure(turn(building((13,10))),Pos(14,10)),0)
  self.assertEqual(exposure(turn(building((15,10))),Pos(14,10)),1.75)
  self.assertEqual(exposure(turn(building((14,11))),Pos(14,10)),1.75)
 def test_moving_role_old_position_not_fixed_cover(self):
  self.assertEqual(exposure(turn(building((11,10),220,'worker')),Pos(13,10)),5)
if __name__=='__main__':unittest.main()
