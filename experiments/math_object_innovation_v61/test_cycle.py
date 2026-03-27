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


def test_semantic_slot_frontier():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "semantic slot frontier"
    assert report["tier"] == "descriptive_oracle"
    assert report["row_count"] == 9
    assert report["positive_basis_size"] == 2
    assert report["residual_basis_size"] == 2
    assert report["preferred_support_profile_all_positive"] == {
        "features": ["has_AB", "has_MIX"],
        "language": {
            "cost": 3,
            "language": {
                "other": ["not has_MIX"],
                "slot_a": ["has_AB"],
                "slot_b": ["not has_AB and has_MIX"],
            },
        },
    }
    assert report["preferred_support_profile_residual_default"] == {
        "features": ["has_AB", "has_MIX"],
        "language": {
            "cost": 2,
            "default_label": "other",
            "language": {
                "slot_a": ["has_AB"],
                "slot_b": ["not has_AB and has_MIX"],
            },
        },
    }


if __name__ == "__main__":
    test_semantic_slot_frontier()
    print("ok")
