"""Rule regressions and a real HTTP smoke check; this is not a game simulator."""
import copy
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'CoreGeek' / 'src'))
from agent.brain import decide
from agent.grid import next_step
from agent.protocol import Pos, Turn


def unit(uid, kind, x, y, **extra):
    if kind.endswith('Robot'):
        extra.setdefault('targetTeam', 'challenger')
    return dict(id=uid, roleType=kind, pos=dict(x=x, y=y), health=1000,
                level=1, backpack=[], **extra)


def state(round_no=1, gold=75, roles=None):
    return {
        'roundNo': round_no,
        'mapInfo': {'width': 41, 'height': 32, 'zones': []},
        'teamOur': {'type': 'challenger', 'goldNum': gold, 'roles': roles or [
            unit(10013, 'station', 10, 24),
            unit(10010, 'worker', 8, 22),
            unit(10012, 'worker', 8, 24),
        ]},
        'teamEnemy': {'roles': []},
        'robot': {'roles': []},
    }


def tower_builds(commands):
    return [cmd for cmd in commands.values()
            if cmd['action'] == 'build' and cmd['name'] != 'wall']


class RuleChecks(unittest.TestCase):
    def test_shared_wallet_cannot_build_two_towers_with_25_gold(self):
        builds = tower_builds(decide(state(gold=25)))
        self.assertEqual(len(builds), 1)

    def test_sufficient_wallet_allows_two_different_builds(self):
        builds = tower_builds(decide(state(gold=50)))
        self.assertEqual(len(builds), 2)
        self.assertNotEqual(builds[0]['targetPos'], builds[1]['targetPos'])

    def test_three_existing_towers_at_other_sites_prevent_fourth(self):
        payload = state()
        payload['teamOur']['roles'] += [
            unit(10020, 'gatling', 12, 24),
            unit(10030, 'railgun', 12, 23),
            unit(10040, 'rocket', 12, 22),
        ]
        self.assertEqual(tower_builds(decide(payload)), [])

    def test_only_one_slot_left_reserves_last_slot(self):
        payload = state()
        payload['teamOur']['roles'] += [
            unit(10020, 'gatling', 12, 24),
            unit(10030, 'railgun', 12, 23),
        ]
        self.assertEqual(len(tower_builds(decide(payload))), 1)

    def test_visible_enemy_blocks_path_and_base_uses_four_cells(self):
        payload = state(roles=[unit(10010, 'worker', 2, 3)])
        payload['teamEnemy']['roles'] = [
            unit(20010, 'worker', 3, 3),
            unit(20013, 'station', 5, 5),
        ]
        turn = Turn.load(payload)
        role = turn.workers()[0]
        self.assertIsNone(next_step(turn, role, Pos(3, 3)))
        step = next_step(turn, role, Pos(4, 3))
        self.assertIsNotNone(step)
        self.assertNotEqual(step, Pos(3, 3))
        self.assertTrue({Pos(5, 5), Pos(6, 5), Pos(5, 4), Pos(6, 4)}
                        <= turn.blocked(role))

    def test_dead_enemy_no_longer_blocks_path(self):
        payload = state(roles=[unit(10010, 'worker', 2, 3)])
        enemy = unit(20010, 'worker', 3, 3)
        enemy['health'] = 0
        payload['teamEnemy']['roles'] = [enemy]
        turn = Turn.load(payload)
        self.assertEqual(next_step(turn, turn.workers()[0], Pos(3, 3)), Pos(3, 3))

    def test_day_night_boundaries(self):
        for number, expected in [(1, True), (70, True), (71, False),
                                 (130, False), (131, True), (1300, False)]:
            with self.subTest(round=number):
                self.assertEqual(Turn.load(state(number)).is_day, expected)

    def test_attack_uses_tower_id_and_adjacent_controller(self):
        payload = state(71, roles=[
            unit(10010, 'worker', 8, 24),
            unit(10020, 'gatling', 9, 24, attackRange=3),
        ])
        payload['robot']['roles'] = [unit(30001, 'smallRobot', 11, 24)]
        commands = decide(payload)
        self.assertEqual(set(commands), {'10020'})
        self.assertEqual(commands['10020']['controllerId'], '10010')
        self.assertEqual(commands['10020']['targetPos'], [{'x': 11, 'y': 24}])

    def test_rocket_does_not_fire_on_cooldown(self):
        payload = state(71, roles=[
            unit(10010, 'worker', 8, 24),
            unit(10040, 'rocket', 9, 24, cooldown=2),
        ])
        payload['robot']['roles'] = [unit(30001, 'smallRobot', 11, 24)]
        self.assertEqual(decide(payload), {})


class HTTPCheck(unittest.TestCase):
    def test_entrypoint_sample_malformed_recovery_and_trace(self):
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        with tempfile.TemporaryDirectory() as temp:
            trace = Path(temp) / 'turns.jsonl'
            env = dict(os.environ, PYTHON=sys.executable,
                       COMPETITION_TRACE=str(trace))
            log = open(Path(temp) / 'server.log', 'wb')
            proc = subprocess.Popen(['bash', str(ROOT / 'run.sh'), str(port)],
                                    cwd=temp, env=env, stdout=log, stderr=log)
            try:
                deadline = time.monotonic() + 5
                while True:
                    try:
                        with socket.create_connection(('127.0.0.1', port), timeout=.2):
                            break
                    except OSError:
                        if proc.poll() is not None or time.monotonic() > deadline:
                            self.fail('Server failed to start: ' +
                                      (Path(temp) / 'server.log').read_text())
                        time.sleep(.05)

                def post(raw):
                    start = time.monotonic()
                    req = Request(f'http://127.0.0.1:{port}/', data=raw,
                                  headers={'Content-Type': 'application/json'})
                    with urlopen(req, timeout=4) as response:
                        self.assertEqual(response.status, 200)
                        result = json.load(response)
                    self.assertLess(time.monotonic() - start, 4)
                    return result

                sample = json.loads((ROOT / 'docs' / 'request.txt').read_text())
                for number in [1, 70, 71, 85, 130, 131, 1300]:
                    payload = copy.deepcopy(sample)
                    payload['roundNo'] = number
                    result = post(json.dumps(payload).encode())
                    self.assertEqual(result, {'roleCommandMap': decide(payload)})
                    self.assertTrue(result['roleCommandMap'])
                self.assertEqual(post(b'{invalid'), {'roleCommandMap': {}})
                self.assertEqual(post(json.dumps(sample).encode()),
                                 {'roleCommandMap': decide(sample)})
                deadline = time.monotonic() + 2
                records = []
                while time.monotonic() < deadline:
                    try:
                        records = [json.loads(s) for s in trace.read_text().splitlines()]
                        if len(records) == 9:
                            break
                    except (FileNotFoundError, ValueError):
                        pass
                    time.sleep(.01)
                self.assertEqual(len(records), 9)
                self.assertEqual(sum(r['error'] is not None for r in records), 1)
                self.assertTrue(all(r['decisionMs'] < 4000 for r in records))
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=3)
                log.close()


if __name__ == '__main__':
    unittest.main()
