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
    assert report["survivor"] == "staged temporal monitor-cell obligation quotient"
    assert report["candidate_count"] == 5832
    assert report["trace_obligation_count"] == 144
    assert report["monitor_cell_count"] == 36
    assert report["partition_matches"] is False
    assert report["trace_and_cell_perfect_sets_match"] is True
    assert report["spec_trace_class_size"] == report["spec_cell_class_size"]
    assert report["cell_greedy_yes_only"]["checks"] > report["trace_greedy_yes_only"]["checks"]
    assert report["step1_safe_candidate_count"] == 108
    assert report["staged_partition_matches"] is True
    assert report["staged_trace_and_cell_perfect_sets_match"] is True
    assert report["staged_trace_behavior_class_count"] == report["staged_cell_behavior_class_count"] == 12
    assert report["staged_trace_greedy_yes_only"]["checks"] == report["staged_cell_greedy_yes_only"]["checks"] == 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
