#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
V15_REPORT = REPO_ROOT / "experiments" / "math_object_innovation_v15" / "generated" / "report.json"
OUT = ROOT / "generated" / "report.json"


def build_report():
    v15 = json.loads(V15_REPORT.read_text(encoding="utf-8"))
    assert v15["first_safe_rank_without_bank"] == 1

    return {
        "tier": "descriptive_symbolic_controller",
        "oracle_dependent": False,
        "discovery_domain": "negative boundary derived from the v15 minimal-bank result",
        "holdout_domain": "same weighted 5x5 and 6x6 holdout used in v15",
        "survivor": "obligation-fiber proposer frontier",
        "global_safe_call_count": 1,
        "improvement_floor": 1,
        "strict_improvement_possible": False,
        "winning_pair": v15["target_safe_pair"],
        "strongest_claim": (
            "Once the globally ranked residual-consistent frontier already yields a safe repair program at call 1, "
            "obligation-fiber proposer specialization cannot strictly improve top-1 exact-safe discovery in this bounded model. "
            "Any remaining leverage from specialization must come from a different objective, such as top-k diversity or pre-frontier shaping."
        ),
    }


def main() -> int:
    report = build_report()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
