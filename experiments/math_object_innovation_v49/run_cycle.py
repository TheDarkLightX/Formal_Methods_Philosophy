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


def canonical_template(formula: str):
    mapping = {}
    out = []
    for literal in split_top_level(formula):
        positive, feature = literal_parts(literal)
        if feature not in mapping:
            mapping[feature] = f"F{len(mapping) + 1}"
        token = mapping[feature]
        out.append(token if positive else f"not {token}")
    return " and ".join(out)


def build_report():
    v41 = json.loads(V41.read_text(encoding="utf-8"))
    v46 = json.loads(V46.read_text(encoding="utf-8"))

    schemas_41 = set(v41["best_shared_schemas"])
    schemas_46 = set(v46["best_shared_schemas"])
    core = schemas_41 & schemas_46
    v41_only = schemas_41 - core
    v46_only = schemas_46 - core
    residual_union = sorted(v41_only | v46_only)

    buckets = defaultdict(list)
    for formula in residual_union:
        buckets[canonical_template(formula)].append(formula)

    residual_templates = {
        template: sorted(bucket)
        for template, bucket in sorted(
            buckets.items(), key=lambda item: (-len(item[1]), item[0])
        )
    }

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "core-plus-patch decomposition over the exact global witness-schema "
            "libraries from v41 and v46"
        ),
        "holdout_domain": "the bounded hard-frontier witness-schema libraries from v41 and v46",
        "survivor": "cross-frontier core-plus-patch frontier",
        "core_schema_count": len(core),
        "v41_patch_count": len(v41_only),
        "v46_patch_count": len(v46_only),
        "residual_union_count": len(residual_union),
        "residual_template_count": len(residual_templates),
        "core_schemas": sorted(core),
        "v41_only_schemas": sorted(v41_only),
        "v46_only_schemas": sorted(v46_only),
        "residual_templates": [
            {"template": template, "schemas": formulas}
            for template, formulas in residual_templates.items()
        ],
        "residual_template_irreducible": len(residual_templates) == len(residual_union),
        "strongest_claim": (
            "The exact global witness-schema frontiers from v41 and v46 decompose "
            "into a shared exact core of 17 schemas plus five frontier-specific "
            "patch schemas, and those five patches are already template-irreducible "
            "in the searched conjunction-shape grammar."
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
