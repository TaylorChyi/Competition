#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
exec "${PYTHON:-python3}" bot/main3.py "$@"
