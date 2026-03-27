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


def exact_4(order, viable, vectors):
    buckets = defaultdict(set)
    for item, vector in zip(viable, vectors):
        active_prefix = tuple(bit for bit in order if vector[bit])[:4]
        buckets[(item["hold_score"], active_prefix)].add(item["first_refuter"])
    return all(len(labels) == 1 for labels in buckets.values())


def law(order):
    first4 = set(order[:4])
    if 3 in first4:
        return bool(first4 & {6, 8})
    if {6, 8}.issubset(first4):
        omitted = list(set(V29_BASIS) - first4 - {3})
        assert len(omitted) == 1
        return order.index(3) < order.index(omitted[0])
    return False


def build_report():
    viable, vectors = viable_vectors()
    mismatches = []
    exact_examples = []
    inexact_examples = []
    exact_count = 0
    for order in permutations(V29_BASIS):
        exact = exact_4(order, viable, vectors)
        predicted = law(order)
        if exact:
            exact_count += 1
            if len(exact_examples) < 5:
                exact_examples.append(list(order))
        else:
            if len(inexact_examples) < 5:
                inexact_examples.append(list(order))
        if exact != predicted and len(mismatches) < 10:
            mismatches.append(
                {
                    "order": list(order),
                    "exact_4": exact,
                    "law": predicted,
                }
            )

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": "exact order-law discovery for the k=4 monotone refill ordered-basis compiler",
        "holdout_domain": "the same 13 holdout fact states from v29 to v32",
        "survivor": "k4 refill order law frontier",
        "viable_behavior_count": len(viable),
        "basis": list(V29_BASIS),
        "exact_order_count": exact_count,
        "total_order_count": 720,
        "law_exact_match": len(mismatches) == 0,
        "mismatches": mismatches,
        "example_exact_orders": exact_examples,
        "example_inexact_orders": inexact_examples,
        "strongest_claim": (
            "In the monotone refill transfer case, the k=4 ordered-basis compiler frontier has an exact structural law. "
            "An order is exact iff its first four positions either contain bit 3 and at least one of {6,8}, "
            "or else contain both 6 and 8 while deferring 3 only ahead of the unique omitted bit from {9,10,12}."
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

