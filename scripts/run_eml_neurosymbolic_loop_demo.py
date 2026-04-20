#!/usr/bin/env python3
"""Small EML-tree neuro-symbolic loop demo.

This is a teaching experiment inspired by Andrzej Odrzywolek's 2026 EML paper.
It does not reimplement the paper's gradient training. It uses EML trees as a
finite symbolic hypothesis language, scores them numerically, filters them by
domain/spec checks, and renormalizes the surviving candidates.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

try:
    import sympy as sp
except ImportError:  # pragma: no cover - optional teaching dependency
    sp = None


ROOT = Path(__file__).resolve().parents[1]
MAX_ABS = 1.0e80


def repo_path(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


@dataclass(frozen=True)
class Tree:
    kind: str
    left: "Tree | None" = None
    right: "Tree | None" = None

    def depth(self) -> int:
        if self.kind in {"x", "one"}:
            return 0
        assert self.left is not None and self.right is not None
        return 1 + max(self.left.depth(), self.right.depth())

    def size(self) -> int:
        if self.kind in {"x", "one"}:
            return 1
        assert self.left is not None and self.right is not None
        return 1 + self.left.size() + self.right.size()

    def pretty(self) -> str:
        if self.kind == "x":
            return "x"
        if self.kind == "one":
            return "1"
        assert self.left is not None and self.right is not None
        return f"eml({self.left.pretty()},{self.right.pretty()})"

    def eval(self, x: float) -> float:
        if self.kind == "x":
            return x
        if self.kind == "one":
            return 1.0
        assert self.left is not None and self.right is not None
        a = self.left.eval(x)
        b = self.right.eval(x)
        if not math.isfinite(a) or not math.isfinite(b):
            raise ValueError("non-finite child")
        if b <= 0.0:
            raise ValueError("real log domain failure")
        if abs(a) > 180.0:
            raise ValueError("exp guard failure")
        out = math.exp(a) - math.log(b)
        if not math.isfinite(out) or abs(out) > MAX_ABS:
            raise ValueError("non-finite output")
        return out


class ParseError(ValueError):
    """Raised when an external EML proposal is not in the demo grammar."""


@dataclass(frozen=True)
class Interval:
    lo: float
    hi: float


class TreeParser:
    def __init__(self, text: str) -> None:
        self.text = text
        self.i = 0

    def parse(self) -> Tree:
        tree = self.parse_tree()
        self.skip_ws()
        if self.i != len(self.text):
            raise ParseError(f"unexpected trailing text at offset {self.i}")
        return tree

    def skip_ws(self) -> None:
        while self.i < len(self.text) and self.text[self.i].isspace():
            self.i += 1

    def eat(self, token: str) -> bool:
        self.skip_ws()
        if self.text.startswith(token, self.i):
            self.i += len(token)
            return True
        return False

    def expect(self, token: str) -> None:
        if not self.eat(token):
            raise ParseError(f"expected {token!r} at offset {self.i}")

    def parse_tree(self) -> Tree:
        self.skip_ws()
        if self.eat("x"):
            return X
        if self.eat("1"):
            return ONE
        if self.eat("eml"):
            self.expect("(")
            left = self.parse_tree()
            self.expect(",")
            right = self.parse_tree()
            self.expect(")")
            return eml(left, right)
        raise ParseError(f"expected x, 1, or eml(...) at offset {self.i}")


def eml(left: Tree, right: Tree) -> Tree:
    return Tree("eml", left, right)


X = Tree("x")
ONE = Tree("one")


def enumerate_trees(max_depth: int) -> list[Tree]:
    by_depth: list[list[Tree]] = [[X, ONE]]
    seen = {X.pretty(): X, ONE.pretty(): ONE}

    for depth in range(1, max_depth + 1):
        candidates: list[Tree] = []
        lower = [tree for bucket in by_depth for tree in bucket]
        for left in lower:
            for right in lower:
                tree = eml(left, right)
                if tree.depth() == depth and tree.pretty() not in seen:
                    seen[tree.pretty()] = tree
                    candidates.append(tree)
        by_depth.append(candidates)

    return list(seen.values())


def values_on_grid(tree: Tree, xs: tuple[float, ...]) -> tuple[float, ...] | None:
    values, _reason = values_on_grid_with_reason(tree, xs)
    return values


def values_on_grid_with_reason(tree: Tree, xs: tuple[float, ...]) -> tuple[tuple[float, ...] | None, str | None]:
    values: list[float] = []
    try:
        for x in xs:
            values.append(tree.eval(x))
    except (OverflowError, ValueError) as exc:
        return None, str(exc)
    return tuple(values), None


def mse(values: tuple[float, ...], target: tuple[float, ...]) -> float:
    return sum((a - b) * (a - b) for a, b in zip(values, target, strict=True)) / len(values)


def mse_on_grid(tree: Tree, target_fn: Callable[[float], float], xs: tuple[float, ...]) -> float | None:
    values = values_on_grid(tree, xs)
    if values is None:
        return None
    target = tuple(target_fn(x) for x in xs)
    return mse(values, target)


def interval_eval(tree: Tree, interval: Interval) -> Interval:
    return interval_eval_collect(tree, interval, [], [])


def interval_eval_collect(
    tree: Tree,
    interval: Interval,
    log_arguments: list[dict[str, Any]],
    exp_arguments: list[dict[str, Any]],
) -> Interval:
    if tree.kind == "x":
        return interval
    if tree.kind == "one":
        return Interval(1.0, 1.0)
    assert tree.left is not None and tree.right is not None
    left = interval_eval_collect(tree.left, interval, log_arguments, exp_arguments)
    right = interval_eval_collect(tree.right, interval, log_arguments, exp_arguments)
    exp_arguments.append({"source": tree.left.pretty(), "interval": [left.lo, left.hi]})
    log_arguments.append({"source": tree.right.pretty(), "interval": [right.lo, right.hi]})
    if right.lo <= 0.0:
        raise ValueError("interval log domain failure")
    if abs(left.lo) > 180.0 or abs(left.hi) > 180.0:
        raise ValueError("interval exp guard failure")
    return Interval(math.exp(left.lo) - math.log(right.hi), math.exp(left.hi) - math.log(right.lo))


def interval_domain_receipt(tree: Tree, interval: Interval) -> dict[str, Any]:
    log_arguments: list[dict[str, Any]] = []
    exp_arguments: list[dict[str, Any]] = []
    try:
        out = interval_eval_collect(tree, interval, log_arguments, exp_arguments)
    except (OverflowError, ValueError) as exc:
        return {
            "status": "DomainReject",
            "domain_kind": "PositiveRealInputInterval",
            "input_interval": [interval.lo, interval.hi],
            "reason": str(exc),
            "log_arguments_checked": log_arguments,
            "exp_arguments_checked": exp_arguments,
        }
    log_lower_bounds = [item["interval"][0] for item in log_arguments]
    return {
        "status": "DomainOK",
        "domain_kind": "PositiveRealInputInterval",
        "input_interval": [interval.lo, interval.hi],
        "range_interval": [out.lo, out.hi],
        "log_arguments_checked": log_arguments,
        "exp_arguments_checked": exp_arguments,
        "minimum_log_argument_lower_bound": min(log_lower_bounds) if log_lower_bounds else None,
        "assumption": "interval evaluator is conservative over the positive real input interval",
    }


def neural_weight(error: float, size: int, sigma: float, size_penalty: float) -> float:
    return math.exp(-error / (2.0 * sigma * sigma) - size_penalty * size)


def tree_to_sympy(tree: Tree, x: Any) -> Any:
    if sp is None:
        raise RuntimeError("SymPy is not available")
    if tree.kind == "x":
        return x
    if tree.kind == "one":
        return sp.Integer(1)
    assert tree.left is not None and tree.right is not None
    return sp.exp(tree_to_sympy(tree.left, x)) - sp.log(tree_to_sympy(tree.right, x))


def symbolic_identity_check(tree: Tree, target_sympy: Callable[[Any], Any] | None) -> dict[str, Any]:
    if sp is None:
        return {"available": False, "reason": "sympy is not installed"}
    if target_sympy is None:
        return {"available": False, "reason": "no symbolic target was provided"}
    x = sp.symbols("x", positive=True)
    try:
        expr = tree_to_sympy(tree, x)
        target = target_sympy(x)
        difference = sp.simplify(sp.expand_log(expr - target, force=True))
        difference = sp.simplify(difference)
    except Exception as exc:  # pragma: no cover - diagnostic path
        return {"available": True, "proved_by_simplify": False, "error": repr(exc)}
    return {
        "available": True,
        "proved_by_simplify": bool(difference == 0),
        "symbolic_expression": str(expr),
        "simplified_difference": str(difference),
    }


def strategy_normalizer_receipt(expr: str, target_name: str) -> dict[str, Any]:
    receipts = {
        ("x", "x"): {
            "normalized_expr": "x",
            "normal_form": "x",
            "fuel_policy": "source compileExpr.size",
            "stable": True,
            "idempotent": True,
            "reaches_theorem": (
                "NeuroSymbolicMathV001.EML.RewriteStrategy."
                "var_emitChainFuel_size_reaches"
            ),
        },
        ("eml(x,1)", "exp(x)"): {
            "normalized_expr": "exp(x)",
            "normal_form": "expX",
            "fuel_policy": "source compileExpr.size",
            "stable": True,
            "idempotent": True,
            "reaches_theorem": (
                "NeuroSymbolicMathV001.EML.RewriteStrategy."
                "exp_emitChainFuel_size_reaches"
            ),
        },
        ("eml(1,eml(eml(1,eml(eml(x,1),1)),1))", "exp(x)"): {
            "normalized_expr": "exp(x)",
            "normal_form": "expX",
            "fuel_policy": "source compileExpr.size",
            "stable": True,
            "idempotent": True,
            "reaches_theorem": (
                "NeuroSymbolicMathV001.EML.RewriteStrategy."
                "logExpExp_emitChainFuel_size_reaches"
            ),
        },
        ("eml(1,eml(eml(1,x),1))", "ln(x)"): {
            "normalized_expr": "log(x)",
            "normal_form": "logX",
            "fuel_policy": "source compileExpr.size",
            "stable": True,
            "idempotent": True,
            "reaches_theorem": (
                "NeuroSymbolicMathV001.EML.RewriteStrategy."
                "logStandard_emitChainFuel_size_reaches"
            ),
        },
        ("eml(x,eml(eml(x,x),1))", "ln(x)"): {
            "normalized_expr": "log(x)",
            "normal_form": "logX",
            "fuel_policy": "source compileExpr.size",
            "stable": True,
            "idempotent": True,
            "reaches_theorem": (
                "NeuroSymbolicMathV001.EML.RewriteStrategy."
                "logDiscovered_emitChainFuel_size_reaches"
            ),
        },
        ("eml(1,eml(eml(1,eml(x,1)),1))", "x"): {
            "normalized_expr": "x",
            "normal_form": "x",
            "fuel_policy": "source compileExpr.size",
            "stable": True,
            "idempotent": True,
            "reaches_theorem": (
                "NeuroSymbolicMathV001.EML.RewriteStrategy."
                "identityViaLogExp_emitChainFuel_size_reaches"
            ),
        },
        ("eml(eml(x,1),1)", "exp(exp(x))"): {
            "normalized_expr": "exp(exp(x))",
            "normal_form": "expExpX",
            "fuel_policy": "source compileExpr.size",
            "stable": True,
            "idempotent": True,
            "reaches_theorem": (
                "NeuroSymbolicMathV001.EML.RewriteStrategy."
                "expExp_emitChainFuel_size_reaches"
            ),
        },
    }
    receipt = receipts.get((expr, target_name))
    if receipt is None:
        return {"accepted": False}
    return {
        "accepted": True,
        **receipt,
        "api": "NeuroSymbolicMathV001.EML.RewriteStrategy.normalize",
        "stable_theorem": "NeuroSymbolicMathV001.EML.RewriteStrategy.normalize_stable",
        "soundness_theorem": "NeuroSymbolicMathV001.EML.RewriteStrategy.normalize_sound",
        "idempotence_theorem": "NeuroSymbolicMathV001.EML.RewriteStrategy.normalize_idempotent",
        "cert_norm_bridge_theorem": (
            "NeuroSymbolicMathV001.EML.RewriteStrategy."
            "normalize_certNorm_reaches"
        ),
        "canon_zero_receipt_soundness_theorem": (
            "NeuroSymbolicMathV001.EML.RewriteStrategy."
            "normalizeReceiptCanonZero_sound"
        ),
        "boundary": (
            "strategy-normalizer receipt, not a canonical semantic "
            "normal-form proof"
        ),
    }


def lean_certificate(expr: str, target_name: str) -> dict[str, Any]:
    certificates = {
        ("x", "x"): "varTree",
        ("eml(x,1)", "exp(x)"): "expTree",
        ("eml(1,eml(eml(1,eml(eml(x,1),1)),1))", "exp(x)"): "logExpExpTree",
        ("eml(1,eml(eml(1,x),1))", "ln(x)"): "logStandardTree",
        ("eml(x,eml(eml(x,x),1))", "ln(x)"): "logDiscoveredTree",
        ("eml(1,eml(eml(1,eml(x,1)),1))", "x"): "identityViaLogExpTree",
        ("eml(eml(x,1),1)", "exp(exp(x))"): "expExpTree",
    }
    normal_forms = {
        ("x", "x"): "x",
        ("eml(x,1)", "exp(x)"): "expX",
        ("eml(1,eml(eml(1,eml(eml(x,1),1)),1))", "exp(x)"): "expX",
        ("eml(1,eml(eml(1,x),1))", "ln(x)"): "logX",
        ("eml(x,eml(eml(x,x),1))", "ln(x)"): "logX",
        ("eml(1,eml(eml(1,eml(x,1)),1))", "x"): "x",
        ("eml(eml(x,1),1)", "exp(exp(x))"): "expExpX",
    }
    name = certificates.get((expr, target_name))
    if name is None:
        return {"accepted": False}
    rewrite_chain = {"accepted": False}
    if (expr, target_name) == ("eml(x,eml(eml(x,x),1))", "ln(x)"):
        rewrite_chain = {
            "accepted": True,
            "chain_name": "logDiscoveredRewriteChain",
            "chain_length": 4,
            "target": "Expr.log Expr.var",
            "acceptance_theorem": "NeuroSymbolicMathV001.EML.logDiscoveredRewriteChain_accepts",
            "soundness_theorem": "NeuroSymbolicMathV001.EML.logDiscoveredRewriteChain_sound",
            "steps": [
                "rewrite nested log(1) to 0",
                "rewrite nested sub(a,0) to a",
                "rewrite right-side log(exp(a)) to a",
                "rewrite root sub(a,sub(a,b)) to b",
            ],
        }
    return {
        "accepted": True,
        "certificate": name,
        "checker": "NeuroSymbolicMathV001.EML.Cert.check",
        "soundness_theorem": "NeuroSymbolicMathV001.EML.Cert.sound",
        "normal_form": normal_forms[(expr, target_name)],
        "normal_form_checker": "NeuroSymbolicMathV001.EML.checkByNorm",
        "normal_form_soundness_theorem": "NeuroSymbolicMathV001.EML.checkByNorm_sound",
        "strategy_normalizer": strategy_normalizer_receipt(expr, target_name),
        "rewrite_chain": rewrite_chain,
    }


def parse_tree_expr(text: str) -> Tree:
    return TreeParser(text).parse()


def load_candidate_proposals(path: Path | None) -> list[dict[str, Any]]:
    if path is None:
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("candidates"), list):
        raise SystemExit("--candidate-json must contain an object with a candidates list")
    proposals: list[dict[str, Any]] = []
    for index, item in enumerate(data["candidates"]):
        if not isinstance(item, dict):
            raise SystemExit(f"candidate {index} is not an object")
        expr = item.get("expr")
        if not isinstance(expr, str) or not expr.strip():
            raise SystemExit(f"candidate {index} has no expr string")
        target = item.get("target", "*")
        if not isinstance(target, str):
            raise SystemExit(f"candidate {index} target must be a string")
        origin = item.get("origin", "llm")
        if not isinstance(origin, str):
            raise SystemExit(f"candidate {index} origin must be a string")
        proposals.append(
            {
                "expr": expr,
                "target": target,
                "origin": origin,
                "note": item.get("note", ""),
            }
        )
    return proposals


def combine_trees(
    enumerated: list[Tree],
    proposals: list[dict[str, Any]],
) -> tuple[list[Tree], dict[str, set[str]], list[dict[str, Any]]]:
    trees_by_expr = {tree.pretty(): tree for tree in enumerated}
    origins: dict[str, set[str]] = {expr: {"enumerated"} for expr in trees_by_expr}
    rejected: list[dict[str, Any]] = []
    for proposal in proposals:
        expr = str(proposal["expr"])
        try:
            tree = parse_tree_expr(expr)
        except ParseError as exc:
            rejected.append(
                {
                    "source_expr": expr,
                    "target": proposal["target"],
                    "origin": proposal["origin"],
                    "parse_ok": False,
                    "domain_status": "DomainUnknown",
                    "qns_status": "reject",
                    "rejection_reason": f"parse_error: {exc}",
                }
            )
            continue
        pretty = tree.pretty()
        if pretty not in trees_by_expr:
            trees_by_expr[pretty] = tree
        origins.setdefault(pretty, set()).add(str(proposal["origin"]))
    return list(trees_by_expr.values()), origins, rejected


def origin_label(origins: dict[str, set[str]], expr: str) -> str:
    values = sorted(origins.get(expr, {"unknown"}))
    return "+".join(values)


def worst_error_point(
    tree: Tree,
    target_fn: Callable[[float], float],
    xs: tuple[float, ...],
) -> dict[str, Any] | None:
    worst: dict[str, Any] | None = None
    for x in xs:
        try:
            got = tree.eval(x)
        except (OverflowError, ValueError) as exc:
            return {"x": x, "reason": str(exc), "kind": "domain"}
        expected = target_fn(x)
        absolute_error = abs(got - expected)
        if worst is None or absolute_error > worst["absolute_error"]:
            worst = {
                "x": x,
                "expected": expected,
                "actual": got,
                "absolute_error": absolute_error,
                "kind": "value",
            }
    return worst


def mask_hex(indices: list[int]) -> str:
    mask = 0
    for index in indices:
        mask |= 1 << index
    return hex(mask)


def build_qns_report(
    target_name: str,
    rows: list[dict[str, Any]],
    invalid_candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    reported_rows = sorted(rows, key=lambda row: (row["mse"], row["size"], row["expr"]))[:16]
    for row in reported_rows:
        cert = lean_certificate(str(row["expr"]), target_name)
        holdout_ok = bool(row.get("holdout_ok", False))
        proof_supported = bool(cert.get("accepted", False))
        spec_candidate = bool(row["spec_ok"]) and holdout_ok
        if spec_candidate and proof_supported:
            status = "accept"
        elif spec_candidate:
            status = "review"
        else:
            status = "reject"
        records.append(
            {
                "expr": row["expr"],
                "origin": row["candidate_origin"],
                "domain_status": "DomainOK",
                "spec_candidate": spec_candidate,
                "proof_supported": proof_supported,
                "qns_status": status,
            }
        )
    for candidate in invalid_candidates:
        if candidate["target"] in {"*", target_name}:
            records.append(candidate)
    records = records[:64]
    masks = {
        "proposed": mask_hex(list(range(len(records)))),
        "domain_valid": mask_hex(
            [i for i, item in enumerate(records) if item.get("domain_status") == "DomainOK"]
        ),
        "spec_candidate": mask_hex(
            [i for i, item in enumerate(records) if item.get("spec_candidate") is True]
        ),
        "proof_supported": mask_hex(
            [i for i, item in enumerate(records) if item.get("proof_supported") is True]
        ),
        "accepted": mask_hex([i for i, item in enumerate(records) if item.get("qns_status") == "accept"]),
        "review": mask_hex([i for i, item in enumerate(records) if item.get("qns_status") == "review"]),
        "rejected": mask_hex([i for i, item in enumerate(records) if item.get("qns_status") == "reject"]),
    }
    return {
        "target": target_name,
        "universe_count": len(records),
        "mask_semantics": "bit i refers to records[i]",
        "masks": masks,
        "records": records,
    }


def collect_counterexample_diagnostics(
    rows: list[dict[str, Any]],
    tree_by_expr: dict[str, Tree],
    target_fn: Callable[[float], float],
    holdout_xs: tuple[float, ...],
    limit: int = 5,
) -> list[dict[str, Any]]:
    rows_sorted = sorted(rows, key=lambda row: (row["mse"], row["size"], row["expr"]))
    diagnostics = []
    for row in rows_sorted:
        if row["spec_ok"]:
            continue
        tree = tree_by_expr[str(row["expr"])]
        witness = worst_error_point(tree, target_fn, holdout_xs)
        if witness is not None:
            diagnostics.append({"expr": row["expr"], "origin": row["candidate_origin"], **witness})
        if len(diagnostics) >= limit:
            break
    return diagnostics


def run_target(
    name: str,
    target_fn: Callable[[float], float],
    target_sympy: Callable[[Any], Any] | None,
    trees: list[Tree],
    origins: dict[str, set[str]],
    invalid_candidates: list[dict[str, Any]],
    xs: tuple[float, ...],
    holdout_xs: tuple[float, ...],
    *,
    tolerance: float,
    sigma: float,
    size_penalty: float,
    cegis_rounds: int,
) -> dict[str, object]:
    tree_by_expr = {tree.pretty(): tree for tree in trees}
    interval = Interval(min((*xs, *holdout_xs)), max((*xs, *holdout_xs)))
    counterexample_bank: list[dict[str, Any]] = []

    def score_candidates(grid: tuple[float, ...]) -> tuple[list[dict[str, Any]], int]:
        target = tuple(target_fn(x) for x in grid)
        rows: list[dict[str, Any]] = []
        valid_count = 0
        for tree in trees:
            values, reason = values_on_grid_with_reason(tree, grid)
            if values is None:
                continue
            valid_count += 1
            error = mse(values, target)
            holdout_error = mse_on_grid(tree, target_fn, holdout_xs)
            weight = neural_weight(error, tree.size(), sigma, size_penalty)
            spec_ok = error <= tolerance
            interval_receipt = interval_domain_receipt(tree, interval)
            rows.append(
                {
                    "expr": tree.pretty(),
                    "candidate_origin": origin_label(origins, tree.pretty()),
                    "depth": tree.depth(),
                    "size": tree.size(),
                    "domain_status": "DomainOK",
                    "domain_error": reason,
                    "interval_domain": interval_receipt,
                    "mse": error,
                    "neural_weight": weight,
                    "spec_ok": spec_ok,
                    "holdout_mse": holdout_error,
                    "holdout_ok": holdout_error is not None and holdout_error <= tolerance,
                }
            )
        return rows, valid_count

    active_grid = tuple(xs)
    rows, valid_count = score_candidates(active_grid)
    for _round in range(max(0, cegis_rounds)):
        diagnostics = collect_counterexample_diagnostics(rows, tree_by_expr, target_fn, holdout_xs)
        additions = []
        seen_additions = set(active_grid)
        for item in diagnostics:
            x = item.get("x")
            if isinstance(x, (int, float)) and float(x) not in seen_additions:
                additions.append(float(x))
                seen_additions.add(float(x))
                counterexample_bank.append(item)
        if not additions:
            break
        active_grid = tuple(sorted((*active_grid, *additions)))
        rows, valid_count = score_candidates(active_grid)

    neural_total = sum(row["neural_weight"] for row in rows)
    spec_total = sum(row["neural_weight"] for row in rows if row["spec_ok"])
    survivors = []
    for row in rows:
        if row["spec_ok"]:
            tree = tree_by_expr[str(row["expr"])]
            qn = row["neural_weight"] / neural_total if neural_total else 0.0
            qns = row["neural_weight"] / spec_total if spec_total else 0.0
            survivors.append(
                {
                    **row,
                    "q_N": qn,
                    "q_NS": qns,
                    "lean_certificate": lean_certificate(str(row["expr"]), name),
                    "symbolic_identity": symbolic_identity_check(tree, target_sympy),
                }
            )

    rows_sorted = sorted(rows, key=lambda row: (row["mse"], row["size"], row["expr"]))
    survivors_sorted = sorted(survivors, key=lambda row: (-row["q_NS"], row["size"], row["expr"]))
    diagnostics = collect_counterexample_diagnostics(rows, tree_by_expr, target_fn, holdout_xs)
    qns_report = build_qns_report(name, rows, invalid_candidates)

    return {
        "target": name,
        "grid": list(active_grid),
        "initial_grid": list(xs),
        "holdout_grid": list(holdout_xs),
        "candidate_count": len(trees),
        "domain_valid_count": valid_count,
        "spec_survivor_count": len(survivors_sorted),
        "best_before_filter": rows_sorted[:8],
        "survivors": survivors_sorted,
        "counterexample_bank": counterexample_bank,
        "counterexample_diagnostics": diagnostics,
        "qns_filter_report": qns_report,
        "ok": len(survivors_sorted) > 0,
    }


def build_tau_sidecar_manifest(results: list[dict[str, object]]) -> dict[str, Any]:
    formulas: list[dict[str, Any]] = []
    rejected_candidates: list[dict[str, Any]] = []
    qns_reports: list[dict[str, Any]] = []
    for target in results:
        target_name = str(target["target"])
        qns_reports.append(target["qns_filter_report"])  # type: ignore[arg-type]
        for item in target["qns_filter_report"]["records"]:  # type: ignore[index]
            if item.get("qns_status") == "reject" and item.get("parse_ok") is False:
                rejected_candidates.append(item)
        for survivor in target["survivors"]:  # type: ignore[index]
            expr = str(survivor["expr"])
            cert = survivor["lean_certificate"]
            strategy = cert.get("strategy_normalizer", {"accepted": False})
            proof_accepted = bool(cert.get("accepted", False)) and bool(strategy.get("accepted", False))
            formulas.append(
                {
                    "target": target_name,
                    "source_expr": expr,
                    "candidate_origin": survivor["candidate_origin"],
                    "normalized_expr": strategy.get("normalized_expr", expr),
                    "normal_form": strategy.get("normal_form", "unknown"),
                    "domain_guard": "real log arguments must be positive",
                    "domain_status": survivor["domain_status"],
                    "interval_domain": survivor["interval_domain"],
                    "sample_mse": survivor["mse"],
                    "holdout_mse": survivor["holdout_mse"],
                    "qns_status": "accept" if proof_accepted else "review",
                    "proof_status": "accepted" if proof_accepted else "needs_review",
                    "proof_api": strategy.get("api"),
                    "soundness_theorem": strategy.get("soundness_theorem"),
                    "stability_theorem": strategy.get("stable_theorem"),
                    "idempotence_theorem": strategy.get("idempotence_theorem"),
                    "bridge_theorem": strategy.get("cert_norm_bridge_theorem"),
                    "canon_zero_receipt_soundness_theorem": strategy.get(
                        "canon_zero_receipt_soundness_theorem"
                    ),
                    "boundary": (
                        "Tau-facing metadata sidecar; not native unrestricted "
                        "analytic Tau semantics"
                    ),
                }
            )
    return {
        "schema": "eml_tau_sidecar_manifest_v2",
        "purpose": (
            "formula-discovery and certificate-carrying simplification metadata "
            "for Tau-adjacent demos"
        ),
        "native_tau_claim": False,
        "boundary": (
            "This manifest can inform Tau specs, explanations, thresholds, or "
            "demo metadata. It does not add exp/log semantics to Tau Language."
        ),
        "qns_filter": {
            "semantics": "models propose formulas; symbolic masks accept, reject, or route them to review",
            "target_reports": qns_reports,
        },
        "rejected_candidates": rejected_candidates,
        "formula_count": len(formulas),
        "formulas": formulas,
    }


def build_reproposal_feedback_packet(results: list[dict[str, object]]) -> dict[str, Any]:
    """Create a compact feedback packet for the next untrusted proposer round."""

    target_feedback: list[dict[str, Any]] = []
    for target in results:
        accepted = [
            {
                "expr": survivor["expr"],
                "origin": survivor["candidate_origin"],
                "normalized_expr": survivor["lean_certificate"]
                .get("strategy_normalizer", {})
                .get("normalized_expr", survivor["expr"]),
            }
            for survivor in target["survivors"]  # type: ignore[index]
        ]
        qns_records = target["qns_filter_report"]["records"]  # type: ignore[index]
        rejected = [
            {
                "expr": item.get("expr") or item.get("source_expr"),
                "origin": item.get("origin"),
                "reason": item.get("rejection_reason", "failed qNS promotion gates"),
                "domain_status": item.get("domain_status"),
            }
            for item in qns_records
            if item.get("qns_status") == "reject"
        ][:12]
        target_feedback.append(
            {
                "target": target["target"],
                "accepted": accepted,
                "counterexample_bank": target["counterexample_bank"],
                "counterexample_diagnostics": target["counterexample_diagnostics"],
                "rejected": rejected,
                "next_constraints": [
                    "use only the grammar T ::= x | 1 | eml(T,T)",
                    "do not use constants other than 1",
                    "keep every real logarithm argument positive on the checked interval",
                    "prefer formulas that differ structurally from accepted expressions unless improving proof support",
                    "treat every diagnostic point as an input that the next candidate should satisfy",
                ],
            }
        )
    return {
        "schema": "eml_reproposal_feedback_v1",
        "purpose": "bounded counterexample and rejection feedback for the next EML proposer round",
        "trusted_by_itself": False,
        "grammar": "T ::= x | 1 | eml(T,T)",
        "operator": "eml(a,b)=exp(a)-ln(b)",
        "boundary": (
            "This packet is proposer feedback. It is not proof evidence and "
            "does not authorize a candidate without re-running parser, qNS, "
            "domain, spec, and proof-receipt checks."
        ),
        "targets": target_feedback,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-depth", type=int, default=3)
    parser.add_argument("--tolerance", type=float, default=1.0e-20)
    parser.add_argument("--sigma", type=float, default=0.1)
    parser.add_argument("--size-penalty", type=float, default=0.01)
    parser.add_argument(
        "--candidate-json",
        type=Path,
        help="Optional external proposal file with EML strings, for example LLM-proposed formulas.",
    )
    parser.add_argument(
        "--cegis-rounds",
        type=int,
        default=1,
        help="Number of diagnostic counterexample rounds to report. The current demo uses one bounded diagnostic round.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "results" / "local" / "eml-neurosymbolic-loop-demo.json",
    )
    parser.add_argument(
        "--sidecar-out",
        type=Path,
        default=ROOT / "results" / "local" / "eml-tau-sidecar-manifest.json",
    )
    parser.add_argument(
        "--feedback-out",
        type=Path,
        default=ROOT / "results" / "local" / "eml-reproposal-feedback-packet.json",
    )
    parser.add_argument(
        "--include-identity-target",
        action="store_true",
        help="Also check the identity target x, including a composed log(exp(x)) EML survivor.",
    )
    parser.add_argument(
        "--include-exp-exp-target",
        action="store_true",
        help="Also check exp(exp(x)), including the context-lifted eml(eml(x,1),1) survivor.",
    )
    args = parser.parse_args()

    if args.max_depth < 0:
        raise SystemExit("--max-depth must be non-negative")
    args.out = repo_path(args.out)
    args.sidecar_out = repo_path(args.sidecar_out)
    args.feedback_out = repo_path(args.feedback_out)
    if args.candidate_json is not None:
        args.candidate_json = repo_path(args.candidate_json)

    xs = (0.5, 1.0, 2.0)
    holdout_xs = (0.25, 0.75, 1.5, 3.0)
    proposals = load_candidate_proposals(args.candidate_json)
    trees, origins, invalid_candidates = combine_trees(enumerate_trees(args.max_depth), proposals)
    targets: list[tuple[str, Callable[[float], float], Callable[[Any], Any] | None]] = [
        ("exp(x)", math.exp, (lambda x: sp.exp(x)) if sp is not None else None),
        ("ln(x)", math.log, (lambda x: sp.log(x)) if sp is not None else None),
    ]
    if args.include_identity_target:
        targets.append(("x", lambda x: x, (lambda x: x) if sp is not None else None))
    if args.include_exp_exp_target:
        targets.append(
            (
                "exp(exp(x))",
                lambda x: math.exp(math.exp(x)),
                (lambda x: sp.exp(sp.exp(x))) if sp is not None else None,
            )
        )

    results = [
        run_target(
            name,
            fn,
            symbolic_fn,
            trees,
            origins,
            invalid_candidates,
            xs,
            holdout_xs,
            tolerance=args.tolerance,
            sigma=args.sigma,
            size_penalty=args.size_penalty,
            cegis_rounds=args.cegis_rounds,
        )
        for name, fn, symbolic_fn in targets
    ]

    output = {
        "ok": all(result["ok"] for result in results),
        "scope": "finite EML-tree qNS loop demo over real-domain sample checks",
        "grammar": "T ::= x | 1 | eml(T,T), eml(a,b)=exp(a)-ln(b)",
        "max_depth": args.max_depth,
        "candidate_count": len(trees),
        "external_candidate_count": len(proposals),
        "external_candidate_reject_count": len(invalid_candidates),
        "cegis_rounds": args.cegis_rounds,
        "hard_filter": "real log domain plus sampled spec tolerance",
        "certificate_checker": "Lean-checked finite certificate and normal-form checker for current survivor shapes",
        "strategy_normalizer": "Lean-checked current-strategy normalizer with stability, soundness, and idempotence",
        "symbolic_verifier": "sympy simplify over a positive real symbol" if sp is not None else "unavailable",
        "candidate_input_boundary": "external candidates are proposals only; they enter through qNS masks and require proof or review before promotion",
        "targets": results,
    }
    sidecar = build_tau_sidecar_manifest(results)
    feedback_packet = build_reproposal_feedback_packet(results)
    output["tau_sidecar_manifest"] = {
        "path": str(args.sidecar_out.relative_to(ROOT)),
        "schema": sidecar["schema"],
        "formula_count": sidecar["formula_count"],
    }
    output["reproposal_feedback_packet"] = {
        "path": str(args.feedback_out.relative_to(ROOT)),
        "schema": feedback_packet["schema"],
        "target_count": len(feedback_packet["targets"]),
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    args.sidecar_out.parent.mkdir(parents=True, exist_ok=True)
    args.sidecar_out.write_text(json.dumps(sidecar, indent=2) + "\n", encoding="utf-8")
    args.feedback_out.parent.mkdir(parents=True, exist_ok=True)
    args.feedback_out.write_text(json.dumps(feedback_packet, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": output["ok"], "targets": len(results)}, indent=2))
    return 0 if output["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
