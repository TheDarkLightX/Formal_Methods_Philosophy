"""A bounded executable deontic kernel for the GlassMind tutorial.

This module deliberately implements a small, selectable input-output
detachment profile, not Standard Deontic Logic and not a universal ethics
engine.  A packet declares a finite action alphabet, explicit true and false
context facts, and rules whose modalities are ``O`` (obligation), ``F``
(prohibition), or ``P`` (explicit permission).  Rule conditions use only the
finite predicate tree ``fact``, ``all``, ``any``, and ``not``.  Predicate
evaluation is three-valued: an unprovided fact is unknown, rather than false.
Empty ``all`` is true and empty ``any`` is false.

The hard bounds are part of the executable schema:

* packet JSON and canonical packet bytes: 32,768 bytes;
* pack JSON: 65,536 bytes and at most 32 decisions;
* packet nesting: 12 levels and 512 JSON nodes;
* 64 facts, 32 actions, and 64 rules per decision;
* identifiers are ASCII and at most 64 characters;
* generic arrays and objects have at most 128 entries, and generic text has
  at most 512 characters before field-specific limits are applied;
* predicates have depth at most 6, 32 nodes, and 8 children per connective;
* 16 assumptions and profile nonclaims, each at most 256 characters;
* extension objects have at most 6 known fields and 1,024 canonical bytes;
* extension lists have at most 4 entries and extension nesting is at most
  3 levels.

The ``extensions`` fields are bounded metadata only.  They are not interpreted
as temporal logic, exception handling, priority, theorem references, or
knowledge-base queries.  In particular, this example does not implement
contrary-to-duty semantics, defeasible priority, temporal reasoning, or
machine-checked proofs.  A receipt is a deterministic derivation receipt and
human-readable explanation, not a machine-checkable proof object.  The finite
trace checker emits bounded counterexamples; it does not claim full LTL model
checking.

``validate_packet`` and ``validate_decision_pack`` are strict APIs and raise
``SchemaError``.  ``evaluate`` is the safe boundary: validation failures are
represented as an escalation result with a receipt, so callers do not need to
turn an exception into a potentially permissive decision themselves.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

KERNEL_VERSION = "glassmind-deontic-kernel-v1"
PACK_SCHEMA = "glassmind-deontic-decision-pack-v1"
PACKET_SCHEMA = "glassmind-deontic-decision-v1"
RECEIPT_SCHEMA = "glassmind-deontic-receipt-v1"
PREDICATE_LANGUAGE = "glassmind-explicit-predicate-v1"
POLICY_PROFILE_SCHEMA = "glassmind-deontic-policy-profile-v1"
LOGIC_PROFILE_ID = "bounded-finite-detachment-v1"
TRACE_SCHEMA = "glassmind-deontic-finite-trace-v1"
ESSO_IR_VERSION = "esso-ir/v1"
ESSO_VERIFICATION_STATUS_SCHEMA = "glassmind-esso-verification-status-v1"

OBLIGATION = "O"
PROHIBITION = "F"
PERMISSION = "P"
MODALITIES = (OBLIGATION, PROHIBITION, PERMISSION)
ABSTAIN_ACTION = "abstain"
ESCALATE_ACTION = "escalate"
RESERVED_ACTIONS = (ABSTAIN_ACTION, ESCALATE_ACTION)

MAX_PACKET_BYTES = 32_768
MAX_PACK_BYTES = 65_536
MAX_PACKET_NESTING = 12
MAX_PACKET_NODES = 512
MAX_GENERIC_LIST_ITEMS = 128
MAX_FACTS = 64
MAX_ACTIONS = 32
MAX_RULES = 64
MAX_PACK_DECISIONS = 32
MAX_IDENTIFIER_LENGTH = 64
MAX_FACT_LENGTH = 64
MAX_ACTION_LENGTH = 64
MAX_RULE_LENGTH = 64
MAX_TEXT_LENGTH = 256
MAX_PACK_TEXT_LENGTH = 512
MAX_ASSUMPTIONS = 16
MAX_PREDICATE_DEPTH = 6
MAX_PREDICATE_NODES = 32
MAX_PREDICATE_CHILDREN = 8
MAX_EXTENSION_FIELDS = 6
MAX_EXTENSION_ITEMS = 4
MAX_EXTENSION_DEPTH = 3
MAX_EXTENSION_BYTES = 1_024
MAX_RECEIPT_BYTES = 65_536
MAX_TRACE_STEPS = 1_024
MAX_TRACE_DEADLINE = 1_024


LIMITS: dict[str, int] = {
    "max_packet_bytes": MAX_PACKET_BYTES,
    "max_pack_bytes": MAX_PACK_BYTES,
    "max_packet_nesting": MAX_PACKET_NESTING,
    "max_packet_nodes": MAX_PACKET_NODES,
    "max_generic_entries": MAX_GENERIC_LIST_ITEMS,
    "max_generic_text": MAX_PACK_TEXT_LENGTH,
    "max_facts": MAX_FACTS,
    "max_actions": MAX_ACTIONS,
    "max_rules": MAX_RULES,
    "max_pack_decisions": MAX_PACK_DECISIONS,
    "max_identifier_length": MAX_IDENTIFIER_LENGTH,
    "max_predicate_depth": MAX_PREDICATE_DEPTH,
    "max_predicate_nodes": MAX_PREDICATE_NODES,
    "max_predicate_children": MAX_PREDICATE_CHILDREN,
    "max_extension_fields": MAX_EXTENSION_FIELDS,
    "max_extension_items": MAX_EXTENSION_ITEMS,
    "max_extension_depth": MAX_EXTENSION_DEPTH,
    "max_extension_bytes": MAX_EXTENSION_BYTES,
    "max_trace_steps": MAX_TRACE_STEPS,
    "max_trace_deadline": MAX_TRACE_DEADLINE,
}

_PACKET_REQUIRED_FIELDS = {
    "schema",
    "decision_id",
    "logic_profile",
    "policy_profile",
    "actions",
    "context",
    "rules",
}
_PACKET_OPTIONAL_FIELDS = {"allow_abstain", "assumptions", "extensions"}
_CONTEXT_FIELDS = {"facts", "false_facts"}
_RULE_REQUIRED_FIELDS = {"id", "modality", "action", "when"}
_RULE_OPTIONAL_FIELDS = {"extensions", "contrary_to_duty"}
_PACK_FIELDS = {
    "schema",
    "policy_profile",
    "decisions",
    "assumptions",
    "future_extension_nonclaims",
    "extensions",
}
_SCENARIO_FIELDS = {"id", "description", "packet"}
_EXTENSION_FIELDS = {
    "source_refs",
    "temporal",
    "exception_hook",
    "priority_hook",
    "theorem_refs",
    "knowledge_base",
}
_TEMPORAL_FIELDS = {"deadline", "valid_from", "valid_until"}
_KNOWLEDGE_BASE_FIELDS = {"name", "snapshot", "record_refs"}

LOGIC_SEMANTICS_PROFILE: dict[str, object] = {
    "schema": "glassmind-logic-semantics-v1",
    "profile_id": LOGIC_PROFILE_ID,
    "family": "bounded-input-output-detachment",
    "inputs": ["finite-explicit-true-facts", "finite-explicit-false-facts", "conditional-norms"],
    "outputs": ["O", "F", "P"],
    "predicate_values": ["true", "false", "unknown"],
    "unknown_predicate_policy": "fail-closed",
    "coherence": "O-implies-P",
    "conflict_policy": "quarantine",
    "multiple_obligation_policy": "quarantine",
    "priority_and_exception_hooks": "metadata-only",
    "contrary_to_duty": "not-implemented-quarantine",
    "explosion": False,
    "temporal_reasoning": "not-implemented",
    "sdl_claim": "not-standard-deontic-logic",
}

_POLICY_PROFILE_REQUIRED_FIELDS = {
    "schema",
    "profile_id",
    "evidence_completion",
    "unknown_predicates",
    "conflict_handling",
    "multiple_obligations",
    "contrary_to_duty",
    "priority",
    "exceptions",
    "abstention",
    "nonclaims",
}
_POLICY_PROFILE_OPTIONAL_FIELDS = {"description"}


class DeonticKernelError(ValueError):
    """Base class for deterministic kernel errors."""


class SchemaError(DeonticKernelError):
    """A strict, fail-closed schema or resource-limit rejection."""

    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        self.detail = message
        super().__init__(f"{code} at {path}: {message}")


class _DuplicateKeyError(ValueError):
    def __init__(self, key: object) -> None:
        self.key = key
        super().__init__("duplicate object key")


def _schema_error(code: str, path: str, message: str) -> SchemaError:
    return SchemaError(code, path, message)


def _require_exact_dict(value: object, path: str) -> dict[str, object]:
    if type(value) is not dict:
        raise _schema_error("wrong_type", path, "expected a JSON object")
    result = value
    for key in result:
        if type(key) is not str:
            raise _schema_error("wrong_type", f"{path}.<key>", "object keys must be strings")
    return result


def _require_exact_list(value: object, path: str) -> list[object]:
    if type(value) is not list:
        raise _schema_error("wrong_type", path, "expected a JSON array")
    return value


def _check_fields(
    value: dict[str, object],
    required: set[str],
    optional: set[str],
    path: str,
) -> None:
    keys = set(value)
    missing = sorted(required - keys)
    if missing:
        raise _schema_error("missing_field", path, f"missing field {missing[0]!r}")
    unknown = sorted(keys - required - optional)
    if unknown:
        raise _schema_error("unknown_field", f"{path}.{unknown[0]}", "field is not in the bounded schema")


def _check_text(value: object, path: str, maximum: int) -> str:
    if type(value) is not str:
        raise _schema_error("wrong_type", path, "expected a string")
    if not 1 <= len(value) <= maximum:
        raise _schema_error("size_limit", path, f"string length must be between 1 and {maximum}")
    if any(ord(character) < 0x20 or ord(character) > 0x7E for character in value):
        raise _schema_error("invalid_text", path, "text must use printable ASCII characters")
    return value


def _check_identifier(value: object, path: str, maximum: int) -> str:
    text = _check_text(value, path, maximum)
    first = ord(text[0])
    if not (65 <= first <= 90 or 97 <= first <= 122 or first == 95):
        raise _schema_error("invalid_identifier", path, "identifier must start with ASCII letter or underscore")
    for character in text:
        code = ord(character)
        if not (
            65 <= code <= 90
            or 97 <= code <= 122
            or 48 <= code <= 57
            or character in "_-.:"
        ):
            raise _schema_error("invalid_identifier", path, "identifier contains an unsupported character")
    if text.startswith("__"):
        raise _schema_error("invalid_identifier", path, "dunder identifiers are reserved")
    return text


def _check_json_shape(
    value: object,
    path: str,
    *,
    depth: int = 0,
    counter: list[int] | None = None,
    ancestors: set[int] | None = None,
    max_depth: int = MAX_PACKET_NESTING,
    max_nodes: int = MAX_PACKET_NODES,
    max_collection_items: int = MAX_GENERIC_LIST_ITEMS,
) -> None:
    """Reject hostile Python object graphs before schema interpretation."""

    if counter is None:
        counter = [0]
    if ancestors is None:
        ancestors = set()
    counter[0] += 1
    if counter[0] > max_nodes:
        raise _schema_error("node_limit", path, "JSON node count exceeds the hard bound")
    if depth > max_depth:
        raise _schema_error("nesting_limit", path, "JSON nesting exceeds the hard bound")
    if type(value) is dict:
        identity = id(value)
        if identity in ancestors:
            raise _schema_error("cyclic_input", path, "JSON-compatible input must not contain a cycle")
        if len(value) > max_collection_items:
            raise _schema_error("field_limit", path, "object field count exceeds the hard bound")
        ancestors.add(identity)
        try:
            for key, child in value.items():
                if type(key) is not str:
                    raise _schema_error("wrong_type", f"{path}.<key>", "object keys must be strings")
                _check_json_shape(
                    child,
                    f"{path}.{key}",
                    depth=depth + 1,
                    counter=counter,
                    ancestors=ancestors,
                    max_depth=max_depth,
                    max_nodes=max_nodes,
                    max_collection_items=max_collection_items,
                )
        finally:
            ancestors.remove(identity)
        return
    if type(value) is list:
        identity = id(value)
        if identity in ancestors:
            raise _schema_error("cyclic_input", path, "JSON-compatible input must not contain a cycle")
        if len(value) > max_collection_items:
            raise _schema_error("field_limit", path, "array item count exceeds the hard bound")
        ancestors.add(identity)
        try:
            for index, child in enumerate(value):
                _check_json_shape(
                    child,
                    f"{path}[{index}]",
                    depth=depth + 1,
                    counter=counter,
                    ancestors=ancestors,
                    max_depth=max_depth,
                    max_nodes=max_nodes,
                    max_collection_items=max_collection_items,
                )
        finally:
            ancestors.remove(identity)
        return
    if type(value) is str:
        if len(value) > MAX_PACK_TEXT_LENGTH:
            raise _schema_error("size_limit", path, "string exceeds the hard bound")
        return
    if type(value) is bool or type(value) is int:
        return
    raise _schema_error("wrong_type", path, "only bounded JSON objects, arrays, strings, booleans, and integers are allowed")


def _canonical_json_bytes(value: object) -> bytes:
    try:
        encoded = json.dumps(
            value,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    except (TypeError, ValueError, OverflowError, UnicodeError) as error:
        raise DeonticKernelError(f"value is not canonical JSON: {error}") from error
    return encoded


def canonical_json_bytes(value: object) -> bytes:
    """Return stable JSON bytes using sorted keys and no insignificant space."""

    return _canonical_json_bytes(value)


def canonical_sha256(value: object) -> str:
    """Hash stable JSON bytes; packet validation remains the caller's gate."""

    return hashlib.sha256(_canonical_json_bytes(value)).hexdigest()


