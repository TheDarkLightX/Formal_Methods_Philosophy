#!/usr/bin/env python3
from __future__ import annotations

import json
from itertools import product
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
OUT = ROOT / "generated" / "report.json"
V49 = REPO_ROOT / "experiments" / "math_object_innovation_v49" / "generated" / "report.json"


def parse_formula(formula: str):
    literals = {}
    for literal in formula.split(" and "):
        negative = literal.startswith("not ")
        feature = literal[4:] if negative else literal
        literals[feature] = not negative
    return literals


def feature_kind(feature: str):
    if " AND " in feature:
        return f"AND{feature.count(' AND ') + 1}"
    if " OR " in feature:
        return f"OR{feature.count(' OR ') + 1}"
    return "ATOM"


def semantic_script(core_formula: str, patch_formula: str):
    core = parse_formula(core_formula)
    patch = parse_formula(patch_formula)
    ops = []
    families = set()

    for feature in sorted(set(core) | set(patch)):
        in_core = feature in core
        in_patch = feature in patch
        if in_core and in_patch:
            if core[feature] == patch[feature]:
                continue
            ops.append(
                {
                    "family": "FLIP_SIGN",
                    "kind": feature_kind(feature),
                    "feature": feature,
                    "from_sign": "POS" if core[feature] else "NEG",
                    "to_sign": "POS" if patch[feature] else "NEG",
                }
            )
            families.add("FLIP_SIGN")
        elif in_patch:
            ops.append(
                {
                    "family": "ADD_LITERAL",
                    "kind": feature_kind(feature),
                    "feature": feature,
                    "sign": "POS" if patch[feature] else "NEG",
                }
            )
            families.add("ADD_LITERAL")
        else:
            ops.append(
                {
                    "family": "DROP_LITERAL",
                    "kind": feature_kind(feature),
                    "feature": feature,
                    "sign": "POS" if core[feature] else "NEG",
                }
            )
            families.add("DROP_LITERAL")

    return tuple(sorted(families)), ops


def build_report():
    data = json.loads(V49.read_text(encoding="utf-8"))
    core_formulas = data["core_schemas"]
    patch_formulas = data["v41_only_schemas"] + data["v46_only_schemas"]

    best = None
    best_assignment = None
    search_count = 0

    all_choices = []
    for patch_formula in patch_formulas:
        patch_choices = []
        for core_formula in core_formulas:
            families, ops = semantic_script(core_formula, patch_formula)
            patch_choices.append((core_formula, families, ops))
        all_choices.append(patch_choices)

    for combo in product(*all_choices):
        search_count += 1
        family_set = set()
        total_ops = 0
        for _, families, ops in combo:
            family_set.update(families)
            total_ops += len(ops)
        score = (len(family_set), total_ops, tuple(sorted(family_set)))
        if best is None or score < best:
            best = score
            best_assignment = combo

    family_count, total_ops, family_subset = best

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "semantic macro-family search over the shared exact core from v49, "
            "using ADD_LITERAL, DROP_LITERAL, and FLIP_SIGN as candidate families"
        ),
        "holdout_domain": "the five residual patch formulas from the v49 core-plus-patch frontier",
        "survivor": "semantic macro-family frontier",
        "shared_core_size": len(core_formulas),
        "patch_count": len(patch_formulas),
        "search_count": search_count,
        "best_family_count": family_count,
        "best_family_subset": list(family_subset),
        "best_total_ops": total_ops,
        "best_patch_assignments": [
            {
                "patch": patch_formula,
                "core": core_formula,
                "families": list(families),
                "ops": ops,
            }
            for patch_formula, (core_formula, families, ops) in zip(patch_formulas, best_assignment)
        ],
        "strongest_claim": (
            "Over the v49 shared exact core, the five residual patch formulas are "
            "exactly scriptable using only two semantic macro families, ADD_LITERAL "
            "and FLIP_SIGN, and no exact one-family solution exists in the searched model."
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
