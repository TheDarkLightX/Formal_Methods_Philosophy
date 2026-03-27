#!/usr/bin/env python3
from __future__ import annotations

from run_cycle import build_report


def test_repair_program_cegis_finds_safe_pair() -> None:
    report = build_report()
    assert report["survivor"] == "repair-program CEGIS frontier"
    assert report["safe_pair"] is not None
    assert len(report["iterations"]) >= 3
    assert report["safe_pair"]["holdout_5_hits"] < 2999 or report["safe_pair"]["holdout_6_hits"] < 898


if __name__ == "__main__":
    test_repair_program_cegis_finds_safe_pair()
    print("ok")