LOGIC_SEMANTICS_HASH = canonical_sha256(LOGIC_SEMANTICS_PROFILE)
LOGIC_SEMANTICS_SHA256 = LOGIC_SEMANTICS_HASH


def _parse_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKeyError(key)
        result[key] = value
    return result


def _reject_json_constant(value: str) -> object:
    raise ValueError(f"non-finite JSON constant {value!r} is not accepted")


def _parse_json_bytes(raw: bytes, *, maximum: int) -> object:
    if len(raw) > maximum:
        raise _schema_error("input_size_limit", "$", f"input exceeds {maximum} bytes")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise _schema_error("invalid_encoding", "$", "input must be UTF-8 JSON") from error
    try:
        return json.loads(
            text,
            object_pairs_hook=_parse_pairs,
            parse_constant=_reject_json_constant,
        )
    except _DuplicateKeyError as error:
        raise _schema_error("duplicate_field", "$", f"duplicate object key {error.key!r}") from error
    except RecursionError as error:
        raise _schema_error("nesting_limit", "$", "JSON nesting exceeds the parser hard bound") from error
    except (TypeError, ValueError, json.JSONDecodeError) as error:
        raise _schema_error("invalid_json", "$", "input is not valid strict JSON") from error


def parse_json(raw: bytes | str) -> dict[str, object]:
    """Parse a packet-sized JSON document with duplicate-key rejection."""

    if type(raw) is bytes:
        data = raw
    elif type(raw) is str:
        try:
            data = raw.encode("utf-8")
        except UnicodeEncodeError as error:
            raise _schema_error("invalid_encoding", "$", "input must be UTF-8 JSON") from error
    else:
        raise _schema_error("wrong_type", "$", "raw JSON must be bytes or string")
    parsed = _parse_json_bytes(data, maximum=MAX_PACKET_BYTES)
    return _require_exact_dict(parsed, "$")


def _freeze_json(value: object) -> object:
    if type(value) is dict:
        return ("__dict__", tuple((key, _freeze_json(value[key])) for key in sorted(value)))
    if type(value) is list:
        return ("__list__", tuple(_freeze_json(item) for item in value))
    if type(value) is tuple:
        return ("__list__", tuple(_freeze_json(item) for item in value))
    return value


def _thaw_json(value: object) -> object:
    if type(value) is tuple:
        if len(value) == 2 and value[0] == "__dict__":
            entries = value[1]
            return {key: _thaw_json(child) for key, child in entries}  # type: ignore[misc]
        if len(value) == 2 and value[0] == "__list__":
            return [_thaw_json(child) for child in value[1]]  # type: ignore[index]
        raise DeonticKernelError("internal frozen JSON tag is invalid")
    return value


@dataclass(frozen=True)
class PolicyProfile:
    """A bounded normative profile compiled as part of a packet."""

    profile_id: str
    evidence_completion: str
    unknown_predicates: str
    conflict_handling: str
    multiple_obligations: str
    contrary_to_duty: str
    priority: str
    exceptions: str
    abstention: str
    nonclaims: tuple[str, ...]
    description: str = ""

    @property
    def schema(self) -> str:
        return POLICY_PROFILE_SCHEMA

    def to_data(self) -> dict[str, object]:
        return {
            "schema": POLICY_PROFILE_SCHEMA,
            "profile_id": self.profile_id,
            "evidence_completion": self.evidence_completion,
            "unknown_predicates": self.unknown_predicates,
            "conflict_handling": self.conflict_handling,
            "multiple_obligations": self.multiple_obligations,
            "contrary_to_duty": self.contrary_to_duty,
            "priority": self.priority,
            "exceptions": self.exceptions,
            "abstention": self.abstention,
            "nonclaims": list(self.nonclaims),
            "description": self.description,
        }

    @property
    def canonical_bytes(self) -> bytes:
        return _canonical_json_bytes(self.to_data())

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_bytes).hexdigest()


def compile_policy_profile(profile: object) -> PolicyProfile:
    """Strictly compile one finite policy profile into an immutable value.

    The kernel currently implements one family of policy choices.  A caller
    may give that profile a different bounded identifier or description, which
    changes its binding hash, but unsupported semantic choices are rejected
    instead of being silently ignored.
    """

    raw = profile.to_data() if isinstance(profile, PolicyProfile) else _require_exact_dict(profile, "$.policy_profile")
    _check_json_shape(raw, "$.policy_profile", max_depth=MAX_PACKET_NESTING)
    _check_fields(raw, _POLICY_PROFILE_REQUIRED_FIELDS, _POLICY_PROFILE_OPTIONAL_FIELDS, "$.policy_profile")
    if raw["schema"] != POLICY_PROFILE_SCHEMA:
        raise _schema_error("schema_version", "$.policy_profile.schema", f"expected {POLICY_PROFILE_SCHEMA!r}")
    profile_id = _check_identifier(raw["profile_id"], "$.policy_profile.profile_id", MAX_IDENTIFIER_LENGTH)

    expected_modes = {
        "evidence_completion": "explicit-facts-only",
        "unknown_predicates": "fail-closed",
        "conflict_handling": "quarantine",
        "multiple_obligations": "quarantine",
        "contrary_to_duty": "not-implemented-quarantine",
        "priority": "metadata-only",
        "exceptions": "metadata-only",
        "abstention": "explicit-only",
    }
    modes: dict[str, str] = {}
    for field, expected in expected_modes.items():
        actual = _check_text(raw[field], f"$.policy_profile.{field}", MAX_TEXT_LENGTH)
        if actual != expected:
            raise _schema_error(
                "unsupported_policy_semantics",
                f"$.policy_profile.{field}",
                f"the bounded kernel requires {expected!r}",
            )
        modes[field] = actual

    nonclaims_value = _require_exact_list(raw["nonclaims"], "$.policy_profile.nonclaims")
    if not 1 <= len(nonclaims_value) <= MAX_ASSUMPTIONS:
        raise _schema_error("nonclaim_limit", "$.policy_profile.nonclaims", "profile nonclaims must be bounded and non-empty")
    nonclaims = tuple(
        _check_text(item, f"$.policy_profile.nonclaims[{index}]", MAX_TEXT_LENGTH)
        for index, item in enumerate(nonclaims_value)
    )
    if len(set(nonclaims)) != len(nonclaims):
        raise _schema_error("duplicate_nonclaim", "$.policy_profile.nonclaims", "profile nonclaims must be unique")
    description_value = raw.get("description", "")
    description = (
        ""
        if description_value == ""
        else _check_text(description_value, "$.policy_profile.description", MAX_TEXT_LENGTH)
    )
    return PolicyProfile(
        profile_id=profile_id,
        evidence_completion=modes["evidence_completion"],
        unknown_predicates=modes["unknown_predicates"],
        conflict_handling=modes["conflict_handling"],
        multiple_obligations=modes["multiple_obligations"],
        contrary_to_duty=modes["contrary_to_duty"],
        priority=modes["priority"],
        exceptions=modes["exceptions"],
        abstention=modes["abstention"],
        nonclaims=nonclaims,
        description=description,
    )


NEUTRAL_EVIDENCE_COMPLETION_POLICY_PROFILE = compile_policy_profile(
    {
        "schema": POLICY_PROFILE_SCHEMA,
        "profile_id": "neutral-evidence-completion-v1",
        "evidence_completion": "explicit-facts-only",
        "unknown_predicates": "fail-closed",
        "conflict_handling": "quarantine",
        "multiple_obligations": "quarantine",
        "contrary_to_duty": "not-implemented-quarantine",
        "priority": "metadata-only",
        "exceptions": "metadata-only",
        "abstention": "explicit-only",
        "nonclaims": [
            "This finite profile is not universal ethics or a best normative theory.",
            "The profile does not verify the truth of supplied facts or source evidence.",
            "Priority, exceptions, contrary-to-duty patterns, and temporal hooks are not implemented semantics.",
        ],
        "description": "Neutral evidence-completion profile for a bounded tutorial fixture.",
    }
)
NEUTRAL_POLICY_PROFILE = NEUTRAL_EVIDENCE_COMPLETION_POLICY_PROFILE
POLICY_PROFILE_SHA256 = NEUTRAL_EVIDENCE_COMPLETION_POLICY_PROFILE.sha256


def _validate_extension_list(value: object, path: str, maximum_length: int = 128) -> tuple[str, ...]:
    items = _require_exact_list(value, path)
    if len(items) > MAX_EXTENSION_ITEMS:
        raise _schema_error("extension_limit", path, f"extension list exceeds {MAX_EXTENSION_ITEMS} items")
    result = tuple(_check_text(item, f"{path}[{index}]", maximum_length) for index, item in enumerate(items))
    if len(set(result)) != len(result):
        raise _schema_error("duplicate_extension", path, "extension entries must be unique")
    return result


