#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "assets" / "data" / "eml_regression_certificate_manifest.json"
DEFAULT_EXACT = ROOT / "assets" / "data" / "eml_bounded_symbolic_regression.json"
DEFAULT_NOISY = ROOT / "assets" / "data" / "eml_noisy_regression_certificates.json"
DEFAULT_QNS_TAU = ROOT / "external" / "tau-lang-qns-ba" / "build-Release" / "tau"
MASK = 0xFF

sys.path.insert(0, str(ROOT / "scripts"))
from generate_qns_candidate_ba_artifacts import qns_const, qns_not, run_tau_qns_normalize  # noqa: E402


CERT_BITS = {
    "grammar_bounded": 0,
    "fit_passed": 1,
    "holdout_passed": 2,
    "minimality_scoped": 3,
    "proof_receipt": 4,
    "symbolic_identity": 5,
    "residual_certificate": 6,
    "review_required": 7,
}
REQUIRED_MASK = sum(1 << bit for name, bit in CERT_BITS.items() if name != "review_required")


def bit(name: str) -> int:
    return 1 << CERT_BITS[name]


def mask_names(mask: int) -> list[str]:
    return [name for name, idx in CERT_BITS.items() if mask & (1 << idx)]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_exact_result(result: dict[str, Any]) -> dict[str, Any]:
    accepted = 0
    review_reasons: list[str] = []
    best = result.get("best_fit")
    if best is not None:
        accepted |= bit("grammar_bounded")
    else:
        review_reasons.append("missing best_fit")
    if best and best.get("train_ok") is True:
        accepted |= bit("fit_passed")
    else:
        review_reasons.append("training fit did not pass")
    if best and best.get("holdout_ok") is True:
        accepted |= bit("holdout_passed")
    else:
        review_reasons.append("holdout fit did not pass")
    minimal = result.get("minimality_certificate", {})
    if minimal.get("minimal_within_bounded_corpus") is True:
        accepted |= bit("minimality_scoped")
    else:
        review_reasons.append("bounded minimality certificate did not pass")
    if result.get("proof_receipt", {}).get("accepted") is True:
        accepted |= bit("proof_receipt")
    else:
        review_reasons.append("proof receipt did not accept")
    if result.get("symbolic_identity", {}).get("proved_by_simplify") is True:
        accepted |= bit("symbolic_identity")
    else:
        review_reasons.append("symbolic identity check did not accept")
    if best and best.get("train_error") is not None and best.get("holdout_error") is not None:
        accepted |= bit("residual_certificate")
    else:
        review_reasons.append("residual fields are missing")
    review = bit("review_required") if review_reasons else 0
    return {
        "source_kind": "exact_bounded",
        "target": result["target"],
        "expr": best["expr"] if best else None,
        "accepted_mask": accepted,
        "review_mask": review,
        "review_reasons": review_reasons,
    }


def validate_noisy_result(result: dict[str, Any]) -> dict[str, Any]:
    accepted = 0
    review_reasons: list[str] = []
    winner = result.get("winner")
    if winner is not None:
        accepted |= bit("grammar_bounded")
    else:
        review_reasons.append("missing winner")
    if winner and winner.get("train_mse_noisy") is not None:
        accepted |= bit("fit_passed")
    else:
        review_reasons.append("no noisy training objective")
    if winner and winner.get("holdout_mse_clean") is not None:
        accepted |= bit("holdout_passed")
    else:
        review_reasons.append("no holdout objective")
    residual = result.get("residual_certificate", {})
    if residual.get("winner_rank") == 0:
        accepted |= bit("minimality_scoped")
    else:
        review_reasons.append("winner is not rank 0 under declared objective")
    if result.get("proof_receipt", {}).get("accepted") is True:
        accepted |= bit("proof_receipt")
    else:
        review_reasons.append("proof receipt did not accept")
    if result.get("symbolic_identity", {}).get("proved_by_simplify") is True:
        accepted |= bit("symbolic_identity")
    else:
        review_reasons.append("symbolic identity check did not accept")
    if residual.get("winner_train_residual_noisy") and residual.get("winner_holdout_residual_clean"):
        accepted |= bit("residual_certificate")
    else:
        review_reasons.append("residual certificate is missing")
    review = bit("review_required") if review_reasons else 0
    return {
        "source_kind": "noisy_bounded",
        "target": result["clean_target"],
        "expr": winner["expr"] if winner else None,
        "accepted_mask": accepted,
        "review_mask": review,
        "review_reasons": review_reasons,
    }


