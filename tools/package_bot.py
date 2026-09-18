#!/usr/bin/env python3
"""Package the bot at the original Demo's CoreGeek/main3.py entrypoint."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile

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


def payloads() -> dict[str, bytes]:
    files = {target: (ROOT / source).read_bytes() for source, target in FILES}
    files['run.sh'] = PACKAGE_LAUNCHER
    manifest = {'files': {name: hashlib.sha256(raw).hexdigest()
                          for name, raw in files.items()}}
    files['MANIFEST.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
    return files


def build(output_dir: Path = ROOT) -> dict:
    files = payloads()
    # Fixed name: the current checkout contains one ready-to-upload artifact.
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / 'CoreGeek.tar.gz'
    data = io.BytesIO()
    # Stable metadata prevents a rebuild with identical inputs changing the file.
    with gzip.GzipFile(fileobj=data, mode='wb', filename='', mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode='w') as package:
            for name, raw in sorted(files.items()):
                info = tarfile.TarInfo('CoreGeek/' + name)
                info.size = len(raw)
                info.mode = 0o755 if name == 'run.sh' else 0o644
                package.addfile(info, io.BytesIO(raw))
    output.write_bytes(data.getvalue())
    return {'path': str(output), 'bytes': output.stat().st_size,
            'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
            'files': len(files)}


def main():
    print(json.dumps(build(), indent=2))


if __name__ == '__main__':
    main()
