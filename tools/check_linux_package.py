#!/usr/bin/env python3
"""Maintainer check: the shipped artifact alone, at the platform's literal path."""
import argparse
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
IMAGE = 'python:3.11-slim@sha256:9534e5a8e315485d4061ed659af0fd78a284c015f9b73661b41d6bab25604534'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', nargs='?', type=Path, default=ROOT / 'dist' / 'CoreGeek.tar.gz')
    args = parser.parse_args()
    archive = args.archive.resolve(strict=True)
    docker = shutil.which('docker')
    if docker is None:
        parser.error('Docker is required only for this maintainer check, not by receivers.')
    for layout in ('parent', 'named-directory', 'strip'):
        print('Linux/Python 3.11 extraction:', layout, flush=True)
        # Mount only the archive and the verification scripts. There is no bot
        # checkout in the container for a broken package to import accidentally.
        command = [docker, 'run', '--rm', '--platform', 'linux/amd64',
                   '--network', 'none', '--read-only', '--tmpfs', '/tmp', '--tmpfs', '/home']
        for source, target in ((archive, '/upload/CoreGeek.tar.gz'),
                               (ROOT / 'tests/test_package.py', '/checks/tests/test_package.py'),
                               (ROOT / 'tools/platform_start.py', '/checks/tools/platform_start.py'),
                               (ROOT / 'tools/package_bot.py', '/checks/tools/package_bot.py')):
            command += ['--mount', f'type=bind,src={source},dst={target},readonly']
        command += ['-e', 'COMPETITION_PACKAGE_PATH=/upload/CoreGeek.tar.gz',
                    '-e', 'COMPETITION_PLATFORM_LAYOUT=' + layout,
                    IMAGE, 'python3', '/checks/tests/test_package.py',
                    'PackageEntryPoints.test_official_tar_layout_and_both_entrypoints', '-v']
        subprocess.run(command, check=True, timeout=60)


if __name__ == '__main__':
    main()
