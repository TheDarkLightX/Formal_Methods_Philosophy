#!/usr/bin/env python3
"""Generate the bounded Synthetic Deontic Luna v1 candidate corpus.

This module owns deterministic expansion of the frozen template bank and a
candidate implementation of its finite semantics.  It does not own a release
verdict.  The independent oracle must decode the raw records without importing
this module and must recompute every release-critical result.

All generated cases are synthetic and non-authoritative.  They are not law,
ethics, world truth, production policy, or permission to cause an external
effect.
"""

from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import io
import json
import os
import platform
import re
import shutil
import sys
import tempfile
import zlib
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

TEMPLATE_SCHEMA = "synthetic-deontic-luna-template-bank-v1"
CASE_SCHEMA = "synthetic-deontic-luna-case-v1"
RESULT_SCHEMA = "synthetic-deontic-luna-result-v1"
MANIFEST_SCHEMA = "synthetic-deontic-luna-corpus-manifest-v1"
PROFILE_ID = "sdk-luna-v1-bounded-causal-four-valued"

EXPECTED_TEMPLATE_SHA256 = (
    "eadfeeb5a464f89a878800d21e84acd2ce8f3844a75cc49234bccde95b16c3c9"
)
EXPECTED_SEMANTICS_SHA256 = (
    "d265a71141d3b5f0291a971c2997d085efe53c91851359f181b0682d7fd6f371"
)
EXPECTED_RECORD_COUNT = 65_536
AXIS_RADICES = (16, 16, 4, 4, 4, 4)
AXIS_NAMES = (
    "domain",
    "topology_program",
    "evidence_value",
    "local_state_variant",
    "resolution_variant",
    "defeater_variant",
)
MODIFIER_AXES = (
    "evidence_value",
    "local_state_variant",
    "resolution_variant",
    "defeater_variant",
)
APPLICATION_TARGET_AXES = ("evidence", "state", "resolution", "defeater")
SHARD_PREFIXES = tuple("0123456789abcdef")
TRUTHS = ("T", "F", "U", "B")
DEADLINE_STATES = (
    "before_deadline_unperformed",
    "deadline_reached_timely_performed",
    "deadline_reached_late_performed",
    "deadline_reached_performance_unknown",
)
NONCLAIMS = (
    "not_complete_deontic_logic",
    "not_ethics",
    "not_external_authority",
    "not_kernel_parity_without_execution",
    "not_law",
    "not_population_frequency",
    "not_production_readiness",
    "not_world_truth",
)
AUTHORITY = {
    "status": "synthetic_non_authoritative",
    "source_kind": "generated_fixture",
    "issuer_id": "none",
    "truth_status": "not_asserted",
    "may_authorize_external_effects": False,
    "may_be_cited_as_law": False,
}
BLOCKER_CODES = frozenset(
    {
        "unknown_condition",
        "inconsistent_condition",
        "unknown_defeater",
        "inconsistent_defeater",
        "unknown_lifecycle",
        "unknown_deadline",
        "unknown_primary_violation",
        "inconsistent_primary_violation",
        "unknown_repair_availability",
        "inconsistent_repair_availability",
        "repair_unavailable",
        "unresolved_priority",
        "relevant_priority_cycle",
        "modal_conflict",
        "single_action_cardinality_conflict",
    }
)
ID_RE = re.compile(r"[a-z][a-z0-9_]{0,63}\Z")
HASH_RE = re.compile(r"[0-9a-f]{64}\Z")
MAX_TEMPLATE_BYTES = 2_000_000

CLOSED_SHAPES = {
    "domain": [
        "id",
        "summary",
        "actor_role_bindings",
        "actors",
        "actions",
        "relations",
        "raw_state_fields",
        "derived_predicates",
        "witness_states",
        "causal_mutations",
    ],
    "actor": ["id", "kind"],
    "action": ["id", "role", "actor_id", "kind"],
    "relation": ["id", "kind", "source_ref", "target_ref"],
    "raw_state_field": ["id", "type", "allowed_values"],
    "derived_predicate": ["id", "slot", "expression", "consumed_by"],
    "witness_state": ["id", "raw_state", "expected_truths"],
    "causal_mutation": [
        "id",
        "from_witness",
        "to_witness",
        "changed_field_ids",
        "expected_truth_delta",
        "disposition_targets",
    ],
    "topology_program": [
        "id",
        "summary",
        "kernel_projection",
        "norms",
        "conflicts",
        "state_variants",
        "resolution_variants",
        "defeater_variants",
        "application_targets",
        "validity_rules",
    ],
    "norm": [
        "id",
        "operator",
        "source_actor_role",
        "action_role",
        "condition_refs",
        "source_id",
        "lifecycle_slot",
        "defeater_slot",
        "repair_for",
    ],
    "conflict": ["id", "left_norm_id", "right_norm_id", "kind"],
    "state_variant": ["code", "id", "domain_witness", "norm_states", "flags"],
    "resolution_variant": ["code", "id", "priority_edges", "expected_if_conflict"],
    "defeater_variant": ["code", "id", "slot_truths", "expected_effect"],
    "counterfactual_contract": [
        "modifier_axes",
        "mutation",
        "unordered_value_pairs",
        "spanning_tree_edges",
        "spanning_applications",
        "required_receipt_fields",
        "behavior_change_classes",
        "unchanged_class",
        "negative_knowledge_rule",
    ],
    "spanning_application": ["axis", "held_codes", "predicate"],
}

TOP_FIELDS = frozenset(
    {
        "schema",
        "profile_id",
        "authoritative_status",
        "generation_method",
        "factorization",
        "closed_shapes",
        "expression_language",
        "evidence_values",
        "variant_codes",
        "domains",
        "topology_programs",
        "counterfactual_contract",
        "nonclaims",
    }
)


class GeneratorReject(ValueError):
    """Typed fail-closed rejection at the generator boundary."""

    def __init__(self, code: str, path: str, detail: str = "") -> None:
        self.code = code
        self.path = path
        self.detail = detail
        message = f"{code} at {path}"
        if detail:
            message += f": {detail}"
        super().__init__(message)


@dataclass(frozen=True)
class TemplateBank:
    data: dict[str, Any]
    sha256: str


def _reject(code: str, path: str, detail: str = "") -> None:
    raise GeneratorReject(code, path, detail)


def _pairs_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _reject("duplicate_json_key", "$", key)
        result[key] = value
    return result


def canonical_json_bytes(value: object) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise GeneratorReject("noncanonical_value", "$", str(exc)) from exc


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_hash(value: object) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as exc:
        raise GeneratorReject("file_read_error", str(path), str(exc)) from exc
    return digest.hexdigest()


def parse_json_exact(raw: bytes, *, max_bytes: int = MAX_TEMPLATE_BYTES) -> Any:
    if len(raw) > max_bytes:
        _reject("resource_limit", "$", f"bytes={len(raw)}")
    try:
        text = raw.decode("ascii")
        return json.loads(
            text,
            object_pairs_hook=_pairs_object,
            parse_constant=lambda token: _reject("nonfinite_number", "$", token),
        )
    except GeneratorReject:
        raise
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise GeneratorReject("invalid_json", "$", str(exc)) from exc


def _object(value: Any, fields: set[str] | frozenset[str], path: str) -> dict[str, Any]:
    if type(value) is not dict:
        _reject("wrong_type", path, "expected object")
    actual = set(value)
    if actual != set(fields):
        _reject(
            "field_set_mismatch",
            path,
            f"missing={sorted(set(fields)-actual)} extra={sorted(actual-set(fields))}",
        )
    return value


def _list(value: Any, path: str) -> list[Any]:
    if type(value) is not list:
        _reject("wrong_type", path, "expected array")
    return value


def _string(value: Any, path: str) -> str:
    if type(value) is not str:
        _reject("wrong_type", path, "expected string")
    return value


def _id(value: Any, path: str, *, allow_none: bool = False) -> str:
    text = _string(value, path)
    if allow_none and text == "none":
        return text
    if ID_RE.fullmatch(text) is None:
        _reject("invalid_id", path, text)
    return text


def _integer(value: Any, path: str, lower: int, upper: int) -> int:
    if type(value) is not int:
        _reject("wrong_type", path, "expected integer")
    if not lower <= value <= upper:
        _reject("integer_out_of_range", path, str(value))
    return value


def _boolean(value: Any, path: str) -> bool:
    if type(value) is not bool:
        _reject("wrong_type", path, "expected Boolean")
    return value


def _enum(value: Any, allowed: set[str] | frozenset[str], path: str) -> str:
    text = _string(value, path)
    if text not in allowed:
        _reject("unknown_enum", path, text)
    return text


