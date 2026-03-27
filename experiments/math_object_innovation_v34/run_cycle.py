#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter, defaultdict
from itertools import permutations
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.math_object_innovation_v29.run_cycle import HOLDOUT, gold, unique_viable_behaviors
from experiments.math_object_innovation_v30.run_cycle import V29_BASIS


OUT = ROOT / "generated" / "report.json"


def viable_vectors():
    _, _, viable = unique_viable_behaviors()
    vectors = [tuple(item["prediction"][state] != gold(state) for state in HOLDOUT) for item in viable]
    return viable, vectors


def score_partitions(viable, vectors):
    by_score = defaultdict(list)
    for item, vector in zip(viable, vectors):
        by_score[item["hold_score"]].append((item, vector))
    return by_score


def minimal_depth_for_block(items, order):
    for depth in range(0, 6):
        buckets = defaultdict(set)
        for item, vector in items:
            prefix = tuple(bit for bit in order if vector[bit])[:depth]
            buckets[prefix].add(item["first_refuter"])
        if all(len(labels) == 1 for labels in buckets.values()):
            return depth, len(buckets)
    return None, None


def build_report():
    viable, vectors = viable_vectors()
    by_score = score_partitions(viable, vectors)
    score_counts = Counter(item["hold_score"] for item in viable)
    scores = sorted(score_counts)

    best = None
    best_order = None
    best_depths = None
    best_bucket_total = None
    by_max_depth = {}
    per_score_lower_bound = {}

    for order in permutations(V29_BASIS):
        depths = {}
        bucket_total = 0
        feasible = True
        for score in scores:
            depth, bucket_count = minimal_depth_for_block(by_score[score], order)
            if depth is None:
                feasible = False
                break
            depths[score] = depth
            bucket_total += bucket_count
            prev = per_score_lower_bound.get(score)
            if prev is None or depth < prev:
                per_score_lower_bound[score] = depth
        if not feasible:
            continue

        weighted = sum(score_counts[score] * depths[score] for score in scores)
        max_depth = max(depths.values())
        active_scores = sum(1 for score in scores if depths[score] > 0)
        lex = (weighted, max_depth, active_scores, bucket_total)

        if best is None or lex < best:
            best = lex
            best_order = order
            best_depths = depths
            best_bucket_total = bucket_total

        prior = by_max_depth.get(max_depth)
        by_max_lex = (weighted, active_scores, bucket_total)
        if prior is None or by_max_lex < prior[0]:
            by_max_depth[max_depth] = (by_max_lex, order, depths)

    weighted_cost = best[0]
    max_depth = best[1]
    lower_bound = sum(score_counts[score] * per_score_lower_bound[score] for score in scores)

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": "regional explanation-ladder search on the monotone refill transfer frontier",
        "holdout_domain": "the same 13 holdout fact states from v29 to v33",
        "survivor": "regional refill ladder frontier",
        "viable_behavior_count": len(viable),
        "basis": list(V29_BASIS),
        "score_counts": {str(score): score_counts[score] for score in scores},
        "best_order": list(best_order),
        "best_local_depths": {str(score): best_depths[score] for score in scores},
        "weighted_cost": weighted_cost,
        "average_depth_numerator": weighted_cost,
        "average_depth_denominator": len(viable),
        "max_depth": max_depth,
        "active_score_count": best[2],
        "bucket_total": best_bucket_total,
        "global_k4_cost": 4 * len(viable),
        "global_k5_cost": 5 * len(viable),
        "scorewise_lower_bound": lower_bound,
        "exact_with_max_depth_3": 3 in by_max_depth,
        "best_by_max_depth": {
            str(depth): {
                "weighted_cost": data[0][0],
                "active_score_count": data[0][1],
                "bucket_total": data[0][2],
                "order": list(data[1]),
                "local_depths": {str(score): data[2][score] for score in scores},
            }
            for depth, data in sorted(by_max_depth.items())
        },
        "strongest_claim": (
            "In the monotone refill transfer case, a regional explanation ladder beats any global depth assignment by a large margin. "
            "The best exact ladder uses order (3,6,8,9,10,12), reaches weighted cost 118 with maximum depth 4, "
            "and no exact regional ladder exists with maximum depth 3."
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

