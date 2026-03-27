#!/usr/bin/env python3
from __future__ import annotations

from run_cycle import build_report


def test_minimal_bank_collapses_to_zero_for_rank_one_winner() -> None:
    report = build_report()
    assert report["survivor"] == "minimal-bank synthesis frontier"
    assert report["raw_state_count"] == 320927
    assert report["unique_pattern_count"] == 4263
    assert report["viable_pair_count_without_bank"] == 7104
    assert report["first_safe_rank_without_bank"] == 1
    assert report["unsafe_prefix_size"] == 0
    assert report["minimal_bank_size"] == 0


if __name__ == "__main__":
    test_minimal_bank_collapses_to_zero_for_rank_one_winner()
    print("ok")
