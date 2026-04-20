#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "assets" / "data" / "qns_certificate_proposer_traces.json"
DEFAULT_QNS_TAU = ROOT / "external" / "tau-lang-qns-ba" / "build-Release" / "tau"
MASK = 0xFF
REQUIRED_COLLATERAL = 0x3F
RISK_ATOMS = 1 << 6
OLD_MEMORY = 0x00

sys.path.insert(0, str(ROOT / "scripts"))
from compile_qns_ontology_masks import (  # noqa: E402
    AMBIGUOUS_PHRASES,
    ATOMS,
    WORD_RE,
    compile_text,
    normalize,
)
from generate_qns_candidate_ba_artifacts import qns_const, qns_not, run_tau_qns_normalize  # noqa: E402


@dataclass(frozen=True)
class Claim:
    span: str
    atom: str
    confidence: float
    reason: str


CERTIFICATES: tuple[dict[str, Any], ...] = (
    {
        "name": "clean_certified_collateral",
        "claims": (
            Claim("registry verified", "registry_verified", 0.94, "registry receipt found"),
            Claim("deep liquidity", "liquidity_deep", 0.91, "pool depth threshold met"),
            Claim("old token", "token_old_enough", 0.88, "age threshold met"),
            Claim("clean provenance", "provenance_clean", 0.89, "trace screen passed"),
            Claim("separated governance", "governance_separated", 0.86, "admin path separated"),
            Claim("stable oracle", "oracle_stable", 0.92, "oracle variance bounded"),
        ),
    },
    {
        "name": "ambiguous_certificate",
        "claims": (
            Claim("registry exists", "registry_verified", 0.84, "registry entry present"),
            Claim("review", "human_review_required", 0.61, "model asks for review"),
            Claim("risk", "sanction_risk", 0.58, "model reports risk"),
        ),
    },
    {
        "name": "bad_certificate",
        "claims": (
            Claim("stable oracle", "oracle_stable", 0.82, "oracle check passed"),
            Claim("deep liquidity", "market_sentiment_positive", 0.79, "unsupported atom"),
            Claim("quantum sentiment", "oracle_stable", 0.77, "unsupported span"),
        ),
    },
)


def atoms_by_name() -> dict[str, Any]:
    return {atom.name: atom for atom in ATOMS}


def mask_names(mask: int) -> list[str]:
    return [atom.name for atom in ATOMS if mask & atom.mask]


def span_tokens(span: str) -> set[str]:
    return set(WORD_RE.findall(span.lower()))


def claim_matches_atom(claim: Claim, atom: Any) -> bool:
    norm = normalize(claim.span)
    return any(phrase == norm for phrase in atom.phrases)


def ambiguous_mask_for_span(span: str) -> int:
    atoms = atoms_by_name()
    norm = normalize(span)
    mask = 0
    for phrase, names in AMBIGUOUS_PHRASES.items():
        if phrase == norm:
            for name in names:
                mask |= atoms[name].mask
    return mask


def validate_certificate(certificate: dict[str, Any]) -> dict[str, Any]:
    atoms = atoms_by_name()
    accepted_mask = 0
    review_mask = 0
    rejected_claims: list[dict[str, Any]] = []
    accepted_claims: list[dict[str, Any]] = []

    for claim in certificate["claims"]:
        row = {
            "span": claim.span,
            "atom": claim.atom,
            "confidence": claim.confidence,
            "reason": claim.reason,
        }
        atom = atoms.get(claim.atom)
        if atom is None:
            rejected_claims.append({**row, "reject_reason": "unknown_atom"})
            review_mask |= 1 << 7
            continue
        if claim_matches_atom(claim, atom):
            accepted_mask |= atom.mask
            accepted_claims.append({**row, "accepted_mask": atom.mask})
            continue
        ambiguous = ambiguous_mask_for_span(claim.span)
        if ambiguous:
            rejected_claims.append(
                {**row, "reject_reason": "ambiguous_span_requires_review", "review_mask": ambiguous}
            )
            review_mask |= ambiguous
            continue
        span_compiled = compile_text(claim.span)
        unknown_terms = span_compiled["unknown_terms"]
        rejected_claims.append(
            {
                **row,
                "reject_reason": "unsupported_span_for_atom",
                "unknown_terms": unknown_terms,
            }
        )
        review_mask |= 1 << 7

    return {
        "accepted_mask": accepted_mask,
        "review_mask": review_mask,
        "accepted_atoms": mask_names(accepted_mask),
        "review_atoms": mask_names(review_mask),
        "accepted_claims": accepted_claims,
        "rejected_claims": rejected_claims,
    }


