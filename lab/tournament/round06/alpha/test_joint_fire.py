import unittest
from .protocol import Pos,Unit,Robot,Turn
from .fire_control import targets,joint_railgun_targets,ray_hits


def gun(uid,pos):
    return Unit(uid,Pos(*pos),'railgun',1000,1,0,0,None,())


def turn(robots):
    base=Unit(9,Pos(5,5),'station',1500,1,0,0,None,())
    return Turn(71,False,0,20,20,{},(base,),tuple(robots),(),'challenger')


class JointAllocation(unittest.TestCase):
    def test_constrained_gun_fires_first_to_avoid_idle_shot(self):
        a,b=gun(1,(5,6)),gun(2,(1,6))
        x=Robot(101,Pos(6,6),10,'challenger')
        y=Robot(102,Pos(8,12),10,'challenger')
        t=turn((x,y));reserved={}
        self.assertEqual(targets(t,a,reserved),[x.pos])
        self.assertEqual(targets(t,b,reserved),[])
        reserved={};plan=joint_railgun_targets(t,[a,b],reserved)
        self.assertEqual(plan,{b.unit_id:[x.pos],a.unit_id:[y.pos]})
        self.assertEqual(reserved,{x.robot_id:10,y.robot_id:10})

    def test_real_front_blocker_cannot_be_ignored_after_reserved_kill(self):
        a,b=gun(1,(2,5)),gun(2,(2,6))
        x=Robot(101,Pos(4,5),10,'challenger')
        y=Robot(102,Pos(6,5),10,'challenger')
        t=turn((x,y))
        self.assertEqual([r.robot_id for r in ray_hits(a.pos,y.pos,t.robots)],[101,102])
        # Snapshot damage reservation must not pretend a front body vanished.
        reserved={101:10}
        self.assertEqual(targets(t,a,reserved),[])

    def test_single_gun_and_tied_orders_keep_inherited_target(self):
        a=gun(1,(5,6));x=Robot(101,Pos(6,6),40,'challenger');t=turn((x,))
        expected={};chosen=targets(t,a,expected)
        actual={};self.assertEqual(joint_railgun_targets(t,[a],actual),{1:chosen})
        self.assertEqual(actual,expected)

    def test_equal_damage_and_kills_preserve_original_order(self):
        a,b=gun(1,(5,6)),gun(2,(4,6))
        x=Robot(101,Pos(6,6),40,'challenger');t=turn((x,))
        expected={};plan={g.unit_id:targets(t,g,expected) for g in (a,b)}
        actual={}
        self.assertEqual(joint_railgun_targets(t,[a,b],actual),plan)
        self.assertEqual(actual,expected)

if __name__=='__main__':unittest.main()
