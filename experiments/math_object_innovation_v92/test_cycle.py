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
    assert report["survivor"] == "unlock taxonomy for the mature witness-language line"
    assert report["event_count"] == 14
    assert report["outcome_counts"] == {
        "baseline_ordering": 1,
        "boundary": 3,
        "frontier_gain": 6,
        "localized_gain": 1,
        "saturation": 3,
    }
    axis = report["axis_summary"]
    assert axis["new_search_axis"] == {"cycles": 9, "gain_cycles": 5, "gain_events": 16}
    assert axis["same_axis_widening"] == {"cycles": 5, "gain_cycles": 2, "gain_events": 4}
    classes = {row["intervention_class"]: row for row in report["class_summary"]}
    assert classes["new_axis"]["gain_events"] == 16
    assert classes["new_axis"]["gain_cycles"] == 5
    assert classes["grammar_widening"]["gain_events"] == 4
    assert classes["grammar_widening"]["saturation_cycles"] == 3
    assert classes["comparison_family"]["boundary_cycles"] == 2
    ranking = report["next_family_ranking"]
    assert [row["family"] for row in ranking[:2]] == [
        "temporal_monitor_cell_obligation_carving",
        "temporal_minimal_witness_language_discovery",
    ]
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
