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


def test_quotient_boundary_frontier():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "quotient boundary frontier"
    assert report["tier"] == "symbolic_state_compiler"
    assert report["label_only"]["best_slot_cost"] == 2
    assert report["label_only"]["ordered_best_count"] == 12
    assert report["label_only"]["unordered_best_count"] == 6
    assert report["label_only"]["best_unordered"] == [
        {"slot_cost": 2, "slots": [["add[10]"], ["add[8]"]]},
        {"slot_cost": 2, "slots": [["add[10]"], ["drop[12]"]]},
        {"slot_cost": 2, "slots": [["add[3]"], ["add[8]"]]},
        {"slot_cost": 2, "slots": [["add[3]"], ["drop[12]"]]},
        {"slot_cost": 2, "slots": [["add[6]"], ["add[8]"]]},
        {"slot_cost": 2, "slots": [["add[6]"], ["drop[12]"]]},
    ]
    assert report["basis_faithful"]["best_slot_cost"] == 5
    assert sorted([
        sorted(report["basis_faithful"]["best_slot_compiler"]["left"]),
        sorted(report["basis_faithful"]["best_slot_compiler"]["right"]),
    ]) == [
        ["add[10]", "add[3]", "add[6]"],
        ["add[8]", "drop[12]"],
    ]


if __name__ == "__main__":
    test_quotient_boundary_frontier()
    print("ok")