def _validate_extensions(value: object, path: str) -> object:
    extensions = _require_exact_dict(value, path)
    _check_json_shape(extensions, path, max_depth=MAX_EXTENSION_DEPTH)
    if len(extensions) > MAX_EXTENSION_FIELDS:
        raise _schema_error("extension_limit", path, f"extensions allow at most {MAX_EXTENSION_FIELDS} fields")
    unknown = sorted(set(extensions) - _EXTENSION_FIELDS)
    if unknown:
        raise _schema_error("unknown_extension", f"{path}.{unknown[0]}", "extension name is not registered")
    for key, child in extensions.items():
        child_path = f"{path}.{key}"
        if key in {"source_refs", "theorem_refs"}:
            _validate_extension_list(child, child_path, 128)
        elif key in {"exception_hook", "priority_hook"}:
            _check_text(child, child_path, 128)
        elif key == "temporal":
            temporal = _require_exact_dict(child, child_path)
            if not temporal:
                raise _schema_error("empty_extension", child_path, "temporal metadata must have a field")
            unknown_temporal = sorted(set(temporal) - _TEMPORAL_FIELDS)
            if unknown_temporal:
                raise _schema_error("unknown_extension", f"{child_path}.{unknown_temporal[0]}", "temporal field is not registered")
            for temporal_key, temporal_value in temporal.items():
                _check_text(temporal_value, f"{child_path}.{temporal_key}", 128)
        elif key == "knowledge_base":
            knowledge_base = _require_exact_dict(child, child_path)
            if not knowledge_base:
                raise _schema_error("empty_extension", child_path, "knowledge-base metadata must have a field")
            unknown_knowledge = sorted(set(knowledge_base) - _KNOWLEDGE_BASE_FIELDS)
            if unknown_knowledge:
                raise _schema_error("unknown_extension", f"{child_path}.{unknown_knowledge[0]}", "knowledge-base field is not registered")
            for knowledge_key, knowledge_value in knowledge_base.items():
                if knowledge_key == "record_refs":
                    _validate_extension_list(knowledge_value, f"{child_path}.{knowledge_key}", 128)
                else:
                    _check_text(knowledge_value, f"{child_path}.{knowledge_key}", 128)
    try:
        encoded = _canonical_json_bytes(extensions)
    except DeonticKernelError as error:
        raise _schema_error("invalid_extension", path, str(error)) from error
    if len(encoded) > MAX_EXTENSION_BYTES:
        raise _schema_error("extension_size_limit", path, f"extension payload exceeds {MAX_EXTENSION_BYTES} bytes")
    return _freeze_json(extensions)


@dataclass(frozen=True)
class Predicate:
    """An immutable node in the finite explicit predicate language."""

    operation: str
    fact: str | None = None
    children: tuple[Predicate, ...] = ()

    def applies(
        self,
        facts: frozenset[str],
        false_facts: frozenset[str] = frozenset(),
    ) -> bool | None:
        if self.operation == "fact":
            if self.fact in facts:
                return True
            if self.fact in false_facts:
                return False
            return None
        if self.operation == "all":
            values = tuple(child.applies(facts, false_facts) for child in self.children)
            if any(value is False for value in values):
                return False
            if any(value is None for value in values):
                return None
            return True
        if self.operation == "any":
            values = tuple(child.applies(facts, false_facts) for child in self.children)
            if any(value is True for value in values):
                return True
            if any(value is None for value in values):
                return None
            return False
        if self.operation == "not":
            value = self.children[0].applies(facts, false_facts)
            return None if value is None else not value
        raise DeonticKernelError("internal predicate operation is outside the bounded language")

    def to_data(self) -> dict[str, object]:
        if self.operation == "fact":
            return {"fact": self.fact}
        if self.operation == "not":
            return {"not": self.children[0].to_data()}
        return {self.operation: [child.to_data() for child in self.children]}


def _predicate_sort_key(predicate: Predicate) -> bytes:
    return _canonical_json_bytes(predicate.to_data())


def _parse_predicate(
    value: object,
    path: str,
    *,
    depth: int,
    counter: list[int],
) -> Predicate:
    if depth > MAX_PREDICATE_DEPTH:
        raise _schema_error("predicate_depth_limit", path, "predicate depth exceeds the hard bound")
    counter[0] += 1
    if counter[0] > MAX_PREDICATE_NODES:
        raise _schema_error("predicate_node_limit", path, "predicate node count exceeds the hard bound")
    predicate = _require_exact_dict(value, path)
    if len(predicate) != 1:
        raise _schema_error("predicate_shape", path, "predicate must contain exactly one operation")
    operation = next(iter(predicate))
    if operation == "fact":
        fact = _check_identifier(predicate[operation], f"{path}.fact", MAX_FACT_LENGTH)
        return Predicate(operation="fact", fact=fact)
    if operation == "not":
        child = _parse_predicate(predicate[operation], f"{path}.not", depth=depth + 1, counter=counter)
        return Predicate(operation="not", children=(child,))
    if operation not in {"all", "any"}:
        raise _schema_error("predicate_operation", f"{path}.{operation}", "operation is outside the finite predicate language")
    children = _require_exact_list(predicate[operation], f"{path}.{operation}")
    if len(children) > MAX_PREDICATE_CHILDREN:
        raise _schema_error("predicate_child_limit", f"{path}.{operation}", "predicate connective has too many children")
    parsed_children = tuple(
        _parse_predicate(child, f"{path}.{operation}[{index}]", depth=depth + 1, counter=counter)
        for index, child in enumerate(children)
    )
    ordered_children = tuple(sorted(parsed_children, key=_predicate_sort_key))
    if len({_predicate_sort_key(child) for child in ordered_children}) != len(ordered_children):
        raise _schema_error("duplicate_predicate", f"{path}.{operation}", "duplicate predicate children are rejected")
    return Predicate(operation=operation, children=ordered_children)


@dataclass(frozen=True)
class Rule:
    identifier: str
    modality: str
    action: str
    predicate: Predicate
    extensions: object
    contrary_to_duty: bool = False

    def to_data(self) -> dict[str, object]:
        return {
            "id": self.identifier,
            "modality": self.modality,
            "action": self.action,
            "when": self.predicate.to_data(),
            "extensions": _thaw_json(self.extensions),
            "contrary_to_duty": self.contrary_to_duty,
        }


@dataclass(frozen=True)
class ValidatedPacket:
    """A transitively immutable, normalized decision packet."""

    decision_id: str
    logic_profile: str
    policy_profile: PolicyProfile
    actions: tuple[str, ...]
    facts: tuple[str, ...]
    false_facts: tuple[str, ...]
    rules: tuple[Rule, ...]
    allow_abstain: bool
    assumptions: tuple[str, ...]
    extensions: object

    @property
    def schema(self) -> str:
        return PACKET_SCHEMA

    @property
    def policy_profile_sha256(self) -> str:
        return self.policy_profile.sha256

    @property
    def logic_semantics_sha256(self) -> str:
        return LOGIC_SEMANTICS_HASH

    def to_data(self) -> dict[str, object]:
        return {
            "schema": PACKET_SCHEMA,
            "decision_id": self.decision_id,
            "logic_profile": self.logic_profile,
            "policy_profile": self.policy_profile.to_data(),
            "actions": list(self.actions),
            "context": {"facts": list(self.facts), "false_facts": list(self.false_facts)},
            "rules": [rule.to_data() for rule in self.rules],
            "allow_abstain": self.allow_abstain,
            "assumptions": list(self.assumptions),
            "extensions": _thaw_json(self.extensions),
        }

    @property
    def canonical_bytes(self) -> bytes:
        encoded = _canonical_json_bytes(self.to_data())
        if len(encoded) > MAX_PACKET_BYTES:
            raise _schema_error("packet_size_limit", "$", f"canonical packet exceeds {MAX_PACKET_BYTES} bytes")
        return encoded


def validate_packet(
    packet: object,
    *,
    policy_profile: object | None = None,
) -> ValidatedPacket:
    """Strictly validate and normalize one decision packet."""

    raw_input = _require_exact_dict(packet, "$")
    raw = dict(raw_input)
    if "policy_profile" not in raw and policy_profile is not None:
        raw["policy_profile"] = compile_policy_profile(policy_profile).to_data()
    _check_json_shape(raw, "$")
    _check_fields(raw, _PACKET_REQUIRED_FIELDS, _PACKET_OPTIONAL_FIELDS, "$")
    if raw["schema"] != PACKET_SCHEMA:
        raise _schema_error("schema_version", "$.schema", f"expected {PACKET_SCHEMA!r}")
    decision_id = _check_identifier(raw["decision_id"], "$.decision_id", MAX_IDENTIFIER_LENGTH)
    logic_profile = raw["logic_profile"]
    if type(logic_profile) is not str or logic_profile != LOGIC_PROFILE_ID:
        raise _schema_error("unsupported_logic_profile", "$.logic_profile", f"expected {LOGIC_PROFILE_ID!r}")
    compiled_policy_profile = compile_policy_profile(raw["policy_profile"])
    if policy_profile is not None:
        supplied_profile = compile_policy_profile(policy_profile)
        if supplied_profile.sha256 != compiled_policy_profile.sha256:
            raise _schema_error(
                "policy_profile_mismatch",
                "$.policy_profile",
                "packet and compilation-input policy profiles differ",
            )

    raw_actions = _require_exact_list(raw["actions"], "$.actions")
    if not 2 <= len(raw_actions) <= MAX_ACTIONS:
        raise _schema_error("action_limit", "$.actions", f"actions must contain between 2 and {MAX_ACTIONS} entries")
    actions = tuple(sorted(_check_identifier(item, f"$.actions[{index}]", MAX_ACTION_LENGTH) for index, item in enumerate(raw_actions)))
    if len(set(actions)) != len(actions):
        raise _schema_error("duplicate_action", "$.actions", "actions must be unique")
    if not set(RESERVED_ACTIONS).issubset(actions):
        raise _schema_error("reserved_action_missing", "$.actions", "actions must include abstain and escalate")

    context = _require_exact_dict(raw["context"], "$.context")
    _check_fields(context, {"facts"}, {"false_facts"}, "$.context")
    raw_facts = _require_exact_list(context["facts"], "$.context.facts")
    if len(raw_facts) > MAX_FACTS:
        raise _schema_error("fact_limit", "$.context.facts", f"facts exceed {MAX_FACTS} entries")
    facts = tuple(sorted(_check_identifier(item, f"$.context.facts[{index}]", MAX_FACT_LENGTH) for index, item in enumerate(raw_facts)))
    if len(set(facts)) != len(facts):
        raise _schema_error("duplicate_fact", "$.context.facts", "facts must be unique")
    raw_false_facts = _require_exact_list(context.get("false_facts", []), "$.context.false_facts")
    if len(raw_false_facts) > MAX_FACTS:
        raise _schema_error("fact_limit", "$.context.false_facts", f"false_facts exceed {MAX_FACTS} entries")
    false_facts = tuple(
        sorted(_check_identifier(item, f"$.context.false_facts[{index}]", MAX_FACT_LENGTH) for index, item in enumerate(raw_false_facts))
    )
    if len(set(false_facts)) != len(false_facts):
        raise _schema_error("duplicate_fact", "$.context.false_facts", "false_facts must be unique")
    if set(facts).intersection(false_facts):
        raise _schema_error("contradictory_context", "$.context", "a fact cannot be both true and false")

    allow_abstain = raw.get("allow_abstain", False)
    if type(allow_abstain) is not bool:
        raise _schema_error("wrong_type", "$.allow_abstain", "allow_abstain must be a boolean")
    assumptions_value = raw.get("assumptions", [])
    assumptions_list = _require_exact_list(assumptions_value, "$.assumptions")
    if len(assumptions_list) > MAX_ASSUMPTIONS:
        raise _schema_error("assumption_limit", "$.assumptions", f"assumptions exceed {MAX_ASSUMPTIONS} entries")
    assumptions = tuple(
        _check_text(item, f"$.assumptions[{index}]", MAX_TEXT_LENGTH)
        for index, item in enumerate(assumptions_list)
    )
    if len(set(assumptions)) != len(assumptions):
        raise _schema_error("duplicate_assumption", "$.assumptions", "assumptions must be unique")

    extensions_value = raw.get("extensions", {})
    extensions = _validate_extensions(extensions_value, "$.extensions")

    raw_rules = _require_exact_list(raw["rules"], "$.rules")
    if len(raw_rules) > MAX_RULES:
        raise _schema_error("rule_limit", "$.rules", f"rules exceed {MAX_RULES} entries")
    rules: list[Rule] = []
    seen_rule_ids: set[str] = set()
    for index, raw_rule in enumerate(raw_rules):
        rule_path = f"$.rules[{index}]"
        rule = _require_exact_dict(raw_rule, rule_path)
        _check_fields(rule, _RULE_REQUIRED_FIELDS, _RULE_OPTIONAL_FIELDS, rule_path)
        identifier = _check_identifier(rule["id"], f"{rule_path}.id", MAX_RULE_LENGTH)
        if identifier in seen_rule_ids:
            raise _schema_error("duplicate_rule", f"{rule_path}.id", "rule ids must be unique")
        seen_rule_ids.add(identifier)
        modality = rule["modality"]
        if type(modality) is not str or modality not in MODALITIES:
            raise _schema_error("invalid_modality", f"{rule_path}.modality", "modality must be O, F, or P")
        action = _check_identifier(rule["action"], f"{rule_path}.action", MAX_ACTION_LENGTH)
        if action not in actions:
            raise _schema_error("unknown_action", f"{rule_path}.action", "rule action is not declared")
        if action in RESERVED_ACTIONS:
            raise _schema_error("reserved_action_target", f"{rule_path}.action", "reserved actions are kernel-owned")
        predicate_counter = [0]
        predicate = _parse_predicate(
            rule["when"],
            f"{rule_path}.when",
            depth=0,
            counter=predicate_counter,
        )
        rule_extensions = _validate_extensions(rule.get("extensions", {}), f"{rule_path}.extensions")
        contrary_to_duty = rule.get("contrary_to_duty", False)
        if type(contrary_to_duty) is not bool:
            raise _schema_error("wrong_type", f"{rule_path}.contrary_to_duty", "contrary_to_duty must be a boolean")
        rules.append(Rule(identifier, modality, action, predicate, rule_extensions, contrary_to_duty))
    rules.sort(key=lambda item: item.identifier)
    validated = ValidatedPacket(
        decision_id=decision_id,
        logic_profile=logic_profile,
        policy_profile=compiled_policy_profile,
        actions=actions,
        facts=facts,
        false_facts=false_facts,
        rules=tuple(rules),
        allow_abstain=allow_abstain,
        assumptions=assumptions,
        extensions=extensions,
    )
    _ = validated.canonical_bytes
    return validated


