"""Independent release oracle for the synthetic deontic corpus.

This module intentionally does not import the corpus generator, its template
loader, its canonicalizer, or its candidate evaluator.  It duplicates the
small finite semantics and registries so generator agreement is a comparison
between implementations rather than a call back into generation code.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

RECORD_SCHEMA = "synthetic-deontic-decision-v1"
MANIFEST_SCHEMA = "synthetic-deontic-corpus-manifest-v1"
PROFILE_ID = "sdk1-bounded-four-valued-deontic-fixtures-v1"
EXPECTED_RECORD_COUNT = 65_536
SHARD_PREFIXES = tuple("0123456789abcdef")
AXIS_NAMES = (
    "domain",
    "norm_graph",
    "premise_truth",
    "time",
    "priority",
    "exception",
    "revision",
)
AXIS_SIZES = (8, 8, 4, 8, 4, 4, 2)
PREMISE_VALUES = ("true", "false", "unknown", "both")
TIME_VALUES = (
    "atemporal",
    "before_window",
    "at_deadline_unperformed",
    "at_deadline_performed",
    "after_deadline_unperformed",
    "after_deadline_performed",
    "unknown_clock",
    "contradictory_clock",
)
PRIORITY_VALUES = ("equal_rank", "n0_gt_n1", "n1_gt_n0", "cyclic_priority")
EXCEPTION_VALUES = ("absent", "supported_true", "supported_false", "unknown_support")
REVISION_VALUES = ("active", "revoked")
NONCLAIMS = (
    "not_complete_deontic_logic",
    "not_ethics",
    "not_external_authority",
    "not_law",
    "not_population_frequency",
    "not_world_truth",
)
TOP_LEVEL_FIELDS = {
    "schema",
    "ordinal",
    "coordinate_id",
    "coordinate",
    "stable_id",
    "semantic_signature_sha256",
    "generator_profile_sha256",
    "authority",
    "semantic_core",
    "generator_candidate_result",
    "negative_knowledge",
    "kernel_v1_projection",
    "nonclaims",
    "record_sha256",
}


DOMAIN_REGISTRY: dict[str, dict[str, object]] = {
    "resource_allocation": {
        "actors": ("affected_requester", "allocator", "resource_owner"),
        "actions": {
            "primary": ("allocate_capacity", "allocator", "resource_change"),
            "safe": ("retain_reserve", "resource_owner", "safe_fallback"),
            "repair": ("reclaim_allocation", "allocator", "reparation"),
            "review": ("quota_review", "resource_owner", "review"),
        },
        "relation": ("capacity_exclusive", "primary", "safe"),
        "predicate": "request_is_eligible",
    },
    "safety_hazard_control": {
        "actors": ("exposed_party", "safety_authority", "safety_controller"),
        "actions": {
            "primary": ("activate_system", "safety_controller", "state_change"),
            "safe": ("enter_safe_state", "safety_controller", "safe_fallback"),
            "repair": ("recover_and_inspect", "safety_controller", "reparation"),
            "review": ("hazard_review", "safety_authority", "review"),
        },
        "relation": ("hazard_entails", "primary", "safe"),
        "predicate": "hazard_controls_verified",
    },
    "privacy_disclosure": {
        "actors": ("data_steward", "data_subject", "privacy_authority"),
        "actions": {
            "primary": ("disclose_record", "data_steward", "disclosure"),
            "safe": ("redact_or_deny", "data_steward", "safe_fallback"),
            "repair": ("revoke_and_notify", "data_steward", "reparation"),
            "review": ("privacy_review", "privacy_authority", "review"),
        },
        "relation": ("disclosure_conflict", "primary", "safe"),
        "predicate": "disclosure_basis_verified",
    },
    "governance_enactment": {
        "actors": ("constituency", "governance_authority", "proposal_operator"),
        "actions": {
            "primary": ("enact_proposal", "proposal_operator", "governance_change"),
            "safe": ("defer_for_vote", "governance_authority", "safe_fallback"),
            "repair": ("repeal_and_restore", "governance_authority", "reparation"),
            "review": ("governance_review", "governance_authority", "review"),
        },
        "relation": ("quorum_gate", "primary", "safe"),
        "predicate": "quorum_evidence_verified",
    },
    "evidence_publication": {
        "actors": ("evidence_consumer", "researcher", "review_authority"),
        "actions": {
            "primary": ("publish_claim", "researcher", "publication"),
            "safe": ("withhold_and_annotate", "researcher", "safe_fallback"),
            "repair": ("retract_and_correct", "researcher", "reparation"),
            "review": ("evidence_review", "review_authority", "review"),
        },
        "relation": ("evidence_dependency", "primary", "safe"),
        "predicate": "claim_evidence_verified",
    },
    "integrity_commit": {
        "actors": ("commit_worker", "integrity_authority", "state_consumer"),
        "actions": {
            "primary": ("commit_state", "commit_worker", "state_change"),
            "safe": ("serialize_or_retry", "commit_worker", "safe_fallback"),
            "repair": ("rollback_commit", "commit_worker", "reparation"),
            "review": ("integrity_review", "integrity_authority", "review"),
        },
        "relation": ("integrity_gate", "primary", "safe"),
        "predicate": "commit_preconditions_verified",
    },
    "coordination_assignment": {
        "actors": ("assignment_worker", "coordination_authority", "peer_worker"),
        "actions": {
            "primary": ("assign_task", "assignment_worker", "delegation"),
            "safe": ("coordinate_before_assigning", "peer_worker", "safe_fallback"),
            "repair": ("revoke_and_reassign", "assignment_worker", "reparation"),
            "review": ("coordination_review", "coordination_authority", "review"),
        },
        "relation": ("lease_exclusive", "primary", "safe"),
        "predicate": "assignment_scope_verified",
    },
    "workflow_transition": {
        "actors": ("downstream_worker", "workflow_authority", "workflow_worker"),
        "actions": {
            "primary": ("advance_workflow", "workflow_worker", "state_change"),
            "safe": ("pause_for_predecessor", "workflow_worker", "safe_fallback"),
            "repair": ("compensate_transition", "workflow_worker", "reparation"),
            "review": ("workflow_review", "workflow_authority", "review"),
        },
        "relation": ("predecessor_order", "primary", "safe"),
        "predicate": "predecessor_receipt_verified",
    },
}
DOMAIN_VALUES = tuple(DOMAIN_REGISTRY)
GRAPH_VALUES = (
    "obligation_with_safe_permission",
    "primary_prohibition_safe_permission",
    "dual_permission",
    "coherent_obligation_permission",
    "same_action_obligation_prohibition",
    "exclusive_dual_obligation",
    "deadline_with_repair",
    "repair_obligation_prohibition",
)


class OracleError(ValueError):
    """A corpus record or manifest failed an independent release gate."""


class _DuplicateKeyError(ValueError):
    pass


def _pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKeyError(key)
        result[key] = value
    return result


def _strict_json(payload: bytes, label: str) -> object:
    try:
        text = payload.decode("ascii")
        return json.loads(
            text,
            object_pairs_hook=_pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                OracleError(f"{label}: non-finite token {token}")
            ),
        )
    except (UnicodeError, json.JSONDecodeError, _DuplicateKeyError) as exc:
        raise OracleError(f"{label}: invalid strict JSON: {exc}") from exc


def _cjson(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _exact_fields(value: object, expected: set[str], path: str) -> dict[str, Any]:
    if type(value) is not dict:
        raise OracleError(f"{path}: expected object")
    actual = set(value)
    if actual != expected:
        raise OracleError(
            f"{path}: fields mismatch missing={sorted(expected-actual)} "
            f"extra={sorted(actual-expected)}"
        )
    return value


def _hex64(value: object, path: str) -> str:
    if type(value) is not str or len(value) != 64 or any(
        character not in "0123456789abcdef" for character in value
    ):
        raise OracleError(f"{path}: expected lowercase SHA-256")
    return value


def _truth(value: object, path: str) -> str:
    if value not in {"T", "F", "U", "B"}:
        raise OracleError(f"{path}: invalid four-valued truth code")
    return str(value)


def _rank(coordinate: Sequence[int]) -> int:
    result = 0
    for value, size in zip(coordinate, AXIS_SIZES):
        result = result * size + value
    return result


def _priority_path(edges: set[tuple[str, str]], source: str, target: str) -> bool:
    pending = [source]
    visited: set[str] = set()
    while pending:
        node = pending.pop()
        if node == target:
            return True
        if node in visited:
            continue
        visited.add(node)
        pending.extend(b for a, b in edges if a == node)
    return False


def _condition_value(norm: Mapping[str, Any], facts: Mapping[str, str], violated: set[str]) -> str:
    condition = norm["condition"]
    if condition["kind"] == "fact":
        return facts[condition["fact_id"]]
    if condition["kind"] == "violation":
        return "T" if condition["norm_id"] in violated else "F"
    raise OracleError("record.semantic_core.norms.condition: unsupported kind")


def oracle_result(core: Mapping[str, Any]) -> dict[str, object]:
    """Evaluate the named finite semantics without generator code."""

    world = core["world"]
    fact_truth = {item["id"]: item["truth"] for item in world["facts"]}
    norm_map = {item["id"]: item for item in core["norms"]}
    clock = world["clock"]
    active: set[str] = set()
    defeated: set[str] = set()
    satisfied: set[str] = set()
    violated: set[str] = set()
    repairs: set[str] = set()
    codes: set[str] = set()

    def process(norm: Mapping[str, Any]) -> None:
        identifier = norm["id"]
        if norm["revision"]["status"] == "revoked":
            defeated.add(identifier)
            codes.add("revoked_norm_ignored")
            return
        value = _condition_value(norm, fact_truth, violated)
        if value == "F":
            defeated.add(identifier)
            return
        if value == "U":
            codes.add("unknown_norm_condition")
            return
        if value == "B":
            codes.add("inconsistent_norm_condition")
            return
        exception = norm["exception"]
        if exception["kind"] == "unless":
            exception_value = fact_truth[exception["fact_id"]]
            if exception_value == "T":
                defeated.add(identifier)
                codes.add("supported_exception_defeats_norm")
                return
            if exception_value == "U":
                codes.add("unknown_exception_support")
                return
            if exception_value == "B":
                codes.add("inconsistent_exception_support")
                return
        temporal = norm["temporal"]
        if temporal["kind"] == "deadline":
            clock_value = clock["observation_truth"]
            if clock_value == "U":
                codes.add("unknown_clock")
                return
            if clock_value == "B":
                codes.add("contradictory_clock")
                return
            performed = fact_truth["fact_primary_performed"]
            deadline_reached = clock["now_tick"] >= clock["deadline_tick"]
            if performed == "T" and deadline_reached:
                satisfied.add(identifier)
                codes.add("deadline_obligation_satisfied")
                return
            if performed == "F" and deadline_reached and norm["operator"] == "O":
                violated.add(identifier)
                codes.add("deadline_obligation_violated")
        active.add(identifier)
        if norm["repair"]["kind"] == "ctd":
            repairs.add(identifier)
            codes.add("ctd_repair_activated")

    for norm_id in sorted(norm_map):
        norm = norm_map[norm_id]
        if norm["condition"]["kind"] == "fact":
            process(norm)
    for norm_id in sorted(norm_map):
        norm = norm_map[norm_id]
        if norm["condition"]["kind"] == "violation":
            process(norm)

    priority_edges = {tuple(edge) for edge in core["priority_edges"]}
    for left, right, _kind in core["norm_conflicts"]:
        if not {left, right} <= active:
            continue
        left_over_right = _priority_path(priority_edges, left, right)
        right_over_left = _priority_path(priority_edges, right, left)
        if left_over_right != right_over_left:
            loser = right if left_over_right else left
            active.remove(loser)
            defeated.add(loser)
            codes.add("priority_defeat")
        else:
            codes.add("unresolved_norm_conflict")

    obligations = {
        norm_map[norm_id]["action_id"]
        for norm_id in active
        if norm_map[norm_id]["operator"] == "O"
    }
    prohibitions = {
        norm_map[norm_id]["action_id"]
        for norm_id in active
        if norm_map[norm_id]["operator"] == "F"
    }
    permissions = obligations | {
        norm_map[norm_id]["action_id"]
        for norm_id in active
        if norm_map[norm_id]["operator"] == "P"
    }
    if obligations & prohibitions or permissions & prohibitions:
        codes.add("unresolved_modal_conflict")
    if len(obligations) > 1:
        codes.add("multiple_exclusive_obligations")
    blockers = {
        "contradictory_clock",
        "inconsistent_exception_support",
        "inconsistent_norm_condition",
        "multiple_exclusive_obligations",
        "unknown_clock",
        "unknown_exception_support",
        "unknown_norm_condition",
        "unresolved_modal_conflict",
        "unresolved_norm_conflict",
    }
    if blockers & codes:
        status, fallback = "unresolved", "escalate"
    elif obligations or permissions - prohibitions:
        status, fallback = "resolved", "none"
    else:
        status, fallback = "unresolved", "abstain"
        codes.add("no_positive_norm")
    return {
        "status": status,
        "required_action_ids": sorted(obligations),
        "forbidden_action_ids": sorted(prohibitions),
        "permitted_action_ids": sorted(permissions - prohibitions),
        "active_norm_ids": sorted(active),
        "defeated_norm_ids": sorted(defeated),
        "satisfied_norm_ids": sorted(satisfied),
        "violated_norm_ids": sorted(violated),
        "activated_ctd_norm_ids": sorted(repairs),
        "fallback": fallback,
        "reason_codes": sorted(codes),
    }


def _derive_domain(world: Mapping[str, Any]) -> tuple[str, dict[str, str]]:
    domain_id = world.get("domain_id")
    if domain_id not in DOMAIN_REGISTRY:
        raise OracleError("record.semantic_core.world.domain_id: unknown domain")
    expected = DOMAIN_REGISTRY[str(domain_id)]
    if tuple(world.get("actors", [])) != expected["actors"]:
        raise OracleError("record.semantic_core.world.actors: registry mismatch")
    actions = world.get("actions")
    if type(actions) is not list or len(actions) != 4:
        raise OracleError("record.semantic_core.world.actions: expected four actions")
    if actions != sorted(actions, key=lambda row: row.get("id", "")):
        raise OracleError("record.semantic_core.world.actions: noncanonical order")
    role_to_id: dict[str, str] = {}
    expected_actions = expected["actions"]
    for row in actions:
        action = _exact_fields(row, {"role", "id", "actor_id", "kind"}, "action")
        role = action["role"]
        if role not in expected_actions:
            raise OracleError("record.semantic_core.world.actions: unknown role")
        identifier, actor, kind = expected_actions[role]
        if (action["id"], action["actor_id"], action["kind"]) != (
            identifier,
            actor,
            kind,
        ):
            raise OracleError("record.semantic_core.world.actions: registry mismatch")
        role_to_id[str(role)] = str(identifier)
    if set(role_to_id) != {"primary", "safe", "repair", "review"}:
        raise OracleError("record.semantic_core.world.actions: role coverage mismatch")
    relations = world.get("relations")
    relation_kind, source_role, target_role = expected["relation"]
    expected_relation = [
        {
            "id": "relation_domain",
            "kind": relation_kind,
            "source_action_id": role_to_id[source_role],
            "target_action_id": role_to_id[target_role],
        }
    ]
    if relations != expected_relation:
        raise OracleError("record.semantic_core.world.relations: registry mismatch")
    return str(domain_id), role_to_id


def _derive_graph(core: Mapping[str, Any], role_to_id: Mapping[str, str]) -> str:
    reverse_role = {identifier: role for role, identifier in role_to_id.items()}
    signature = []
    for norm in core["norms"]:
        condition = norm["condition"]
        condition_code = (
            "premise"
            if condition == {"kind": "fact", "fact_id": "fact_premise"}
            else "violation:n0"
            if condition == {"kind": "violation", "norm_id": "norm_n0"}
            else None
        )
        repair = norm["repair"]
        repair_code = (
            "none"
            if repair == {"kind": "none"}
            else "ctd:n0"
            if repair == {"kind": "ctd", "primary_norm_id": "norm_n0"}
            else None
        )
        temporal = norm["temporal"]
        temporal_code = (
            "atemporal"
            if temporal == {"kind": "atemporal"}
            else "deadline"
            if temporal == {"kind": "deadline", "clock_id": "clock0"}
            else None
        )
        action_role = reverse_role.get(norm["action_id"])
        if None in {condition_code, repair_code, temporal_code, action_role}:
            raise OracleError("record.semantic_core.norms: unsupported graph form")
        signature.append(
            (
                norm["id"],
                norm["operator"],
                action_role,
                condition_code,
                temporal_code,
                repair_code,
            )
        )
    signatures: dict[tuple[tuple[object, ...], ...], str] = {
        (
            ("norm_n0", "O", "primary", "premise", "atemporal", "none"),
            ("norm_n1", "P", "safe", "premise", "atemporal", "none"),
        ): GRAPH_VALUES[0],
        (
            ("norm_n0", "F", "primary", "premise", "atemporal", "none"),
            ("norm_n1", "P", "safe", "premise", "atemporal", "none"),
        ): GRAPH_VALUES[1],
        (
            ("norm_n0", "P", "primary", "premise", "atemporal", "none"),
            ("norm_n1", "P", "safe", "premise", "atemporal", "none"),
        ): GRAPH_VALUES[2],
        (
            ("norm_n0", "O", "primary", "premise", "atemporal", "none"),
            ("norm_n1", "P", "primary", "premise", "atemporal", "none"),
        ): GRAPH_VALUES[3],
        (
            ("norm_n0", "O", "primary", "premise", "atemporal", "none"),
            ("norm_n1", "F", "primary", "premise", "atemporal", "none"),
        ): GRAPH_VALUES[4],
        (
            ("norm_n0", "O", "primary", "premise", "atemporal", "none"),
            ("norm_n1", "O", "safe", "premise", "atemporal", "none"),
        ): GRAPH_VALUES[5],
        (
            ("norm_n0", "O", "primary", "premise", "deadline", "none"),
            ("norm_n1", "O", "repair", "violation:n0", "atemporal", "ctd:n0"),
        ): GRAPH_VALUES[6],
        (
            ("norm_n0", "O", "primary", "premise", "deadline", "none"),
            ("norm_n1", "O", "repair", "violation:n0", "atemporal", "ctd:n0"),
            ("norm_n2", "F", "repair", "violation:n0", "atemporal", "none"),
        ): GRAPH_VALUES[7],
    }
    key = tuple(signature)
    try:
        graph = signatures[key]
    except KeyError as exc:
        raise OracleError("record.semantic_core.norms: graph does not match registry") from exc
    expected_conflicts = {
        GRAPH_VALUES[4]: [["norm_n0", "norm_n1", "same_action"]],
        GRAPH_VALUES[5]: [["norm_n0", "norm_n1", "exclusive_actions"]],
        GRAPH_VALUES[7]: [["norm_n1", "norm_n2", "same_action"]],
    }.get(graph, [])
    if core["norm_conflicts"] != expected_conflicts:
        raise OracleError("record.semantic_core.norm_conflicts: graph mismatch")
    return graph


def _derive_premise(world: Mapping[str, Any], domain_id: str) -> str:
    facts = world.get("facts")
    if type(facts) is not list or len(facts) != 3:
        raise OracleError("record.semantic_core.world.facts: expected three facts")
    if facts != sorted(facts, key=lambda row: row.get("id", "")):
        raise OracleError("record.semantic_core.world.facts: noncanonical order")
    fact_map = {row.get("id"): row for row in facts if type(row) is dict}
    if set(fact_map) != {"fact_exception", "fact_premise", "fact_primary_performed"}:
        raise OracleError("record.semantic_core.world.facts: ID mismatch")
    premise = _exact_fields(
        fact_map["fact_premise"],
        {"id", "predicate", "args", "truth", "evidence_id"},
        "fact_premise",
    )
    if premise["predicate"] != DOMAIN_REGISTRY[domain_id]["predicate"]:
        raise OracleError("record.semantic_core.world.facts: premise predicate mismatch")
    code = _truth(premise["truth"], "fact_premise.truth")
    return {"T": "true", "F": "false", "U": "unknown", "B": "both"}[code]


def _derive_time(world: Mapping[str, Any]) -> str:
    clock = _exact_fields(
        world.get("clock"),
        {"id", "mode", "now_tick", "deadline_tick", "performance", "observation_truth"},
        "clock",
    )
    if clock["id"] != "clock0":
        raise OracleError("clock.id mismatch")
    if type(clock["now_tick"]) is not int or type(clock["deadline_tick"]) is not int:
        raise OracleError("clock tick must be an integer, not bool")
    observed = _truth(clock["observation_truth"], "clock.observation_truth")
    key = (clock["now_tick"], clock["deadline_tick"], clock["performance"], observed)
    states = {
        (0, 0, "not_applicable", "T"): "atemporal",
        (0, 2, "unperformed", "T"): "before_window",
        (2, 2, "unperformed", "T"): "at_deadline_unperformed",
        (2, 2, "performed", "T"): "at_deadline_performed",
        (3, 2, "unperformed", "T"): "after_deadline_unperformed",
        (3, 2, "performed", "T"): "after_deadline_performed",
        (0, 2, "unknown", "U"): "unknown_clock",
        (2, 2, "both", "B"): "contradictory_clock",
    }
    if key not in states or clock["mode"] != states[key]:
        raise OracleError("clock fields do not derive the declared time mode")
    performed_fact = next(
        row for row in world["facts"] if row["id"] == "fact_primary_performed"
    )
    expected_truth = {
        "not_applicable": "U",
        "unperformed": "F",
        "performed": "T",
        "unknown": "U",
        "both": "B",
    }[clock["performance"]]
    if performed_fact["truth"] != expected_truth:
        raise OracleError("performance fact and clock disagree")
    return states[key]


def _derive_priority(core: Mapping[str, Any]) -> str:
    norms = core["norms"]
    count = len(norms)
    if any(type(norm.get("priority")) is not int for norm in norms):
        raise OracleError("norm priority must be an integer, not bool")
    priorities = [norm["priority"] for norm in norms]
    edges = core["priority_edges"]
    # Construct the variable-length rows explicitly to avoid trusting labels.
    rows = {
        "equal_rank": ([1] * count, []),
        "n0_gt_n1": (
            [2, 1] + ([2] if count == 3 else []),
            [["norm_n0", "norm_n1"]]
            + ([["norm_n2", "norm_n1"]] if count == 3 else []),
        ),
        "n1_gt_n0": (
            [1, 2] + ([1] if count == 3 else []),
            [["norm_n1", "norm_n0"]]
            + ([["norm_n1", "norm_n2"]] if count == 3 else []),
        ),
        "cyclic_priority": (
            [1] * count,
            [["norm_n0", "norm_n1"], ["norm_n1", "norm_n0"]]
            + (
                [["norm_n1", "norm_n2"], ["norm_n2", "norm_n1"]]
                if count == 3
                else []
            ),
        ),
    }
    matches = [name for name, value in rows.items() if value == (priorities, edges)]
    if len(matches) != 1:
        raise OracleError("norm priorities and edges do not derive one priority mode")
    return matches[0]


def _derive_exception(core: Mapping[str, Any]) -> str:
    norm_n1 = next(norm for norm in core["norms"] if norm["id"] == "norm_n1")
    fact = next(row for row in core["world"]["facts"] if row["id"] == "fact_exception")
    truth = _truth(fact["truth"], "fact_exception.truth")
    exception = norm_n1["exception"]
    if exception == {"kind": "none"} and truth == "F":
        return "absent"
    if exception != {"kind": "unless", "fact_id": "fact_exception"}:
        raise OracleError("norm_n1 exception does not match the bounded form")
    try:
        return {"T": "supported_true", "F": "supported_false", "U": "unknown_support"}[
            truth
        ]
    except KeyError as exc:
        raise OracleError("inconsistent exception evidence is outside the lattice") from exc


def _derive_revision(core: Mapping[str, Any]) -> str:
    norm_n0 = next(norm for norm in core["norms"] if norm["id"] == "norm_n0")
    status = norm_n0["revision"]["status"]
    if status not in REVISION_VALUES:
        raise OracleError("norm_n0 revision is outside the lattice")
    for norm in core["norms"]:
        if type(norm["revision"].get("number")) is not int or norm["revision"].get(
            "number"
        ) != 1:
            raise OracleError("norm revision number mismatch")
        if norm["id"] != "norm_n0" and norm["revision"].get("status") != "active":
            raise OracleError("only norm_n0 may vary revision status")
    return str(status)


def _derive_coordinate(record: Mapping[str, Any]) -> tuple[dict[str, str], int, str]:
    core = _exact_fields(
        record["semantic_core"],
        {"profile_id", "world", "norms", "norm_conflicts", "priority_edges", "query"},
        "record.semantic_core",
    )
    if core["profile_id"] != PROFILE_ID:
        raise OracleError("record.semantic_core.profile_id mismatch")
    world = _exact_fields(
        core["world"],
        {"domain_id", "actors", "actions", "relations", "facts", "clock"},
        "record.semantic_core.world",
    )
    domain, roles = _derive_domain(world)
    graph = _derive_graph(core, roles)
    premise = _derive_premise(world, domain)
    time = _derive_time(world)
    priority = _derive_priority(core)
    exception = _derive_exception(core)
    revision = _derive_revision(core)
    derived = {
        "domain": domain,
        "norm_graph": graph,
        "premise_truth": premise,
        "time": time,
        "priority": priority,
        "exception": exception,
        "revision": revision,
    }
    indices = (
        DOMAIN_VALUES.index(domain),
        GRAPH_VALUES.index(graph),
        PREMISE_VALUES.index(premise),
        TIME_VALUES.index(time),
        PRIORITY_VALUES.index(priority),
        EXCEPTION_VALUES.index(exception),
        REVISION_VALUES.index(revision),
    )
    ordinal = _rank(indices)
    return derived, ordinal, graph


def _expected_kernel_projection(
    coordinate: Mapping[str, str], graph: str
) -> dict[str, object]:
    reasons: list[str] = []
    if graph in {GRAPH_VALUES[6], GRAPH_VALUES[7]}:
        reasons.append("ctd_or_deadline_semantics_unsupported")
    if coordinate["priority"] != "equal_rank":
        reasons.append("priority_semantics_metadata_only")
    if coordinate["exception"] != "absent":
        reasons.append("exception_semantics_metadata_only")
    if coordinate["revision"] != "active":
        reasons.append("revision_semantics_unsupported")
    if coordinate["premise_truth"] == "both":
        reasons.append("four_valued_inconsistency_unsupported")
    return {
        "status": "exact_supported" if not reasons else "unsupported_quarantine",
        "reason_codes": reasons or ["bounded_kernel_projection_available"],
    }


def _expected_negative(
    record: Mapping[str, Any], result: Mapping[str, Any]
) -> dict[str, object]:
    action_ids = set(record["semantic_core"]["query"]["alternatives"])
    eligible = set(result["required_action_ids"]) | set(result["permitted_action_ids"])
    return {
        "rejected_action_ids": sorted(action_ids - eligible),
        "unresolved_codes": sorted(
            code
            for code in result["reason_codes"]
            if "unknown" in code
            or "inconsistent" in code
            or "unresolved" in code
            or "multiple" in code
        ),
        "counterfactuals": [
            {
                "mutation": "cycle_premise_truth",
                "expected_delta": "condition_or_quarantine_may_change",
            },
            {
                "mutation": "advance_clock_state",
                "expected_delta": "deadline_or_violation_may_change",
            },
            {
                "mutation": "swap_n0_n1_priority",
                "expected_delta": "conflict_winner_or_quarantine_may_change",
            },
            {
                "mutation": "toggle_n1_exception_support",
                "expected_delta": "n1_activity_or_quarantine_may_change",
            },
        ],
    }


def validate_record(record: object, shard_prefix: str | None = None) -> dict[str, object]:
    value = _exact_fields(record, TOP_LEVEL_FIELDS, "record")
    if value["schema"] != RECORD_SCHEMA:
        raise OracleError("record.schema mismatch")
    ordinal = value["ordinal"]
    if type(ordinal) is not int or not 0 <= ordinal < EXPECTED_RECORD_COUNT:
        raise OracleError("record.ordinal must be uint16, not bool")
    if value["coordinate_id"] != f"sdkv0-{ordinal:04x}":
        raise OracleError("record.coordinate_id mismatch")
    signature = _hex64(value["semantic_signature_sha256"], "semantic signature")
    if value["stable_id"] != f"sdk1-{signature}":
        raise OracleError("record.stable_id mismatch")
    _hex64(value["generator_profile_sha256"], "generator profile")
    authority = _exact_fields(
        value["authority"],
        {
            "status",
            "source_kind",
            "issuer_id",
            "jurisdiction_id",
            "truth_status",
            "may_authorize_external_effects",
            "may_be_cited_as_law",
        },
        "record.authority",
    )
    if authority["may_authorize_external_effects"] is not False or authority[
        "may_be_cited_as_law"
    ] is not False:
        raise OracleError("record.authority Boolean boundary mismatch")
    if authority != {
        "status": "synthetic_non_authoritative",
        "source_kind": "generated_fixture",
        "issuer_id": "none",
        "jurisdiction_id": "none",
        "truth_status": "not_asserted",
        "may_authorize_external_effects": False,
        "may_be_cited_as_law": False,
    }:
        raise OracleError("record.authority may not claim real authority")
    if value["nonclaims"] != list(NONCLAIMS):
        raise OracleError("record.nonclaims mismatch")
    core = value["semantic_core"]
    recomputed_signature = _sha(_cjson(core))
    if signature != recomputed_signature:
        raise OracleError("record semantic signature mismatch")
    if shard_prefix is not None and signature[0] != shard_prefix:
        raise OracleError("record is in the wrong semantic-hash shard")
    derived, derived_ordinal, graph = _derive_coordinate(value)
    if value["coordinate"] != derived or ordinal != derived_ordinal:
        raise OracleError("record coordinate is not derivable from semantic IR")
    query = core["query"]
    action_ids = sorted(row["id"] for row in core["world"]["actions"])
    if query.get("omission_admissible") is not False or query != {
        "decision_id": f"decision_{derived['domain']}_{derived['norm_graph']}",
        "alternatives": action_ids,
        "omission_admissible": False,
        "fallback": "abstain_or_escalate",
    }:
        raise OracleError("record.semantic_core.query mismatch")
    actor_ids = set(core["world"]["actors"])
    action_id_set = set(action_ids)
    fact_ids = {row["id"] for row in core["world"]["facts"]}
    norm_ids = {row["id"] for row in core["norms"]}
    if len(norm_ids) != len(core["norms"]):
        raise OracleError("duplicate norm ID")
    if core["norms"] != sorted(core["norms"], key=lambda row: row["id"]):
        raise OracleError("norm order is not canonical")
    for norm in core["norms"]:
        _exact_fields(
            norm,
            {
                "id",
                "operator",
                "subject_id",
                "action_id",
                "condition",
                "temporal",
                "priority",
                "exception",
                "repair",
                "revision",
            },
            "norm",
        )
        if norm["operator"] not in {"O", "F", "P"}:
            raise OracleError("norm operator mismatch")
        if norm["subject_id"] not in actor_ids or norm["action_id"] not in action_id_set:
            raise OracleError("unresolved norm actor or action reference")
        condition = norm["condition"]
        if condition["kind"] == "fact" and condition.get("fact_id") not in fact_ids:
            raise OracleError("unresolved norm fact reference")
        if condition["kind"] == "violation" and condition.get("norm_id") not in norm_ids:
            raise OracleError("unresolved violation norm reference")
        exception = norm["exception"]
        if exception["kind"] == "unless" and exception.get("fact_id") not in fact_ids:
            raise OracleError("unresolved exception fact reference")
        repair = norm["repair"]
        if repair["kind"] == "ctd" and repair.get("primary_norm_id") not in norm_ids:
            raise OracleError("unresolved CTD norm reference")
    for left, right, _kind in core["norm_conflicts"]:
        if left not in norm_ids or right not in norm_ids:
            raise OracleError("unresolved conflict norm reference")
    for left, right in core["priority_edges"]:
        if left not in norm_ids or right not in norm_ids or left == right:
            raise OracleError("invalid priority edge")
    result = oracle_result(core)
    if value["generator_candidate_result"] != result:
        raise OracleError("generator candidate result disagrees with independent oracle")
    if value["kernel_v1_projection"] != _expected_kernel_projection(derived, graph):
        raise OracleError("kernel projection label mismatch")
    if value["negative_knowledge"] != _expected_negative(value, result):
        raise OracleError("negative-knowledge projection mismatch")
    without_record_hash = dict(value)
    supplied_record_hash = _hex64(
        without_record_hash.pop("record_sha256"), "record hash"
    )
    if supplied_record_hash != _sha(_cjson(without_record_hash)):
        raise OracleError("record SHA-256 mismatch")
    return {
        "ordinal": ordinal,
        "record_sha256": supplied_record_hash,
        "semantic_signature_sha256": signature,
        "generator_profile_sha256": value["generator_profile_sha256"],
        "coordinate": derived,
        "outcome": result["status"],
        "fallback": result["fallback"],
        "kernel_projection": value["kernel_v1_projection"]["status"],
        "negative_count": len(value["negative_knowledge"]["rejected_action_ids"])
        + len(value["negative_knowledge"]["unresolved_codes"]),
    }


def _load_manifest(path: Path) -> dict[str, Any]:
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise OracleError(f"manifest read failed: {exc}") from exc
    value = _strict_json(payload, "manifest")
    if type(value) is not dict or _cjson(value) != payload:
        raise OracleError("manifest is not canonical JSON")
    _exact_fields(
        value,
        {
            "schema",
            "status",
            "authoritative_status",
            "record_schema",
            "record_count",
            "factorization",
            "hashes",
            "coverage",
            "sharding",
            "compression",
            "nonclaims",
        },
        "manifest",
    )
    if value.get("schema") != MANIFEST_SCHEMA:
        raise OracleError("manifest schema mismatch")
    if value.get("status") != "generation_only_pending_independent_oracle":
        raise OracleError("manifest generation status mismatch")
    if value.get("authoritative_status") != "synthetic_non_authoritative":
        raise OracleError("manifest authority boundary mismatch")
    if value.get("record_schema") != RECORD_SCHEMA:
        raise OracleError("manifest record schema mismatch")
    if value.get("nonclaims") != list(NONCLAIMS):
        raise OracleError("manifest nonclaims mismatch")
    if value.get("factorization") != {
        "axis_names": list(AXIS_NAMES),
        "axis_sizes": list(AXIS_SIZES),
        "product": EXPECTED_RECORD_COUNT,
    }:
        raise OracleError("manifest factorization mismatch")
    hashes = _exact_fields(
        value.get("hashes"),
        {
            "template_bank_sha256",
            "generator_source_sha256",
            "generator_profile_sha256",
            "corpus_root_sha256",
            "semantic_set_root_sha256",
        },
        "manifest.hashes",
    )
    for name, digest in hashes.items():
        _hex64(digest, f"manifest.hashes.{name}")
    sharding = _exact_fields(
        value.get("sharding"), {"method", "shard_count", "shards"}, "manifest.sharding"
    )
    if sharding["method"] != "first_hex_of_full_semantic_signature":
        raise OracleError("manifest sharding method mismatch")
    if type(sharding["shard_count"]) is not int or sharding["shard_count"] != 16:
        raise OracleError("manifest shard count mismatch")
    compression = _exact_fields(
        value.get("compression"),
        {"format", "compresslevel", "mtime", "filename_header", "python", "zlib"},
        "manifest.compression",
    )
    if (
        compression["format"] != "gzip"
        or type(compression["compresslevel"]) is not int
        or compression["compresslevel"] != 9
        or type(compression["mtime"]) is not int
        or compression["mtime"] != 0
        or compression["filename_header"] != "empty"
    ):
        raise OracleError("manifest compression profile mismatch")
    return value


def verify_corpus(corpus_dir: Path, manifest_path: Path) -> dict[str, object]:
    manifest = _load_manifest(manifest_path)
    errors: list[str] = []
    ordinal_rows: list[list[object]] = []
    signatures: set[str] = set()
    stable_ids: set[str] = set()
    ordinals: set[int] = set()
    coverage = {name: Counter() for name in AXIS_NAMES}
    outcomes = Counter()
    fallbacks = Counter()
    projections = Counter()
    negative_items = 0
    checked = 0
    manifest_shards = manifest.get("sharding", {}).get("shards", [])
    if type(manifest_shards) is not list:
        raise OracleError("manifest shard list missing")
    if len(manifest_shards) != len(SHARD_PREFIXES):
        raise OracleError("manifest must contain exactly 16 shard rows")
    shard_fields = {
        "prefix",
        "file",
        "records",
        "uncompressed_bytes",
        "uncompressed_sha256",
        "compressed_bytes",
        "compressed_sha256",
    }
    for index, row in enumerate(manifest_shards):
        _exact_fields(row, shard_fields, f"manifest.sharding.shards[{index}]")
    shard_by_prefix = {
        row.get("prefix"): row for row in manifest_shards if type(row) is dict
    }
    if set(shard_by_prefix) != set(SHARD_PREFIXES):
        raise OracleError("manifest must bind exactly 16 shards")
    for prefix in SHARD_PREFIXES:
        row = shard_by_prefix[prefix]
        if row.get("file") != f"part-{prefix}.jsonl.gz":
            errors.append(f"shard {prefix}: file name mismatch")
            continue
        path = corpus_dir / row["file"]
        try:
            compressed_sha = _file_sha(path)
            compressed_bytes = path.stat().st_size
        except OSError as exc:
            errors.append(f"shard {prefix}: read failed: {exc}")
            continue
        if compressed_sha != row.get("compressed_sha256"):
            errors.append(f"shard {prefix}: compressed SHA-256 mismatch")
        if compressed_bytes != row.get("compressed_bytes"):
            errors.append(f"shard {prefix}: compressed byte count mismatch")
        raw_hasher = hashlib.sha256()
        raw_bytes = 0
        shard_records = 0
        try:
            with gzip.open(path, "rb") as handle:
                for line_number, line in enumerate(handle, 1):
                    raw_hasher.update(line)
                    raw_bytes += len(line)
                    if not line.endswith(b"\n") or line == b"\n":
                        raise OracleError(
                            f"shard {prefix} line {line_number}: invalid JSONL framing"
                        )
                    payload = line[:-1]
                    record = _strict_json(payload, f"shard {prefix} line {line_number}")
                    if _cjson(record) != payload:
                        raise OracleError(
                            f"shard {prefix} line {line_number}: noncanonical JSON"
                        )
                    summary = validate_record(record, prefix)
                    if summary["generator_profile_sha256"] != manifest["hashes"][
                        "generator_profile_sha256"
                    ]:
                        raise OracleError(
                            "record generator profile hash disagrees with manifest"
                        )
                    ordinal = int(summary["ordinal"])
                    signature = str(summary["semantic_signature_sha256"])
                    stable_id = str(record["stable_id"])
                    if ordinal in ordinals:
                        raise OracleError(f"duplicate ordinal {ordinal}")
                    if signature in signatures or stable_id in stable_ids:
                        raise OracleError("duplicate semantic signature or stable ID")
                    ordinals.add(ordinal)
                    signatures.add(signature)
                    stable_ids.add(stable_id)
                    ordinal_rows.append([ordinal, summary["record_sha256"]])
                    for name in AXIS_NAMES:
                        coverage[name][summary["coordinate"][name]] += 1
                    outcomes[str(summary["outcome"])] += 1
                    fallbacks[str(summary["fallback"])] += 1
                    projections[str(summary["kernel_projection"])] += 1
                    negative_items += int(summary["negative_count"])
                    checked += 1
                    shard_records += 1
        except (OSError, EOFError, gzip.BadGzipFile, OracleError) as exc:
            errors.append(str(exc))
            continue
        if shard_records != row.get("records"):
            errors.append(f"shard {prefix}: record count mismatch")
        if raw_bytes != row.get("uncompressed_bytes"):
            errors.append(f"shard {prefix}: uncompressed byte count mismatch")
        if raw_hasher.hexdigest() != row.get("uncompressed_sha256"):
            errors.append(f"shard {prefix}: uncompressed SHA-256 mismatch")
    ordinal_rows.sort(key=lambda item: item[0])
    corpus_root = _sha(_cjson(ordinal_rows))
    semantic_root = _sha(
        b"".join(bytes.fromhex(signature) for signature in sorted(signatures))
    )
    declared_hashes = manifest.get("hashes", {})
    if corpus_root != declared_hashes.get("corpus_root_sha256"):
        errors.append("corpus root mismatch")
    if semantic_root != declared_hashes.get("semantic_set_root_sha256"):
        errors.append("semantic-set root mismatch")
    expected_ordinals = set(range(EXPECTED_RECORD_COUNT))
    if ordinals != expected_ordinals:
        missing = len(expected_ordinals - ordinals)
        extra = len(ordinals - expected_ordinals)
        errors.append(f"ordinal coverage mismatch: missing={missing} extra={extra}")
    declared_coverage = manifest.get("coverage")
    computed_coverage = {
        name: dict(sorted(counter.items())) for name, counter in coverage.items()
    }
    if declared_coverage != computed_coverage:
        errors.append("manifest coverage disagrees with independently derived coverage")
    if manifest.get("record_count") != EXPECTED_RECORD_COUNT or checked != EXPECTED_RECORD_COUNT:
        errors.append("exact 65,536-record count gate failed")
    passed = not errors
    return {
        "schema": "synthetic-deontic-corpus-verification-v1",
        "passed": passed,
        "promotion_label": (
            "EXHAUSTIVELY_CHECKED_SYNTHETIC_FIXTURE"
            if passed
            else "QUARANTINED_CORPUS"
        ),
        "authoritative_status": "synthetic_non_authoritative",
        "checked_records": checked,
        "unique_ordinals": len(ordinals),
        "unique_stable_ids": len(stable_ids),
        "unique_semantic_signatures": len(signatures),
        "corpus_root_sha256": corpus_root,
        "semantic_set_root_sha256": semantic_root,
        "oracle_source_sha256": _file_sha(Path(__file__)),
        "coverage": computed_coverage,
        "outcome_counts": dict(sorted(outcomes.items())),
        "fallback_counts": dict(sorted(fallbacks.items())),
        "kernel_projection_counts": dict(sorted(projections.items())),
        "negative_knowledge_item_count": negative_items,
        "errors": errors[:100],
        "tool_receipts": {
            "independent_python_oracle": {
                "status": "PASS" if passed else "FAIL",
                "scope": "closed schema, references, hashes, coordinate derivation, finite semantics, coverage, and negative projections",
            },
            "z3_cvc5": {
                "status": "SKIP",
                "scope": "no raw-record SMT translator was executed for this corpus",
            },
            "esso": {
                "status": "SKIP",
                "scope": "no ESSO model was compiled from raw corpus rules",
            },
            "tau_lean_hol": {
                "status": "SKIP",
                "scope": "no Tau, Lean, or HOL proof was executed for this corpus",
            },
        },
        "oracle_boundary": {
            "generator_module_imported": False,
            "generator_candidate_labels_trusted": False,
            "semantic_result_recomputed": True,
            "coordinate_recomputed_from_semantic_ir": True,
        },
        "nonclaims": list(NONCLAIMS),
    }


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(_cjson(value))
    os.replace(temporary, path)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser


def _main(argv: Sequence[str]) -> int:
    args = _parser().parse_args(argv)
    try:
        result = verify_corpus(args.corpus_dir, args.manifest)
        _write_json(args.report, result)
        sys.stdout.buffer.write(_cjson(result) + b"\n")
        return 0 if result["passed"] else 1
    except OracleError as exc:
        sys.stderr.write(f"synthetic_deontic_oracle: {exc}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
