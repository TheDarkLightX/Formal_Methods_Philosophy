#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "generated" / "report.json"


def ensure_report() -> dict:
    if not REPORT.exists():
        subprocess.run(["python3", str(ROOT / "run_cycle.py")], check=True)
    return json.loads(REPORT.read_text(encoding="utf-8"))


def main() -> int:
    report = ensure_report()
    assert report["survivor"] == "lab-followup unsafe earliest-error residual law"
    assert report["unsafe_behavior_count"] == 163
    assert report["smallest_exact_all_positive_cost"] == 5
    assert report["smallest_exact_residual_cost"] == 4
    assert report["minimal_residual_defaults"] == [
        "(0, 0, 1)",
        "(0, 1, 0)",
        "(0, 1, 1)",
        "(1, 1, 0)",
        "(1, 1, 1)",
    ]
    assert report["label_counts"] == {
        "(0, 0, 1)": 101,
        "(0, 1, 0)": 40,
        "(0, 1, 1)": 14,
        "(1, 1, 0)": 6,
        "(1, 1, 1)": 2,
    }
    direct = report["direct_earliest_error_check"]
    assert direct["default_label"] == "(0, 0, 1)"
    assert direct["mismatch_count"] == 0
    assert direct["formula_map"] == {
        "(0, 1, 0)": "not e1 and e2",
        "(0, 1, 1)": "not e1 and not e2 and e3",
        "(1, 1, 0)": "not e1 and not e2 and not e3 and e4",
        "(1, 1, 1)": "not e1 and not e2 and not e3 and not e4",
    }
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