def host_not(mask: int) -> int:
    return MASK ^ mask


def host_revise(old: int, guard: int, replacement: int) -> int:
    return (guard & replacement) | (host_not(guard) & old)


def host_outputs(validated: dict[str, Any]) -> dict[str, int]:
    observed = int(validated["accepted_mask"])
    review = int(validated["review_mask"])
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


def tau_exprs(validated: dict[str, Any]) -> dict[str, str]:
    observed = qns_const(int(validated["accepted_mask"]))
    review = qns_const(int(validated["review_mask"]))
    required = qns_const(REQUIRED_COLLATERAL)
    risk = qns_const(RISK_ATOMS)
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


def run_tau_case(tau_bin: str, certificate: dict[str, Any], timeout_s: float) -> dict[str, Any]:
    validated = validate_certificate(certificate)
    expected = host_outputs(validated)
    exprs = tau_exprs(validated)
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
    name = certificate["name"]
    return {
        "name": name,
        "validated_certificate": validated,
        "expected": expected,
        "actual": actual,
        "named_outputs": {key: mask_names(value) for key, value in actual.items()},
        "checks": {
            "tau_matches_host": not mismatches,
            "clean_has_no_blockers": actual["blocker_surface"] == 0
            if name == "clean_certified_collateral"
            else True,
            "nonclean_input_has_blockers": actual["blocker_surface"] != 0
            if name != "clean_certified_collateral"
            else True,
            "revision_idempotent": actual["revised_twice"] == actual["revised_memory"],
            "unknown_atom_claims_do_not_enter_accepted_mask": all(
                rejected["atom"] not in validated["accepted_atoms"]
                or rejected["reject_reason"] != "unknown_atom"
                for rejected in validated["rejected_claims"]
            ),
        },
        "mismatches": mismatches,
        "measurements": measurements,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate certificate-carrying qNS proposer output.")
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

    rows = [run_tau_case(str(tau_bin), cert, args.timeout_s) for cert in CERTIFICATES]
    accepted_claim_count = sum(len(row["validated_certificate"]["accepted_claims"]) for row in rows)
    rejected_claim_count = sum(len(row["validated_certificate"]["rejected_claims"]) for row in rows)
    ambiguous_claim_count = sum(
        1
        for row in rows
        for rejected in row["validated_certificate"]["rejected_claims"]
        if rejected["reject_reason"] == "ambiguous_span_requires_review"
    )
    unknown_atom_claim_count = sum(
        1
        for row in rows
        for rejected in row["validated_certificate"]["rejected_claims"]
        if rejected["reject_reason"] == "unknown_atom"
    )
    unsupported_span_claim_count = sum(
        1
        for row in rows
        for rejected in row["validated_certificate"]["rejected_claims"]
        if rejected["reject_reason"] == "unsupported_span_for_atom"
    )
    summary = {
        "ok": all(row["checks"]["tau_matches_host"] for row in rows),
        "certificate_count": len(rows),
        "total_claim_count": accepted_claim_count + rejected_claim_count,
        "accepted_claim_count": accepted_claim_count,
        "rejected_claim_count": rejected_claim_count,
        "ambiguous_claim_count": ambiguous_claim_count,
        "unknown_atom_claim_count": unknown_atom_claim_count,
        "unsupported_span_claim_count": unsupported_span_claim_count,
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
        "schema": "qns_certificate_proposer_traces_v1",
        "generator": "scripts/generate_qns_certificate_proposer_artifacts.py",
        "scope": {
            "claim": (
                "Certificate-carrying proposer output can be deterministically "
                "validated against the governed qNS ontology before accepted "
                "masks are sent to Tau."
            ),
            "not_claimed": [
                "not general natural-language understanding",
                "not proof that an external LLM extracted the right spans",
                "not upstream nlang semantics",
                "not official Tau Language support",
            ],
        },
        "certificate_schema": {
            "required_fields": ["span", "atom", "confidence", "reason"],
            "acceptance_rule": "the atom must exist and the normalized span must exactly match one audited phrase for that atom",
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
                "certificate_count": summary["certificate_count"],
            },
            indent=2,
        )
    )
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
