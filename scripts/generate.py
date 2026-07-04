#!/usr/bin/env python3
"""Thin wrapper for generating all dictionaries from the CSV source.

Run from the repository root:

    uv run python scripts/generate.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from math_symbol_ime_dict.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:] or ["build"]))
