#!/usr/bin/env python3
from __future__ import annotations

from run_cycle import build_report


def test_bank_then_rank_hits_safe_pair_immediately() -> None:
    report = build_report()
    assert report["survivor"] == "bank-then-rank frontier"
    assert report["viable_pair_count"] == 576
    assert report["first_safe_rank"] == 1
    assert report["first_safe_pair"]["safe"] is True


if __name__ == "__main__":
    test_bank_then_rank_hits_safe_pair_immediately()
    print("ok")
