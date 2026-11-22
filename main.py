#!/usr/bin/env python3
"""Thin CLI entrypoint for 芝ばたJ (Shibabata-J), powered by monju SDK."""
from __future__ import annotations

import sys
from pathlib import Path

# Auto-detect sibling ../monju checkout when running locally without pip install
SITE_ROOT = Path(__file__).resolve().parent
SIBLING_MONJU = SITE_ROOT.parent / "monju"
if SIBLING_MONJU.exists() and str(SIBLING_MONJU) not in sys.path:
    sys.path.insert(0, str(SIBLING_MONJU))

from monju.cli import main  # noqa: E402

if __name__ == "__main__":
    main(default_site=str(SITE_ROOT))
