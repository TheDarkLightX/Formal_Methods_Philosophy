#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict
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


def bad_mass_for_order(viable, vectors, order, k):
    buckets = defaultdict(set)
    for item, vector in zip(viable, vectors):
        active_prefix = tuple(bit for bit in order if vector[bit])[:k]
        buckets[(item["hold_score"], active_prefix)].add(item["first_refuter"])
    bad_mass = sum(len(labels) - 1 for labels in buckets.values())
    return bad_mass, len(buckets)


def analyze():
    viable, vectors = viable_vectors()
    results = {}
    for k in [3, 4, 5]:
        exact_orders = []
        best_bad = None
        best_order = None
        best_bucket_count = None
        for order in permutations(V29_BASIS):
            bad_mass, bucket_count = bad_mass_for_order(viable, vectors, order, k)
            if best_bad is None or bad_mass < best_bad:
                best_bad = bad_mass
                best_order = order
                best_bucket_count = bucket_count
            if bad_mass == 0:
                exact_orders.append(order)
        results[k] = {
            "exact_order_count": len(exact_orders),
            "example_exact_order": list(exact_orders[0]) if exact_orders else None,
            "best_bad_mass": best_bad,
            "best_order": list(best_order),
            "best_bucket_count": best_bucket_count,
        }
    return viable, results


def build_report():
    viable, results = analyze()
    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": "ordered active-prefix compiler search over the irredundant monotone refill basis",
        "holdout_domain": "the same 13 holdout fact states from v29 to v31",
        "survivor": "ordered refill basis compiler frontier",
        "viable_behavior_count": len(viable),
        "basis": list(V29_BASIS),
        "k3": results[3],
        "k4": results[4],
        "k5": results[5],
        "strongest_claim": (
            "In the monotone refill transfer case, the essential six-bit basis admits an ordered compiler law. "
            "No order is exact with only the first 3 active basis bits, some orders are exact with the first 4 active basis bits, "
            "and every order is exact with the first 5 active basis bits."
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

