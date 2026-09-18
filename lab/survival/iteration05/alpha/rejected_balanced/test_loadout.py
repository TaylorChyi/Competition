import unittest
from dataclasses import replace
from .protocol import Pos,Unit,Robot,Turn
from .brain import TOWER_LOADOUT
from .fire_control import targets,ray_hits
from .targeting import splash_damage

class RocketBehindWalls(unittest.TestCase):
    def test_three_guns_same_total_build_cost(self):
        self.assertEqual(TOWER_LOADOUT,('railgun','railgun','rocket'))
        self.assertEqual(len(TOWER_LOADOUT)*25,75)

    def test_clustered_incoming_supports_aoe(self):
        rocket=Unit(1,Pos(5,5),'rocket',1500,2,0,0,None,())
        robots=tuple(Robot(100+i,Pos(x,y),100,'challenger') for i,(x,y) in enumerate(((8,5),(8,6),(9,5),(9,6))))
        turn=Turn(71,False,0,20,20,{},(),robots,(),'challenger')
        reserved={};chosen=targets(turn,rocket,reserved)
        self.assertEqual(len(chosen),2)
        self.assertGreater(sum(min(r.health,reserved[r.robot_id]) for r in robots),80)

    def test_walls_are_not_robot_ray_interceptors(self):
        robot=Robot(101,Pos(8,5),40,'challenger')
        # Official ray rule intersects robots; static defenses are not targets.
        self.assertEqual(ray_hits(Pos(5,5),robot.pos,(robot,)),[robot])
        self.assertEqual(splash_damage(Pos(8,5),Pos(9,6)),10)

if __name__=='__main__':unittest.main()
