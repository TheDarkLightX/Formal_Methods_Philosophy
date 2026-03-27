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


def test_direct_delta_certificate_frontier():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "direct delta-certificate frontier"
    assert report["tier"] == "symbolic_state_compiler"
    assert report["feature_names"] == ["has_add", "has_drop", "has_flip"]
    assert report["atom_count"] == 26
    assert report["row_count"] == 5
    assert report["labels"] == [
        "ADD_BUNDLE",
        "ADD_BUNDLE+DROP_BUNDLE",
        "FLIP_BUNDLE",
    ]
    assert report["all_positive"]["cost"] == 3
    assert report["all_positive"]["language"] == {
        "ADD_BUNDLE": ["has_add and not has_drop"],
        "ADD_BUNDLE+DROP_BUNDLE": ["has_drop"],
        "FLIP_BUNDLE": ["has_flip"],
    }
    assert report["residual_default"]["cost"] == 2
    assert report["residual_default"]["default_label"] == "ADD_BUNDLE"
    assert report["residual_default"]["language"] == {
        "ADD_BUNDLE+DROP_BUNDLE": ["has_drop"],
        "FLIP_BUNDLE": ["has_flip"],
    }


if __name__ == "__main__":
    test_direct_delta_certificate_frontier()
    print("ok")
