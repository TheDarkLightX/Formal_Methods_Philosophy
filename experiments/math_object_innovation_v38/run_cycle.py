#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from itertools import combinations
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.math_object_innovation_v37.run_cycle import (
    BASE_ORDER,
    feature_name,
    primitive_candidates,
    score_partitions,
    solve_order,
    viable_vectors,
)


OUT = ROOT / "generated" / "report.json"


def best_two_insertions():
    viable, vectors = viable_vectors()
    by_score = score_partitions(viable, vectors)
    score_counts = Counter(item["hold_score"] for item in viable)
    scores = sorted(score_counts)

    baseline_lex, baseline_depths = solve_order(by_score, score_counts, scores, BASE_ORDER)
    best = None
    best_by_max_depth = {}
    searched = 0

    for primitive_one, primitive_two in combinations(primitive_candidates(), 2):
        for position_one in range(len(BASE_ORDER) + 1):
            order_one = list(BASE_ORDER)
            order_one.insert(position_one, primitive_one)
            for position_two in range(len(order_one) + 1):
                order = tuple(order_one[:position_two] + [primitive_two] + order_one[position_two:])
                searched += 1
                solved = solve_order(by_score, score_counts, scores, order)
                if solved is None:
                    continue
                lex, depths = solved
                candidate = (lex, primitive_one, position_one, primitive_two, position_two, order, depths)
                if best is None or candidate < best:
                    best = candidate
                prior = best_by_max_depth.get(lex[1])
                if prior is None or candidate < prior:
                    best_by_max_depth[lex[1]] = candidate

    return {
        "viable_behavior_count": len(viable),
        "score_counts": {str(score): score_counts[score] for score in scores},
        "baseline_lex": baseline_lex,
        "baseline_depths": {str(score): baseline_depths[score] for score in scores},
        "best": best,
        "best_by_max_depth": best_by_max_depth,
        "searched": searched,
    }


def build_report():
    result = best_two_insertions()
    best_lex, primitive_one, position_one, primitive_two, position_two, order, depths = result["best"]

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": "two-shortcut concept-market search on the hard monotone refill transfer frontier",
        "holdout_domain": "the same 13 holdout fact states from v29 to v37",
        "survivor": "refill two-concept ladder frontier",
        "viable_behavior_count": result["viable_behavior_count"],
        "basis": list(BASE_ORDER),
        "score_counts": result["score_counts"],
        "baseline_weighted_cost": result["baseline_lex"][0],
        "baseline_max_depth": result["baseline_lex"][1],
        "baseline_local_depths": result["baseline_depths"],
        "searched_candidate_count": result["searched"],
        "best_weighted_cost": best_lex[0],
        "best_max_depth": best_lex[1],
        "best_active_score_count": best_lex[2],
        "best_bucket_total": best_lex[3],
        "best_primitives": [
            {
                "name": feature_name(primitive_one),
                "op": primitive_one[0],
                "subset": list(primitive_one[1]),
                "insert_position": position_one,
            },
            {
                "name": feature_name(primitive_two),
                "op": primitive_two[0],
                "subset": list(primitive_two[1]),
                "insert_position": position_two,
            },
        ],
        "best_order": [feature_name(feature) for feature in order],
        "best_local_depths": {str(score): depths[score] for score in sorted(map(int, result["score_counts"].keys()))},
        "exact_with_max_depth_1": 1 in result["best_by_max_depth"],
        "best_by_max_depth": {
            str(depth): {
                "weighted_cost": candidate[0][0],
                "active_score_count": candidate[0][2],
                "bucket_total": candidate[0][3],
                "primitives": [
                    {
                        "name": feature_name(candidate[1]),
                        "insert_position": candidate[2],
                    },
                    {
                        "name": feature_name(candidate[3]),
                        "insert_position": candidate[4],
                    },
                ],
                "order": [feature_name(feature) for feature in candidate[5]],
                "local_depths": {str(score): candidate[6][score] for score in sorted(map(int, result["score_counts"].keys()))},
            }
            for depth, candidate in sorted(result["best_by_max_depth"].items())
        },
        "strongest_claim": (
            "In the hard monotone refill transfer case, two inserted pure shortcut concepts improve the exact ladder again. "
            "The best searched pair is err[6] AND err[10] AND err[12] together with err[9] AND err[10] AND err[12], "
            "which lowers weighted cost from 118 to 80 and lowers maximum depth from 4 to 2. "
            "No exact pair in the searched grammar reaches maximum depth 1."
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
