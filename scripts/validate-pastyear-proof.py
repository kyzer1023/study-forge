#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
import sys
from typing import Final

REPO_ROOT: Final = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.pastyear_proof_cli import CliRuntime, CliSpec, run_validation_cli
from scripts.pastyear_proof_selftest import run_self_test
from scripts.pastyear_proof_validator import validate


def main(argv: Sequence[str]) -> int:
    return run_validation_cli(
        argv,
        CliRuntime(
            spec=CliSpec("scripts/validate-pastyear-proof.py", allow_self_test=True),
            validator=validate,
            self_test_runner=run_self_test,
        ),
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
