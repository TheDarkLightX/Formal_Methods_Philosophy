#!/usr/bin/env python3
from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
OUT = ROOT / "generated" / "report.json"

V44_REPORT = REPO_ROOT / "experiments" / "math_object_innovation_v44" / "generated" / "report.json"
V80_REPORT = REPO_ROOT / "experiments" / "math_object_innovation_v80" / "generated" / "report.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def region_key(region: list[int] | tuple[int, ...]) -> tuple[int, ...]:
    return tuple(region)


def region_schemas(summary: dict, key: str) -> set[str]:
    schemas: set[str] = set()
    for formulas in summary[key].values():
        schemas.update(formulas)
    return schemas


def build_report() -> dict:
    v44 = load(V44_REPORT)
    v80 = load(V80_REPORT)

    regions = tuple(region_key(region) for region in v44["best_partition"])
    residual_regions = {
        region_key(row["scores"]): row for row in v44["best_region_summaries"]
    }
    certificate_regions = {
        region_key(row["scores"]): row for row in v80["region_reports"]
    }

    ladder = []
    feasible_subsets_all = []
    for residual_budget in range(len(regions) + 1):
        feasible_rows = []
        for subset in combinations(regions, residual_budget):
            subset_set = set(subset)
            total_cost = 0
            shared_schemas: set[str] = set()
            possible = True

            for region in regions:
                if region in subset_set:
                    summary = residual_regions[region]
                    total_cost += summary["cost"]
                    shared_schemas.update(region_schemas(summary, "language"))
                else:
                    summary = certificate_regions[region]
                    if not summary["possible"]:
                        possible = False
                        break
                    total_cost += summary["total_cost"]
                    shared_schemas.update(region_schemas(summary, "covers"))

            if not possible:
                continue

            feasible_rows.append(
                {
                    "residual_regions": [list(region) for region in subset],
                    "total_cost": total_cost,
                    "shared_schema_count": len(shared_schemas),
                }
            )
            feasible_subsets_all.append(set(subset))

        if not feasible_rows:
            ladder.append(
                {
                    "residual_region_count": residual_budget,
                    "feasible_subset_count": 0,
                    "optimal_total_cost": None,
                    "optimal_shared_schema_count": None,
                    "optimal_subsets": [],
                }
            )
            continue

        feasible_rows.sort(
            key=lambda row: (
                row["total_cost"],
                row["shared_schema_count"],
                row["residual_regions"],
            )
        )
        best_cost = feasible_rows[0]["total_cost"]
        best_shared = feasible_rows[0]["shared_schema_count"]
        optimal_subsets = [
            row["residual_regions"]
            for row in feasible_rows
            if row["total_cost"] == best_cost
            and row["shared_schema_count"] == best_shared
        ]
        ladder.append(
            {
                "residual_region_count": residual_budget,
                "feasible_subset_count": len(feasible_rows),
                "optimal_total_cost": best_cost,
                "optimal_shared_schema_count": best_shared,
                "optimal_subsets": optimal_subsets,
            }
        )

    minimum_exact_budget = next(
        row["residual_region_count"]
        for row in ladder
        if row["optimal_total_cost"] is not None
    )
    mandatory_regions = sorted(
        [list(region) for region in set.intersection(*feasible_subsets_all)],
        key=lambda region: tuple(region),
    )
    strict_cost_ladder = [
        {
            "residual_region_count": row["residual_region_count"],
            "optimal_total_cost": row["optimal_total_cost"],
            "optimal_shared_schema_count": row["optimal_shared_schema_count"],
        }
        for row in ladder
        if row["optimal_total_cost"] is not None
    ]

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "exact local residual-budget search on the hard v44 merged-region "
            "partition, mixing residual-default witness regions with "
            "all-positive certificate regions"
        ),
        "holdout_domain": "the same 13 holdout fact states used from v29 through v46",
        "survivor": "hard local residual-budget ladder",
        "best_partition": [list(region) for region in regions],
        "residual_budget_ladder": ladder,
        "minimum_exact_residual_region_count": minimum_exact_budget,
        "mandatory_residual_regions": mandatory_regions,
        "strict_cost_ladder": strict_cost_ladder,
        "strongest_claim": (
            "On the hard merged-region witness frontier, exactness in the "
            "searched 1-to-4-literal conjunction grammar already returns once "
            "a single region is allowed residual-default witnessing, but that "
            "region is forced to be `(10,11)`. As the residual budget rises "
            "from 1 to 5 regions, the best exact total cost drops strictly "
            "from 28 to 26 to 24 to 23 to 22. So residual structure on this "
            "frontier is locally budgetable rather than all-or-nothing."
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
