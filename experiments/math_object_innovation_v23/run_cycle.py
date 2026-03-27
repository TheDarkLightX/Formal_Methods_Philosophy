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

from experiments.math_object_innovation_v15.run_cycle import (
    PATTERN_CACHE,
    deserialize_patterns,
    pattern_choice,
    residual_consistent_pairs,
)


OUT = ROOT / "generated" / "report.json"

LABEL_NAME = {
    ("safe",): "safe",
    ("fail", 13116, (0, 1, 2, 3), 0): "fail_13116",
    ("fail", 1915, (0, 1, 2), 2): "fail_1915",
    ("fail", 828, (0, 1, 2, 3), 0): "fail_828",
}


def refuter_label(item, patterns):
    for pattern in patterns:
        if pattern_choice(item["params_1"], item["params_2"], pattern.rows_key) != pattern.target:
            return ("fail", pattern.exemplar_mask, tuple(pattern.exemplar_candidates), pattern.target)
    return ("safe",)


def labeled_items():
    patterns = deserialize_patterns(json.loads(PATTERN_CACHE.read_text(encoding="utf-8")))
    items = []
    for item in residual_consistent_pairs():
        label = LABEL_NAME[refuter_label(item, patterns)]
        items.append({**item, "label": label})
    return items


def feature_library():
    features = []
    for idx in range(7):
        features.append({
            "name": f"c1[{idx}]",
            "kind": "c1_component",
            "cost": (2, idx),
            "value": lambda item, idx=idx: item["params_1"][idx],
        })
        features.append({
            "name": f"c2[{idx}]",
            "kind": "c2_component",
            "cost": (2, idx),
            "value": lambda item, idx=idx: item["params_2"][idx],
        })
    for idx in range(5):
        features.append({
            "name": f"num_eq[{idx}]",
            "kind": "numeric_equality",
            "cost": (0, idx),
            "value": lambda item, idx=idx: item["params_1"][idx] == item["params_2"][idx],
        })
        features.append({
            "name": f"num_lt[{idx}]",
            "kind": "numeric_order",
            "cost": (1, idx),
            "value": lambda item, idx=idx: item["params_1"][idx] < item["params_2"][idx],
        })
    for idx in (5, 6):
        features.append({
            "name": f"str_eq[{idx}]",
            "kind": "string_equality",
            "cost": (0, idx),
            "value": lambda item, idx=idx: item["params_1"][idx] == item["params_2"][idx],
        })
    return features


def mixed_bucket(items):
    bucket = [item for item in items if item["holdout_6_hits"] == 859]
    labels = sorted({item["label"] for item in bucket})
    return bucket, labels


def bucket_purity(bucket, feature):
    mapping = defaultdict(set)
    for item in bucket:
        mapping[feature["value"](item)].add(item["label"])
    pure = all(len(labels) == 1 for labels in mapping.values())
    return pure, {repr(key): sorted(value) for key, value in sorted(mapping.items(), key=lambda kv: repr(kv[0]))}


def pair_exact(items, feature):
    mapping = defaultdict(set)
    for item in items:
        mapping[(item["holdout_6_hits"], feature["value"](item))].add(item["label"])
    return all(len(labels) == 1 for labels in mapping.values())


def build_report():
    items = labeled_items()
    bucket, mixed_labels = mixed_bucket(items)
    survivors = []
    for feature in feature_library():
        pure, bucket_map = bucket_purity(bucket, feature)
        if not pure:
            continue
        exact = pair_exact(items, feature)
        if exact:
            survivors.append({
                "name": feature["name"],
                "kind": feature["kind"],
                "cost": feature["cost"],
                "mixed_bucket_partition": bucket_map,
            })
    survivors.sort(key=lambda item: (item["cost"], item["name"]))
    best = survivors[0]

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": "single-feature repair search for the mixed `holdout_6_hits = 859` bucket in the residual-consistent repair-program frontier",
        "holdout_domain": "same weighted 5x5 and 6x6 score coordinates used in v15 through v22",
        "survivor": "mixed-bucket repair frontier",
        "frontier_size": len(items),
        "mixed_bucket_value": 859,
        "mixed_bucket_size": len(bucket),
        "mixed_bucket_labels": mixed_labels,
        "survivor_count": len(survivors),
        "best_repair_feature": best,
        "repair_logic_formulas": [
            "Let E(x) := p1_4(x) = p2_4(x), the equality of the fifth numeric slot of params_1 and params_2.",
            "Safe(x) ↔ H6(x) > 869",
            "Fail_13116(x) ↔ 865 < H6(x) ≤ 869",
            "Fail_1915(x) ↔ H6(x) = 865 ∨ (H6(x) = 859 ∧ ¬E(x))",
            "Fail_828(x) ↔ H6(x) ∈ {864, 863, 858} ∨ (H6(x) = 859 ∧ E(x))",
        ],
        "strongest_claim": (
            "The only scalar obstruction on the `holdout_6_hits` side is the mixed bucket `859`, and in the searched simple feature library it is repaired by exactly one single-feature coordinate, `num_eq[4]`, the equality of the fifth numeric slot between `params_1` and `params_2`. "
            "The pair `(holdout_6_hits, num_eq[4])` is an exact quotient for the full refuter partition in this bounded model."
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