@dataclass(frozen=True)
class ValidatedDecisionPack:
    policy_profile: PolicyProfile
    assumptions: tuple[str, ...]
    future_extension_nonclaims: tuple[str, ...]
    decisions: tuple[tuple[str, str, ValidatedPacket], ...]
    extensions: object

    @property
    def schema(self) -> str:
        return PACK_SCHEMA

    @property
    def policy_profile_sha256(self) -> str:
        return self.policy_profile.sha256

    def to_data(self) -> dict[str, object]:
        return {
            "schema": PACK_SCHEMA,
            "policy_profile": self.policy_profile.to_data(),
            "assumptions": list(self.assumptions),
            "future_extension_nonclaims": list(self.future_extension_nonclaims),
            "decisions": [
                {"id": identifier, "description": description, "packet": packet.to_data()}
                for identifier, description, packet in self.decisions
            ],
            "extensions": _thaw_json(self.extensions),
        }


def validate_decision_pack(pack: object) -> ValidatedDecisionPack:
    """Strictly validate a small collection of demo decision packets."""

    raw = _require_exact_dict(pack, "$")
    _check_json_shape(raw, "$", max_depth=MAX_PACKET_NESTING + 2)
    _check_fields(
        raw,
        {"schema", "policy_profile", "decisions", "assumptions", "future_extension_nonclaims"},
        {"extensions"},
        "$",
    )
    if raw["schema"] != PACK_SCHEMA:
        raise _schema_error("schema_version", "$.schema", f"expected {PACK_SCHEMA!r}")
    compiled_policy_profile = compile_policy_profile(raw["policy_profile"])

    def pack_text_list(field: str) -> tuple[str, ...]:
        values = _require_exact_list(raw[field], f"$.{field}")
        if len(values) > MAX_ASSUMPTIONS:
            raise _schema_error("assumption_limit", f"$.{field}", f"{field} exceeds {MAX_ASSUMPTIONS} entries")
        result = tuple(_check_text(item, f"$.{field}[{index}]", MAX_PACK_TEXT_LENGTH) for index, item in enumerate(values))
        if len(set(result)) != len(result):
            raise _schema_error("duplicate_text", f"$.{field}", f"{field} entries must be unique")
        return result

    assumptions = pack_text_list("assumptions")
    nonclaims = pack_text_list("future_extension_nonclaims")
    extensions = _validate_extensions(raw.get("extensions", {}), "$.extensions")

    raw_decisions = _require_exact_list(raw["decisions"], "$.decisions")
    if not 1 <= len(raw_decisions) <= MAX_PACK_DECISIONS:
        raise _schema_error("decision_limit", "$.decisions", f"decisions must contain between 1 and {MAX_PACK_DECISIONS} entries")
    decisions: list[tuple[str, str, ValidatedPacket]] = []
    seen_ids: set[str] = set()
    for index, raw_decision in enumerate(raw_decisions):
        path = f"$.decisions[{index}]"
        scenario = _require_exact_dict(raw_decision, path)
        _check_fields(scenario, _SCENARIO_FIELDS, set(), path)
        identifier = _check_identifier(scenario["id"], f"{path}.id", MAX_IDENTIFIER_LENGTH)
        if identifier in seen_ids:
            raise _schema_error("duplicate_decision", f"{path}.id", "decision ids must be unique")
        seen_ids.add(identifier)
        description = _check_text(scenario["description"], f"{path}.description", MAX_PACK_TEXT_LENGTH)
        packet = validate_packet(scenario["packet"], policy_profile=compiled_policy_profile)
        if packet.decision_id != identifier:
            raise _schema_error("decision_id_mismatch", f"{path}.packet.decision_id", "scenario id must match packet decision_id")
        decisions.append((identifier, description, packet))
    decisions.sort(key=lambda item: item[0])
    encoded = _canonical_json_bytes(
        {
            "schema": PACK_SCHEMA,
            "policy_profile": compiled_policy_profile.to_data(),
            "assumptions": list(assumptions),
            "future_extension_nonclaims": list(nonclaims),
            "decisions": [
                {"id": identifier, "description": description, "packet": packet.to_data()}
                for identifier, description, packet in decisions
            ],
            "extensions": _thaw_json(extensions),
        }
    )
    if len(encoded) > MAX_PACK_BYTES:
        raise _schema_error("pack_size_limit", "$", f"canonical pack exceeds {MAX_PACK_BYTES} bytes")
    return ValidatedDecisionPack(compiled_policy_profile, tuple(assumptions), tuple(nonclaims), tuple(decisions), extensions)


def load_decision_pack(path: str | Path) -> ValidatedDecisionPack:
    """Load and strictly validate a local JSON decision pack."""

    file_path = Path(path)
    try:
        with file_path.open("rb") as handle:
            raw = handle.read(MAX_PACK_BYTES + 1)
    except OSError as error:
        raise DeonticKernelError(f"could not read decision pack: {error}") from error
    if len(raw) > MAX_PACK_BYTES:
        raise _schema_error("input_size_limit", "$", f"input exceeds {MAX_PACK_BYTES} bytes")
    parsed = _parse_json_bytes(raw, maximum=MAX_PACK_BYTES)
    return validate_decision_pack(parsed)


@dataclass(frozen=True)
class RuleExamination:
    identifier: str
    modality: str
    action: str
    applicable: bool | None
    predicate: Predicate
    reason: str

    def to_data(self) -> dict[str, object]:
        return {
            "id": self.identifier,
            "modality": self.modality,
            "action": self.action,
            "applicable": self.applicable,
            "predicate": self.predicate.to_data(),
            "reason": self.reason,
        }


@dataclass(frozen=True)
class ActionStatus:
    action: str
    obligation: bool
    prohibition: bool
    permission: bool

    def to_data(self) -> dict[str, bool]:
        return {
            "O": self.obligation,
            "F": self.prohibition,
            "P": self.permission,
        }


@dataclass(frozen=True)
class Conflict:
    action: str
    modalities: tuple[str, ...]
    rule_ids: tuple[str, ...]
    reason: str

    def to_data(self) -> dict[str, object]:
        return {
            "action": self.action,
            "modalities": list(self.modalities),
            "rule_ids": list(self.rule_ids),
            "reason": self.reason,
        }


@dataclass(frozen=True)
class DecisionResult:
    """Immutable observable result of one validation/evaluation boundary."""

    decision_id: str
    valid: bool
    actions: tuple[str, ...]
    action_mask: tuple[bool, ...]
    obligatory_action_mask: tuple[bool, ...]
    selected_action: str | None
    resolution: str
    failure_mode: str | None
    input_sha256: str
    input_hash_mode: str
    policy_profile_id: str
    policy_profile_sha256: str
    logic_profile: str
    logic_semantics_sha256: str
    applicable_facts: tuple[str, ...]
    known_false_facts: tuple[str, ...]
    rules_examined: tuple[RuleExamination, ...]
    statuses: tuple[ActionStatus, ...]
    obligations: tuple[str, ...]
    prohibitions: tuple[str, ...]
    permissions: tuple[str, ...]
    conflicts: tuple[Conflict, ...]
    unresolved: tuple[str, ...]
    unknown_predicates: tuple[str, ...]
    receipt_json: str
    receipt_sha256: str
    validation_error: str | None

    @property
    def action_mask_by_action(self) -> dict[str, bool]:
        return dict(zip(self.actions, self.action_mask))

    @property
    def eligible_action_mask(self) -> tuple[bool, ...]:
        """The deontic eligibility mask exposed to an external optimizer."""

        return self.action_mask

    @property
    def obligatory_actions(self) -> tuple[str, ...]:
        return tuple(action for action, required in zip(self.actions, self.obligatory_action_mask) if required)

    @property
    def eligible_actions(self) -> tuple[str, ...]:
        return self.allowed_actions

    @property
    def deontic_mask(self) -> tuple[bool, ...]:
        return self.action_mask

    @property
    def rule_reasons(self) -> tuple[tuple[str, str], ...]:
        return tuple((item.identifier, item.reason) for item in self.rules_examined)

    @property
    def rule_reasons_by_id(self) -> dict[str, str]:
        return dict(self.rule_reasons)

    @property
    def allowed_actions(self) -> tuple[str, ...]:
        return tuple(action for action, allowed in zip(self.actions, self.action_mask) if allowed)

    @property
    def receipt(self) -> dict[str, object]:
        parsed = json.loads(self.receipt_json)
        if type(parsed) is not dict:
            raise DeonticKernelError("internal receipt is not an object")
        return parsed

    def to_dict(self) -> dict[str, object]:
        return {
            "decision_id": self.decision_id,
            "valid": self.valid,
            "actions": list(self.actions),
            "action_mask": self.action_mask_by_action,
            "eligible_action_mask": dict(zip(self.actions, self.eligible_action_mask)),
            "obligatory_action_mask": dict(zip(self.actions, self.obligatory_action_mask)),
            "allowed_actions": list(self.allowed_actions),
            "selected_action": self.selected_action,
            "resolution": self.resolution,
            "failure_mode": self.failure_mode,
            "input_sha256": self.input_sha256,
            "input_hash_mode": self.input_hash_mode,
            "policy_profile_id": self.policy_profile_id,
            "policy_profile_sha256": self.policy_profile_sha256,
            "logic_profile": self.logic_profile,
            "logic_semantics_sha256": self.logic_semantics_sha256,
            "applicable_facts": list(self.applicable_facts),
            "known_false_facts": list(self.known_false_facts),
            "obligations": list(self.obligations),
            "prohibitions": list(self.prohibitions),
            "permissions": list(self.permissions),
            "conflicts": [conflict.to_data() for conflict in self.conflicts],
            "unresolved": list(self.unresolved),
            "unknown_predicates": list(self.unknown_predicates),
            "rule_reasons": dict(self.rule_reasons),
            "receipt": self.receipt,
            "receipt_sha256": self.receipt_sha256,
            "validation_error": self.validation_error,
        }

    def __getitem__(self, key: str) -> object:
        if key == "mask":
            key = "action_mask"
        if key == "receipt_hash":
            key = "receipt_sha256"
        return self.to_dict()[key]

    def get(self, key: str, default: object = None) -> object:
        try:
            return self[key]
        except KeyError:
            return default


