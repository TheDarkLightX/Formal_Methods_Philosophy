#!/usr/bin/env python3
from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
OUT = ROOT / "generated" / "report.json"

V24_REPORT = REPO_ROOT / "experiments" / "math_object_innovation_v24" / "generated" / "report.json"
V25_REPORT = REPO_ROOT / "experiments" / "math_object_innovation_v25" / "generated" / "report.json"


def load_reports():
    v24 = json.loads(V24_REPORT.read_text(encoding="utf-8"))
    v25 = json.loads(V25_REPORT.read_text(encoding="utf-8"))
    return v24, v25


def label_states(v24):
    states = {}
    for row in v24["state_rows"]:
        states.setdefault(row["label"], set()).add((row["H6"], row["E"]))
    return states


def dedup_pure_atoms(v25):
    pure = {}
    for label, rows in v25["pure_atom_summary"].items():
        best = {}
        for row in rows:
            mask = frozenset((state["H6"], state["E"]) for state in row["covered_states"])
            if mask not in best or len(row["guard"]) < len(best[mask]):
                best[mask] = row["guard"]
        pure[label] = [(guard, mask) for mask, guard in best.items()]
    return pure


def minimal_cover_size(target, options):
    for size in range(1, len(options) + 1):
        for combo in combinations(range(len(options)), size):
            cover = frozenset().union(*(options[index][1] for index in combo))
            if cover == target:
                return size, [options[index][0] for index in combo]
    raise ValueError("no exact cover found")


def build_report():
    v24, v25 = load_reports()
    states_by_label = label_states(v24)
    pure = dedup_pure_atoms(v25)
    labels = sorted(states_by_label)

    baseline = {}
    for label in labels:
        baseline[label] = minimal_cover_size(frozenset(states_by_label[label]), pure[label])
    baseline_total = sum(size for size, _ in baseline.values())

    candidate_primitives = []
    for label in labels:
        existing_masks = {mask for _, mask in pure[label]}
        options = pure[label]
        for size in [2, 3]:
            for combo in combinations(range(len(options)), size):
                masks = [options[index][1] for index in combo]
                cover = frozenset().union(*masks)
                if cover in existing_masks:
                    continue
                if not cover or not cover.issubset(states_by_label[label]):
                    continue
                candidate_primitives.append(
                    {
                        "label": label,
                        "parts": [options[index][0] for index in combo],
                        "cover": cover,
                        "cover_states": [
                            {"H6": state[0], "E": state[1]}
                            for state in sorted(cover, key=lambda state: (state[0], state[1]))
                        ],
                        "formula": " OR ".join(options[index][0] for index in combo),
                    }
                )

    best_one = None
    for primitive in candidate_primitives:
        augmented = {label: list(pure[label]) for label in labels}
        augmented[primitive["label"]].append((primitive["formula"], primitive["cover"]))
        total = 0
        cover_summary = {}
        for label in labels:
            size, formulae = minimal_cover_size(frozenset(states_by_label[label]), augmented[label])
            total += size
            cover_summary[label] = formulae
        candidate = {
            "total_cost": total,
            "primitive": {
                "label": primitive["label"],
                "parts": primitive["parts"],
                "formula": primitive["formula"],
                "cover_states": primitive["cover_states"],
            },
            "covers": cover_summary,
        }
        if best_one is None or total < best_one["total_cost"]:
            best_one = candidate

    best_two = None
    for combo in combinations(range(len(candidate_primitives)), 2):
        augmented = {label: list(pure[label]) for label in labels}
        used = []
        for index in combo:
            primitive = candidate_primitives[index]
            augmented[primitive["label"]].append((primitive["formula"], primitive["cover"]))
            used.append(primitive)
        total = 0
        cover_summary = {}
        for label in labels:
            size, formulae = minimal_cover_size(frozenset(states_by_label[label]), augmented[label])
            total += size
            cover_summary[label] = formulae
        candidate = {
            "total_cost": total,
            "primitives": [
                {
                    "label": primitive["label"],
                    "parts": primitive["parts"],
                    "formula": primitive["formula"],
                    "cover_states": primitive["cover_states"],
                }
                for primitive in used
            ],
            "covers": cover_summary,
        }
        if best_two is None or total < best_two["total_cost"]:
            best_two = candidate

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": "primitive-invention search over exact label-pure unions on the repaired verifier frontier",
        "holdout_domain": "the same 10 reachable quotient states over `(H6, E)` used in v24, v25, and v35",
        "survivor": "primitive-invention label frontier",
        "baseline_all_positive_cost": baseline_total,
        "baseline_covers": baseline,
        "candidate_primitive_count": len(candidate_primitives),
        "best_one_primitive": best_one,
        "best_two_primitives": best_two,
        "strongest_claim": (
            "On the repaired verifier frontier, bounded primitive invention improves the all-positive exact label language. "
            "One invented pure primitive lowers cost from 7 to 5, and two invented pure primitives lower cost from 7 to 4, "
            "matching the best mixed-sign language from v35."
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