def _unique_objects(items: Any, shape: str, path: str) -> dict[str, dict[str, Any]]:
    values = _list(items, path)
    result: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(values):
        item_path = f"{path}[{index}]"
        item = _object(raw, set(CLOSED_SHAPES[shape]), item_path)
        item_id = _id(item["id"], f"{item_path}.id")
        if item_id in result:
            _reject("duplicate_id", f"{item_path}.id", item_id)
        result[item_id] = item
    return result


def _unique_strings(value: Any, path: str, *, nonempty: bool = True) -> list[str]:
    items = _list(value, path)
    result = [_string(item, f"{path}[{index}]") for index, item in enumerate(items)]
    if nonempty and not result:
        _reject("empty_application_set", path)
    if len(set(result)) != len(result):
        _reject("duplicate_value", path)
    return result


def _truth_pair(value: str) -> tuple[bool, bool]:
    return {
        "T": (True, False),
        "F": (False, True),
        "U": (False, False),
        "B": (True, True),
    }[value]


def _pair_truth(value: tuple[bool, bool]) -> str:
    return {
        (True, False): "T",
        (False, True): "F",
        (False, False): "U",
        (True, True): "B",
    }[value]


def truth_not(value: str) -> str:
    positive, negative = _truth_pair(value)
    return _pair_truth((negative, positive))


def truth_all(values: Iterable[str]) -> str:
    pairs = [_truth_pair(value) for value in values]
    if not pairs:
        return "T"
    return _pair_truth((all(p for p, _ in pairs), any(n for _, n in pairs)))


def truth_any(values: Iterable[str]) -> str:
    pairs = [_truth_pair(value) for value in values]
    if not pairs:
        return "F"
    return _pair_truth((any(p for p, _ in pairs), all(n for _, n in pairs)))


def _expression_fields(
    expression: Any,
    fields: Mapping[str, Mapping[str, Any]],
    path: str,
) -> set[str]:
    form = _list(expression, path)
    if not form:
        _reject("empty_expression", path)
    operator = _enum(form[0], {"eq", "all", "any", "not"}, f"{path}[0]")
    if operator == "eq":
        if len(form) != 3:
            _reject("expression_arity", path, "eq")
        field_id = _id(form[1], f"{path}[1]")
        if field_id not in fields:
            _reject("dangling_state_reference", f"{path}[1]", field_id)
        literal = _string(form[2], f"{path}[2]")
        if literal not in fields[field_id]["allowed_values"] or literal in {"unknown", "both"}:
            _reject("invalid_expression_literal", f"{path}[2]", literal)
        return {field_id}
    if operator == "not":
        if len(form) != 2:
            _reject("expression_arity", path, "not")
        return _expression_fields(form[1], fields, f"{path}[1]")
    if len(form) < 3:
        _reject("expression_arity", path, operator)
    used: set[str] = set()
    for index, child in enumerate(form[1:], 1):
        used |= _expression_fields(child, fields, f"{path}[{index}]")
    return used


def evaluate_expression(expression: Any, raw_state: Mapping[str, str]) -> str:
    form = expression
    operator = form[0]
    if operator == "eq":
        actual = raw_state[form[1]]
        if actual == "unknown":
            return "U"
        if actual == "both":
            return "B"
        return "T" if actual == form[2] else "F"
    if operator == "not":
        return truth_not(evaluate_expression(form[1], raw_state))
    values = [evaluate_expression(child, raw_state) for child in form[1:]]
    return truth_all(values) if operator == "all" else truth_any(values)


def _validate_domain(domain: Any, index: int) -> None:
    path = f"$.domains[{index}]"
    item = _object(domain, set(CLOSED_SHAPES["domain"]), path)
    _id(item["id"], f"{path}.id")
    _string(item["summary"], f"{path}.summary")

    bindings = _object(
        item["actor_role_bindings"],
        {"operator", "authority", "affected", "reviewer"},
        f"{path}.actor_role_bindings",
    )
    for role, actor_id in bindings.items():
        _id(role, f"{path}.actor_role_bindings.{role}")
        _id(actor_id, f"{path}.actor_role_bindings.{role}")
    if len(set(bindings.values())) != 4:
        _reject("duplicate_role_binding", f"{path}.actor_role_bindings")

    actors = _unique_objects(item["actors"], "actor", f"{path}.actors")
    if len(actors) != 4 or set(actors) != set(bindings.values()):
        _reject("actor_registry_mismatch", f"{path}.actors")
    for actor_id, actor in actors.items():
        _id(actor["kind"], f"{path}.actors.{actor_id}.kind")

    actions = _unique_objects(item["actions"], "action", f"{path}.actions")
    if len(actions) != 4:
        _reject("wrong_cardinality", f"{path}.actions", str(len(actions)))
    by_role: dict[str, str] = {}
    for action_id, action in actions.items():
        action_path = f"{path}.actions.{action_id}"
        role = _enum(action["role"], {"primary", "safe", "repair", "review"}, f"{action_path}.role")
        if role in by_role:
            _reject("duplicate_action_role", f"{action_path}.role", role)
        by_role[role] = action_id
        if _id(action["actor_id"], f"{action_path}.actor_id") not in actors:
            _reject("dangling_actor_reference", f"{action_path}.actor_id")
        _id(action["kind"], f"{action_path}.kind")
    if set(by_role) != {"primary", "safe", "repair", "review"}:
        _reject("action_role_coverage", f"{path}.actions")

    relations = _unique_objects(item["relations"], "relation", f"{path}.relations")
    if not relations:
        _reject("empty_registry", f"{path}.relations")
    for relation_id, relation in relations.items():
        relation_path = f"{path}.relations.{relation_id}"
        _id(relation["kind"], f"{relation_path}.kind")
        for field in ("source_ref", "target_ref"):
            reference = _string(relation[field], f"{relation_path}.{field}")
            try:
                sort, role = reference.split(":", 1)
            except ValueError:
                _reject("malformed_reference", f"{relation_path}.{field}", reference)
            if (sort == "actor" and role in bindings) or (sort == "action" and role in by_role):
                continue
            _reject("wrong_sort_reference", f"{relation_path}.{field}", reference)

    fields = _unique_objects(item["raw_state_fields"], "raw_state_field", f"{path}.raw_state_fields")
    if not 3 <= len(fields) <= 8:
        _reject("wrong_cardinality", f"{path}.raw_state_fields", str(len(fields)))
    for field_id, field in fields.items():
        field_path = f"{path}.raw_state_fields.{field_id}"
        _id(field["type"], f"{field_path}.type")
        values = _unique_strings(field["allowed_values"], f"{field_path}.allowed_values")
        if len(values) != 4 or "unknown" not in values or "both" not in values:
            _reject("state_value_coverage", f"{field_path}.allowed_values")

    predicates = _unique_objects(item["derived_predicates"], "derived_predicate", f"{path}.derived_predicates")
    if len(predicates) != 2:
        _reject("wrong_cardinality", f"{path}.derived_predicates", str(len(predicates)))
    predicate_by_slot: dict[str, dict[str, Any]] = {}
    used_fields: set[str] = set()
    for predicate_id, predicate in predicates.items():
        predicate_path = f"{path}.derived_predicates.{predicate_id}"
        slot = _enum(predicate["slot"], {"primary_gate", "safe_gate"}, f"{predicate_path}.slot")
        if slot in predicate_by_slot:
            _reject("duplicate_predicate_slot", f"{predicate_path}.slot", slot)
        predicate_by_slot[slot] = predicate
        used_fields |= _expression_fields(predicate["expression"], fields, f"{predicate_path}.expression")
        _unique_strings(predicate["consumed_by"], f"{predicate_path}.consumed_by")
    if set(predicate_by_slot) != {"primary_gate", "safe_gate"}:
        _reject("predicate_slot_coverage", f"{path}.derived_predicates")
    if used_fields != set(fields):
        _reject("dead_raw_state_field", f"{path}.raw_state_fields")

    witnesses = _unique_objects(item["witness_states"], "witness_state", f"{path}.witness_states")
    required_witnesses = {"both_gates_true", "primary_gate_only", "safe_gate_only", "gates_unknown"}
    if set(witnesses) != required_witnesses:
        _reject("witness_coverage", f"{path}.witness_states")
    signatures: set[bytes] = set()
    for witness_id, witness in witnesses.items():
        witness_path = f"{path}.witness_states.{witness_id}"
        raw_state = _object(witness["raw_state"], set(fields), f"{witness_path}.raw_state")
        for field_id, value in raw_state.items():
            _enum(value, set(fields[field_id]["allowed_values"]), f"{witness_path}.raw_state.{field_id}")
        signature = canonical_json_bytes(raw_state)
        if signature in signatures:
            _reject("duplicate_witness_state", f"{witness_path}.raw_state")
        signatures.add(signature)
        expected = _object(witness["expected_truths"], set(predicate_by_slot), f"{witness_path}.expected_truths")
        for slot, predicate in predicate_by_slot.items():
            actual = evaluate_expression(predicate["expression"], raw_state)
            declared = _enum(expected[slot], set(TRUTHS), f"{witness_path}.expected_truths.{slot}")
            if actual != declared:
                _reject("witness_truth_mismatch", f"{witness_path}.expected_truths.{slot}")

    mutations = _unique_objects(item["causal_mutations"], "causal_mutation", f"{path}.causal_mutations")
    if len(mutations) != 2:
        _reject("wrong_cardinality", f"{path}.causal_mutations", str(len(mutations)))
    for mutation_id, mutation in mutations.items():
        mutation_path = f"{path}.causal_mutations.{mutation_id}"
        source = _id(mutation["from_witness"], f"{mutation_path}.from_witness")
        target = _id(mutation["to_witness"], f"{mutation_path}.to_witness")
        if source not in witnesses or target not in witnesses or source == target:
            _reject("dangling_witness_reference", mutation_path)
        changed = _unique_strings(mutation["changed_field_ids"], f"{mutation_path}.changed_field_ids")
        actual_changed = sorted(
            field_id
            for field_id in fields
            if witnesses[source]["raw_state"][field_id] != witnesses[target]["raw_state"][field_id]
        )
        if len(changed) != 1 or sorted(changed) != actual_changed:
            _reject("mutation_delta_mismatch", f"{mutation_path}.changed_field_ids")
        declared_delta = sorted(_unique_strings(mutation["expected_truth_delta"], f"{mutation_path}.expected_truth_delta"))
        actual_delta = sorted(
            f"{slot}:{witnesses[source]['expected_truths'][slot]}_to_{witnesses[target]['expected_truths'][slot]}"
            for slot in predicate_by_slot
            if witnesses[source]["expected_truths"][slot] != witnesses[target]["expected_truths"][slot]
        )
        if declared_delta != actual_delta:
            _reject("truth_delta_mismatch", f"{mutation_path}.expected_truth_delta")
        _unique_strings(mutation["disposition_targets"], f"{mutation_path}.disposition_targets")


