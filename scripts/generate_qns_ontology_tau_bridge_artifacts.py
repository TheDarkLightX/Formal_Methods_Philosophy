#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "assets" / "data" / "qns_ontology_tau_bridge_traces.json"
DEFAULT_QNS_TAU = ROOT / "external" / "tau-lang-qns-ba" / "build-Release" / "tau"
MASK = 0xFF
REQUIRED_COLLATERAL = 0x3F
RISK_ATOMS = 1 << 6
OLD_MEMORY = 0x00

sys.path.insert(0, str(ROOT / "scripts"))
from compile_qns_ontology_masks import CASES, compile_text  # noqa: E402
from generate_qns_candidate_ba_artifacts import qns_const, qns_not, run_tau_qns_normalize  # noqa: E402


def host_not(mask: int) -> int:
    return MASK ^ mask


def host_revise(old: int, guard: int, replacement: int) -> int:
    return (guard & replacement) | (host_not(guard) & old)


def host_outputs(compiled: dict[str, Any]) -> dict[str, int]:
    observed = int(compiled["observed_mask"])
    review = int(compiled["review_mask"])
    present_required = observed & REQUIRED_COLLATERAL
    missing_required = REQUIRED_COLLATERAL & host_not(observed)
    risk_hits = observed & RISK_ATOMS
    blocker_surface = missing_required | risk_hits | review
    clearance_surface = present_required & host_not(risk_hits | review)
    revised_memory = host_revise(OLD_MEMORY, blocker_surface, blocker_surface)
    revised_twice = host_revise(revised_memory, blocker_surface, blocker_surface)
    return {
        "present_required": present_required,
        "missing_required": missing_required,
        "risk_hits": risk_hits,
        "review_hits": review,
        "blocker_surface": blocker_surface,
        "clearance_surface": clearance_surface,
        "revised_memory": revised_memory,
        "revised_twice": revised_twice,
    }


def tau_exprs(compiled: dict[str, Any]) -> dict[str, str]:
    observed = qns_const(int(compiled["observed_mask"]))
    review = qns_const(int(compiled["review_mask"]))
    required = qns_const(REQUIRED_COLLATERAL)
    risk = qns_const(RISK_ATOMS)
    old = qns_const(OLD_MEMORY)
    present_required = f"(({observed}) & ({required}))"
    missing_required = f"(({required}) & ({qns_not(observed)}))"
    risk_hits = f"(({observed}) & ({risk}))"
    review_hits = review
    blocker_surface = f"(({missing_required}) | ({risk_hits}) | ({review_hits}))"
    clearance_surface = f"(({present_required}) & ({qns_not(f'(({risk_hits}) | ({review_hits}))')}))"
    return {
        "present_required": present_required,
        "missing_required": missing_required,
        "risk_hits": risk_hits,
        "review_hits": review_hits,
        "blocker_surface": blocker_surface,
        "clearance_surface": clearance_surface,
    }


def mask_names(mask: int) -> list[str]:
    names = (
        "registry_verified",
        "liquidity_deep",
        "token_old_enough",
        "provenance_clean",
        "governance_separated",
        "oracle_stable",
        "sanction_risk",
        "human_review_required",
    )
    return [name for bit, name in enumerate(names) if mask & (1 << bit)]


