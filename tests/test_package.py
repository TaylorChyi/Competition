"""Regression: the uploaded artifact must support CoreGeek/main3.py directly."""
import hashlib
import json
import os
import platform
from pathlib import Path
import shlex
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
from tools.package_bot import DIST, archive_payloads
from tools.platform_start import start_command

ARCHIVE = Path(os.environ.get('COMPETITION_PACKAGE_PATH', DIST / 'CoreGeek.tar.gz'))


class PackageEntryPoints(unittest.TestCase):
    def check_archive(self, layout):
        # Exercise the built or downloaded Release artifact; never rebuild it in tests.
        archive = ARCHIVE
        with tempfile.TemporaryDirectory(prefix='competition package ') as temp:
            root = Path(temp)
            if os.environ.get('COMPETITION_PLATFORM_LAYOUT'):
                # Only disposable Linux containers may exercise the literal
                # path from the user's error. Each layout gets a fresh container.
                self.assertEqual(sys.platform, 'linux')
                self.assertEqual(sys.version_info[:2], (3, 11))
                self.assertTrue(Path('/.dockerenv').is_file())
                print('Runtime:', platform.python_version(), platform.machine(),
                      '| upload root: /home/docker | layout:', layout, flush=True)
                docker = Path('/home/docker')
                self.assertFalse(docker.exists(), 'Use a fresh container per layout')
            else:
                docker = root / 'home' / 'docker'
            package = docker / 'CoreGeek'
            destination = docker if layout == 'parent' else package
            destination.mkdir(parents=True)
            command = ['tar', '-xzf', str(archive), '-C', str(destination)]
            if layout == 'strip':
                command.append('--strip-components=1')
            subprocess.run(command, check=True, capture_output=True)
            runtime = package / 'CoreGeek' if layout == 'named-directory' else package
            if layout == 'named-directory':
                # A strict official archive really does nest here. Only the
                # external preflight command can run before the missing path.
                self.assertFalse((package / 'main3.py').exists())
            else:
                self.assertTrue((package / 'main3.py').is_file())
            self.assertTrue((runtime / 'src' / 'agent' / 'server.py').is_file())
            manifest = json.loads((runtime / 'MANIFEST.json').read_text())
            for name, digest in manifest['files'].items():
                self.assertEqual(hashlib.sha256((runtime / name).read_bytes()).hexdigest(), digest)
            entries = ('preflight',) if layout == 'named-directory' else ('main3.py', 'run.sh', 'preflight')
            for entry in entries:
                for policy in ('default', 'experimental'):
                    with self.subTest(entry=entry, policy=policy):
                        self.check_server(package, runtime, root, entry, policy, docker)

    def check_server(self, package, runtime, unrelated_cwd, entry, policy, search_root):
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        if os.environ.get('COMPETITION_PLATFORM_LAYOUT'):
            port = 6666
        env = dict(os.environ)
        for key in ('COMPETITION_ROCKET_POLICY', 'COMPETITION_TRACE'):
            env.pop(key, None)
        env['PYTHON'] = sys.executable
        env['PATH'] = str(Path(sys.executable).parent) + os.pathsep + env.get('PATH', '')
        if policy == 'experimental':
            env['COMPETITION_ROCKET_POLICY'] = str(runtime / 'selected-policy.json')
        if entry == 'preflight':
            digest = hashlib.sha256((runtime / 'MANIFEST.json').read_bytes()).hexdigest()
            command = ['bash', '-c', start_command(digest, search_root, port)]
        else:
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

                sample = post((runtime / 'sample-request.json').read_bytes())
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
                # Include the platform's action validity feedback in diagnostics.
                night['roundNo'] = 72
                night['lastRoundRoleActionResults'] = {'2': False}
                post(json.dumps(night).encode())
                deadline = time.monotonic() + 2
                while 'last_invalid=[\'2\']' not in log_path.read_text():
                    if time.monotonic() > deadline:
                        self.fail('Missing round/action diagnostics: ' + log_path.read_text())
                    time.sleep(.01)
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=3)
        self.assertNotIn('decision failed', log_path.read_text())
        self.assertIn('CoreGeek startup | package=', log_path.read_text())
        self.assertIn('runtime=' + str(runtime.resolve()), log_path.read_text())
        self.assertIn('round 72 | phase=night', log_path.read_text())
        if entry == 'preflight':
            self.assertIn('CoreGeek preflight | entries=', log_path.read_text())
            self.assertIn('matches=1', log_path.read_text())

    def test_official_tar_layout_and_both_entrypoints(self):
        layouts = ('parent', 'named-directory', 'strip')
        platform_layout = os.environ.get('COMPETITION_PLATFORM_LAYOUT')
        if platform_layout:
            self.assertIn(platform_layout, layouts)
            layouts = (platform_layout,)
        for layout in layouts:
            with self.subTest(layout=layout):
                self.check_archive(layout)

    def test_shipped_archive_matches_current_sources(self):
        expected = archive_payloads()
        with tarfile.open(ARCHIVE) as stream:
            self.assertEqual(stream.getmembers()[0].name, 'CoreGeek')
            self.assertTrue(stream.getmembers()[0].isdir())
            self.assertEqual({Path(name).parts[0] for name in stream.getnames()}, {'CoreGeek'})
            directories = {str(parent) for name in expected for parent in Path(name).parents
                           if str(parent) != '.'}
            self.assertEqual(set(stream.getnames()), set(expected) | directories)
            self.assertEqual(len(stream.getnames()), len(expected) + len(directories))
            for member in stream.getmembers():
                if member.name in directories:
                    self.assertTrue(member.isdir())
                    self.assertEqual(member.mode, 0o755)
                    continue
                self.assertTrue(member.isfile())
                self.assertEqual(stream.extractfile(member).read(), expected[member.name],
                                 'Stale package; run python3 tools/package_bot.py')
            self.assertEqual(stream.getmember('CoreGeek/run.sh').mode, 0o755)

    def test_preflight_reports_missing_upload_before_opening_main(self):
        with tempfile.TemporaryDirectory(prefix='competition preflight ') as temp:
            root = Path(temp)
            for state in ('missing-directory', 'archive-only', 'wrong-version', 'duplicate', 'incomplete'):
                with self.subTest(state=state):
                    upload = root / state
                    if state != 'missing-directory':
                        upload.mkdir()
                    if state == 'archive-only':
                        (upload / 'CoreGeek.tar.gz').write_bytes(ARCHIVE.read_bytes())
                    manifest = b'this exact release'
                    if state in ('wrong-version', 'duplicate', 'incomplete'):
                        for name in (('a', 'b') if state == 'duplicate' else ('a',)):
                            folder = upload / name
                            folder.mkdir()
                            (folder / 'main3.py').write_text('raise RuntimeError("MUST NOT EXECUTE")')
                            (folder / 'MANIFEST.json').write_bytes(b'older release' if state == 'wrong-version' else manifest)
                    digest = hashlib.sha256(manifest).hexdigest()
                    command = shlex.split(start_command(digest, upload))
                    command[0] = sys.executable
                    result = subprocess.run(command, capture_output=True, text=True, timeout=5)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('CoreGeek preflight | entries=', result.stdout)
                    self.assertIn('CoreGeek preflight FAILED:', result.stderr)
                    self.assertNotIn('MUST NOT EXECUTE', result.stderr)
                    if state == 'missing-directory':
                        self.assertIn('directory=MISSING', result.stdout)
                    elif state == 'archive-only':
                        self.assertIn('CoreGeek.tar.gz', result.stdout)
                    elif state == 'wrong-version':
                        self.assertIn('matches=0', result.stdout)
                    elif state == 'duplicate':
                        self.assertIn('matches=2', result.stdout)
                    else:
                        self.assertIn('runtime is incomplete', result.stderr)


if __name__ == '__main__':
    unittest.main()