def tau_check(tau_bin: str, accepted_mask: int, review_mask: int, timeout_s: float) -> dict[str, Any]:
    accepted = qns_const(accepted_mask)
    required = qns_const(REQUIRED_MASK)
    review = qns_const(review_mask)
    missing_expr = f"(({required}) & ({qns_not(accepted)}))"
    promoted_expr = f"(({accepted}) & ({required}))"
    blocker_expr = f"(({missing_expr}) | ({review}))"
    missing, _ = run_tau_qns_normalize(tau_bin, missing_expr, timeout_s=timeout_s)
    promoted, _ = run_tau_qns_normalize(tau_bin, promoted_expr, timeout_s=timeout_s)
    blocker, _ = run_tau_qns_normalize(tau_bin, blocker_expr, timeout_s=timeout_s)
    return {
        "missing_required_mask": int(missing),
        "promoted_mask": int(promoted),
        "blocker_mask": int(blocker),
        "promoted": int(missing) == 0 and int(blocker) == 0 and int(promoted) == REQUIRED_MASK,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Wrap EML regression winners in qNS certificates.")
    parser.add_argument("--exact", type=Path, default=DEFAULT_EXACT)
    parser.add_argument("--noisy", type=Path, default=DEFAULT_NOISY)
    parser.add_argument("--tau-bin", type=Path, default=DEFAULT_QNS_TAU)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--timeout-s", type=float, default=10.0)
    args = parser.parse_args()

    exact_path = args.exact if args.exact.is_absolute() else ROOT / args.exact
    noisy_path = args.noisy if args.noisy.is_absolute() else ROOT / args.noisy
    tau_bin = args.tau_bin if args.tau_bin.is_absolute() else ROOT / args.tau_bin
    if not tau_bin.exists():
        raise SystemExit("patched qNS Tau binary is missing")
    exact = load_json(exact_path)
    noisy = load_json(noisy_path)
    source_artifacts = {
        "exact_bounded": {
            "path": str(exact_path.relative_to(ROOT)),
            "sha256": sha256_file(exact_path),
            "schema": exact.get("schema"),
        },
        "noisy_bounded": {
            "path": str(noisy_path.relative_to(ROOT)),
            "sha256": sha256_file(noisy_path),
            "schema": noisy.get("schema"),
        },
    }

    rows = [validate_exact_result(result) for result in exact["results"]]
    rows.extend(validate_noisy_result(result) for result in noisy["results"])
    for row in rows:
        source = source_artifacts[row["source_kind"]]
        row["source_artifact"] = source["path"]
        row["source_sha256"] = source["sha256"]
        row["accepted_atoms"] = mask_names(row["accepted_mask"])
        row["review_atoms"] = mask_names(row["review_mask"])
        row["tau_check"] = tau_check(
            str(tau_bin), row["accepted_mask"], row["review_mask"], args.timeout_s
        )

    artifact = {
        "schema": "eml_regression_certificate_manifest_v1",
        "generator": "scripts/generate_eml_regression_certificate_manifest.py",
        "scope": {
            "claim": (
                "EML regression winners can be wrapped as qNS-style certificates "
                "and promoted only when required finite evidence bits are present."
            ),
            "not_claimed": [
                "not full symbolic regression",
                "not statistical consistency",
                "not native Tau analytic semantics",
                "not proof beyond each source artifact's bounded corpus",
            ],
        },
        "certificate_bits": CERT_BITS,
        "required_mask": REQUIRED_MASK,
        "source_artifacts": source_artifacts,
        "summary": {
            "ok": all(row["tau_check"]["promoted"] for row in rows),
            "certificate_count": len(rows),
            "promoted_count": sum(1 for row in rows if row["tau_check"]["promoted"]),
            "review_count": sum(1 for row in rows if row["review_mask"] != 0),
            "tau_blocker_count": sum(1 for row in rows if row["tau_check"]["blocker_mask"] != 0),
            "exact_source_count": sum(1 for row in rows if row["source_kind"] == "exact_bounded"),
            "noisy_source_count": sum(1 for row in rows if row["source_kind"] == "noisy_bounded"),
        },
        "rows": rows,
    }
    out = args.out if args.out.is_absolute() else ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "ok": artifact["summary"]["ok"],
                "out": str(out.relative_to(ROOT)),
                "certificate_count": artifact["summary"]["certificate_count"],
            },
            indent=2,
        )
    )
    return 0 if artifact["summary"]["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
