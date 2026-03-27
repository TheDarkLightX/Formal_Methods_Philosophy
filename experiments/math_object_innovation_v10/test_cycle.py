#!/usr/bin/env python3
from __future__ import annotations

from run_cycle import build_report


def test_two_clause_language_improves_over_core() -> None:
    report = build_report()
    assert report["survivor"] == "two-clause dominance language"
    assert report["safe_repair_count"] >= 1
    best = report["best_two_clause_language"]
    assert best["holdout_5_hits"] + best["holdout_6_hits"] > report["core_holdout_5_hits"] + report["core_holdout_6_hits"]


if __name__ == "__main__":
    test_two_clause_language_improves_over_core()
    print("ok")
