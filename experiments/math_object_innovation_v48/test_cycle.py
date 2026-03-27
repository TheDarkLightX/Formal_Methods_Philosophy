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


def test_cross_frontier_witness_template_frontier():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "cross-frontier witness-template frontier"
    assert report["source_frontiers"] == {
        "v41_schema_count": 20,
        "v46_schema_count": 19,
        "shared_schema_count": 17,
        "union_schema_count": 22,
    }
    assert report["untyped_template_count"] == 10
    assert report["typed_template_count"] == 13
    assert report["v41_only"] == [
        "err[6] and err[9] and not err[10]",
        "not err[3] and err[9] AND err[10] AND err[12] and not err[6]",
        "not err[8] and not err[12]",
    ]
    assert report["v46_only"] == [
        "not err[3] and not err[6] and err[10] and err[12]",
        "not err[3] and not err[6] and not err[8] and err[10]",
    ]
    assert report["largest_untyped_buckets"][0] == {
        "template": "F1",
        "count": 5,
        "schemas": ["err[12]", "err[3]", "err[6]", "err[8]", "err[9]"],
    }


if __name__ == "__main__":
    test_cross_frontier_witness_template_frontier()
    print("ok")