def _validate_topology(topology: Any, index: int) -> None:
    path = f"$.topology_programs[{index}]"
    item = _object(topology, set(CLOSED_SHAPES["topology_program"]), path)
    topology_id = _id(item["id"], f"{path}.id")
    _string(item["summary"], f"{path}.summary")
    if item["kernel_projection"] != "unclaimed_without_execution":
        _reject("kernel_claim_boundary", f"{path}.kernel_projection")

    norms = _unique_objects(item["norms"], "norm", f"{path}.norms")
    if len(norms) not in {2, 3}:
        _reject("wrong_cardinality", f"{path}.norms", str(len(norms)))
    lifecycle_slots: set[str] = set()
    defeater_slots: set[str] = set()
    repair_families: dict[str, list[str]] = defaultdict(list)
    evidence_norms: set[str] = set()
    for norm_id, norm in norms.items():
        norm_path = f"{path}.norms.{norm_id}"
        operator = _enum(norm["operator"], {"O", "F", "P"}, f"{norm_path}.operator")
        _enum(norm["source_actor_role"], {"operator", "authority", "affected", "reviewer"}, f"{norm_path}.source_actor_role")
        _enum(norm["action_role"], {"primary", "safe", "repair", "review"}, f"{norm_path}.action_role")
        references = _unique_strings(norm["condition_refs"], f"{norm_path}.condition_refs")
        state_refs = 0
        violation_refs: list[str] = []
        for ref_index, reference in enumerate(references):
            ref_path = f"{norm_path}.condition_refs[{ref_index}]"
            try:
                kind, target = reference.split(":", 1)
            except ValueError:
                _reject("malformed_reference", ref_path, reference)
            if kind == "evidence" and target == "e0":
                evidence_norms.add(norm_id)
            elif kind == "domain" and target in {"primary_gate", "safe_gate"}:
                pass
            elif kind == "state" and target == norm_id:
                state_refs += 1
            elif kind == "violation" and target in norms:
                violation_refs.append(target)
            else:
                _reject("wrong_sort_reference", ref_path, reference)
        if state_refs != 1:
            _reject("state_mirror_mismatch", f"{norm_path}.condition_refs")
        _id(norm["source_id"], f"{norm_path}.source_id")
        lifecycle_slot = _id(norm["lifecycle_slot"], f"{norm_path}.lifecycle_slot")
        lifecycle_slots.add(lifecycle_slot)
        if lifecycle_slot == "deadline0" and operator == "P":
            _reject("unsupported_deadline_operator", f"{norm_path}.operator")
        defeater_slots.add(_id(norm["defeater_slot"], f"{norm_path}.defeater_slot"))
        repair_for = _id(norm["repair_for"], f"{norm_path}.repair_for", allow_none=True)
        if repair_for == "none":
            if violation_refs:
                _reject("violation_on_nonrepair", f"{norm_path}.condition_refs")
        else:
            if repair_for not in norms or repair_for == norm_id or norms[repair_for]["repair_for"] != "none":
                _reject("invalid_repair_reference", f"{norm_path}.repair_for", repair_for)
            if violation_refs != [repair_for]:
                _reject("repair_gate_mismatch", f"{norm_path}.condition_refs")
            repair_families[repair_for].append(norm_id)
    for primary, linked in repair_families.items():
        providers = [norm_id for norm_id in linked if norms[norm_id]["operator"] == "O"]
        if len(providers) > 1:
            _reject("multiple_repair_providers", f"{path}.norms", primary)

    conflicts = _unique_objects(item["conflicts"], "conflict", f"{path}.conflicts")
    if len(conflicts) != 1:
        _reject("wrong_cardinality", f"{path}.conflicts", str(len(conflicts)))
    for conflict_id, conflict in conflicts.items():
        conflict_path = f"{path}.conflicts.{conflict_id}"
        left = _id(conflict["left_norm_id"], f"{conflict_path}.left_norm_id")
        right = _id(conflict["right_norm_id"], f"{conflict_path}.right_norm_id")
        if left not in norms or right not in norms or left == right:
            _reject("dangling_conflict_reference", conflict_path)
        _id(conflict["kind"], f"{conflict_path}.kind")

    states = _unique_objects(item["state_variants"], "state_variant", f"{path}.state_variants")
    if len(states) != 4:
        _reject("wrong_cardinality", f"{path}.state_variants", str(len(states)))
    by_state_code: dict[int, dict[str, Any]] = {}
    for state_id, state in states.items():
        state_path = f"{path}.state_variants.{state_id}"
        code = _integer(state["code"], f"{state_path}.code", 0, 3)
        if code in by_state_code:
            _reject("duplicate_code", f"{state_path}.code", str(code))
        by_state_code[code] = state
        _enum(
            state["domain_witness"],
            {"both_gates_true", "primary_gate_only", "safe_gate_only", "gates_unknown"},
            f"{state_path}.domain_witness",
        )
        norm_states = _object(state["norm_states"], set(norms), f"{state_path}.norm_states")
        for norm_id, value in norm_states.items():
            _enum(value, {"active", "inactive", "satisfied", "violated", "unknown"}, f"{state_path}.norm_states.{norm_id}")
        _unique_strings(state["flags"], f"{state_path}.flags")
    if set(by_state_code) != {0, 1, 2, 3}:
        _reject("variant_code_coverage", f"{path}.state_variants")
    deadline_norms = [norm_id for norm_id, norm in norms.items() if norm["lifecycle_slot"] == "deadline0"]
    if deadline_norms:
        if topology_id != "deadline_obligation_prohibition":
            _reject("deadline_slot_scope", f"{path}.norms")
        for code, expected_id in enumerate(DEADLINE_STATES):
            if by_state_code[code]["id"] != expected_id:
                _reject("deadline_state_mismatch", f"{path}.state_variants", str(code))
            for norm_id in deadline_norms:
                expected = {
                    0: "active",
                    1: "satisfied" if norms[norm_id]["operator"] == "O" else "violated",
                    2: "violated",
                    3: "unknown",
                }[code]
                if by_state_code[code]["norm_states"][norm_id] != expected:
                    _reject("deadline_mirror_mismatch", f"{path}.state_variants", f"{code}/{norm_id}")

    resolutions = _unique_objects(item["resolution_variants"], "resolution_variant", f"{path}.resolution_variants")
    resolution_codes: set[int] = set()
    resolution_signatures: set[bytes] = set()
    for resolution_id, resolution in resolutions.items():
        resolution_path = f"{path}.resolution_variants.{resolution_id}"
        code = _integer(resolution["code"], f"{resolution_path}.code", 0, 3)
        if code in resolution_codes:
            _reject("duplicate_code", f"{resolution_path}.code", str(code))
        resolution_codes.add(code)
        checked_edges: list[list[str]] = []
        for edge_index, edge in enumerate(_list(resolution["priority_edges"], f"{resolution_path}.priority_edges")):
            edge_path = f"{resolution_path}.priority_edges[{edge_index}]"
            pair = _list(edge, edge_path)
            if len(pair) != 2:
                _reject("wrong_cardinality", edge_path, str(len(pair)))
            higher = _id(pair[0], f"{edge_path}[0]")
            lower = _id(pair[1], f"{edge_path}[1]")
            if higher not in norms or lower not in norms or higher == lower:
                _reject("dangling_priority_reference", edge_path)
            checked_edges.append([higher, lower])
        if checked_edges != sorted(checked_edges) or len({tuple(edge) for edge in checked_edges}) != len(checked_edges):
            _reject("noncanonical_order", f"{resolution_path}.priority_edges")
        signature = canonical_json_bytes(checked_edges)
        if signature in resolution_signatures:
            _reject("duplicate_variant_semantics", resolution_path)
        resolution_signatures.add(signature)
        _id(resolution["expected_if_conflict"], f"{resolution_path}.expected_if_conflict")
    if resolution_codes != {0, 1, 2, 3}:
        _reject("variant_code_coverage", f"{path}.resolution_variants")

    defeaters = _unique_objects(item["defeater_variants"], "defeater_variant", f"{path}.defeater_variants")
    defeater_codes: set[int] = set()
    defeater_signatures: set[bytes] = set()
    for defeater_id, defeater in defeaters.items():
        defeater_path = f"{path}.defeater_variants.{defeater_id}"
        code = _integer(defeater["code"], f"{defeater_path}.code", 0, 3)
        if code in defeater_codes:
            _reject("duplicate_code", f"{defeater_path}.code", str(code))
        defeater_codes.add(code)
        slot_truths = defeater["slot_truths"]
        if type(slot_truths) is not dict or not slot_truths or not set(slot_truths) <= defeater_slots:
            _reject("defeater_slot_mismatch", f"{defeater_path}.slot_truths")
        for slot, truth in slot_truths.items():
            _id(slot, f"{defeater_path}.slot_truths.{slot}")
            _enum(truth, set(TRUTHS), f"{defeater_path}.slot_truths.{slot}")
        full = {slot: slot_truths.get(slot, "F") for slot in sorted(defeater_slots)}
        signature = canonical_json_bytes(full)
        if signature in defeater_signatures:
            _reject("duplicate_variant_semantics", defeater_path)
        defeater_signatures.add(signature)
        _id(defeater["expected_effect"], f"{defeater_path}.expected_effect")
    if defeater_codes != {0, 1, 2, 3}:
        _reject("variant_code_coverage", f"{path}.defeater_variants")

    targets = _object(item["application_targets"], set(APPLICATION_TARGET_AXES), f"{path}.application_targets")
    target_values = {
        axis: _unique_strings(targets[axis], f"{path}.application_targets.{axis}")
        for axis in APPLICATION_TARGET_AXES
    }
    if set(target_values["evidence"]) != evidence_norms:
        _reject("evidence_target_mismatch", f"{path}.application_targets.evidence")
    if not set(target_values["state"]) <= lifecycle_slots | set(norms):
        _reject("state_target_mismatch", f"{path}.application_targets.state")
    if not set(target_values["resolution"]) <= set(conflicts):
        _reject("resolution_target_mismatch", f"{path}.application_targets.resolution")
    if not set(target_values["defeater"]) <= defeater_slots:
        _reject("defeater_target_mismatch", f"{path}.application_targets.defeater")
    _unique_strings(item["validity_rules"], f"{path}.validity_rules")


