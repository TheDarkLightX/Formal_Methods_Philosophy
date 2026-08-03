"""Independent verifier for the bounded Synthetic Deontic Luna v1 corpus.

This module intentionally does not import the corpus generator.  It parses raw
canonical records, reconstructs the selected template coordinate, evaluates
the closed four-valued semantics, and compares the complete claimed result.

The corpus is synthetic and non-authoritative.  A successful check is evidence
about the frozen finite profile only.  It is not legal, ethical, factual, or
production-policy authority and cannot authorize an external effect.
"""

from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import itertools
import json
import os
import re
import sys
import tempfile
from collections import Counter, defaultdict
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

TEMPLATE_SCHEMA = "synthetic-deontic-luna-template-bank-v1"
PROFILE_ID = "sdk-luna-v1-bounded-causal-four-valued"
CASE_SCHEMA = "synthetic-deontic-luna-case-v1"
RESULT_SCHEMA = "synthetic-deontic-luna-result-v1"
NORMALIZATION_SCHEMA = "synthetic-deontic-luna-normalized-disposition-v1"
RECEIPT_SCHEMA = "synthetic-deontic-luna-counterfactual-v1"
REPORT_SCHEMA = "synthetic-deontic-luna-oracle-report-v1"

EXPECTED_TEMPLATE_SHA256 = (
    "eadfeeb5a464f89a878800d21e84acd2ce8f3844a75cc49234bccde95b16c3c9"
)
EXPECTED_SEMANTICS_SHA256 = (
    "d265a71141d3b5f0291a971c2997d085efe53c91851359f181b0682d7fd6f371"
)
EXPECTED_RELEASE_GATES_SHA256 = (
    "4dd3d794f501723eb2bcd06d09e1140418a1956edce2214c245d175bd1b72cb3"
)

RECORD_COUNT = 65_536
PAIR_COUNT = 393_216
SPANNING_WITNESS_COUNT = 3_072
MAX_RECORD_BYTES = 1_000_000
MAX_TEMPLATE_BYTES = 2_000_000

AXES = ("evidence", "state", "resolution", "defeater")
AXIS_FIELDS = {
    "evidence": "evidence_code",
    "state": "state_code",
    "resolution": "resolution_code",
    "defeater": "defeater_code",
}
TRUTHS = ("T", "F", "U", "B")
NORM_DISPOSITIONS = frozenset(
    {
        "inactive",
        "active",
        "satisfied",
        "violated",
        "defeated",
        "blocked_unknown",
        "blocked_inconsistent",
    }
)
REPAIR_AVAILABILITIES = frozenset(
    {
        "not_triggered",
        "absent",
        "active",
        "satisfied",
        "violated",
        "defeated",
        "inactive",
        "blocked_unknown",
        "blocked_inconsistent",
    }
)
ID_RE = re.compile(r"[a-z][a-z0-9_]{0,63}\Z")
HASH_RE = re.compile(r"[0-9a-f]{64}\Z")

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
CASE_FIELDS = frozenset(
    {
        "schema",
        "ordinal",
        "coordinate",
        "profile_ref",
        "authority",
        "semantic_core",
        "semantic_core_sha256",
        "stable_id",
        "generator_claim",
        "nonclaims",
        "record_sha256",
    }
)
COORDINATE_FIELDS = frozenset(
    {
        "domain_code",
        "topology_code",
        "evidence_code",
        "state_code",
        "resolution_code",
        "defeater_code",
        "domain_id",
        "topology_id",
        "evidence_id",
        "state_id",
        "resolution_id",
        "defeater_id",
    }
)
PROFILE_REF_FIELDS = frozenset(
    {"profile_id", "semantics_spec_sha256", "template_bank_sha256"}
)
AUTHORITY_FIELDS = frozenset(AUTHORITY)
CORE_FIELDS = frozenset(
    {
        "domain_id",
        "actors",
        "actions",
        "relations",
        "raw_state",
        "facts",
        "evidence",
        "norms",
        "conflicts",
        "priority_edges",
        "query",
    }
)
RESULT_FIELDS = frozenset(
    {
        "schema",
        "status",
        "fallback",
        "blocker_codes",
        "active_norm_ids",
        "defeated_norm_ids",
        "satisfied_norm_ids",
        "violated_norm_ids",
        "activated_repair_norm_ids",
        "norm_violation_truths",
        "repair_availability",
        "diagnostic_required_action_ids",
        "diagnostic_permitted_action_ids",
        "diagnostic_forbidden_action_ids",
        "executable_required_action_ids",
        "executable_permitted_action_ids",
        "admissible_action_ids",
        "rejected_action_ids",
        "proof_trace",
        "proof_trace_sha256",
        "result_sha256",
    }
)

