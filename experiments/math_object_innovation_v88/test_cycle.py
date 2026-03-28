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
    assert report["survivor"] == "lab-followup partition-aware residual-budget transfer frontier"
    assert report["nontrivial_scores"] == [1, 2, 3, 4]
    assert report["best_budget"] == 1
    assert report["best_budget_shared_schema_count"] == 4
    assert report["best_budget_total_cost"] == 4
    ladder = report["residual_budget_ladder"]
    assert [row["residual_region_count"] for row in ladder] == [0, 1, 2, 3, 4]
    assert [row["optimal_shared_schema_count"] for row in ladder] == [5, 4, 4, 4, 6]
    assert [row["optimal_total_cost"] for row in ladder] == [5, 4, 5, 7, 10]
    assert ladder[0]["optimal_partition"] == [[1, 2, 3, 4]]
    assert ladder[0]["optimal_residual_regions"] == []
    assert ladder[1]["optimal_partition"] == [[1, 2, 3, 4]]
    assert ladder[1]["optimal_residual_regions"] == [[1, 2, 3, 4]]
    assert ladder[2]["optimal_partition"] == [[1], [2, 3, 4]]
    assert ladder[2]["optimal_residual_regions"] == [[1], [2, 3, 4]]
    assert ladder[3]["optimal_partition"] == [[1], [2], [3, 4]]
    assert ladder[3]["optimal_residual_regions"] == [[1], [2], [3, 4]]
    assert ladder[4]["optimal_partition"] == [[1], [2], [3], [4]]
    assert ladder[4]["optimal_residual_regions"] == [[1], [2], [3], [4]]
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