def run_case(tau_bin: str, case: dict[str, str], timeout_s: float) -> dict[str, Any]:
    compiled = compile_text(case["text"])
    expected = host_outputs(compiled)
    exprs = tau_exprs(compiled)
    actual: dict[str, int] = {}
    measurements: dict[str, dict[str, Any]] = {}
    for name, expr in exprs.items():
        value, _raw = run_tau_qns_normalize(tau_bin, expr, timeout_s=timeout_s)
        actual[name] = int(value)
        measurements[name] = {"ok": True, "expression_bytes": len(expr.encode("utf-8"))}
    blocker = qns_const(actual["blocker_surface"])
    old = qns_const(OLD_MEMORY)
    revised_expr = f"((({blocker}) & ({blocker})) | ({qns_not(blocker)} & ({old})))"
    revised_value, _raw = run_tau_qns_normalize(tau_bin, revised_expr, timeout_s=timeout_s)
    actual["revised_memory"] = int(revised_value)
    measurements["revised_memory"] = {
        "ok": True,
        "expression_bytes": len(revised_expr.encode("utf-8")),
        "staged_from": "blocker_surface",
    }
    revised = qns_const(actual["revised_memory"])
    revised_twice_expr = f"((({blocker}) & ({blocker})) | ({qns_not(blocker)} & ({revised})))"
    revised_twice_value, _raw = run_tau_qns_normalize(
        tau_bin, revised_twice_expr, timeout_s=timeout_s
    )
    actual["revised_twice"] = int(revised_twice_value)
    measurements["revised_twice"] = {
        "ok": True,
        "expression_bytes": len(revised_twice_expr.encode("utf-8")),
        "staged_from": "blocker_surface",
    }
    mismatches = {
        key: {"expected": expected[key], "actual": actual.get(key)}
        for key in expected
        if expected[key] != actual.get(key)
    }
    return {
        "name": case["name"],
        "text": case["text"],
        "compiled": {
            "observed_mask": compiled["observed_mask"],
            "exact_mask": compiled["exact_mask"],
            "review_mask": compiled["review_mask"],
            "unknown_terms": compiled["unknown_terms"],
            "ambiguous_phrases": compiled["ambiguous_phrases"],
        },
        "expected": expected,
        "actual": actual,
        "named_outputs": {key: mask_names(value) for key, value in actual.items()},
        "checks": {
            "tau_matches_host": not mismatches,
            "clean_has_no_blockers": actual["blocker_surface"] == 0
            if case["name"] == "clean_collateral_report"
            else True,
            "nonclean_input_has_blockers": actual["blocker_surface"] != 0
            if case["name"] != "clean_collateral_report"
            else True,
            "revision_idempotent": actual["revised_twice"] == actual["revised_memory"],
        },
        "mismatches": mismatches,
        "measurements": measurements,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run qNS ontology compiler outputs through Tau.")
    parser.add_argument("--tau-bin", type=Path, default=DEFAULT_QNS_TAU)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--timeout-s", type=float, default=10.0)
    args = parser.parse_args()

    tau_bin = args.tau_bin if args.tau_bin.is_absolute() else ROOT / args.tau_bin
    if not tau_bin.exists():
        raise SystemExit(
            "qNS Tau binary not found. Run scripts/run_qns_semantic_ba_demos.sh first "
            "or pass --tau-bin."
        )

    rows = [run_case(str(tau_bin), case, args.timeout_s) for case in CASES]
    summary = {
        "ok": all(row["checks"]["tau_matches_host"] for row in rows),
        "case_count": len(rows),
        "tau_mismatch_count": sum(1 for row in rows if not row["checks"]["tau_matches_host"]),
        "clean_blocker_failure_count": sum(
            1 for row in rows if not row["checks"]["clean_has_no_blockers"]
        ),
        "nonclean_blocker_failure_count": sum(
            1 for row in rows if not row["checks"]["nonclean_input_has_blockers"]
        ),
        "revision_idempotence_failure_count": sum(
            1 for row in rows if not row["checks"]["revision_idempotent"]
        ),
    }
    artifact = {
        "schema": "qns_ontology_tau_bridge_traces_v1",
        "generator": "scripts/generate_qns_ontology_tau_bridge_artifacts.py",
        "scope": {
            "claim": (
                "Compiled qNS ontology masks can be passed into real Tau qns8 "
                "expressions for blocker detection and pointwise revision-style "
                "memory updates."
            ),
            "not_claimed": [
                "not general natural-language understanding",
                "not upstream nlang semantics",
                "not official Tau Language support",
                "not semantic correctness outside the audited ontology table",
            ],
        },
        "parameters": {
            "required_collateral_mask": REQUIRED_COLLATERAL,
            "risk_atoms_mask": RISK_ATOMS,
            "old_memory_mask": OLD_MEMORY,
        },
        "summary": summary,
        "rows": rows,
    }
    out = args.out if args.out.is_absolute() else ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "ok": summary["ok"],
                "out": str(out.relative_to(ROOT)),
                "case_count": summary["case_count"],
            },
            indent=2,
        )
    )
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
