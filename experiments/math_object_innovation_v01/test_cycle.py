#!/usr/bin/env python3
from __future__ import annotations

from run_cycle import (
    build_report,
    choose_closure,
    choose_live,
    pick_best_singleton_candidate,
    pick_min_candidate,
    choose_smallest,
    optimal_policy_cost,
    relation_from_mask,
    run_scheduler,
)


def test_closure_is_exact_on_3x3() -> None:
    for mask in range(1 << 9):
        rel = relation_from_mask(3, 3, mask)
        assert run_scheduler(rel, pick_min_candidate, choose_closure) == optimal_policy_cost(rel, pick_min_candidate)


def test_smallest_is_not_exact_on_3x3() -> None:
    found = False
    for mask in range(1 << 9):
        rel = relation_from_mask(3, 3, mask)
        if run_scheduler(rel, pick_min_candidate, choose_smallest) != optimal_policy_cost(rel, pick_min_candidate):
            found = True
            break
    assert found


def test_known_4x4_failure_boundary() -> None:
    rel = relation_from_mask(4, 4, 6120)
    assert run_scheduler(rel, pick_min_candidate, choose_closure) == (3, 7)
    assert optimal_policy_cost(rel, pick_min_candidate, primary="steps") == (2, 7)
    assert optimal_policy_cost(rel, pick_min_candidate, primary="checks") == (2, 7)


def test_coupled_policy_fixes_known_boundary() -> None:
    rel = relation_from_mask(4, 4, 6120)
    coupled = run_scheduler(rel, pick_best_singleton_candidate, choose_closure)
    assert coupled == optimal_policy_cost(rel, pick_best_singleton_candidate, primary="steps")
    assert coupled == optimal_policy_cost(rel, pick_best_singleton_candidate, primary="checks")


def test_closure_and_live_tie_on_exhaustive_frontier() -> None:
    report = build_report()

    three_by_three = report["exhaustive"][0]
    assert three_by_three["schedulers"]["closure"]["optimal_steps_hits"] == 512
    assert three_by_three["schedulers"]["closure"]["optimal_checks_hits"] == 512
    assert three_by_three["schedulers"]["live"]["optimal_steps_hits"] == 512
    assert three_by_three["schedulers"]["live"]["optimal_checks_hits"] == 512

    three_by_four = report["exhaustive"][1]
    assert three_by_four["schedulers"]["closure"]["optimal_steps_hits"] == 4096
    assert three_by_four["schedulers"]["closure"]["optimal_checks_hits"] == 4096
    assert three_by_four["schedulers"]["live"]["optimal_steps_hits"] == 4096
    assert three_by_four["schedulers"]["live"]["optimal_checks_hits"] == 4096

    four_by_four = report["exhaustive"][2]
    assert four_by_four["schedulers"]["closure"] == {
        "avg_checks": 4.892822265625,
        "avg_steps": 1.5792694091796875,
        "optimal_checks_hits": 65146,
        "optimal_steps_hits": 64731,
    }
    assert four_by_four["schedulers"]["live"] == four_by_four["schedulers"]["closure"]


def test_live_matches_closure_on_known_4x4_step_failure() -> None:
    rel = relation_from_mask(4, 4, 6120)
    assert run_scheduler(rel, pick_min_candidate, choose_live) == (3, 7)


def test_report_fields() -> None:
    report = build_report()
    assert report["tier"] == "descriptive_oracle"
    assert report["oracle_dependent"] is False
    assert report["survivor"] == "closure-guided coupled policy"
    assert report["scope_notes"] == [
        "The exhaustive verifier-policy tables hold the proposer fixed to x_t = min(C_t).",
        "The coupled 4x4 table holds the proposer fixed to the singleton-closure chooser.",
        "Step and check optimality are computed independently, with the other metric used only as a tiebreak.",
    ]


if __name__ == "__main__":
    test_closure_is_exact_on_3x3()
    test_smallest_is_not_exact_on_3x3()
    test_known_4x4_failure_boundary()
    test_coupled_policy_fixes_known_boundary()
    test_closure_and_live_tie_on_exhaustive_frontier()
    test_live_matches_closure_on_known_4x4_step_failure()
    test_report_fields()
    print("ok")
