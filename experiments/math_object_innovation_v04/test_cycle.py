#!/usr/bin/env python3
from __future__ import annotations

from run_cycle import build_report


def test_report_has_frontier_signal() -> None:
    report = build_report()
    assert report["survivor"] == "controller compression frontier"
    assert report["dataset_size"] > 0
    assert report["best_pi2_formula"]["hits"] < report["best_pi2_formula"]["total"]


if __name__ == "__main__":
    test_report_has_frontier_signal()
    print("ok")
