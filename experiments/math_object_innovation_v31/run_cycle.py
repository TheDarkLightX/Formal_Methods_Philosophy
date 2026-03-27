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

from experiments.math_object_innovation_v29.run_cycle import HOLDOUT, gold, unique_viable_behaviors
from experiments.math_object_innovation_v30.run_cycle import V29_BASIS, closure, exact_with_basis, horn_implications


OUT = ROOT / "generated" / "report.json"
MISSING_BITS = (5, 11)


def viable_vectors():
    _, _, viable = unique_viable_behaviors()
    vectors = [tuple(item["prediction"][state] != gold(state) for state in HOLDOUT) for item in viable]
    return viable, vectors


def first_mixed_bucket(viable, vectors, basis, implications):
    buckets = defaultdict(set)
    for item, vector in zip(viable, vectors):
        active = {index for index in basis if vector[index]}
        closed = closure(active, implications)
        key = (item["hold_score"],) + tuple(index in closed for index in range(len(HOLDOUT)))
        buckets[key].add(item["first_refuter"])
    for key, labels in buckets.items():
        if len(labels) > 1:
            return {
                "hold_score": key[0],
                "labels": [str(label) for label in sorted(labels, key=str)],
            }
    return None


def bucket_count_with_extra_bit(viable, vectors, basis, implications, extra_bit):
    buckets = defaultdict(set)
    for item, vector in zip(viable, vectors):
        active = {index for index in basis if vector[index]}
        closed = closure(active, implications)
        key = (item["hold_score"],) + tuple(index in closed for index in range(len(HOLDOUT))) + (vector[extra_bit],)
        buckets[key].add(item["first_refuter"])
    exact = all(len(labels) == 1 for labels in buckets.values())
    return exact, len(buckets)


def build_report():
    viable, vectors = viable_vectors()
    implications = horn_implications(vectors)
    exact, exact_bucket_count = exact_with_basis(viable, vectors, V29_BASIS, implications)

    drop_results = []
    for dropped in V29_BASIS:
        smaller = tuple(bit for bit in V29_BASIS if bit != dropped)
        still_exact, bucket_count = exact_with_basis(viable, vectors, smaller, implications)
        drop_results.append(
            {
                "dropped_bit": dropped,
                "exact": still_exact,
                "bucket_count": bucket_count,
                "first_mixed_bucket": None if still_exact else first_mixed_bucket(viable, vectors, smaller, implications),
            }
        )

    missing_results = []
    for bit in MISSING_BITS:
        still_exact, bucket_count = bucket_count_with_extra_bit(viable, vectors, V29_BASIS, implications, bit)
        missing_results.append(
            {
                "extra_bit": bit,
                "exact": still_exact,
                "bucket_count": bucket_count,
            }
        )

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": "irredundancy analysis for the Horn-closed semantic basis in the monotone refill transfer frontier",
        "holdout_domain": "the same 13 holdout fact states from v29 and v30",
        "survivor": "irredundant refill Horn basis frontier",
        "viable_behavior_count": len(viable),
        "basis": list(V29_BASIS),
        "basis_exact": exact,
        "basis_bucket_count": exact_bucket_count,
        "drop_results": drop_results,
        "missing_bit_results": missing_results,
        "strongest_claim": (
            "In the monotone refill transfer case, the 6-bit Horn-closed semantic basis is irredundant: dropping any retained bit destroys exact first-refuter classification. "
            "The two non-derivable bits from v30 are not required for exact classification. Adding either one can split already-pure buckets, but it does not improve label exactness."
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
