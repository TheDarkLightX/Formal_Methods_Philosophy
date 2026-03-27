#!/usr/bin/env python3
from __future__ import annotations

from run_cycle import build_report


def test_specialization_cannot_beat_call_one_safe_winner() -> None:
    report = build_report()
    assert report["survivor"] == "obligation-fiber proposer frontier"
    assert report["global_safe_call_count"] == 1
    assert report["strict_improvement_possible"] is False


if __name__ == "__main__":
    test_specialization_cannot_beat_call_one_safe_winner()
    print("ok")
