"""Log observed causes separately from issued actions and later settlement."""
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'CoreGeek/src'))
from agent.server import battlefield_context
from test_baseline import state, unit


class FieldLoggingChecks(unittest.TestCase):
    def test_log_distinguishes_out_of_range_from_missing_operator(self):
        payload=state(71,roles=[unit(1,'worker',6,5),unit(2,'railgun',5,5)])
        payload['robot']['roles']=[unit(10,'smallRobot',30,20)]
        self.assertEqual(battlefield_context(payload,{})['guns'][0]['status'],'no-incoming-in-range')
        payload['robot']['roles'][0]['pos']={'x':8,'y':5}
        payload['teamOur']['roles'][0]['pos']={'x':20,'y':20}
        self.assertEqual(battlefield_context(payload,{})['guns'][0]['status'],'no-adjacent-operator')

    def test_log_exposes_voucher_inventory_and_actual_base_level(self):
        payload=state(169,roles=[unit(1,'pioneer',29,10),unit(2,'station',30,10)])
        payload['teamOur']['roles'][0]['backpack']=['StationUpgradeVoucher1','copper','copper']
        payload['teamOur']['roles'][1].update(level=2,health=1820)
        context=battlefield_context(payload,{})
        self.assertEqual(context['base']['level'],2)
        self.assertEqual(context['base']['hp'],1820)
        self.assertEqual(context['operators'][0]['backpack'],{'StationUpgradeVoucher1':1,'copper':2})

    def test_attack_is_logged_as_issued_not_successful(self):
        payload=state(71,roles=[unit(1,'worker',6,5),unit(2,'railgun',5,5)])
        context=battlefield_context(payload,{'2':{'action':'attack','controllerId':'1'}})
        self.assertEqual(context['guns'][0]['status'],'attack-issued')


if __name__=='__main__':
    unittest.main()
