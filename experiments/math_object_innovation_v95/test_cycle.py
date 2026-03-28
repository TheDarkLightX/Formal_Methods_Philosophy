#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "generated" / "report.json"


def ensure_report() -> dict:
    if not REPORT.exists():
        subprocess.run(["python3", str(ROOT / "run_cycle.py")], check=True)
    return json.loads(REPORT.read_text(encoding="utf-8"))


def main() -> int:
    report = ensure_report()
    assert report["survivor"] == "certificate-carrying repair basis"
    families = {row["family"]: row for row in report["families"]}
    for family_name in ("separable_patch_family", "overlap_patch_family"):
        family = families[family_name]
        assert family["candidate_count"] == 27
        assert family["minimal_exact_certificate_size"] == 3
        assert family["minimal_exact_certificate_bases"] == [["guard", "bounds", "transform"]]
        assert family["certificate_verification_cost"] == 3
        assert family["certificate_verification_cost"] < family["v94_dependency_fiber_average_eval_cost"]
        assert family["certificate_verification_cost"] < family["v94_monolithic_average_eval_cost"]
        size_two_rows = [row for row in family["basis_scan"] if row["size"] == 2]
        assert all(not row["exact"] for row in size_two_rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
