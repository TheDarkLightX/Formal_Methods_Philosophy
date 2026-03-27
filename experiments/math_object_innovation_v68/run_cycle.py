#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
V67 = ROOT.parent / "math_object_innovation_v67" / "generated" / "report.json"
OUT_DIR = ROOT / "generated"
OUT_PATH = OUT_DIR / "report.json"


def edge_count(rep):
    return {
        (0, 1, 2, 3): 4,
        (0, 1, 2, 4): 3,
        (0, 1, 2, 5): 3,
        (0, 1, 2, 7): 2,
        (0, 1, 6, 7): 2,
        (0, 3, 5, 6): 0,
    }[rep]


def degree_sequence(rep):
    return {
        (0, 1, 2, 3): (2, 2, 2, 2),
        (0, 1, 2, 4): (3, 1, 1, 1),
        (0, 1, 2, 5): (2, 2, 1, 1),
        (0, 1, 2, 7): (2, 1, 1, 0),
        (0, 1, 6, 7): (1, 1, 1, 1),
        (0, 3, 5, 6): (0, 0, 0, 0),
    }[rep]


def component_sizes(rep):
    return {
        (0, 1, 2, 3): (4,),
        (0, 1, 2, 4): (4,),
        (0, 1, 2, 5): (4,),
        (0, 1, 2, 7): (3, 1),
        (0, 1, 6, 7): (2, 2),
        (0, 3, 5, 6): (1, 1, 1, 1),
    }[rep]


def rows():
    report = json.loads(V67.read_text(encoding="utf-8"))
    out = []
    for entry in report["orbit_atlas"]:
        rep = tuple(entry["representative"])
        deg = degree_sequence(rep)
        out.append(
            {
                "representative": rep,
                "cost": entry["uniform_cost"],
                "edge_count": edge_count(rep),
                "max_degree": max(deg),
                "leaf_count": sum(d == 1 for d in deg),
                "isolated_count": sum(d == 0 for d in deg),
                "degree_sequence": deg,
                "component_sizes": component_sizes(rep),
                "connected": len(component_sizes(rep)) == 1,
            }
        )
    return out


def exact_on(rows, features):
    seen = {}
    for row in rows:
        key = tuple(row[feature] for feature in features)
        if key in seen and seen[key] != row["cost"]:
            return False
        seen[key] = row["cost"]
    return True


def build_exact_map(rows, features):
    mapping = {}
    for row in rows:
        key = tuple(row[feature] for feature in features)
        mapping[key] = row["cost"]
    return [
        {
            "features": list(key),
            "cost": cost,
        }
        for key, cost in sorted(mapping.items())
    ]


def main():
    data = rows()
    feature_names = [
        "edge_count",
        "max_degree",
        "leaf_count",
        "isolated_count",
        "connected",
        "component_sizes",
        "degree_sequence",
    ]
    singleton_exact = [name for name in feature_names if exact_on(data, [name])]
    pair_exact = [
        (a, b)
        for i, a in enumerate(feature_names)
        for b in feature_names[i + 1 :]
        if exact_on(data, [a, b])
    ]
    chosen = ("edge_count", "max_degree")
    report = {
        "survivor": "width3 invariant law frontier",
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "minimal exact invariant basis for the width-3 four-role orbit-cost "
            "atlas from v67, within the searched graph-invariant library"
        ),
        "holdout_domain": "the exact six-orbit width-3 atlas from v67",
        "row_count": len(data),
        "singleton_exact": singleton_exact,
        "pair_exact": [list(item) for item in pair_exact],
        "chosen_pair": list(chosen),
        "chosen_pair_map": build_exact_map(data, chosen),
        "strongest_claim": (
            "On the exact v67 orbit atlas, no searched singleton scalar invariant "
            "is exact, but the pair (edge_count, max_degree) predicts the orbit "
            "cost exactly: (3,3)->3, (3,2)->4, (2,2)->5, and all other pairs "
            "map to cost 6."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
