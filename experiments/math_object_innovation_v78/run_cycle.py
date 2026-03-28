#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
OUT = ROOT / "generated" / "report.json"

V40_REPORT = REPO_ROOT / "experiments" / "math_object_innovation_v40" / "generated" / "report.json"
V44_REPORT = REPO_ROOT / "experiments" / "math_object_innovation_v44" / "generated" / "report.json"
V46_REPORT = REPO_ROOT / "experiments" / "math_object_innovation_v46" / "generated" / "report.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_report() -> dict:
    v40 = load(V40_REPORT)
    v44 = load(V44_REPORT)
    v46 = load(V46_REPORT)

    families = [
        {
            "family": "score_local_mixed_witnesses",
            "contract": "exact score-local positive-cover plus residual-default witnesses on each nontrivial score block",
            "cost_metric": "total positive witness count across nontrivial score blocks",
            "description_cost": v40["total_mixed_cost"],
            "region_count": v40["nontrivial_score_count"],
            "shared_schema": False,
            "source_cycle": "v40",
        },
        {
            "family": "merged_region_mixed_witnesses",
            "contract": "exact merged-region positive-cover plus residual-default witnesses on the best exact score partition",
            "cost_metric": "total positive witness count across exact merged regions",
            "description_cost": v44["best_total_cost"],
            "region_count": v44["best_region_count"],
            "shared_schema": False,
            "partition": v44["best_partition"],
            "source_cycle": "v44",
        },
        {
            "family": "shared_schema_witness_language",
            "contract": "exact shared witness-schema library over the best exact merged-region partition",
            "cost_metric": "distinct shared witness schemas",
            "description_cost": v46["best_shared_schema_count"],
            "region_count": len(v46["best_partition"]),
            "shared_schema": True,
            "partition": v46["best_partition"],
            "source_cycle": "v46",
        },
    ]

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": "hard-frontier minimal witness-language phase diagram over the v38 refill feature surface",
        "holdout_domain": "the same 13 holdout fact states used from v29 through v46",
        "survivor": "hard witness-language phase diagram",
        "local_all_positive_failure_scores": v40["all_positive_failure_scores"],
        "families": families,
        "strict_cost_ladder": [
            {
                "family": row["family"],
                "description_cost": row["description_cost"],
                "cost_metric": row["cost_metric"],
            }
            for row in families
        ],
        "strongest_claim": (
            "On the hard refill witness frontier, minimal witness-language discovery yields a strict bounded ladder once the witness contract is widened. "
            "Exact score-local residual-default witnesses cost 27, exact merged-region residual-default witnesses cost 22 on partition `(7), (8), (9), (10,11), (12)`, "
            "and the best exact shared witness-schema library over that same partition has size 19. Local all-positive witnesses already fail on scores 9 and 10. "
            "So the harder frontier does not merely tie several exact families. It orders them."
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