def _validate_counterfactual_contract(value: Any) -> None:
    path = "$.counterfactual_contract"
    contract = _object(value, set(CLOSED_SHAPES["counterfactual_contract"]), path)
    if contract["modifier_axes"] != list(MODIFIER_AXES):
        _reject("modifier_axis_mismatch", f"{path}.modifier_axes")
    _string(contract["mutation"], f"{path}.mutation")
    expected_pairs = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]
    if contract["unordered_value_pairs"] != expected_pairs:
        _reject("unordered_pair_mismatch", f"{path}.unordered_value_pairs")
    if contract["spanning_tree_edges"] != [[0, 1], [0, 2], [0, 3]]:
        _reject("spanning_tree_mismatch", f"{path}.spanning_tree_edges")
    applications = _list(contract["spanning_applications"], f"{path}.spanning_applications")
    if len(applications) != 4:
        _reject("wrong_cardinality", f"{path}.spanning_applications", str(len(applications)))
    seen: set[str] = set()
    for index, raw in enumerate(applications):
        app_path = f"{path}.spanning_applications[{index}]"
        app = _object(raw, set(CLOSED_SHAPES["spanning_application"]), app_path)
        axis = _enum(app["axis"], set(MODIFIER_AXES), f"{app_path}.axis")
        if axis in seen:
            _reject("duplicate_axis_application", f"{app_path}.axis", axis)
        seen.add(axis)
        held = _object(app["held_codes"], set(MODIFIER_AXES) - {axis}, f"{app_path}.held_codes")
        for field, code in held.items():
            _integer(code, f"{app_path}.held_codes.{field}", 0, 3)
        if app["predicate"] != "normalized_results_differ_for_every_declared_edge":
            _reject("unknown_application_predicate", f"{app_path}.predicate")
    _unique_strings(contract["required_receipt_fields"], f"{path}.required_receipt_fields")
    _unique_strings(contract["behavior_change_classes"], f"{path}.behavior_change_classes")
    _id(contract["unchanged_class"], f"{path}.unchanged_class")
    _string(contract["negative_knowledge_rule"], f"{path}.negative_knowledge_rule")


def validate_template_bank(data: Any) -> dict[str, Any]:
    bank = _object(data, TOP_FIELDS, "$")
    if bank["schema"] != TEMPLATE_SCHEMA or bank["profile_id"] != PROFILE_ID:
        _reject("template_profile_mismatch", "$")
    if bank["authoritative_status"] != "synthetic_non_authoritative":
        _reject("authority_boundary_mismatch", "$.authoritative_status")
    _string(bank["generation_method"], "$.generation_method")
    if bank["closed_shapes"] != CLOSED_SHAPES:
        _reject("template_shape_mismatch", "$.closed_shapes")
    if bank["nonclaims"] != list(NONCLAIMS):
        _reject("authority_boundary_mismatch", "$.nonclaims")

    factorization = _object(bank["factorization"], {"formula", "record_count", "ordinal_order", "radices"}, "$.factorization")
    if (
        factorization["formula"] != "16*16*4*4*4*4"
        or factorization["record_count"] != EXPECTED_RECORD_COUNT
        or factorization["ordinal_order"] != list(AXIS_NAMES)
        or factorization["radices"] != list(AXIS_RADICES)
    ):
        _reject("factorization_mismatch", "$.factorization")

    language = _object(
        bank["expression_language"],
        {"truth_values", "operators", "forms", "unknown_rule", "composition_rule"},
        "$.expression_language",
    )
    if language["truth_values"] != list(TRUTHS) or language["operators"] != ["eq", "all", "any", "not"]:
        _reject("expression_language_mismatch", "$.expression_language")
    _object(language["forms"], {"eq", "all", "any", "not"}, "$.expression_language.forms")
    _string(language["unknown_rule"], "$.expression_language.unknown_rule")
    _string(language["composition_rule"], "$.expression_language.composition_rule")

    evidence = _list(bank["evidence_values"], "$.evidence_values")
    expected_evidence = [(0, "supported", "T"), (1, "refuted", "F"), (2, "unknown", "U"), (3, "inconsistent", "B")]
    if len(evidence) != 4:
        _reject("wrong_cardinality", "$.evidence_values", str(len(evidence)))
    for index, (raw, expected) in enumerate(zip(evidence, expected_evidence, strict=True)):
        path = f"$.evidence_values[{index}]"
        item = _object(raw, {"code", "id", "truth", "effect"}, path)
        if (item["code"], item["id"], item["truth"]) != expected:
            _reject("evidence_axis_mismatch", path)
        _id(item["effect"], f"{path}.effect")

    variants = _object(
        bank["variant_codes"],
        {"local_state_variant", "resolution_variant", "defeater_variant"},
        "$.variant_codes",
    )
    if any(codes != [0, 1, 2, 3] for codes in variants.values()):
        _reject("variant_code_mismatch", "$.variant_codes")

    domains = _list(bank["domains"], "$.domains")
    topologies = _list(bank["topology_programs"], "$.topology_programs")
    if len(domains) != 16 or len(topologies) != 16:
        _reject("factorization_mismatch", "$", f"domains={len(domains)} topologies={len(topologies)}")
    for index, domain in enumerate(domains):
        _validate_domain(domain, index)
    for index, topology in enumerate(topologies):
        _validate_topology(topology, index)
    domain_ids = [domain["id"] for domain in domains]
    topology_ids = [topology["id"] for topology in topologies]
    if len(set(domain_ids)) != 16 or len(set(topology_ids)) != 16:
        _reject("duplicate_id", "$", "domain or topology")
    _validate_counterfactual_contract(bank["counterfactual_contract"])
    return bank


