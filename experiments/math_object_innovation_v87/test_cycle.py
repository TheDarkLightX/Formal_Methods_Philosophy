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
    assert report["survivor"] == "low-residual widened-certificate saturation boundary"
    assert report["low_residual_budgets"] == [0, 1, 2]
    assert report["moved_budgets"] == []
    ladder = report["budget_ladder"]
    assert [row["residual_region_count"] for row in ladder] == [0, 1, 2]
    assert [row["optimal_shared_schema_count"] for row in ladder] == [25, 23, 21]
    assert [row["optimal_total_cost"] for row in ladder] == [29, 27, 25]
    assert [row["schema_gain_over_v85"] for row in ladder] == [0, 0, 0]
    assert [row["cost_gain_over_v85"] for row in ladder] == [0, 0, 0]
    assert ladder[0]["optimal_partition"] == [[7, 12], [8], [9], [10, 11]]
    assert ladder[0]["optimal_residual_regions"] == []
    assert ladder[1]["optimal_partition"] == [[7, 12], [8], [9], [10, 11]]
    assert ladder[1]["optimal_residual_regions"] == [[8]]
    assert ladder[2]["optimal_partition"] == [[7, 12], [8], [9], [10, 11]]
    assert ladder[2]["optimal_residual_regions"] == [[8], [9]]
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