TEMPLATE_SHAPES = {
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
    "state_variant": [
        "code",
        "id",
        "domain_witness",
        "norm_states",
        "flags",
    ],
    "resolution_variant": [
        "code",
        "id",
        "priority_edges",
        "expected_if_conflict",
    ],
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


class OracleReject(ValueError):
    """Typed fail-closed rejection at the oracle boundary."""

    def __init__(self, code: str, path: str, detail: str = "") -> None:
        self.code = code
        self.path = path
        self.detail = detail
        message = f"{code} at {path}"
        if detail:
            message += f": {detail}"
        super().__init__(message)


@dataclass(frozen=True)
class BoundTemplate:
    data: dict[str, Any]
    sha256: str
    domains_by_id: Mapping[str, dict[str, Any]]
    topologies_by_id: Mapping[str, dict[str, Any]]


@dataclass(frozen=True)
class VerifiedCase:
    ordinal: int
    codes: tuple[int, int, int, int, int, int]
    domain_id: str
    topology_id: str
    stable_id: str
    record_sha256: str
    result_sha256: str
    normalized_sha256: str
    normalized: dict[str, Any]
    status: str
    fallback: str


_RECONCILED_CASE_SET_SEAL = object()


@dataclass(frozen=True)
class _ReconciledCaseSet:
    """Privately constructed canonical cases admitted by this oracle."""

    _template_sha256: str
    _cases: tuple[VerifiedCase, ...]
    _cases_by_ordinal: Mapping[int, VerifiedCase]
    _seal: object


def _reject(code: str, path: str, detail: str = "") -> None:
    raise OracleReject(code, path, detail)


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    """Encode the v1 canonical JSON representation."""

    try:
        text = json.dumps(
            value,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as exc:
        _reject("noncanonical_value", "$", str(exc))
    return text.encode("ascii")


def canonical_hash(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def _pairs_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _reject("duplicate_json_key", "$", key)
        result[key] = value
    return result


def _reject_float(text: str) -> Any:
    _reject("json_float_forbidden", "$", text)


def _reject_constant(text: str) -> Any:
    _reject("json_nonfinite_forbidden", "$", text)


def parse_json_exact(raw: bytes, *, canonical: bool, max_bytes: int) -> Any:
    """Parse ASCII JSON with duplicate-key, float, and canonical-byte checks."""

    if type(raw) is not bytes:
        _reject("raw_bytes_required", "$", type(raw).__name__)
    if not raw or len(raw) > max_bytes:
        _reject("resource_bound", "$", f"byte_count={len(raw)}")
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        _reject("non_ascii_json", "$", str(exc))
    try:
        value = json.loads(
            text,
            object_pairs_hook=_pairs_object,
            parse_float=_reject_float,
            parse_constant=_reject_constant,
        )
    except OracleReject:
        raise
    except (json.JSONDecodeError, RecursionError) as exc:
        _reject("malformed_json", "$", str(exc))
    if canonical and canonical_bytes(value) != raw:
        _reject("noncanonical_bytes", "$", "re-encoding differs")
    return value


def _exact_object(
    value: Any, fields: frozenset[str] | set[str], path: str
) -> dict[str, Any]:
    if type(value) is not dict:
        _reject("wrong_type", path, "expected object")
    actual = set(value)
    missing = sorted(fields - actual)
    unknown = sorted(actual - fields)
    if missing:
        _reject("missing_field", path, ",".join(missing))
    if unknown:
        _reject("unknown_field", path, ",".join(unknown))
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
    if not ID_RE.fullmatch(text):
        _reject("invalid_id", path, text)
    return text


def _hash(value: Any, path: str) -> str:
    text = _string(value, path)
    if not HASH_RE.fullmatch(text):
        _reject("invalid_sha256", path, text)
    return text


def _integer(value: Any, path: str, low: int, high: int) -> int:
    if type(value) is not int:
        _reject("wrong_type", path, "expected integer (Boolean aliases forbidden)")
    if value < low or value > high:
        _reject("integer_out_of_range", path, str(value))
    return value


def _boolean(value: Any, path: str) -> bool:
    if type(value) is not bool:
        _reject("wrong_type", path, "expected Boolean")
    return value


def _enum(
    value: Any, allowed: set[str] | frozenset[str] | tuple[str, ...], path: str
) -> str:
    text = _string(value, path)
    if text not in allowed:
        _reject("unknown_enum", path, text)
    return text


def _sorted_unique_strings(
    value: Any,
    path: str,
    *,
    ids: bool = True,
    allowed: set[str] | frozenset[str] | None = None,
    require_sorted: bool = True,
) -> list[str]:
    items = _list(value, path)
    checked: list[str] = []
    for index, item in enumerate(items):
        item_path = f"{path}[{index}]"
        text = _id(item, item_path) if ids else _string(item, item_path)
        if allowed is not None and text not in allowed:
            _reject("unknown_enum", item_path, text)
        checked.append(text)
    if require_sorted and checked != sorted(checked):
        _reject("noncanonical_order", path, "array is not sorted")
    if len(set(checked)) != len(checked):
        _reject("duplicate_id", path, "array contains duplicate values")
    return checked


def _unique_objects_by_id(
    items: Any, path: str, *, require_sorted: bool = False
) -> dict[str, dict[str, Any]]:
    values = _list(items, path)
    result: dict[str, dict[str, Any]] = {}
    previous = ""
    for index, item in enumerate(values):
        item_path = f"{path}[{index}]"
        if type(item) is not dict:
            _reject("wrong_type", item_path, "expected object")
        item_id = _id(item.get("id"), f"{item_path}.id")
        if item_id in result:
            _reject("duplicate_id", item_path, item_id)
        if require_sorted and previous and item_id < previous:
            _reject("noncanonical_order", path, "objects are not sorted by id")
        previous = item_id
        result[item_id] = item
    return result


def _expect_equal(
    actual: Any, expected: Any, path: str, code: str = "value_mismatch"
) -> None:
    if actual != expected:
        _reject(code, path, f"expected {expected!r}, got {actual!r}")


def _bound_file(path: Path, expected_sha256: str, max_bytes: int) -> bytes:
    raw = path.read_bytes()
    if len(raw) > max_bytes:
        _reject("resource_bound", str(path), f"byte_count={len(raw)}")
    actual = sha256_bytes(raw)
    if actual != expected_sha256:
        _reject(
            "source_hash_mismatch",
            str(path),
            f"expected {expected_sha256}, got {actual}",
        )
    return raw


def load_bound_semantics(
    path: str | Path, expected_sha256: str = EXPECTED_SEMANTICS_SHA256
) -> bytes:
    return _bound_file(Path(path), expected_sha256, MAX_TEMPLATE_BYTES)


def load_bound_release_gates(
    path: str | Path, expected_sha256: str = EXPECTED_RELEASE_GATES_SHA256
) -> bytes:
    return _bound_file(Path(path), expected_sha256, MAX_TEMPLATE_BYTES)


def _truth_pair(truth: str) -> tuple[bool, bool]:
    return {
        "T": (True, False),
        "F": (False, True),
        "U": (False, False),
        "B": (True, True),
    }[truth]


def _pair_truth(pair: tuple[bool, bool]) -> str:
    return {
        (True, False): "T",
        (False, True): "F",
        (False, False): "U",
        (True, True): "B",
    }[pair]


def truth_not(value: str) -> str:
    positive, negative = _truth_pair(value)
    return _pair_truth((negative, positive))


def truth_all(values: Iterable[str]) -> str:
    positives: list[bool] = []
    negatives: list[bool] = []
    for value in values:
        positive, negative = _truth_pair(value)
        positives.append(positive)
        negatives.append(negative)
    if not positives:
        _reject("empty_expression", "expression.all")
    return _pair_truth((all(positives), any(negatives)))


def truth_any(values: Iterable[str]) -> str:
    positives: list[bool] = []
    negatives: list[bool] = []
    for value in values:
        positive, negative = _truth_pair(value)
        positives.append(positive)
        negatives.append(negative)
    if not positives:
        _reject("empty_expression", "expression.any")
    return _pair_truth((any(positives), all(negatives)))


def _expression_fields(
    expression: Any, fields: Mapping[str, dict[str, Any]], path: str
) -> set[str]:
    form = _list(expression, path)
    if not form:
        _reject("malformed_expression", path, "empty")
    op = _enum(form[0], {"eq", "all", "any", "not"}, f"{path}[0]")
    if op == "eq":
        if len(form) != 3:
            _reject("malformed_expression", path, "eq arity")
        field_id = _id(form[1], f"{path}[1]")
        if field_id not in fields:
            _reject("dangling_reference", f"{path}[1]", field_id)
        literal = _id(form[2], f"{path}[2]")
        if literal not in fields[field_id]["allowed_values"]:
            _reject("invalid_literal", f"{path}[2]", literal)
        return {field_id}
    if op == "not":
        if len(form) != 2:
            _reject("malformed_expression", path, "not arity")
        return _expression_fields(form[1], fields, f"{path}[1]")
    if len(form) < 3:
        _reject("malformed_expression", path, f"{op} needs at least two operands")
    result: set[str] = set()
    for index, child in enumerate(form[1:], 1):
        result.update(_expression_fields(child, fields, f"{path}[{index}]"))
    return result


def evaluate_expression(expression: Any, raw_state: Mapping[str, str]) -> str:
    form = expression
    op = form[0]
    if op == "eq":
        actual = raw_state[form[1]]
        if actual == "unknown":
            return "U"
        if actual == "both":
            return "B"
        return "T" if actual == form[2] else "F"
    if op == "not":
        return truth_not(evaluate_expression(form[1], raw_state))
    values = [evaluate_expression(child, raw_state) for child in form[1:]]
    return truth_all(values) if op == "all" else truth_any(values)


def _validate_domain(domain: Any, index: int) -> None:
    path = f"$.domains[{index}]"
    _exact_object(domain, set(TEMPLATE_SHAPES["domain"]), path)
    domain_id = _id(domain["id"], f"{path}.id")
    _string(domain["summary"], f"{path}.summary")

    bindings = domain["actor_role_bindings"]
    _exact_object(
        bindings,
        {"operator", "authority", "affected", "reviewer"},
        f"{path}.actor_role_bindings",
    )
    for role, actor_id in bindings.items():
        _id(role, f"{path}.actor_role_bindings.{role}")
        _id(actor_id, f"{path}.actor_role_bindings.{role}")
    if len(set(bindings.values())) != 4:
        _reject("duplicate_role_binding", f"{path}.actor_role_bindings")

    actors = _unique_objects_by_id(domain["actors"], f"{path}.actors")
    if len(actors) != 4:
        _reject("wrong_cardinality", f"{path}.actors", str(len(actors)))
    for actor_id, actor in actors.items():
        _exact_object(actor, set(TEMPLATE_SHAPES["actor"]), f"{path}.actors.{actor_id}")
        _id(actor["kind"], f"{path}.actors.{actor_id}.kind")
    if set(bindings.values()) != set(actors):
        _reject("role_binding_mismatch", f"{path}.actor_role_bindings")

    actions = _unique_objects_by_id(domain["actions"], f"{path}.actions")
    if len(actions) != 4:
        _reject("wrong_cardinality", f"{path}.actions", str(len(actions)))
    roles: dict[str, str] = {}
    for action_id, action in actions.items():
        item_path = f"{path}.actions.{action_id}"
        _exact_object(action, set(TEMPLATE_SHAPES["action"]), item_path)
        role = _enum(
            action["role"], {"primary", "safe", "repair", "review"}, f"{item_path}.role"
        )
        if role in roles:
            _reject("duplicate_action_role", f"{item_path}.role", role)
        roles[role] = action_id
        if _id(action["actor_id"], f"{item_path}.actor_id") not in actors:
            _reject("dangling_reference", f"{item_path}.actor_id")
        _id(action["kind"], f"{item_path}.kind")
    if set(roles) != {"primary", "safe", "repair", "review"}:
        _reject("action_role_coverage", f"{path}.actions")

    relations = _unique_objects_by_id(domain["relations"], f"{path}.relations")
    if not relations:
        _reject("empty_registry", f"{path}.relations")
    for relation_id, relation in relations.items():
        item_path = f"{path}.relations.{relation_id}"
        _exact_object(relation, set(TEMPLATE_SHAPES["relation"]), item_path)
        _id(relation["kind"], f"{item_path}.kind")
        for ref_name in ("source_ref", "target_ref"):
            ref = _string(relation[ref_name], f"{item_path}.{ref_name}")
            try:
                sort, role = ref.split(":", 1)
            except ValueError:
                _reject("malformed_reference", f"{item_path}.{ref_name}", ref)
            if sort == "action" and role in roles:
                continue
            if sort == "actor" and role in bindings:
                continue
            _reject("wrong_sort_reference", f"{item_path}.{ref_name}", ref)

    fields = _unique_objects_by_id(
        domain["raw_state_fields"], f"{path}.raw_state_fields"
    )
    if not 3 <= len(fields) <= 8:
        _reject("wrong_cardinality", f"{path}.raw_state_fields", str(len(fields)))
    for field_id, field in fields.items():
        item_path = f"{path}.raw_state_fields.{field_id}"
        _exact_object(field, set(TEMPLATE_SHAPES["raw_state_field"]), item_path)
        _id(field["type"], f"{item_path}.type")
        values = _sorted_unique_strings(
            field["allowed_values"], f"{item_path}.allowed_values", require_sorted=False
        )
        if set(values) != {"unknown", "both"} | (set(values) - {"unknown", "both"}):
            _reject("state_value_coverage", f"{item_path}.allowed_values")
        if "unknown" not in values or "both" not in values or len(values) != 4:
            _reject("state_value_coverage", f"{item_path}.allowed_values")

    predicates = _unique_objects_by_id(
        domain["derived_predicates"], f"{path}.derived_predicates"
    )
    if len(predicates) != 2:
        _reject("wrong_cardinality", f"{path}.derived_predicates", str(len(predicates)))
    slots: dict[str, str] = {}
    predicate_fields: dict[str, set[str]] = {}
    for predicate_id, predicate in predicates.items():
        item_path = f"{path}.derived_predicates.{predicate_id}"
        _exact_object(predicate, set(TEMPLATE_SHAPES["derived_predicate"]), item_path)
        slot = _enum(
            predicate["slot"], {"primary_gate", "safe_gate"}, f"{item_path}.slot"
        )
        if slot in slots:
            _reject("duplicate_predicate_slot", f"{item_path}.slot", slot)
        slots[slot] = predicate_id
        predicate_fields[slot] = _expression_fields(
            predicate["expression"], fields, f"{item_path}.expression"
        )
        consumers = _list(predicate["consumed_by"], f"{item_path}.consumed_by")
        if not consumers:
            _reject("empty_application_set", f"{item_path}.consumed_by")
        for consumer_index, consumer in enumerate(consumers):
            _string(consumer, f"{item_path}.consumed_by[{consumer_index}]")
    if set(slots) != {"primary_gate", "safe_gate"}:
        _reject("predicate_slot_coverage", f"{path}.derived_predicates")
    if set().union(*predicate_fields.values()) != set(fields):
        _reject("dead_raw_state_field", f"{path}.raw_state_fields", domain_id)

    witnesses = _unique_objects_by_id(
        domain["witness_states"], f"{path}.witness_states"
    )
    if len(witnesses) != 4:
        _reject("wrong_cardinality", f"{path}.witness_states", str(len(witnesses)))
    raw_signatures: set[bytes] = set()
    for witness_id, witness in witnesses.items():
        item_path = f"{path}.witness_states.{witness_id}"
        _exact_object(witness, set(TEMPLATE_SHAPES["witness_state"]), item_path)
        raw_state = witness["raw_state"]
        _exact_object(raw_state, set(fields), f"{item_path}.raw_state")
        for field_id, value in raw_state.items():
            _enum(
                value,
                set(fields[field_id]["allowed_values"]),
                f"{item_path}.raw_state.{field_id}",
            )
        signature = canonical_bytes(raw_state)
        if signature in raw_signatures:
            _reject("duplicate_witness_state", f"{item_path}.raw_state")
        raw_signatures.add(signature)
        expected_truths = witness["expected_truths"]
        _exact_object(expected_truths, set(slots), f"{item_path}.expected_truths")
        for slot, predicate_id in slots.items():
            actual = evaluate_expression(
                predicates[predicate_id]["expression"], raw_state
            )
            expected = _enum(
                expected_truths[slot],
                set(TRUTHS),
                f"{item_path}.expected_truths.{slot}",
            )
            if actual != expected:
                _reject("witness_truth_mismatch", f"{item_path}.expected_truths.{slot}")

    mutations = _unique_objects_by_id(
        domain["causal_mutations"], f"{path}.causal_mutations"
    )
    if len(mutations) < 2:
        _reject("insufficient_causal_mutations", f"{path}.causal_mutations")
    for mutation_id, mutation in mutations.items():
        item_path = f"{path}.causal_mutations.{mutation_id}"
        _exact_object(mutation, set(TEMPLATE_SHAPES["causal_mutation"]), item_path)
        source = _id(mutation["from_witness"], f"{item_path}.from_witness")
        target = _id(mutation["to_witness"], f"{item_path}.to_witness")
        if source not in witnesses or target not in witnesses or source == target:
            _reject("dangling_reference", item_path, "witness mutation")
        changed = _sorted_unique_strings(
            mutation["changed_field_ids"],
            f"{item_path}.changed_field_ids",
            require_sorted=False,
        )
        actual_changed = sorted(
            field_id
            for field_id in fields
            if witnesses[source]["raw_state"][field_id]
            != witnesses[target]["raw_state"][field_id]
        )
        if sorted(changed) != actual_changed or len(changed) != 1:
            _reject("mutation_delta_mismatch", f"{item_path}.changed_field_ids")
        deltas = _list(
            mutation["expected_truth_delta"], f"{item_path}.expected_truth_delta"
        )
        targets = _list(
            mutation["disposition_targets"], f"{item_path}.disposition_targets"
        )
        if not deltas or not targets:
            _reject("empty_application_set", item_path)


def _validate_topology(topology: Any, index: int) -> None:
    path = f"$.topology_programs[{index}]"
    _exact_object(topology, set(TEMPLATE_SHAPES["topology_program"]), path)
    topology_id = _id(topology["id"], f"{path}.id")
    _string(topology["summary"], f"{path}.summary")
    _expect_equal(
        topology["kernel_projection"],
        "unclaimed_without_execution",
        f"{path}.kernel_projection",
    )

    norms = _unique_objects_by_id(topology["norms"], f"{path}.norms")
    if len(norms) not in {2, 3}:
        _reject("wrong_cardinality", f"{path}.norms", str(len(norms)))
    repair_edges: dict[str, str] = {}
    defeater_slots: set[str] = set()
    lifecycle_slots: set[str] = set()
    for norm_id, norm in norms.items():
        item_path = f"{path}.norms.{norm_id}"
        _exact_object(norm, set(TEMPLATE_SHAPES["norm"]), item_path)
        _enum(norm["operator"], {"O", "F", "P"}, f"{item_path}.operator")
        _enum(
            norm["source_actor_role"],
            {"operator", "authority", "affected", "reviewer"},
            f"{item_path}.source_actor_role",
        )
        _enum(
            norm["action_role"],
            {"primary", "safe", "repair", "review"},
            f"{item_path}.action_role",
        )
        refs = _list(norm["condition_refs"], f"{item_path}.condition_refs")
        if not refs:
            _reject("empty_condition", f"{item_path}.condition_refs")
        for ref_index, ref_value in enumerate(refs):
            ref_path = f"{item_path}.condition_refs[{ref_index}]"
            ref = _string(ref_value, ref_path)
            try:
                kind, target = ref.split(":", 1)
            except ValueError:
                _reject("malformed_reference", ref_path, ref)
            if kind == "evidence" and target == "e0":
                continue
            if kind == "domain" and target in {"primary_gate", "safe_gate"}:
                continue
            if kind in {"state", "violation"} and target in norms:
                continue
            _reject("wrong_sort_reference", ref_path, ref)
        _id(norm["source_id"], f"{item_path}.source_id")
        lifecycle_slots.add(_id(norm["lifecycle_slot"], f"{item_path}.lifecycle_slot"))
        defeater_slots.add(_id(norm["defeater_slot"], f"{item_path}.defeater_slot"))
        repair_for = _id(norm["repair_for"], f"{item_path}.repair_for", allow_none=True)
        if repair_for != "none":
            if repair_for not in norms or repair_for == norm_id:
                _reject(
                    "dangling_repair_reference", f"{item_path}.repair_for", repair_for
                )
            repair_edges[norm_id] = repair_for
    for start in repair_edges:
        seen: set[str] = set()
        cursor = start
        while cursor in repair_edges:
            if cursor in seen:
                _reject("repair_cycle", f"{path}.norms", start)
            seen.add(cursor)
            cursor = repair_edges[cursor]

    conflicts = _unique_objects_by_id(topology["conflicts"], f"{path}.conflicts")
    if len(conflicts) != 1:
        _reject("wrong_cardinality", f"{path}.conflicts", str(len(conflicts)))
    for conflict_id, conflict in conflicts.items():
        item_path = f"{path}.conflicts.{conflict_id}"
        _exact_object(conflict, set(TEMPLATE_SHAPES["conflict"]), item_path)
        left = _id(conflict["left_norm_id"], f"{item_path}.left_norm_id")
        right = _id(conflict["right_norm_id"], f"{item_path}.right_norm_id")
        if left not in norms or right not in norms or left == right:
            _reject("dangling_conflict_reference", item_path)
        _id(conflict["kind"], f"{item_path}.kind")

    states = _unique_objects_by_id(topology["state_variants"], f"{path}.state_variants")
    if len(states) != 4:
        _reject("wrong_cardinality", f"{path}.state_variants", str(len(states)))
    state_codes: set[int] = set()
    for state_id, state in states.items():
        item_path = f"{path}.state_variants.{state_id}"
        _exact_object(state, set(TEMPLATE_SHAPES["state_variant"]), item_path)
        code = _integer(state["code"], f"{item_path}.code", 0, 3)
        if code in state_codes:
            _reject("duplicate_code", f"{item_path}.code", str(code))
        state_codes.add(code)
        _id(state["domain_witness"], f"{item_path}.domain_witness")
        norm_states = state["norm_states"]
        _exact_object(norm_states, set(norms), f"{item_path}.norm_states")
        for norm_id, value in norm_states.items():
            _enum(
                value,
                {"active", "inactive", "satisfied", "violated", "unknown"},
                f"{item_path}.norm_states.{norm_id}",
            )
        flags = _list(state["flags"], f"{item_path}.flags")
        if not flags:
            _reject("empty_flags", f"{item_path}.flags")
        for flag_index, flag in enumerate(flags):
            _id(flag, f"{item_path}.flags[{flag_index}]")
    if state_codes != {0, 1, 2, 3}:
        _reject("variant_code_coverage", f"{path}.state_variants")

    resolutions = _unique_objects_by_id(
        topology["resolution_variants"], f"{path}.resolution_variants"
    )
    if len(resolutions) != 4:
        _reject(
            "wrong_cardinality", f"{path}.resolution_variants", str(len(resolutions))
        )
    resolution_codes: set[int] = set()
    resolution_signatures: set[bytes] = set()
    for resolution_id, resolution in resolutions.items():
        item_path = f"{path}.resolution_variants.{resolution_id}"
        _exact_object(resolution, set(TEMPLATE_SHAPES["resolution_variant"]), item_path)
        code = _integer(resolution["code"], f"{item_path}.code", 0, 3)
        if code in resolution_codes:
            _reject("duplicate_code", f"{item_path}.code", str(code))
        resolution_codes.add(code)
        edges = _list(resolution["priority_edges"], f"{item_path}.priority_edges")
        checked_edges: list[list[str]] = []
        for edge_index, edge in enumerate(edges):
            edge_path = f"{item_path}.priority_edges[{edge_index}]"
            pair = _list(edge, edge_path)
            if len(pair) != 2:
                _reject("wrong_cardinality", edge_path, str(len(pair)))
            higher = _id(pair[0], f"{edge_path}[0]")
            lower = _id(pair[1], f"{edge_path}[1]")
            if higher not in norms or lower not in norms or higher == lower:
                _reject("dangling_priority_reference", edge_path)
            checked_edges.append([higher, lower])
        if checked_edges != sorted(checked_edges) or len(
            {tuple(edge) for edge in checked_edges}
        ) != len(checked_edges):
            _reject("noncanonical_order", f"{item_path}.priority_edges")
        signature = canonical_bytes(checked_edges)
        if signature in resolution_signatures:
            _reject("duplicate_variant_semantics", item_path)
        resolution_signatures.add(signature)
        _id(resolution["expected_if_conflict"], f"{item_path}.expected_if_conflict")
    if resolution_codes != {0, 1, 2, 3}:
        _reject("variant_code_coverage", f"{path}.resolution_variants")

    defeaters = _unique_objects_by_id(
        topology["defeater_variants"], f"{path}.defeater_variants"
    )
    if len(defeaters) != 4:
        _reject("wrong_cardinality", f"{path}.defeater_variants", str(len(defeaters)))
    defeater_codes: set[int] = set()
    defeater_signatures: set[bytes] = set()
    for defeater_id, defeater in defeaters.items():
        item_path = f"{path}.defeater_variants.{defeater_id}"
        _exact_object(defeater, set(TEMPLATE_SHAPES["defeater_variant"]), item_path)
        code = _integer(defeater["code"], f"{item_path}.code", 0, 3)
        if code in defeater_codes:
            _reject("duplicate_code", f"{item_path}.code", str(code))
        defeater_codes.add(code)
        slot_truths = defeater["slot_truths"]
        if type(slot_truths) is not dict or not slot_truths:
            _reject("empty_application_set", f"{item_path}.slot_truths")
        if not set(slot_truths) <= defeater_slots:
            _reject("dangling_defeater_reference", f"{item_path}.slot_truths")
        for slot, truth in slot_truths.items():
            _id(slot, f"{item_path}.slot_truths.{slot}")
            _enum(truth, set(TRUTHS), f"{item_path}.slot_truths.{slot}")
        full_signature = {
            slot: slot_truths.get(slot, "F") for slot in sorted(defeater_slots)
        }
        signature = canonical_bytes(full_signature)
        if signature in defeater_signatures:
            _reject("duplicate_variant_semantics", item_path)
        defeater_signatures.add(signature)
        _id(defeater["expected_effect"], f"{item_path}.expected_effect")
    if defeater_codes != {0, 1, 2, 3}:
        _reject("variant_code_coverage", f"{path}.defeater_variants")

    targets = topology["application_targets"]
    _exact_object(targets, set(AXES), f"{path}.application_targets")
    for axis in AXES:
        values = _sorted_unique_strings(
            targets[axis], f"{path}.application_targets.{axis}", require_sorted=False
        )
        if not values:
            _reject("empty_application_set", f"{path}.application_targets.{axis}")
    if not set(targets["evidence"]) <= set(norms):
        _reject("dangling_reference", f"{path}.application_targets.evidence")
    if not set(targets["resolution"]) <= set(conflicts):
        _reject("dangling_reference", f"{path}.application_targets.resolution")
    if not set(targets["defeater"]) <= defeater_slots:
        _reject("dangling_reference", f"{path}.application_targets.defeater")
    if not set(targets["state"]) <= lifecycle_slots | set(norms):
        _reject("dangling_reference", f"{path}.application_targets.state")

    rules = _list(topology["validity_rules"], f"{path}.validity_rules")
    if not rules:
        _reject("empty_validity_rules", f"{path}.validity_rules")
    for rule_index, rule in enumerate(rules):
        _id(rule, f"{path}.validity_rules[{rule_index}]")

    if topology_id == "deadline_obligation_prohibition":
        state_by_code = {state["code"]: state for state in states.values()}
        for code in (1, 2):
            if state_by_code[code]["domain_witness"] != "both_gates_true":
                _reject(
                    "terminal_gate_inapplicable", f"{path}.state_variants", str(code)
                )
    if topology_id in {
        "ctd_repair_prohibition",
        "transaction_commit_rollback_conflict",
    }:
        state_by_code = {state["code"]: state for state in states.values()}
        for code, state in state_by_code.items():
            if (
                state["norm_states"].get("n0") == "violated"
                and state["domain_witness"] != "both_gates_true"
            ):
                _reject(
                    "terminal_gate_inapplicable", f"{path}.state_variants", str(code)
                )


def validate_template_bank(data: Any) -> dict[str, Any]:
    bank = _exact_object(data, TOP_FIELDS, "$")
    _expect_equal(bank["schema"], TEMPLATE_SCHEMA, "$.schema")
    _expect_equal(bank["profile_id"], PROFILE_ID, "$.profile_id")
    _expect_equal(
        bank["authoritative_status"],
        "synthetic_non_authoritative",
        "$.authoritative_status",
    )
    _string(bank["generation_method"], "$.generation_method")
    _expect_equal(
        bank["closed_shapes"],
        TEMPLATE_SHAPES,
        "$.closed_shapes",
        "template_shape_mismatch",
    )
    _expect_equal(
        bank["nonclaims"], list(NONCLAIMS), "$.nonclaims", "authority_boundary_mismatch"
    )

    factorization = _exact_object(
        bank["factorization"],
        {"formula", "record_count", "ordinal_order", "radices"},
        "$.factorization",
    )
    _expect_equal(factorization["formula"], "16*16*4*4*4*4", "$.factorization.formula")
    _integer(
        factorization["record_count"],
        "$.factorization.record_count",
        RECORD_COUNT,
        RECORD_COUNT,
    )
    _expect_equal(
        factorization["ordinal_order"],
        [
            "domain",
            "topology_program",
            "evidence_value",
            "local_state_variant",
            "resolution_variant",
            "defeater_variant",
        ],
        "$.factorization.ordinal_order",
    )
    _expect_equal(
        factorization["radices"], [16, 16, 4, 4, 4, 4], "$.factorization.radices"
    )

    language = _exact_object(
        bank["expression_language"],
        {"truth_values", "operators", "forms", "unknown_rule", "composition_rule"},
        "$.expression_language",
    )
    _expect_equal(
        language["truth_values"], list(TRUTHS), "$.expression_language.truth_values"
    )
    _expect_equal(
        language["operators"],
        ["eq", "all", "any", "not"],
        "$.expression_language.operators",
    )
    _exact_object(
        language["forms"], {"eq", "all", "any", "not"}, "$.expression_language.forms"
    )
    _string(language["unknown_rule"], "$.expression_language.unknown_rule")
    _string(language["composition_rule"], "$.expression_language.composition_rule")

    evidence_values = _list(bank["evidence_values"], "$.evidence_values")
    if len(evidence_values) != 4:
        _reject("wrong_cardinality", "$.evidence_values", str(len(evidence_values)))
    expected_evidence = [
        (0, "supported", "T"),
        (1, "refuted", "F"),
        (2, "unknown", "U"),
        (3, "inconsistent", "B"),
    ]
    for index, (item, expected) in enumerate(
        zip(evidence_values, expected_evidence, strict=True)
    ):
        path = f"$.evidence_values[{index}]"
        _exact_object(item, {"code", "id", "truth", "effect"}, path)
        _expect_equal((item["code"], item["id"], item["truth"]), expected, path)
        _id(item["effect"], f"{path}.effect")

    variants = _exact_object(
        bank["variant_codes"],
        {"local_state_variant", "resolution_variant", "defeater_variant"},
        "$.variant_codes",
    )
    for name, codes in variants.items():
        _expect_equal(codes, [0, 1, 2, 3], f"$.variant_codes.{name}")

    contract = _exact_object(
        bank["counterfactual_contract"],
        {
            "modifier_axes",
            "mutation",
            "unordered_value_pairs",
            "spanning_tree_edges",
            "spanning_applications",
            "required_receipt_fields",
            "behavior_change_classes",
            "unchanged_class",
            "negative_knowledge_rule",
        },
        "$.counterfactual_contract",
    )
    _expect_equal(
        contract["modifier_axes"],
        [
            "evidence_value",
            "local_state_variant",
            "resolution_variant",
            "defeater_variant",
        ],
        "$.counterfactual_contract.modifier_axes",
    )
    expected_pairs = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]
    _expect_equal(
        contract["unordered_value_pairs"],
        expected_pairs,
        "$.counterfactual_contract.unordered_value_pairs",
    )
    _expect_equal(
        contract["spanning_tree_edges"],
        [[0, 1], [0, 2], [0, 3]],
        "$.counterfactual_contract.spanning_tree_edges",
    )
    applications = _list(
        contract["spanning_applications"],
        "$.counterfactual_contract.spanning_applications",
    )
    expected_axis_names = [
        "evidence_value",
        "local_state_variant",
        "resolution_variant",
        "defeater_variant",
    ]
    if len(applications) != 4:
        _reject(
            "wrong_cardinality",
            "$.counterfactual_contract.spanning_applications",
            str(len(applications)),
        )
    for index, (application, axis_name) in enumerate(
        zip(applications, expected_axis_names, strict=True)
    ):
        item_path = f"$.counterfactual_contract.spanning_applications[{index}]"
        _exact_object(application, {"axis", "held_codes", "predicate"}, item_path)
        _expect_equal(application["axis"], axis_name, f"{item_path}.axis")
        held = application["held_codes"]
        _exact_object(
            held,
            set(expected_axis_names) - {axis_name},
            f"{item_path}.held_codes",
        )
        for held_name, code in held.items():
            _integer(code, f"{item_path}.held_codes.{held_name}", 0, 3)
        _expect_equal(
            application["predicate"],
            "normalized_results_differ_for_every_declared_edge",
            f"{item_path}.predicate",
        )
    for field in ("mutation", "unchanged_class", "negative_knowledge_rule"):
        _string(contract[field], f"$.counterfactual_contract.{field}")
    for field in ("required_receipt_fields", "behavior_change_classes"):
        values = _list(contract[field], f"$.counterfactual_contract.{field}")
        if not values:
            _reject("empty_application_set", f"$.counterfactual_contract.{field}")
        for index, value in enumerate(values):
            _id(value, f"$.counterfactual_contract.{field}[{index}]")

    domains = _list(bank["domains"], "$.domains")
    topologies = _list(bank["topology_programs"], "$.topology_programs")
    if len(domains) != 16 or len(topologies) != 16:
        _reject(
            "factorization_mismatch",
            "$",
            f"domains={len(domains)}, topologies={len(topologies)}",
        )
    for index, domain in enumerate(domains):
        _validate_domain(domain, index)
    for index, topology in enumerate(topologies):
        _validate_topology(topology, index)
    domain_ids = [
        _id(domain["id"], f"$.domains[{index}].id")
        for index, domain in enumerate(domains)
    ]
    topology_ids = [
        _id(topology["id"], f"$.topology_programs[{index}].id")
        for index, topology in enumerate(topologies)
    ]
    if len(set(domain_ids)) != 16 or len(set(topology_ids)) != 16:
        _reject("duplicate_id", "$", "domain or topology ID")
    return bank


def load_template_bank(
    path: str | Path, expected_sha256: str = EXPECTED_TEMPLATE_SHA256
) -> BoundTemplate:
    raw = _bound_file(Path(path), expected_sha256, MAX_TEMPLATE_BYTES)
    data = parse_json_exact(raw, canonical=False, max_bytes=MAX_TEMPLATE_BYTES)
    bank = validate_template_bank(data)
    domains = {domain["id"]: domain for domain in bank["domains"]}
    topologies = {topology["id"]: topology for topology in bank["topology_programs"]}
    return BoundTemplate(bank, expected_sha256, domains, topologies)


def rank_coordinate(codes: Sequence[int]) -> int:
    if len(codes) != 6:
        _reject("coordinate_arity", "coordinate", str(len(codes)))
    radices = (16, 16, 4, 4, 4, 4)
    ordinal = 0
    for index, (code, radix) in enumerate(zip(codes, radices, strict=True)):
        code = _integer(code, f"coordinate[{index}]", 0, radix - 1)
        ordinal = ordinal * radix + code
    return ordinal


def unrank_ordinal(ordinal: int) -> tuple[int, int, int, int, int, int]:
    value = _integer(ordinal, "ordinal", 0, RECORD_COUNT - 1)
    codes: list[int] = []
    for radix in reversed((16, 16, 4, 4, 4, 4)):
        codes.append(value % radix)
        value //= radix
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
    matches = [
        predicate
        for predicate in domain["derived_predicates"]
        if predicate["slot"] == slot
    ]
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


def _compile_lifecycle(
    topology_id: str,
    lifecycle_slot: str,
    state_code: int,
    state_value: str,
) -> dict[str, str]:
    if (
        topology_id == "deadline_obligation_prohibition"
        and lifecycle_slot == "deadline0"
    ):
        value = {
            0: "before_deadline_unperformed",
            1: "deadline_reached_timely_performed",
            2: "deadline_reached_late_performed",
            3: "deadline_reached_performance_unknown",
        }[state_code]
        return {"kind": "deadline", "value": value}
    return {"kind": "state", "value": state_value}


def _condition_ref(domain: Mapping[str, Any], raw_reference: str) -> dict[str, str]:
    kind, target = raw_reference.split(":", 1)
    if kind == "domain":
        predicate = _predicate_by_slot(domain, target)
        return {"kind": "fact", "id": predicate["id"]}
    return {"kind": kind, "id": target}


def compile_core(
    template: BoundTemplate,
    codes: Sequence[int],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Independently compile the semantic core for one coordinate."""

    ordinal = rank_coordinate(codes)
    (
        domain_code,
        topology_code,
        evidence_code,
        state_code,
        resolution_code,
        defeater_code,
    ) = unrank_ordinal(ordinal)
    domain = template.data["domains"][domain_code]
    topology = template.data["topology_programs"][topology_code]
    evidence_variant = template.data["evidence_values"][evidence_code]
    state_variant = _variant_by_code(topology["state_variants"], state_code)
    resolution_variant = _variant_by_code(
        topology["resolution_variants"], resolution_code
    )
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
        fields = sorted(
            _expression_fields(
                predicate["expression"], field_by_id, "compile.expression"
            )
        )
        facts.append(
            {
                "id": predicate["id"],
                "slot": predicate["slot"],
                "truth": evaluate_expression(predicate["expression"], raw_map),
                "evidence_ids": [],
                "derivation_rule_id": predicate["id"],
                "input_state_ids": fields,
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

    target_norm_ids = sorted(topology["application_targets"]["evidence"])
    evidence_payload = {
        "evidence_id": "e0",
        "target_norm_ids": target_norm_ids,
        "truth": evidence_variant["truth"],
    }
    evidence = [
        {
            "id": "e0",
            "kind": "synthetic_observation",
            "target_norm_ids": target_norm_ids,
            "truth": evidence_variant["truth"],
            "payload_sha256": canonical_hash(evidence_payload),
            "authority_status": "synthetic_non_authoritative",
        }
    ]

    norm_state = state_variant["norm_states"]
    norms: list[dict[str, Any]] = []
    for source_norm in topology["norms"]:
        action = _action_by_role(domain, source_norm["action_role"])
        condition_refs = [
            _condition_ref(domain, reference)
            for reference in source_norm["condition_refs"]
        ]
        condition_refs.sort(key=lambda item: (item["kind"], item["id"]))
        norms.append(
            {
                "id": source_norm["id"],
                "operator": source_norm["operator"],
                "source_actor_id": domain["actor_role_bindings"][
                    source_norm["source_actor_role"]
                ],
                "subject_id": action["actor_id"],
                "action_id": action["id"],
                "condition_refs": condition_refs,
                "source_id": source_norm["source_id"],
                "lifecycle": _compile_lifecycle(
                    topology["id"],
                    source_norm["lifecycle_slot"],
                    state_code,
                    norm_state[source_norm["id"]],
                ),
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
    priority_edges.sort(
        key=lambda item: (item["higher_norm_id"], item["lower_norm_id"])
    )
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
    coordinate = {
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
    return core, coordinate


def _validate_typed_ref(value: Any, path: str) -> tuple[str, str]:
    ref = _exact_object(value, {"kind", "id"}, path)
    kind = _enum(
        ref["kind"], {"actor", "action", "fact", "norm", "state"}, f"{path}.kind"
    )
    target = _id(ref["id"], f"{path}.id")
    return kind, target


def _validate_condition_ref(value: Any, path: str) -> tuple[str, str]:
    ref = _exact_object(value, {"kind", "id"}, path)
    kind = _enum(
        ref["kind"], {"evidence", "fact", "state", "violation"}, f"{path}.kind"
    )
    target = _id(ref["id"], f"{path}.id")
    return kind, target


def _validate_core_shape(core: Any) -> dict[str, Any]:
    value = _exact_object(core, CORE_FIELDS, "$.semantic_core")
    _id(value["domain_id"], "$.semantic_core.domain_id")

    actors = _unique_objects_by_id(
        value["actors"], "$.semantic_core.actors", require_sorted=True
    )
    for actor_id, actor in actors.items():
        path = f"$.semantic_core.actors.{actor_id}"
        _exact_object(actor, {"id", "role", "kind"}, path)
        _id(actor["role"], f"{path}.role")
        _id(actor["kind"], f"{path}.kind")

    actions = _unique_objects_by_id(
        value["actions"], "$.semantic_core.actions", require_sorted=True
    )
    action_roles: set[str] = set()
    for action_id, action in actions.items():
        path = f"$.semantic_core.actions.{action_id}"
        _exact_object(action, {"id", "role", "actor_id", "kind"}, path)
        role = _enum(
            action["role"], {"primary", "safe", "repair", "review"}, f"{path}.role"
        )
        if role in action_roles:
            _reject("duplicate_action_role", f"{path}.role", role)
        action_roles.add(role)
        actor_id = _id(action["actor_id"], f"{path}.actor_id")
        if actor_id not in actors:
            _reject("dangling_reference", f"{path}.actor_id", actor_id)
        _id(action["kind"], f"{path}.kind")

    states = _unique_objects_by_id(
        value["raw_state"], "$.semantic_core.raw_state", require_sorted=True
    )
    for state_id, state in states.items():
        path = f"$.semantic_core.raw_state.{state_id}"
        _exact_object(state, {"id", "type_id", "value_id"}, path)
        _id(state["type_id"], f"{path}.type_id")
        _id(state["value_id"], f"{path}.value_id")

    facts = _unique_objects_by_id(
        value["facts"], "$.semantic_core.facts", require_sorted=True
    )
    for fact_id, fact in facts.items():
        path = f"$.semantic_core.facts.{fact_id}"
        _exact_object(
            fact,
            {
                "id",
                "slot",
                "truth",
                "evidence_ids",
                "derivation_rule_id",
                "input_state_ids",
            },
            path,
        )
        _id(fact["slot"], f"{path}.slot")
        _enum(fact["truth"], set(TRUTHS), f"{path}.truth")
        _sorted_unique_strings(fact["evidence_ids"], f"{path}.evidence_ids")
        _id(fact["derivation_rule_id"], f"{path}.derivation_rule_id")
        inputs = _sorted_unique_strings(
            fact["input_state_ids"], f"{path}.input_state_ids"
        )
        for state_id in inputs:
            if state_id not in states:
                _reject("wrong_sort_reference", f"{path}.input_state_ids", state_id)

    evidence = _unique_objects_by_id(
        value["evidence"], "$.semantic_core.evidence", require_sorted=True
    )
    for evidence_id, item in evidence.items():
        path = f"$.semantic_core.evidence.{evidence_id}"
        _exact_object(
            item,
            {
                "id",
                "kind",
                "target_norm_ids",
                "truth",
                "payload_sha256",
                "authority_status",
            },
            path,
        )
        _expect_equal(item["kind"], "synthetic_observation", f"{path}.kind")
        _sorted_unique_strings(item["target_norm_ids"], f"{path}.target_norm_ids")
        _enum(item["truth"], set(TRUTHS), f"{path}.truth")
        _hash(item["payload_sha256"], f"{path}.payload_sha256")
        _expect_equal(
            item["authority_status"],
            "synthetic_non_authoritative",
            f"{path}.authority_status",
            "authority_boundary_mismatch",
        )

    norms = _unique_objects_by_id(
        value["norms"], "$.semantic_core.norms", require_sorted=True
    )
    for norm_id, norm in norms.items():
        path = f"$.semantic_core.norms.{norm_id}"
        _exact_object(
            norm,
            {
                "id",
                "operator",
                "source_actor_id",
                "subject_id",
                "action_id",
                "condition_refs",
                "source_id",
                "lifecycle",
                "defeater",
                "repair_for",
            },
            path,
        )
        _enum(norm["operator"], {"O", "F", "P"}, f"{path}.operator")
        source_actor_id = _id(norm["source_actor_id"], f"{path}.source_actor_id")
        subject_id = _id(norm["subject_id"], f"{path}.subject_id")
        action_id = _id(norm["action_id"], f"{path}.action_id")
        if source_actor_id not in actors:
            _reject("wrong_sort_reference", f"{path}.source_actor_id", source_actor_id)
        if subject_id not in actors:
            _reject("wrong_sort_reference", f"{path}.subject_id", subject_id)
        if action_id not in actions:
            _reject("wrong_sort_reference", f"{path}.action_id", action_id)
        if actions[action_id]["actor_id"] != subject_id:
            _reject("wrong_owner_reference", f"{path}.subject_id", subject_id)
        refs = _list(norm["condition_refs"], f"{path}.condition_refs")
        checked_refs = [
            _validate_condition_ref(ref, f"{path}.condition_refs[{index}]")
            for index, ref in enumerate(refs)
        ]
        if checked_refs != sorted(checked_refs):
            _reject("noncanonical_order", f"{path}.condition_refs")
        if len(set(checked_refs)) != len(checked_refs):
            _reject("duplicate_reference", f"{path}.condition_refs")
        state_mirrors = [target for kind, target in checked_refs if kind == "state"]
        if state_mirrors != [norm_id]:
            _reject(
                "state_mirror_mismatch", f"{path}.condition_refs", str(state_mirrors)
            )
        violation_gates = [
            target for kind, target in checked_refs if kind == "violation"
        ]
        _id(norm["source_id"], f"{path}.source_id")
        lifecycle = norm["lifecycle"]
        if type(lifecycle) is not dict or "kind" not in lifecycle:
            _reject("wrong_type", f"{path}.lifecycle", "expected lifecycle object")
        if lifecycle["kind"] == "state":
            _exact_object(lifecycle, {"kind", "value"}, f"{path}.lifecycle")
            _enum(
                lifecycle["value"],
                {"active", "inactive", "satisfied", "violated", "unknown"},
                f"{path}.lifecycle.value",
            )
        elif lifecycle["kind"] == "deadline":
            _exact_object(lifecycle, {"kind", "value"}, f"{path}.lifecycle")
            deadline_value = _string(lifecycle["value"], f"{path}.lifecycle.value")
            if deadline_value not in {
                "before_deadline_unperformed",
                "deadline_reached_timely_performed",
                "deadline_reached_late_performed",
                "deadline_reached_performance_unknown",
            }:
                _reject(
                    "invalid_deadline_state",
                    f"{path}.lifecycle.value",
                    deadline_value,
                )
            if norm["operator"] == "P":
                _reject("unsupported_deadline_operator", path, norm_id)
        else:
            _reject("unknown_enum", f"{path}.lifecycle.kind", str(lifecycle["kind"]))
        defeater = _exact_object(
            norm["defeater"], {"kind", "fact_id"}, f"{path}.defeater"
        )
        _expect_equal(defeater["kind"], "unless", f"{path}.defeater.kind")
        fact_id = _id(defeater["fact_id"], f"{path}.defeater.fact_id")
        if fact_id not in facts:
            _reject("wrong_sort_reference", f"{path}.defeater.fact_id", fact_id)
        _id(norm["repair_for"], f"{path}.repair_for", allow_none=True)
        if norm["repair_for"] == "none" and violation_gates:
            _reject("unexpected_repair_gate", f"{path}.condition_refs")
        if norm["repair_for"] != "none" and violation_gates != [norm["repair_for"]]:
            _reject("repair_gate_mismatch", f"{path}.condition_refs")

    for evidence_id, item in evidence.items():
        for norm_id in item["target_norm_ids"]:
            if norm_id not in norms:
                _reject(
                    "wrong_sort_reference",
                    f"$.semantic_core.evidence.{evidence_id}.target_norm_ids",
                    norm_id,
                )
        expected_payload = {
            "evidence_id": evidence_id,
            "target_norm_ids": item["target_norm_ids"],
            "truth": item["truth"],
        }
        if item["payload_sha256"] != canonical_hash(expected_payload):
            _reject(
                "payload_hash_mismatch",
                f"$.semantic_core.evidence.{evidence_id}.payload_sha256",
            )
    for fact_id, fact in facts.items():
        for evidence_id in fact["evidence_ids"]:
            if evidence_id not in evidence:
                _reject(
                    "wrong_sort_reference",
                    f"$.semantic_core.facts.{fact_id}.evidence_ids",
                    evidence_id,
                )

    for norm_id, norm in norms.items():
        path = f"$.semantic_core.norms.{norm_id}"
        for kind, target in (
            _validate_condition_ref(ref, f"{path}.condition_refs[{index}]")
            for index, ref in enumerate(norm["condition_refs"])
        ):
            registry = {
                "evidence": evidence,
                "fact": facts,
                "state": norms,
                "violation": norms,
            }[kind]
            if target not in registry:
                _reject(
                    "wrong_sort_reference", f"{path}.condition_refs", f"{kind}:{target}"
                )
        repair_for = norm["repair_for"]
        if repair_for != "none":
            if repair_for not in norms or repair_for == norm_id:
                _reject("dangling_repair_reference", f"{path}.repair_for", repair_for)
            if norms[repair_for]["repair_for"] != "none":
                _reject("nested_repair_forbidden", f"{path}.repair_for", repair_for)

    repair_providers: Counter[str] = Counter(
        norm["repair_for"]
        for norm in norms.values()
        if norm["repair_for"] != "none" and norm["operator"] == "O"
    )
    for primary, count in repair_providers.items():
        if count > 1:
            _reject("multiple_repair_providers", "$.semantic_core.norms", primary)

    relations = _unique_objects_by_id(
        value["relations"], "$.semantic_core.relations", require_sorted=True
    )
    registries = {
        "actor": actors,
        "action": actions,
        "fact": facts,
        "norm": norms,
        "state": states,
    }
    for relation_id, relation in relations.items():
        path = f"$.semantic_core.relations.{relation_id}"
        _exact_object(relation, {"id", "kind", "source_ref", "target_ref"}, path)
        _id(relation["kind"], f"{path}.kind")
        for name in ("source_ref", "target_ref"):
            kind, target = _validate_typed_ref(relation[name], f"{path}.{name}")
            if target not in registries[kind]:
                _reject("wrong_sort_reference", f"{path}.{name}", f"{kind}:{target}")

    conflicts = _unique_objects_by_id(
        value["conflicts"], "$.semantic_core.conflicts", require_sorted=True
    )
    for conflict_id, conflict in conflicts.items():
        path = f"$.semantic_core.conflicts.{conflict_id}"
        _exact_object(conflict, {"id", "left_norm_id", "right_norm_id", "kind"}, path)
        left = _id(conflict["left_norm_id"], f"{path}.left_norm_id")
        right = _id(conflict["right_norm_id"], f"{path}.right_norm_id")
        if left not in norms or right not in norms or left == right:
            _reject("dangling_conflict_reference", path)
        _id(conflict["kind"], f"{path}.kind")

    priority_edges = _list(value["priority_edges"], "$.semantic_core.priority_edges")
    checked_edges: list[tuple[str, str]] = []
    for index, edge in enumerate(priority_edges):
        path = f"$.semantic_core.priority_edges[{index}]"
        _exact_object(edge, {"higher_norm_id", "lower_norm_id"}, path)
        higher = _id(edge["higher_norm_id"], f"{path}.higher_norm_id")
        lower = _id(edge["lower_norm_id"], f"{path}.lower_norm_id")
        if higher not in norms or lower not in norms or higher == lower:
            _reject("dangling_priority_reference", path)
        checked_edges.append((higher, lower))
    if checked_edges != sorted(checked_edges) or len(set(checked_edges)) != len(
        checked_edges
    ):
        _reject("noncanonical_order", "$.semantic_core.priority_edges")

    query = _exact_object(
        value["query"],
        {"mode", "alternative_action_ids", "omission_admissible", "fallback_action_id"},
        "$.semantic_core.query",
    )
    _expect_equal(query["mode"], "single_action", "$.semantic_core.query.mode")
    alternatives = _sorted_unique_strings(
        query["alternative_action_ids"], "$.semantic_core.query.alternative_action_ids"
    )
    if set(alternatives) != set(actions):
        _reject("alternative_coverage", "$.semantic_core.query.alternative_action_ids")
    _expect_equal(
        _boolean(
            query["omission_admissible"], "$.semantic_core.query.omission_admissible"
        ),
        False,
        "$.semantic_core.query.omission_admissible",
    )
    fallback_action = _id(
        query["fallback_action_id"], "$.semantic_core.query.fallback_action_id"
    )
    if fallback_action not in actions or actions[fallback_action]["role"] != "review":
        _reject(
            "invalid_fallback_action",
            "$.semantic_core.query.fallback_action_id",
            fallback_action,
        )
    return value


def _without_lifecycle(norm: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in norm.items() if key != "lifecycle"}


def _first_difference(left: Any, right: Any, path: str = "$") -> str | None:
    if type(left) is not type(right):
        return path
    if type(left) is dict:
        if set(left) != set(right):
            return path
        for key in sorted(left):
            difference = _first_difference(left[key], right[key], f"{path}.{key}")
            if difference is not None:
                return difference
        return None
    if type(left) is list:
        if len(left) != len(right):
            return path
        for index, (left_item, right_item) in enumerate(zip(left, right, strict=True)):
            difference = _first_difference(left_item, right_item, f"{path}[{index}]")
            if difference is not None:
                return difference
        return None
    return None if left == right else path


def derive_coordinate(
    template: BoundTemplate, core: Mapping[str, Any]
) -> tuple[tuple[int, int, int, int, int, int], dict[str, Any]]:
    """Derive all six codes from semantic content, never from record metadata."""

    domain_matches = [
        index
        for index, domain in enumerate(template.data["domains"])
        if domain["id"] == core["domain_id"]
    ]
    if len(domain_matches) != 1:
        _reject("unknown_domain", "$.semantic_core.domain_id", str(core["domain_id"]))
    domain_code = domain_matches[0]

    if len(core["evidence"]) != 1 or core["evidence"][0]["id"] != "e0":
        _reject("evidence_registry_mismatch", "$.semantic_core.evidence")
    evidence_truth = core["evidence"][0]["truth"]
    evidence_matches = [
        index
        for index, evidence in enumerate(template.data["evidence_values"])
        if evidence["truth"] == evidence_truth
    ]
    if len(evidence_matches) != 1:
        _reject("evidence_axis_ambiguous", "$.semantic_core.evidence[0].truth")
    evidence_code = evidence_matches[0]

    topology_matches: list[int] = []
    for topology_code in range(16):
        candidate, _ = compile_core(
            template, (domain_code, topology_code, evidence_code, 0, 0, 0)
        )
        static_match = (
            [_without_lifecycle(norm) for norm in core["norms"]]
            == [_without_lifecycle(norm) for norm in candidate["norms"]]
            and core["conflicts"] == candidate["conflicts"]
            and core["actors"] == candidate["actors"]
            and core["actions"] == candidate["actions"]
            and core["relations"] == candidate["relations"]
            and core["query"] == candidate["query"]
        )
        if static_match:
            topology_matches.append(topology_code)
    if len(topology_matches) != 1:
        _reject(
            "topology_axis_ambiguous", "$.semantic_core.norms", str(topology_matches)
        )
    topology_code = topology_matches[0]

    state_matches: list[int] = []
    for state_code in range(4):
        candidate, _ = compile_core(
            template, (domain_code, topology_code, evidence_code, state_code, 0, 0)
        )
        if core["raw_state"] == candidate["raw_state"] and [
            norm["lifecycle"] for norm in core["norms"]
        ] == [norm["lifecycle"] for norm in candidate["norms"]]:
            state_matches.append(state_code)
    if len(state_matches) != 1:
        _reject("state_axis_ambiguous", "$.semantic_core.raw_state", str(state_matches))
    state_code = state_matches[0]

    resolution_matches: list[int] = []
    for resolution_code in range(4):
        candidate, _ = compile_core(
            template,
            (domain_code, topology_code, evidence_code, state_code, resolution_code, 0),
        )
        if core["priority_edges"] == candidate["priority_edges"]:
            resolution_matches.append(resolution_code)
    if len(resolution_matches) != 1:
        _reject(
            "resolution_axis_ambiguous",
            "$.semantic_core.priority_edges",
            str(resolution_matches),
        )
    resolution_code = resolution_matches[0]

    actual_defeater_facts = [
        fact
        for fact in core["facts"]
        if fact["derivation_rule_id"] == "defeater_axis_v1"
    ]
    defeater_matches: list[int] = []
    for defeater_code in range(4):
        candidate, _ = compile_core(
            template,
            (
                domain_code,
                topology_code,
                evidence_code,
                state_code,
                resolution_code,
                defeater_code,
            ),
        )
        expected_defeater_facts = [
            fact
            for fact in candidate["facts"]
            if fact["derivation_rule_id"] == "defeater_axis_v1"
        ]
        if actual_defeater_facts == expected_defeater_facts:
            defeater_matches.append(defeater_code)
    if len(defeater_matches) != 1:
        _reject(
            "defeater_axis_ambiguous", "$.semantic_core.facts", str(defeater_matches)
        )
    defeater_code = defeater_matches[0]

    codes = (
        domain_code,
        topology_code,
        evidence_code,
        state_code,
        resolution_code,
        defeater_code,
    )
    expected_core, coordinate = compile_core(template, codes)
    difference = _first_difference(core, expected_core, "$.semantic_core")
    if difference is not None:
        _reject("semantic_core_mismatch", difference)
    return codes, coordinate


def _lifecycle_label(lifecycle: Mapping[str, str]) -> str:
    return lifecycle["value"]


def _priority_reachable(
    source: str, target: str, edges: Sequence[Mapping[str, str]]
) -> bool:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        adjacency[edge["higher_norm_id"]].add(edge["lower_norm_id"])
    frontier = [source]
    seen: set[str] = set()
    while frontier:
        current = frontier.pop()
        if current in seen:
            continue
        seen.add(current)
        if current == target and current != source:
            return True
        frontier.extend(sorted(adjacency[current] - seen, reverse=True))
    return target in adjacency[source] if source == target else target in seen


def _ordinary_guard_truth(
    norm: Mapping[str, Any],
    facts: Mapping[str, Mapping[str, Any]],
    evidence: Mapping[str, Mapping[str, Any]],
) -> str:
    values: list[str] = []
    for ref in norm["condition_refs"]:
        kind = ref["kind"]
        target = ref["id"]
        if kind in {"state", "violation"}:
            # State is an integrity mirror and violation is a separate repair
            # gate.  Neither participates in the ordinary guard conjunction.
            continue
        if kind == "fact":
            values.append(facts[target]["truth"])
        elif kind == "evidence":
            values.append(evidence[target]["truth"])
        else:  # pragma: no cover - shape validation rejects this branch
            _reject("unknown_condition_kind", "condition", str(kind))
    return truth_all(values) if values else "T"


def _lifecycle_disposition(
    norm: Mapping[str, Any],
) -> tuple[str, str | None]:
    """Return a disposition and an optional lifecycle blocker."""

    lifecycle = norm["lifecycle"]
    if lifecycle["kind"] == "state":
        value = lifecycle["value"]
        if value == "unknown":
            return "blocked_unknown", "unknown_lifecycle"
        return value, None
    value = lifecycle["value"]
    if value == "before_deadline_unperformed":
        return "active", None
    if value == "deadline_reached_timely_performed":
        return ("satisfied", None) if norm["operator"] == "O" else ("violated", None)
    if value == "deadline_reached_late_performed":
        return "violated", None
    if value == "deadline_reached_performance_unknown":
        return "blocked_unknown", "unknown_deadline"
    _reject("invalid_deadline_state", f"norm.{norm['id']}.lifecycle", value)


def _violation_truth(disposition: str) -> str:
    if disposition == "violated":
        return "T"
    if disposition in {"inactive", "active", "satisfied", "defeated"}:
        return "F"
    if disposition == "blocked_unknown":
        return "U"
    if disposition == "blocked_inconsistent":
        return "B"
    _reject("unknown_disposition", "violation_truth", disposition)


def evaluate_core(core: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate a validated v1 semantic core from first principles."""

    raw_state = {cell["id"]: cell["value_id"] for cell in core["raw_state"]}
    facts = {fact["id"]: fact for fact in core["facts"]}
    evidence = {item["id"]: item for item in core["evidence"]}
    norms = {norm["id"]: norm for norm in core["norms"]}

    predicate_steps = [
        {
            "fact_id": fact["id"],
            "rule_id": fact["derivation_rule_id"],
            "input_state_ids": list(fact["input_state_ids"]),
            "input_values": [
                raw_state[state_id] for state_id in fact["input_state_ids"]
            ],
            "truth": fact["truth"],
        }
        for fact in core["facts"]
    ]

    blockers: set[str] = set()
    norm_steps_by_id: dict[str, dict[str, Any]] = {}
    pre_dispositions: dict[str, str] = {}

    def ordinary_evaluation(
        norm: Mapping[str, Any], ordinary_guard: str, defeater_truth: str
    ) -> tuple[str, list[str]]:
        reasons: list[str] = []
        if ordinary_guard == "F":
            return "inactive", ["condition_false"]
        if ordinary_guard == "U":
            blockers.add("unknown_condition")
            return "blocked_unknown", ["unknown_condition"]
        if ordinary_guard == "B":
            blockers.add("inconsistent_condition")
            return "blocked_inconsistent", ["inconsistent_condition"]
        if defeater_truth == "T":
            return "defeated", ["defeater_true"]
        if defeater_truth == "U":
            blockers.add("unknown_defeater")
            return "blocked_unknown", ["unknown_defeater"]
        if defeater_truth == "B":
            blockers.add("inconsistent_defeater")
            return "blocked_inconsistent", ["inconsistent_defeater"]
        disposition, blocker = _lifecycle_disposition(norm)
        if blocker is not None:
            blockers.add(blocker)
            reasons.append(blocker)
        else:
            reasons.append(f"lifecycle_{disposition}")
        return disposition, reasons

    def record_norm(
        norm: Mapping[str, Any],
        repair_gate: str,
        ordinary_guard: str,
        defeater_truth: str,
        disposition: str,
        reasons: Sequence[str],
    ) -> None:
        norm_id = norm["id"]
        pre_dispositions[norm_id] = disposition
        norm_steps_by_id[norm_id] = {
            "norm_id": norm_id,
            "repair_gate_truth": repair_gate,
            "ordinary_guard_truth": ordinary_guard,
            "defeater_truth": defeater_truth,
            "lifecycle_value": _lifecycle_label(norm["lifecycle"]),
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
        ordinary_guard = _ordinary_guard_truth(norm, facts, evidence)
        defeater_truth = facts[norm["defeater"]["fact_id"]]["truth"]
        disposition, reasons = ordinary_evaluation(norm, ordinary_guard, defeater_truth)
        record_norm(norm, "none", ordinary_guard, defeater_truth, disposition, reasons)

    primary_violation_truths = {
        norm["id"]: _violation_truth(pre_dispositions[norm["id"]])
        for norm in non_repairs
    }
    activated_repairs: set[str] = set()
    for norm in repairs:
        primary = norm["repair_for"]
        gate = primary_violation_truths[primary]
        ordinary_guard = _ordinary_guard_truth(norm, facts, evidence)
        defeater_truth = facts[norm["defeater"]["fact_id"]]["truth"]
        if gate == "F":
            disposition = "inactive"
            reasons = ["primary_not_violated"]
        elif gate == "U":
            disposition = "blocked_unknown"
            blockers.add("unknown_primary_violation")
            reasons = ["unknown_primary_violation"]
        elif gate == "B":
            disposition = "blocked_inconsistent"
            blockers.add("inconsistent_primary_violation")
            reasons = ["inconsistent_primary_violation"]
        else:
            activated_repairs.add(norm["id"])
            disposition, reasons = ordinary_evaluation(
                norm, ordinary_guard, defeater_truth
            )
        record_norm(
            norm,
            gate,
            ordinary_guard,
            defeater_truth,
            disposition,
            reasons,
        )

    conflict_steps: list[dict[str, Any]] = []
    priority_losers: set[str] = set()
    for conflict in core["conflicts"]:
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
                priority_losers.add(right)
            elif right_reaches and not left_reaches:
                disposition = "right_wins"
                loser = left
                priority_losers.add(left)
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
    for norm_id in sorted(priority_losers):
        final_dispositions[norm_id] = "defeated"
        step = norm_steps_by_id[norm_id]
        step["final_disposition"] = "defeated"
        step["reason_codes"] = sorted(set(step["reason_codes"]) | {"priority_defeated"})

    norm_violation_truths = [
        {"norm_id": norm_id, "truth": _violation_truth(final_dispositions[norm_id])}
        for norm_id in sorted(norms)
    ]
    final_violation_by_id = {
        item["norm_id"]: item["truth"] for item in norm_violation_truths
    }

    repair_groups: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for norm in repairs:
        repair_groups[norm["repair_for"]].append(norm)
    repair_availability: list[dict[str, Any]] = []
    repair_steps: list[dict[str, Any]] = []
    for primary in sorted(repair_groups):
        linked = sorted(norm["id"] for norm in repair_groups[primary])
        providers = sorted(
            norm["id"] for norm in repair_groups[primary] if norm["operator"] == "O"
        )
        if len(providers) > 1:
            _reject("multiple_repair_providers", f"repair_family.{primary}")
        provider = providers[0] if providers else "none"
        provider_disposition = (
            final_dispositions[provider] if provider != "none" else "none"
        )
        violation_truth = final_violation_by_id[primary]
        if violation_truth == "F":
            availability = "not_triggered"
        elif violation_truth == "U":
            availability = "blocked_unknown"
            blockers.update(
                {"unknown_primary_violation", "unknown_repair_availability"}
            )
        elif violation_truth == "B":
            availability = "blocked_inconsistent"
            blockers.update(
                {
                    "inconsistent_primary_violation",
                    "inconsistent_repair_availability",
                }
            )
        elif provider == "none":
            availability = "absent"
            blockers.add("repair_unavailable")
        else:
            availability = provider_disposition
            if provider_disposition in {"violated", "defeated", "inactive"}:
                blockers.add("repair_unavailable")
            elif provider_disposition == "blocked_unknown":
                blockers.add("unknown_repair_availability")
            elif provider_disposition == "blocked_inconsistent":
                blockers.add("inconsistent_repair_availability")
        availability_item = {
            "primary_norm_id": primary,
            "primary_violation_truth": violation_truth,
            "linked_norm_ids": linked,
            "provider_norm_id": provider,
            "provider_disposition": provider_disposition,
            "availability": availability,
        }
        repair_availability.append(availability_item)
        repair_steps.append(
            {**availability_item, "reason_codes": [f"repair_{availability}"]}
        )

    active = {
        norm_id
        for norm_id, disposition in final_dispositions.items()
        if disposition == "active"
    }
    defeated = {
        norm_id
        for norm_id, disposition in final_dispositions.items()
        if disposition == "defeated"
    }
    satisfied = {
        norm_id
        for norm_id, disposition in final_dispositions.items()
        if disposition == "satisfied"
    }
    violated = {
        norm_id
        for norm_id, disposition in final_dispositions.items()
        if disposition == "violated"
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
            admissible = set(required)
            executable_permitted = set(required)
        else:
            admissible = permitted - forbidden
            executable_permitted = set(admissible)

    alternatives = set(core["query"]["alternative_action_ids"])
    rejected = alternatives - admissible
    admissibility_steps: list[dict[str, Any]] = []
    for action_id in sorted(alternatives):
        admitted = action_id in admissible
        reasons: set[str] = set()
        if blockers:
            reasons.update(blockers)
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

    proof_trace = {
        "predicate_steps": predicate_steps,
        "norm_steps": [
            norm_steps_by_id[norm_id] for norm_id in sorted(norm_steps_by_id)
        ],
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
        "norm_violation_truths": norm_violation_truths,
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
    return result


def _validate_proof_trace(trace: Any, path: str) -> None:
    value = _exact_object(
        trace,
        {
            "predicate_steps",
            "norm_steps",
            "repair_steps",
            "conflict_steps",
            "admissibility_steps",
        },
        path,
    )
    predicates = _list(value["predicate_steps"], f"{path}.predicate_steps")
    predicate_ids: list[str] = []
    for index, step in enumerate(predicates):
        item_path = f"{path}.predicate_steps[{index}]"
        _exact_object(
            step,
            {"fact_id", "rule_id", "input_state_ids", "input_values", "truth"},
            item_path,
        )
        predicate_ids.append(_id(step["fact_id"], f"{item_path}.fact_id"))
        _id(step["rule_id"], f"{item_path}.rule_id")
        input_ids = _sorted_unique_strings(
            step["input_state_ids"], f"{item_path}.input_state_ids"
        )
        input_values = _list(step["input_values"], f"{item_path}.input_values")
        if len(input_ids) != len(input_values):
            _reject("trace_arity_mismatch", item_path)
        for value_index, input_value in enumerate(input_values):
            _id(input_value, f"{item_path}.input_values[{value_index}]")
        _enum(step["truth"], set(TRUTHS), f"{item_path}.truth")
    if predicate_ids != sorted(predicate_ids) or len(set(predicate_ids)) != len(
        predicate_ids
    ):
        _reject("noncanonical_order", f"{path}.predicate_steps")

    norm_steps = _list(value["norm_steps"], f"{path}.norm_steps")
    norm_ids: list[str] = []
    for index, step in enumerate(norm_steps):
        item_path = f"{path}.norm_steps[{index}]"
        _exact_object(
            step,
            {
                "norm_id",
                "repair_gate_truth",
                "ordinary_guard_truth",
                "defeater_truth",
                "lifecycle_value",
                "pre_conflict_disposition",
                "final_disposition",
                "reason_codes",
            },
            item_path,
        )
        norm_ids.append(_id(step["norm_id"], f"{item_path}.norm_id"))
        _enum(
            step["repair_gate_truth"],
            {"none", *TRUTHS},
            f"{item_path}.repair_gate_truth",
        )
        _enum(
            step["ordinary_guard_truth"],
            set(TRUTHS),
            f"{item_path}.ordinary_guard_truth",
        )
        _enum(step["defeater_truth"], set(TRUTHS), f"{item_path}.defeater_truth")
        _id(step["lifecycle_value"], f"{item_path}.lifecycle_value")
        _enum(
            step["pre_conflict_disposition"],
            NORM_DISPOSITIONS,
            f"{item_path}.pre_conflict_disposition",
        )
        _enum(
            step["final_disposition"],
            NORM_DISPOSITIONS,
            f"{item_path}.final_disposition",
        )
        _sorted_unique_strings(step["reason_codes"], f"{item_path}.reason_codes")
    if norm_ids != sorted(norm_ids) or len(set(norm_ids)) != len(norm_ids):
        _reject("noncanonical_order", f"{path}.norm_steps")

    repair_steps = _list(value["repair_steps"], f"{path}.repair_steps")
    repair_ids: list[str] = []
    for index, step in enumerate(repair_steps):
        item_path = f"{path}.repair_steps[{index}]"
        _exact_object(
            step,
            {
                "primary_norm_id",
                "primary_violation_truth",
                "linked_norm_ids",
                "provider_norm_id",
                "provider_disposition",
                "availability",
                "reason_codes",
            },
            item_path,
        )
        repair_ids.append(_id(step["primary_norm_id"], f"{item_path}.primary_norm_id"))
        _enum(
            step["primary_violation_truth"],
            set(TRUTHS),
            f"{item_path}.primary_violation_truth",
        )
        _sorted_unique_strings(step["linked_norm_ids"], f"{item_path}.linked_norm_ids")
        _id(step["provider_norm_id"], f"{item_path}.provider_norm_id", allow_none=True)
        _enum(
            step["provider_disposition"],
            {"none", *NORM_DISPOSITIONS},
            f"{item_path}.provider_disposition",
        )
        _enum(
            step["availability"],
            REPAIR_AVAILABILITIES,
            f"{item_path}.availability",
        )
        _sorted_unique_strings(step["reason_codes"], f"{item_path}.reason_codes")
    if repair_ids != sorted(repair_ids) or len(set(repair_ids)) != len(repair_ids):
        _reject("noncanonical_order", f"{path}.repair_steps")

    conflict_steps = _list(value["conflict_steps"], f"{path}.conflict_steps")
    conflict_ids: list[str] = []
    for index, step in enumerate(conflict_steps):
        item_path = f"{path}.conflict_steps[{index}]"
        _exact_object(
            step,
            {
                "conflict_id",
                "left_active",
                "right_active",
                "left_reaches_right",
                "right_reaches_left",
                "disposition",
                "defeated_norm_id",
            },
            item_path,
        )
        conflict_ids.append(_id(step["conflict_id"], f"{item_path}.conflict_id"))
        for field in (
            "left_active",
            "right_active",
            "left_reaches_right",
            "right_reaches_left",
        ):
            _boolean(step[field], f"{item_path}.{field}")
        _id(step["disposition"], f"{item_path}.disposition")
        _id(step["defeated_norm_id"], f"{item_path}.defeated_norm_id", allow_none=True)
    if conflict_ids != sorted(conflict_ids) or len(set(conflict_ids)) != len(
        conflict_ids
    ):
        _reject("noncanonical_order", f"{path}.conflict_steps")

    admissibility_steps = _list(
        value["admissibility_steps"], f"{path}.admissibility_steps"
    )
    action_ids: list[str] = []
    for index, step in enumerate(admissibility_steps):
        item_path = f"{path}.admissibility_steps[{index}]"
        _exact_object(
            step,
            {
                "action_id",
                "required",
                "permitted",
                "forbidden",
                "admitted",
                "reason_codes",
            },
            item_path,
        )
        action_ids.append(_id(step["action_id"], f"{item_path}.action_id"))
        for field in ("required", "permitted", "forbidden", "admitted"):
            _boolean(step[field], f"{item_path}.{field}")
        _sorted_unique_strings(step["reason_codes"], f"{item_path}.reason_codes")
    if action_ids != sorted(action_ids) or len(set(action_ids)) != len(action_ids):
        _reject("noncanonical_order", f"{path}.admissibility_steps")


def validate_result_shape(
    result: Any, path: str = "$.generator_claim"
) -> dict[str, Any]:
    value = _exact_object(result, RESULT_FIELDS, path)
    _expect_equal(value["schema"], RESULT_SCHEMA, f"{path}.schema")
    _enum(value["status"], {"resolved", "unresolved"}, f"{path}.status")
    _enum(value["fallback"], {"none", "abstain", "escalate"}, f"{path}.fallback")
    _sorted_unique_strings(
        value["blocker_codes"],
        f"{path}.blocker_codes",
        allowed=BLOCKER_CODES,
    )
    for field in (
        "active_norm_ids",
        "defeated_norm_ids",
        "satisfied_norm_ids",
        "violated_norm_ids",
        "activated_repair_norm_ids",
        "diagnostic_required_action_ids",
        "diagnostic_permitted_action_ids",
        "diagnostic_forbidden_action_ids",
        "executable_required_action_ids",
        "executable_permitted_action_ids",
        "admissible_action_ids",
        "rejected_action_ids",
    ):
        _sorted_unique_strings(value[field], f"{path}.{field}")
    violation_items = _list(
        value["norm_violation_truths"], f"{path}.norm_violation_truths"
    )
    violation_ids: list[str] = []
    for index, item in enumerate(violation_items):
        item_path = f"{path}.norm_violation_truths[{index}]"
        _exact_object(item, {"norm_id", "truth"}, item_path)
        violation_ids.append(_id(item["norm_id"], f"{item_path}.norm_id"))
        _enum(item["truth"], set(TRUTHS), f"{item_path}.truth")
    if violation_ids != sorted(violation_ids) or len(set(violation_ids)) != len(
        violation_ids
    ):
        _reject("noncanonical_order", f"{path}.norm_violation_truths")

    availability_items = _list(
        value["repair_availability"], f"{path}.repair_availability"
    )
    primary_ids: list[str] = []
    for index, item in enumerate(availability_items):
        item_path = f"{path}.repair_availability[{index}]"
        _exact_object(
            item,
            {
                "primary_norm_id",
                "primary_violation_truth",
                "linked_norm_ids",
                "provider_norm_id",
                "provider_disposition",
                "availability",
            },
            item_path,
        )
        primary_ids.append(_id(item["primary_norm_id"], f"{item_path}.primary_norm_id"))
        _enum(
            item["primary_violation_truth"],
            set(TRUTHS),
            f"{item_path}.primary_violation_truth",
        )
        _sorted_unique_strings(item["linked_norm_ids"], f"{item_path}.linked_norm_ids")
        _id(item["provider_norm_id"], f"{item_path}.provider_norm_id", allow_none=True)
        _enum(
            item["provider_disposition"],
            {"none", *NORM_DISPOSITIONS},
            f"{item_path}.provider_disposition",
        )
        _enum(
            item["availability"],
            REPAIR_AVAILABILITIES,
            f"{item_path}.availability",
        )
    if primary_ids != sorted(primary_ids) or len(set(primary_ids)) != len(primary_ids):
        _reject("noncanonical_order", f"{path}.repair_availability")
    _validate_proof_trace(value["proof_trace"], f"{path}.proof_trace")
    proof_hash = _hash(value["proof_trace_sha256"], f"{path}.proof_trace_sha256")
    if proof_hash != canonical_hash(value["proof_trace"]):
        _reject("proof_trace_hash_mismatch", f"{path}.proof_trace_sha256")
    result_hash = _hash(value["result_sha256"], f"{path}.result_sha256")
    hash_input = {key: item for key, item in value.items() if key != "result_sha256"}
    if result_hash != canonical_hash(hash_input):
        _reject("result_hash_mismatch", f"{path}.result_sha256")
    return value


def _validate_coordinate_shape(
    value: Any, path: str = "$.coordinate"
) -> dict[str, Any]:
    coordinate = _exact_object(value, COORDINATE_FIELDS, path)
    for field, high in (
        ("domain_code", 15),
        ("topology_code", 15),
        ("evidence_code", 3),
        ("state_code", 3),
        ("resolution_code", 3),
        ("defeater_code", 3),
    ):
        _integer(coordinate[field], f"{path}.{field}", 0, high)
    for field in (
        "domain_id",
        "topology_id",
        "evidence_id",
        "state_id",
        "resolution_id",
        "defeater_id",
    ):
        _id(coordinate[field], f"{path}.{field}")
    return coordinate


def _validate_profile_ref(
    value: Any,
    template_sha256: str,
    semantics_sha256: str,
    path: str = "$.profile_ref",
) -> None:
    profile = _exact_object(value, PROFILE_REF_FIELDS, path)
    _expect_equal(
        profile["profile_id"], PROFILE_ID, f"{path}.profile_id", "profile_mismatch"
    )
    template_hash = _hash(
        profile["template_bank_sha256"], f"{path}.template_bank_sha256"
    )
    semantics_hash = _hash(
        profile["semantics_spec_sha256"], f"{path}.semantics_spec_sha256"
    )
    if template_hash != template_sha256:
        _reject("profile_hash_mismatch", f"{path}.template_bank_sha256")
    if semantics_hash != semantics_sha256:
        _reject("profile_hash_mismatch", f"{path}.semantics_spec_sha256")


def _validate_authority(value: Any, path: str = "$.authority") -> None:
    authority = _exact_object(value, AUTHORITY_FIELDS, path)
    for field in ("may_authorize_external_effects", "may_be_cited_as_law"):
        _boolean(authority[field], f"{path}.{field}")
    if authority != AUTHORITY:
        _reject("authority_boundary_mismatch", path)


def normalize_result(
    result: Mapping[str, Any],
    core: Mapping[str, Any],
) -> dict[str, Any]:
    """Construct exact alpha-minimized ``NormalizedDispositionV1``."""

    norm_ids = sorted(norm["id"] for norm in core["norms"])
    norms = {norm["id"]: norm for norm in core["norms"]}
    norm_steps = {step["norm_id"]: step for step in result["proof_trace"]["norm_steps"]}
    violation_truths = {
        item["norm_id"]: item["truth"] for item in result["norm_violation_truths"]
    }
    actors = {actor["id"]: actor["role"] for actor in core["actors"]}
    action_roles = {action["id"]: action["role"] for action in core["actions"]}
    conflicts = {conflict["id"]: conflict for conflict in core["conflicts"]}
    conflict_steps = {
        step["conflict_id"]: step for step in result["proof_trace"]["conflict_steps"]
    }

    def lifecycle_category(norm: Mapping[str, Any], step: Mapping[str, Any]) -> str:
        gate_reached = step["repair_gate_truth"] in {"none", "T"}
        lifecycle_reached = (
            gate_reached
            and step["ordinary_guard_truth"] == "T"
            and step["defeater_truth"] == "F"
        )
        if not lifecycle_reached:
            return "none"
        lifecycle = norm["lifecycle"]
        return f"{lifecycle['kind']}:{lifecycle['value']}"

    def build(candidate_order: Sequence[str]) -> dict[str, Any]:
        role = {norm_id: index for index, norm_id in enumerate(candidate_order)}
        normalized_norms: list[dict[str, Any]] = []
        for norm_id in norm_ids:
            norm = norms[norm_id]
            step = norm_steps[norm_id]
            normalized_norms.append(
                {
                    "role": role[norm_id],
                    "operator": norm["operator"],
                    "source_actor_role": actors[norm["source_actor_id"]],
                    "action_role": action_roles[norm["action_id"]],
                    "repair_for_role": (
                        "none"
                        if norm["repair_for"] == "none"
                        else role[norm["repair_for"]]
                    ),
                    "repair_gate_truth": step["repair_gate_truth"],
                    "evaluated_lifecycle_category": lifecycle_category(norm, step),
                    "pre_conflict_disposition": step["pre_conflict_disposition"],
                    "final_disposition": step["final_disposition"],
                    "violation_truth": violation_truths[norm_id],
                }
            )
        normalized_norms.sort(key=lambda item: item["role"])

        normalized_conflicts: list[dict[str, Any]] = []
        for conflict_id in sorted(conflicts):
            conflict = conflicts[conflict_id]
            step = conflict_steps[conflict_id]
            if not (step["left_active"] and step["right_active"]):
                disposition = "dormant"
            else:
                disposition = {
                    "left_wins": "left_wins",
                    "right_wins": "right_wins",
                    "blocked_unresolved_priority": "unresolved",
                    "blocked_priority_cycle": "cycle",
                }[step["disposition"]]
            loser = step["defeated_norm_id"]
            normalized_conflicts.append(
                {
                    "left_role": role[conflict["left_norm_id"]],
                    "right_role": role[conflict["right_norm_id"]],
                    "operational_disposition": disposition,
                    "defeated_role": "none" if loser == "none" else role[loser],
                }
            )
        normalized_conflicts.sort(
            key=lambda item: (item["left_role"], item["right_role"])
        )

        normalized_repairs: list[dict[str, Any]] = []
        for family in result["repair_availability"]:
            provider = family["provider_norm_id"]
            normalized_repairs.append(
                {
                    "primary_role": role[family["primary_norm_id"]],
                    "primary_violation_truth": family["primary_violation_truth"],
                    "linked_roles": sorted(
                        role[norm_id] for norm_id in family["linked_norm_ids"]
                    ),
                    "provider_role": "none" if provider == "none" else role[provider],
                    "provider_disposition": family["provider_disposition"],
                    "availability": family["availability"],
                }
            )
        normalized_repairs.sort(key=lambda item: item["primary_role"])

        memberships = {
            field: set(result[field])
            for field in (
                "diagnostic_required_action_ids",
                "diagnostic_permitted_action_ids",
                "diagnostic_forbidden_action_ids",
                "executable_required_action_ids",
                "executable_permitted_action_ids",
                "admissible_action_ids",
                "rejected_action_ids",
            )
        }
        action_by_role = {action["role"]: action["id"] for action in core["actions"]}
        normalized_actions = []
        for action_role in ("primary", "safe", "repair", "review"):
            action_id = action_by_role[action_role]
            normalized_actions.append(
                {
                    "role": action_role,
                    "diagnostic_required": action_id
                    in memberships["diagnostic_required_action_ids"],
                    "diagnostic_permitted": action_id
                    in memberships["diagnostic_permitted_action_ids"],
                    "diagnostic_forbidden": action_id
                    in memberships["diagnostic_forbidden_action_ids"],
                    "executable_required": action_id
                    in memberships["executable_required_action_ids"],
                    "executable_permitted": action_id
                    in memberships["executable_permitted_action_ids"],
                    "admissible": action_id in memberships["admissible_action_ids"],
                    "rejected": action_id in memberships["rejected_action_ids"],
                }
            )
        return {
            "schema": NORMALIZATION_SCHEMA,
            "status": result["status"],
            "fallback": result["fallback"],
            "blocker_codes": list(result["blocker_codes"]),
            "norms": normalized_norms,
            "activated_repair_norm_roles": sorted(
                role[norm_id] for norm_id in result["activated_repair_norm_ids"]
            ),
            "conflicts": normalized_conflicts,
            "repair_families": normalized_repairs,
            "actions": normalized_actions,
        }

    best_bytes: bytes | None = None
    best: dict[str, Any] | None = None
    for candidate_order in itertools.permutations(norm_ids):
        candidate = build(candidate_order)
        encoded = canonical_bytes(candidate)
        if best_bytes is None or encoded < best_bytes:
            best_bytes = encoded
            best = candidate
    if best is None:  # pragma: no cover - valid cores always contain norms
        _reject("empty_norm_registry", "$.semantic_core.norms")
    return best


def verify_record(
    raw: bytes,
    template: BoundTemplate,
    *,
    semantics_sha256: str = EXPECTED_SEMANTICS_SHA256,
) -> VerifiedCase:
    record = parse_json_exact(raw, canonical=True, max_bytes=MAX_RECORD_BYTES)
    value = _exact_object(record, CASE_FIELDS, "$")
    _expect_equal(value["schema"], CASE_SCHEMA, "$.schema")
    ordinal = _integer(value["ordinal"], "$.ordinal", 0, RECORD_COUNT - 1)
    declared_coordinate = _validate_coordinate_shape(value["coordinate"])
    _validate_profile_ref(value["profile_ref"], template.sha256, semantics_sha256)
    _validate_authority(value["authority"])
    if value["nonclaims"] != list(NONCLAIMS):
        _reject("authority_boundary_mismatch", "$.nonclaims")

    core = _validate_core_shape(value["semantic_core"])
    core_hash = _hash(value["semantic_core_sha256"], "$.semantic_core_sha256")
    recomputed_core_hash = canonical_hash(core)
    if core_hash != recomputed_core_hash:
        _reject("semantic_core_hash_mismatch", "$.semantic_core_sha256")
    stable_id = _string(value["stable_id"], "$.stable_id")
    if stable_id != f"sdk-luna-v1-{core_hash}":
        _reject("stable_id_mismatch", "$.stable_id")

    codes, derived_coordinate = derive_coordinate(template, core)
    if declared_coordinate != derived_coordinate:
        difference = _first_difference(
            declared_coordinate, derived_coordinate, "$.coordinate"
        )
        _reject("coordinate_mismatch", difference or "$.coordinate")
    recomputed_ordinal = rank_coordinate(codes)
    if ordinal != recomputed_ordinal:
        _reject("ordinal_mismatch", "$.ordinal", f"expected {recomputed_ordinal}")

    claim = validate_result_shape(value["generator_claim"])
    expected_result = evaluate_core(core)
    if claim != expected_result:
        difference = _first_difference(claim, expected_result, "$.generator_claim")
        _reject("generator_claim_mismatch", difference or "$.generator_claim")

    declared_record_hash = _hash(value["record_sha256"], "$.record_sha256")
    hash_input = {key: item for key, item in value.items() if key != "record_sha256"}
    recomputed_record_hash = canonical_hash(hash_input)
    if declared_record_hash != recomputed_record_hash:
        _reject("record_hash_mismatch", "$.record_sha256")

    normalized = normalize_result(expected_result, core)
    return VerifiedCase(
        ordinal=ordinal,
        codes=codes,
        domain_id=derived_coordinate["domain_id"],
        topology_id=derived_coordinate["topology_id"],
        stable_id=stable_id,
        record_sha256=declared_record_hash,
        result_sha256=expected_result["result_sha256"],
        normalized_sha256=canonical_hash(normalized),
        normalized=normalized,
        status=expected_result["status"],
        fallback=expected_result["fallback"],
    )


def build_reference_record(
    template: BoundTemplate,
    codes: Sequence[int],
    *,
    semantics_sha256: str = EXPECTED_SEMANTICS_SHA256,
) -> dict[str, Any]:
    """Build an oracle-owned golden record for boundary and mutation tests."""

    core, coordinate = compile_core(template, codes)
    core_hash = canonical_hash(core)
    result = evaluate_core(core)
    record: dict[str, Any] = {
        "schema": CASE_SCHEMA,
        "ordinal": rank_coordinate(codes),
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


def encode_reference_record(
    template: BoundTemplate,
    codes: Sequence[int],
    *,
    semantics_sha256: str = EXPECTED_SEMANTICS_SHA256,
) -> bytes:
    return canonical_bytes(
        build_reference_record(template, codes, semantics_sha256=semantics_sha256)
    )


def _all_differences(left: Any, right: Any, path: str = "$") -> list[str]:
    if type(left) is not type(right):
        return [path]
    if type(left) is dict:
        paths: list[str] = []
        for key in sorted(set(left) | set(right)):
            child_path = f"{path}.{key}"
            if key not in left or key not in right:
                paths.append(child_path)
            else:
                paths.extend(_all_differences(left[key], right[key], child_path))
        return paths
    if type(left) is list:
        paths = []
        for index in range(max(len(left), len(right))):
            child_path = f"{path}[{index}]"
            if index >= len(left) or index >= len(right):
                paths.append(child_path)
            else:
                paths.extend(_all_differences(left[index], right[index], child_path))
        return paths
    return [] if left == right else [path]


def _indexed_field(path: str, collection: str, field: str) -> int | None:
    match = re.fullmatch(
        rf"\$\.semantic_core\.{re.escape(collection)}\[(\d+)\]\."
        rf"{re.escape(field)}",
        path,
    )
    return int(match.group(1)) if match else None


def _resolution_variant_edges(topology: Mapping[str, Any]) -> set[bytes]:
    return {
        canonical_bytes(
            sorted(
                (
                    {
                        "higher_norm_id": edge[0],
                        "lower_norm_id": edge[1],
                    }
                    for edge in variant["priority_edges"]
                ),
                key=lambda item: (item["higher_norm_id"], item["lower_norm_id"]),
            )
        )
        for variant in topology["resolution_variants"]
    }


def _axis_change_is_closed(
    axis: str,
    changed_paths: Sequence[str],
    before_core: Mapping[str, Any],
    after_core: Mapping[str, Any],
    topology: Mapping[str, Any],
) -> bool:
    """Check the actual diff against the frozen field-level axis closure."""

    if axis not in AXES or not changed_paths:
        return False
    actual_paths = sorted(_all_differences(before_core, after_core, "$.semantic_core"))
    if list(changed_paths) != actual_paths:
        return False
    targets = topology["application_targets"]

    if axis == "evidence":
        for path in actual_paths:
            index = _indexed_field(path, "evidence", "truth")
            if index is None:
                index = _indexed_field(path, "evidence", "payload_sha256")
            if index is None:
                return False
            try:
                before_item = before_core["evidence"][index]
                after_item = after_core["evidence"][index]
            except (IndexError, KeyError, TypeError):
                return False
            if (
                before_item.get("id") != "e0"
                or after_item.get("id") != "e0"
                or before_item.get("target_norm_ids") != sorted(targets["evidence"])
                or after_item.get("target_norm_ids") != sorted(targets["evidence"])
            ):
                return False
        return True

    if axis == "state":
        topology_norms = {norm["id"]: norm for norm in topology["norms"]}
        state_targets = set(targets["state"])
        for path in actual_paths:
            raw_index = _indexed_field(path, "raw_state", "value_id")
            if raw_index is not None:
                continue
            fact_index = _indexed_field(path, "facts", "truth")
            if fact_index is not None:
                try:
                    before_fact = before_core["facts"][fact_index]
                    after_fact = after_core["facts"][fact_index]
                except (IndexError, KeyError, TypeError):
                    return False
                if (
                    before_fact.get("derivation_rule_id") == "defeater_axis_v1"
                    or after_fact.get("derivation_rule_id") == "defeater_axis_v1"
                ):
                    return False
                continue
            norm_index = _indexed_field(path, "norms", "lifecycle.value")
            if norm_index is None:
                return False
            try:
                before_norm = before_core["norms"][norm_index]
                after_norm = after_core["norms"][norm_index]
            except (IndexError, KeyError, TypeError):
                return False
            if before_norm.get("id") != after_norm.get("id"):
                return False
            topology_norm = topology_norms.get(before_norm.get("id"))
            if topology_norm is None or not (
                topology_norm["id"] in state_targets
                or topology_norm["lifecycle_slot"] in state_targets
            ):
                return False
        return True

    if axis == "resolution":
        if not all(
            path == "$.semantic_core.priority_edges"
            or path.startswith("$.semantic_core.priority_edges[")
            for path in actual_paths
        ):
            return False
        conflict_ids = {conflict["id"] for conflict in topology["conflicts"]}
        if not targets["resolution"] or not set(targets["resolution"]) <= conflict_ids:
            return False
        variants = _resolution_variant_edges(topology)
        return (
            canonical_bytes(before_core["priority_edges"]) in variants
            and canonical_bytes(after_core["priority_edges"]) in variants
        )

    for path in actual_paths:
        fact_index = _indexed_field(path, "facts", "truth")
        if fact_index is None:
            return False
        try:
            before_fact = before_core["facts"][fact_index]
            after_fact = after_core["facts"][fact_index]
        except (IndexError, KeyError, TypeError):
            return False
        if (
            before_fact.get("id") != after_fact.get("id")
            or before_fact.get("id") not in targets["defeater"]
            or before_fact.get("derivation_rule_id") != "defeater_axis_v1"
            or after_fact.get("derivation_rule_id") != "defeater_axis_v1"
        ):
            return False
    return True


def _dependency_closure(topology: Mapping[str, Any], axis: str) -> list[str]:
    targets = sorted(topology["application_targets"][axis])
    base = {
        "evidence": ["semantic_core.evidence"],
        "state": [
            "semantic_core.raw_state",
            "semantic_core.derived_facts",
            "semantic_core.norm_lifecycle",
        ],
        "resolution": [
            "semantic_core.priority_edges",
            "semantic_core.conflict_resolution",
        ],
        "defeater": ["semantic_core.defeater_facts", "semantic_core.norm_defeat"],
    }[axis]
    return sorted(base + [f"application_target.{axis}.{target}" for target in targets])


def _source_sha256() -> str:
    return sha256_bytes(Path(__file__).read_bytes())


def _reference_case(template: BoundTemplate, codes: Sequence[int]) -> VerifiedCase:
    raw = encode_reference_record(template, codes)
    return verify_record(raw, template)


def _reconcile_verified_cases(
    cases: Sequence[VerifiedCase],
    template: BoundTemplate,
    *,
    case_paths: Sequence[str] | None = None,
) -> _ReconciledCaseSet:
    """Rebuild each supplied case once and retain only canonical oracle values."""

    supplied_cases = tuple(cases)
    if case_paths is not None and len(case_paths) != len(supplied_cases):
        _reject("internal_reconciliation_error", "reconcile.case_paths")
    canonical_cases: list[VerifiedCase] = []
    for index, supplied in enumerate(supplied_cases):
        rebuilt = _reference_case(template, supplied.codes)
        if supplied != rebuilt:
            path = (
                case_paths[index]
                if case_paths is not None
                else f"analyze.cases[{index}]"
            )
            _reject("verified_case_tamper", path)
        canonical_cases.append(rebuilt)
    frozen_cases = tuple(canonical_cases)
    owned_index = {case.ordinal: case for case in frozen_cases}
    return _ReconciledCaseSet(
        _template_sha256=template.sha256,
        _cases=frozen_cases,
        _cases_by_ordinal=MappingProxyType(owned_index),
        _seal=_RECONCILED_CASE_SET_SEAL,
    )


def _counterfactual_receipt_reconciled(
    reconciled: _ReconciledCaseSet,
    before_ordinal: int,
    after_ordinal: int,
    *,
    axis: str,
    template: BoundTemplate,
    oracle_source_sha256: str | None = None,
    evaluator_source_sha256: str | None = None,
) -> dict[str, Any]:
    """Classify endpoints admitted by one private reconciliation boundary."""

    if axis not in AXES:
        _reject("unknown_axis", "counterfactual.axis", axis)
    if (
        type(reconciled) is not _ReconciledCaseSet
        or reconciled._seal is not _RECONCILED_CASE_SET_SEAL
        or reconciled._template_sha256 != template.sha256
    ):
        _reject("unreconciled_case_set", "counterfactual.internal")
    try:
        before = reconciled._cases_by_ordinal[before_ordinal]
        after = reconciled._cases_by_ordinal[after_ordinal]
    except KeyError:
        _reject("unreconciled_case", "counterfactual.ordinal")
    if before.ordinal > after.ordinal:
        before, after = after, before
    axis_index = AXES.index(axis) + 2
    differences = [
        index
        for index, (left, right) in enumerate(
            zip(before.codes, after.codes, strict=True)
        )
        if left != right
    ]
    if differences != [axis_index]:
        _reject("not_one_axis_pair", "counterfactual.codes", str(differences))
    before_core, _ = compile_core(template, before.codes)
    after_core, _ = compile_core(template, after.codes)
    changed_paths = sorted(_all_differences(before_core, after_core, "$.semantic_core"))
    topology = template.data["topology_programs"][before.codes[1]]
    if not _axis_change_is_closed(
        axis, changed_paths, before_core, after_core, topology
    ):
        _reject("axis_dependency_escape", "counterfactual.changed_semantic_paths", axis)
    source_hash = oracle_source_sha256 or _source_sha256()
    evaluator_hash = evaluator_source_sha256 or source_hash
    coordinate_fields = [
        "domain_code",
        "topology_code",
        "evidence_code",
        "state_code",
        "resolution_code",
        "defeater_code",
    ]
    unchanged_fields = sorted(
        field for index, field in enumerate(coordinate_fields) if index != axis_index
    )
    receipt_body: dict[str, Any] = {
        "schema": RECEIPT_SCHEMA,
        "changed_axis": axis,
        "before": {
            "ordinal": before.ordinal,
            "stable_id": before.stable_id,
            "record_sha256": before.record_sha256,
            "result_sha256": before.result_sha256,
        },
        "after": {
            "ordinal": after.ordinal,
            "stable_id": after.stable_id,
            "record_sha256": after.record_sha256,
            "result_sha256": after.result_sha256,
        },
        "unchanged_coordinate_fields": unchanged_fields,
        "changed_semantic_paths": changed_paths,
        "allowed_dependency_closure": _dependency_closure(topology, axis),
        "normalized_before_sha256": before.normalized_sha256,
        "normalized_after_sha256": after.normalized_sha256,
        "classification": (
            "EFFECT"
            if before.normalized_sha256 != after.normalized_sha256
            else "INVARIANT"
        ),
        "semantics_spec_sha256": EXPECTED_SEMANTICS_SHA256,
        "template_bank_sha256": template.sha256,
        "oracle_source_sha256": source_hash,
        "evaluator_source_sha256": evaluator_hash,
    }
    receipt_id = canonical_hash(receipt_body)
    receipt = {"receipt_id": receipt_id, **receipt_body}
    receipt["receipt_sha256"] = canonical_hash(receipt)
    return receipt


def counterfactual_receipt(
    before: VerifiedCase,
    after: VerifiedCase,
    *,
    axis: str,
    template: BoundTemplate,
    oracle_source_sha256: str | None = None,
    evaluator_source_sha256: str | None = None,
) -> dict[str, Any]:
    """Rebuild and classify one exact unordered one-axis pair."""

    if axis not in AXES:
        _reject("unknown_axis", "counterfactual.axis", axis)
    reconciled = _reconcile_verified_cases(
        (before, after),
        template,
        case_paths=("counterfactual.before", "counterfactual.after"),
    )
    return _counterfactual_receipt_reconciled(
        reconciled,
        reconciled._cases[0].ordinal,
        reconciled._cases[1].ordinal,
        axis=axis,
        template=template,
        oracle_source_sha256=oracle_source_sha256,
        evaluator_source_sha256=evaluator_source_sha256,
    )


def _gate(
    gate_id: str,
    status: str,
    checked_count: int,
    threshold: str,
    *,
    counterexamples: Sequence[str] = (),
    detail: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if status not in {"PASS", "FAIL", "SKIP"}:
        _reject("unknown_gate_status", f"gate.{gate_id}", status)
    return {
        "gate_id": gate_id,
        "status": status,
        "checked_count": checked_count,
        "threshold": threshold,
        "counterexample_ids": sorted(set(counterexamples))[:64],
        "detail": dict(detail or {}),
    }


def unbound_evidence_gate_status(*, corpus_complete: bool, precheck_pass: bool) -> str:
    """Return an honest gate status when no durable evidence binding is supplied.

    A successful in-memory precheck is useful diagnostic evidence, but it is not
    a replayable release artifact.  This standalone analyzer intentionally has
    no input that can confer that missing authority, so this function can never
    return ``PASS``.
    """

    if type(corpus_complete) is not bool or type(precheck_pass) is not bool:
        _reject("wrong_type", "gate.precheck", "expected exact booleans")
    return "SKIP" if corpus_complete and precheck_pass else "FAIL"


def _domain_fingerprint(domain: Mapping[str, Any]) -> str:
    field_index = {
        field["id"]: index for index, field in enumerate(domain["raw_state_fields"])
    }
    actor_index = {actor["id"]: index for index, actor in enumerate(domain["actors"])}
    action_index = {action["id"]: action["role"] for action in domain["actions"]}

    def expression_shape(expression: Any) -> Any:
        if expression[0] == "eq":
            field = domain["raw_state_fields"][field_index[expression[1]]]
            literal_index = field["allowed_values"].index(expression[2])
            return ["eq", field_index[expression[1]], literal_index]
        return [expression[0], *[expression_shape(child) for child in expression[1:]]]

    normalized = {
        "actor_kinds": sorted(actor["kind"] for actor in domain["actors"]),
        "actions": sorted(
            [
                action["role"],
                actor_index[action["actor_id"]],
                action["kind"],
            ]
            for action in domain["actions"]
        ),
        "relations": sorted(
            [
                relation["kind"],
                relation["source_ref"].split(":", 1)[0],
                relation["target_ref"].split(":", 1)[0],
            ]
            for relation in domain["relations"]
        ),
        "field_types": [field["type"] for field in domain["raw_state_fields"]],
        "predicates": sorted(
            [predicate["slot"], expression_shape(predicate["expression"])]
            for predicate in domain["derived_predicates"]
        ),
        "mutations": sorted(
            [
                [field_index[field_id] for field_id in mutation["changed_field_ids"]],
                mutation["expected_truth_delta"],
                mutation["disposition_targets"],
            ]
            for mutation in domain["causal_mutations"]
        ),
        "action_roles": sorted(action_index.values()),
    }
    return canonical_hash(normalized)


def _topology_fingerprint(topology: Mapping[str, Any]) -> str:
    norm_index = {norm["id"]: index for index, norm in enumerate(topology["norms"])}
    conflict_index = {
        conflict["id"]: index for index, conflict in enumerate(topology["conflicts"])
    }
    normalized = {
        "norms": [
            {
                "operator": norm["operator"],
                "source_role": norm["source_actor_role"],
                "action_role": norm["action_role"],
                "conditions": [ref.split(":", 1)[0] for ref in norm["condition_refs"]],
                "lifecycle_kind": (
                    "deadline" if norm["lifecycle_slot"] == "deadline0" else "state"
                ),
                "repair_for": (
                    "none"
                    if norm["repair_for"] == "none"
                    else norm_index[norm["repair_for"]]
                ),
            }
            for norm in topology["norms"]
        ],
        "conflicts": [
            [
                norm_index[conflict["left_norm_id"]],
                norm_index[conflict["right_norm_id"]],
                conflict["kind"],
            ]
            for conflict in topology["conflicts"]
        ],
        "states": [
            [
                state["code"],
                [state["norm_states"][norm["id"]] for norm in topology["norms"]],
                sorted(state["flags"]),
            ]
            for state in sorted(
                topology["state_variants"], key=lambda item: item["code"]
            )
        ],
        "resolutions": [
            [
                resolution["code"],
                [
                    [norm_index[higher], norm_index[lower]]
                    for higher, lower in resolution["priority_edges"]
                ],
            ]
            for resolution in sorted(
                topology["resolution_variants"], key=lambda item: item["code"]
            )
        ],
        "defeaters": [
            [
                variant["code"],
                [
                    variant["slot_truths"].get(norm["defeater_slot"], "F")
                    for norm in topology["norms"]
                ],
            ]
            for variant in sorted(
                topology["defeater_variants"], key=lambda item: item["code"]
            )
        ],
        "targets": {
            "evidence_norms": [
                norm_index[target]
                for target in topology["application_targets"]["evidence"]
            ],
            "resolution_conflicts": [
                conflict_index[target]
                for target in topology["application_targets"]["resolution"]
            ],
            "state_count": len(topology["application_targets"]["state"]),
            "defeater_count": len(topology["application_targets"]["defeater"]),
        },
    }
    return canonical_hash(normalized)


def _record_outcome(case: VerifiedCase) -> str:
    if case.status == "resolved":
        return "resolved"
    return f"unresolved_{case.fallback}"


def analyze_verified_cases(
    cases: Sequence[VerifiedCase],
    template: BoundTemplate,
    *,
    rejected_records: Sequence[OracleReject] = (),
    enumerate_counterfactuals: bool = True,
    receipt_sink: Any | None = None,
) -> dict[str, Any]:
    """Compute release diagnostics without assigning unexecuted tool claims."""

    reconciled = _reconcile_verified_cases(cases, template)
    cases = reconciled._cases
    by_ordinal: dict[int, VerifiedCase] = {}
    duplicate_ids: list[str] = []
    stable_ids: set[str] = set()
    record_hashes: set[str] = set()
    for case in cases:
        if case.ordinal in by_ordinal:
            duplicate_ids.append(f"ordinal_{case.ordinal}")
        by_ordinal[case.ordinal] = case
        if case.stable_id in stable_ids:
            duplicate_ids.append(case.stable_id)
        stable_ids.add(case.stable_id)
        if case.record_sha256 in record_hashes:
            duplicate_ids.append(case.record_sha256)
        record_hashes.add(case.record_sha256)
    missing = sorted(set(range(RECORD_COUNT)) - set(by_ordinal))
    full = (
        not rejected_records
        and not duplicate_ids
        and len(cases) == RECORD_COUNT
        and not missing
    )

    gate_results: list[dict[str, Any]] = [
        _gate("G00", "SKIP", 0, "external frozen release-subject receipt required"),
        _gate(
            "G01",
            unbound_evidence_gate_status(corpus_complete=full, precheck_pass=full),
            len(cases),
            "bound package, shard, root, and coverage-manifest receipt required",
            counterexamples=[
                *duplicate_ids,
                *[f"missing_{ordinal}" for ordinal in missing[:32]],
            ],
            detail={"coverage_precheck": "PASS" if full else "FAIL"},
        ),
        _gate(
            "G02",
            unbound_evidence_gate_status(corpus_complete=full, precheck_pass=full),
            len(cases),
            "complete canonical-corpus and malformed-input mutation receipt required",
            counterexamples=[
                f"{error.code}:{error.path}" for error in rejected_records
            ],
            detail={"canonical_corpus_precheck": "PASS" if full else "FAIL"},
        ),
        _gate(
            "G03",
            unbound_evidence_gate_status(corpus_complete=full, precheck_pass=full),
            len(cases),
            "schema-derived invalid-combination enumeration receipt required",
            detail={"typed_reconstruction_precheck": "PASS" if full else "FAIL"},
        ),
        _gate("G04", "SKIP", 0, "hostile mutation receipt required"),
        _gate(
            "G05",
            unbound_evidence_gate_status(corpus_complete=full, precheck_pass=full),
            len(cases),
            "complete oracle-agreement plus law-witness and breaker receipt required",
            detail={"oracle_agreement_precheck": "PASS" if full else "FAIL"},
        ),
    ]

    metrics: dict[str, Any] = {
        "accepted_records": len(cases),
        "rejected_records": len(rejected_records),
        "unique_stable_ids": len(stable_ids),
        "unique_record_hashes": len(record_hashes),
        "distinct_normalized_dispositions": len(
            {case.normalized_sha256 for case in cases}
        ),
    }
    pair_summary: dict[str, Any] = {
        "expected": PAIR_COUNT,
        "checked": 0,
        "effect": 0,
        "invariant": 0,
        "receipt_set_root": "none",
        "spanning_effect_witnesses": 0,
    }

    if full:
        block_outcomes: dict[tuple[int, int], Counter[str]] = defaultdict(Counter)
        block_behaviors: dict[tuple[int, int], Counter[str]] = defaultdict(Counter)
        topology_behaviors: dict[int, set[str]] = defaultdict(set)
        for case in cases:
            domain_code, topology_code = case.codes[:2]
            block_outcomes[(domain_code, topology_code)][_record_outcome(case)] += 1
            block_behaviors[(domain_code, topology_code)][case.normalized_sha256] += 1
            topology_behaviors[topology_code].add(case.normalized_sha256)

        domain_fingerprints = [
            _domain_fingerprint(domain) for domain in template.data["domains"]
        ]
        topology_program_fingerprints = [
            _topology_fingerprint(topology)
            for topology in template.data["topology_programs"]
        ]

        domain_mutation_effects = 0
        domain_mutation_failures: list[str] = []
        for domain_code, domain in enumerate(template.data["domains"]):
            for mutation in domain["causal_mutations"]:
                found = False
                for topology_code, topology in enumerate(
                    template.data["topology_programs"]
                ):
                    state_codes_by_witness = {
                        state["domain_witness"]: state["code"]
                        for state in topology["state_variants"]
                    }
                    source_code = state_codes_by_witness.get(mutation["from_witness"])
                    target_code = state_codes_by_witness.get(mutation["to_witness"])
                    if source_code is None or target_code is None:
                        continue
                    left = by_ordinal[
                        rank_coordinate(
                            (domain_code, topology_code, 0, source_code, 0, 0)
                        )
                    ]
                    right = by_ordinal[
                        rank_coordinate(
                            (domain_code, topology_code, 0, target_code, 0, 0)
                        )
                    ]
                    if left.normalized_sha256 != right.normalized_sha256:
                        found = True
                        domain_mutation_effects += 1
                        break
                if not found:
                    domain_mutation_failures.append(f"{domain['id']}:{mutation['id']}")
        g06_pass = (
            domain_mutation_effects >= 32
            and len(set(domain_fingerprints)) == 16
            and not domain_mutation_failures
        )
        gate_results.append(
            _gate(
                "G06",
                unbound_evidence_gate_status(
                    corpus_complete=full, precheck_pass=g06_pass
                ),
                domain_mutation_effects,
                "durable domain-mutation witness receipt required",
                counterexamples=domain_mutation_failures,
                detail={
                    "domain_precheck": "PASS" if g06_pass else "FAIL",
                    "required_effects": 32,
                    "distinct_domain_fingerprints": len(set(domain_fingerprints)),
                },
            )
        )

        spanning_failures: list[str] = []
        spanning_count = 0
        for domain_code in range(16):
            for topology_code in range(16):
                for axis_index, axis in enumerate(AXES, 2):
                    base = [domain_code, topology_code, 0, 0, 0, 0]
                    source = by_ordinal[rank_coordinate(base)]
                    for target_code in (1, 2, 3):
                        target_codes = list(base)
                        target_codes[axis_index] = target_code
                        target = by_ordinal[rank_coordinate(target_codes)]
                        if source.normalized_sha256 != target.normalized_sha256:
                            spanning_count += 1
                        else:
                            spanning_failures.append(
                                f"d{domain_code}:t{topology_code}:{axis}:0-{target_code}"
                            )
        pair_summary["spanning_effect_witnesses"] = spanning_count

        if enumerate_counterfactuals:
            source_hash = _source_sha256()
            receipt_hashes: list[str] = []
            axis_counts: dict[str, Counter[str]] = {axis: Counter() for axis in AXES}
            for axis_index, axis in enumerate(AXES, 2):
                other_axis_indices = [
                    index for index in range(2, 6) if index != axis_index
                ]
                for domain_code in range(16):
                    for topology_code in range(16):
                        for held_values in itertools.product(range(4), repeat=3):
                            base = [domain_code, topology_code, 0, 0, 0, 0]
                            for index, code in zip(
                                other_axis_indices, held_values, strict=True
                            ):
                                base[index] = code
                            variants: list[VerifiedCase] = []
                            for axis_code in range(4):
                                codes = list(base)
                                codes[axis_index] = axis_code
                                variants.append(by_ordinal[rank_coordinate(codes)])
                            for left_code, right_code in itertools.combinations(
                                range(4), 2
                            ):
                                receipt = _counterfactual_receipt_reconciled(
                                    reconciled,
                                    variants[left_code].ordinal,
                                    variants[right_code].ordinal,
                                    axis=axis,
                                    template=template,
                                    oracle_source_sha256=source_hash,
                                    evaluator_source_sha256=source_hash,
                                )
                                classification = receipt["classification"]
                                axis_counts[axis][classification] += 1
                                receipt_hashes.append(receipt["receipt_sha256"])
                                if receipt_sink is not None:
                                    receipt_sink(receipt)
            pair_summary["checked"] = len(receipt_hashes)
            pair_summary["effect"] = sum(
                counts["EFFECT"] for counts in axis_counts.values()
            )
            pair_summary["invariant"] = sum(
                counts["INVARIANT"] for counts in axis_counts.values()
            )
            pair_summary["per_axis"] = {
                axis: dict(sorted(counts.items()))
                for axis, counts in axis_counts.items()
            }
            pair_summary["receipt_set_root"] = canonical_hash(sorted(receipt_hashes))
            g07_pass = (
                len(receipt_hashes) == PAIR_COUNT
                and spanning_count == SPANNING_WITNESS_COUNT
                and not spanning_failures
            )
            gate_results.append(
                _gate(
                    "G07",
                    unbound_evidence_gate_status(
                        corpus_complete=full, precheck_pass=g07_pass
                    ),
                    len(receipt_hashes),
                    "replayable bound counterfactual receipt corpus required",
                    counterexamples=spanning_failures,
                    detail={
                        "counterfactual_precheck": "PASS" if g07_pass else "FAIL",
                        "expected_pairs": PAIR_COUNT,
                        "expected_spanning_effects": SPANNING_WITNESS_COUNT,
                        "spanning_effect_witnesses": spanning_count,
                    },
                )
            )
        else:
            gate_results.append(
                _gate(
                    "G07",
                    "SKIP",
                    0,
                    "full exhaustive pair enumeration required",
                    detail={"spanning_effect_witnesses_precheck": spanning_count},
                )
            )

        topology_behavior_fingerprints: list[str] = []
        for topology_code in range(16):
            sequence = [
                by_ordinal[
                    rank_coordinate((0, topology_code, *axis_codes))
                ].normalized_sha256
                for axis_codes in itertools.product(range(4), repeat=4)
            ]
            topology_behavior_fingerprints.append(canonical_hash(sequence))
        min_topology_distance = 256
        distance_failures: list[str] = []
        for left_topology, right_topology in itertools.combinations(range(16), 2):
            for domain_code in range(16):
                distance = sum(
                    by_ordinal[
                        rank_coordinate((domain_code, left_topology, *axis_codes))
                    ].normalized_sha256
                    != by_ordinal[
                        rank_coordinate((domain_code, right_topology, *axis_codes))
                    ].normalized_sha256
                    for axis_codes in itertools.product(range(4), repeat=4)
                )
                min_topology_distance = min(min_topology_distance, distance)
                if distance < 16:
                    distance_failures.append(
                        f"d{domain_code}:t{left_topology}-t{right_topology}:{distance}"
                    )
        distinct_global = len({case.normalized_sha256 for case in cases})
        g08_pass = (
            distinct_global >= 64
            and all(len(topology_behaviors[index]) >= 4 for index in range(16))
            and len(set(topology_program_fingerprints)) == 16
            and len(set(topology_behavior_fingerprints)) == 16
            and not distance_failures
        )
        gate_results.append(
            _gate(
                "G08",
                "PASS" if g08_pass else "FAIL",
                distinct_global,
                "64 global behaviors, 4/topology, 16 fingerprints, distance >=16",
                counterexamples=distance_failures,
                detail={
                    "distinct_topology_program_fingerprints": len(
                        set(topology_program_fingerprints)
                    ),
                    "distinct_topology_behavior_fingerprints": len(
                        set(topology_behavior_fingerprints)
                    ),
                    "minimum_pairwise_topology_distance": min_topology_distance,
                    "per_topology_behavior_count": {
                        str(index): len(topology_behaviors[index])
                        for index in range(16)
                    },
                },
            )
        )

        balance_failures: list[str] = []
        max_dominant = 0
        outcome_rows: dict[str, dict[str, int]] = {}
        for (domain_code, topology_code), outcomes in sorted(block_outcomes.items()):
            block_id = f"d{domain_code}:t{topology_code}"
            outcome_rows[block_id] = dict(sorted(outcomes.items()))
            dominant = max(block_behaviors[(domain_code, topology_code)].values())
            max_dominant = max(max_dominant, dominant)
            if (
                outcomes["resolved"] < 16
                or outcomes["unresolved_abstain"] < 16
                or outcomes["unresolved_escalate"] < 16
                or dominant > 192
            ):
                balance_failures.append(block_id)
        gate_results.append(
            _gate(
                "G09",
                "PASS" if not balance_failures else "FAIL",
                256 - len(balance_failures),
                "all 256 blocks meet 16/16/16 floors and dominant <=192",
                counterexamples=balance_failures,
                detail={"maximum_dominant_class": max_dominant},
            )
        )
        metrics["outcomes_by_block"] = outcome_rows

        if enumerate_counterfactuals:
            g10_precheck = pair_summary["checked"] == PAIR_COUNT
            gate_results.append(
                _gate(
                    "G10",
                    unbound_evidence_gate_status(
                        corpus_complete=full, precheck_pass=g10_precheck
                    ),
                    pair_summary["checked"],
                    "retained and replayable content-addressed receipt set required",
                    detail={
                        "receipt_precheck": "PASS" if g10_precheck else "FAIL",
                        "receipt_set_root": pair_summary["receipt_set_root"],
                    },
                )
            )
        else:
            gate_results.append(
                _gate("G10", "SKIP", 0, "counterfactual receipt execution disabled")
            )
    else:
        for gate_id, threshold in (
            ("G06", "complete corpus required"),
            ("G07", "complete corpus required"),
            ("G08", "complete corpus required"),
            ("G09", "complete corpus required"),
            ("G10", "complete corpus required"),
        ):
            gate_results.append(_gate(gate_id, "FAIL", len(cases), threshold))

    gate_results.extend(
        [
            _gate(
                "G11",
                "SKIP",
                0,
                "independent call-graph and hostile-mutation receipts required",
            ),
            _gate("G12", "SKIP", 0, "two clean external rebuilds required"),
            _gate(
                "G13",
                unbound_evidence_gate_status(corpus_complete=full, precheck_pass=full),
                len(cases),
                "manifest, replay, report, tutorial, and authority-mutation receipt required",
                detail={"record_authority_precheck": "PASS" if full else "FAIL"},
            ),
            _gate("G14", "PASS", 0, "explicit honest tool status table present"),
        ]
    )
    tool_rows = [
        {
            "tool": tool,
            "status": "SKIP",
            "reason": "not_executed_against_this_exact_profile",
        }
        for tool in (
            "decision_kernel",
            "z3",
            "cvc5",
            "esso",
            "tau",
            "lean",
            "hol",
            "research_kernel",
            "popperpad",
            "leap",
            "morph",
            "zag",
        )
    ]
    mandatory_statuses = {
        row["gate_id"]: row["status"] for row in gate_results if row["gate_id"] != "G14"
    }
    promotion = (
        "BOUNDED_VERIFIED_SYNTHETIC_DEONTIC_CORPUS_V1"
        if all(status == "PASS" for status in mandatory_statuses.values())
        else "QUARANTINED_CORPUS"
    )
    gate_results.append(
        _gate(
            "G15",
            "PASS" if promotion.startswith("BOUNDED_") else "FAIL",
            sum(status == "PASS" for status in mandatory_statuses.values()),
            "G00-G13 mandatory PASS and honest G14 table",
            counterexamples=[
                gate_id
                for gate_id, status in mandatory_statuses.items()
                if status != "PASS"
            ],
        )
    )
    report = {
        "schema": REPORT_SCHEMA,
        "profile_id": PROFILE_ID,
        "template_bank_sha256": template.sha256,
        "semantics_spec_sha256": EXPECTED_SEMANTICS_SHA256,
        "oracle_source_sha256": _source_sha256(),
        "metrics": metrics,
        "counterfactuals": pair_summary,
        "gate_results": gate_results,
        "tools": tool_rows,
        "promotion": {
            "assigned_label": promotion,
            "veto_reasons": [
                row["gate_id"]
                for row in gate_results
                if row["gate_id"] != "G15" and row["status"] != "PASS"
            ],
        },
        "residual_nonclaims": list(NONCLAIMS),
    }
    report["report_sha256"] = canonical_hash(report)
    return report


def iter_record_bytes(paths: Sequence[str | Path]) -> Iterator[bytes]:
    for raw_path in sorted(Path(path) for path in paths):
        candidates = (
            sorted(
                candidate
                for candidate in raw_path.iterdir()
                if candidate.is_file()
                and (
                    candidate.name.endswith(".jsonl")
                    or candidate.name.endswith(".jsonl.gz")
                )
            )
            if raw_path.is_dir()
            else [raw_path]
        )
        for candidate in candidates:
            opener = gzip.open if candidate.name.endswith(".gz") else open
            with opener(candidate, "rb") as handle:
                for line_number, line in enumerate(handle, 1):
                    if line.endswith(b"\n"):
                        line = line[:-1]
                    if line.endswith(b"\r"):
                        _reject(
                            "noncanonical_line_ending",
                            f"{candidate}:{line_number}",
                        )
                    if not line:
                        _reject("blank_record", f"{candidate}:{line_number}")
                    yield line


def analyze_raw_records(
    records: Iterable[bytes],
    template: BoundTemplate,
    *,
    enumerate_counterfactuals: bool = True,
) -> dict[str, Any]:
    accepted: list[VerifiedCase] = []
    rejected: list[OracleReject] = []
    for raw in records:
        try:
            accepted.append(verify_record(raw, template))
        except OracleReject as exc:
            rejected.append(exc)
    return analyze_verified_cases(
        accepted,
        template,
        rejected_records=rejected,
        enumerate_counterfactuals=enumerate_counterfactuals,
    )


def _validate_report_target(path: str | Path) -> Path:
    output_path = Path(path)
    if output_path.exists() or output_path.is_symlink():
        _reject("report_exists", "analyze.report", str(output_path))
    parent = output_path.parent
    if not parent.is_dir():
        _reject("report_parent_missing", "analyze.report", str(parent))
    return output_path


def write_canonical_report_exclusive(
    path: str | Path, report: Mapping[str, Any]
) -> None:
    """Atomically publish canonical report bytes without replacing any path."""

    output_path = _validate_report_target(path)
    parent = output_path.parent

    descriptor, temporary_name = tempfile.mkstemp(
        dir=parent,
        prefix=f".{output_path.name}.",
        suffix=".tmp",
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(canonical_bytes(report))
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary_path, output_path)
        except FileExistsError:
            _reject("report_exists", "analyze.report", str(output_path))
        temporary_path.unlink()
        directory_descriptor = os.open(parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--template", required=True, help="frozen v1 template-bank JSON"
    )
    parser.add_argument(
        "--semantics", required=True, help="frozen v1 semantics Markdown"
    )
    parser.add_argument(
        "--release-gates", help="optional frozen release-gates Markdown binding"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    verify_parser = subparsers.add_parser("verify-record")
    verify_parser.add_argument("record")
    analyze_parser = subparsers.add_parser("analyze")
    analyze_parser.add_argument("corpus", nargs="+")
    analyze_parser.add_argument("--skip-counterfactuals", action="store_true")
    analyze_parser.add_argument(
        "--report",
        help="atomically write canonical report JSON; fail if PATH already exists",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    template = load_template_bank(args.template)
    load_bound_semantics(args.semantics)
    if args.release_gates:
        load_bound_release_gates(args.release_gates)
    if args.command == "analyze" and args.report:
        _validate_report_target(args.report)
    if args.command == "verify-record":
        verified = verify_record(Path(args.record).read_bytes(), template)
        output = {
            "status": "PASS",
            "ordinal": verified.ordinal,
            "stable_id": verified.stable_id,
            "result_sha256": verified.result_sha256,
            "normalized_sha256": verified.normalized_sha256,
        }
    else:
        output = analyze_raw_records(
            iter_record_bytes(args.corpus),
            template,
            enumerate_counterfactuals=not args.skip_counterfactuals,
        )
    if args.command == "analyze" and args.report:
        write_canonical_report_exclusive(args.report, output)
        stdout_value = {
            "status": "PASS",
            "accepted_records": output["metrics"]["accepted_records"],
            "assigned_label": output["promotion"]["assigned_label"],
            "counterfactual_receipt_set_root": output["counterfactuals"][
                "receipt_set_root"
            ],
            "report_path": str(args.report),
            "report_sha256": output["report_sha256"],
        }
    else:
        stdout_value = output
    sys.stdout.write(json.dumps(stdout_value, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except OracleReject as exc:
        sys.stderr.write(
            json.dumps(
                {
                    "status": "FAIL",
                    "code": exc.code,
                    "path": exc.path,
                    "detail": exc.detail,
                },
                sort_keys=True,
            )
            + "\n"
        )
        raise SystemExit(2) from None
