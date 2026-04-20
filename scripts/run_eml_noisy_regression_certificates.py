#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "assets" / "data" / "eml_noisy_regression_certificates.json"

sys.path.insert(0, str(ROOT / "scripts"))
from run_eml_neurosymbolic_loop_demo import (  # noqa: E402
    Tree,
    enumerate_trees,
    lean_certificate,
    symbolic_identity_check,
    values_on_grid_with_reason,
)


def exp_exp(x: float) -> float:
    return math.exp(math.exp(x))


NOISY_TARGETS: tuple[dict[str, Any], ...] = (
    {
        "name": "noisy_exp",
        "clean_target": "exp(x)",
        "train_xs": (0.5, 1.0, 2.0),
        "holdout_xs": (0.25, 0.75, 1.5, 3.0),
        "noise": (0.02, -0.015, 0.01),
        "fn": math.exp,
    },
    {
        "name": "noisy_log",
        "clean_target": "ln(x)",
        "train_xs": (0.5, 1.0, 2.0),
        "holdout_xs": (0.25, 0.75, 1.5, 3.0),
        "noise": (-0.01, 0.02, -0.015),
        "fn": math.log,
    },
    {
        "name": "noisy_exp_exp",
        "clean_target": "exp(exp(x))",
        "train_xs": (0.1, 0.2, 0.3),
        "holdout_xs": (0.15, 0.25, 0.35),
        "noise": (0.01, -0.008, 0.012),
        "fn": exp_exp,
    },
)


def clean_values(target: dict[str, Any], xs: tuple[float, ...]) -> tuple[float, ...]:
    return tuple(float(target["fn"](x)) for x in xs)


def mse(values: tuple[float, ...], expected: tuple[float, ...]) -> float:
    return sum((a - b) * (a - b) for a, b in zip(values, expected, strict=True)) / len(values)


def residuals(values: tuple[float, ...], expected: tuple[float, ...]) -> list[float]:
    return [a - b for a, b in zip(values, expected, strict=True)]


def evaluate_candidate(
    tree: Tree,
    train_xs: tuple[float, ...],
    train_y_noisy: tuple[float, ...],
    train_y_clean: tuple[float, ...],
    holdout_xs: tuple[float, ...],
    holdout_y: tuple[float, ...],
) -> dict[str, Any] | None:
    train_values, train_reason = values_on_grid_with_reason(tree, train_xs)
    if train_values is None:
        return None
    holdout_values, holdout_reason = values_on_grid_with_reason(tree, holdout_xs)
    if holdout_values is None:
        return None
    return {
        "expr": tree.pretty(),
        "depth": tree.depth(),
        "size": tree.size(),
        "train_mse_noisy": mse(train_values, train_y_noisy),
        "train_mse_clean": mse(train_values, train_y_clean),
        "holdout_mse_clean": mse(holdout_values, holdout_y),
        "train_residual_noisy": residuals(train_values, train_y_noisy),
        "train_residual_clean": residuals(train_values, train_y_clean),
        "holdout_residual_clean": residuals(holdout_values, holdout_y),
        "domain_reason": train_reason or holdout_reason,
    }


def target_sympy(clean_target: str):
    try:
        import sympy as sp
    except ImportError:
        return None
    if clean_target == "exp(x)":
        return lambda x: sp.exp(x)
    if clean_target == "ln(x)":
        return lambda x: sp.log(x)
    if clean_target == "exp(exp(x))":
        return lambda x: sp.exp(sp.exp(x))
    return None


def solve_target(target: dict[str, Any], trees: list[Tree]) -> dict[str, Any]:
    train_xs = tuple(target["train_xs"])
    holdout_xs = tuple(target["holdout_xs"])
    noise = tuple(target["noise"])
    train_y_clean = clean_values(target, train_xs)
    train_y_noisy = tuple(y + n for y, n in zip(train_y_clean, noise, strict=True))
    holdout_y = clean_values(target, holdout_xs)

    rows: list[dict[str, Any]] = []
    for tree in trees:
        row = evaluate_candidate(
            tree, train_xs, train_y_noisy, train_y_clean, holdout_xs, holdout_y
        )
        if row is not None:
            rows.append(row)
    rows_sorted = sorted(
        rows,
        key=lambda row: (
            row["train_mse_noisy"],
            row["holdout_mse_clean"],
            row["size"],
            row["depth"],
            row["expr"],
        ),
    )
    winner = rows_sorted[0]
    tree_by_expr = {tree.pretty(): tree for tree in trees}
    proof_receipt = lean_certificate(winner["expr"], target["clean_target"])
    symbolic_receipt = symbolic_identity_check(
        tree_by_expr[winner["expr"]],
        target_sympy(target["clean_target"]),
    )
    return {
        "name": target["name"],
        "clean_target": target["clean_target"],
        "train_xs": list(train_xs),
        "holdout_xs": list(holdout_xs),
        "noise": list(noise),
        "train_y_clean": list(train_y_clean),
        "train_y_noisy": list(train_y_noisy),
        "holdout_y_clean": list(holdout_y),
        "domain_valid_count": len(rows),
        "winner": winner,
        "top_candidates": rows_sorted[:8],
        "residual_certificate": {
            "ordering": (
                "train_mse_noisy, holdout_mse_clean, size, depth, expression"
            ),
            "winner_rank": 0,
            "exhaustive_bounded_candidate_count": len(rows),
            "winner_train_residual_noisy": winner["train_residual_noisy"],
            "winner_holdout_residual_clean": winner["holdout_residual_clean"],
            "winner_train_mse_noisy": winner["train_mse_noisy"],
            "winner_holdout_mse_clean": winner["holdout_mse_clean"],
        },
        "proof_receipt": proof_receipt,
        "symbolic_identity": symbolic_receipt,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Noisy bounded EML regression certificates.")
    parser.add_argument("--max-depth", type=int, default=3)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    trees = enumerate_trees(args.max_depth)
    results = [solve_target(target, trees) for target in NOISY_TARGETS]
    artifact = {
        "schema": "eml_noisy_regression_certificates_v1",
        "generator": "scripts/run_eml_noisy_regression_certificates.py",
        "scope": {
            "claim": (
                "Within the bounded EML corpus, noisy regression can return "
                "an empirical minimizer with explicit residual certificates "
                "and proof metadata for the selected survivor."
            ),
            "not_claimed": [
                "not full symbolic regression",
                "not statistical consistency",
                "not global optimality beyond the bounded corpus",
                "not native Tau analytic semantics",
            ],
        },
        "parameters": {
            "max_depth": args.max_depth,
            "corpus_size": len(trees),
            "selection_order": "train_mse_noisy, holdout_mse_clean, size, depth, expression",
        },
        "summary": {
            "ok": all(result["winner"] for result in results),
            "target_count": len(results),
            "winner_count": len(results),
            "proof_receipt_accept_count": sum(
                1 for result in results if result["proof_receipt"].get("accepted") is True
            ),
            "symbolic_identity_accept_count": sum(
                1
                for result in results
                if result["symbolic_identity"].get("proved_by_simplify") is True
            ),
            "zero_holdout_mse_count": sum(
                1 for result in results if result["winner"]["holdout_mse_clean"] == 0.0
            ),
        },
        "results": results,
    }
    out = args.out if args.out.is_absolute() else ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "ok": artifact["summary"]["ok"],
                "out": str(out.relative_to(ROOT)),
                "corpus_size": len(trees),
            },
            indent=2,
        )
    )
    return 0 if artifact["summary"]["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
