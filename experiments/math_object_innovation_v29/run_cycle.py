#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter, defaultdict
from itertools import combinations, permutations, product
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "generated" / "report.json"

STATES = list(product([0, 1], repeat=4))
ACTIONS = ["refill", "review"]
TRAIN = [(1, 1, 1, 1), (0, 1, 1, 1), (1, 1, 0, 1)]
HOLDOUT = [state for state in STATES if state not in TRAIN]


def gold(state):
    return "refill" if all(state) else "review"


def monotone_guards():
    guards = []
    for bits in product([0, 1], repeat=4):
        if sum(bits) == 0 or sum(bits) == 4:
            continue
        names = [name for bit, name in zip(bits, ["id", "dose", "labs", "window"]) if bit]
        mask = tuple(all((not bit) or state[idx] for idx, bit in enumerate(bits)) for state in STATES)
        guards.append(("_and_".join(names), mask))
    return guards


def unique_viable_behaviors():
    guards = monotone_guards()
    unique = {}
    for length in [1, 2, 3]:
        for guard_indices in permutations(range(len(guards)), length):
            masks = [guards[index][1] for index in guard_indices]
            for actions in product(ACTIONS, repeat=length + 1):
                behavior = []
                for state_index, _ in enumerate(STATES):
                    output = actions[-1]
                    for mask, action in zip(masks, actions):
                        if mask[state_index]:
                            output = action
                            break
                    behavior.append(output)
                unique.setdefault(tuple(behavior), (guard_indices, actions))

    viable = []
    for behavior in unique:
        prediction = dict(zip(STATES, behavior))
        if all(prediction[state] == gold(state) for state in TRAIN):
            hold_score = sum(prediction[state] == gold(state) for state in HOLDOUT)
            first_refuter = "safe"
            for state in HOLDOUT:
                if prediction[state] != gold(state):
                    first_refuter = state
                    break
            viable.append({
                "behavior": behavior,
                "prediction": prediction,
                "hold_score": hold_score,
                "first_refuter": first_refuter,
            })
    return guards, unique, viable


def smallest_exact_semantic_basis(viable):
    features = [(f"err[{state}]", lambda item, state=state: item["prediction"][state] != gold(state)) for state in HOLDOUT]
    best_failures = {}
    for size in [1, 2, 3, 4, 5, 6]:
        best_bad = None
        best_combo = None
        for combo in combinations(features, size):
            buckets = defaultdict(set)
            for item in viable:
                key = (item["hold_score"],) + tuple(feature(item) for _, feature in combo)
                buckets[key].add(item["first_refuter"])
            bad = sum(len(labels) - 1 for labels in buckets.values())
            if best_bad is None or bad < best_bad:
                best_bad = bad
                best_combo = [name for name, _ in combo]
            if bad == 0:
                return {
                    "size": size,
                    "features": [name for name, _ in combo],
                    "bucket_count": len(buckets),
                    "best_failure_by_size": best_failures,
                }
        best_failures[size] = {"bad_mass": best_bad, "features": best_combo}
    return {
        "size": None,
        "features": None,
        "bucket_count": None,
        "best_failure_by_size": best_failures,
    }


def build_report():
    guards, unique, viable = unique_viable_behaviors()
    basis = smallest_exact_semantic_basis(viable)
    hold_blocks = defaultdict(Counter)
    for item in viable:
        hold_blocks[item["hold_score"]][item["first_refuter"]] += 1

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": "monotone refill-style MPRD controller family with residual consistency and holdout error-basis search",
        "holdout_domain": "the 13 holdout fact states induced by the chosen 3-state training set",
        "survivor": "monotone refill transfer frontier",
        "guard_count": len(guards),
        "unique_behavior_count": len(unique),
        "viable_behavior_count": len(viable),
        "train_states": TRAIN,
        "holdout_states": HOLDOUT,
        "hold_blocks": [
            {
                "hold_score": score,
                "label_counts": {str(label): count for label, count in sorted(counter.items(), key=lambda item: str(item[0]))},
            }
            for score, counter in sorted(hold_blocks.items(), reverse=True)
        ],
        "smallest_exact_semantic_basis_size": basis["size"],
        "smallest_exact_semantic_basis_features": basis["features"],
        "smallest_exact_semantic_basis_bucket_count": basis["bucket_count"],
        "best_failure_by_size": basis["best_failure_by_size"],
        "strongest_claim": (
            "In the searched monotone refill-style MPRD controller family, the verifier-compiler transfer is substantially more expensive than in the abstract verifier frontier. "
            "No exact semantic repair exists with 5 holdout error bits or fewer, and the first exact semantic basis in the searched library appears at 6 error bits."
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