_NONCLAIMS = (
    "The selected profile is a bounded finite detachment profile, not Standard Deontic Logic.",
    "A policy profile is a declared normative fixture, not universal ethics or a best normative theory.",
    "Extensions are metadata only and do not implement temporal, exception, priority, or theorem checking.",
    "A deterministic derivation receipt and human explanation are not a machine-checkable proof object.",
    "Finite trace checks are bounded counterexample checks, not full LTL model checking.",
)


def _build_receipt(
    *,
    packet_schema: str,
    decision_id: str,
    valid: bool,
    policy_profile_id: str,
    policy_profile_sha256: str,
    logic_profile: str,
    logic_semantics_sha256: str,
    input_sha256: str,
    input_hash_mode: str,
    applicable_facts: tuple[str, ...],
    rules_examined: tuple[RuleExamination, ...],
    statuses: tuple[ActionStatus, ...],
    obligations: tuple[str, ...],
    prohibitions: tuple[str, ...],
    permissions: tuple[str, ...],
    conflicts: tuple[Conflict, ...],
    unresolved: tuple[str, ...],
    actions: tuple[str, ...],
    action_mask: tuple[bool, ...],
    obligatory_action_mask: tuple[bool, ...],
    selected_action: str | None,
    resolution: str,
    assumptions: tuple[str, ...],
    known_false_facts: tuple[str, ...],
    unknown_predicates: tuple[str, ...],
    failure_mode: str | None,
    validation_error: str | None,
) -> tuple[str, str]:
    receipt: dict[str, object] = {
        "receipt_schema": RECEIPT_SCHEMA,
        "kernel_version": KERNEL_VERSION,
        "packet_schema": packet_schema,
        "predicate_language": PREDICATE_LANGUAGE,
        "decision_id": decision_id,
        "valid": valid,
        "policy_profile_id": policy_profile_id,
        "policy_profile_sha256": policy_profile_sha256,
        "logic_profile": logic_profile,
        "logic_semantics_sha256": logic_semantics_sha256,
        "input_sha256": input_sha256,
        "input_hash_mode": input_hash_mode,
        "applicable_facts": list(applicable_facts),
        "known_false_facts": list(known_false_facts),
        "rules_examined": [rule.to_data() for rule in rules_examined],
        "rule_reasons": {rule.identifier: rule.reason for rule in rules_examined},
        "derived_statuses": {
            status.action: status.to_data()
            for status in statuses
        },
        "obligations": list(obligations),
        "prohibitions": list(prohibitions),
        "explicit_permissions": list(permissions),
        "conflicts": [conflict.to_data() for conflict in conflicts],
        "unresolved": list(unresolved),
        "unknown_predicates": list(unknown_predicates),
        "action_mask": dict(zip(actions, action_mask)),
        "eligible_action_mask": dict(zip(actions, action_mask)),
        "obligatory_action_mask": dict(zip(actions, obligatory_action_mask)),
        "resolution": resolution,
        "selected_action": selected_action,
        "failure_mode": failure_mode,
        "assumptions": list(assumptions),
        "limits": dict(LIMITS),
        "nonclaims": list(_NONCLAIMS),
        "artifact_distinctions": {
            "deterministic_derivation_receipt": True,
            "human_explanation": True,
            "machine_checkable_proof_object": False,
            "countermodel_or_counterexample": "finite_trace_checker_only",
        },
        "validation_error": validation_error,
    }
    encoded = _canonical_json_bytes(receipt)
    if len(encoded) > MAX_RECEIPT_BYTES:
        raise DeonticKernelError("internal receipt exceeded its hard bound")
    return encoded.decode("ascii"), hashlib.sha256(encoded).hexdigest()


def _result(
    *,
    decision_id: str,
    valid: bool,
    actions: tuple[str, ...],
    action_mask: tuple[bool, ...],
    obligatory_action_mask: tuple[bool, ...],
    selected_action: str | None,
    resolution: str,
    failure_mode: str | None,
    input_sha256: str,
    input_hash_mode: str,
    policy_profile_id: str,
    policy_profile_sha256: str,
    logic_profile: str,
    logic_semantics_sha256: str,
    applicable_facts: tuple[str, ...],
    known_false_facts: tuple[str, ...],
    rules_examined: tuple[RuleExamination, ...],
    statuses: tuple[ActionStatus, ...],
    obligations: tuple[str, ...],
    prohibitions: tuple[str, ...],
    permissions: tuple[str, ...],
    conflicts: tuple[Conflict, ...],
    unresolved: tuple[str, ...],
    unknown_predicates: tuple[str, ...],
    assumptions: tuple[str, ...],
    validation_error: str | None,
) -> DecisionResult:
    receipt_json, receipt_sha256 = _build_receipt(
        packet_schema=PACKET_SCHEMA,
        decision_id=decision_id,
        valid=valid,
        policy_profile_id=policy_profile_id,
        policy_profile_sha256=policy_profile_sha256,
        logic_profile=logic_profile,
        logic_semantics_sha256=logic_semantics_sha256,
        input_sha256=input_sha256,
        input_hash_mode=input_hash_mode,
        applicable_facts=applicable_facts,
        rules_examined=rules_examined,
        statuses=statuses,
        obligations=obligations,
        prohibitions=prohibitions,
        permissions=permissions,
        conflicts=conflicts,
        unresolved=unresolved,
        actions=actions,
        action_mask=action_mask,
        obligatory_action_mask=obligatory_action_mask,
        selected_action=selected_action,
        resolution=resolution,
        assumptions=assumptions,
        known_false_facts=known_false_facts,
        unknown_predicates=unknown_predicates,
        failure_mode=failure_mode,
        validation_error=validation_error,
    )
    return DecisionResult(
        decision_id=decision_id,
        valid=valid,
        actions=actions,
        action_mask=action_mask,
        obligatory_action_mask=obligatory_action_mask,
        selected_action=selected_action,
        resolution=resolution,
        failure_mode=failure_mode,
        input_sha256=input_sha256,
        input_hash_mode=input_hash_mode,
        policy_profile_id=policy_profile_id,
        policy_profile_sha256=policy_profile_sha256,
        logic_profile=logic_profile,
        logic_semantics_sha256=logic_semantics_sha256,
        applicable_facts=applicable_facts,
        known_false_facts=known_false_facts,
        rules_examined=rules_examined,
        statuses=statuses,
        obligations=obligations,
        prohibitions=prohibitions,
        permissions=permissions,
        conflicts=conflicts,
        unresolved=unresolved,
        unknown_predicates=unknown_predicates,
        receipt_json=receipt_json,
        receipt_sha256=receipt_sha256,
        validation_error=validation_error,
    )


def _best_effort_input_hash(value: object) -> tuple[str, str]:
    if type(value) is bytes:
        return hashlib.sha256(value).hexdigest(), "raw-bytes"
    if type(value) is str:
        try:
            return hashlib.sha256(value.encode("utf-8")).hexdigest(), "raw-utf8"
        except UnicodeEncodeError:
            pass
    try:
        encoded = _canonical_json_bytes(value)
        return hashlib.sha256(encoded).hexdigest(), "canonical-json-invalid"
    except (DeonticKernelError, TypeError, ValueError, OverflowError):
        encoded = b"<invalid-input>"
        return hashlib.sha256(encoded).hexdigest(), "invalid-input-sentinel"


def _best_effort_policy_profile_hash(value: object) -> tuple[str, str, str]:
    """Bind a candidate profile hash even when packet validation fails."""

    if type(value) is dict and "policy_profile" in value:
        candidate = value["policy_profile"]
        try:
            encoded = _canonical_json_bytes(candidate)
            return hashlib.sha256(encoded).hexdigest(), "unvalidated-canonical-json", "unvalidated"
        except (DeonticKernelError, TypeError, ValueError, OverflowError):
            pass
    return POLICY_PROFILE_SHA256, "neutral-default", NEUTRAL_EVIDENCE_COMPLETION_POLICY_PROFILE.profile_id


def _reserved_statuses(actions: tuple[str, ...], *, abstain_allowed: bool) -> tuple[ActionStatus, ...]:
    return tuple(
        ActionStatus(
            action=action,
            obligation=False,
            prohibition=False,
            permission=(action == ESCALATE_ACTION or (action == ABSTAIN_ACTION and abstain_allowed)),
        )
        for action in actions
    )


def _invalid_result(error: SchemaError, value: object) -> DecisionResult:
    input_sha256, input_hash_mode = _best_effort_input_hash(value)
    policy_profile_sha256, _policy_hash_mode, policy_profile_id = _best_effort_policy_profile_hash(value)
    actions = tuple(sorted(RESERVED_ACTIONS))
    action_mask = (False, True) if actions == (ABSTAIN_ACTION, ESCALATE_ACTION) else tuple(action == ESCALATE_ACTION for action in actions)
    obligatory_action_mask = tuple(False for _ in actions)
    statuses = _reserved_statuses(actions, abstain_allowed=False)
    return _result(
        decision_id="invalid",
        valid=False,
        actions=actions,
        action_mask=action_mask,
        obligatory_action_mask=obligatory_action_mask,
        selected_action=ESCALATE_ACTION,
        resolution="escalate",
        failure_mode="schema_rejection",
        input_sha256=input_sha256,
        input_hash_mode=input_hash_mode,
        policy_profile_id=policy_profile_id,
        policy_profile_sha256=policy_profile_sha256,
        logic_profile=LOGIC_PROFILE_ID,
        logic_semantics_sha256=LOGIC_SEMANTICS_HASH,
        applicable_facts=(),
        known_false_facts=(),
        rules_examined=(),
        statuses=statuses,
        obligations=(),
        prohibitions=(),
        permissions=(),
        conflicts=(),
        unresolved=("invalid_packet",),
        unknown_predicates=(),
        assumptions=("Invalid input is quarantined; the safe boundary permits escalation only.",),
        validation_error=f"{error.code} at {error.path}: {error.detail}",
    )


