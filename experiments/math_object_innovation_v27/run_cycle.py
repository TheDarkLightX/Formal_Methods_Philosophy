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

from experiments.math_object_innovation_v26.run_cycle import HOLDOUT, build_report as build_v26_report, gold, unique_viable_behaviors


OUT = ROOT / "generated" / "report.json"


def semantic_feature_library():
    features = []
    for state in HOLDOUT:
        features.append((f"err[{state}]", lambda item, state=state: item["prediction"][state] != gold(state)))
        features.append((f"is_review[{state}]", lambda item, state=state: item["prediction"][state] == "review"))
        features.append((f"is_repeat[{state}]", lambda item, state=state: item["prediction"][state] == "repeat"))
        features.append((f"is_watch[{state}]", lambda item, state=state: item["prediction"][state] == "watch"))
    features.append(("error_count", lambda item: sum(item["prediction"][state] != gold(state) for state in HOLDOUT)))
    features.append(("review_count_holdout", lambda item: sum(item["prediction"][state] == "review" for state in HOLDOUT)))
    features.append(("repeat_count_holdout", lambda item: sum(item["prediction"][state] == "repeat" for state in HOLDOUT)))
    features.append(("watch_count_holdout", lambda item: sum(item["prediction"][state] == "watch" for state in HOLDOUT)))
    return features


def smallest_exact_semantic_repair(viable):
    features = semantic_feature_library()
    for size in [1, 2, 3, 4]:
        for combo in combinations(features, size):
            buckets = defaultdict(set)
            for item in viable:
                key = (item["hold_score"],) + tuple(feature(item) for _, feature in combo)
                buckets[key].add(item["first_refuter"])
            if all(len(labels) == 1 for labels in buckets.values()):
                return size, [name for name, _ in combo], len(buckets)
    return None, None, None


def build_report():
    _, _, viable = unique_viable_behaviors()
    base = build_v26_report()
    size, names, bucket_count = smallest_exact_semantic_repair(viable)
    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": "semantic repair search for the toy MPRD lab-followup transfer frontier",
        "holdout_domain": base["holdout_domain"],
        "survivor": "MPRD semantic repair frontier",
        "viable_behavior_count": base["viable_behavior_count"],
        "smallest_exact_semantic_repair_count": size,
        "smallest_exact_semantic_repair_features": names,
        "smallest_exact_semantic_repair_bucket_count": bucket_count,
        "strongest_claim": (
            "In the toy MPRD lab-followup transfer case, the first exact repair also appears in a semantic feature library, not only in raw predicted-action features. "
            "No exact semantic repair exists with `1`, `2`, or `3` features, and the first exact repair appears at `4` mistake-indicator bits: "
            "`err[(0, 0, 1)]`, `err[(0, 1, 0)]`, `err[(0, 1, 1)]`, and `err[(1, 1, 0)]`."
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
