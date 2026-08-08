#!/usr/bin/env python3
"""Validate a proof-carrying Tau coordination plan.

The checker validates bindings and structural safety conditions. It does not
validate the embedded Tau, SAT, confluence, or network-consensus proofs. Those
proof objects need their own independently pinned checkers.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any


HASH_RE = re.compile(r"^[0-9a-f]{64}$")
SCHEMA = "formal-philosophy.tau-coordination-plan.v1"
ALLOWED_PROOF_KINDS = {
    "ACI_SEMILATTICE",
    "BOUNDED_EXHAUSTIVE",
    "CALM_MONOTONICITY",
    "INVARIANT_CONFLUENCE",
    "TERMINATING_CRITICAL_PAIRS",
}
ALLOWED_EVIDENCE_KINDS = {
    "FAST_CONFLUENT",
    "JOINT_UNSAT",
    "ORDER_DEPENDENT",
    "INVARIANT_VIOLATION",
    "UNKNOWN",
}


class PlanError(ValueError):
    """Raised when a coordination plan fails closed."""


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PlanError(message)


def require_keys(value: dict[str, Any], keys: set[str], label: str) -> None:
    require(set(value) == keys, f"{label} keys must be exactly {sorted(keys)}")


def require_hash(value: Any, label: str) -> None:
    require(isinstance(value, str) and HASH_RE.fullmatch(value) is not None,
            f"{label} must be a lowercase SHA-256 digest")


def require_sorted_unique_strings(value: Any, label: str) -> list[str]:
    require(isinstance(value, list) and all(isinstance(x, str) for x in value),
            f"{label} must be a string list")
    require(value == sorted(set(value)), f"{label} must be sorted and unique")
    return value


def path_exists(edges: list[tuple[str, str]], start: str, end: str) -> bool:
    graph: dict[str, list[str]] = defaultdict(list)
    for left, right in edges:
        graph[left].append(right)
    pending = [start]
    seen: set[str] = set()
    while pending:
        node = pending.pop()
        if node == end:
            return True
        if node not in seen:
            seen.add(node)
            pending.extend(graph[node])
    return False


def require_acyclic(nodes: set[str], edges: list[tuple[str, str]]) -> None:
    successors: dict[str, list[str]] = defaultdict(list)
    indegree = {node: 0 for node in nodes}
    for left, right in edges:
        require(left != right, "precedence cannot contain a self-edge")
        successors[left].append(right)
        indegree[right] += 1
    queue = deque(sorted(node for node, degree in indegree.items() if degree == 0))
    visited = 0
    while queue:
        node = queue.popleft()
        visited += 1
        for successor in sorted(successors[node]):
            indegree[successor] -= 1
            if indegree[successor] == 0:
                queue.append(successor)
    require(visited == len(nodes), "precedence relation must be acyclic")


def agreement_subject(plan: dict[str, Any]) -> dict[str, Any]:
    """Return every field that the network agreement digest must bind."""
    return {
        "evidence_root": plan["evidence_root"],
        "proposal_root": plan["proposal_root"],
        "resolution": plan["resolution"],
        "subject": plan["subject"],
    }


def refresh_derived_hashes(plan: dict[str, Any]) -> None:
    """Recompute hashes after a self-test mutation without repairing semantics."""
    plan["proposal_root"] = digest(plan["operations"])
    plan["evidence_root"] = digest(plan["evidence"])
    plan["agreement_input_hash"] = digest(agreement_subject(plan))
    plan_without_hash = copy.deepcopy(plan)
    plan_without_hash.pop("plan_hash")
    plan["plan_hash"] = digest(plan_without_hash)


def validate_evidence(
    evidence: dict[str, Any], operation_ids: set[str], subject: dict[str, Any]
) -> None:
    require_keys(
        evidence,
        {
            "certificate_hash",
            "evidence_id",
            "kind",
            "members",
            "model_hash",
            "proof_kind",
            "scope",
        },
        "evidence item",
    )
    require(isinstance(evidence["evidence_id"], str) and evidence["evidence_id"],
            "evidence_id must be nonempty")
    require(evidence["kind"] in ALLOWED_EVIDENCE_KINDS,
            f"unknown evidence kind {evidence['kind']!r}")
    members = require_sorted_unique_strings(evidence["members"], "evidence.members")
    require(bool(members), "evidence must bind at least one operation")
    require(set(members) <= operation_ids, "evidence names an unknown operation")
    require_hash(evidence["certificate_hash"], "evidence.certificate_hash")
    require(evidence["model_hash"] == subject["model_hash"],
            "evidence model_hash does not match the subject")
    require(isinstance(evidence["scope"], str) and evidence["scope"],
            "evidence scope must be nonempty")

    kind = evidence["kind"]
    proof_kind = evidence["proof_kind"]
    if kind == "FAST_CONFLUENT":
        require(proof_kind in ALLOWED_PROOF_KINDS,
                f"unsupported fast-path proof kind {proof_kind!r}")
        require(len(members) >= 1, "fast certificate needs a member")
    elif kind == "JOINT_UNSAT":
        require(proof_kind in {"PROVED_MINIMAL", "CORE_ONLY", "UNKNOWN"},
                "joint conflict must state its minimality status")
        require(len(members) >= 2, "joint conflict needs at least two members")
    elif kind == "ORDER_DEPENDENT":
        require(proof_kind == "CHECKED_DIVERGENT_DIAMOND",
                "order witness needs CHECKED_DIVERGENT_DIAMOND")
        require(len(members) == 2, "order witness needs exactly two members")
    elif kind == "INVARIANT_VIOLATION":
        require(proof_kind == "CHECKED_INVALID_MERGE",
                "invariant witness needs CHECKED_INVALID_MERGE")
        require(len(members) >= 2, "invariant witness needs at least two members")
    else:
        require(proof_kind in {
            "MISSING_CERTIFICATE",
            "TIMEOUT",
            "UNBOUNDED_REACHABILITY",
            "UNSUPPORTED_FRAGMENT",
        }, "unknown evidence needs an allowed failure reason")


def validate_plan(plan: dict[str, Any]) -> dict[str, Any]:
    require_keys(
        plan,
        {
            "agreement_input_hash",
            "claim_boundary",
            "evidence",
            "evidence_root",
            "operations",
            "plan_hash",
            "proposal_root",
            "resolution",
            "schema",
            "subject",
        },
        "plan",
    )
    require(plan["schema"] == SCHEMA, f"schema must be {SCHEMA}")
    require(isinstance(plan["claim_boundary"], str) and plan["claim_boundary"],
            "claim_boundary must be nonempty")

    subject = plan["subject"]
    require(isinstance(subject, dict), "subject must be an object")
    require_keys(
        subject,
        {
            "delivery_model_hash",
            "fault_profile_hash",
            "invariant_hash",
            "model_hash",
            "pre_state_hash",
            "reachable_scope_hash",
            "resolver_policy_hash",
            "resource_budget_hash",
            "tau_semantics_hash",
            "transition_system_hash",
        },
        "subject",
    )
    for key, value in subject.items():
        require_hash(value, f"subject.{key}")

    operations = plan["operations"]
    require(isinstance(operations, list) and operations, "operations must be nonempty")
    operation_keys = {"class_hash", "operation_id", "payload_hash"}
    operation_ids: list[str] = []
    for operation in operations:
        require(isinstance(operation, dict), "operation must be an object")
        require_keys(operation, operation_keys, "operation")
        operation_id = operation["operation_id"]
        require(isinstance(operation_id, str) and operation_id,
                "operation_id must be nonempty")
        require_hash(operation["class_hash"], "operation.class_hash")
        require_hash(operation["payload_hash"], "operation.payload_hash")
        operation_ids.append(operation_id)
    require(operation_ids == sorted(set(operation_ids)),
            "operations must be sorted by unique operation_id")
    operation_set = set(operation_ids)
    require(plan["proposal_root"] == digest(operations), "proposal_root mismatch")

    evidence_items = plan["evidence"]
    require(isinstance(evidence_items, list) and evidence_items,
            "evidence must be nonempty")
    evidence_by_id: dict[str, dict[str, Any]] = {}
    for item in evidence_items:
        require(isinstance(item, dict), "evidence item must be an object")
        validate_evidence(item, operation_set, subject)
        evidence_id = item["evidence_id"]
        require(evidence_id not in evidence_by_id, "duplicate evidence_id")
        evidence_by_id[evidence_id] = item
    require([item["evidence_id"] for item in evidence_items]
            == sorted(evidence_by_id), "evidence must be sorted by evidence_id")
    require(plan["evidence_root"] == digest(evidence_items), "evidence_root mismatch")

    resolution = plan["resolution"]
    require(isinstance(resolution, dict), "resolution must be an object")
    require_keys(
        resolution,
        {
            "admitted",
            "excluded",
            "precedence",
            "quarantined",
            "slow_justifications",
        },
        "resolution",
    )
    admitted = set(require_sorted_unique_strings(resolution["admitted"],
                                                  "resolution.admitted"))

    def validate_dispositions(label: str) -> tuple[set[str], dict[str, list[str]]]:
        records = resolution[label]
        require(isinstance(records, list), f"resolution.{label} must be a list")
        ids: list[str] = []
        refs: dict[str, list[str]] = {}
        for record in records:
            require(isinstance(record, dict), f"{label} record must be an object")
            require_keys(record, {"evidence_ids", "operation_id", "reason"},
                         f"{label} record")
            operation_id = record["operation_id"]
            require(isinstance(operation_id, str), f"{label}.operation_id invalid")
            evidence_ids = require_sorted_unique_strings(record["evidence_ids"],
                                                          f"{label}.evidence_ids")
            require(bool(evidence_ids), f"{label} record needs evidence")
            require(set(evidence_ids) <= set(evidence_by_id),
                    f"{label} record references unknown evidence")
            require(isinstance(record["reason"], str) and record["reason"],
                    f"{label}.reason must be nonempty")
            ids.append(operation_id)
            refs[operation_id] = evidence_ids
        require(ids == sorted(set(ids)), f"resolution.{label} must be sorted and unique")
        return set(ids), refs

    excluded, excluded_refs = validate_dispositions("excluded")
    quarantined, quarantined_refs = validate_dispositions("quarantined")
    require(admitted.isdisjoint(excluded | quarantined), "dispositions overlap")
    require(excluded.isdisjoint(quarantined), "dispositions overlap")
    require(admitted | excluded | quarantined == operation_set,
            "every operation must have exactly one disposition")

    precedence_records = resolution["precedence"]
    require(isinstance(precedence_records, list), "precedence must be a list")
    precedence: list[tuple[str, str]] = []
    precedence_evidence: dict[frozenset[str], set[str]] = defaultdict(set)
    precedence_sort_keys: list[tuple[str, str, str]] = []
    for record in precedence_records:
        require(isinstance(record, dict), "precedence record must be an object")
        require_keys(record, {"after", "before", "evidence_id", "reason"},
                     "precedence record")
        before, after = record["before"], record["after"]
        require(before in admitted and after in admitted,
                "precedence endpoints must both be admitted")
        evidence_id = record["evidence_id"]
        require(evidence_id in evidence_by_id, "precedence references unknown evidence")
        require(evidence_by_id[evidence_id]["kind"] == "ORDER_DEPENDENT",
                "precedence must cite ORDER_DEPENDENT evidence")
        require({before, after} == set(evidence_by_id[evidence_id]["members"]),
                "precedence endpoints do not match the order witness")
        require(isinstance(record["reason"], str) and record["reason"],
                "precedence reason must be nonempty")
        precedence.append((before, after))
        precedence_evidence[frozenset((before, after))].add(evidence_id)
        precedence_sort_keys.append((before, after, evidence_id))
    require(precedence_sort_keys == sorted(set(precedence_sort_keys)),
            "precedence records must be sorted and unique")
    require_acyclic(admitted, precedence)

    fast_operations: set[str] = set()
    joint_conflicts: list[set[str]] = []
    invariant_violations: list[set[str]] = []
    for item in evidence_items:
        members = set(item["members"])
        if item["kind"] == "FAST_CONFLUENT":
            fast_operations |= members
        elif item["kind"] == "JOINT_UNSAT":
            joint_conflicts.append(members)
            require(not members <= admitted,
                    f"admitted set contains joint conflict {item['evidence_id']}")
        elif item["kind"] == "INVARIANT_VIOLATION":
            invariant_violations.append(members)
            require(not members <= admitted,
                    f"admitted set contains invariant violation {item['evidence_id']}")
        elif item["kind"] == "ORDER_DEPENDENT" and members <= admitted:
            left, right = sorted(members)
            require(path_exists(precedence, left, right)
                    or path_exists(precedence, right, left),
                    f"admitted order-dependent pair lacks precedence: {left}, {right}")
        elif item["kind"] == "UNKNOWN":
            require(members <= quarantined,
                    "operations with UNKNOWN evidence must be quarantined")

    for operation_id, evidence_ids in excluded_refs.items():
        require(operation_id in operation_set, "excluded operation is unknown")
        require(any(
            evidence_by_id[eid]["kind"] in {"JOINT_UNSAT", "INVARIANT_VIOLATION"}
            and operation_id in evidence_by_id[eid]["members"]
            for eid in evidence_ids
        ), "excluded operation lacks applicable conflict evidence")
    for operation_id, evidence_ids in quarantined_refs.items():
        require(operation_id in operation_set, "quarantined operation is unknown")
        require(any(
            evidence_by_id[eid]["kind"] == "UNKNOWN"
            and operation_id in evidence_by_id[eid]["members"]
            for eid in evidence_ids
        ), "quarantined operation lacks UNKNOWN evidence")

    slow_records = resolution["slow_justifications"]
    require(isinstance(slow_records, list), "slow_justifications must be a list")
    slow_ids: list[str] = []
    for record in slow_records:
        require(isinstance(record, dict), "slow justification must be an object")
        require_keys(record, {"evidence_ids", "operation_id", "reason"},
                     "slow justification")
        operation_id = record["operation_id"]
        require(operation_id in admitted, "slow justification must name an admitted operation")
        evidence_ids = require_sorted_unique_strings(record["evidence_ids"],
                                                      "slow_justification.evidence_ids")
        require(bool(evidence_ids) and set(evidence_ids) <= set(evidence_by_id),
                "slow justification references unknown evidence")
        require(all(operation_id in evidence_by_id[eid]["members"] for eid in evidence_ids),
                "slow justification evidence must bind its operation")
        require(all(evidence_by_id[eid]["kind"] != "UNKNOWN" for eid in evidence_ids),
                "UNKNOWN evidence cannot justify admission")
        require(isinstance(record["reason"], str) and record["reason"],
                "slow justification reason must be nonempty")
        slow_ids.append(operation_id)
    require(slow_ids == sorted(set(slow_ids)),
            "slow justifications must be sorted and unique")
    require(admitted <= fast_operations | set(slow_ids),
            "every admitted operation needs fast evidence or a slow justification")
    require(not (quarantined & fast_operations),
            "a fast-certified operation cannot be quarantined in the same plan")

    require(plan["agreement_input_hash"] == digest(agreement_subject(plan)),
            "agreement_input_hash mismatch")

    plan_without_hash = copy.deepcopy(plan)
    plan_without_hash.pop("plan_hash")
    require(plan["plan_hash"] == digest(plan_without_hash), "plan_hash mismatch")

    return {
        "schema": "formal-philosophy.tau-coordination-plan-check.v1",
        "plan_hash": plan["plan_hash"],
        "agreement_input_hash": plan["agreement_input_hash"],
        "operation_count": len(operation_ids),
        "admitted_count": len(admitted),
        "excluded_count": len(excluded),
        "quarantined_count": len(quarantined),
        "joint_conflict_count": len(joint_conflicts),
        "invariant_violation_count": len(invariant_violations),
        "precedence_edge_count": len(precedence),
        "passed": True,
        "claim_boundary": (
            "PASS establishes structural integrity, complete disposition, hash binding, "
            "acyclic precedence, and resolution of the declared conflicts. It does not "
            "validate the embedded semantic certificates or a network protocol."
        ),
    }


def mutation_tests(plan: dict[str, Any]) -> dict[str, bool]:
    def rejected(mutator: Any, *, refresh_hashes: bool = True) -> bool:
        candidate = copy.deepcopy(plan)
        mutator(candidate)
        if refresh_hashes:
            refresh_derived_hashes(candidate)
        try:
            validate_plan(candidate)
        except PlanError:
            return True
        return False

    def add_invariant_violation(candidate: dict[str, Any]) -> None:
        candidate["evidence"].append({
            "certificate_hash": digest("adversarial-invariant-violation"),
            "evidence_id": "invariant-fast-ab",
            "kind": "INVARIANT_VIOLATION",
            "members": ["fast-a", "fast-b"],
            "model_hash": candidate["subject"]["model_hash"],
            "proof_kind": "CHECKED_INVALID_MERGE",
            "scope": "adversarial-self-test",
        })
        candidate["evidence"].sort(key=lambda item: item["evidence_id"])

    def mutate_evidence_without_agreement(candidate: dict[str, Any]) -> None:
        candidate["evidence"][0]["certificate_hash"] = digest(
            "changed-evidence-certificate"
        )
        candidate["evidence_root"] = digest(candidate["evidence"])
        plan_without_hash = copy.deepcopy(candidate)
        plan_without_hash.pop("plan_hash")
        candidate["plan_hash"] = digest(plan_without_hash)

    tests = {
        "changed_model_binding_rejected": rejected(
            lambda p: p["subject"].__setitem__("model_hash", "0" * 64)
        ),
        "cyclic_precedence_rejected": rejected(
            lambda p: p["resolution"]["precedence"].append({
                "after": "order-a",
                "before": "order-b",
                "evidence_id": "order-ab",
                "reason": "adversarial reverse edge",
            })
        ),
        "joint_conflict_admitted_rejected": rejected(
            lambda p: (
                p["resolution"]["admitted"].append("core-a"),
                p["resolution"]["admitted"].sort(),
                p["resolution"].__setitem__(
                    "excluded",
                    [x for x in p["resolution"]["excluded"]
                     if x["operation_id"] != "core-a"],
                ),
            )
        ),
        "invariant_violation_admitted_rejected": rejected(
            add_invariant_violation
        ),
        "unknown_admitted_rejected": rejected(
            lambda p: (
                p["resolution"]["admitted"].append("unknown-x"),
                p["resolution"]["admitted"].sort(),
                p["resolution"].__setitem__("quarantined", []),
            )
        ),
        "unbound_operation_rejected": rejected(
            lambda p: p["resolution"]["admitted"].remove("fast-b")
        ),
        "changed_evidence_binding_rejected": rejected(
            mutate_evidence_without_agreement,
            refresh_hashes=False,
        ),
        "stale_plan_hash_rejected": rejected(
            lambda p: p.__setitem__(
                "claim_boundary", "mutated after plan hashing"
            ),
            refresh_hashes=False,
        ),
    }
    return tests


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "plan",
        nargs="?",
        type=Path,
        default=Path("examples/tau_coordination_boundary/coordination_plan_v1.json"),
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
        result = validate_plan(plan)
        if args.self_test:
            tests = mutation_tests(plan)
            result["mutation_tests"] = tests
            result["passed"] = result["passed"] and all(tests.values())
    except (OSError, json.JSONDecodeError, PlanError) as error:
        result = {
            "schema": "formal-philosophy.tau-coordination-plan-check.v1",
            "passed": False,
            "error": str(error),
        }

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Tau coordination plan: {'PASS' if result['passed'] else 'FAIL'}")
        if not result["passed"]:
            print(result.get("error", "mutation test failed"))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