def load_template_bank(
    path: Path,
    *,
    expected_sha256: str = EXPECTED_TEMPLATE_SHA256,
) -> TemplateBank:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise GeneratorReject("file_read_error", str(path), str(exc)) from exc
    actual = sha256_bytes(raw)
    if actual != expected_sha256:
        _reject("template_hash_mismatch", str(path), f"expected={expected_sha256} actual={actual}")
    data = validate_template_bank(parse_json_exact(raw))
    return TemplateBank(data=data, sha256=actual)


def rank_coordinate(coordinate: Sequence[int]) -> int:
    if len(coordinate) != len(AXIS_RADICES):
        _reject("coordinate_arity", "coordinate", str(len(coordinate)))
    ordinal = 0
    for index, (code, radix) in enumerate(zip(coordinate, AXIS_RADICES, strict=True)):
        code = _integer(code, f"coordinate[{index}]", 0, radix - 1)
        ordinal = ordinal * radix + code
    return ordinal


def unrank_ordinal(ordinal: int) -> tuple[int, int, int, int, int, int]:
    value = _integer(ordinal, "ordinal", 0, EXPECTED_RECORD_COUNT - 1)
    codes: list[int] = []
    for radix in reversed(AXIS_RADICES):
        value, code = divmod(value, radix)
        codes.append(code)
    if value != 0:
        raise AssertionError("unrank remainder")
    return tuple(reversed(codes))  # type: ignore[return-value]


def _variant_by_code(items: Sequence[dict[str, Any]], code: int) -> dict[str, Any]:
    matches = [item for item in items if item["code"] == code]
    if len(matches) != 1:
        _reject("variant_code_lookup", "template", str(code))
    return matches[0]


def _action_by_role(domain: Mapping[str, Any], role: str) -> dict[str, Any]:
    matches = [action for action in domain["actions"] if action["role"] == role]
    if len(matches) != 1:
        _reject("action_role_lookup", f"domain.{domain['id']}", role)
    return matches[0]


def _predicate_by_slot(domain: Mapping[str, Any], slot: str) -> dict[str, Any]:
    matches = [predicate for predicate in domain["derived_predicates"] if predicate["slot"] == slot]
    if len(matches) != 1:
        _reject("predicate_slot_lookup", f"domain.{domain['id']}", slot)
    return matches[0]


def _resolve_template_ref(domain: Mapping[str, Any], reference: str) -> dict[str, str]:
    sort, role = reference.split(":", 1)
    if sort == "action":
        target = _action_by_role(domain, role)["id"]
    elif sort == "actor":
        target = domain["actor_role_bindings"][role]
    else:
        _reject("wrong_sort_reference", "template.relation", reference)
    return {"kind": sort, "id": target}


def _condition_ref(domain: Mapping[str, Any], reference: str) -> dict[str, str]:
    kind, target = reference.split(":", 1)
    if kind == "domain":
        return {"kind": "fact", "id": _predicate_by_slot(domain, target)["id"]}
    return {"kind": kind, "id": target}


