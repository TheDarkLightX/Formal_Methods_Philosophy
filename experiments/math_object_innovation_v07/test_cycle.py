#!/usr/bin/env python3
from __future__ import annotations

from run_cycle import build_report


def test_dominance_controller_is_exact_on_bounded_4x4() -> None:
    report = build_report()
    assert report["survivor"] == "lookahead-dominance controller"
    assert report["exhaustive_4x4_roots"]["hits"] == report["exhaustive_4x4_roots"]["total"]
    assert report["exhaustive_4x4_states"]["hits"] == report["exhaustive_4x4_states"]["total"]


if __name__ == "__main__":
    test_dominance_controller_is_exact_on_bounded_4x4()
    print("ok")
