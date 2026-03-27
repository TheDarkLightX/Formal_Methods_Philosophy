#!/usr/bin/env python3
from __future__ import annotations

import json
from itertools import product
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
OUT = ROOT / "generated" / "report.json"
V49 = REPO_ROOT / "experiments" / "math_object_innovation_v49" / "generated" / "report.json"


def split_formula(formula: str):
    return tuple(sorted(formula.split(" and ")))


def parse_literal(literal: str):
    negative = literal.startswith("not ")
    feature = literal[4:] if negative else literal
    if " AND " in feature:
        kind = f"AND{feature.count(' AND ') + 1}"
    elif " OR " in feature:
        kind = f"OR{feature.count(' OR ') + 1}"
    else:
        kind = "ATOM"
    return negative, kind, feature


def edit_signature(core_formula, patch_formula):
    removed = sorted(set(core_formula) - set(patch_formula))
    added = sorted(set(patch_formula) - set(core_formula))
    ops = []
    for literal in removed:
        negative, kind, _ = parse_literal(literal)
        ops.append(f"DROP_{'NEG' if negative else 'POS'}_{kind}")
    for literal in added:
        negative, kind, _ = parse_literal(literal)
        ops.append(f"ADD_{'NEG' if negative else 'POS'}_{kind}")
    return tuple(sorted(ops)), len(removed) + len(added)


def build_report():
    data = json.loads(V49.read_text(encoding="utf-8"))
    core_formulas = [split_formula(formula) for formula in data["core_schemas"]]
    patch_names = data["v41_only_schemas"] + data["v46_only_schemas"]
    patch_formulas = [split_formula(formula) for formula in patch_names]

    nearest_choices = []
    for patch_formula in patch_formulas:
        best_cost = None
        options = []
        for core_formula in core_formulas:
            signature, cost = edit_signature(core_formula, patch_formula)
            if best_cost is None or cost < best_cost:
                best_cost = cost
                options = []
            if cost == best_cost:
                options.append((core_formula, signature, cost))
        nearest_choices.append(options)

    nearest_vocab = {
        signature
        for options in nearest_choices
        for _, signature, _ in options[:1]
    }

    all_choices = []
    for patch_formula in patch_formulas:
        patch_choices = []
        for core_formula in core_formulas:
            signature, cost = edit_signature(core_formula, patch_formula)
            patch_choices.append((core_formula, signature, cost))
        all_choices.append(patch_choices)

    best = None
    best_assignment = None
    search_count = 0
    for combo in product(*all_choices):
        search_count += 1
        vocab = {signature for _, signature, _ in combo}
        score = (
            len(vocab),
            sum(cost for _, _, cost in combo),
            sum(len(signature) for signature in vocab),
            sorted(vocab),
        )
        if best is None or score < best:
            best = score
            best_assignment = combo

    best_vocab_size, best_total_cost, _, best_vocab = best

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "typed edit-signature search over the shared exact core from v49, "
            "allowing each residual patch to attach to any core formula"
        ),
        "holdout_domain": "the five residual patch formulas from the v49 core-plus-patch frontier",
        "survivor": "typed semantic-patch frontier",
        "shared_core_size": len(core_formulas),
        "patch_count": len(patch_formulas),
        "search_count": search_count,
        "nearest_core_signature_count": len(
            {
                signature
                for options in nearest_choices
                for _, signature, _ in options[:1]
            }
        ),
        "best_signature_vocab_size": best_vocab_size,
        "best_total_edit_cost": best_total_cost,
        "best_signature_vocab": [list(signature) for signature in best_vocab],
        "best_patch_assignments": [
            {
                "patch": patch_name,
                "core": " and ".join(core_formula),
                "edit_cost": cost,
                "signature": list(signature),
            }
            for patch_name, (core_formula, signature, cost) in zip(patch_names, best_assignment)
        ],
        "strongest_claim": (
            "In the searched typed edit model over the shared v49 core, the five "
            "frontier-specific patch formulas collapse from five nearest-core edit "
            "signatures to four typed edit signatures once non-nearest core "
            "attachments are allowed."
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
