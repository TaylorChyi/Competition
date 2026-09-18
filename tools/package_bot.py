#!/usr/bin/env python3
"""Build the submission using the official archive's single CoreGeek root."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
FILES = [
    ('CoreGeek/main3.py', 'main3.py'),
    ('CoreGeek/run.sh', 'run.sh'),
    ('CoreGeek/pyproject.toml', 'pyproject.toml'),
    ('CoreGeek/src/agent/__init__.py', 'src/agent/__init__.py'),
    ('CoreGeek/src/agent/brain.py', 'src/agent/brain.py'),
    ('CoreGeek/src/agent/grid.py', 'src/agent/grid.py'),
    ('CoreGeek/src/agent/protocol.py', 'src/agent/protocol.py'),
    ('CoreGeek/src/agent/server.py', 'src/agent/server.py'),
    ('CoreGeek/src/agent/targeting.py', 'src/agent/targeting.py'),
    ('night-demo/selected-policy.json', 'selected-policy.json'),
    ('docs/request.txt', 'sample-request.json'),
    ('docs/交付说明.md', 'README.md'),
]


def payloads() -> dict[str, bytes]:
    files = {target: (ROOT / source).read_bytes() for source, target in FILES}
    manifest = {'files': {name: hashlib.sha256(raw).hexdigest()
                          for name, raw in files.items()}}
    files['MANIFEST.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
    return files


def archive_payloads() -> dict[str, bytes]:
    # Some uploaders select or validate the top-level directory before unpacking.
    # Match the official Demo: one explicit CoreGeek directory, no sibling files.
    return {'CoreGeek/' + name: raw for name, raw in payloads().items()}


def build(output_dir: Path = DIST) -> dict:
    files = archive_payloads()
    # Fixed local output; publish this tested file as a GitHub Release asset.
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / 'CoreGeek.tar.gz'
    data = io.BytesIO()
    # Stable metadata prevents a rebuild with identical inputs changing the file.
    with gzip.GzipFile(fileobj=data, mode='wb', filename='', mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode='w', format=tarfile.USTAR_FORMAT) as package:
            directories = set()
            for name, raw in files.items():
                for parent in reversed(Path(name).parents):
                    if str(parent) == '.' or str(parent) in directories:
                        continue
                    info = tarfile.TarInfo(parent.as_posix())
                    info.type = tarfile.DIRTYPE
                    info.mode = 0o755
                    package.addfile(info)
                    directories.add(str(parent))
                info = tarfile.TarInfo(name)
                info.size = len(raw)
                info.mode = 0o755 if name.endswith('run.sh') else 0o644
                package.addfile(info, io.BytesIO(raw))
    output.write_bytes(data.getvalue())
    return {'path': str(output), 'bytes': output.stat().st_size,
            'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
            'files': len(files)}


def main():
    print(json.dumps(build(), indent=2))


if __name__ == '__main__':
    main()
