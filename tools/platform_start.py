#!/usr/bin/env python3
"""Generate a copyable startup command that locates this exact uploaded package."""
import hashlib
import json
from pathlib import Path
import shlex
import sys
import tarfile


def start_command(manifest_sha: str, root: Path = Path('/home/docker'), port: int = 6666) -> str:
    # Runs before main3.py is opened; works with shell or shlex-style launchers.
    # Search a bounded depth and require this release's manifest, never choose
    # an arbitrary main3.py from another upload or an older extracted version.
    code = '; '.join([
        'import hashlib,os,sys; from pathlib import Path',
        'print("Caffeine-Taylor",flush=True)',
        f'r=Path({json.dumps(str(root))}); expected={json.dumps(manifest_sha)}',
        'print("CoreGeek preflight | cwd="+os.getcwd(),flush=True)',
        'print("CoreGeek preflight | directory="+str(sorted(p.name for p in r.iterdir()) if r.is_dir() else "MISSING"),flush=True)',
        'entries=sorted({p.resolve() for pattern in ("main3.py","*/main3.py","*/*/main3.py","*/*/*/main3.py") for p in r.glob(pattern) if p.is_file()})',
        'print("CoreGeek preflight | entries="+str([str(p) for p in entries]),flush=True)',
        'matches=[p for p in entries if (p.parent/"MANIFEST.json").is_file() and hashlib.sha256((p.parent/"MANIFEST.json").read_bytes()).hexdigest()==expected]',
        'print("CoreGeek preflight | expected="+expected[:12]+" matches="+str(len(matches)),flush=True)',
        'len(matches)==1 or sys.exit("CoreGeek preflight FAILED: need one matching extracted package; check upload/extraction logs and listed paths")',
        '(matches[0].parent/"src/agent/server.py").is_file() or sys.exit("CoreGeek preflight FAILED: package runtime is incomplete")',
        'os.execv(sys.executable,[sys.executable,"-u",str(matches[0]),*sys.argv[1:]])',
    ])
    return shlex.join(['python3', '-u', '-c', code, str(port)])


def main():
    archive = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / 'dist/CoreGeek.tar.gz'
    with tarfile.open(archive) as package:
        digest = hashlib.sha256(package.extractfile('CoreGeek/MANIFEST.json').read()).hexdigest()
    print(start_command(digest))


if __name__ == '__main__':
    main()
