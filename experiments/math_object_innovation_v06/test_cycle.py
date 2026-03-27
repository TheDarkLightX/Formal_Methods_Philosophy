#!/usr/bin/env python3
from __future__ import annotations

from run_cycle import build_report


def test_report_has_statewise_frontier_signal() -> None:
    report = build_report()
    assert report["survivor"] == "statewise motif dictionary frontier"
    assert report["nonterminal_state_count"] > 0
    assert report["base_controller"]["hits"] < report["base_controller"]["total"]
    assert report["failure_motif_count"] > 0


if __name__ == "__main__":
    test_report_has_statewise_frontier_signal()
    print("ok")
