#!/usr/bin/env python3
from __future__ import annotations

from run_cycle import build_report


def test_minimal_winner_certificate_has_size_six() -> None:
    report = build_report()
    assert report["survivor"] == "winner-certificate language frontier"
    assert report["frontier_size"] == 7104
    assert report["minimal_certificate_size"] == 6
    assert report["solution_count_at_min_size"] >= 1


if __name__ == "__main__":
    test_minimal_winner_certificate_has_size_six()
    print("ok")
