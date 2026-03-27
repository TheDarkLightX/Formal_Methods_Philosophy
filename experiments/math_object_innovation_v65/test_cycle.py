#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "generated" / "report.json"


def ensure_report():
    if REPORT.exists():
        return
    subprocess.run([sys.executable, str(ROOT / "run_cycle.py")], check=True)


def test_v65_report():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "three-signature support law frontier"
    assert report["tier"] == "descriptive_oracle"
    assert report["oracle_dependent"] is True
    assert report["abstract_counts"] == [
        {"exact": 24, "total": 24, "width": 2},
        {"exact": 336, "total": 336, "width": 3},
        {"exact": 3360, "total": 3360, "width": 4},
        {"exact": 29760, "total": 29760, "width": 5},
        {"exact": 249984, "total": 249984, "width": 6},
        {"exact": 2048256, "total": 2048256, "width": 7},
    ]
    assert report["domain_instances"]["domain_a"]["compiler"] == {
        "default_label": "CORE",
        "branches": [
            {"atom": "not has_v46", "label": "V41_PATCH"},
            {"atom": "not has_v41", "label": "V46_PATCH"},
        ],
    }
    assert report["domain_instances"]["domain_b"]["compiler"] == {
        "default_label": "MIX_DISCRIM",
        "branches": [
            {"atom": "has_AB", "label": "ADD_ANCHOR"},
            {"atom": "not has_MIX", "label": "OTHER"},
        ],
    }
    assert report["domain_instances"]["domain_c"]["compiler"] == {
        "default_label": "ADD_BUNDLE",
        "branches": [
            {"atom": "has_drop", "label": "ADD_BUNDLE+DROP_BUNDLE"},
            {"atom": "has_flip", "label": "FLIP_BUNDLE"},
        ],
    }


if __name__ == "__main__":
    test_v65_report()
    print("ok")
