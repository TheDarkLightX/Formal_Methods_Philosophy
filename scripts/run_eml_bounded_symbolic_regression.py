#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "assets" / "data" / "eml_bounded_symbolic_regression.json"

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


TARGETS: tuple[dict[str, Any], ...] = (
    {
        "name": "identity",
        "display": "x",
        "train_xs": (0.5, 1.0, 2.0),
        "holdout_xs": (0.25, 0.75, 1.5, 3.0),
        "fn": lambda x: x,
    },
    {
        "name": "exp",
        "display": "exp(x)",
        "train_xs": (0.5, 1.0, 2.0),
        "holdout_xs": (0.25, 0.75, 1.5, 3.0),
        "fn": math.exp,
    },
    {
        "name": "log",
        "display": "ln(x)",
        "train_xs": (0.5, 1.0, 2.0),
        "holdout_xs": (0.25, 0.75, 1.5, 3.0),
        "fn": math.log,
    },
    {
        "name": "exp_exp",
        "display": "exp(exp(x))",
        "train_xs": (0.1, 0.2, 0.3),
        "holdout_xs": (0.15, 0.25, 0.35),
        "fn": exp_exp,
    },
)


def target_values(target: dict[str, Any], xs: tuple[float, ...]) -> tuple[float, ...]:
    return tuple(float(target["fn"](x)) for x in xs)


def max_abs_error(values: tuple[float, ...], expected: tuple[float, ...]) -> float:
    return max(abs(a - b) for a, b in zip(values, expected, strict=True))


def evaluate_fit(
    tree: Tree,
    train_xs: tuple[float, ...],
    train_y: tuple[float, ...],
    holdout_xs: tuple[float, ...],
    holdout_y: tuple[float, ...],
) -> dict[str, Any]:
    train_values, train_reason = values_on_grid_with_reason(tree, train_xs)
    if train_values is None:
        return {
            "domain_ok": False,
            "train_error": None,
            "holdout_error": None,
            "reason": train_reason,
        }
    holdout_values, holdout_reason = values_on_grid_with_reason(tree, holdout_xs)
    if holdout_values is None:
        return {
            "domain_ok": False,
            "train_error": max_abs_error(train_values, train_y),
            "holdout_error": None,
            "reason": holdout_reason,
        }
    return {
        "domain_ok": True,
        "train_error": max_abs_error(train_values, train_y),
        "holdout_error": max_abs_error(holdout_values, holdout_y),
        "train_values": train_values,
        "holdout_values": holdout_values,
        "reason": None,
    }


def fit_target(
    target: dict[str, Any],
    trees: list[Tree],
    tolerance: float,
) -> dict[str, Any]:
    train_xs = tuple(target["train_xs"])
    holdout_xs = tuple(target["holdout_xs"])
    train_y = target_values(target, train_xs)
    holdout_y = target_values(target, holdout_xs)
    rows: list[dict[str, Any]] = []
    domain_valid = 0
    for tree in trees:
        fit = evaluate_fit(tree, train_xs, train_y, holdout_xs, holdout_y)
        if fit["domain_ok"]:
            domain_valid += 1
        train_error = fit["train_error"]
        holdout_error = fit["holdout_error"]
        train_ok = train_error is not None and train_error <= tolerance
        holdout_ok = holdout_error is not None and holdout_error <= tolerance
        rows.append(
            {
                "expr": tree.pretty(),
                "depth": tree.depth(),
                "size": tree.size(),
                "domain_ok": fit["domain_ok"],
                "train_error": train_error,
                "holdout_error": holdout_error,
                "train_ok": train_ok,
                "holdout_ok": holdout_ok,
                "fit_ok": train_ok and holdout_ok,
                "domain_reason": fit["reason"],
            }
        )
    fitting = [row for row in rows if row["fit_ok"]]
    fitting_sorted = sorted(fitting, key=lambda row: (row["size"], row["depth"], row["expr"]))
    best = fitting_sorted[0] if fitting_sorted else None
    smaller_fit_count = 0
    if best is not None:
        smaller_fit_count = sum(
            1
            for row in fitting
            if (row["size"], row["depth"], row["expr"])
            < (best["size"], best["depth"], best["expr"])
        )
    proof_receipt = {"accepted": False}
    symbolic_receipt = {"available": False, "reason": "no survivor"}
    if best is not None:
        proof_receipt = lean_certificate(str(best["expr"]), str(target["display"]))
        tree = next(tree for tree in trees if tree.pretty() == best["expr"])
        target_sympy = None
        try:
            import sympy as sp

            if target["display"] == "x":
                target_sympy = lambda x: x
            elif target["display"] == "exp(x)":
                target_sympy = lambda x: sp.exp(x)
            elif target["display"] == "ln(x)":
                target_sympy = lambda x: sp.log(x)
            elif target["display"] == "exp(exp(x))":
                target_sympy = lambda x: sp.exp(sp.exp(x))
        except ImportError:
            target_sympy = None
        symbolic_receipt = symbolic_identity_check(tree, target_sympy)
    return {
        "target": target["display"],
        "train_xs": list(train_xs),
        "holdout_xs": list(holdout_xs),
        "train_y": list(train_y),
        "holdout_y": list(holdout_y),
        "domain_valid_count": domain_valid,
        "fit_count": len(fitting),
        "best_fit": best,
        "top_fits": fitting_sorted[:8],
        "minimality_certificate": {
            "bounded_corpus_order": "size, then depth, then expression string",
            "smaller_fit_count": smaller_fit_count,
            "minimal_within_bounded_corpus": best is not None and smaller_fit_count == 0,
        },
        "proof_receipt": proof_receipt,
        "symbolic_identity": symbolic_receipt,
        "not_claimed": [
            "not complete symbolic regression over all formulas",
            "not proof that no deeper EML tree fits",
            "not a native Tau analytic backend",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Bounded EML symbolic regression demo.")
    parser.add_argument("--max-depth", type=int, default=3)
    parser.add_argument("--tolerance", type=float, default=1.0e-9)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    trees = enumerate_trees(args.max_depth)
    results = [fit_target(target, trees, args.tolerance) for target in TARGETS]
    artifact = {
        "schema": "eml_bounded_symbolic_regression_v1",
        "generator": "scripts/run_eml_bounded_symbolic_regression.py",
        "scope": {
            "claim": (
                "Within the bounded EML corpus, enumerative regression can "
                "return minimal train-and-holdout fits with explicit "
                "certificate metadata."
            ),
            "not_claimed": [
                "not full symbolic regression",
                "not learned gradient search",
                "not native Tau analytic semantics",
                "not a global proof over all EML trees",
            ],
        },
        "parameters": {
            "max_depth": args.max_depth,
            "tolerance": args.tolerance,
            "corpus_size": len(trees),
        },
        "summary": {
            "ok": all(result["best_fit"] is not None for result in results),
            "target_count": len(results),
            "all_targets_fit": all(result["fit_count"] > 0 for result in results),
            "all_best_minimal": all(
                result["minimality_certificate"]["minimal_within_bounded_corpus"]
                for result in results
            ),
            "proof_receipt_accept_count": sum(
                1 for result in results if result["proof_receipt"].get("accepted") is True
            ),
            "symbolic_identity_accept_count": sum(
                1
                for result in results
                if result["symbolic_identity"].get("proved_by_simplify") is True
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
