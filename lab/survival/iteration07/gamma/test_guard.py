import unittest
from lab.survival.iteration07.gamma.protocol import Pos,Unit,Turn,Robot
from lab.survival.iteration07.gamma.guard import nearest_risk,safer_step

def unit(uid,kind,pos,hp):return Unit(uid,Pos(*pos),kind,hp,1,0,0,40,())
def turn(*units):return Turn(71,False,0,41,32,{},units,(Robot(9,Pos(10,10),40,'defender'),),(),'defender')
class ProtectedStepTests(unittest.TestCase):
 def test_current_wall_still_absorbs_but_dying_cover_not_future_safe(self):
  t=turn(unit(2,'wall',(11,10),1))
  self.assertEqual(nearest_risk(t,Pos(13,10)),0)
  self.assertEqual(nearest_risk(t,Pos(13,10),future=True),5)
 def test_equal_cover_is_unsafe_and_base_footprint_counts(self):
  self.assertEqual(nearest_risk(turn(unit(2,'wall',(13,11),1000)),Pos(13,10)),5)
  self.assertEqual(nearest_risk(turn(unit(2,'station',(11,11),1500)),Pos(12,10)),0)
 def test_healthy_worker_can_take_safe_adjacent_operating_cell(self):
  role=unit(1,'worker',(12,10),220);tower=unit(2,'railgun',(13,11),1000)
  t=turn(role,tower,unit(3,'wall',(12,12),1000))
  step=safer_step(t,role,tower,set())
  self.assertIsNotNone(step)
  self.assertEqual(nearest_risk(t,step,future=True),0)
 def test_moving_role_not_fixed_cover(self):
  self.assertEqual(nearest_risk(turn(unit(2,'worker',(11,10),220)),Pos(13,10)),5)
if __name__=='__main__':unittest.main()
