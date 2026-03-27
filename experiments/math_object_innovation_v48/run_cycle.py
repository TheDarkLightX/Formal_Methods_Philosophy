#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
OUT = ROOT / "generated" / "report.json"

V41 = REPO_ROOT / "experiments" / "math_object_innovation_v41" / "generated" / "report.json"
V46 = REPO_ROOT / "experiments" / "math_object_innovation_v46" / "generated" / "report.json"


def split_top_level(formula: str):
    return formula.split(" and ")


def literal_parts(literal: str):
    if literal.startswith("not "):
        return False, literal[4:]
    return True, literal


def feature_kind(feature: str):
    if " AND " in feature:
        return ("AND", feature.count(" AND ") + 1)
    if " OR " in feature:
        return ("OR", feature.count(" OR ") + 1)
    return ("ATOM", 1)


def canonical_template(formula: str, *, typed: bool):
    mapping = {}
    out = []
    for literal in split_top_level(formula):
        positive, feature = literal_parts(literal)
        if feature not in mapping:
            if typed:
                kind, arity = feature_kind(feature)
                mapping[feature] = f"{kind}{arity}_{len(mapping) + 1}"
            else:
                mapping[feature] = f"F{len(mapping) + 1}"
        token = mapping[feature]
        out.append(token if positive else f"not {token}")
    return " and ".join(out)


def template_buckets(formulas, *, typed: bool):
    buckets = defaultdict(list)
    for formula in formulas:
        buckets[canonical_template(formula, typed=typed)].append(formula)
    return {
        template: sorted(bucket)
        for template, bucket in sorted(
            buckets.items(), key=lambda item: (-len(item[1]), item[0])
        )
    }


def build_report():
    v41 = json.loads(V41.read_text(encoding="utf-8"))
    v46 = json.loads(V46.read_text(encoding="utf-8"))

    schemas_41 = set(v41["best_shared_schemas"])
    schemas_46 = set(v46["best_shared_schemas"])
    union = schemas_41 | schemas_46
    overlap = schemas_41 & schemas_46

    untyped = template_buckets(union, typed=False)
    typed = template_buckets(union, typed=True)

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "cross-frontier witness-template mining over the exact shared schema "
            "libraries from v41 and v46"
        ),
        "holdout_domain": "the bounded hard-frontier witness-schema libraries from v41 and v46",
        "survivor": "cross-frontier witness-template frontier",
        "source_frontiers": {
            "v41_schema_count": len(schemas_41),
            "v46_schema_count": len(schemas_46),
            "shared_schema_count": len(overlap),
            "union_schema_count": len(union),
        },
        "v41_only": sorted(schemas_41 - schemas_46),
        "v46_only": sorted(schemas_46 - schemas_41),
        "untyped_template_count": len(untyped),
        "typed_template_count": len(typed),
        "largest_untyped_buckets": [
            {"template": template, "count": len(bucket), "schemas": bucket}
            for template, bucket in list(untyped.items())[:10]
        ],
        "largest_typed_buckets": [
            {"template": template, "count": len(bucket), "schemas": bucket}
            for template, bucket in list(typed.items())[:10]
        ],
        "strongest_claim": (
            "The two exact global witness-schema frontiers from v41 and v46 contain "
            "22 unique formulas in union, but those formulas collapse to 10 untyped "
            "conjunction-shape templates, or 13 typed templates when feature kind is retained."
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
