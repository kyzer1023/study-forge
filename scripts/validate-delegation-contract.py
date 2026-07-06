#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# ///
# --- How to run ---
# python scripts/validate-delegation-contract.py --self-test
# python scripts/validate-delegation-contract.py --hook-exercise delegated
# python scripts/validate-delegation-contract.py --hook-exercise opt-out
# python scripts/validate-delegation-contract.py .

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.delegation_contract.cli import main


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