def _evaluate_valid(packet: ValidatedPacket) -> DecisionResult:
    facts = frozenset(packet.facts)
    false_facts = frozenset(packet.false_facts)

    def examination_reason(value: bool | None) -> str:
        if value is True:
            return "detached"
        if value is False:
            return "predicate_false"
        return "unknown_predicate_applicability"

    examined_items: list[RuleExamination] = []
    for rule in packet.rules:
        applicability = rule.predicate.applies(facts, false_facts)
        examined_items.append(
            RuleExamination(
                identifier=rule.identifier,
                modality=rule.modality,
                action=rule.action,
                applicable=applicability,
                predicate=rule.predicate,
                reason=examination_reason(applicability),
            )
        )
    examinations = tuple(examined_items)
    applicable = tuple(examination for examination in examinations if examination.applicable is True)
    unknown_examinations = tuple(examination for examination in examinations if examination.applicable is None)
    unknown_predicates = tuple(item.identifier for item in unknown_examinations)
    obligations_set = {item.action for item in applicable if item.modality == OBLIGATION}
    prohibitions_set = {item.action for item in applicable if item.modality == PROHIBITION}
    permissions_set = {item.action for item in applicable if item.modality == PERMISSION}
    obligations = tuple(action for action in packet.actions if action in obligations_set)
    prohibitions = tuple(action for action in packet.actions if action in prohibitions_set)
    permissions = tuple(action for action in packet.actions if action in permissions_set)

    conflicts: list[Conflict] = []
    for action in packet.actions:
        if action in RESERVED_ACTIONS:
            continue
        action_modalities = set()
        action_rule_ids: set[str] = set()
        if action in obligations_set:
            action_modalities.add(OBLIGATION)
        if action in prohibitions_set:
            action_modalities.add(PROHIBITION)
        if action in permissions_set:
            action_modalities.add(PERMISSION)
        if PROHIBITION in action_modalities and (
            OBLIGATION in action_modalities or PERMISSION in action_modalities
        ):
            for examination in applicable:
                if examination.action == action:
                    action_rule_ids.add(examination.identifier)
            if OBLIGATION in action_modalities:
                reason = "applicable obligation and prohibition cannot be coherent"
            else:
                reason = "applicable permission and prohibition cannot be coherent"
            conflicts.append(
                Conflict(
                    action=action,
                    modalities=tuple(modality for modality in MODALITIES if modality in action_modalities),
                    rule_ids=tuple(sorted(action_rule_ids)),
                    reason=reason,
                )
            )
    conflicts_tuple = tuple(conflicts)

    unresolved: list[str] = []
    hard_failures: list[str] = []
    if unknown_examinations:
        hard_failures.extend(("incomplete_context", "unknown_predicate_applicability"))
    if len(obligations) > 1:
        hard_failures.append("multiple_incompatible_obligations")
    if any(rule.contrary_to_duty for rule in packet.rules):
        hard_failures.append("contrary_to_duty_not_implemented")
    unresolved.extend(hard_failures)
    positive_actions = tuple(
        action
        for action in packet.actions
        if action not in RESERVED_ACTIONS
        and (action in obligations_set or action in permissions_set)
        and action not in prohibitions_set
    )
    if not positive_actions:
        unresolved.append("no_applicable_positive_action")

    if conflicts_tuple or hard_failures:
        resolution = "escalate"
        selected_action = ESCALATE_ACTION
        action_mask = tuple(action == ESCALATE_ACTION for action in packet.actions)
        abstain_allowed = False
        failure_mode = "quarantine"
    elif not positive_actions:
        abstain_allowed = packet.allow_abstain
        resolution = "abstain" if abstain_allowed else "escalate"
        selected_action = ABSTAIN_ACTION if abstain_allowed else ESCALATE_ACTION
        action_mask = tuple(
            action == ESCALATE_ACTION or (action == ABSTAIN_ACTION and abstain_allowed)
            for action in packet.actions
        )
        failure_mode = "conservative_abstention" if abstain_allowed else "escalation"
    else:
        abstain_allowed = False
        resolution = "allow"
        selected_action = None
        action_mask = tuple(
            action in positive_actions
            for action in packet.actions
        )
        failure_mode = None

    # Optimizers consume the masks, while the raw O/F/P derivations remain in
    # statuses and obligations. A quarantined obligation must never survive as
    # an executable requirement outside the eligible mask.
    obligatory_action_mask = tuple(
        action in obligations_set and allowed
        for action, allowed in zip(packet.actions, action_mask)
    )

    statuses = tuple(
        ActionStatus(
            action=action,
            obligation=action in obligations_set,
            prohibition=action in prohibitions_set,
            permission=(
                action in permissions_set or action in obligations_set
            ),
        )
        for action in packet.actions
    )
    return _result(
        decision_id=packet.decision_id,
        valid=True,
        actions=packet.actions,
        action_mask=action_mask,
        obligatory_action_mask=obligatory_action_mask,
        selected_action=selected_action,
        resolution=resolution,
        failure_mode=failure_mode,
        input_sha256=hashlib.sha256(packet.canonical_bytes).hexdigest(),
        input_hash_mode="canonical-normalized-packet",
        policy_profile_id=packet.policy_profile.profile_id,
        policy_profile_sha256=packet.policy_profile.sha256,
        logic_profile=packet.logic_profile,
        logic_semantics_sha256=LOGIC_SEMANTICS_HASH,
        applicable_facts=packet.facts,
        known_false_facts=packet.false_facts,
        rules_examined=examinations,
        statuses=statuses,
        obligations=obligations,
        prohibitions=prohibitions,
        permissions=permissions,
        conflicts=conflicts_tuple,
        unresolved=tuple(unresolved),
        unknown_predicates=unknown_predicates,
        assumptions=packet.assumptions,
        validation_error=None,
    )


def evaluate(packet: object, *, policy_profile: object | None = None) -> DecisionResult:
    """Evaluate a packet and fail closed to escalation on schema rejection."""

    try:
        validated = validate_packet(packet, policy_profile=policy_profile)
    except SchemaError as error:
        return _invalid_result(error, packet)
    return _evaluate_valid(validated)


def evaluate_strict(packet: object, *, policy_profile: object | None = None) -> DecisionResult:
    """Strict evaluation variant that propagates schema rejection."""

    return _evaluate_valid(validate_packet(packet, policy_profile=policy_profile))


def evaluate_json(raw: bytes | str, *, policy_profile: object | None = None) -> DecisionResult:
    """Evaluate packet JSON, including parse failures, through escalation."""

    try:
        packet = parse_json(raw)
    except SchemaError as error:
        return _invalid_result(error, raw)
    return evaluate(packet, policy_profile=policy_profile)


def evaluate_decision_pack(pack: object) -> tuple[tuple[str, DecisionResult], ...]:
    """Evaluate every packet in a validated, canonically ordered pack."""

    validated = validate_decision_pack(pack)
    return tuple((identifier, _evaluate_valid(packet)) for identifier, _description, packet in validated.decisions)


TRACE_PENDING = "pending"
TRACE_RESOLVED = "resolved"
TRACE_ABSTAIN = "abstain"
TRACE_QUARANTINE = "quarantine"
TRACE_ESCALATE = "escalate"
TRACE_TERMINAL_STATES = (TRACE_RESOLVED, TRACE_ABSTAIN, TRACE_QUARANTINE, TRACE_ESCALATE)


@dataclass(frozen=True)
class TraceStep:
    """One chronologically numbered observation in a bounded trace."""

    step: int
    state: str
    executed_action: str | None = None

    def to_data(self) -> dict[str, object]:
        result: dict[str, object] = {"step": self.step, "state": self.state}
        if self.executed_action is not None:
            result["executed_action"] = self.executed_action
        return result


@dataclass(frozen=True)
class TraceCheckResult:
    """PASS or a concrete counterexample inside the declared finite trace."""

    status: str
    deadline: int | None
    trace_sha256: str
    checked_steps: tuple[TraceStep, ...]
    _counterexample: object | None
    reason: str

    @property
    def passed(self) -> bool:
        return self.status == "PASS"

    @property
    def counterexample(self) -> object | None:
        return _thaw_json(self._counterexample) if self._counterexample is not None else None

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": TRACE_SCHEMA,
            "status": self.status,
            "deadline": self.deadline,
            "trace_sha256": self.trace_sha256,
            "checked_steps": [step.to_data() for step in self.checked_steps],
            "counterexample": self.counterexample,
            "reason": self.reason,
            "nonclaim": "This is a bounded trace check, not full LTL model checking.",
            "artifact_distinctions": {
                "deterministic_derivation_receipt": False,
                "human_explanation": False,
                "machine_checkable_proof_object": False,
                "countermodel_or_counterexample": self.counterexample is not None,
            },
        }


def _trace_failure(
    *,
    raw_trace: object,
    deadline: int | None,
    steps: tuple[TraceStep, ...],
    reason: str,
    kind: str,
    index: int | None = None,
) -> TraceCheckResult:
    input_sha256, _ = _best_effort_input_hash(raw_trace)
    prefix = steps if index is None else steps[: index + 1]
    counterexample: dict[str, object] = {
        "kind": kind,
        "reason": reason,
        "deadline": deadline,
        "trace": [step.to_data() for step in prefix],
    }
    if index is not None:
        counterexample["index"] = index
        counterexample["step"] = steps[index].step
    return TraceCheckResult(
        status="FAIL",
        deadline=deadline,
        trace_sha256=input_sha256,
        checked_steps=steps,
        _counterexample=_freeze_json(counterexample),
        reason=reason,
    )


def _validate_trace(trace: object) -> tuple[int, tuple[str, ...], tuple[TraceStep, ...]]:
    raw = _require_exact_dict(trace, "$")
    _check_json_shape(
        raw,
        "$",
        max_depth=MAX_PACKET_NESTING + 2,
        max_nodes=MAX_TRACE_STEPS * 4 + 16,
        max_collection_items=MAX_TRACE_STEPS,
    )
    _check_fields(raw, {"schema", "deadline", "forbidden_actions", "steps"}, set(), "$")
    if raw["schema"] != TRACE_SCHEMA:
        raise _schema_error("schema_version", "$.schema", f"expected {TRACE_SCHEMA!r}")
    deadline = raw["deadline"]
    if type(deadline) is not int or not 0 <= deadline <= MAX_TRACE_DEADLINE:
        raise _schema_error("trace_deadline", "$.deadline", f"deadline must be an integer from 0 to {MAX_TRACE_DEADLINE}")
    raw_forbidden = _require_exact_list(raw["forbidden_actions"], "$.forbidden_actions")
    if len(raw_forbidden) > MAX_ACTIONS:
        raise _schema_error("action_limit", "$.forbidden_actions", f"forbidden_actions exceed {MAX_ACTIONS} entries")
    forbidden = tuple(
        sorted(_check_identifier(item, f"$.forbidden_actions[{index}]", MAX_ACTION_LENGTH) for index, item in enumerate(raw_forbidden))
    )
    if len(set(forbidden)) != len(forbidden):
        raise _schema_error("duplicate_action", "$.forbidden_actions", "forbidden actions must be unique")

    raw_steps = _require_exact_list(raw["steps"], "$.steps")
    if not 1 <= len(raw_steps) <= MAX_TRACE_STEPS:
        raise _schema_error("trace_step_limit", "$.steps", f"steps must contain between 1 and {MAX_TRACE_STEPS} entries")
    steps: list[TraceStep] = []
    for index, raw_step in enumerate(raw_steps):
        path = f"$.steps[{index}]"
        step_object = _require_exact_dict(raw_step, path)
        _check_fields(step_object, {"step", "state"}, {"executed_action"}, path)
        step_number = step_object["step"]
        if type(step_number) is not int or not 0 <= step_number <= MAX_TRACE_STEPS:
            raise _schema_error("trace_step", f"{path}.step", f"step must be an integer from 0 to {MAX_TRACE_STEPS}")
        state = step_object["state"]
        if type(state) is not str or state not in (TRACE_PENDING, *TRACE_TERMINAL_STATES):
            raise _schema_error("trace_state", f"{path}.state", "state is outside the bounded trace state set")
        executed_action_value = step_object.get("executed_action")
        executed_action: str | None = None
        if executed_action_value is not None:
            executed_action = _check_identifier(executed_action_value, f"{path}.executed_action", MAX_ACTION_LENGTH)
        if index == 0 and step_number != 0:
            raise _schema_error("trace_order", f"{path}.step", "the first chronological step must be 0")
        if index and step_number != steps[-1].step + 1:
            raise _schema_error("trace_order", f"{path}.step", "chronological step fields must increase by one")
        steps.append(TraceStep(step=step_number, state=state, executed_action=executed_action))
    return deadline, forbidden, tuple(steps)


