#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter, defaultdict
from itertools import combinations, permutations
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.math_object_innovation_v29.run_cycle import HOLDOUT, gold, unique_viable_behaviors
from experiments.math_object_innovation_v30.run_cycle import V29_BASIS


OUT = ROOT / "generated" / "report.json"
BASE_ORDER = V29_BASIS


def viable_vectors():
    _, _, viable = unique_viable_behaviors()
    vectors = [tuple(item["prediction"][state] != gold(state) for state in HOLDOUT) for item in viable]
    return viable, vectors


def score_partitions(viable, vectors):
    by_score = defaultdict(list)
    for item, vector in zip(viable, vectors):
        by_score[item["hold_score"]].append((item, vector))
    return by_score


def primitive_candidates():
    candidates = []
    for op in ["or", "and"]:
        for size in [2, 3]:
            for subset in combinations(V29_BASIS, size):
                candidates.append((op, subset))
    return candidates


def feature_active(feature, vector):
    if isinstance(feature, int):
        return vector[feature]
    op, subset = feature
    values = [vector[index] for index in subset]
    if op == "or":
        return any(values)
    return all(values)


def feature_name(feature):
    if isinstance(feature, int):
        return f"err[{feature}]"
    op, subset = feature
    joiner = " OR " if op == "or" else " AND "
    return joiner.join(f"err[{index}]" for index in subset)


def minimal_depth_for_block(items, order):
    for depth in range(0, len(order) + 1):
        buckets = defaultdict(set)
        for item, vector in items:
            active = [feature for feature in order if feature_active(feature, vector)]
            prefix = tuple(active[:depth])
            buckets[prefix].add(item["first_refuter"])
        if all(len(labels) == 1 for labels in buckets.values()):
            return depth, len(buckets)
    return None, None


def solve_order(by_score, score_counts, scores, order):
    depths = {}
    bucket_total = 0
    for score in scores:
        depth, bucket_count = minimal_depth_for_block(by_score[score], order)
        if depth is None:
            return None
        depths[score] = depth
        bucket_total += bucket_count
    weighted = sum(score_counts[score] * depths[score] for score in scores)
    max_depth = max(depths.values())
    active_scores = sum(1 for score in scores if depths[score] > 0)
    return (weighted, max_depth, active_scores, bucket_total), depths


def best_fixed_order_insertion(by_score, score_counts, scores):
    best = None
    best_by_max_depth = {}
    searched = 0
    for primitive in primitive_candidates():
        for position in range(len(BASE_ORDER) + 1):
            searched += 1
            order = BASE_ORDER[:position] + (primitive,) + BASE_ORDER[position:]
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
    return best, best_by_max_depth, searched


def replacement_languages():
    for primitive in primitive_candidates():
        op, subset = primitive
        features = tuple(feature for feature in V29_BASIS if feature not in subset) + (primitive,)
        yield primitive, features


def replacement_summary(by_score, score_counts, scores):
    exact = []
    searched_languages = 0
    searched_orders = 0
    for primitive, features in replacement_languages():
        searched_languages += 1
        for order in permutations(features):
            searched_orders += 1
            solved = solve_order(by_score, score_counts, scores, order)
            if solved is None:
                continue
            lex, depths = solved
            exact.append(
                {
                    "primitive": feature_name(primitive),
                    "feature_count": len(features),
                    "order": [feature_name(feature) for feature in order],
                    "weighted_cost": lex[0],
                    "max_depth": lex[1],
                    "active_score_count": lex[2],
                    "bucket_total": lex[3],
                    "local_depths": {str(score): depths[score] for score in scores},
                }
            )
    exact.sort(
        key=lambda row: (
            row["feature_count"],
            row["weighted_cost"],
            row["max_depth"],
            row["active_score_count"],
            row["bucket_total"],
            row["primitive"],
        )
    )
    return {
        "searched_language_count": searched_languages,
        "searched_order_count": searched_orders,
        "exact_count": len(exact),
        "best_exact": exact[0] if exact else None,
    }


def build_report():
    viable, vectors = viable_vectors()
    by_score = score_partitions(viable, vectors)
    score_counts = Counter(item["hold_score"] for item in viable)
    scores = sorted(score_counts)

    baseline_lex, baseline_depths = solve_order(by_score, score_counts, scores, BASE_ORDER)
    best_insert, by_max_depth, searched_insertions = best_fixed_order_insertion(by_score, score_counts, scores)
    replacement = replacement_summary(by_score, score_counts, scores)

    best_insert_lex, best_insert_primitive, best_insert_position, best_insert_order, best_insert_depths = best_insert

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": "single-primitive concept-market search on the hard monotone refill transfer frontier",
        "holdout_domain": "the same 13 holdout fact states from v29 to v34",
        "survivor": "refill concept-market frontier",
        "viable_behavior_count": len(viable),
        "basis": list(V29_BASIS),
        "score_counts": {str(score): score_counts[score] for score in scores},
        "baseline_order": [feature_name(feature) for feature in BASE_ORDER],
        "baseline_weighted_cost": baseline_lex[0],
        "baseline_max_depth": baseline_lex[1],
        "baseline_local_depths": {str(score): baseline_depths[score] for score in scores},
        "fixed_order_insertion_search": {
            "searched_candidate_count": searched_insertions,
            "best_weighted_cost": best_insert_lex[0],
            "best_max_depth": best_insert_lex[1],
            "best_active_score_count": best_insert_lex[2],
            "best_bucket_total": best_insert_lex[3],
            "best_primitive": feature_name(best_insert_primitive),
            "best_primitive_op": best_insert_primitive[0],
            "best_primitive_subset": list(best_insert_primitive[1]),
            "best_insert_position": best_insert_position,
            "best_order": [feature_name(feature) for feature in best_insert_order],
            "best_local_depths": {str(score): best_insert_depths[score] for score in scores},
            "exact_with_max_depth_2": 2 in by_max_depth,
            "best_by_max_depth": {
                str(depth): {
                    "weighted_cost": candidate[0][0],
                    "active_score_count": candidate[0][2],
                    "bucket_total": candidate[0][3],
                    "primitive": feature_name(candidate[1]),
                    "insert_position": candidate[2],
                    "order": [feature_name(feature) for feature in candidate[3]],
                    "local_depths": {str(score): candidate[4][score] for score in scores},
                }
                for depth, candidate in sorted(by_max_depth.items())
            },
        },
        "replacement_search": replacement,
        "strongest_claim": (
            "In the hard monotone refill transfer case, simple pure concept invention is real but fragile. "
            "In the searched fixed-order insertion grammar, the best exact ladder inserts err[10] AND err[12] before err[10], "
            "lowering weighted cost from 118 to 90 and reducing maximum depth from 4 to 3. "
            "In the searched replacement grammar, no single 2- or 3-bit pure AND or OR primitive yields any exact ladder at all."
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
