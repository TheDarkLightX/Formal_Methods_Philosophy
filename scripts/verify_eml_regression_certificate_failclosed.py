#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "assets" / "data" / "eml_regression_certificate_manifest.json"
DEFAULT_OUT = ROOT / "assets" / "data" / "eml_regression_certificate_failclosed.json"
DEFAULT_QNS_TAU = ROOT / "external" / "tau-lang-qns-ba" / "build-Release" / "tau"

sys.path.insert(0, str(ROOT / "scripts"))
from generate_eml_regression_certificate_manifest import (  # noqa: E402
    CERT_BITS,
    REQUIRED_MASK,
    bit,
    mask_names,
    sha256_file,
    tau_check,
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def current_source_hashes(manifest: dict[str, Any]) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for source in manifest["source_artifacts"].values():
        path = ROOT / source["path"]
        hashes[source["path"]] = sha256_file(path)
    return hashes


def verify_row(row: dict[str, Any], hashes: dict[str, str], tau_bin: str, timeout_s: float) -> dict[str, Any]:
    expected_hash = hashes.get(row["source_artifact"])
    hash_ok = expected_hash is not None and row["source_sha256"] == expected_hash
    tau = tau_check(tau_bin, int(row["accepted_mask"]), int(row["review_mask"]), timeout_s)
    accepted_mask = int(row["accepted_mask"])
    missing_required = REQUIRED_MASK & (REQUIRED_MASK ^ (accepted_mask & REQUIRED_MASK))
    review_blocked = int(row["review_mask"]) != 0
    promoted = hash_ok and tau["promoted"]
    return {
        "hash_ok": hash_ok,
        "missing_required_mask": missing_required,
        "missing_required_atoms": mask_names(missing_required),
        "review_blocked": review_blocked,
        "tau_check": tau,
        "promoted": promoted,
        "reject_reason": None
        if promoted
        else (
            "stale_source_hash"
            if not hash_ok
            else "tau_missing_required_or_review_blocked"
        ),
    }


def tamper_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tampered: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        for bit_name in ("proof_receipt", "residual_certificate"):
            modified = copy.deepcopy(row)
            modified["tamper_kind"] = f"drop_{bit_name}"
            modified["source_index"] = index
            modified["accepted_mask"] = int(modified["accepted_mask"]) & ~bit(bit_name)
            tampered.append(modified)
        modified = copy.deepcopy(row)
        modified["tamper_kind"] = "force_review_required"
        modified["source_index"] = index
        modified["review_mask"] = int(modified["review_mask"]) | bit("review_required")
        tampered.append(modified)
        modified = copy.deepcopy(row)
        modified["tamper_kind"] = "stale_source_hash"
        modified["source_index"] = index
        modified["source_sha256"] = "0" * 64
        tampered.append(modified)
    return tampered


def main() -> int:
    parser = argparse.ArgumentParser(description="Check fail-closed behavior for EML regression qNS certificates.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--tau-bin", type=Path, default=DEFAULT_QNS_TAU)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--timeout-s", type=float, default=10.0)
    args = parser.parse_args()

    manifest_path = args.manifest if args.manifest.is_absolute() else ROOT / args.manifest
    tau_bin = args.tau_bin if args.tau_bin.is_absolute() else ROOT / args.tau_bin
    if not tau_bin.exists():
        raise SystemExit("patched qNS Tau binary is missing")
    manifest = load_json(manifest_path)
    hashes = current_source_hashes(manifest)
    valid_rows = []
    for row in manifest["rows"]:
        check = verify_row(row, hashes, str(tau_bin), args.timeout_s)
        valid_rows.append({"target": row["target"], "expr": row["expr"], "check": check})
    tampered = []
    for row in tamper_rows(manifest["rows"]):
        check = verify_row(row, hashes, str(tau_bin), args.timeout_s)
        tampered.append(
            {
                "target": row["target"],
                "expr": row["expr"],
                "tamper_kind": row["tamper_kind"],
                "source_index": row["source_index"],
                "check": check,
            }
        )

    artifact = {
        "schema": "eml_regression_certificate_failclosed_v1",
        "generator": "scripts/verify_eml_regression_certificate_failclosed.py",
        "scope": {
            "claim": (
                "The EML regression qNS certificate wrapper promotes valid "
                "rows and rejects rows with missing required bits, review "
                "blockers, or stale source hashes."
            ),
            "not_claimed": [
                "not full symbolic regression",
                "not a cryptographic attestation scheme",
                "not protection against a compromised verifier",
            ],
        },
        "required_mask": REQUIRED_MASK,
        "certificate_bits": CERT_BITS,
        "source_hashes": hashes,
        "summary": {
            "ok": all(row["check"]["promoted"] for row in valid_rows)
            and all(not row["check"]["promoted"] for row in tampered),
            "valid_count": len(valid_rows),
            "valid_promoted_count": sum(1 for row in valid_rows if row["check"]["promoted"]),
            "tampered_count": len(tampered),
            "tampered_rejected_count": sum(1 for row in tampered if not row["check"]["promoted"]),
            "tau_rejected_count": sum(
                1
                for row in tampered
                if row["check"]["reject_reason"] == "tau_missing_required_or_review_blocked"
            ),
            "hash_rejected_count": sum(
                1 for row in tampered if row["check"]["reject_reason"] == "stale_source_hash"
            ),
        },
        "valid_rows": valid_rows,
        "tampered_rows": tampered,
    }
    out = args.out if args.out.is_absolute() else ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "ok": artifact["summary"]["ok"],
                "out": str(out.relative_to(ROOT)),
                "tampered_count": artifact["summary"]["tampered_count"],
            },
            indent=2,
        )
    )
    return 0 if artifact["summary"]["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
