#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "generated" / "report.json"


def ensure_report() -> None:
    if REPORT.exists():
        return
    subprocess.run([sys.executable, str(ROOT / "run_cycle.py")], cwd=ROOT, check=True)


def test_raw_edit_basis_frontier():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "raw edit-basis frontier"
    assert report["tier"] == "symbolic_state_compiler"
    assert report["row_count"] == 5
    assert report["labels"] == [
        "ADD_BUNDLE",
        "ADD_BUNDLE+DROP_BUNDLE",
        "FLIP_BUNDLE",
    ]
    assert report["primitive_features"] == [
        "add[3]",
        "add[6]",
        "add[8]",
        "add[10]",
        "drop[12]",
        "flip[6]",
        "flip[8]",
        "flip[9]",
        "flip[12]",
    ]
    assert report["all_positive"]["basis_size"] == 2
    assert report["residual_default"]["basis_size"] == 2
    assert [item["features"] for item in report["all_positive"]["exact_bases"]] == [
        ["add[3]", "add[8]"],
        ["add[3]", "drop[12]"],
        ["add[6]", "add[8]"],
        ["add[6]", "drop[12]"],
        ["add[8]", "add[10]"],
        ["add[10]", "drop[12]"],
    ]
    assert len(report["residual_default"]["exact_bases"]) == 18


if __name__ == "__main__":
    test_raw_edit_basis_frontier()
    print("ok")
