#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.math_object_innovation_v26.run_cycle import HOLDOUT, gold, unique_viable_behaviors


OUT = ROOT / "generated" / "report.json"


def error_vector(item):
    return tuple(item["prediction"][state] != gold(state) for state in HOLDOUT)


def earliest_error_label(errs):
    for state, bit in zip(HOLDOUT, errs):
        if bit:
            return state
    return "safe"


def exact_with_indices(viable, indices):
    buckets = defaultdict(set)
    for item in viable:
        errs = error_vector(item)
        key = (item["hold_score"],) + tuple(errs[i] for i in indices)
        buckets[key].add(item["first_refuter"])
    exact = all(len(labels) == 1 for labels in buckets.values())
    witness = None
    if not exact:
        for key, labels in buckets.items():
            if len(labels) > 1:
                witness = {"key": key, "labels": sorted(labels, key=str)}
                break
    return exact, witness, len(buckets)


def build_report():
    _, _, viable = unique_viable_behaviors()
    earliest_exact = True
    for item in viable:
        errs = error_vector(item)
        if earliest_error_label(errs) != item["first_refuter"]:
            earliest_exact = False
            break

    exact_four, _, bucket_count_four = exact_with_indices(viable, (0, 1, 2, 3))

    three_bit_results = []
    for combo in combinations(range(5), 3):
        exact, witness, bucket_count = exact_with_indices(viable, combo)
        three_bit_results.append({
            "indices": combo,
            "exact": exact,
            "bucket_count": bucket_count,
            "witness": witness,
        })

    four_bit_results = []
    for combo in combinations(range(5), 4):
        exact, witness, bucket_count = exact_with_indices(viable, combo)
        four_bit_results.append({
            "indices": combo,
            "exact": exact,
            "bucket_count": bucket_count,
            "witness": witness,
        })

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": "earliest-error symbolic compiler law for the toy MPRD transfer frontier",
        "holdout_domain": "the 5 ordered holdout fact states induced by the chosen 3-state training set",
        "survivor": "earliest-error compiler frontier",
        "viable_behavior_count": len(viable),
        "holdout_order": HOLDOUT,
        "earliest_error_exact": earliest_exact,
        "four_bit_basis_exact": exact_four,
        "four_bit_basis_bucket_count": bucket_count_four,
        "three_bit_results": three_bit_results,
        "four_bit_results": four_bit_results,
        "logic_formulas": [
            "Let e_i(x) be the error bit on the i-th holdout state h_i.",
            "Safe(x) ↔ ¬e_1(x) ∧ ¬e_2(x) ∧ ¬e_3(x) ∧ ¬e_4(x) ∧ ¬e_5(x).",
            "FirstRefuter(x) = h_i ↔ ¬e_1(x) ∧ ... ∧ ¬e_{i-1}(x) ∧ e_i(x).",
            "S(x) = 5 - (e_1(x) + e_2(x) + e_3(x) + e_4(x) + e_5(x)).",
            "So e_5(x) = 5 - S(x) - e_1(x) - e_2(x) - e_3(x) - e_4(x).",
        ],
        "strongest_claim": (
            "In the toy MPRD lab-followup transfer case, the first-refuter label is exactly the earliest holdout error in the fixed holdout order. "
            "The basis `holdout score + (e1,e2,e3,e4)` is exact, and every searched three-bit subbasis fails. "
            "So the semantic repair basis from v27 compresses further into an earliest-error compiler law with a minimal ordered-error basis."
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
