#!/usr/bin/env python3
"""Replay the ADD-only Tau hypergraph example and its Python reference model."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

EXPECTED_RE = re.compile(r"^# EXPECTED-RESULTS:\s+([TF ]+)$", re.MULTILINE)
RESULT_RE = re.compile(r"%\d+:\s*(?:!!)?([TF])\b")
TEST_COUNT_RE = re.compile(r"Ran (\d+) tests?")
PROPOSAL_ROOT_RE = re.compile(
    r"^proposal set root: ([0-9a-f]{64})$", re.MULTILINE
)
RESOLUTION_ROOT_RE = re.compile(
    r"^resolution root: ([0-9a-f]{64})$", re.MULTILINE
)
ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
SCHEMA = "formal-philosophy.tau-semantic-conflict-hypergraph-replay.v1"
EXPECTED_PYTHON_TEST_COUNT = 17
REQUIRED_TEST_NAMES = (
    "test_all_arrival_permutations_have_one_resolution_root",
    "test_conflicting_duplicate_proposal_id_fails_closed",
    "test_manifest_root_binds_payload_cost_and_dependencies",
    "test_rehashed_semantic_certificate_mutation_is_rejected",
    "test_unknown_fails_closed",
    "test_unsupported_policy_and_budget_mismatch_fail_closed",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tau", default="tau", help="Tau executable to invoke")
    parser.add_argument(
        "--spec",
        type=Path,
        default=Path("examples/tau/consensus_hypergraph_v1.tau"),
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=Path(
            "examples/tau_coordination_boundary/"
            "semantic_conflict_hypergraph_v1.py"
        ),
    )
    parser.add_argument(
        "--tests",
        type=Path,
        default=Path(
            "examples/tau_coordination_boundary/"
            "test_semantic_conflict_hypergraph_v1.py"
        ),
    )
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def public_label(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.name


def run_tau(tau: str, source: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            [tau],
            input=source,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    except FileNotFoundError:
        return subprocess.CompletedProcess(
            args=[tau],
            returncode=127,
            stdout=f"Tau executable not found: {Path(tau).name}\n",
        )


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


def run_python_artifacts(
    model: Path, tests: Path
) -> tuple[subprocess.CompletedProcess[str], subprocess.CompletedProcess[str]]:
    demo = subprocess.run(
        [sys.executable, model.name],
        cwd=model.parent,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    unit_tests = subprocess.run(
        [sys.executable, "-m", "unittest", "-v", tests.name],
        cwd=tests.parent,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return demo, unit_tests


def main() -> int:
    args = parse_args()
    source = args.spec.read_text(encoding="utf-8")
    expected_match = EXPECTED_RE.search(source)
    if expected_match is None:
        raise SystemExit("missing EXPECTED-RESULTS declaration")
    expected = expected_match.group(1).split()

    tau_run = run_tau(args.tau, source)
    tau_output = ANSI_RE.sub("", tau_run.stdout)
    actual = RESULT_RE.findall(tau_output)
    demo_run, test_run = run_python_artifacts(args.model, args.tests)
    count_match = TEST_COUNT_RE.search(test_run.stdout)
    test_count = int(count_match.group(1)) if count_match else 0
    proposal_root_match = PROPOSAL_ROOT_RE.search(demo_run.stdout)
    resolution_root_match = RESOLUTION_ROOT_RE.search(demo_run.stdout)
    proposal_set_root = (
        proposal_root_match.group(1) if proposal_root_match else None
    )
    resolution_root = (
        resolution_root_match.group(1) if resolution_root_match else None
    )
    required_tests_observed = all(
        test_name in test_run.stdout for test_name in REQUIRED_TEST_NAMES
    )

    passed = all(
        (
            tau_run.returncode == 0,
            actual == expected,
            demo_run.returncode == 0,
            "all reference assertions passed" in demo_run.stdout,
            proposal_set_root is not None,
            resolution_root is not None,
            test_run.returncode == 0,
            test_count == EXPECTED_PYTHON_TEST_COUNT,
            required_tests_observed,
        )
    )

    receipt = {
        "schema": SCHEMA,
        "checker": public_label(Path(__file__)),
        "checker_sha256": sha256_file(Path(__file__)),
        "spec": public_label(args.spec),
        "spec_sha256": sha256_file(args.spec),
        "model": public_label(args.model),
        "model_sha256": sha256_file(args.model),
        "tests": public_label(args.tests),
        "tests_sha256": sha256_file(args.tests),
        "tau_binary_name": Path(args.tau).name,
        "tau_version_output": tau_version(args.tau),
        "expected": expected,
        "actual": actual,
        "tau_exit_code": tau_run.returncode,
        "python_demo_passed": demo_run.returncode == 0,
        "python_test_count": test_count,
        "expected_python_test_count": EXPECTED_PYTHON_TEST_COUNT,
        "required_python_tests_observed": required_tests_observed,
        "python_tests_passed": test_run.returncode == 0,
        "proposal_set_root": proposal_set_root,
        "resolution_root": resolution_root,
        "passed": passed,
        "claim_boundary": (
            "PASS reproduces 15 bounded Tau normalizations and validates 17 "
            "Python tests for the finite reference model. Those tests cover "
            "higher-order conflicts, exact small-instance optimization, "
            "dependency closure, all 24 arrival permutations, canonical sealed "
            "proposal roots, subject- and policy-bound resolution certificates, "
            "mutation rejection, and fail-closed UNKNOWN and budget outcomes. "
            "It does not establish a production network protocol, agreement on "
            "the epoch input set, unbounded tractability, or Tau semantic "
            "soundness."
        ),
    }

    if args.json:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        print(f"Tau semantic conflict hypergraph: {'PASS' if passed else 'FAIL'}")
        print(f"Tau values: {len(actual)}/{len(expected)}")
        print(f"Python tests: {test_count} ({'PASS' if test_run.returncode == 0 else 'FAIL'})")
        if not passed:
            print(json.dumps(receipt, indent=2, sort_keys=True))
            print("\nTau output:\n", tau_run.stdout)
            print("\nDemo output:\n", demo_run.stdout)
            print("\nTest output:\n", test_run.stdout)

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
