#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter, defaultdict
from itertools import combinations, permutations, product
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "generated" / "report.json"

STATES = [(p, r, a) for p, r, a in product([0, 1], [0, 1], [0, 1])]
ACTIONS = ["watch", "repeat", "review"]
TRAIN = [(1, 0, 0), (1, 0, 1), (0, 0, 0)]
HOLDOUT = [state for state in STATES if state not in TRAIN]


def gold(state):
    pathway_open, red_flag, abnormal = state
    if (not pathway_open) or red_flag:
        return "review"
    if abnormal:
        return "repeat"
    return "watch"


def guard_library():
    guards = []
    literals = []
    for idx, name in enumerate(["p", "r", "a"]):
        literals.append((name, lambda state, idx=idx: state[idx] == 1))
        literals.append((f"not_{name}", lambda state, idx=idx: state[idx] == 0))

    guards.extend(literals)
    for i in range(len(literals)):
        for j in range(i + 1, len(literals)):
            name_i = literals[i][0]
            name_j = literals[j][0]
            if name_i.replace("not_", "") == name_j.replace("not_", ""):
                continue
            guards.append((
                f"{name_i}_and_{name_j}",
                lambda state, f_i=literals[i][1], f_j=literals[j][1]: f_i(state) and f_j(state),
            ))

    for bits in product([0, 1], repeat=3):
        guards.append((
            "_and_".join((
                "p" if bits[0] else "not_p",
                "r" if bits[1] else "not_r",
                "a" if bits[2] else "not_a",
            )),
            lambda state, bits=bits: all(state[idx] == bits[idx] for idx in range(3)),
        ))

    best = {}
    for name, guard in guards:
        mask = tuple(guard(state) for state in STATES)
        if all(mask) or not any(mask):
            continue
        if mask not in best or len(name) < len(best[mask][0]):
            best[mask] = (name, guard)
    return list(best.values())


def controller_output(guard_indices, actions, guards):
    behavior = []
    for state in STATES:
        output = actions[-1]
        for guard_index, action in zip(guard_indices, actions):
            if guards[guard_index][1](state):
                output = action
                break
        behavior.append(output)
    return tuple(behavior)


def unique_viable_behaviors():
    guards = guard_library()
    unique = {}
    for length in [1, 2, 3]:
        for guard_indices in permutations(range(len(guards)), length):
            if len(set(guard_indices)) < length:
                continue
            for actions in product(ACTIONS, repeat=length + 1):
                behavior = controller_output(guard_indices, actions, guards)
                unique.setdefault(behavior, (guard_indices, actions))

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


def feature_library():
    features = []
    for state in HOLDOUT:
        features.append((f"pred[{state}]", lambda item, state=state: item["prediction"][state]))
    for action in ACTIONS:
        features.append((f"count[{action}]", lambda item, action=action: sum(1 for value in item["behavior"] if value == action)))
    return features


def exact_repair_size(viable):
    features = feature_library()
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
    guards, unique, viable = unique_viable_behaviors()
    size, names, bucket_count = exact_repair_size(viable)
    hold_blocks = defaultdict(Counter)
    for item in viable:
        hold_blocks[item["hold_score"]][item["first_refuter"]] += 1

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": "MPRD-shaped toy lab-followup controller family with residual consistency, score blocks, and behavior-feature repair search",
        "holdout_domain": "the 5 holdout fact states induced by the chosen 3-state training set",
        "survivor": "MPRD transfer boundary frontier",
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
        "smallest_exact_repair_feature_count": size,
        "smallest_exact_repair_features": names,
        "smallest_exact_repair_bucket_count": bucket_count,
        "strongest_claim": (
            "In the searched toy MPRD lab-followup controller family, the quotient-and-repair loop does not transfer as cheaply as in the abstract verifier frontier. "
            "On the residual-consistent unique-behavior frontier, `holdout score + 1`, `+2`, and `+3` simple behavior features are all insufficient to recover the full first-refuter partition. "
            "The first exact repair in the searched library appears at 4 predicted-action features: "
            "`pred[(0, 0, 1)]`, `pred[(0, 1, 0)]`, `pred[(0, 1, 1)]`, and `pred[(1, 1, 0)]`."
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
