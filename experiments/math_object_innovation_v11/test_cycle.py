#!/usr/bin/env python3
from __future__ import annotations

from run_cycle import build_report


def test_third_clause_frontier_is_negative() -> None:
    report = build_report()
    assert report["survivor"] == "third-clause tie-break frontier"
    assert report["residual_case_count"] == 3
    assert report["candidate_count_fixing_at_least_one_residual"] > 0
    assert report["safe_candidates_fixing_all_residuals"] == []


if __name__ == "__main__":
    test_third_clause_frontier_is_negative()
    print("ok")
