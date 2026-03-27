#!/usr/bin/env python3
from __future__ import annotations

from run_cycle import build_report


def test_core_preserving_frontier_runs() -> None:
    report = build_report()
    assert report["survivor"] == "core-preserving repair frontier"
    assert report["state_total"] > 0
    assert report["safe_repair_count"] >= 1


if __name__ == "__main__":
    test_core_preserving_frontier_runs()
    print("ok")
