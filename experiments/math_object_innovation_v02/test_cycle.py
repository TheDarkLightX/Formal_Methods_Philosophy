#!/usr/bin/env python3
from __future__ import annotations

from run_cycle import build_report, optimal_y_policy, pair_policy, relation_from_mask, route_policy


def test_pair_route_equivalence_on_4x4() -> None:
    for mask in range(1 << 16):
        rel = relation_from_mask(4, 4, mask)
        assert pair_policy(rel) == route_policy(rel)


def test_pair_is_step_optimal_on_4x4() -> None:
    for mask in range(1 << 16):
        rel = relation_from_mask(4, 4, mask)
        assert pair_policy(rel)[0] == optimal_y_policy(rel)[0]


def test_report_fields() -> None:
    report = build_report()
    assert report["survivor"] == "obligation-targeted witness routing"
    assert report["oracle_dependent"] is False
    assert report["exhaustive_4x4"]["pair_matches_route"] == 65536
    assert report["exhaustive_4x4"]["pair_matches_opt_steps"] == 65536


if __name__ == "__main__":
    test_pair_route_equivalence_on_4x4()
    test_pair_is_step_optimal_on_4x4()
    test_report_fields()
    print("ok")
