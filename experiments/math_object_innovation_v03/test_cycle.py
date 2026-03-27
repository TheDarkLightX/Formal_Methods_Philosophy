#!/usr/bin/env python3
from __future__ import annotations

from run_cycle import (
    build_report,
    improve_selector,
    make_value_function,
    optimal_value_function,
    phi,
    relation_from_mask,
    route_selector,
)


def test_pi2_is_exact_on_4x4() -> None:
    for mask in range(1 << 16):
        rel = relation_from_mask(mask, 4)
        pi0 = route_selector(rel)
        pi1 = improve_selector(rel, pi0)
        pi2 = improve_selector(rel, pi1)
        value = make_value_function(rel, pi2)
        opt = optimal_value_function(rel)
        root = tuple(sorted(phi(rel, frozenset())))
        assert value(root) == opt(root)


def test_report_fields() -> None:
    report = build_report()
    assert report["survivor"] == "obligation-side policy iteration"
    assert report["exhaustive_4x4"]["exact_hits"]["pi2"] == 65536
    assert report["exhaustive_4x4"]["first_failure_pi2"] is None


if __name__ == "__main__":
    test_pi2_is_exact_on_4x4()
    test_report_fields()
    print("ok")
