#!/usr/bin/env python3
from __future__ import annotations

from run_cycle import build_report


def test_exact_clause_family_exists() -> None:
    report = build_report()
    assert report["survivor"] == "dominance-clause family frontier"
    assert report["exact_on_4x4_state_count"] >= 1
    assert report["best_exact_clause"]["state_hits"] == report["state_total"]


if __name__ == "__main__":
    test_exact_clause_family_exists()
    print("ok")