def check_finite_trace(trace: object) -> TraceCheckResult:
    """Check bounded trace obligations and return PASS or a counterexample."""

    input_sha256, _ = _best_effort_input_hash(trace)
    try:
        deadline, forbidden, steps = _validate_trace(trace)
    except SchemaError as error:
        return TraceCheckResult(
            status="FAIL",
            deadline=None,
            trace_sha256=input_sha256,
            checked_steps=(),
            _counterexample=_freeze_json(
                {
                    "kind": "schema",
                    "reason": f"{error.code} at {error.path}: {error.detail}",
                    "trace": [],
                }
            ),
            reason=f"{error.code} at {error.path}: {error.detail}",
        )

    for index, step in enumerate(steps):
        if step.executed_action in forbidden:
            return _trace_failure(
                raw_trace=trace,
                deadline=deadline,
                steps=steps,
                reason="executed action is forbidden",
                kind="forbidden_action",
                index=index,
            )

    terminal_index: int | None = None
    for index, step in enumerate(steps):
        if step.state in TRACE_TERMINAL_STATES and terminal_index is None:
            terminal_index = index
        elif terminal_index is not None and step.state == TRACE_PENDING:
            return _trace_failure(
                raw_trace=trace,
                deadline=deadline,
                steps=steps,
                reason="terminal resolution transitioned back to pending",
                kind="terminal_to_pending",
                index=index,
            )

    if terminal_index is None or steps[terminal_index].step > deadline:
        return _trace_failure(
            raw_trace=trace,
            deadline=deadline,
            steps=steps,
            reason="trace has no terminal resolution by the declared deadline",
            kind="deadline_liveness",
        )
    return TraceCheckResult(
        status="PASS",
        deadline=deadline,
        trace_sha256=input_sha256,
        checked_steps=steps,
        _counterexample=None,
        reason="bounded trace obligations satisfied",
    )


def check_trace(trace: object) -> TraceCheckResult:
    """Compatibility alias for the finite trace checker."""

    return check_finite_trace(trace)


def _is_lower_sha256(value: object) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _normalize_esso_results(value: object) -> list[dict[str, object]]:
    if type(value) is tuple and len(value) == 2 and value[0] in {"__dict__", "__list__"}:
        value = _thaw_json(value)
    if type(value) not in (list, tuple):
        raise _schema_error("esso_evidence_type", "$.results", "ESSO results must be a finite array")
    results = list(value)
    _check_json_shape(
        results,
        "$.results",
        max_depth=8,
        max_nodes=512,
        max_collection_items=64,
    )
    normalized: list[dict[str, object]] = []
    for index, result in enumerate(results):
        normalized.append(_require_exact_dict(result, f"$.results[{index}]"))
    return normalized


def _esso_pass_evidence_error(
    commands: tuple[str, ...],
    results: list[dict[str, object]],
) -> str | None:
    for marker in (" guide ", " validate ", " verify-multi "):
        if not any(marker in f" {command} " for command in commands):
            return f"PASS evidence is missing an ESSO{marker.rstrip()} command"

    by_command: dict[str, dict[str, object]] = {}
    for result in results:
        command = result.get("command")
        if type(command) is str:
            by_command[command] = result

    guide = by_command.get("guide")
    if guide is None or guide.get("ok") is not True:
        return "PASS requires a successful ESSO guide result"
    validate = by_command.get("validate")
    if validate is None or validate.get("ok") is not True or validate.get("errors") != []:
        return "PASS requires ESSO validation with no recorded errors"
    verify = by_command.get("verify-multi")
    if verify is None or verify.get("ok") is not True or verify.get("verdict") != "VERIFIED":
        return "PASS requires a VERIFIED ESSO verify-multi result"
    if verify.get("determinism") is not True:
        return "PASS requires deterministic repeated ESSO verification"
    if verify.get("solvers_agreed") is not True:
        return "PASS requires solver agreement"
    if verify.get("failed_queries") != 0 or verify.get("inconclusive_queries") != 0:
        return "PASS forbids failed or inconclusive ESSO queries"
    total = verify.get("total_queries")
    passed = verify.get("passed_queries")
    if type(total) is not int or type(passed) is not int or total < 1 or passed != total:
        return "PASS requires every non-empty ESSO query set to pass"
    solvers = verify.get("solvers")
    solver_names = set(solvers) if type(solvers) is list and all(type(item) is str for item in solvers) else set()
    cross_solver = {"z3", "cvc5"}.issubset(solver_names) or (
        verify.get("z3_passed") is True and verify.get("cvc5_passed") is True
    )
    if not cross_solver:
        return "PASS requires successful Z3 and CVC5 results"
    return None