def compile_core(
    template: TemplateBank,
    coordinate: Sequence[int],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Compile one validated coordinate into the closed semantic core."""

    ordinal = rank_coordinate(coordinate)
    domain_code, topology_code, evidence_code, state_code, resolution_code, defeater_code = unrank_ordinal(ordinal)
    bank = template.data
    domain = bank["domains"][domain_code]
    topology = bank["topology_programs"][topology_code]
    evidence_variant = bank["evidence_values"][evidence_code]
    state_variant = _variant_by_code(topology["state_variants"], state_code)
    resolution_variant = _variant_by_code(topology["resolution_variants"], resolution_code)
    defeater_variant = _variant_by_code(topology["defeater_variants"], defeater_code)
    witnesses = {witness["id"]: witness for witness in domain["witness_states"]}
    witness = witnesses[state_variant["domain_witness"]]
    raw_map = witness["raw_state"]

    inverse_roles = {
        actor_id: role for role, actor_id in domain["actor_role_bindings"].items()
    }
    actors = [
        {"id": actor["id"], "role": inverse_roles[actor["id"]], "kind": actor["kind"]}
        for actor in domain["actors"]
    ]
    actors.sort(key=lambda item: item["id"])
    actions = [copy.deepcopy(action) for action in domain["actions"]]
    actions.sort(key=lambda item: item["id"])
    relations = [
        {
            "id": relation["id"],
            "kind": relation["kind"],
            "source_ref": _resolve_template_ref(domain, relation["source_ref"]),
            "target_ref": _resolve_template_ref(domain, relation["target_ref"]),
        }
        for relation in domain["relations"]
    ]
    relations.sort(key=lambda item: item["id"])
    field_by_id = {field["id"]: field for field in domain["raw_state_fields"]}
    raw_state = [
        {
            "id": field_id,
            "type_id": field_by_id[field_id]["type"],
            "value_id": raw_map[field_id],
        }
        for field_id in sorted(field_by_id)
    ]

    facts: list[dict[str, Any]] = []
    for predicate in domain["derived_predicates"]:
        input_ids = sorted(
            _expression_fields(predicate["expression"], field_by_id, "compile.expression")
        )
        facts.append(
            {
                "id": predicate["id"],
                "slot": predicate["slot"],
                "truth": evaluate_expression(predicate["expression"], raw_map),
                "evidence_ids": [],
                "derivation_rule_id": predicate["id"],
                "input_state_ids": input_ids,
            }
        )
    defeater_slots = sorted({norm["defeater_slot"] for norm in topology["norms"]})
    for slot in defeater_slots:
        facts.append(
            {
                "id": slot,
                "slot": slot,
                "truth": defeater_variant["slot_truths"].get(slot, "F"),
                "evidence_ids": [],
                "derivation_rule_id": "defeater_axis_v1",
                "input_state_ids": [],
            }
        )
    facts.sort(key=lambda item: item["id"])

    evidence_targets = sorted(topology["application_targets"]["evidence"])
    evidence_payload = {
        "evidence_id": "e0",
        "target_norm_ids": evidence_targets,
        "truth": evidence_variant["truth"],
    }
    evidence = [
        {
            "id": "e0",
            "kind": "synthetic_observation",
            "target_norm_ids": evidence_targets,
            "truth": evidence_variant["truth"],
            "payload_sha256": canonical_hash(evidence_payload),
            "authority_status": "synthetic_non_authoritative",
        }
    ]

    norms: list[dict[str, Any]] = []
    for source_norm in topology["norms"]:
        action = _action_by_role(domain, source_norm["action_role"])
        refs = [_condition_ref(domain, reference) for reference in source_norm["condition_refs"]]
        refs.sort(key=lambda item: (item["kind"], item["id"]))
        if source_norm["lifecycle_slot"] == "deadline0":
            lifecycle = {"kind": "deadline", "value": state_variant["id"]}
        else:
            lifecycle = {
                "kind": "state",
                "value": state_variant["norm_states"][source_norm["id"]],
            }
        norms.append(
            {
                "id": source_norm["id"],
                "operator": source_norm["operator"],
                "source_actor_id": domain["actor_role_bindings"][source_norm["source_actor_role"]],
                "subject_id": action["actor_id"],
                "action_id": action["id"],
                "condition_refs": refs,
                "source_id": source_norm["source_id"],
                "lifecycle": lifecycle,
                "defeater": {"kind": "unless", "fact_id": source_norm["defeater_slot"]},
                "repair_for": source_norm["repair_for"],
            }
        )
    norms.sort(key=lambda item: item["id"])

    conflicts = [copy.deepcopy(conflict) for conflict in topology["conflicts"]]
    conflicts.sort(key=lambda item: item["id"])
    priority_edges = [
        {"higher_norm_id": edge[0], "lower_norm_id": edge[1]}
        for edge in resolution_variant["priority_edges"]
    ]
    priority_edges.sort(key=lambda item: (item["higher_norm_id"], item["lower_norm_id"]))
    query = {
        "mode": "single_action",
        "alternative_action_ids": sorted(action["id"] for action in actions),
        "omission_admissible": False,
        "fallback_action_id": _action_by_role(domain, "review")["id"],
    }
    core = {
        "domain_id": domain["id"],
        "actors": actors,
        "actions": actions,
        "relations": relations,
        "raw_state": raw_state,
        "facts": facts,
        "evidence": evidence,
        "norms": norms,
        "conflicts": conflicts,
        "priority_edges": priority_edges,
        "query": query,
    }
    coordinate_value = {
        "domain_code": domain_code,
        "topology_code": topology_code,
        "evidence_code": evidence_code,
        "state_code": state_code,
        "resolution_code": resolution_code,
        "defeater_code": defeater_code,
        "domain_id": domain["id"],
        "topology_id": topology["id"],
        "evidence_id": evidence_variant["id"],
        "state_id": state_variant["id"],
        "resolution_id": resolution_variant["id"],
        "defeater_id": defeater_variant["id"],
    }
    return core, coordinate_value


def _violation_truth(disposition: str) -> str:
    if disposition == "violated":
        return "T"
    if disposition == "blocked_unknown":
        return "U"
    if disposition == "blocked_inconsistent":
        return "B"
    return "F"


def _ordinary_guard(
    norm: Mapping[str, Any],
    facts: Mapping[str, Mapping[str, Any]],
    evidence: Mapping[str, Mapping[str, Any]],
) -> str:
    values: list[str] = []
    for reference in norm["condition_refs"]:
        kind = reference["kind"]
        target = reference["id"]
        if kind == "fact":
            values.append(facts[target]["truth"])
        elif kind == "evidence":
            values.append(evidence[target]["truth"])
        elif kind in {"state", "violation"}:
            continue
        else:  # validated compilation makes this unreachable
            _reject("unknown_condition_kind", f"norm.{norm['id']}", kind)
    return truth_all(values)


def _lifecycle_value(norm: Mapping[str, Any]) -> str:
    lifecycle = norm["lifecycle"]
    return lifecycle["value"]


def _lifecycle_disposition(norm: Mapping[str, Any]) -> tuple[str, str | None]:
    lifecycle = norm["lifecycle"]
    value = lifecycle["value"]
    if lifecycle["kind"] == "state":
        if value == "unknown":
            return "blocked_unknown", "unknown_lifecycle"
        return value, None
    if norm["operator"] == "P":
        _reject("unsupported_deadline_operator", f"norm.{norm['id']}.operator")
    if value == "before_deadline_unperformed":
        return "active", None
    if value == "deadline_reached_timely_performed":
        return ("satisfied", None) if norm["operator"] == "O" else ("violated", None)
    if value == "deadline_reached_late_performed":
        return "violated", None
    if value == "deadline_reached_performance_unknown":
        return "blocked_unknown", "unknown_deadline"
    _reject("invalid_deadline_state", f"norm.{norm['id']}.lifecycle", str(value))


def _priority_reachable(
    source: str,
    target: str,
    edges: Sequence[Mapping[str, str]],
) -> bool:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        adjacency[edge["higher_norm_id"]].add(edge["lower_norm_id"])
    frontier = sorted(adjacency[source], reverse=True)
    seen: set[str] = set()
    while frontier:
        current = frontier.pop()
        if current == target:
            return True
        if current in seen:
            continue
        seen.add(current)
        frontier.extend(sorted(adjacency[current] - seen, reverse=True))
    return False


def evaluate_core(core: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate one compiler-owned core under the frozen finite semantics."""

    raw_state = {cell["id"]: cell["value_id"] for cell in core["raw_state"]}
    facts = {fact["id"]: fact for fact in core["facts"]}
    evidence = {item["id"]: item for item in core["evidence"]}
    norms = {norm["id"]: norm for norm in core["norms"]}
    blockers: set[str] = set()
    steps: dict[str, dict[str, Any]] = {}
    pre_dispositions: dict[str, str] = {}

    def evaluate_norm(norm: Mapping[str, Any], repair_gate: str | None) -> None:
        norm_id = norm["id"]
        guard = _ordinary_guard(norm, facts, evidence)
        defeater_truth = facts[norm["defeater"]["fact_id"]]["truth"]
        reasons: set[str] = set()
        blocker: str | None = None

        if repair_gate == "F":
            disposition = "inactive"
            reasons.add("primary_not_violated")
        elif repair_gate == "U":
            disposition = "blocked_unknown"
            blocker = "unknown_primary_violation"
            reasons.add(blocker)
        elif repair_gate == "B":
            disposition = "blocked_inconsistent"
            blocker = "inconsistent_primary_violation"
            reasons.add(blocker)
        elif guard == "F":
            disposition = "inactive"
            reasons.add("condition_false")
        elif guard == "U":
            disposition = "blocked_unknown"
            blocker = "unknown_condition"
            reasons.add(blocker)
        elif guard == "B":
            disposition = "blocked_inconsistent"
            blocker = "inconsistent_condition"
            reasons.add(blocker)
        elif defeater_truth == "T":
            disposition = "defeated"
            reasons.add("defeater_true")
        elif defeater_truth == "U":
            disposition = "blocked_unknown"
            blocker = "unknown_defeater"
            reasons.add(blocker)
        elif defeater_truth == "B":
            disposition = "blocked_inconsistent"
            blocker = "inconsistent_defeater"
            reasons.add(blocker)
        else:
            disposition, blocker = _lifecycle_disposition(norm)
            if blocker is not None:
                reasons.add(blocker)
            else:
                reasons.add(f"lifecycle_{disposition}")
        if blocker is not None:
            blockers.add(blocker)
        pre_dispositions[norm_id] = disposition
        steps[norm_id] = {
            "norm_id": norm_id,
            "repair_gate_truth": "none" if repair_gate is None else repair_gate,
            "ordinary_guard_truth": guard,
            "defeater_truth": defeater_truth,
            "lifecycle_value": _lifecycle_value(norm),
            "pre_conflict_disposition": disposition,
            "final_disposition": disposition,
            "reason_codes": sorted(reasons),
        }

    non_repairs = sorted(
        (norm for norm in norms.values() if norm["repair_for"] == "none"),
        key=lambda item: item["id"],
    )
    repairs = sorted(
        (norm for norm in norms.values() if norm["repair_for"] != "none"),
        key=lambda item: item["id"],
    )
    for norm in non_repairs:
        evaluate_norm(norm, None)

    primary_gate_truths = {
        norm_id: _violation_truth(disposition)
        for norm_id, disposition in pre_dispositions.items()
    }
    activated_repairs: set[str] = set()
    for norm in repairs:
        gate = primary_gate_truths[norm["repair_for"]]
        if gate == "T":
            activated_repairs.add(norm["id"])
        evaluate_norm(norm, gate)

    conflict_steps: list[dict[str, Any]] = []
    simultaneous_losers: set[str] = set()
    for conflict in sorted(core["conflicts"], key=lambda item: item["id"]):
        left = conflict["left_norm_id"]
        right = conflict["right_norm_id"]
        left_active = pre_dispositions[left] == "active"
        right_active = pre_dispositions[right] == "active"
        left_reaches = _priority_reachable(left, right, core["priority_edges"])
        right_reaches = _priority_reachable(right, left, core["priority_edges"])
        disposition = "inactive_conflict"
        loser = "none"
        if left_active and right_active:
            if left_reaches and not right_reaches:
                disposition = "left_wins"
                loser = right
                simultaneous_losers.add(right)
            elif right_reaches and not left_reaches:
                disposition = "right_wins"
                loser = left
                simultaneous_losers.add(left)
            elif left_reaches and right_reaches:
                disposition = "blocked_priority_cycle"
                blockers.add("relevant_priority_cycle")
            else:
                disposition = "blocked_unresolved_priority"
                blockers.add("unresolved_priority")
        conflict_steps.append(
            {
                "conflict_id": conflict["id"],
                "left_active": left_active,
                "right_active": right_active,
                "left_reaches_right": left_reaches,
                "right_reaches_left": right_reaches,
                "disposition": disposition,
                "defeated_norm_id": loser,
            }
        )

    final_dispositions = dict(pre_dispositions)
    for norm_id in sorted(simultaneous_losers):
        final_dispositions[norm_id] = "defeated"
        steps[norm_id]["final_disposition"] = "defeated"
        steps[norm_id]["reason_codes"] = sorted(
            set(steps[norm_id]["reason_codes"]) | {"priority_defeated"}
        )

    norm_violation_truth = {
        norm_id: _violation_truth(disposition)
        for norm_id, disposition in final_dispositions.items()
    }
    families: dict[str, list[str]] = defaultdict(list)
    for norm in repairs:
        families[norm["repair_for"]].append(norm["id"])
    repair_availability: list[dict[str, Any]] = []
    repair_steps: list[dict[str, Any]] = []
    for primary in sorted(families):
        linked = sorted(families[primary])
        providers = [norm_id for norm_id in linked if norms[norm_id]["operator"] == "O"]
        provider = providers[0] if providers else "none"
        provider_disposition = (
            "none" if provider == "none" else final_dispositions[provider]
        )
        violation = norm_violation_truth[primary]
        family_blocker: str | None = None
        if violation == "F":
            availability = "not_triggered"
        elif violation == "U":
            availability = "blocked_unknown"
            blockers.update({"unknown_primary_violation", "unknown_repair_availability"})
        elif violation == "B":
            availability = "blocked_inconsistent"
            blockers.update(
                {"inconsistent_primary_violation", "inconsistent_repair_availability"}
            )
        elif provider == "none":
            availability = "absent"
            family_blocker = "repair_unavailable"
        else:
            availability = provider_disposition
            if availability in {"violated", "defeated", "inactive"}:
                family_blocker = "repair_unavailable"
            elif availability == "blocked_unknown":
                family_blocker = "unknown_repair_availability"
            elif availability == "blocked_inconsistent":
                family_blocker = "inconsistent_repair_availability"
        if family_blocker is not None:
            blockers.add(family_blocker)
        availability_row = {
            "primary_norm_id": primary,
            "primary_violation_truth": violation,
            "linked_norm_ids": linked,
            "provider_norm_id": provider,
            "provider_disposition": provider_disposition,
            "availability": availability,
        }
        repair_availability.append(availability_row)
        repair_steps.append(
            {
                **availability_row,
                "reason_codes": [f"repair_{availability}"],
            }
        )

    active = {
        norm_id for norm_id, disposition in final_dispositions.items() if disposition == "active"
    }
    defeated = {
        norm_id for norm_id, disposition in final_dispositions.items() if disposition == "defeated"
    }
    satisfied = {
        norm_id for norm_id, disposition in final_dispositions.items() if disposition == "satisfied"
    }
    violated = {
        norm_id for norm_id, disposition in final_dispositions.items() if disposition == "violated"
    }
    required = {
        norms[norm_id]["action_id"]
        for norm_id in active
        if norms[norm_id]["operator"] == "O"
    }
    explicit_permitted = {
        norms[norm_id]["action_id"]
        for norm_id in active
        if norms[norm_id]["operator"] == "P"
    }
    permitted = required | explicit_permitted
    forbidden = {
        norms[norm_id]["action_id"]
        for norm_id in active
        if norms[norm_id]["operator"] == "F"
    }
    if permitted & forbidden:
        blockers.add("modal_conflict")
    if len(required) > 1:
        blockers.add("single_action_cardinality_conflict")

    if blockers:
        status = "unresolved"
        fallback = "escalate"
        executable_required: set[str] = set()
        executable_permitted: set[str] = set()
        admissible: set[str] = set()
    elif not permitted:
        status = "unresolved"
        fallback = "abstain"
        executable_required = set()
        executable_permitted = set()
        admissible = set()
    else:
        status = "resolved"
        fallback = "none"
        executable_required = set(required)
        if required:
            executable_permitted = set(required)
            admissible = set(required)
        else:
            executable_permitted = permitted - forbidden
            admissible = set(executable_permitted)

    alternatives = set(core["query"]["alternative_action_ids"])
    rejected = alternatives - admissible
    admissibility_steps: list[dict[str, Any]] = []
    for action_id in sorted(alternatives):
        admitted = action_id in admissible
        reasons: set[str] = set()
        if blockers:
            reasons |= blockers
        elif fallback == "abstain":
            reasons.add("no_positive_norm")
        elif admitted and action_id in required:
            reasons.add("required_action")
        elif admitted:
            reasons.add("explicit_permission")
        elif action_id in forbidden:
            reasons.add("forbidden_action")
        elif required:
            reasons.add("required_action_elsewhere")
        else:
            reasons.add("not_permitted")
        admissibility_steps.append(
            {
                "action_id": action_id,
                "required": action_id in required,
                "permitted": action_id in permitted,
                "forbidden": action_id in forbidden,
                "admitted": admitted,
                "reason_codes": sorted(reasons),
            }
        )

    predicate_steps = [
        {
            "fact_id": fact["id"],
            "rule_id": fact["derivation_rule_id"],
            "input_state_ids": list(fact["input_state_ids"]),
            "input_values": [raw_state[state_id] for state_id in fact["input_state_ids"]],
            "truth": fact["truth"],
        }
        for fact in sorted(core["facts"], key=lambda item: item["id"])
    ]
    proof_trace = {
        "predicate_steps": predicate_steps,
        "norm_steps": [steps[norm_id] for norm_id in sorted(steps)],
        "repair_steps": repair_steps,
        "conflict_steps": conflict_steps,
        "admissibility_steps": admissibility_steps,
    }
    result: dict[str, Any] = {
        "schema": RESULT_SCHEMA,
        "status": status,
        "fallback": fallback,
        "blocker_codes": sorted(blockers),
        "active_norm_ids": sorted(active),
        "defeated_norm_ids": sorted(defeated),
        "satisfied_norm_ids": sorted(satisfied),
        "violated_norm_ids": sorted(violated),
        "activated_repair_norm_ids": sorted(activated_repairs),
        "norm_violation_truths": [
            {"norm_id": norm_id, "truth": norm_violation_truth[norm_id]}
            for norm_id in sorted(norm_violation_truth)
        ],
        "repair_availability": repair_availability,
        "diagnostic_required_action_ids": sorted(required),
        "diagnostic_permitted_action_ids": sorted(permitted),
        "diagnostic_forbidden_action_ids": sorted(forbidden),
        "executable_required_action_ids": sorted(executable_required),
        "executable_permitted_action_ids": sorted(executable_permitted),
        "admissible_action_ids": sorted(admissible),
        "rejected_action_ids": sorted(rejected),
        "proof_trace": proof_trace,
        "proof_trace_sha256": canonical_hash(proof_trace),
    }
    result["result_sha256"] = canonical_hash(result)
    if not set(result["blocker_codes"]) <= BLOCKER_CODES:
        raise AssertionError("internal blocker escaped closed set")
    if status == "unresolved" and (
        result["executable_required_action_ids"]
        or result["executable_permitted_action_ids"]
        or result["admissible_action_ids"]
    ):
        raise AssertionError("unresolved result exposed executable action")
    return result


def verify_semantics_spec(
    path: Path,
    *,
    expected_sha256: str = EXPECTED_SEMANTICS_SHA256,
) -> str:
    actual = file_sha256(path)
    if actual != expected_sha256:
        _reject(
            "semantics_hash_mismatch",
            str(path),
            f"expected={expected_sha256} actual={actual}",
        )
    return actual


def generate_record(
    template: TemplateBank,
    ordinal: int,
    *,
    semantics_sha256: str = EXPECTED_SEMANTICS_SHA256,
) -> dict[str, Any]:
    """Generate one canonical-content record without performing any effects."""

    if HASH_RE.fullmatch(semantics_sha256) is None:
        _reject("invalid_hash", "semantics_sha256", semantics_sha256)
    codes = unrank_ordinal(ordinal)
    core, coordinate = compile_core(template, codes)
    core_hash = canonical_hash(core)
    result = evaluate_core(core)
    record: dict[str, Any] = {
        "schema": CASE_SCHEMA,
        "ordinal": ordinal,
        "coordinate": coordinate,
        "profile_ref": {
            "profile_id": PROFILE_ID,
            "semantics_spec_sha256": semantics_sha256,
            "template_bank_sha256": template.sha256,
        },
        "authority": copy.deepcopy(AUTHORITY),
        "semantic_core": core,
        "semantic_core_sha256": core_hash,
        "stable_id": f"sdk-luna-v1-{core_hash}",
        "generator_claim": result,
        "nonclaims": list(NONCLAIMS),
    }
    record["record_sha256"] = canonical_hash(record)
    return record


def encode_record(
    template: TemplateBank,
    ordinal: int,
    *,
    semantics_sha256: str = EXPECTED_SEMANTICS_SHA256,
) -> bytes:
    return canonical_json_bytes(
        generate_record(template, ordinal, semantics_sha256=semantics_sha256)
    )


def deterministic_gzip(payload: bytes, *, compresslevel: int = 9) -> bytes:
    """Return gzip bytes with an empty filename and a zero timestamp."""

    target = io.BytesIO()
    with gzip.GzipFile(
        filename="",
        mode="wb",
        compresslevel=compresslevel,
        fileobj=target,
        mtime=0,
    ) as handle:
        handle.write(payload)
    return target.getvalue()


def _write_canonical_json_new(path: Path, value: object) -> None:
    if path.exists():
        _reject("output_exists", str(path))
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(path.name + ".tmp")
        if temporary.exists():
            _reject("output_exists", str(temporary))
        temporary.write_bytes(canonical_json_bytes(value))
        os.replace(temporary, path)
    except GeneratorReject:
        raise
    except OSError as exc:
        raise GeneratorReject("artifact_write_error", str(path), str(exc)) from exc


def build_corpus(
    template_bank_path: Path,
    semantics_spec_path: Path,
    output_dir: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    """Build all 65,536 records into deterministic gzip shards.

    The returned and written manifest is explicitly generation-only.  It never
    assigns a release label and never claims that the independent oracle ran.
    """

    if output_dir.exists():
        _reject("output_exists", str(output_dir))
    if manifest_path.exists():
        _reject("output_exists", str(manifest_path))
    template = load_template_bank(template_bank_path)
    semantics_hash = verify_semantics_spec(semantics_spec_path)
    try:
        output_dir.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(
            tempfile.mkdtemp(
                prefix=f".{output_dir.name}.staging-",
                dir=output_dir.parent,
            )
        )
    except OSError as exc:
        raise GeneratorReject("artifact_write_error", str(output_dir), str(exc)) from exc

    raw_handles: dict[str, Any] = {}
    gzip_handles: dict[str, gzip.GzipFile] = {}
    shard_paths = {
        prefix: staging / f"part-{prefix}.jsonl.gz" for prefix in SHARD_PREFIXES
    }
    shard_hashers = {prefix: hashlib.sha256() for prefix in SHARD_PREFIXES}
    shard_counts: Counter[str] = Counter()
    shard_uncompressed_bytes: Counter[str] = Counter()
    coverage = {
        "domain_id": Counter(),
        "topology_id": Counter(),
        "evidence_id": Counter(),
        "state_id": Counter(),
        "resolution_id": Counter(),
        "defeater_id": Counter(),
    }
    outcomes: Counter[str] = Counter()
    semantic_hashes: set[str] = set()
    stable_ids: set[str] = set()
    record_hashes: set[str] = set()
    ordered_root_rows: list[list[Any]] = []
    try:
        for prefix in SHARD_PREFIXES:
            raw = shard_paths[prefix].open("wb")
            raw_handles[prefix] = raw
            gzip_handles[prefix] = gzip.GzipFile(
                filename="",
                mode="wb",
                compresslevel=9,
                fileobj=raw,
                mtime=0,
            )
        for ordinal in range(EXPECTED_RECORD_COUNT):
            record = generate_record(
                template,
                ordinal,
                semantics_sha256=semantics_hash,
            )
            semantic_hash = record["semantic_core_sha256"]
            stable_id = record["stable_id"]
            record_hash = record["record_sha256"]
            if semantic_hash in semantic_hashes:
                _reject("duplicate_semantic_core", f"ordinal[{ordinal}]", semantic_hash)
            if stable_id in stable_ids:
                _reject("duplicate_stable_id", f"ordinal[{ordinal}]", stable_id)
            if record_hash in record_hashes:
                _reject("duplicate_record_hash", f"ordinal[{ordinal}]", record_hash)
            semantic_hashes.add(semantic_hash)
            stable_ids.add(stable_id)
            record_hashes.add(record_hash)

            payload = canonical_json_bytes(record) + b"\n"
            prefix = semantic_hash[0]
            gzip_handles[prefix].write(payload)
            shard_hashers[prefix].update(payload)
            shard_counts[prefix] += 1
            shard_uncompressed_bytes[prefix] += len(payload)
            coordinate = record["coordinate"]
            for field, counter in coverage.items():
                counter[coordinate[field]] += 1
            result = record["generator_claim"]
            outcomes[f"{result['status']}:{result['fallback']}"] += 1
            ordered_root_rows.append([ordinal, record_hash])

        if len(semantic_hashes) != EXPECTED_RECORD_COUNT:
            _reject("record_count_mismatch", "corpus", str(len(semantic_hashes)))
    except Exception:
        for handle in gzip_handles.values():
            try:
                handle.close()
            except OSError:
                pass
        for handle in raw_handles.values():
            try:
                handle.close()
            except OSError:
                pass
        shutil.rmtree(staging, ignore_errors=True)
        raise
    else:
        for handle in gzip_handles.values():
            handle.close()
        for handle in raw_handles.values():
            if not handle.closed:
                handle.close()

    shards: list[dict[str, Any]] = []
    for prefix in SHARD_PREFIXES:
        path = shard_paths[prefix]
        shards.append(
            {
                "prefix": prefix,
                "file": path.name,
                "records": shard_counts[prefix],
                "uncompressed_bytes": shard_uncompressed_bytes[prefix],
                "uncompressed_sha256": shard_hashers[prefix].hexdigest(),
                "compressed_bytes": path.stat().st_size,
                "compressed_sha256": file_sha256(path),
            }
        )

    source_path = Path(__file__).resolve()
    manifest: dict[str, Any] = {
        "schema": MANIFEST_SCHEMA,
        "status": "generation_only_pending_independent_oracle",
        "authoritative_status": "synthetic_non_authoritative",
        "record_schema": CASE_SCHEMA,
        "record_count": EXPECTED_RECORD_COUNT,
        "factorization": {
            "axis_names": list(AXIS_NAMES),
            "axis_radices": list(AXIS_RADICES),
            "product": EXPECTED_RECORD_COUNT,
        },
        "hashes": {
            "template_bank_sha256": template.sha256,
            "template_profile_sha256": canonical_hash(template.data),
            "semantics_spec_sha256": semantics_hash,
            "generator_source_sha256": file_sha256(source_path),
            "candidate_evaluator_source_sha256": file_sha256(source_path),
            "corpus_root_sha256": canonical_hash(ordered_root_rows),
            "semantic_set_root_sha256": sha256_bytes(
                b"".join(bytes.fromhex(value) for value in sorted(semantic_hashes))
            ),
        },
        "coverage": {
            field: dict(sorted(counter.items())) for field, counter in coverage.items()
        },
        "candidate_outcomes": dict(sorted(outcomes.items())),
        "sharding": {
            "method": "first_hex_of_semantic_core_sha256",
            "shard_count": len(SHARD_PREFIXES),
            "shards": shards,
        },
        "compression": {
            "format": "gzip",
            "compresslevel": 9,
            "mtime": 0,
            "filename_header": "empty",
            "python": platform.python_version(),
            "zlib": zlib.ZLIB_VERSION,
        },
        "release_authority": {
            "generator_owns_release": False,
            "independent_oracle_status": "not_run_by_generator",
            "promotion_reducer_status": "not_run_by_generator",
        },
        "nonclaims": list(NONCLAIMS),
    }

    try:
        os.replace(staging, output_dir)
        _write_canonical_json_new(manifest_path, manifest)
    except Exception:
        if output_dir.exists():
            shutil.rmtree(output_dir, ignore_errors=True)
        elif staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
        raise
    return manifest


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate-template", help="validate the frozen template and semantics hashes")
    validate.add_argument("--template-bank", required=True, type=Path)
    validate.add_argument("--semantics-spec", required=True, type=Path)

    sample = subparsers.add_parser("sample", help="emit one canonical candidate record")
    sample.add_argument("--template-bank", required=True, type=Path)
    sample.add_argument("--semantics-spec", required=True, type=Path)
    sample.add_argument("--ordinal", required=True, type=int)

    build = subparsers.add_parser("build", help="build all 65,536 candidate records")
    build.add_argument("--template-bank", required=True, type=Path)
    build.add_argument("--semantics-spec", required=True, type=Path)
    build.add_argument("--output-dir", required=True, type=Path)
    build.add_argument("--manifest", required=True, type=Path)
    return parser


def _main(argv: Sequence[str]) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "build":
            result: object = build_corpus(
                args.template_bank,
                args.semantics_spec,
                args.output_dir,
                args.manifest,
            )
        else:
            template = load_template_bank(args.template_bank)
            semantics_hash = verify_semantics_spec(args.semantics_spec)
            if args.command == "sample":
                result = generate_record(
                    template,
                    args.ordinal,
                    semantics_sha256=semantics_hash,
                )
            else:
                result = {
                    "status": "PASS",
                    "profile_id": PROFILE_ID,
                    "template_bank_sha256": template.sha256,
                    "semantics_spec_sha256": semantics_hash,
                    "record_count": EXPECTED_RECORD_COUNT,
                    "release_verdict": "not_owned_by_generator",
                }
        sys.stdout.buffer.write(canonical_json_bytes(result) + b"\n")
        return 0
    except GeneratorReject as exc:
        sys.stderr.write(f"synthetic_deontic_luna_v1: {exc}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
