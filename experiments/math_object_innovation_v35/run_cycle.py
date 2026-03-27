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


def minimal_positive_cover(label, label_states, pure_summary):
    options = []
    for row in pure_summary[label]:
        mask = frozenset((state["H6"], state["E"]) for state in row["covered_states"])
        options.append((row["guard"], mask))

    target = label_states[label]
    for size in range(1, len(options) + 1):
        for combo in combinations(range(len(options)), size):
            cover = frozenset().union(*(options[index][1] for index in combo))
            if cover == target:
                return [options[index][0] for index in combo]
    raise ValueError(f"no exact positive cover for label {label}")


def build_report():
    v24, v25 = load_reports()
    labels = sorted(v25["pure_atom_summary"])
    label_states = {label: set() for label in labels}
    for row in v24["state_rows"]:
        label_states[row["label"]].add((row["H6"], row["E"]))

    positive_covers = {}
    for label in labels:
        positive_covers[label] = minimal_positive_cover(label, label_states, v25["pure_atom_summary"])

    all_positive_cost = sum(len(positive_covers[label]) for label in labels)

    best_default = None
    best_cost = None
    for default_label in labels:
        cost = sum(len(positive_covers[label]) for label in labels if label != default_label)
        if best_cost is None or cost < best_cost or (cost == best_cost and default_label < best_default):
            best_cost = cost
            best_default = default_label

    mixed_language = {
        label: positive_covers[label]
        for label in labels
        if label != best_default
    }

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": "mixed-sign certificate-language search on the repaired verifier frontier",
        "holdout_domain": "the same 10 reachable quotient states over `(H6, E)` used in v24 and v25",
        "survivor": "mixed-sign label language frontier",
        "label_count": len(labels),
        "state_count": len(v24["state_rows"]),
        "positive_covers": positive_covers,
        "all_positive_cost": all_positive_cost,
        "best_default_label": best_default,
        "best_mixed_cost": best_cost,
        "best_mixed_language": mixed_language,
        "strongest_claim": (
            "On the repaired verifier frontier, the smallest exact all-positive certificate language uses 7 pure guards, "
            "but the smallest exact mixed-sign language uses only 4 by certifying `safe`, `fail_13116`, and `fail_1915` positively "
            "and leaving `fail_828` as the default residual class."
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

