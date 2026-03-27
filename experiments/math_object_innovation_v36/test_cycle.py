#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "generated" / "report.json"


def test_primitive_invention_label_frontier():
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "primitive-invention label frontier"
    assert report["baseline_all_positive_cost"] == 7
    assert report["best_one_primitive"]["total_cost"] == 5
    assert report["best_two_primitives"]["total_cost"] == 4
    assert report["best_one_primitive"]["primitive"]["label"] == "fail_828"
    assert report["best_one_primitive"]["primitive"]["formula"] == "E = True OR H6 = 858 OR H6 = 864"
    assert [item["label"] for item in report["best_two_primitives"]["primitives"]] == ["fail_1915", "fail_828"]


if __name__ == "__main__":
    test_primitive_invention_label_frontier()
    print("ok")
