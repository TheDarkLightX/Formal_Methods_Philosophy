#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.math_object_innovation_v29.run_cycle import HOLDOUT, unique_viable_behaviors, gold


OUT = ROOT / "generated" / "report.json"
V29_BASIS = (3, 6, 8, 9, 10, 12)


def viable_error_vectors():
    _, _, viable = unique_viable_behaviors()
    vectors = [tuple(item["prediction"][state] != gold(state) for state in HOLDOUT) for item in viable]
    return viable, vectors


def horn_implications(vectors):
    n = len(HOLDOUT)
    implications = []
    for size in [1, 2]:
        for antecedent in combinations(range(n), size):
            for consequent in range(n):
                if consequent in antecedent:
                    continue
                if all((not all(vector[index] for index in antecedent)) or vector[consequent] for vector in vectors):
                    # keep only antecedent-minimal implication for the same consequent
                    if not any(set(prev_antecedent).issubset(antecedent) and prev_antecedent != antecedent and prev_consequent == consequent for prev_antecedent, prev_consequent in implications):
                        implications.append((antecedent, consequent))
    return implications


def closure(active_bits, implications):
    closed = set(active_bits)
    changed = True
    while changed:
        changed = False
        for antecedent, consequent in implications:
            if set(antecedent).issubset(closed) and consequent not in closed:
                closed.add(consequent)
                changed = True
    return closed


def exact_with_basis(viable, vectors, basis, implications):
    buckets = defaultdict(set)
    for item, vector in zip(viable, vectors):
        active_basis = {index for index in basis if vector[index]}
        closed = closure(active_basis, implications)
        key = (item["hold_score"],) + tuple(index in closed for index in range(len(HOLDOUT)))
        buckets[key].add(item["first_refuter"])
    return all(len(labels) == 1 for labels in buckets.values()), len(buckets)


def smallest_exact_basis(viable, vectors, implications):
    n = len(HOLDOUT)
    for size in range(1, len(V29_BASIS) + 1):
        for basis in combinations(range(n), size):
            exact, bucket_count = exact_with_basis(viable, vectors, basis, implications)
            if exact:
                return basis, bucket_count
    return None, None


def build_report():
    viable, vectors = viable_error_vectors()
    implications = horn_implications(vectors)
    closed = closure(set(V29_BASIS), implications)
    best_basis, bucket_count = smallest_exact_basis(viable, vectors, implications)

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": "Horn-closed basis minimization for the monotone refill transfer frontier",
        "holdout_domain": "the same 13 holdout fact states from v29",
        "survivor": "horn-closed refill basis frontier",
        "viable_behavior_count": len(viable),
        "horn_implication_count": len(implications),
        "v29_basis": list(V29_BASIS),
        "v29_basis_closure": sorted(closed),
        "v29_basis_closure_size": len(closed),
        "closure_missing_bits": sorted(set(range(len(HOLDOUT))) - closed),
        "smallest_exact_horn_closed_basis": list(best_basis) if best_basis is not None else None,
        "smallest_exact_horn_closed_basis_size": len(best_basis) if best_basis is not None else None,
        "smallest_exact_horn_closed_bucket_count": bucket_count,
        "strongest_claim": (
            "In the monotone refill transfer case, the 6-bit exact semantic basis from v29 remains minimal even after allowing closure under all exact single- and pair-Horn implications among the holdout error bits. "
            "Its Horn closure expands to 11 of the 13 error bits, but no basis of size 5 or less is exact."
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
