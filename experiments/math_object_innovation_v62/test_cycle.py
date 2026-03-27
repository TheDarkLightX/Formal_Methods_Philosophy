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


def test_shared_role_semantics_frontier():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "shared role semantics frontier"
    assert report["tier"] == "descriptive_oracle"
    assert report["primitive_count"] == 9
    assert report["support_partition"] == {
        "ADD_ANCHOR": ["add[10]", "add[3]", "add[6]"],
        "MIX_DISCRIM": ["add[8]", "drop[12]"],
        "OTHER": ["flip[12]", "flip[6]", "flip[8]", "flip[9]"],
    }
    assert report["support_to_structure"] == {
        "ADD_ANCHOR": ["slot_a"],
        "MIX_DISCRIM": ["slot_b"],
        "OTHER": ["other"],
    }
    assert report["cross_product_matches_label_only"] is True
    assert report["semantic_cross_product"] == [
        {"slot_cost": 2, "slots": [["add[10]"], ["add[8]"]]},
        {"slot_cost": 2, "slots": [["add[10]"], ["drop[12]"]]},
        {"slot_cost": 2, "slots": [["add[3]"], ["add[8]"]]},
        {"slot_cost": 2, "slots": [["add[3]"], ["drop[12]"]]},
        {"slot_cost": 2, "slots": [["add[6]"], ["add[8]"]]},
        {"slot_cost": 2, "slots": [["add[6]"], ["drop[12]"]]},
    ]


if __name__ == "__main__":
    test_shared_role_semantics_frontier()
    print("ok")
