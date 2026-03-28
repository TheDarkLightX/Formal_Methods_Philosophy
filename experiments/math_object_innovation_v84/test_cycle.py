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
    assert report["survivor"] == "hard critical-region certificate widening boundary"
    assert report["critical_regions"] == [[7, 12], [8], [9, 10], [11], [9], [10, 11], [7], [12]]
    assert report["changed_regions"] == [[10, 11]]
    assert report["newly_feasible_regions"] == [[10, 11]]

    expected = {
        (7, 12): (True, 7, True, 7),
        (8,): (True, 7, True, 7),
        (9, 10): (True, 10, True, 10),
        (11,): (True, 6, True, 6),
        (9,): (True, 9, True, 9),
        (10, 11): (False, None, True, 6),
        (7,): (True, 5, True, 5),
        (12,): (True, 2, True, 2),
    }
    for row in report["region_reports"]:
        region = tuple(row["scores"])
        assert (
            row["literal_bound_4"]["possible"],
            row["literal_bound_4"]["total_cost"],
            row["literal_bound_5"]["possible"],
            row["literal_bound_5"]["total_cost"],
        ) == expected[region]

    region_1011 = next(row for row in report["region_reports"] if row["scores"] == [10, 11])
    covers = region_1011["literal_bound_5"]["covers"]
    assert covers["(0, 0, 1, 1)"] == ["err[3]"]
    assert covers["(1, 0, 1, 1)"] == [
        "not err[3] and not err[6] and not err[8] and not err[9] and err[10]"
    ]
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
