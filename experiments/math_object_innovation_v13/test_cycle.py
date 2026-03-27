#!/usr/bin/env python3
from __future__ import annotations

from run_cycle import build_report


def test_multi_proposer_frontier() -> None:
    report = build_report()
    assert report["survivor"] == "shared-bank multi-proposer frontier"
    assert report["pair_count"] > 0
    assert report["best_single_proposer"]["calls"] == 2
    assert report["best_two_proposer_portfolio"]["calls"] >= report["best_single_proposer"]["calls"]


if __name__ == "__main__":
    test_multi_proposer_frontier()
    print("ok")
