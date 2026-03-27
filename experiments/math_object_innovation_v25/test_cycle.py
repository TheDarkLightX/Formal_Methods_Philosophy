#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "generated" / "report.json"


def test_verifier_compiler_lower_bound() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "verifier compiler lower-bound frontier"
    assert report["quotient_state_count"] == 10
    assert report["exact_min_guard_count"] == 4
    assert report["no_exact_solution_leq_3"] is True
    assert [row["guard"] for row in report["pure_atom_summary"]["safe"]] == ["H6 > 869"]
    assert [row["guard"] for row in report["pure_atom_summary"]["fail_13116"]] == ["H6 = 869"]
    assert [row["guard"] for row in report["pure_atom_summary"]["fail_1915"]] == [
        "H6 = 859 and E = False",
        "H6 = 865",
    ]


if __name__ == "__main__":
    test_verifier_compiler_lower_bound()
    print("ok")