@dataclass(frozen=True)
class ESSOVerificationStatus:
    """Evidence-bound ESSO status; absence or uncertainty never becomes PASS."""

    model_sha256: str
    tool: str
    commands: tuple[str, ...]
    results: object
    status: str = "NOT_RUN"
    reason: str = ""

    def __post_init__(self) -> None:
        status = self.status if self.status in {"NOT_RUN", "PASS", "FAIL", "UNKNOWN"} else "FAIL"
        reason = self.reason if type(self.reason) is str else ""
        evidence_error: str | None = None
        commands: tuple[str, ...] = ()
        results: list[dict[str, object]] = []
        try:
            if not _is_lower_sha256(self.model_sha256):
                raise _schema_error("esso_model_hash", "$.model_sha256", "expected a lowercase SHA-256 digest")
            _check_text(self.tool, "$.tool", MAX_PACK_TEXT_LENGTH)
            if type(self.commands) not in (list, tuple):
                raise _schema_error("esso_evidence_type", "$.commands", "ESSO commands must be a finite array")
            if len(self.commands) > 16:
                raise _schema_error("esso_evidence_limit", "$.commands", "ESSO commands exceed 16 entries")
            commands = tuple(
                _check_text(command, f"$.commands[{index}]", MAX_PACK_TEXT_LENGTH)
                for index, command in enumerate(self.commands)
            )
            results = _normalize_esso_results(self.results)
            if len(results) > 16:
                raise _schema_error("esso_evidence_limit", "$.results", "ESSO results exceed 16 entries")
        except (SchemaError, DeonticKernelError, RecursionError) as error:
            status = "FAIL"
            evidence_error = f"invalid ESSO evidence: {error}"
            commands = ()
            results = []
        if status == "PASS" and evidence_error is None:
            evidence_error = _esso_pass_evidence_error(commands, results)
            if evidence_error is not None:
                status = "FAIL"
        if evidence_error is not None:
            reason = evidence_error
        if not reason:
            reason = "No ESSO verification has been run" if status == "NOT_RUN" else "Recorded ESSO verification status"
        object.__setattr__(self, "commands", commands)
        object.__setattr__(self, "results", _freeze_json(results))
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "reason", reason)

    @property
    def schema(self) -> str:
        return ESSO_VERIFICATION_STATUS_SCHEMA

    @property
    def verified(self) -> bool:
        return self.status == "PASS"

    def to_data(self) -> dict[str, object]:
        return {
            "schema": ESSO_VERIFICATION_STATUS_SCHEMA,
            "model_sha256": self.model_sha256,
            "tool": self.tool,
            "commands": list(self.commands),
            "results": _thaw_json(self.results),
            "status": self.status,
            "verified": self.verified,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class ESSOAdapterProfile:
    """Immutable ESSO-IR v1 plus its explicitly untrusted verification status."""

    _ir: object
    model_sha256: str
    verification_status: ESSOVerificationStatus
    scenario_ids: tuple[str, ...]

    @property
    def ir(self) -> dict[str, object]:
        value = _thaw_json(self._ir)
        if type(value) is not dict:
            raise DeonticKernelError("internal ESSO IR is not an object")
        return value

    @property
    def esso_ir(self) -> dict[str, object]:
        return self.ir

    def to_data(self) -> dict[str, object]:
        return {
            "ir": self.ir,
            "model_sha256": self.model_sha256,
            "scenario_ids": list(self.scenario_ids),
            "verification_status": self.verification_status.to_data(),
            "nonclaim": (
                "ESSO evidence is structurally checked and model-hash-bound, not authenticated; "
                "the status is not a proof object."
            ),
        }


def _esso_expr_not(expr: dict[str, object]) -> dict[str, object]:
    return {"op": "not", "args": [expr]}


def _esso_expr_or(*expressions: dict[str, object]) -> dict[str, object]:
    return {"op": "or", "args": list(expressions)}


def _esso_expr_and(*expressions: dict[str, object]) -> dict[str, object]:
    return {"op": "and", "args": list(expressions)}


def _esso_expr_eq(left: dict[str, object], right: dict[str, object]) -> dict[str, object]:
    return {"op": "=", "args": [left, right]}


def _esso_scenario_results(scenarios: object) -> tuple[DecisionResult, ...]:
    if isinstance(scenarios, ValidatedDecisionPack):
        return tuple(_evaluate_valid(packet) for _identifier, _description, packet in scenarios.decisions)
    if isinstance(scenarios, DecisionResult):
        return (scenarios,)
    if type(scenarios) is dict and "decisions" in scenarios:
        return tuple(result for _identifier, result in evaluate_decision_pack(scenarios))
    if type(scenarios) in (list, tuple):
        results: list[DecisionResult] = []
        for item in scenarios:
            if isinstance(item, DecisionResult):
                results.append(item)
            else:
                results.append(evaluate(item))
        return tuple(results)
    raise DeonticKernelError("ESSO adapter expects a validated pack, result, or finite scenario sequence")


def compile_esso_ir(scenarios: object) -> ESSOAdapterProfile:
    """Compile evaluated finite outcomes into a deterministic ESSO-IR v1 profile."""

    results = tuple(sorted(_esso_scenario_results(scenarios), key=lambda result: result.decision_id))
    if not results:
        raise DeonticKernelError("ESSO adapter requires at least one evaluated scenario")
    scenario_ids = tuple(result.decision_id for result in results)
    if len(set(scenario_ids)) != len(scenario_ids):
        raise DeonticKernelError("ESSO adapter requires unique scenario decision ids")
    for index, result in enumerate(results):
        _check_identifier(result.decision_id, f"$.scenarios[{index}].decision_id", MAX_IDENTIFIER_LENGTH)
        if len(result.actions) != len(result.action_mask) or len(result.actions) != len(result.obligatory_action_mask):
            raise DeonticKernelError("ESSO adapter requires action-aligned eligible and obligatory masks")
        if any(required and not allowed for required, allowed in zip(result.obligatory_action_mask, result.action_mask)):
            raise DeonticKernelError("ESSO adapter rejects an obligatory action outside the eligible mask")
    if len({result.policy_profile_sha256 for result in results}) != 1:
        raise DeonticKernelError("ESSO adapter requires one policy profile per compiled model")
    if len({result.logic_semantics_sha256 for result in results}) != 1:
        raise DeonticKernelError("ESSO adapter requires one logic semantics profile per compiled model")

    phases: list[str] = []
    for result in results:
        if result.failure_mode == "quarantine":
            phase = "Quarantine"
        elif result.resolution == "allow":
            phase = "Resolved"
        elif result.resolution == "abstain":
            phase = "Abstain"
        else:
            phase = "Escalate"
        phases.append(phase)

    def mask_digest(result: DecisionResult, mask: tuple[bool, ...]) -> str:
        return canonical_sha256(dict(zip(result.actions, mask)))

    receipt_symbols = tuple(sorted({"rh_" + result.receipt_sha256 for result in results}))
    policy_symbols = tuple(sorted({"ph_" + result.policy_profile_sha256 for result in results}))
    logic_symbols = tuple(sorted({"lh_" + result.logic_semantics_sha256 for result in results}))
    eligible_symbols = tuple(sorted({"em_" + mask_digest(result, result.eligible_action_mask) for result in results}))
    obligatory_symbols = tuple(sorted({"om_" + mask_digest(result, result.obligatory_action_mask) for result in results}))
    reason_symbols = tuple(sorted({"rr_" + canonical_sha256(dict(result.rule_reasons)) for result in results}))
    phase_symbols = ("Pending", "Resolved", "Abstain", "Quarantine", "Escalate")

    state_vars = [
        {"id": "phase", "role": "control", "type": {"ref": "t_phase"}},
        {"id": "coherent", "role": "data", "type": {"kind": "bool"}},
        {"id": "obligation_visible", "role": "data", "type": {"kind": "bool"}},
        {"id": "permission_visible", "role": "data", "type": {"kind": "bool"}},
        {"id": "conflict_present", "role": "data", "type": {"kind": "bool"}},
        {"id": "incomplete_context", "role": "data", "type": {"kind": "bool"}},
        {"id": "fail_closed_mask", "role": "data", "type": {"kind": "bool"}},
        {"id": "receipt_bound", "role": "data", "type": {"kind": "bool"}},
    ]
    types = [
        {"id": "t_phase", "type": {"kind": "enum", "symbols": list(phase_symbols)}},
        {"id": "t_receipt_hash", "type": {"kind": "enum", "symbols": list(receipt_symbols)}},
        {"id": "t_policy_hash", "type": {"kind": "enum", "symbols": list(policy_symbols)}},
        {"id": "t_logic_hash", "type": {"kind": "enum", "symbols": list(logic_symbols)}},
        {"id": "t_eligible_mask", "type": {"kind": "enum", "symbols": list(eligible_symbols)}},
        {"id": "t_obligatory_mask", "type": {"kind": "enum", "symbols": list(obligatory_symbols)}},
        {"id": "t_rule_reasons", "type": {"kind": "enum", "symbols": list(reason_symbols)}},
    ]
    init = [
        {"var": "phase", "expr": {"enum": "Pending"}},
        {"var": "coherent", "expr": {"bool": False}},
        {"var": "obligation_visible", "expr": {"bool": False}},
        {"var": "permission_visible", "expr": {"bool": False}},
        {"var": "conflict_present", "expr": {"bool": False}},
        {"var": "incomplete_context", "expr": {"bool": False}},
        {"var": "fail_closed_mask", "expr": {"bool": False}},
        {"var": "receipt_bound", "expr": {"bool": False}},
    ]
    actions: list[dict[str, object]] = []
    for result, phase in zip(results, phases):
        conflict_present = bool(result.conflicts) or "multiple_incompatible_obligations" in result.unresolved
        incomplete_context = "incomplete_context" in result.unresolved or "unknown_predicate_applicability" in result.unresolved
        fail_closed_mask = result.resolution != "allow" and all(
            action in RESERVED_ACTIONS for action in result.allowed_actions
        )
        permission_visible = all(
            not status.obligation or status.permission
            for status in result.statuses
            if status.action not in RESERVED_ACTIONS
        )
        receipt = result.receipt
        try:
            receipt_digest = hashlib.sha256(result.receipt_json.encode("ascii")).hexdigest()
        except UnicodeEncodeError:
            receipt_digest = ""
        receipt_bound = (
            receipt_digest == result.receipt_sha256
            and receipt.get("policy_profile_sha256") == result.policy_profile_sha256
            and receipt.get("logic_semantics_sha256") == result.logic_semantics_sha256
            and receipt.get("receipt_schema") == RECEIPT_SCHEMA
            and receipt.get("input_sha256") == result.input_sha256
            and receipt.get("decision_id") == result.decision_id
        )
        safe_id = "".join(
            character if character.isalnum() or character == "_" else "_"
            for character in result.decision_id
        )[:40]
        id_digest = hashlib.sha256(result.decision_id.encode("ascii")).hexdigest()[:12]
        action_id = f"scenario_{safe_id}_{id_digest}"
        actions.append(
            {
                "id": action_id,
                "params": [],
                "guard": _esso_expr_eq({"var": "phase"}, {"enum": "Pending"}),
                "updates": [
                    {"var": "phase", "expr": {"enum": phase}},
                    {"var": "coherent", "expr": {"bool": result.resolution == "allow"}},
                    {"var": "obligation_visible", "expr": {"bool": bool(result.obligations)}},
                    {"var": "permission_visible", "expr": {"bool": permission_visible}},
                    {"var": "conflict_present", "expr": {"bool": conflict_present}},
                    {"var": "incomplete_context", "expr": {"bool": incomplete_context}},
                    {"var": "fail_closed_mask", "expr": {"bool": fail_closed_mask}},
                    {"var": "receipt_bound", "expr": {"bool": receipt_bound}},
                ],
                "effects": {
                    "receipt_sha256": {"enum": "rh_" + result.receipt_sha256},
                    "policy_profile_sha256": {"enum": "ph_" + result.policy_profile_sha256},
                    "logic_semantics_sha256": {"enum": "lh_" + result.logic_semantics_sha256},
                    "eligible_mask_sha256": {"enum": "em_" + mask_digest(result, result.eligible_action_mask)},
                    "obligatory_mask_sha256": {"enum": "om_" + mask_digest(result, result.obligatory_action_mask)},
                    "rule_reasons_sha256": {"enum": "rr_" + canonical_sha256(dict(result.rule_reasons))},
                },
            }
        )

    ir: dict[str, object] = {
        "ir_version": ESSO_IR_VERSION,
        "meta": {
            "model_id": "glassmind_deontic_kernel",
            "created_by": "glassmind",
            "seed": 0,
            "notes": "Finite scenario adapter; ESSO status is recorded separately and starts NOT_RUN.",
            "policy_profile_sha256": results[0].policy_profile_sha256,
            "logic_semantics_sha256": results[0].logic_semantics_sha256,
            "scenario_ids": list(scenario_ids),
        },
        "observables": {
            "state_vars": [item["id"] for item in state_vars],
            "effects": [
                "receipt_sha256",
                "policy_profile_sha256",
                "logic_semantics_sha256",
                "eligible_mask_sha256",
                "obligatory_mask_sha256",
                "rule_reasons_sha256",
            ],
        },
        "types": types,
        "state_vars": state_vars,
        "invariants": [
            {
                "id": "inv_coherent_obligation_implies_permission",
                "kind": "safety",
                "expr": _esso_expr_or(
                    _esso_expr_not({"var": "coherent"}),
                    _esso_expr_not({"var": "obligation_visible"}),
                    {"var": "permission_visible"},
                ),
            },
            {
                "id": "inv_conflict_fail_closed_mask",
                "kind": "safety",
                "expr": _esso_expr_or(_esso_expr_not({"var": "conflict_present"}), {"var": "fail_closed_mask"}),
            },
            {
                "id": "inv_incomplete_context_fail_closed_mask",
                "kind": "safety",
                "expr": _esso_expr_or(_esso_expr_not({"var": "incomplete_context"}), {"var": "fail_closed_mask"}),
            },
            {
                "id": "inv_receipt_binding",
                "kind": "safety",
                "expr": _esso_expr_or(_esso_expr_not({"var": "coherent"}), {"var": "receipt_bound"}),
            },
        ],
        "init": init,
        "actions": actions,
    }
    frozen_ir = _freeze_json(ir)
    model_sha256 = canonical_sha256(ir)
    status = ESSOVerificationStatus(
        model_sha256=model_sha256,
        tool="ESSO",
        commands=(),
        results=(),
        status="NOT_RUN",
        reason="ESSO guide, validation, and verify-multi evidence has not been attached.",
    )
    return ESSOAdapterProfile(frozen_ir, model_sha256, status, scenario_ids)


def bind_esso_verification_status(
    profile: ESSOAdapterProfile,
    status: ESSOVerificationStatus,
) -> ESSOAdapterProfile:
    """Attach evidence only when its model hash matches the compiled profile."""

    profile_hash = canonical_sha256(profile.ir)
    if profile_hash != profile.model_sha256:
        status = ESSOVerificationStatus(
            model_sha256=profile_hash,
            tool=status.tool,
            commands=status.commands,
            results=status.results,
            status="FAIL",
            reason="ESSO adapter profile hash does not match its IR",
        )
        return ESSOAdapterProfile(profile._ir, profile_hash, status, profile.scenario_ids)
    if status.model_sha256 != profile.model_sha256:
        status = ESSOVerificationStatus(
            model_sha256=profile.model_sha256,
            tool=status.tool,
            commands=status.commands,
            results=status.results,
            status="FAIL",
            reason="ESSO verification evidence is bound to a different model hash",
        )
    return ESSOAdapterProfile(profile._ir, profile.model_sha256, status, profile.scenario_ids)


def compile_esso_profile(scenarios: object) -> ESSOAdapterProfile:
    """Named adapter/profile entry point for callers that prefer profile terminology."""

    return compile_esso_ir(scenarios)


def to_esso_ir(scenarios: object) -> ESSOAdapterProfile:
    """Alias for the ESSO-compatible finite scenario adapter."""

    return compile_esso_ir(scenarios)


__all__ = [
    "ABSTAIN_ACTION",
    "ESCALATE_ACTION",
    "ESSO_IR_VERSION",
    "ESSO_VERIFICATION_STATUS_SCHEMA",
    "LIMITS",
    "LOGIC_PROFILE_ID",
    "LOGIC_SEMANTICS_HASH",
    "LOGIC_SEMANTICS_PROFILE",
    "MODALITIES",
    "NEUTRAL_EVIDENCE_COMPLETION_POLICY_PROFILE",
    "NEUTRAL_POLICY_PROFILE",
    "OBLIGATION",
    "PACKET_SCHEMA",
    "PACK_SCHEMA",
    "PERMISSION",
    "POLICY_PROFILE_SCHEMA",
    "POLICY_PROFILE_SHA256",
    "PROHIBITION",
    "RECEIPT_SCHEMA",
    "TRACE_ABSTAIN",
    "TRACE_ESCALATE",
    "TRACE_PENDING",
    "TRACE_QUARANTINE",
    "TRACE_RESOLVED",
    "TRACE_SCHEMA",
    "TRACE_TERMINAL_STATES",
    "ActionStatus",
    "Conflict",
    "DecisionResult",
    "DeonticKernelError",
    "ESSOAdapterProfile",
    "ESSOVerificationStatus",
    "PolicyProfile",
    "Predicate",
    "Rule",
    "RuleExamination",
    "SchemaError",
    "TraceCheckResult",
    "TraceStep",
    "ValidatedDecisionPack",
    "ValidatedPacket",
    "bind_esso_verification_status",
    "canonical_json_bytes",
    "canonical_sha256",
    "check_finite_trace",
    "check_trace",
    "compile_esso_ir",
    "compile_esso_profile",
    "compile_policy_profile",
    "evaluate",
    "evaluate_decision_pack",
    "evaluate_json",
    "evaluate_strict",
    "load_decision_pack",
    "parse_json",
    "to_esso_ir",
    "validate_decision_pack",
    "validate_packet",
]
