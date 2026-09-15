#!/usr/bin/env python3
"""Create a small uploadable bot ZIP from an explicit runtime file list."""
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ('run.sh', 'run.sh'),
    ('bot/main3.py', 'bot/main3.py'),
    ('bot/pyproject.toml', 'bot/pyproject.toml'),
    ('bot/src/agent/__init__.py', 'bot/src/agent/__init__.py'),
    ('bot/src/agent/brain.py', 'bot/src/agent/brain.py'),
    ('bot/src/agent/grid.py', 'bot/src/agent/grid.py'),
    ('bot/src/agent/protocol.py', 'bot/src/agent/protocol.py'),
    ('bot/src/agent/server.py', 'bot/src/agent/server.py'),
    ('bot/src/agent/targeting.py', 'bot/src/agent/targeting.py'),
    ('night-demo/selected-policy.json', 'night-demo/selected-policy.json'),
    ('docs/request.txt', 'sample-request.json'),
    ('docs/交付说明.md', 'README.md'),
]


def main():
    payloads = {target: (ROOT / source).read_bytes() for source, target in FILES}
    manifest = {'files': {name: hashlib.sha256(raw).hexdigest()
                          for name, raw in payloads.items()}}
    content_id = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()[:12]
    output = ROOT / 'deliverables' / f'competition-bot-{content_id}.zip'
    output.parent.mkdir(exist_ok=True)
    with ZipFile(output, 'w', ZIP_DEFLATED) as package:
        for name, raw in payloads.items():
            package.writestr(name, raw)
        package.writestr('MANIFEST.json', json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'path': str(output), 'bytes': output.stat().st_size,
                      'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
                      'files': len(payloads) + 1}, indent=2))


if __name__ == '__main__':
    main()
