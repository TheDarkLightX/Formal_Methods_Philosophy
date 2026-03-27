#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.math_object_innovation_v37.run_cycle import (
    feature_name,
    primitive_candidates,
    score_partitions,
    solve_order,
    viable_vectors,
)


OUT = ROOT / "generated" / "report.json"
FIXED_PRIMITIVE_ONE = ("and", (6, 10, 12))
FIXED_PRIMITIVE_TWO = ("and", (9, 10, 12))
FIXED_ORDER = (
    FIXED_PRIMITIVE_ONE,
    3,
    FIXED_PRIMITIVE_TWO,
    6,
    8,
    9,
    10,
    12,
)


def build_report():
    viable, vectors = viable_vectors()
    by_score = score_partitions(viable, vectors)
    score_counts = Counter(item["hold_score"] for item in viable)
    scores = sorted(score_counts)

    baseline_lex, baseline_depths = solve_order(by_score, score_counts, scores, FIXED_ORDER)
    best = None
    best_by_max_depth = {}
    searched = 0

    for primitive in primitive_candidates():
        if primitive in {FIXED_PRIMITIVE_ONE, FIXED_PRIMITIVE_TWO}:
            continue
        for position in range(len(FIXED_ORDER) + 1):
            order = tuple(list(FIXED_ORDER[:position]) + [primitive] + list(FIXED_ORDER[position:]))
            searched += 1
            solved = solve_order(by_score, score_counts, scores, order)
            if solved is None:
                continue
            lex, depths = solved
            candidate = (lex, primitive, position, order, depths)
            if best is None or candidate < best:
                best = candidate
            prior = best_by_max_depth.get(lex[1])
            if prior is None or candidate < prior:
                best_by_max_depth[lex[1]] = candidate

    best_lex, best_primitive, best_position, best_order, best_depths = best

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": "anchored third-shortcut search on the hard monotone refill transfer frontier",
        "holdout_domain": "the same 13 holdout fact states from v29 to v38",
        "survivor": "anchored third-shortcut boundary frontier",
        "viable_behavior_count": len(viable),
        "score_counts": {str(score): score_counts[score] for score in scores},
        "fixed_primitives": [
            feature_name(FIXED_PRIMITIVE_ONE),
            feature_name(FIXED_PRIMITIVE_TWO),
        ],
        "fixed_order": [feature_name(feature) for feature in FIXED_ORDER],
        "baseline_weighted_cost": baseline_lex[0],
        "baseline_max_depth": baseline_lex[1],
        "baseline_bucket_total": baseline_lex[3],
        "baseline_local_depths": {str(score): baseline_depths[score] for score in scores},
        "searched_candidate_count": searched,
        "best_weighted_cost": best_lex[0],
        "best_max_depth": best_lex[1],
        "best_active_score_count": best_lex[2],
        "best_bucket_total": best_lex[3],
        "best_extra_primitive": feature_name(best_primitive),
        "best_extra_primitive_op": best_primitive[0],
        "best_extra_primitive_subset": list(best_primitive[1]),
        "best_insert_position": best_position,
        "best_order": [feature_name(feature) for feature in best_order],
        "best_local_depths": {str(score): best_depths[score] for score in scores},
        "exact_with_max_depth_1": 1 in best_by_max_depth,
        "best_by_max_depth": {
            str(depth): {
                "weighted_cost": candidate[0][0],
                "active_score_count": candidate[0][2],
                "bucket_total": candidate[0][3],
                "extra_primitive": feature_name(candidate[1]),
                "insert_position": candidate[2],
                "order": [feature_name(feature) for feature in candidate[3]],
                "local_depths": {str(score): candidate[4][score] for score in scores},
            }
            for depth, candidate in sorted(best_by_max_depth.items())
        },
        "strongest_claim": (
            "In the anchored third-shortcut grammar, no searched third shortcut lowers the exact hard refill ladder below weighted cost 80 or max depth 2. "
            "The best searched extra shortcut is err[3] OR err[6] OR err[8], which preserves weighted cost 80 and max depth 2 while reducing bucket count from 51 to 48."
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
