#!/usr/bin/env bash
# Local preview only; no publishing or existing-server termination.
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python tools/preview_page.py --port "${PORT:-8090}" "$@"
