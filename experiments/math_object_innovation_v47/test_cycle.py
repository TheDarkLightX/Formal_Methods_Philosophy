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


def test_global_witness_synthesis_grammar_boundary_frontier():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "global witness-synthesis grammar boundary frontier"
    assert report["feature_count"] == 8
    assert report["best_partition"] == [[7], [8], [9], [10, 11], [12]]
    assert report["summary_4"] == {
        "atom_count": 1696,
        "total_region_cost": 22,
        "best_shared_schema_count": 19,
    }
    assert report["summary_5"] == {
        "atom_count": 3488,
        "total_region_cost": 22,
        "best_shared_schema_count": 19,
    }


if __name__ == "__main__":
    test_global_witness_synthesis_grammar_boundary_frontier()
    print("ok")
