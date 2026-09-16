#!/usr/bin/env python3
"""Package the bot at the original Demo's CoreGeek/main3.py entrypoint."""
import hashlib
import io
import json
from pathlib import Path
import tarfile
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ('bot/main3.py', 'main3.py'),
    ('bot/pyproject.toml', 'pyproject.toml'),
    ('bot/src/agent/__init__.py', 'src/agent/__init__.py'),
    ('bot/src/agent/brain.py', 'src/agent/brain.py'),
    ('bot/src/agent/grid.py', 'src/agent/grid.py'),
    ('bot/src/agent/protocol.py', 'src/agent/protocol.py'),
    ('bot/src/agent/server.py', 'src/agent/server.py'),
    ('bot/src/agent/targeting.py', 'src/agent/targeting.py'),
    ('night-demo/selected-policy.json', 'selected-policy.json'),
    ('docs/request.txt', 'sample-request.json'),
    ('docs/交付说明.md', 'README.md'),
]
# The development checkout keeps code under bot/; the submission puts it at root.
PACKAGE_LAUNCHER = b'''#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
exec "${PYTHON:-python3}" main3.py "$@"
'''


def build(output_dir: Path) -> dict:
    payloads = {target: (ROOT / source).read_bytes() for source, target in FILES}
    payloads['run.sh'] = PACKAGE_LAUNCHER
    manifest = {'files': {name: hashlib.sha256(raw).hexdigest()
                          for name, raw in payloads.items()}}
    content_id = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()[:12]
    payloads['MANIFEST.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
    output = output_dir / content_id
    output.mkdir(parents=True, exist_ok=True)
    tar_path = output / 'CoreGeek.tar.gz'
    zip_path = output / 'CoreGeek-flat.zip'
    # Same top-level folder as the upstream Demo: extract into /home/docker.
    with tarfile.open(tar_path, 'w:gz') as package:
        for name, raw in payloads.items():
            info = tarfile.TarInfo('CoreGeek/' + name)
            info.size = len(raw)
            info.mode = 0o755 if name == 'run.sh' else 0o644
            package.addfile(info, io.BytesIO(raw))
    # For uploaders that already extract into /home/docker/CoreGeek.
    with ZipFile(zip_path, 'w', ZIP_DEFLATED) as package:
        for name, raw in payloads.items():
            package.writestr(name, raw)
    return {'files': len(payloads), 'archives': [
        {'path': str(path), 'bytes': path.stat().st_size,
         'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        for path in (tar_path, zip_path)
    ]}


def main():
    print(json.dumps(build(ROOT / 'deliverables'), indent=2))


if __name__ == '__main__':
    main()
