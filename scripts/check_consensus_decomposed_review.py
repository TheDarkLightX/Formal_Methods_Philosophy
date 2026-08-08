#!/usr/bin/env python3
"""Replay the Tau peer-review addendum and check its declared results."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


EXPECTED_RE = re.compile(r"^# EXPECTED-RESULTS:\s+([TF ]+)$", re.MULTILINE)
EXPECTED_CODES_RE = re.compile(
    r"^# EXPECTED-CODES:\s+([0-9, ]+)$", re.MULTILINE
)
RESULT_RE = re.compile(r"%\d+:\s*([TF])\b")
CODE_RE = re.compile(r"o0res\[[0-9]+\]\s*:=\s*([0-9]+)")
ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
REVIEWED_SOURCE_SHA256 = (
    "869e4cba2f553afd67b0d7ba87e945e6d4826f1d6ab9055176af8c964bec6f5e"
)
REVIEW_SUBJECT = {
    "commit": "4baf38cbad096fdbe7c41c46e4b41d35c9ba44d2",
    "repository": "taumorrow/tau-lang-demos",
    "source": "consensus_decomposed.tau",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tau",
        default="tau",
        help="Tau executable to invoke (default: tau)",
    )
    parser.add_argument(
        "--spec",
        type=Path,
        default=Path("examples/tau/consensus_decomposed_review_addendum_v1.tau"),
        help="Tau addendum to replay",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print a machine-readable receipt",
    )
    return parser.parse_args()


def public_spec_label(path: Path) -> str:
    """Return a replay label without exposing a machine-local directory."""
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.name


def tau_version(tau: str) -> str | None:
    try:
        completed = subprocess.run(
            [tau, "-v"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    except FileNotFoundError:
        return None
    version = ANSI_RE.sub("", completed.stdout).strip()
    return version or None


def main() -> int:
    args = parse_args()
    source = args.spec.read_text(encoding="utf-8")
    expected_match = EXPECTED_RE.search(source)
    if expected_match is None:
        raise SystemExit("missing EXPECTED-RESULTS declaration")

    expected = expected_match.group(1).split()
    expected_codes_match = EXPECTED_CODES_RE.search(source)
    expected_codes = (
        [code.strip() for code in expected_codes_match.group(1).split(",")]
        if expected_codes_match is not None
        else []
    )

    try:
        completed = subprocess.run(
            [args.tau, "-q"],
            input=source,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    except FileNotFoundError:
        completed = subprocess.CompletedProcess(
            args=[args.tau, "-q"],
            returncode=127,
            stdout=f"Tau executable not found: {Path(args.tau).name}\n",
        )

    plain_output = ANSI_RE.sub("", completed.stdout)
    actual = RESULT_RE.findall(plain_output)
    actual_codes = CODE_RE.findall(plain_output)
    codes_passed = not expected_codes or actual_codes == expected_codes
    passed = completed.returncode == 0 and actual == expected and codes_passed
    spec_sha256 = hashlib.sha256(source.encode("utf-8")).hexdigest()
    review_subject = dict(REVIEW_SUBJECT)
    if spec_sha256 == REVIEWED_SOURCE_SHA256:
        review_subject["source_sha256"] = REVIEWED_SOURCE_SHA256
    claim_boundary = (
        "This receipt checks the declared Tau normalizations and temporal "
        "verdict codes only. It is not evidence of a complete distributed "
        "protocol."
        if expected_codes
        else "This receipt checks the declared Tau normalizations only. It is "
        "not evidence of a complete distributed protocol."
    )

    receipt = {
        "schema": "formal-philosophy.tau-peer-review-replay.v2",
        "spec": public_spec_label(args.spec),
        "spec_sha256": spec_sha256,
        "review_subject": review_subject,
        "tau_binary_name": Path(args.tau).name,
        "tau_version_output": tau_version(args.tau),
        "expected": expected,
        "actual": actual,
        "expected_codes": expected_codes,
        "actual_codes": actual_codes,
        "tau_exit_code": completed.returncode,
        "passed": passed,
        "claim_boundary": claim_boundary,
    }

    if args.json:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        print(f"Tau review addendum: {'PASS' if passed else 'FAIL'}")
        print(f"Expected {len(expected)} results; observed {len(actual)}")
        if expected_codes:
            print(
                f"Expected {len(expected_codes)} codes; "
                f"observed {len(actual_codes)}"
            )
        if not passed:
            print(json.dumps(receipt, indent=2, sort_keys=True))
            print("\nTau output:\n", completed.stdout)

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
