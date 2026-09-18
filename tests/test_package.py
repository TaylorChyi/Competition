"""Regression: the uploaded artifact must support CoreGeek/main3.py directly."""
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tarfile
import tempfile
import time
import unittest
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.package_bot import payloads


class PackageEntryPoints(unittest.TestCase):
    def check_archive(self):
        # Exercise the exact checked-in artifact that recipients download.
        archive = ROOT / 'CoreGeek.tar.gz'
        with tempfile.TemporaryDirectory(prefix='competition package ') as temp:
            root = Path(temp)
            docker = root / 'home' / 'docker'
            package = docker / 'CoreGeek'
            docker.mkdir(parents=True)
            with tarfile.open(archive) as stream:
                stream.extractall(docker, filter='data')
            self.assertTrue((package / 'main3.py').is_file())
            self.assertTrue((package / 'src' / 'agent' / 'server.py').is_file())
            self.assertFalse((package / 'CoreGeek').exists())
            manifest = json.loads((package / 'MANIFEST.json').read_text())
            for name, digest in manifest['files'].items():
                self.assertEqual(hashlib.sha256((package / name).read_bytes()).hexdigest(), digest)
            for entry in ('main3.py', 'run.sh'):
                for policy in ('default', 'experimental'):
                    with self.subTest(entry=entry, policy=policy):
                        self.check_server(package, root, entry, policy)

    def check_server(self, package, unrelated_cwd, entry, policy):
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        env = dict(os.environ)
        for key in ('COMPETITION_ROCKET_POLICY', 'COMPETITION_TRACE'):
            env.pop(key, None)
        env['PYTHON'] = sys.executable
        if policy == 'experimental':
            env['COMPETITION_ROCKET_POLICY'] = str(package / 'selected-policy.json')
        command = [sys.executable if entry.endswith('.py') else 'bash',
                   str(package / entry), str(port)]
        log_path = unrelated_cwd / 'server.log'
        with log_path.open('wb') as log:
            proc = subprocess.Popen(command, cwd=unrelated_cwd, env=env,
                                    stdout=log, stderr=log)
            try:
                deadline = time.monotonic() + 5
                while True:
                    try:
                        with socket.create_connection(('127.0.0.1', port), timeout=.2):
                            break
                    except OSError:
                        if proc.poll() is not None or time.monotonic() > deadline:
                            self.fail('Packaged server failed to start: ' + log_path.read_text())
                        time.sleep(.05)

                def post(raw):
                    request = Request(f'http://127.0.0.1:{port}/', data=raw,
                                      headers={'Content-Type': 'application/json'})
                    with urlopen(request, timeout=4) as response:
                        self.assertEqual(response.status, 200)
                        return json.load(response)

                sample = post((package / 'sample-request.json').read_bytes())
                self.assertTrue(sample['roleCommandMap'])
                night = {
                    'roundNo': 71, 'mapInfo': {'width': 41, 'height': 32, 'zones': []},
                    'teamOur': {'roles': [
                        {'id': 1, 'roleType': 'worker', 'pos': {'x': 0, 'y': 1}, 'health': 220},
                        {'id': 2, 'roleType': 'rocket', 'pos': {'x': 1, 'y': 1}, 'health': 1500, 'level': 2},
                    ]},
                    'robot': {'roles': [
                        {'id': 30000+i, 'roleType': 'smallRobot', 'pos': {'x': x, 'y': y}, 'health': 100}
                        for i, (x, y) in enumerate([(5, 5), (5, 7), (7, 5), (7, 7)])
                    ]},
                }
                action = post(json.dumps(night).encode())['roleCommandMap']['2']
                self.assertEqual(action['action'], 'attack')
                self.assertEqual(action['controllerId'], '1')
                expected = {'x': 5, 'y': 5} if policy == 'default' else {'x': 6, 'y': 6}
                self.assertEqual(action['targetPos'], [expected, expected])
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=3)
        self.assertNotIn('decision failed', log_path.read_text())

    def test_official_tar_layout_and_both_entrypoints(self):
        self.check_archive()

    def test_shipped_archive_matches_current_sources(self):
        expected = {'CoreGeek/' + name: raw for name, raw in payloads().items()}
        with tarfile.open(ROOT / 'CoreGeek.tar.gz') as stream:
            self.assertEqual(sorted(stream.getnames()), sorted(expected))
            for member in stream.getmembers():
                self.assertTrue(member.isfile())
                self.assertEqual(stream.extractfile(member).read(), expected[member.name],
                                 'Stale package; run python3 tools/package_bot.py')
            self.assertEqual(stream.getmember('CoreGeek/run.sh').mode, 0o755)


if __name__ == '__main__':
    unittest.main()
