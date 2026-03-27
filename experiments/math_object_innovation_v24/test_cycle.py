#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "generated" / "report.json"


def test_repaired_verifier_compiler() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "repaired verifier compiler frontier"
    assert report["frontier_size"] == 7104
    assert report["quotient_state_count"] == 10
    assert report["guard_count"] == 4
    assert report["decision_list"] == [
        "if H6 = 859 and E = False then fail_1915",
        "if H6 = 865 then fail_1915",
        "if H6 = 869 then fail_13116",
        "if H6 > 869 then safe",
        "else fail_828",
    ]


if __name__ == "__main__":
    test_repaired_verifier_compiler()
    print("ok")
