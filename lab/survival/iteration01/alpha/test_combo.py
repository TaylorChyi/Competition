import unittest
from dataclasses import replace
from .test_field_regressions import unit, observation
from .economy import urgent_refit, develop
from .protocol import Pos

class EconomyInteraction(unittest.TestCase):
    def test_lightly_damaged_base_does_not_preempt_gun_upgrade(self):
        role=unit(20011,'pioneer',(25,19),200,backpack=('Medicine',))
        tower=unit(20,'railgun',(31,8),1000)
        turn=observation(role,base_health=1490,extra=(tower,))
        turn=replace(turn,shop_prices={**turn.shop_prices,'WeaponUpgradeVoucher1':100})
        commands={}
        self.assertFalse(urgent_refit(turn,role,set(),commands))
        self.assertTrue(develop(turn,role,set(),commands))
        self.assertEqual(commands[role.unit_id]['name'],'WeaponUpgradeVoucher1')

    def test_under_75_percent_preserves_station_priority(self):
        role=unit(20011,'pioneer',(25,19),200,backpack=('Medicine',))
        tower=unit(20,'railgun',(31,8),1000)
        turn=observation(role,base_health=1124,extra=(tower,))
        turn=replace(turn,shop_prices={**turn.shop_prices,'WeaponUpgradeVoucher1':100})
        for planner in (urgent_refit,develop):
            commands={}
            self.assertTrue(planner(turn,role,set(),commands))
            self.assertEqual(commands[role.unit_id]['name'],'StationUpgradeVoucher1')

if __name__=='__main__':unittest.main()
