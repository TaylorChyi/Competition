#!/usr/bin/env python3
import logging
import hashlib
import os
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python main3.py <port>")
    port = int(sys.argv[1])
    entry = Path(__file__).resolve()
    root = entry.parent
    if not (root / "src" / "agent" / "server.py").is_file():
        raise SystemExit("CoreGeek runtime missing beside entrypoint: " + str(root))
    os.chdir(root)
    sys.path.insert(0, str(root / "src"))

    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="%(asctime)s | %(message)s",
    )

    from agent.server import serve

    manifest = root / "MANIFEST.json"
    package_id = hashlib.sha256(manifest.read_bytes()).hexdigest()[:12] if manifest.is_file() else "source"
    logging.info("CoreGeek startup | package=%s python=%s entry=%s runtime=%s",
                 package_id, sys.version.split()[0], entry, root)
    serve(port)


if __name__ == "__main__":
    main()
