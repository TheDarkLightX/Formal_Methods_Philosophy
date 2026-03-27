#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.math_object_innovation_v42.run_cycle import (
    FEATURES,
    NONTRIVIAL_SCORES,
    atom_candidates,
    feature_name,
    region_summary,
    rows,
)


OUT = ROOT / "generated" / "report.json"


def all_set_partitions(values):
    values = list(values)

    def rec(seq):
        if not seq:
            yield []
            return
        first, rest = seq[0], seq[1:]
        for part in rec(rest):
            yield [(first,), *part]
            for index in range(len(part)):
                merged = tuple(sorted((first,) + tuple(part[index])))
                new_part = part[:index] + [merged] + part[index + 1 :]
                canon = tuple(sorted(tuple(sorted(block)) for block in new_part))
                yield [tuple(block) for block in canon]

    seen = set()
    for partition in rec(values):
        canon = tuple(sorted(tuple(sorted(block)) for block in partition))
        if canon in seen:
            continue
        seen.add(canon)
        yield [tuple(block) for block in canon]


def build_report():
    all_rows = rows()
    atoms = atom_candidates()
    grouped_rows = defaultdict(list)
    for row in all_rows:
        grouped_rows[row["score"]].append(row)

    feasible = []
    partition_count = 0
    for partition in all_set_partitions(NONTRIVIAL_SCORES):
        partition_count += 1
        summaries = [region_summary(region, grouped_rows, atoms) for region in partition]
        if not all(summary["possible"] for summary in summaries):
            continue
        total_cost = sum(summary["cost"] for summary in summaries)
        feasible.append((total_cost, len(partition), partition, summaries))

    feasible.sort(key=lambda item: (item[0], item[1], item[2]))
    best_cost, best_region_count, best_partition, best_summaries = feasible[0]

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": "unconstrained score-partition search over exact mixed-sign witness regions on the hard v38 feature frontier",
        "holdout_domain": "the same 13 holdout fact states from v29 to v42",
        "survivor": "unconstrained score-abstraction boundary frontier",
        "feature_count": len(FEATURES),
        "feature_names": [feature_name(feature) for feature in FEATURES],
        "atom_count": len(atoms),
        "nontrivial_scores": list(NONTRIVIAL_SCORES),
        "partition_count": partition_count,
        "feasible_partition_count": len(feasible),
        "best_total_cost": best_cost,
        "best_region_count": best_region_count,
        "best_partition": [list(region) for region in best_partition],
        "best_region_summaries": [
            {
                "scores": list(region),
                "cost": summary["cost"],
                "default_label": summary["default_label"],
                "label_count": summary["label_count"],
                "row_count": summary["row_count"],
            }
            for region, summary in zip(best_partition, best_summaries)
        ],
        "top_feasible_partitions": [
            {
                "total_cost": total_cost,
                "region_count": region_count,
                "partition": [list(region) for region in partition],
            }
            for total_cost, region_count, partition, _ in feasible[:10]
        ],
        "strongest_claim": (
            "In the searched unconstrained score-partition space, only 10 of 203 set partitions are exact, and the same partition from v42, "
            "(7), (8), (9), (10,11), (12), remains optimal with total witness cost 23."
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
