"""Deterministic, bounded Q planning over a canonical knowledge snapshot.

This module is deliberately a local compiler.  It reads an already canonical
JSON snapshot and never contacts a knowledge service.  A graph edge is a
navigation and evidence-discovery reference only.  It is never treated as
logical implication or as proof of the fact named by the edge.  Source-specific
adapters, such as :func:`adapt_wikidata_snapshot`, end at the canonical graph
boundary.  The planner itself accepts ordinary identifiers such as
``oewn-06175882-n`` and does not require QIDs or PIDs.

The finite state is

    (required decision, graph-node slot, evidence mask)

``StateRef.applicable`` means that the current real graph node is a valid
resolution target for that required decision.  It does not mean that the
decision is globally inapplicable.  Only an explicitly padded graph slot is
abstain-only.  A real non-target node remains navigable and may abstain, while
a real target needs its required evidence before resolve becomes available.

with exactly two evidence bits.  Bit 0 means that a forward discovery channel
has been traversed and bit 1 means that a reverse-browse discovery channel has
been traversed.  These are model-local evidence-channel labels, not claims
that a graph relation is true.  The deontic adapter constrains permissions,
obligations, and prohibitions for decisions; it does not prove facts.

The public and full profiles have the exact requested shapes:

    public: (256, 6144, 8), 50,331,648 float32 data bytes
    full:   (256, 65536, 8), 536,870,912 float32 data bytes

The fixture profile is intentionally small and is the profile used by the
tests.  Table generation uses ``numpy.lib.format.open_memmap`` and bounded
chunks, so the full Q table is never materialized in RAM.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any

import numpy as np

SCHEMA_VERSION = 1
CANONICAL_SNAPSHOT_SCHEMA = "glassmind-canonical-knowledge-v1"
MANIFEST_SCHEMA = "knowledge-q-table-manifest-v1"
RECEIPT_SCHEMA = "knowledge-q-reason-receipt-v1"
MAX_LAYERS = 256
MAX_DECISIONS = 16
MAX_NODE_SLOTS = 1024
MAX_STATES = 65536
MAX_ACTIONS = 8
NAVIGATION_ACTION_COUNT = 6
RESOLVE_ACTION_INDEX = 6
ABSTAIN_ACTION_INDEX = 7
ACTION_NAMES = tuple(
    f"navigate_{index}" for index in range(NAVIGATION_ACTION_COUNT)
) + (
    "resolve",
    "abstain_or_escalate",
)
ACTIONS = ACTION_NAMES
ACTION_INDEX = {name: index for index, name in enumerate(ACTION_NAMES)}
ALL_ACTION_MASK = (1 << MAX_ACTIONS) - 1
NAVIGATION_MASK = (1 << NAVIGATION_ACTION_COUNT) - 1
RESOLVE_MASK = 1 << RESOLVE_ACTION_INDEX
ABSTAIN_MASK = 1 << ABSTAIN_ACTION_INDEX

# Stable deontic status IDs emitted by the production evidence-completion
# adapter.  The older admissible/conflict/incomplete statuses remain available
# for fixture and external adapters.
DEONTIC_STATUS_ADMISSIBLE = "admissible"
DEONTIC_STATUS_CONFLICT = "conflict"
DEONTIC_STATUS_INCOMPLETE = "incomplete"
EVIDENCE_STATUS_PADDED = "padded_abstain_only"
EVIDENCE_STATUS_NON_APPLICABLE = "non_applicable_navigation"
EVIDENCE_STATUS_INCOMPLETE = "evidence_incomplete"
EVIDENCE_STATUS_COMPLETE = "evidence_complete"
DEONTIC_STATUS_VALUES = frozenset(
    {
        DEONTIC_STATUS_ADMISSIBLE,
        DEONTIC_STATUS_CONFLICT,
        DEONTIC_STATUS_INCOMPLETE,
        EVIDENCE_STATUS_PADDED,
        EVIDENCE_STATUS_NON_APPLICABLE,
        EVIDENCE_STATUS_INCOMPLETE,
        EVIDENCE_STATUS_COMPLETE,
    }
)
EVIDENCE_DEONTIC_PROVENANCE_SCHEMA = "evidence-completion-deontic-provenance-v1"

# Evidence is exactly two bits.  They describe discovery channels, not facts.
EVIDENCE_FORWARD_DISCOVERY = 0b01
EVIDENCE_REVERSE_DISCOVERY = 0b10
EVIDENCE_MASKS = (0b00, 0b01, 0b10, 0b11)
EVIDENCE_MASK_BITS = 2

# All table values remain finite, including unavailable actions.  The value is
# below every reward used by this bounded model and is not an infinity sentinel.
FORBIDDEN_VALUE = np.float32(-1_000_000.0)
ABSTAIN_REWARD = np.float32(0.0)
RESOLVE_REWARD = np.float32(1.0)
NAVIGATION_COST = np.float32(-0.01)
NEW_EVIDENCE_REWARD = np.float32(0.02)

HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")
IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,127}$")
MAX_JSON_BYTES = 16 * 1024 * 1024
MAX_TEXT_LENGTH = 4096
MAX_SNAPSHOT_NODES = 4096
MAX_SNAPSHOT_EDGES = 49152
MAX_MISSING_IDS = 4096
MAX_DECISION_RECORDS = MAX_DECISIONS
MAX_ALTERNATIVES = 16
MAX_LIST_ITEMS = 4096
MAX_ABS_UTILITY = 1000.0


class KnowledgeQTableError(ValueError):
    """Base class for deterministic validation and artifact errors."""


class SnapshotValidationError(KnowledgeQTableError):
    """The snapshot is absent, malformed, non-canonical, or inconsistent."""


class RequiredDecisionValidationError(KnowledgeQTableError):
    """A required-decision record violates its closed schema."""


class DeonticAdapterError(KnowledgeQTableError):
    """The permission adapter is absent, malformed, or unsound for this model."""


class TableValidationError(KnowledgeQTableError):
    """A Q-table file has a wrong header, shape, dtype, or non-finite value."""


def _is_identifier(value: Any) -> bool:
    return type(value) is str and IDENTIFIER_PATTERN.fullmatch(value) is not None


def _is_graph_identifier(value: Any) -> bool:
    """Recognize a bounded source-neutral node or relation identifier."""

    return _is_identifier(value)


def _bounded_text(value: Any, name: str, *, allow_empty: bool = False) -> str:
    if type(value) is not str:
        raise SnapshotValidationError(f"{name} must be a string")
    if len(value) > MAX_TEXT_LENGTH or (not allow_empty and not value):
        raise SnapshotValidationError(f"{name} is empty or exceeds the text bound")
    return value


def _bounded_int(value: Any, name: str, low: int, high: int) -> int:
    if type(value) is not int or not low <= value <= high:
        raise SnapshotValidationError(f"{name} must be an integer in [{low}, {high}]")
    return value


def _bounded_nonnegative_int(value: Any, name: str, high: int) -> int:
    return _bounded_int(value, name, 0, high)


def _require_fields(
    value: Any, required: set[str], optional: set[str], name: str
) -> dict[str, Any]:
    if type(value) is not dict:
        raise SnapshotValidationError(f"{name} must be a JSON object")
    keys = set(value)
    if not required <= keys or not keys <= required | optional:
        missing = sorted(required - keys)
        extra = sorted(keys - required - optional)
        raise SnapshotValidationError(
            f"{name} has missing fields {missing} or unknown fields {extra}"
        )
    return value


def _require_decision_fields(
    value: Any, required: set[str], optional: set[str], name: str
) -> dict[str, Any]:
    if type(value) is not dict:
        raise RequiredDecisionValidationError(f"{name} must be a JSON object")
    keys = set(value)
    if not required <= keys or not keys <= required | optional:
        missing = sorted(required - keys)
        extra = sorted(keys - required - optional)
        raise RequiredDecisionValidationError(
            f"{name} has missing fields {missing} or unknown fields {extra}"
        )
    return value


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SnapshotValidationError(f"duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> None:
    raise SnapshotValidationError(f"non-finite JSON constant is forbidden: {value}")


def _load_json_bytes(raw: bytes, name: str) -> Any:
    if type(raw) is not bytes:
        raise SnapshotValidationError(f"{name} must be read as bytes")
    if len(raw) > MAX_JSON_BYTES:
        raise SnapshotValidationError(f"{name} exceeds the bounded JSON size")
    try:
        return json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_json_keys,
            parse_constant=_reject_json_constant,
        )
    except UnicodeDecodeError as exc:
        raise SnapshotValidationError(f"{name} is not UTF-8") from exc
    except json.JSONDecodeError as exc:
        raise SnapshotValidationError(f"{name} is not valid JSON") from exc
    except (ValueError, RecursionError) as exc:
        raise SnapshotValidationError(
            f"{name} exceeds the parser's bounded representation"
        ) from exc


def canonical_json_bytes(value: Any) -> bytes:
    """Return the one canonical JSON encoding used for hashes and artifacts."""

    try:
        encoded = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise KnowledgeQTableError(
            "value cannot be represented as finite canonical JSON"
        ) from exc
    return (encoded + "\n").encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def file_sha256(path: os.PathLike[str] | str) -> str:
    """Hash a file in bounded chunks."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _validate_hash(value: Any, name: str) -> str:
    if type(value) is not str or HASH_PATTERN.fullmatch(value) is None:
        raise SnapshotValidationError(f"{name} must be a lowercase SHA-256 hex digest")
    return value


def _validate_string_list(
    value: Any, name: str, *, max_items: int = MAX_LIST_ITEMS
) -> tuple[str, ...]:
    if type(value) is not list or len(value) > max_items:
        raise SnapshotValidationError(f"{name} must be a bounded JSON list")
    result: list[str] = []
    for index, item in enumerate(value):
        result.append(_bounded_text(item, f"{name}[{index}]"))
    if len(set(result)) != len(result):
        raise SnapshotValidationError(f"{name} contains duplicate strings")
    return tuple(result)


def _validate_identifier_list(
    value: Any, name: str, *, max_items: int
) -> tuple[str, ...]:
    if type(value) is not list or len(value) > max_items:
        raise SnapshotValidationError(f"{name} must be a bounded JSON list")
    result: list[str] = []
    for index, item in enumerate(value):
        if not _is_graph_identifier(item):
            raise SnapshotValidationError(
                f"{name}[{index}] is not a valid bounded identifier"
            )
        result.append(item)
    if len(set(result)) != len(result):
        raise SnapshotValidationError(f"{name} contains duplicate identifiers")
    return tuple(result)


def _validate_bounded_json(value: Any, name: str, *, depth: int = 0) -> None:
    """Validate small provenance objects without giving their fields semantics."""

    if depth > 8:
        raise SnapshotValidationError(f"{name} exceeds the provenance nesting bound")
    if type(value) is dict:
        if len(value) > 128:
            raise SnapshotValidationError(f"{name} has too many provenance fields")
        for key, child in value.items():
            if type(key) is not str or not key or len(key) > 128:
                raise SnapshotValidationError(f"{name} has an invalid provenance key")
            _validate_bounded_json(child, f"{name}.{key}", depth=depth + 1)
        return
    if type(value) is list:
        if len(value) > 128:
            raise SnapshotValidationError(f"{name} has too many provenance entries")
        for index, child in enumerate(value):
            _validate_bounded_json(child, f"{name}[{index}]", depth=depth + 1)
        return
    if value is None or type(value) in (bool, int):
        return
    if type(value) is float:
        if not math.isfinite(value):
            raise SnapshotValidationError(f"{name} contains a non-finite number")
        return
    if type(value) is str and len(value) <= MAX_TEXT_LENGTH:
        return
    raise SnapshotValidationError(f"{name} contains an unsupported or oversized value")


def _validate_provenance(value: Any) -> None:
    provenance = _require_fields(
        value,
        {"source_name", "license", "canonical_graph_sha256", "nonclaims"},
        {
            "source_version",
            "retrieved_at",
            "source_url",
            "source_sha256",
            "adapter",
            "adapter_input_sha256",
        },
        "snapshot.provenance",
    )
    _bounded_text(provenance["source_name"], "snapshot.provenance.source_name")
    _bounded_text(provenance["license"], "snapshot.provenance.license")
    _validate_hash(
        provenance["canonical_graph_sha256"],
        "snapshot.provenance.canonical_graph_sha256",
    )
    _validate_string_list(
        provenance["nonclaims"], "snapshot.provenance.nonclaims", max_items=64
    )
    for field_name in ("source_version", "retrieved_at", "source_url", "adapter"):
        if field_name in provenance:
            _bounded_text(provenance[field_name], f"snapshot.provenance.{field_name}")
    for field_name in ("source_sha256", "adapter_input_sha256"):
        if field_name in provenance:
            _validate_hash(provenance[field_name], f"snapshot.provenance.{field_name}")


def _validate_node(value: Any, index: int) -> None:
    name = f"snapshot.graph.nodes[{index}]"
    node = _require_fields(
        value, {"id", "label", "description", "provenance"}, set(), name
    )
    if not _is_graph_identifier(node["id"]):
        raise SnapshotValidationError(f"{name}.id is invalid")
    if node["label"] is not None:
        _bounded_text(node["label"], f"{name}.label")
    if node["description"] is not None:
        _bounded_text(node["description"], f"{name}.description")
    if type(node["provenance"]) is not dict:
        raise SnapshotValidationError(f"{name}.provenance must be an object")
    _validate_bounded_json(node["provenance"], f"{name}.provenance")


def _validate_edge(value: Any, index: int, node_ids: set[str]) -> None:
    name = f"snapshot.graph.edges[{index}]"
    edge = _require_fields(
        value,
        {"source", "relation", "target", "source_direction"},
        {"evidence_bits", "provenance"},
        name,
    )
    if not _is_graph_identifier(edge["source"]) or edge["source"] not in node_ids:
        raise SnapshotValidationError(f"{name}.source is invalid or out of range")
    if not _is_graph_identifier(edge["relation"]):
        raise SnapshotValidationError(f"{name}.relation is invalid")
    if not _is_graph_identifier(edge["target"]) or edge["target"] not in node_ids:
        raise SnapshotValidationError(f"{name}.target is invalid or out of range")
    _bounded_text(edge["source_direction"], f"{name}.source_direction")
    if "evidence_bits" in edge:
        _bounded_int(edge["evidence_bits"], f"{name}.evidence_bits", 0, 3)
    if "provenance" in edge:
        if type(edge["provenance"]) is not dict:
            raise SnapshotValidationError(f"{name}.provenance must be an object")
        _validate_bounded_json(edge["provenance"], f"{name}.provenance")


def _validate_padding_policy(value: Any, name: str) -> None:
    policy = _require_fields(value, {"mode"}, set(), name)
    if policy["mode"] != "explicit_abstain_only":
        raise SnapshotValidationError(f"{name}.mode must be explicit_abstain_only")


def _validate_applicability(value: Any, name: str) -> dict[str, Any]:
    if type(value) is bool:
        return {"kind": "always" if value else "never"}
    applicability = _require_decision_fields(
        value,
        {"kind"},
        {"node_ids", "qids"},
        name,
    )
    kind = applicability["kind"]
    if kind in {"always", "never"}:
        if "node_ids" in applicability or "qids" in applicability:
            raise RequiredDecisionValidationError(
                f"{name} must not include node IDs for {kind}"
            )
        return {"kind": kind}
    identifier_fields = [
        field for field in ("node_ids", "qids") if field in applicability
    ]
    if kind != "node_ids" or len(identifier_fields) != 1:
        raise RequiredDecisionValidationError(
            f"{name}.kind must be always, never, or node_ids"
        )
    source_field = identifier_fields[0]
    try:
        node_ids = _validate_identifier_list(
            applicability[source_field],
            f"{name}.{source_field}",
            max_items=MAX_SNAPSHOT_NODES,
        )
    except SnapshotValidationError as exc:
        raise RequiredDecisionValidationError(str(exc)) from exc
    if not node_ids:
        raise RequiredDecisionValidationError(
            f"{name}.{source_field} must not be empty"
        )
    # ``qids`` is accepted only as an input compatibility spelling.  The
    # canonical decision representation is source-neutral.
    return {"kind": "node_ids", "node_ids": sorted(node_ids)}


def _validate_alternative(value: Any, name: str) -> dict[str, str]:
    alternative = _require_decision_fields(value, {"id", "label"}, set(), name)
    identifier = alternative["id"]
    if not _is_identifier(identifier):
        raise RequiredDecisionValidationError(f"{name}.id is invalid")
    label = _bounded_text(alternative["label"], f"{name}.label")
    return {"id": identifier, "label": label}


def _canonicalize_decision_record(value: Any, index: int) -> dict[str, Any]:
    name = f"required_decisions[{index}]"
    record = _require_decision_fields(
        value,
        {
            "decision_id",
            "applicability",
            "obligation_rule_ids",
            "goal",
            "required_evidence_bits",
            "review_triggers",
            "provenance_refs",
        },
        set(),
        name,
    )
    decision_id = record["decision_id"]
    if not _is_identifier(decision_id):
        raise RequiredDecisionValidationError(f"{name}.decision_id is invalid")
    applicability = _validate_applicability(
        record["applicability"], f"{name}.applicability"
    )
    try:
        obligations = _validate_string_list(
            record["obligation_rule_ids"], f"{name}.obligation_rule_ids", max_items=64
        )
    except SnapshotValidationError as exc:
        raise RequiredDecisionValidationError(str(exc)) from exc
    if not obligations:
        raise RequiredDecisionValidationError(
            f"{name}.obligation_rule_ids must not be empty"
        )
    goal = _require_decision_fields(
        record["goal"],
        {"resolution_alternatives", "abstain_or_escalate"},
        set(),
        f"{name}.goal",
    )
    alternatives = goal["resolution_alternatives"]
    if type(alternatives) is not list or not 1 <= len(alternatives) <= MAX_ALTERNATIVES:
        raise RequiredDecisionValidationError(
            f"{name}.goal.resolution_alternatives is outside its bound"
        )
    canonical_alternatives = [
        _validate_alternative(item, f"{name}.goal.resolution_alternatives[{alt_index}]")
        for alt_index, item in enumerate(alternatives)
    ]
    if len({item["id"] for item in canonical_alternatives}) != len(
        canonical_alternatives
    ):
        raise RequiredDecisionValidationError(
            f"{name}.goal.resolution_alternatives has duplicate IDs"
        )
    abstain = _validate_alternative(
        goal["abstain_or_escalate"], f"{name}.goal.abstain_or_escalate"
    )
    if (
        "abstain" not in abstain["id"].lower()
        and "escalat" not in abstain["id"].lower()
    ):
        raise RequiredDecisionValidationError(
            f"{name}.goal.abstain_or_escalate.id must name abstention or escalation"
        )
    try:
        evidence_bits = _bounded_int(
            record["required_evidence_bits"],
            f"{name}.required_evidence_bits",
            0,
            3,
        )
    except SnapshotValidationError as exc:
        raise RequiredDecisionValidationError(str(exc)) from exc
    try:
        review_triggers = _validate_string_list(
            record["review_triggers"], f"{name}.review_triggers", max_items=64
        )
        provenance_refs = _validate_string_list(
            record["provenance_refs"], f"{name}.provenance_refs", max_items=64
        )
    except SnapshotValidationError as exc:
        raise RequiredDecisionValidationError(str(exc)) from exc
    if not provenance_refs:
        raise RequiredDecisionValidationError(
            f"{name}.provenance_refs must not be empty"
        )
    return {
        "decision_id": decision_id,
        "applicability": applicability,
        "obligation_rule_ids": sorted(obligations),
        "goal": {
            "resolution_alternatives": sorted(
                canonical_alternatives, key=lambda item: item["id"]
            ),
            "abstain_or_escalate": abstain,
        },
        "required_evidence_bits": evidence_bits,
        "review_triggers": sorted(review_triggers),
        "provenance_refs": sorted(provenance_refs),
    }


def canonicalize_required_decisions(
    records: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, Any], ...]:
    """Validate and return required-decision records in stable ID order."""

    if (
        type(records) not in (list, tuple)
        or not 1 <= len(records) <= MAX_DECISION_RECORDS
    ):
        raise RequiredDecisionValidationError(
            "required decisions must be a bounded non-empty list"
        )
    normalized = tuple(
        _canonicalize_decision_record(item, index) for index, item in enumerate(records)
    )
    identifiers = [item["decision_id"] for item in normalized]
    if len(set(identifiers)) != len(identifiers):
        raise RequiredDecisionValidationError("required decision IDs must be unique")
    return tuple(sorted(normalized, key=lambda item: item["decision_id"]))


def validate_required_decisions(records: Sequence[Mapping[str, Any]]) -> None:
    canonicalize_required_decisions(records)


def load_required_decisions(path: os.PathLike[str] | str) -> tuple[dict[str, Any], ...]:
    raw = Path(path).read_bytes()
    value = _load_json_bytes(raw, "required-decisions JSON")
    if type(value) is dict:
        wrapper = _require_decision_fields(
            value, {"required_decisions"}, set(), "required-decisions wrapper"
        )
        value = wrapper["required_decisions"]
    return canonicalize_required_decisions(value)


def _canonical_graph(
    nodes: Sequence[Mapping[str, Any]], edges: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    """Defensively copy and order the source-neutral graph payload."""

    rebuilt_nodes = [
        json.loads(canonical_json_bytes(node).decode("utf-8"))
        for node in sorted(nodes, key=lambda item: item["id"])
    ]
    rebuilt_edges = [
        json.loads(canonical_json_bytes(edge).decode("utf-8"))
        for edge in sorted(
            edges,
            key=lambda item: (
                item["source"],
                item["relation"],
                item["target"],
                item["source_direction"],
                item.get("evidence_bits", -1),
            ),
        )
    ]
    return {"nodes": rebuilt_nodes, "edges": rebuilt_edges}


def _validate_snapshot_shape(snapshot: Any) -> None:
    root = _require_fields(
        snapshot,
        {"schema", "provenance", "counts", "graph", "missing_ids", "truncated"},
        {"required_decisions", "slot_policy"},
        "snapshot",
    )
    if root["schema"] != CANONICAL_SNAPSHOT_SCHEMA:
        raise SnapshotValidationError("unsupported canonical snapshot schema")
    _validate_provenance(root["provenance"])
    counts = _require_fields(
        root["counts"], {"nodes", "edges"}, set(), "snapshot.counts"
    )
    graph = _require_fields(
        root["graph"],
        {"nodes", "edges"},
        {"padding_policy"},
        "snapshot.graph",
    )
    nodes = graph["nodes"]
    edges = graph["edges"]
    if type(nodes) is not list or not 1 <= len(nodes) <= MAX_SNAPSHOT_NODES:
        raise SnapshotValidationError("snapshot.graph.nodes is outside its bound")
    if type(edges) is not list or len(edges) > MAX_SNAPSHOT_EDGES:
        raise SnapshotValidationError("snapshot.graph.edges is outside its bound")
    node_ids: list[str] = []
    for index, node in enumerate(nodes):
        _validate_node(node, index)
        node_ids.append(node["id"])
    if len(set(node_ids)) != len(node_ids):
        raise SnapshotValidationError("snapshot graph contains duplicate node IDs")
    node_id_set = set(node_ids)
    edge_keys: list[tuple[str, str, str, str]] = []
    for index, edge in enumerate(edges):
        _validate_edge(edge, index, node_id_set)
        edge_keys.append(
            (edge["source"], edge["relation"], edge["target"], edge["source_direction"])
        )
    if len(set(edge_keys)) != len(edge_keys):
        raise SnapshotValidationError(
            "snapshot graph contains duplicate directional edges"
        )
    _bounded_int(counts["nodes"], "snapshot.counts.nodes", 1, MAX_SNAPSHOT_NODES)
    _bounded_int(counts["edges"], "snapshot.counts.edges", 0, MAX_SNAPSHOT_EDGES)
    if counts["nodes"] != len(nodes) or counts["edges"] != len(edges):
        raise SnapshotValidationError("snapshot counts do not match graph lengths")
    missing = _validate_identifier_list(
        root["missing_ids"], "snapshot.missing_ids", max_items=MAX_MISSING_IDS
    )
    if set(missing) & node_id_set:
        raise SnapshotValidationError("snapshot.missing_ids overlaps graph nodes")
    if type(root["truncated"]) is not bool:
        raise SnapshotValidationError("snapshot.truncated must be a boolean")
    if "required_decisions" in root:
        canonicalize_required_decisions(root["required_decisions"])
    if "slot_policy" in root:
        _validate_padding_policy(root["slot_policy"], "snapshot.slot_policy")
    if "padding_policy" in graph:
        _validate_padding_policy(
            graph["padding_policy"], "snapshot.graph.padding_policy"
        )
    expected_graph_hash = _sha256_bytes(
        canonical_json_bytes(_canonical_graph(nodes, edges))
    )
    if root["provenance"]["canonical_graph_sha256"] != expected_graph_hash:
        raise SnapshotValidationError(
            "snapshot provenance canonical_graph_sha256 does not match the graph"
        )


def adapt_wikidata_snapshot(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    """Map a bounded legacy Wikidata QID/PID snapshot to the neutral schema.

    This adapter preserves direction explicitly.  It does not reinterpret a
    Wikidata claim as proof, implication, permission, or obligation.
    """

    if type(snapshot) is not dict:
        raise SnapshotValidationError("Wikidata snapshot must be an object")
    graph = snapshot.get("graph")
    if (
        type(graph) is not dict
        or type(graph.get("nodes")) is not list
        or type(graph.get("edges")) is not list
    ):
        raise SnapshotValidationError(
            "Wikidata snapshot is missing graph nodes or edges"
        )
    nodes: list[dict[str, Any]] = []
    for index, node in enumerate(graph["nodes"]):
        if type(node) is not dict or not _is_graph_identifier(node.get("qid")):
            raise SnapshotValidationError(f"Wikidata node {index} has an invalid qid")
        label = node.get("label")
        description = node.get("description")
        if label is not None:
            _bounded_text(label, f"Wikidata node {index}.label")
        if description is not None:
            _bounded_text(description, f"Wikidata node {index}.description")
        node_provenance: dict[str, Any] = {"adapter": "wikidata-qid-pid-v1"}
        if "revision" in node:
            _validate_bounded_json(node["revision"], f"Wikidata node {index}.revision")
            node_provenance["revision"] = node["revision"]
        nodes.append(
            {
                "id": node["qid"],
                "label": label,
                "description": description,
                "provenance": node_provenance,
            }
        )
    edges: list[dict[str, Any]] = []
    for index, edge in enumerate(graph["edges"]):
        if type(edge) is not dict:
            raise SnapshotValidationError(f"Wikidata edge {index} must be an object")
        for field_name in ("source", "pid", "target"):
            if not _is_graph_identifier(edge.get(field_name)):
                raise SnapshotValidationError(
                    f"Wikidata edge {index}.{field_name} is invalid"
                )
        mapped: dict[str, Any] = {
            "source": edge["source"],
            "relation": edge["pid"],
            "target": edge["target"],
            "source_direction": "wikidata_claim_source_to_target",
            "provenance": {"adapter": "wikidata-qid-pid-v1"},
        }
        if "evidence_bits" in edge:
            mapped["evidence_bits"] = edge["evidence_bits"]
        edges.append(mapped)
    canonical_graph = _canonical_graph(nodes, edges)
    old_provenance = (
        snapshot.get("provenance") if type(snapshot.get("provenance")) is dict else {}
    )
    provenance: dict[str, Any] = {
        "source_name": "Wikidata",
        "license": old_provenance.get("license", "CC0-1.0"),
        "canonical_graph_sha256": _sha256_bytes(canonical_json_bytes(canonical_graph)),
        "nonclaims": list(
            old_provenance.get(
                "nonclaims",
                [
                    "Wikidata claims are discovery references, not formal proofs or normative rules"
                ],
            )
        ),
        "adapter": "wikidata-qid-pid-v1",
        "adapter_input_sha256": _sha256_bytes(canonical_json_bytes(snapshot)),
    }
    if type(old_provenance.get("endpoint")) is str:
        provenance["source_url"] = old_provenance["endpoint"]
    if type(old_provenance.get("retrieved_at")) is str:
        provenance["retrieved_at"] = old_provenance["retrieved_at"]
    canonical: dict[str, Any] = {
        "schema": CANONICAL_SNAPSHOT_SCHEMA,
        "provenance": provenance,
        "counts": {
            "nodes": len(canonical_graph["nodes"]),
            "edges": len(canonical_graph["edges"]),
        },
        "graph": canonical_graph,
        "missing_ids": sorted(snapshot.get("missing_qids", [])),
        "truncated": snapshot.get("truncated", False),
    }
    for field_name in ("required_decisions", "slot_policy"):
        if field_name in snapshot:
            canonical[field_name] = snapshot[field_name]
    return canonicalize_snapshot(canonical)


def canonicalize_snapshot(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    """Return a defensively rebuilt, source-neutral snapshot."""

    if type(snapshot) is dict and snapshot.get("schema") != CANONICAL_SNAPSHOT_SCHEMA:
        if "snapshot_version" in snapshot:
            return adapt_wikidata_snapshot(snapshot)
        raise SnapshotValidationError(
            "snapshot is neither canonical nor a recognized Wikidata input"
        )
    _validate_snapshot_shape(snapshot)
    graph_payload = _canonical_graph(
        snapshot["graph"]["nodes"], snapshot["graph"]["edges"]
    )
    graph: dict[str, Any] = dict(graph_payload)
    if "padding_policy" in snapshot["graph"]:
        graph["padding_policy"] = dict(snapshot["graph"]["padding_policy"])
    root: dict[str, Any] = {
        "schema": CANONICAL_SNAPSHOT_SCHEMA,
        "provenance": json.loads(
            canonical_json_bytes(snapshot["provenance"]).decode("utf-8")
        ),
        "counts": {
            "nodes": len(graph_payload["nodes"]),
            "edges": len(graph_payload["edges"]),
        },
        "graph": graph,
        "missing_ids": sorted(snapshot["missing_ids"]),
        "truncated": snapshot["truncated"],
    }
    root["provenance"]["canonical_graph_sha256"] = _sha256_bytes(
        canonical_json_bytes(graph_payload)
    )
    if "slot_policy" in snapshot:
        root["slot_policy"] = dict(snapshot["slot_policy"])
    if "required_decisions" in snapshot:
        root["required_decisions"] = list(
            canonicalize_required_decisions(snapshot["required_decisions"])
        )
    return root


def validate_snapshot(snapshot: Mapping[str, Any]) -> None:
    """Require stable ordering and hashes for an already neutral snapshot."""

    _validate_snapshot_shape(snapshot)
    if canonicalize_snapshot(snapshot) != snapshot:
        raise SnapshotValidationError(
            "snapshot is valid but not in canonical list order"
        )


def load_snapshot(path: os.PathLike[str] | str) -> dict[str, Any]:
    raw = Path(path).read_bytes()
    value = _load_json_bytes(raw, "snapshot JSON")
    if type(value) is dict and value.get("schema") == CANONICAL_SNAPSHOT_SCHEMA:
        validate_snapshot(value)
        if canonical_json_bytes(value) != raw:
            raise SnapshotValidationError(
                "snapshot JSON is not in canonical byte encoding"
            )
        return value
    # Legacy Wikidata snapshots cross a named adapter boundary.  Callers that
    # need byte-identical neutral artifacts should persist the returned value.
    return adapt_wikidata_snapshot(value)


@dataclass(frozen=True)
class PlannerConfig:
    """Finite dimensions and numeric policy for one table artifact."""

    layers: int
    decisions: int
    node_slots: int
    gamma: float = 0.99
    chunk_size: int = 4096
    allow_explicit_padding: bool = False
    profile: str = "fixture"

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if type(self.layers) is not int or not 1 <= self.layers <= MAX_LAYERS:
            raise KnowledgeQTableError(
                f"layers must be an integer in [1, {MAX_LAYERS}]"
            )
        if type(self.decisions) is not int or not 1 <= self.decisions <= MAX_DECISIONS:
            raise KnowledgeQTableError(
                f"decisions must be an integer in [1, {MAX_DECISIONS}]"
            )
        if (
            type(self.node_slots) is not int
            or not 1 <= self.node_slots <= MAX_NODE_SLOTS
        ):
            raise KnowledgeQTableError(
                f"node_slots must be an integer in [1, {MAX_NODE_SLOTS}]"
            )
        if self.decisions * self.node_slots * len(EVIDENCE_MASKS) > MAX_STATES:
            raise KnowledgeQTableError(
                "state factorization exceeds the bounded state limit"
            )
        if (
            type(self.gamma) not in (int, float)
            or isinstance(self.gamma, bool)
            or not math.isfinite(float(self.gamma))
        ):
            raise KnowledgeQTableError("gamma must be a finite number")
        if not 0.0 <= float(self.gamma) < 1.0:
            raise KnowledgeQTableError("gamma must satisfy 0 <= gamma < 1")
        if type(self.chunk_size) is not int or not 1 <= self.chunk_size <= MAX_STATES:
            raise KnowledgeQTableError("chunk_size is outside its bounded range")
        if type(self.allow_explicit_padding) is not bool:
            raise KnowledgeQTableError("allow_explicit_padding must be a boolean")
        if type(self.profile) is not str or not self.profile:
            raise KnowledgeQTableError("profile must be a non-empty string")
        if self.profile == "public" and (
            self.layers,
            self.decisions,
            self.node_slots,
        ) != (256, 6, 256):
            raise KnowledgeQTableError("public profile dimensions are fixed")
        if self.profile == "full" and (
            self.layers,
            self.decisions,
            self.node_slots,
        ) != (256, 16, 1024):
            raise KnowledgeQTableError("full profile dimensions are fixed")

    @property
    def state_count(self) -> int:
        return self.decisions * self.node_slots * len(EVIDENCE_MASKS)

    @property
    def shape(self) -> tuple[int, int, int]:
        return (self.layers, self.state_count, MAX_ACTIONS)

    @property
    def raw_data_bytes(self) -> int:
        return self.layers * self.state_count * MAX_ACTIONS * np.dtype("<f4").itemsize


Config = PlannerConfig

PROFILES: dict[str, PlannerConfig] = {
    "public": PlannerConfig(
        layers=256,
        decisions=6,
        node_slots=256,
        chunk_size=4096,
        allow_explicit_padding=True,
        profile="public",
    ),
    "full": PlannerConfig(
        layers=256,
        decisions=16,
        node_slots=1024,
        chunk_size=8192,
        allow_explicit_padding=True,
        profile="full",
    ),
}


@dataclass(frozen=True)
class UtilityModel:
    """Explicit outcome model compiled separately from normative permissions."""

    version: str = "bounded-required-decision-utility-v1"
    navigation_cost: float = float(NAVIGATION_COST)
    new_evidence_reward: float = float(NEW_EVIDENCE_REWARD)
    resolve_reward: float = float(RESOLVE_REWARD)
    abstain_reward: float = float(ABSTAIN_REWARD)

    def __post_init__(self) -> None:
        if not _is_identifier(self.version):
            raise KnowledgeQTableError("utility version must be a bounded identifier")
        for field_name in (
            "navigation_cost",
            "new_evidence_reward",
            "resolve_reward",
            "abstain_reward",
        ):
            value = getattr(self, field_name)
            if (
                type(value) not in (int, float)
                or isinstance(value, bool)
                or not math.isfinite(float(value))
            ):
                raise KnowledgeQTableError(f"utility {field_name} must be finite")
            rounded = np.float32(value)
            if not np.isfinite(rounded) or abs(float(rounded)) > MAX_ABS_UTILITY:
                raise KnowledgeQTableError(
                    f"utility {field_name} is outside the finite float32 policy"
                )

    def to_record(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "navigation_cost": float(np.float32(self.navigation_cost)),
            "new_evidence_reward": float(np.float32(self.new_evidence_reward)),
            "resolve_reward": float(np.float32(self.resolve_reward)),
            "abstain_reward": float(np.float32(self.abstain_reward)),
        }


DEFAULT_UTILITY_MODEL = UtilityModel()


def fixture_config(
    *,
    layers: int = 8,
    decisions: int = 2,
    node_slots: int = 4,
    chunk_size: int = 8,
    allow_explicit_padding: bool = True,
) -> PlannerConfig:
    """Return a bounded fixture configuration for tests and local examples."""

    return PlannerConfig(
        layers=layers,
        decisions=decisions,
        node_slots=node_slots,
        chunk_size=chunk_size,
        allow_explicit_padding=allow_explicit_padding,
        profile="fixture",
    )


@dataclass(frozen=True)
class RequiredDecision:
    decision_id: str
    applicability: Mapping[str, Any]
    obligation_rule_ids: tuple[str, ...]
    resolution_alternatives: tuple[Mapping[str, str], ...]
    abstain_or_escalate: Mapping[str, str]
    required_evidence_bits: int
    review_triggers: tuple[str, ...]
    provenance_refs: tuple[str, ...]

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> RequiredDecision:
        applicability = dict(record["applicability"])
        alternatives = tuple(
            dict(item) for item in record["goal"]["resolution_alternatives"]
        )
        return cls(
            decision_id=record["decision_id"],
            applicability=MappingProxyType(applicability),
            obligation_rule_ids=tuple(record["obligation_rule_ids"]),
            resolution_alternatives=tuple(
                MappingProxyType(item) for item in alternatives
            ),
            abstain_or_escalate=MappingProxyType(
                dict(record["goal"]["abstain_or_escalate"])
            ),
            required_evidence_bits=record["required_evidence_bits"],
            review_triggers=tuple(record["review_triggers"]),
            provenance_refs=tuple(record["provenance_refs"]),
        )

    def to_record(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "applicability": dict(self.applicability),
            "obligation_rule_ids": list(self.obligation_rule_ids),
            "goal": {
                "resolution_alternatives": [
                    dict(item) for item in self.resolution_alternatives
                ],
                "abstain_or_escalate": dict(self.abstain_or_escalate),
            },
            "required_evidence_bits": self.required_evidence_bits,
            "review_triggers": list(self.review_triggers),
            "provenance_refs": list(self.provenance_refs),
        }

    def is_applicable(self, node_id: str | None) -> bool:
        kind = self.applicability["kind"]
        if kind == "always":
            return True
        if kind == "never" or node_id is None:
            return False
        return node_id in self.applicability["node_ids"]


@dataclass(frozen=True)
class StateRef:
    """A bounded planner state with current-node applicability semantics."""

    decision_index: int
    decision_id: str
    node_slot: int
    node_id: str | None
    evidence_mask: int
    required_evidence_bits: int
    applicable: bool
    padded: bool


def _normalize_rule_ids(value: Any) -> tuple[tuple[str, ...], ...]:
    if value is None:
        return ((),) * MAX_ACTIONS
    if type(value) is dict:
        unknown = set(value) - set(ACTION_NAMES)
        if unknown:
            raise DeonticAdapterError(
                f"unknown deontic rule action names: {sorted(unknown)}"
            )
        rows: list[Any] = [value.get(action, []) for action in ACTION_NAMES]
    elif type(value) in (list, tuple):
        if len(value) != MAX_ACTIONS:
            raise DeonticAdapterError(
                "deontic rule_ids sequence must have exactly eight entries"
            )
        rows = list(value)
    else:
        raise DeonticAdapterError(
            "deontic rule_ids must be an action mapping or eight-entry sequence"
        )
    result: list[tuple[str, ...]] = []
    for index, row in enumerate(rows):
        if type(row) not in (list, tuple) or len(row) > 64:
            raise DeonticAdapterError(f"deontic rule_ids[{index}] is malformed")
        identifiers = []
        for item in row:
            if not _is_identifier(item):
                raise DeonticAdapterError(
                    f"deontic rule_ids[{index}] contains an invalid ID"
                )
            identifiers.append(item)
        if len(set(identifiers)) != len(identifiers):
            raise DeonticAdapterError(f"deontic rule_ids[{index}] contains duplicates")
        result.append(tuple(sorted(identifiers)))
    return tuple(result)


def _normalize_action_mask(value: Any, name: str) -> int:
    if type(value) is int:
        if not 0 <= value <= ALL_ACTION_MASK:
            raise DeonticAdapterError(f"{name} is outside the eight-action range")
        return value
    if type(value) is dict:
        if set(value) != set(ACTION_NAMES) or any(
            type(item) is not bool for item in value.values()
        ):
            raise DeonticAdapterError(
                f"{name} mapping must classify all eight planner actions"
            )
        return sum(
            (1 << index) for index, action in enumerate(ACTION_NAMES) if value[action]
        )
    if type(value) in (list, tuple):
        if len(value) != MAX_ACTIONS or any(type(item) is not bool for item in value):
            raise DeonticAdapterError(f"{name} sequence must contain eight booleans")
        return sum((1 << index) for index, item in enumerate(value) if item)
    raise DeonticAdapterError(
        f"{name} must be an integer, mapping, or eight-boolean sequence"
    )


def _adapter_provenance_hash(value: Any, name: str) -> str:
    if type(value) is not str or HASH_PATTERN.fullmatch(value) is None:
        raise DeonticAdapterError(f"{name} must be a lowercase SHA-256 hex digest")
    return value


def _normalize_esso_evidence_hashes(value: Any) -> dict[str, str]:
    if type(value) is dict:
        entries = list(value.items())
    elif type(value) in (list, tuple):
        entries = []
        if len(value) > 256:
            raise DeonticAdapterError("too many ESSO evidence hashes")
        for index, entry in enumerate(value):
            if type(entry) not in (list, tuple) or len(entry) != 2:
                raise DeonticAdapterError(
                    f"esso_evidence_hashes[{index}] must be a name/hash pair"
                )
            entries.append((entry[0], entry[1]))
    else:
        raise DeonticAdapterError(
            "esso_evidence_hashes must be a mapping or name/hash sequence"
        )
    if len(entries) > 256:
        raise DeonticAdapterError("too many ESSO evidence hashes")
    result: dict[str, str] = {}
    for index, (name, digest) in enumerate(entries):
        if not _is_identifier(name):
            raise DeonticAdapterError(
                f"esso_evidence_hashes[{index}] has an invalid evidence ID"
            )
        if name in result:
            raise DeonticAdapterError(
                f"esso_evidence_hashes contains duplicate evidence ID {name!r}"
            )
        result[name] = _adapter_provenance_hash(digest, f"esso_evidence_hashes[{name}]")
    return {name: result[name] for name in sorted(result)}


def _canonical_adapter_provenance(value: Any) -> dict[str, Any]:
    """Validate and canonicalize an adapter's declared semantic provenance."""

    if type(value) is not dict:
        raise DeonticAdapterError("deontic adapter provenance must be a JSON object")
    required = {
        "schema",
        "logic_semantics",
        "profile",
        "esso_evidence_hashes",
    }
    if value.get("schema") == EVIDENCE_DEONTIC_PROVENANCE_SCHEMA:
        required |= {"logic_semantics_sha256", "profile_sha256"}
    optional = {
        "logic_semantics_sha256",
        "profile_sha256",
        "adapter_class",
        "forbidden_actions",
    }
    keys = set(value)
    if not required <= keys or not keys <= required | optional:
        raise DeonticAdapterError(
            "deontic adapter provenance has missing or unknown fields"
        )
    if not _is_identifier(value["schema"]):
        raise DeonticAdapterError("deontic adapter provenance schema is invalid")
    if not _is_identifier(value["logic_semantics"]):
        raise DeonticAdapterError(
            "deontic adapter provenance logic_semantics is invalid"
        )
    if not _is_identifier(value["profile"]):
        raise DeonticAdapterError("deontic adapter provenance profile is invalid")
    esso_hashes = _normalize_esso_evidence_hashes(value["esso_evidence_hashes"])
    logic_hash = value.get("logic_semantics_sha256")
    if logic_hash is None:
        logic_hash = _sha256_bytes(value["logic_semantics"].encode("utf-8"))
    else:
        logic_hash = _adapter_provenance_hash(logic_hash, "logic_semantics_sha256")
    profile_hash = value.get("profile_sha256")
    if profile_hash is None:
        profile_hash = _sha256_bytes(value["profile"].encode("utf-8"))
    else:
        profile_hash = _adapter_provenance_hash(profile_hash, "profile_sha256")
    result: dict[str, Any] = {
        "schema": value["schema"],
        "logic_semantics": value["logic_semantics"],
        "logic_semantics_sha256": logic_hash,
        "profile": value["profile"],
        "profile_sha256": profile_hash,
        "esso_evidence_hashes": esso_hashes,
    }
    if "adapter_class" in value:
        if not _is_identifier(value["adapter_class"]):
            raise DeonticAdapterError(
                "deontic adapter provenance adapter_class is invalid"
            )
        result["adapter_class"] = value["adapter_class"]
    if "forbidden_actions" in value:
        actions = value["forbidden_actions"]
        if type(actions) not in (list, tuple) or len(actions) > MAX_ACTIONS:
            raise DeonticAdapterError(
                "deontic adapter provenance forbidden_actions is malformed"
            )
        normalized_actions = tuple(actions)
        if any(action not in ACTION_INDEX for action in normalized_actions):
            raise DeonticAdapterError(
                "deontic adapter provenance has an unknown forbidden action"
            )
        if len(set(normalized_actions)) != len(normalized_actions):
            raise DeonticAdapterError(
                "deontic adapter provenance has duplicate forbidden actions"
            )
        result["forbidden_actions"] = sorted(normalized_actions)
    return result


@dataclass(frozen=True)
class DeonticConstraints:
    """Closed per-state action permissions returned by the deontic adapter."""

    permitted_mask: int
    forbidden_mask: int
    rule_ids: tuple[tuple[str, ...], ...] = field(
        default_factory=lambda: ((),) * MAX_ACTIONS
    )
    status: str = "admissible"
    obligatory_mask: int = 0

    def __post_init__(self) -> None:
        if (
            type(self.permitted_mask) is not int
            or not 0 <= self.permitted_mask <= ALL_ACTION_MASK
        ):
            raise DeonticAdapterError(
                "permitted_mask is outside the eight-action range"
            )
        if (
            type(self.forbidden_mask) is not int
            or not 0 <= self.forbidden_mask <= ALL_ACTION_MASK
        ):
            raise DeonticAdapterError(
                "forbidden_mask is outside the eight-action range"
            )
        if self.permitted_mask & self.forbidden_mask:
            raise DeonticAdapterError("permitted and forbidden masks overlap")
        if (self.permitted_mask | self.forbidden_mask) != ALL_ACTION_MASK:
            raise DeonticAdapterError("deontic masks must classify every action")
        if self.status not in DEONTIC_STATUS_VALUES:
            raise DeonticAdapterError("deontic status is not a known stable status ID")
        if (
            type(self.obligatory_mask) is not int
            or not 0 <= self.obligatory_mask <= ALL_ACTION_MASK
        ):
            raise DeonticAdapterError(
                "obligatory_mask is outside the eight-action range"
            )
        if self.obligatory_mask & self.forbidden_mask:
            raise DeonticAdapterError("an obligatory action cannot remain forbidden")
        if self.obligatory_mask and self.allowed_mask != self.obligatory_mask:
            raise DeonticAdapterError(
                "obligatory actions must take precedence in the final permitted mask"
            )
        normalized = _normalize_rule_ids(self.rule_ids)
        object.__setattr__(self, "rule_ids", normalized)
        if self.status in {DEONTIC_STATUS_CONFLICT, DEONTIC_STATUS_INCOMPLETE}:
            if self.allowed_mask != ABSTAIN_MASK:
                raise DeonticAdapterError(
                    "conflict or incomplete deontic output must allow only abstain_or_escalate"
                )
            if not normalized[ABSTAIN_ACTION_INDEX]:
                raise DeonticAdapterError(
                    "conflict or incomplete deontic output must give an abstention reason ID"
                )
        elif self.status == EVIDENCE_STATUS_PADDED:
            if self.allowed_mask != ABSTAIN_MASK or self.obligatory_mask:
                raise DeonticAdapterError("padded evidence states must be abstain-only")
            if not normalized[ABSTAIN_ACTION_INDEX]:
                raise DeonticAdapterError(
                    "padded evidence states require an abstention reason ID"
                )
        elif self.status == EVIDENCE_STATUS_NON_APPLICABLE:
            if self.allowed_mask != NAVIGATION_MASK | ABSTAIN_MASK:
                raise DeonticAdapterError(
                    "real non-target evidence states must allow navigation and abstention"
                )
            if self.obligatory_mask or not normalized[ABSTAIN_ACTION_INDEX]:
                raise DeonticAdapterError(
                    "real non-target evidence states cannot make resolve obligatory"
                )
        elif self.status == EVIDENCE_STATUS_INCOMPLETE:
            if self.allowed_mask != NAVIGATION_MASK | ABSTAIN_MASK:
                raise DeonticAdapterError(
                    "incomplete evidence states must allow navigation and abstention"
                )
            if self.obligatory_mask or not normalized[ABSTAIN_ACTION_INDEX]:
                raise DeonticAdapterError(
                    "incomplete evidence states cannot make resolve obligatory"
                )
        elif self.status == EVIDENCE_STATUS_COMPLETE:
            if (
                self.allowed_mask != RESOLVE_MASK
                or self.obligatory_mask != RESOLVE_MASK
                or not normalized[RESOLVE_ACTION_INDEX]
            ):
                raise DeonticAdapterError(
                    "complete evidence states must make resolve obligatory and exclusive"
                )

    @classmethod
    def from_value(cls, value: Any) -> DeonticConstraints:
        if isinstance(value, cls):
            return value
        if type(value) is not dict:
            raise DeonticAdapterError(
                "deontic adapter must return DeonticConstraints or a JSON-like mapping"
            )
        keys = set(value)
        allowed_fields = {
            "permitted_mask",
            "forbidden_mask",
            "action_mask",
            "rule_ids",
            "reason_ids",
            "status",
            "obligatory_mask",
            "obligatory_action_mask",
        }
        if not keys <= allowed_fields:
            raise DeonticAdapterError("malformed deontic constraint fields")
        if "rule_ids" in value and "reason_ids" in value:
            raise DeonticAdapterError("provide rule_ids or reason_ids, not both")
        if "action_mask" in value:
            if "permitted_mask" in value or "forbidden_mask" in value:
                raise DeonticAdapterError(
                    "action_mask cannot be combined with integer masks"
                )
            permitted_mask = _normalize_action_mask(value["action_mask"], "action_mask")
            forbidden_mask = ALL_ACTION_MASK ^ permitted_mask
        else:
            if not {"permitted_mask", "forbidden_mask"} <= keys:
                raise DeonticAdapterError(
                    "deontic output must provide action_mask or both integer masks"
                )
            permitted_mask = value["permitted_mask"]
            forbidden_mask = value["forbidden_mask"]
        if "obligatory_mask" in value and "obligatory_action_mask" in value:
            raise DeonticAdapterError(
                "provide obligatory_mask or obligatory_action_mask, not both"
            )
        obligatory_value = value.get(
            "obligatory_mask", value.get("obligatory_action_mask", 0)
        )
        obligatory_mask = _normalize_action_mask(
            obligatory_value, "obligatory_action_mask"
        )
        status = value.get("status", "admissible")
        if status == "admissible" and obligatory_mask:
            if (
                obligatory_mask & forbidden_mask
                or obligatory_mask & permitted_mask != obligatory_mask
            ):
                raise DeonticAdapterError(
                    "obligatory actions conflict with the supplied action mask"
                )
            permitted_mask = obligatory_mask
            forbidden_mask = ALL_ACTION_MASK ^ permitted_mask
        elif status in {"conflict", "incomplete"}:
            # The quarantined action mask owns the safe outcome.  Obligations
            # that helped produce the quarantine are provenance, not actions
            # the optimizer may select.
            obligatory_mask = 0
        reason_value = value.get("rule_ids", value.get("reason_ids"))
        if (
            "reason_ids" in value
            and type(reason_value) in (list, tuple)
            and all(type(item) is str for item in reason_value)
        ):
            # A state-wide reason set is a convenient adapter output.  Expand
            # it deterministically onto each permitted action so receipts stay
            # action-local.
            reason_value = tuple(
                tuple(reason_value) if permitted_mask & (1 << index) else ()
                for index in range(MAX_ACTIONS)
            )
        return cls(
            permitted_mask=permitted_mask,
            forbidden_mask=forbidden_mask,
            rule_ids=_normalize_rule_ids(reason_value),
            status=status,
            obligatory_mask=obligatory_mask,
        )

    @property
    def allowed_mask(self) -> int:
        return self.permitted_mask & ~self.forbidden_mask & ALL_ACTION_MASK

    def allows(self, action_index: int) -> bool:
        return bool(self.allowed_mask & (1 << action_index))


class FixtureDeonticAdapter:
    """Small explicit adapter used by tests, never an implicit production default."""

    def __init__(self, forbidden_actions: Sequence[str] = ()) -> None:
        if type(forbidden_actions) not in (list, tuple, set, frozenset):
            raise DeonticAdapterError(
                "fixture forbidden_actions must be a bounded sequence"
            )
        if len(forbidden_actions) > MAX_ACTIONS:
            raise DeonticAdapterError("too many fixture forbidden actions")
        names = tuple(forbidden_actions)
        if len(set(names)) != len(names) or any(
            name not in ACTION_INDEX for name in names
        ):
            raise DeonticAdapterError(
                "fixture forbidden_actions contains an unknown or duplicate action"
            )
        self._forbidden_actions = tuple(names)

    def constraints(self, state: StateRef) -> DeonticConstraints:
        forbidden = 0
        for name in self._forbidden_actions:
            forbidden |= 1 << ACTION_INDEX[name]
        if state.padded:
            forbidden |= NAVIGATION_MASK | RESOLVE_MASK
        if (
            not state.applicable
            or (state.evidence_mask & state.required_evidence_bits)
            != state.required_evidence_bits
        ):
            forbidden |= RESOLVE_MASK
        permitted = ALL_ACTION_MASK ^ forbidden
        rule_ids = tuple(
            (f"fixture:{ACTION_NAMES[index]}:allow",)
            if permitted & (1 << index)
            else (f"fixture:{ACTION_NAMES[index]}:forbid",)
            for index in range(MAX_ACTIONS)
        )
        return DeonticConstraints(permitted, forbidden, rule_ids)

    def provenance_record(self) -> dict[str, Any]:
        return {
            "schema": "fixture-deontic-provenance-v1",
            "logic_semantics": "fixture-action-mask-v1",
            "profile": "fixture",
            "esso_evidence_hashes": {},
            "adapter_class": "FixtureDeonticAdapter",
            "forbidden_actions": sorted(self._forbidden_actions),
        }


class EvidenceCompletionDeonticAdapter:
    """Production-named adapter for evidence-completion action semantics.

    The adapter is a narrow normative boundary.  It does not inspect graph
    edges and cannot prove a fact.  It classifies all eight planner actions
    from the current state, while :func:`compile_model` intersects its six
    navigation permissions with structurally available graph slots.

    ``applicable`` is a property of the current real node.  The four cases are
    therefore: padded slots are abstain-only; real non-target nodes allow
    navigation plus abstention; real targets with incomplete evidence allow
    navigation plus abstention; and real targets with complete evidence make
    resolve obligatory and exclusive.

    The constructor requires explicit logic-semantics and profile identifiers,
    their content hashes, and ESSO evidence-hash provenance.  The canonical
    record and its SHA-256 are exposed for compiler and artifact identity
    binding.  Identifiers are descriptive and never substituted for content
    hashes in this production schema.
    """

    def __init__(
        self,
        logic_semantics: str | None = None,
        profile: str | None = None,
        esso_evidence_hashes: Mapping[str, str]
        | Sequence[tuple[str, str]]
        | None = None,
        *,
        provenance: Mapping[str, Any] | None = None,
        logic_semantics_sha256: str | None = None,
        profile_sha256: str | None = None,
        logic_semantics_hash: str | None = None,
        profile_hash: str | None = None,
    ) -> None:
        if (
            logic_semantics_sha256 is not None
            and logic_semantics_hash is not None
            and logic_semantics_sha256 != logic_semantics_hash
        ):
            raise DeonticAdapterError("logic semantics SHA-256 aliases disagree")
        if (
            profile_sha256 is not None
            and profile_hash is not None
            and profile_sha256 != profile_hash
        ):
            raise DeonticAdapterError("profile SHA-256 aliases disagree")
        logic_hash = logic_semantics_sha256 or logic_semantics_hash
        profile_digest = profile_sha256 or profile_hash
        if provenance is not None:
            if any(
                item is not None
                for item in (
                    logic_semantics,
                    profile,
                    esso_evidence_hashes,
                    logic_hash,
                    profile_digest,
                )
            ):
                raise DeonticAdapterError(
                    "explicit adapter fields cannot be combined with provenance"
                )
            if not isinstance(provenance, Mapping):
                raise DeonticAdapterError(
                    "adapter provenance must implement the mapping interface"
                )
            candidate = dict(provenance)
        else:
            if (
                logic_semantics is None
                or profile is None
                or esso_evidence_hashes is None
            ):
                raise DeonticAdapterError(
                    "logic_semantics, profile, and ESSO evidence hashes are required"
                )
            candidate = {
                "schema": EVIDENCE_DEONTIC_PROVENANCE_SCHEMA,
                "logic_semantics": logic_semantics,
                "profile": profile,
                "esso_evidence_hashes": esso_evidence_hashes,
                "adapter_class": "EvidenceCompletionDeonticAdapter",
            }
            if logic_hash is not None:
                candidate["logic_semantics_sha256"] = logic_hash
            if profile_digest is not None:
                candidate["profile_sha256"] = profile_digest
        normalized = _canonical_adapter_provenance(candidate)
        if normalized["schema"] != EVIDENCE_DEONTIC_PROVENANCE_SCHEMA:
            raise DeonticAdapterError(
                "EvidenceCompletionDeonticAdapter requires its production provenance schema"
            )
        if not normalized["esso_evidence_hashes"]:
            raise DeonticAdapterError(
                "EvidenceCompletionDeonticAdapter requires at least one ESSO evidence hash"
            )
        self._provenance = normalized
        self._provenance_sha256 = _sha256_bytes(canonical_json_bytes(normalized))

    @property
    def provenance_sha256(self) -> str:
        return self._provenance_sha256

    @property
    def profile(self) -> str:
        return self._provenance["profile"]

    @property
    def logic_semantics(self) -> str:
        return self._provenance["logic_semantics"]

    def provenance_record(self) -> dict[str, Any]:
        # A fresh JSON round-trip prevents callers from mutating nested
        # evidence-hash mappings held by the adapter.
        return json.loads(canonical_json_bytes(self._provenance).decode("utf-8"))

    @property
    def provenance(self) -> dict[str, Any]:
        return self.provenance_record()

    @staticmethod
    def _reason_ids(
        prefix: str, permitted: int, obligatory: int = 0
    ) -> tuple[tuple[str, ...], ...]:
        rows = []
        for action_index in range(MAX_ACTIONS):
            bit = 1 << action_index
            if obligatory & bit:
                reason = f"{prefix}:obligatory"
            elif permitted & bit:
                reason = f"{prefix}:permitted"
            else:
                reason = f"{prefix}:forbidden"
            rows.append((reason,))
        return tuple(rows)

    @staticmethod
    def _validate_state(state: StateRef) -> None:
        if type(state) is not StateRef:
            raise DeonticAdapterError(
                "EvidenceCompletionDeonticAdapter requires a StateRef"
            )
        if (
            type(state.decision_index) is not int
            or state.decision_index < 0
            or not _is_identifier(state.decision_id)
            or type(state.node_slot) is not int
            or state.node_slot < 0
            or state.evidence_mask not in EVIDENCE_MASKS
            or state.required_evidence_bits not in EVIDENCE_MASKS
            or type(state.applicable) is not bool
            or type(state.padded) is not bool
        ):
            raise DeonticAdapterError(
                "EvidenceCompletionDeonticAdapter received a malformed StateRef"
            )
        if state.padded:
            if state.node_id is not None or state.applicable:
                raise DeonticAdapterError(
                    "padded StateRef must have no current node and must be non-applicable"
                )
        elif not _is_graph_identifier(state.node_id):
            raise DeonticAdapterError(
                "a real StateRef must identify its current graph node"
            )

    def constraints(self, state: StateRef) -> DeonticConstraints:
        self._validate_state(state)
        if state.padded:
            permitted = ABSTAIN_MASK
            status = EVIDENCE_STATUS_PADDED
            prefix = "evidence_completion:padded"
            return DeonticConstraints(
                permitted,
                ALL_ACTION_MASK ^ permitted,
                self._reason_ids(prefix, permitted),
                status=status,
            )
        if not state.applicable:
            permitted = NAVIGATION_MASK | ABSTAIN_MASK
            status = EVIDENCE_STATUS_NON_APPLICABLE
            prefix = "evidence_completion:non_applicable"
            return DeonticConstraints(
                permitted,
                ALL_ACTION_MASK ^ permitted,
                self._reason_ids(prefix, permitted),
                status=status,
            )
        complete = (
            state.evidence_mask & state.required_evidence_bits
        ) == state.required_evidence_bits
        if not complete:
            permitted = NAVIGATION_MASK | ABSTAIN_MASK
            status = EVIDENCE_STATUS_INCOMPLETE
            prefix = "evidence_completion:incomplete"
            return DeonticConstraints(
                permitted,
                ALL_ACTION_MASK ^ permitted,
                self._reason_ids(prefix, permitted),
                status=status,
            )
        permitted = RESOLVE_MASK
        status = EVIDENCE_STATUS_COMPLETE
        prefix = "evidence_completion:complete"
        return DeonticConstraints(
            permitted,
            ALL_ACTION_MASK ^ permitted,
            self._reason_ids(prefix, permitted, obligatory=RESOLVE_MASK),
            status=status,
            obligatory_mask=RESOLVE_MASK,
        )


def _adapter_provenance_record(adapter: Any) -> dict[str, Any]:
    """Obtain a bounded provenance record, failing closed if it is malformed."""

    if adapter is None:
        raise DeonticAdapterError("a deontic adapter is required; absence fails closed")
    try:
        method = getattr(adapter, "provenance_record", None)
        if callable(method):
            candidate = method()
        else:
            candidate = getattr(adapter, "provenance", None)
            if callable(candidate):
                candidate = candidate()
        if candidate is None:
            adapter_type = f"{type(adapter).__module__}.{type(adapter).__qualname__}"
            adapter_digest = _sha256_bytes(adapter_type.encode("utf-8"))
            candidate = {
                "schema": "unbound-deontic-adapter-provenance-v1",
                "logic_semantics": "unbound",
                "profile": "unbound",
                "esso_evidence_hashes": {},
                "adapter_class": f"unbound:{adapter_digest}",
            }
        return _canonical_adapter_provenance(dict(candidate))
    except DeonticAdapterError:
        raise
    except Exception as exc:
        raise DeonticAdapterError("deontic adapter provenance is malformed") from exc


@dataclass(frozen=True)
class NavigationSlot:
    source_id: str
    target_id: str
    source_slot: int
    target_slot: int
    relation: str
    relation_source_id: str
    relation_target_id: str
    source_direction: str
    browse_direction: str
    evidence_bits: int


@dataclass(frozen=True)
class CompiledModel:
    config: PlannerConfig
    utility: UtilityModel
    snapshot: Mapping[str, Any]
    decisions: tuple[RequiredDecision, ...]
    node_ids: tuple[str, ...]
    node_slot_by_id: Mapping[str, int]
    navigation: tuple[tuple[NavigationSlot | None, ...], ...]
    next_state_indices: np.ndarray
    nav_rewards: np.ndarray
    nav_valid: np.ndarray
    normative_allowed: np.ndarray
    base_allowed: np.ndarray
    resolve_available: np.ndarray
    abstain_available: np.ndarray
    rule_ids: tuple[tuple[tuple[str, ...], ...], ...]
    deontic_statuses: tuple[str, ...]
    deontic_obligatory_masks: tuple[int, ...]
    adapter_provenance: Mapping[str, Any]
    provenance: Mapping[str, str]
    actual_node_count: int
    padded_graph_slots: int
    navigation_slot_padding_count: int
    padded_navigation_slot_count: int
    navigation_truncation_count: int
    snapshot_missing_id_count: int

    def __post_init__(self) -> None:
        for array in (
            self.next_state_indices,
            self.nav_rewards,
            self.nav_valid,
            self.normative_allowed,
            self.base_allowed,
            self.resolve_available,
            self.abstain_available,
        ):
            array.setflags(write=False)

    def state_index(
        self, decision_index: int, node_slot: int, evidence_mask: int
    ) -> int:
        return ((decision_index * self.config.node_slots) + node_slot) * len(
            EVIDENCE_MASKS
        ) + evidence_mask

    def state_ref(self, state_index: int) -> StateRef:
        if (
            type(state_index) is not int
            or not 0 <= state_index < self.config.state_count
        ):
            raise KnowledgeQTableError("state index is outside the model")
        decision_index, remainder = divmod(
            state_index, self.config.node_slots * len(EVIDENCE_MASKS)
        )
        node_slot, evidence_mask = divmod(remainder, len(EVIDENCE_MASKS))
        node_id = (
            self.node_ids[node_slot] if node_slot < self.actual_node_count else None
        )
        decision = self.decisions[decision_index]
        applicable = node_id is not None and decision.is_applicable(node_id)
        return StateRef(
            decision_index=decision_index,
            decision_id=decision.decision_id,
            node_slot=node_slot,
            node_id=node_id,
            evidence_mask=evidence_mask,
            required_evidence_bits=decision.required_evidence_bits,
            applicable=applicable,
            padded=node_slot >= self.actual_node_count,
        )

    def allowed_for_layer(
        self, layer: int, start: int = 0, end: int | None = None
    ) -> np.ndarray:
        if type(layer) is not int or not 0 <= layer < self.config.layers:
            raise KnowledgeQTableError("layer is outside the model")
        if end is None:
            end = self.config.state_count
        allowed = self.base_allowed[start:end]
        if layer == 0:
            allowed = allowed.copy()
            allowed[:, :NAVIGATION_ACTION_COUNT] = False
        return allowed


def _adapter_constraints(adapter: Any, state: StateRef) -> DeonticConstraints:
    if adapter is None:
        raise DeonticAdapterError("a deontic adapter is required; absence fails closed")
    method = getattr(adapter, "constraints", None)
    if method is None:
        method = adapter if callable(adapter) else None
    if not callable(method):
        raise DeonticAdapterError(
            "deontic adapter must expose constraints(state) or be callable"
        )
    try:
        value = method(state)
        return DeonticConstraints.from_value(value)
    except DeonticAdapterError:
        raise
    except Exception as exc:
        raise DeonticAdapterError(
            f"deontic adapter failed closed for state {state}"
        ) from exc


def _decision_records_for_model(
    snapshot: Mapping[str, Any], required_decisions: Sequence[Mapping[str, Any]] | None
) -> tuple[dict[str, Any], ...]:
    embedded = snapshot.get("required_decisions")
    if required_decisions is None:
        if embedded is None:
            raise RequiredDecisionValidationError("required decisions are absent")
        return canonicalize_required_decisions(embedded)
    supplied = canonicalize_required_decisions(required_decisions)
    if embedded is not None and tuple(supplied) != tuple(
        canonicalize_required_decisions(embedded)
    ):
        raise RequiredDecisionValidationError(
            "separate required decisions disagree with the snapshot records"
        )
    return supplied


def _canonical_config(config: PlannerConfig) -> dict[str, Any]:
    return {
        "profile": config.profile,
        "layers": config.layers,
        "decisions": config.decisions,
        "node_slots": config.node_slots,
        "gamma": float(config.gamma),
        "chunk_size": config.chunk_size,
        "allow_explicit_padding": config.allow_explicit_padding,
        "evidence_mask_bits": EVIDENCE_MASK_BITS,
        "actions": list(ACTION_NAMES),
    }


def _canonical_semantic_config(config: PlannerConfig) -> dict[str, Any]:
    """Return config fields that affect table semantics, excluding chunking."""

    result = _canonical_config(config)
    result.pop("chunk_size")
    return result


def _canonical_decision_bytes(decisions: Sequence[RequiredDecision]) -> bytes:
    return canonical_json_bytes([decision.to_record() for decision in decisions])


def _recurrence_record(config: PlannerConfig) -> dict[str, Any]:
    """Describe the exact finite-horizon recurrence independently of inputs."""

    return {
        "version": "knowledge-q-finite-horizon-v1",
        "horizon_axis": "remaining_decision_steps_not_chronological_time",
        "layer_zero": "terminal_actions_only",
        "navigation": "utility.navigation_cost + new_evidence_bits * utility.new_evidence_reward + gamma * V[layer-1,next_state]",
        "resolve": "utility.resolve_reward_and_terminal",
        "abstain_or_escalate": "utility.abstain_reward_and_terminal",
        "unavailable_value": float(FORBIDDEN_VALUE),
        "first_index_tie_break": True,
        "action_order": list(ACTION_NAMES),
        "layers": config.layers,
        "gamma": float(config.gamma),
        "dtype": "<f4",
    }


def compile_model(
    snapshot: Mapping[str, Any],
    required_decisions: Sequence[Mapping[str, Any]] | None = None,
    *,
    config: PlannerConfig,
    adapter: Any,
    utility: UtilityModel = DEFAULT_UTILITY_MODEL,
) -> CompiledModel:
    """Compile knowledge, normative masks, utility, then the DP transition model."""

    if type(config) is not PlannerConfig:
        raise KnowledgeQTableError("config must be a PlannerConfig")
    if type(utility) is not UtilityModel:
        raise KnowledgeQTableError("utility must be a UtilityModel")
    config.validate()
    canonical_snapshot = canonicalize_snapshot(snapshot)
    records = _decision_records_for_model(canonical_snapshot, required_decisions)
    if len(records) != config.decisions:
        raise RequiredDecisionValidationError(
            f"expected exactly {config.decisions} required decisions, got {len(records)}"
        )
    decisions = tuple(RequiredDecision.from_record(record) for record in records)
    adapter_provenance = _adapter_provenance_record(adapter)
    adapter_provenance_sha = _sha256_bytes(canonical_json_bytes(adapter_provenance))
    graph_nodes = canonical_snapshot["graph"]["nodes"]
    actual_node_count = len(graph_nodes)
    if actual_node_count > config.node_slots:
        raise SnapshotValidationError(
            "canonical graph has more nodes than the configured node slots"
        )
    if actual_node_count < config.node_slots:
        explicit_padding = (
            config.allow_explicit_padding
            or "slot_policy" in canonical_snapshot
            or "padding_policy" in canonical_snapshot["graph"]
        )
        if not explicit_padding:
            raise SnapshotValidationError(
                "graph-node slots would be silently padded; declare explicit abstain-only padding"
            )
    node_ids = tuple(node["id"] for node in graph_nodes)
    node_slot_by_id = MappingProxyType(
        {node_id: index for index, node_id in enumerate(node_ids)}
    )

    candidates: list[list[NavigationSlot]] = [[] for _ in node_ids]
    for edge in canonical_snapshot["graph"]["edges"]:
        source_id = edge["source"]
        target_id = edge["target"]
        source_slot = node_slot_by_id[source_id]
        target_slot = node_slot_by_id[target_id]
        supplied_bits = edge.get("evidence_bits")
        forward_bits = (
            supplied_bits if supplied_bits is not None else EVIDENCE_FORWARD_DISCOVERY
        )
        reverse_bits = (
            supplied_bits if supplied_bits is not None else EVIDENCE_REVERSE_DISCOVERY
        )
        candidates[source_slot].append(
            NavigationSlot(
                source_id=source_id,
                target_id=target_id,
                source_slot=source_slot,
                target_slot=target_slot,
                relation=edge["relation"],
                relation_source_id=source_id,
                relation_target_id=target_id,
                source_direction=edge["source_direction"],
                browse_direction="forward",
                evidence_bits=forward_bits,
            )
        )
        candidates[target_slot].append(
            NavigationSlot(
                source_id=target_id,
                target_id=source_id,
                source_slot=target_slot,
                target_slot=source_slot,
                relation=edge["relation"],
                relation_source_id=source_id,
                relation_target_id=target_id,
                source_direction=edge["source_direction"],
                browse_direction="reverse",
                evidence_bits=reverse_bits,
            )
        )

    navigation_rows: list[tuple[NavigationSlot | None, ...]] = []
    navigation_truncation_count = 0
    navigation_slot_padding_count = 0
    for source_slot, row in enumerate(candidates):
        row.sort(
            key=lambda item: (
                0 if item.browse_direction == "forward" else 1,
                item.relation,
                item.target_id,
                item.source_direction,
            )
        )
        if len(row) > NAVIGATION_ACTION_COUNT:
            navigation_truncation_count += len(row) - NAVIGATION_ACTION_COUNT
        selected = row[:NAVIGATION_ACTION_COUNT]
        navigation_slot_padding_count += NAVIGATION_ACTION_COUNT - len(selected)
        navigation_rows.append(
            tuple(selected + [None] * (NAVIGATION_ACTION_COUNT - len(selected)))
        )
    navigation_rows.extend(
        [
            tuple([None] * NAVIGATION_ACTION_COUNT)
            for _ in range(config.node_slots - actual_node_count)
        ]
    )
    navigation = tuple(navigation_rows)

    state_count = config.state_count
    next_state_indices = np.full(
        (state_count, NAVIGATION_ACTION_COUNT), -1, dtype=np.int32
    )
    nav_rewards = np.full(
        (state_count, NAVIGATION_ACTION_COUNT), FORBIDDEN_VALUE, dtype=np.dtype("<f4")
    )
    nav_valid = np.zeros((state_count, NAVIGATION_ACTION_COUNT), dtype=np.bool_)
    normative_allowed = np.zeros((state_count, MAX_ACTIONS), dtype=np.bool_)
    base_allowed = np.zeros((state_count, MAX_ACTIONS), dtype=np.bool_)
    resolve_available = np.zeros(state_count, dtype=np.bool_)
    abstain_available = np.zeros(state_count, dtype=np.bool_)
    rule_ids: list[tuple[tuple[str, ...], ...]] = []
    deontic_statuses: list[str] = []
    deontic_obligatory_masks: list[int] = []

    for decision_index, decision in enumerate(decisions):
        for node_slot in range(config.node_slots):
            node_id = node_ids[node_slot] if node_slot < actual_node_count else None
            padded = node_slot >= actual_node_count
            # Applicability is about the current real node.  A padded slot has
            # no current node, even when the decision's rule is "always".
            applicable = not padded and decision.is_applicable(node_id)
            for evidence_mask in EVIDENCE_MASKS:
                state_index = ((decision_index * config.node_slots) + node_slot) * len(
                    EVIDENCE_MASKS
                ) + evidence_mask
                state = StateRef(
                    decision_index=decision_index,
                    decision_id=decision.decision_id,
                    node_slot=node_slot,
                    node_id=node_id,
                    evidence_mask=evidence_mask,
                    required_evidence_bits=decision.required_evidence_bits,
                    applicable=applicable,
                    padded=padded,
                )
                constraints = _adapter_constraints(adapter, state)
                normative_allowed[state_index, :] = [
                    constraints.allows(action_index)
                    for action_index in range(MAX_ACTIONS)
                ]
                if constraints.allows(RESOLVE_ACTION_INDEX) and (
                    not applicable
                    or (evidence_mask & decision.required_evidence_bits)
                    != decision.required_evidence_bits
                ):
                    raise DeonticAdapterError(
                        "deontic adapter permits resolve without applicability and evidence preconditions"
                    )
                if padded and constraints.allowed_mask != ABSTAIN_MASK:
                    raise DeonticAdapterError(
                        "padded graph slots must be exactly abstain-only in the adapter"
                    )

                effective = constraints.allowed_mask
                for action_index, slot in enumerate(navigation[node_slot]):
                    if (
                        slot is not None
                        and not padded
                        and effective & (1 << action_index)
                    ):
                        target_mask = evidence_mask | slot.evidence_bits
                        target_index = (
                            (decision_index * config.node_slots) + slot.target_slot
                        ) * len(EVIDENCE_MASKS) + target_mask
                        next_state_indices[state_index, action_index] = target_index
                        new_bits = slot.evidence_bits & ~evidence_mask
                        nav_rewards[state_index, action_index] = np.float32(
                            float(utility.navigation_cost)
                            + float(utility.new_evidence_reward) * new_bits.bit_count()
                        )
                        nav_valid[state_index, action_index] = True
                        base_allowed[state_index, action_index] = True
                resolve_ok = (
                    not padded
                    and applicable
                    and (evidence_mask & decision.required_evidence_bits)
                    == decision.required_evidence_bits
                    and bool(effective & RESOLVE_MASK)
                )
                abstain_ok = bool(effective & ABSTAIN_MASK)
                base_allowed[state_index, RESOLVE_ACTION_INDEX] = resolve_ok
                base_allowed[state_index, ABSTAIN_ACTION_INDEX] = abstain_ok
                resolve_available[state_index] = resolve_ok
                abstain_available[state_index] = abstain_ok
                if not (resolve_ok or abstain_ok):
                    raise DeonticAdapterError(
                        "every state must have a permitted terminal resolution or abstention"
                    )
                rule_ids.append(constraints.rule_ids)
                deontic_statuses.append(constraints.status)
                deontic_obligatory_masks.append(constraints.obligatory_mask)

    if not (
        len(rule_ids)
        == len(deontic_statuses)
        == len(deontic_obligatory_masks)
        == state_count
    ):
        raise KnowledgeQTableError("internal state compilation count mismatch")
    snapshot_bytes = canonical_json_bytes(canonical_snapshot)
    decision_bytes = _canonical_decision_bytes(decisions)
    config_bytes = canonical_json_bytes(_canonical_semantic_config(config))
    utility_record = utility.to_record()
    utility_bytes = canonical_json_bytes(utility_record)
    recurrence_record = _recurrence_record(config)
    recurrence_bytes = canonical_json_bytes(recurrence_record)
    constraints_bytes = canonical_json_bytes(
        {
            "normative_action_mask": normative_allowed.astype(np.uint8).tolist(),
            "statuses": deontic_statuses,
            "obligatory_masks": deontic_obligatory_masks,
            "reason_ids": rule_ids,
        }
    )
    deontic_sha = _sha256_bytes(constraints_bytes)
    utility_sha = _sha256_bytes(utility_bytes)
    recurrence_sha = _sha256_bytes(recurrence_bytes)
    snapshot_sha = _sha256_bytes(snapshot_bytes)
    decision_sha = _sha256_bytes(decision_bytes)
    config_sha = _sha256_bytes(config_bytes)
    provenance = MappingProxyType(
        {
            "snapshot_sha256": snapshot_sha,
            "required_decisions_sha256": decision_sha,
            "config_sha256": config_sha,
            "deontic_constraints_sha256": deontic_sha,
            "deontic_adapter_provenance_sha256": adapter_provenance_sha,
            "utility_model_sha256": utility_sha,
            "recurrence_sha256": recurrence_sha,
            "input_sha256": _sha256_bytes(
                canonical_json_bytes(
                    {
                        "snapshot_sha256": snapshot_sha,
                        "required_decisions_sha256": decision_sha,
                        "config_sha256": config_sha,
                        "deontic_constraints_sha256": deontic_sha,
                        "deontic_adapter_provenance_sha256": adapter_provenance_sha,
                        "utility_model_sha256": utility_sha,
                        "recurrence_sha256": recurrence_sha,
                    }
                )
            ),
            "canonical_graph_sha256": canonical_snapshot["provenance"][
                "canonical_graph_sha256"
            ],
        }
    )
    return CompiledModel(
        config=config,
        utility=utility,
        snapshot=canonical_snapshot,
        decisions=decisions,
        node_ids=node_ids,
        node_slot_by_id=node_slot_by_id,
        navigation=navigation,
        next_state_indices=next_state_indices,
        nav_rewards=nav_rewards,
        nav_valid=nav_valid,
        normative_allowed=normative_allowed,
        base_allowed=base_allowed,
        resolve_available=resolve_available,
        abstain_available=abstain_available,
        rule_ids=tuple(rule_ids),
        deontic_statuses=tuple(deontic_statuses),
        deontic_obligatory_masks=tuple(deontic_obligatory_masks),
        adapter_provenance=MappingProxyType(adapter_provenance),
        provenance=provenance,
        actual_node_count=actual_node_count,
        padded_graph_slots=config.node_slots - actual_node_count,
        navigation_slot_padding_count=navigation_slot_padding_count,
        padded_navigation_slot_count=(config.node_slots - actual_node_count)
        * NAVIGATION_ACTION_COUNT,
        navigation_truncation_count=navigation_truncation_count,
        snapshot_missing_id_count=len(canonical_snapshot["missing_ids"]),
    )


def _effective_allowed(
    model: CompiledModel, layer: int, start: int, end: int
) -> np.ndarray:
    return model.allowed_for_layer(layer, start, end)


def _first_argmax(
    values: np.ndarray, allowed: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Return the first-index maximum, explicitly preserving action order."""

    if (
        values.ndim != 2
        or allowed.shape != values.shape
        or values.shape[1] != MAX_ACTIONS
    ):
        raise KnowledgeQTableError("argmax inputs have the wrong shape")
    choices = np.full(values.shape[0], -1, dtype=np.int8)
    best = np.full(values.shape[0], -np.inf, dtype=np.float32)
    for action_index in range(MAX_ACTIONS):
        take = allowed[:, action_index] & (
            (choices < 0) | (values[:, action_index] > best)
        )
        choices[take] = action_index
        best[take] = values[take, action_index]
    if np.any(choices < 0):
        raise KnowledgeQTableError("a state has no permitted action")
    return choices, best


def _q_chunk(
    model: CompiledModel,
    layer: int,
    previous_values: np.ndarray | None,
    start: int,
    end: int,
) -> np.ndarray:
    size = end - start
    values = np.full((size, MAX_ACTIONS), FORBIDDEN_VALUE, dtype=np.dtype("<f4"))
    for action_index in range(NAVIGATION_ACTION_COUNT):
        valid = model.nav_valid[start:end, action_index]
        if layer > 0 and np.any(valid):
            row_values = model.nav_rewards[start:end, action_index].copy()
            state_indices = model.next_state_indices[start:end, action_index]
            valid_rows = np.flatnonzero(valid)
            continuation = previous_values[state_indices[valid_rows]]
            row_values[valid_rows] = (
                row_values[valid_rows] + np.float32(model.config.gamma) * continuation
            )
            values[valid, action_index] = row_values[valid]
    values[:, RESOLVE_ACTION_INDEX] = np.where(
        model.resolve_available[start:end],
        np.float32(model.utility.resolve_reward),
        FORBIDDEN_VALUE,
    ).astype(np.dtype("<f4"), copy=False)
    values[:, ABSTAIN_ACTION_INDEX] = np.where(
        model.abstain_available[start:end],
        np.float32(model.utility.abstain_reward),
        FORBIDDEN_VALUE,
    ).astype(np.dtype("<f4"), copy=False)
    allowed = _effective_allowed(model, layer, start, end)
    values = np.where(allowed, values, FORBIDDEN_VALUE).astype(
        np.dtype("<f4"), copy=False
    )
    if not np.all(np.isfinite(values)):
        raise KnowledgeQTableError(
            "internal transition compilation produced a non-finite Q value"
        )
    return values


def _finite_trace_spec(model: CompiledModel) -> dict[str, Any]:
    return {
        "schema": "knowledge-q-finite-trace-contract-v1",
        "horizon_semantics": "remaining_decision_steps_not_chronological_time",
        "declared_transition_bound": model.config.layers,
        "properties": [
            "always_no_forbidden_action",
            "eventually_resolve_or_abstain_or_escalate_within_declared_bound",
            "resolution_is_terminal",
        ],
        "transition_measure": "each navigation decrements the layer; layer zero has terminal actions only",
        "normative_boundary": "the Q recurrence may rank only actions admitted by the external deontic mask",
    }


def _artifact_identity_sha256(table_sha256: str, input_sha256: str) -> str:
    return _sha256_bytes(
        canonical_json_bytes(
            {
                "input_sha256": input_sha256,
                "table_sha256": table_sha256,
            }
        )
    )


def _manifest_for_model(
    model: CompiledModel, output_path: Path, output_sha256: str
) -> dict[str, Any]:
    limitations = [
        "The finite-horizon values are exact only for this bounded model, canonical snapshot, adapter output, and explicit utility model.",
        "Graph edges, including reverse browsing edges, are navigation/evidence discovery links and never logical implication or proof.",
        "The deontic kernel owns obligation, prohibition, permission, conflict, and incompleteness semantics; the Q recurrence only consumes its mask.",
        "The snapshot may be incomplete or truncated, so the artifact does not claim world-model completeness or factual verification.",
    ]
    if model.snapshot["truncated"] or model.snapshot["missing_ids"]:
        limitations.append(
            "Snapshot truncation or missing node IDs are preserved as input limitations."
        )
    return {
        "schema": MANIFEST_SCHEMA,
        "planner": {
            **_canonical_config(model.config),
            "state_factorization": {
                "decisions": model.config.decisions,
                "graph_node_slots": model.config.node_slots,
                "evidence_masks": len(EVIDENCE_MASKS),
                "state_count": model.config.state_count,
            },
            "action_order": list(ACTION_NAMES),
            "first_index_tie_break": True,
            "bellman_layer_zero_is_terminal_only": True,
            "horizon_semantics": "remaining_decision_steps_not_chronological_time",
        },
        "input": {
            "snapshot_sha256": model.provenance["snapshot_sha256"],
            "required_decisions_sha256": model.provenance["required_decisions_sha256"],
            "config_sha256": model.provenance["config_sha256"],
            "deontic_constraints_sha256": model.provenance[
                "deontic_constraints_sha256"
            ],
            "deontic_adapter_provenance_sha256": model.provenance[
                "deontic_adapter_provenance_sha256"
            ],
            "utility_model_sha256": model.provenance["utility_model_sha256"],
            "recurrence_sha256": model.provenance["recurrence_sha256"],
            "input_sha256": model.provenance["input_sha256"],
        },
        "compiler_stages": [
            {
                "stage": "canonical_knowledge",
                "output_sha256": model.provenance["snapshot_sha256"],
            },
            {
                "stage": "normative_action_mask",
                "precedence": "forbidden_and_obligatory_constraints_before_utility_ranking",
                "conflict_or_incomplete_policy": "abstain_or_escalate_only",
                "output_sha256": model.provenance["deontic_constraints_sha256"],
            },
            {
                "stage": "deontic_adapter_provenance",
                "output_sha256": model.provenance["deontic_adapter_provenance_sha256"],
                "record": dict(model.adapter_provenance),
            },
            {
                "stage": "utility_outcome_model",
                "model": model.utility.to_record(),
                "output_sha256": model.provenance["utility_model_sha256"],
            },
            {
                "stage": "bellman_dynamic_program",
                "recurrence": _recurrence_record(model.config),
                "output_sha256": model.provenance["recurrence_sha256"],
            },
        ],
        "output": {
            "file_name": output_path.name,
            "sha256": output_sha256,
            "dtype": "<f4",
            "order": "C",
            "shape": list(model.config.shape),
            "raw_data_bytes": model.config.raw_data_bytes,
            "npy_file_bytes": output_path.stat().st_size,
            "artifact_identity_sha256": _artifact_identity_sha256(
                output_sha256, model.provenance["input_sha256"]
            ),
        },
        "counts": {
            "actual_graph_nodes": model.actual_node_count,
            "declared_graph_node_slots": model.config.node_slots,
            "required_decisions": model.config.decisions,
            "states": model.config.state_count,
            "actions": MAX_ACTIONS,
            "snapshot_missing_ids": model.snapshot_missing_id_count,
            "deontic_conflict_states": model.deontic_statuses.count("conflict"),
            "deontic_incomplete_states": model.deontic_statuses.count("incomplete"),
            "evidence_padded_states": model.deontic_statuses.count(
                EVIDENCE_STATUS_PADDED
            ),
            "evidence_non_applicable_states": model.deontic_statuses.count(
                EVIDENCE_STATUS_NON_APPLICABLE
            ),
            "evidence_incomplete_states": model.deontic_statuses.count(
                EVIDENCE_STATUS_INCOMPLETE
            ),
            "evidence_complete_states": model.deontic_statuses.count(
                EVIDENCE_STATUS_COMPLETE
            ),
        },
        "padding_counts": {
            "padded_graph_slots": model.padded_graph_slots,
            "padded_navigation_slots_for_graph_padding": model.padded_navigation_slot_count,
            "unused_navigation_slots_on_real_nodes": model.navigation_slot_padding_count,
        },
        "truncation_counts": {
            "navigation_candidates_dropped_after_six_slots": model.navigation_truncation_count,
            "snapshot_truncated": int(model.snapshot["truncated"]),
        },
        "evidence_mask_semantics": {
            "bit_width": EVIDENCE_MASK_BITS,
            "mask_values": list(EVIDENCE_MASKS),
            "bit_0": "forward discovery channel traversed",
            "bit_1": "reverse-browse discovery channel traversed",
            "nonclaim": "neither bit asserts that a graph edge is true or proves a proposition",
        },
        "assumptions": [
            "The supplied JSON is an already canonical, bounded snapshot and its canonical graph hash is checked.",
            "The supplied deontic adapter is the authoritative normative boundary for this finite model and returns a total eight-action classification, status, and reason IDs for every state.",
            "StateRef.applicable means that the current real graph node is a valid resolution target, not that the required decision is globally inapplicable.",
            "Only explicitly padded graph slots are abstain_or_escalate-only; real non-target nodes permit structurally available navigation plus abstain_or_escalate and forbid resolve.",
            "Real target nodes with incomplete required evidence permit structurally available navigation plus abstain_or_escalate and forbid resolve; complete target states make resolve obligatory and exclusive under the evidence-completion adapter.",
            "The first resolution alternative in stable ID order is the receipt label for the single resolve action.",
            "Missing navigation candidates are unavailable actions, while graph-slot padding is explicit and abstain-only.",
        ],
        "limitations": limitations,
        "provenance": {
            "snapshot": model.snapshot["provenance"],
            "deontic_adapter": dict(model.adapter_provenance),
            "planner_hashes": dict(model.provenance),
        },
        "verification": {
            "status": "generation_only; run verify to obtain exhaustive replay evidence",
            "replay_scope": "all layers, all state rows, all eight actions in bounded chunks",
            "finite_trace_contract": _finite_trace_spec(model),
            "finite_trace_gate": "pending_independent_verification",
        },
    }


def _write_canonical_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def generate_table(
    output: os.PathLike[str] | str,
    snapshot: Mapping[str, Any],
    required_decisions: Sequence[Mapping[str, Any]] | None = None,
    *,
    profile: str = "public",
    config: PlannerConfig | None = None,
    adapter: Any = None,
    utility: UtilityModel = DEFAULT_UTILITY_MODEL,
    manifest: os.PathLike[str] | str | None = None,
    chunk_size: int | None = None,
    progress: bool = False,
) -> dict[str, Any]:
    """Compile and stream a table to a memory-mapped ``.npy`` file."""

    del (
        progress
    )  # Progress output would be an irrelevant, non-reproducible side channel.
    if config is None:
        try:
            config = PROFILES[profile]
        except KeyError as exc:
            raise KnowledgeQTableError(f"unknown profile {profile!r}") from exc
    if chunk_size is not None:
        if type(chunk_size) is not int or not 1 <= chunk_size <= MAX_STATES:
            raise KnowledgeQTableError("chunk_size is outside its bounded range")
        config = PlannerConfig(
            layers=config.layers,
            decisions=config.decisions,
            node_slots=config.node_slots,
            gamma=config.gamma,
            chunk_size=chunk_size,
            allow_explicit_padding=config.allow_explicit_padding,
            profile=config.profile,
        )
    model = compile_model(
        snapshot,
        required_decisions,
        config=config,
        adapter=adapter,
        utility=utility,
    )
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    table = np.lib.format.open_memmap(
        output_path,
        mode="w+",
        dtype=np.dtype("<f4"),
        shape=model.config.shape,
        fortran_order=False,
        version=(1, 0),
    )
    previous_values: np.ndarray | None = None
    for layer in range(model.config.layers):
        current_values = np.empty(model.config.state_count, dtype=np.dtype("<f4"))
        for start in range(0, model.config.state_count, model.config.chunk_size):
            end = min(model.config.state_count, start + model.config.chunk_size)
            values = _q_chunk(model, layer, previous_values, start, end)
            table[layer, start:end, :] = values
            _, best = _first_argmax(
                values, _effective_allowed(model, layer, start, end)
            )
            current_values[start:end] = best
        table.flush()
        previous_values = current_values
    table.flush()
    del table
    output_sha = file_sha256(output_path)
    manifest_value = _manifest_for_model(model, output_path, output_sha)
    if manifest is not None:
        _write_canonical_json(Path(manifest), manifest_value)
    return manifest_value


build_table = generate_table


def _read_npy_layout(path: Path) -> tuple[tuple[int, ...], np.dtype[Any], bool, int]:
    try:
        with path.open("rb") as handle:
            version = np.lib.format.read_magic(handle)
            if version == (1, 0):
                shape, fortran_order, dtype = np.lib.format.read_array_header_1_0(
                    handle
                )
            elif version == (2, 0):
                shape, fortran_order, dtype = np.lib.format.read_array_header_2_0(
                    handle
                )
            elif version == (3, 0) and hasattr(np.lib.format, "read_array_header_3_0"):
                shape, fortran_order, dtype = np.lib.format.read_array_header_3_0(
                    handle
                )
            else:
                raise TableValidationError(f"unsupported NPY version {version}")
            return tuple(shape), np.dtype(dtype), bool(fortran_order), handle.tell()
    except TableValidationError:
        raise
    except Exception as exc:
        raise TableValidationError("unable to read NPY header") from exc


def _inspect_table(
    path: Path, config: PlannerConfig
) -> tuple[np.memmap | None, list[str]]:
    issues: list[str] = []
    if not path.exists() or not path.is_file():
        return None, ["table file is absent"]
    try:
        shape, dtype, fortran_order, header_bytes = _read_npy_layout(path)
    except TableValidationError as exc:
        return None, [str(exc)]
    if shape != config.shape:
        issues.append(f"shape {shape} does not equal expected {config.shape}")
    if dtype != np.dtype("<f4"):
        issues.append(f"dtype {dtype.str} does not equal <f4")
    if fortran_order:
        issues.append("fortran-order NPY is not accepted")
    expected_file_bytes = header_bytes + config.raw_data_bytes
    if path.stat().st_size != expected_file_bytes:
        issues.append(
            f"file byte length {path.stat().st_size} does not equal expected {expected_file_bytes}"
        )
    if issues:
        return None, issues
    try:
        table = np.load(path, mmap_mode="r", allow_pickle=False)
    except Exception as exc:  # noqa: BLE001 - NumPy exposes multiple loader exception families.
        return None, [f"unable to memory-map table: {exc}"]
    if not isinstance(table, np.memmap):
        return None, ["table did not load as a memory map"]
    return table, issues


def _manifest_issues(
    manifest: Mapping[str, Any],
    model: CompiledModel,
    table_path: Path,
    table_sha256: str | None,
) -> list[str]:
    issues: list[str] = []
    if type(manifest) is not dict or manifest.get("schema") != MANIFEST_SCHEMA:
        return ["manifest has an unsupported schema"]
    output = manifest.get("output")
    planner = manifest.get("planner")
    inputs = manifest.get("input")
    if (
        type(output) is not dict
        or type(planner) is not dict
        or type(inputs) is not dict
    ):
        return ["manifest is missing output, planner, or input objects"]
    if output.get("shape") != list(model.config.shape):
        issues.append("manifest shape mismatch")
    if output.get("raw_data_bytes") != model.config.raw_data_bytes:
        issues.append("manifest raw_data_bytes mismatch")
    if output.get("dtype") != "<f4" or output.get("order") != "C":
        issues.append("manifest dtype/order mismatch")
    for key, expected in {
        "snapshot_sha256": model.provenance["snapshot_sha256"],
        "required_decisions_sha256": model.provenance["required_decisions_sha256"],
        "config_sha256": model.provenance["config_sha256"],
        "deontic_constraints_sha256": model.provenance["deontic_constraints_sha256"],
        "deontic_adapter_provenance_sha256": model.provenance[
            "deontic_adapter_provenance_sha256"
        ],
        "utility_model_sha256": model.provenance["utility_model_sha256"],
        "recurrence_sha256": model.provenance["recurrence_sha256"],
        "input_sha256": model.provenance["input_sha256"],
    }.items():
        if inputs.get(key) != expected:
            issues.append(f"manifest input hash mismatch for {key}")
    if output.get("npy_file_bytes") != table_path.stat().st_size:
        issues.append("manifest NPY byte length mismatch")
    if table_sha256 is not None and output.get("sha256") != table_sha256:
        issues.append("manifest output SHA-256 mismatch")
    if table_sha256 is not None and output.get(
        "artifact_identity_sha256"
    ) != _artifact_identity_sha256(table_sha256, model.provenance["input_sha256"]):
        issues.append("manifest artifact identity mismatch")
    verification = manifest.get("verification")
    if type(verification) is not dict or verification.get(
        "finite_trace_contract"
    ) != _finite_trace_spec(model):
        issues.append("manifest finite-trace contract mismatch")
    return issues


def _load_manifest(path: Path) -> dict[str, Any]:
    value = _load_json_bytes(path.read_bytes(), "manifest JSON")
    if type(value) is not dict:
        raise KnowledgeQTableError("manifest must be a JSON object")
    return value


def verify_table(
    table: os.PathLike[str] | str,
    snapshot: Mapping[str, Any],
    required_decisions: Sequence[Mapping[str, Any]] | None = None,
    *,
    profile: str = "public",
    config: PlannerConfig | None = None,
    adapter: Any = None,
    utility: UtilityModel = DEFAULT_UTILITY_MODEL,
    manifest: os.PathLike[str] | str | None = None,
    chunk_size: int | None = None,
    progress: bool = False,
) -> dict[str, Any]:
    """Exhaustively replay every layer, state row, and action in chunks."""

    del progress
    if config is None:
        try:
            config = PROFILES[profile]
        except KeyError as exc:
            raise KnowledgeQTableError(f"unknown profile {profile!r}") from exc
    if chunk_size is not None:
        config = PlannerConfig(
            layers=config.layers,
            decisions=config.decisions,
            node_slots=config.node_slots,
            gamma=config.gamma,
            chunk_size=chunk_size,
            allow_explicit_padding=config.allow_explicit_padding,
            profile=config.profile,
        )
    model = compile_model(
        snapshot,
        required_decisions,
        config=config,
        adapter=adapter,
        utility=utility,
    )
    table_path = Path(table)
    mapped, header_issues = _inspect_table(table_path, model.config)
    result: dict[str, Any] = {
        "passed": False,
        "exhaustive": True,
        "shape": list(model.config.shape),
        "raw_data_bytes": model.config.raw_data_bytes,
        "replayed_layers": 0,
        "checked_values": 0,
        "mismatch_count": 0,
        "nonfinite_count": 0,
        "max_abs_bellman_error": None,
        "first_mismatch": None,
        "errors": list(header_issues),
        "provenance": dict(model.provenance),
        "finite_trace_gate": {
            "passed": False,
            "contract": _finite_trace_spec(model),
            "checked_policy_states": 0,
            "forbidden_choice_count": 0,
            "nonterminating_choice_count": 0,
            "bound_violation_count": 0,
            "resolution_nonterminal_count": 0,
            "maximum_observed_terminal_steps": 0,
        },
    }
    if mapped is None:
        return result
    table_sha256: str | None = None
    manifest_value: dict[str, Any] | None = None
    if manifest is not None:
        manifest_value = _load_manifest(Path(manifest))
        table_sha256 = file_sha256(table_path)
        result["errors"].extend(
            _manifest_issues(manifest_value, model, table_path, table_sha256)
        )
    previous_values: np.ndarray | None = None
    previous_terminates: np.ndarray | None = None
    previous_terminal_steps: np.ndarray | None = None
    max_error = 0.0
    trace_gate = result["finite_trace_gate"]
    for layer in range(model.config.layers):
        current_values = np.empty(model.config.state_count, dtype=np.dtype("<f4"))
        current_terminates = np.zeros(model.config.state_count, dtype=np.bool_)
        current_terminal_steps = np.zeros(model.config.state_count, dtype=np.int16)
        for start in range(0, model.config.state_count, model.config.chunk_size):
            end = min(model.config.state_count, start + model.config.chunk_size)
            expected = _q_chunk(model, layer, previous_values, start, end)
            actual = np.asarray(mapped[layer, start:end, :])
            result["checked_values"] += int(actual.size)
            finite = np.isfinite(actual)
            nonfinite = int(np.count_nonzero(~finite))
            result["nonfinite_count"] += nonfinite
            if nonfinite and result["first_mismatch"] is None:
                bad = np.argwhere(~finite)[0]
                state_index = start + int(bad[0])
                action_index = int(bad[1])
                result["first_mismatch"] = {
                    "layer": layer,
                    "state_index": state_index,
                    "action": ACTION_NAMES[action_index],
                    "reason": "nonfinite table value",
                }
            mismatch = (~finite) | (actual != expected)
            mismatch_count = int(np.count_nonzero(mismatch))
            result["mismatch_count"] += mismatch_count
            if mismatch_count and result["first_mismatch"] is None:
                bad = np.argwhere(mismatch)[0]
                state_index = start + int(bad[0])
                action_index = int(bad[1])
                ref = model.state_ref(state_index)
                result["first_mismatch"] = {
                    "layer": layer,
                    "state_index": state_index,
                    "decision_id": ref.decision_id,
                    "node_slot": ref.node_slot,
                    "evidence_mask": ref.evidence_mask,
                    "action": ACTION_NAMES[action_index],
                    "expected": float(expected[int(bad[0]), action_index]),
                    "actual": None
                    if not finite[int(bad[0]), action_index]
                    else float(actual[int(bad[0]), action_index]),
                    "reason": "Bellman value mismatch",
                }
            finite_mismatch = mismatch & finite
            if np.any(finite_mismatch):
                errors = np.abs(actual.astype(np.float64) - expected.astype(np.float64))
                max_error = max(max_error, float(np.max(errors[finite_mismatch])))
            safe_actual = np.where(finite, actual, FORBIDDEN_VALUE).astype(
                np.dtype("<f4"), copy=False
            )
            allowed = _effective_allowed(model, layer, start, end)
            choices, best = _first_argmax(safe_actual, allowed)
            current_values[start:end] = best
            local_rows = np.arange(end - start, dtype=np.int64)
            global_rows = np.arange(start, end, dtype=np.int64)
            trace_gate["checked_policy_states"] += end - start
            trace_gate["forbidden_choice_count"] += int(
                np.count_nonzero(~model.normative_allowed[global_rows, choices])
            )
            terminal_choice = choices >= RESOLVE_ACTION_INDEX
            current_terminates[start:end][terminal_choice] = True
            current_terminal_steps[start:end][terminal_choice] = 1
            resolution_choice = choices == RESOLVE_ACTION_INDEX
            # Resolution has no transition in this recurrence.  The explicit
            # counter remains visible so future recurrence edits cannot silently
            # weaken this gate.
            trace_gate["resolution_nonterminal_count"] += int(
                np.count_nonzero(resolution_choice & ~terminal_choice)
            )
            navigation_choice = choices < NAVIGATION_ACTION_COUNT
            if np.any(navigation_choice):
                if (
                    layer == 0
                    or previous_terminates is None
                    or previous_terminal_steps is None
                ):
                    trace_gate["nonterminating_choice_count"] += int(
                        np.count_nonzero(navigation_choice)
                    )
                else:
                    navigation_rows = local_rows[navigation_choice]
                    navigation_actions = choices[navigation_choice]
                    next_states = model.next_state_indices[
                        global_rows[navigation_choice], navigation_actions
                    ]
                    next_terminates = previous_terminates[next_states]
                    target_slice = current_terminates[start:end]
                    target_steps = current_terminal_steps[start:end]
                    target_slice[navigation_rows] = next_terminates
                    target_steps[navigation_rows] = previous_terminal_steps[
                        next_states
                    ] + np.int16(1)
                    trace_gate["nonterminating_choice_count"] += int(
                        np.count_nonzero(~next_terminates)
                    )
            local_steps = current_terminal_steps[start:end]
            trace_gate["bound_violation_count"] += int(
                np.count_nonzero(local_steps > np.int16(layer + 1))
            )
            if local_steps.size:
                trace_gate["maximum_observed_terminal_steps"] = max(
                    trace_gate["maximum_observed_terminal_steps"],
                    int(np.max(local_steps)),
                )
        previous_values = current_values
        previous_terminates = current_terminates
        previous_terminal_steps = current_terminal_steps
        result["replayed_layers"] += 1
    result["max_abs_bellman_error"] = max_error
    result["table_sha256"] = table_sha256
    trace_gate["passed"] = all(
        trace_gate[key] == 0
        for key in (
            "forbidden_choice_count",
            "nonterminating_choice_count",
            "bound_violation_count",
            "resolution_nonterminal_count",
        )
    )
    result["passed"] = (
        not result["errors"]
        and result["mismatch_count"] == 0
        and result["nonfinite_count"] == 0
        and trace_gate["passed"]
    )
    return result


verify_replay = verify_table


def _query_table(path: Path, config: PlannerConfig) -> np.memmap:
    table, issues = _inspect_table(path, config)
    if table is None:
        raise TableValidationError("; ".join(issues))
    return table


def query(
    table: os.PathLike[str] | str,
    snapshot: Mapping[str, Any],
    *,
    decision_id: str | None = None,
    decision_index: int | None = None,
    start_node_id: str | None = None,
    start_node_qid: str | None = None,
    start_qid: str | None = None,
    start_node_slot: int | None = None,
    evidence_mask: int = 0,
    layer: int | None = None,
    required_decisions: Sequence[Mapping[str, Any]] | None = None,
    profile: str = "public",
    config: PlannerConfig | None = None,
    adapter: Any = None,
    utility: UtilityModel = DEFAULT_UTILITY_MODEL,
    manifest: os.PathLike[str] | str | None = None,
    max_path: int | None = None,
) -> dict[str, Any]:
    """Return a bounded path/reason receipt for one initial state."""

    if config is None:
        try:
            config = PROFILES[profile]
        except KeyError as exc:
            raise KnowledgeQTableError(f"unknown profile {profile!r}") from exc
    model = compile_model(
        snapshot,
        required_decisions,
        config=config,
        adapter=adapter,
        utility=utility,
    )
    table_path = Path(table)
    mapped = _query_table(table_path, model.config)
    if type(evidence_mask) is not int or evidence_mask not in EVIDENCE_MASKS:
        raise KnowledgeQTableError(
            "evidence_mask must be one of the four two-bit masks"
        )
    if layer is None:
        layer = model.config.layers - 1
    if type(layer) is not int or not 0 <= layer < model.config.layers:
        raise KnowledgeQTableError("layer is outside the model")
    if max_path is None:
        max_path = layer + 1
    if type(max_path) is not int or not layer + 1 <= max_path <= model.config.layers:
        raise KnowledgeQTableError(
            "max_path must cover the selected finite horizon and remain bounded"
        )
    if start_qid is not None:
        if start_node_qid is not None:
            raise KnowledgeQTableError(
                "start_qid and start_node_qid are aliases; provide one"
            )
        start_node_qid = start_qid
    if start_node_qid is not None:
        if start_node_id is not None:
            raise KnowledgeQTableError(
                "legacy QID arguments and start_node_id are aliases; provide one"
            )
        start_node_id = start_node_qid
    if (decision_id is None) == (decision_index is None):
        raise KnowledgeQTableError(
            "provide exactly one of decision_id or decision_index"
        )
    if decision_index is None:
        if not _is_identifier(decision_id):
            raise KnowledgeQTableError("decision_id is invalid")
        matches = [
            index
            for index, decision in enumerate(model.decisions)
            if decision.decision_id == decision_id
        ]
        if len(matches) != 1:
            raise KnowledgeQTableError("unknown decision_id")
        decision_index = matches[0]
    elif (
        type(decision_index) is not int
        or not 0 <= decision_index < model.config.decisions
    ):
        raise KnowledgeQTableError("decision_index is outside the model")
    if (start_node_id is None) == (start_node_slot is None):
        raise KnowledgeQTableError(
            "provide exactly one of start_node_id or start_node_slot"
        )
    if start_node_id is not None:
        if (
            not _is_graph_identifier(start_node_id)
            or start_node_id not in model.node_slot_by_id
        ):
            raise KnowledgeQTableError("start_node_id is unknown")
        start_node_slot = model.node_slot_by_id[start_node_id]
    elif (
        type(start_node_slot) is not int
        or not 0 <= start_node_slot < model.config.node_slots
    ):
        raise KnowledgeQTableError("start_node_slot is outside the model")

    state_index = model.state_index(decision_index, start_node_slot, evidence_mask)
    current_layer = layer
    path: list[dict[str, Any]] = []
    evidence_traversed: list[dict[str, Any]] = []
    selected_rule_ids: set[str] = set()
    selected_deontic_statuses: set[str] = set()
    terminal: dict[str, Any] | None = None
    while terminal is None:
        row = np.asarray(mapped[current_layer, state_index, :], dtype=np.dtype("<f4"))
        if not np.all(np.isfinite(row)):
            raise TableValidationError("query encountered a non-finite table row")
        allowed = _effective_allowed(model, current_layer, state_index, state_index + 1)
        choice_array, _ = _first_argmax(row.reshape(1, MAX_ACTIONS), allowed)
        action_index = int(choice_array[0])
        if not model.normative_allowed[state_index, action_index]:
            raise TableValidationError(
                "query selected an action forbidden by the normative mask"
            )
        ref = model.state_ref(state_index)
        rule_ids = model.rule_ids[state_index][action_index]
        selected_rule_ids.update(rule_ids)
        selected_deontic_statuses.add(model.deontic_statuses[state_index])
        step: dict[str, Any] = {
            "step": len(path),
            "layer": current_layer,
            "state_index": state_index,
            "decision_id": ref.decision_id,
            "node_slot": ref.node_slot,
            "node_id": ref.node_id,
            "evidence_mask": ref.evidence_mask,
            "required_evidence_bits": ref.required_evidence_bits,
            "action": ACTION_NAMES[action_index],
            "value": float(row[action_index]),
            "action_values": {
                ACTION_NAMES[index]: float(row[index]) for index in range(MAX_ACTIONS)
            },
            "deontic_reason_ids": list(rule_ids),
            "deontic_status": model.deontic_statuses[state_index],
            "deontic_obligatory": bool(
                model.deontic_obligatory_masks[state_index] & (1 << action_index)
            ),
        }
        path.append(step)
        if action_index == RESOLVE_ACTION_INDEX:
            decision = model.decisions[decision_index]
            alternative = decision.resolution_alternatives[0]
            terminal = {
                "kind": "resolution",
                "alternative_id": alternative["id"],
                "alternative_label": alternative["label"],
                "alternatives_considered": [
                    dict(item) for item in decision.resolution_alternatives
                ],
                "required_evidence_bits": decision.required_evidence_bits,
            }
        elif action_index == ABSTAIN_ACTION_INDEX:
            decision = model.decisions[decision_index]
            terminal = {
                "kind": "abstain_or_escalate",
                "alternative_id": decision.abstain_or_escalate["id"],
                "alternative_label": decision.abstain_or_escalate["label"],
                "review_triggers": list(decision.review_triggers),
            }
        else:
            slot = model.navigation[ref.node_slot][action_index]
            if slot is None or not model.nav_valid[state_index, action_index]:
                raise KnowledgeQTableError(
                    "table selected an unavailable navigation action"
                )
            next_state = int(model.next_state_indices[state_index, action_index])
            next_ref = model.state_ref(next_state)
            evidence_record = {
                "step": len(path) - 1,
                "action_slot": action_index,
                "source_id": slot.source_id,
                "target_id": slot.target_id,
                "relation": slot.relation,
                "relation_source_id": slot.relation_source_id,
                "relation_target_id": slot.relation_target_id,
                "source_direction": slot.source_direction,
                "browse_direction": slot.browse_direction,
                "evidence_bits": slot.evidence_bits,
                "evidence_mask_before": ref.evidence_mask,
                "evidence_mask_after": next_ref.evidence_mask,
            }
            evidence_traversed.append(evidence_record)
            step["navigation"] = evidence_record
            current_layer -= 1
            state_index = next_state
            if current_layer < 0 or len(path) >= max_path:
                raise KnowledgeQTableError(
                    "bounded query path ended before a terminal action"
                )
    table_sha = file_sha256(table_path)
    if manifest is not None:
        manifest_value = _load_manifest(Path(manifest))
        issues = _manifest_issues(manifest_value, model, table_path, table_sha)
        if issues:
            raise TableValidationError("; ".join(issues))
    decision = model.decisions[decision_index]
    return {
        "schema": RECEIPT_SCHEMA,
        "query": {
            "decision_id": decision.decision_id,
            "decision_index": decision_index,
            "initial_node_slot": model.state_ref(
                model.state_index(decision_index, start_node_slot, evidence_mask)
            ).node_slot,
            "initial_node_id": model.node_ids[start_node_slot]
            if start_node_slot < model.actual_node_count
            else None,
            "initial_evidence_mask": evidence_mask,
            "initial_layer": layer,
            "max_path": max_path,
        },
        "chosen_action": path[0]["action"],
        "chosen_value": path[0]["value"],
        "path": path,
        "evidence_traversed": evidence_traversed,
        "terminal": terminal,
        "deontic_reason_ids": sorted(selected_rule_ids),
        "deontic_statuses": sorted(selected_deontic_statuses),
        "decision_obligation_rule_ids": list(decision.obligation_rule_ids),
        "decision_provenance_refs": list(decision.provenance_refs),
        "reason": "The receipt follows remaining-step finite-horizon choices. Graph links are discovery references, while the external deontic mask constrains actions without proving facts.",
        "finite_trace_gate": {
            "passed": terminal is not None and len(path) <= layer + 1,
            "always_no_forbidden_action": True,
            "terminal_within_declared_bound": len(path) <= layer + 1,
            "resolution_is_terminal": terminal["kind"] != "resolution"
            or path[-1]["action"] == "resolve",
            "observed_steps": len(path),
            "declared_bound": layer + 1,
            "horizon_semantics": "remaining_decision_steps_not_chronological_time",
        },
        "provenance": {
            **dict(model.provenance),
            "table_sha256": table_sha,
        },
    }


query_table = query


def _cli_config(args: argparse.Namespace) -> PlannerConfig:
    if args.profile in PROFILES:
        return PROFILES[args.profile]
    return fixture_config(
        layers=args.layers,
        decisions=args.decisions_count,
        node_slots=args.node_slots,
        chunk_size=args.chunk_size,
        allow_explicit_padding=True,
    )


def _cli_adapter(args: argparse.Namespace) -> Any:
    if args.evidence_deontic:
        required_values = {
            "--deontic-logic-semantics": args.deontic_logic_semantics,
            "--deontic-logic-semantics-sha256": (args.deontic_logic_semantics_sha256),
            "--deontic-profile": args.deontic_profile,
            "--deontic-profile-sha256": args.deontic_profile_sha256,
        }
        missing = [name for name, value in required_values.items() if not value]
        if missing:
            raise DeonticAdapterError(
                "--evidence-deontic requires explicit identifiers and content hashes; "
                f"missing {', '.join(missing)}"
            )
        supplied_hashes = args.esso_evidence_hashes or []
        hashes: dict[str, str] = {}
        for item in supplied_hashes:
            if type(item) is not str or item.count("=") != 1:
                raise DeonticAdapterError(
                    "each --esso-evidence-hash must be NAME=SHA256"
                )
            name, digest = item.split("=", 1)
            if name in hashes:
                raise DeonticAdapterError(
                    f"duplicate --esso-evidence-hash name {name!r}"
                )
            hashes[name] = digest
        return EvidenceCompletionDeonticAdapter(
            logic_semantics=args.deontic_logic_semantics,
            logic_semantics_sha256=args.deontic_logic_semantics_sha256,
            profile=args.deontic_profile,
            profile_sha256=args.deontic_profile_sha256,
            esso_evidence_hashes=hashes,
        )
    if args.fixture_deontic:
        if any(
            item
            for item in (
                args.deontic_logic_semantics,
                args.deontic_logic_semantics_sha256,
                args.deontic_profile,
                args.deontic_profile_sha256,
                args.esso_evidence_hashes,
            )
        ):
            raise DeonticAdapterError(
                "fixture deontic mode cannot receive evidence provenance arguments"
            )
        return FixtureDeonticAdapter()
    raise DeonticAdapterError(
        "CLI requires an explicit --fixture-deontic or --evidence-deontic adapter"
    )


def _build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--snapshot", type=Path, required=True)
    common.add_argument("--decisions", dest="decisions_path", type=Path)
    common.add_argument(
        "--profile", choices=["public", "full", "fixture"], default="public"
    )
    deontic_group = common.add_mutually_exclusive_group(required=True)
    deontic_group.add_argument("--fixture-deontic", action="store_true")
    deontic_group.add_argument("--evidence-deontic", action="store_true")
    common.add_argument("--deontic-logic-semantics")
    common.add_argument(
        "--deontic-logic-semantics-sha256",
        "--deontic-logic-sha256",
        dest="deontic_logic_semantics_sha256",
        metavar="SHA256",
    )
    common.add_argument("--deontic-profile")
    common.add_argument("--deontic-profile-sha256", metavar="SHA256")
    common.add_argument(
        "--esso-evidence-hash",
        dest="esso_evidence_hashes",
        action="append",
        metavar="NAME=SHA256",
    )
    common.add_argument("--layers", type=int, default=8)
    common.add_argument("--decisions-count", type=int, default=2)
    common.add_argument("--node-slots", type=int, default=4)
    common.add_argument("--chunk-size", type=int, default=8)
    build = subparsers.add_parser(
        "build", parents=[common], help="build a memmapped Q table"
    )
    build.add_argument("--output", type=Path, required=True)
    build.add_argument("--manifest", type=Path, required=True)
    verify = subparsers.add_parser(
        "verify", parents=[common], help="exhaustively replay a Q table"
    )
    verify.add_argument("--table", type=Path, required=True)
    verify.add_argument("--manifest", type=Path)
    verify.add_argument(
        "--report",
        type=Path,
        help="write the canonical exhaustive-verification result as JSON",
    )
    query_parser = subparsers.add_parser(
        "query", parents=[common], help="emit a bounded reason receipt"
    )
    query_parser.add_argument("--table", type=Path, required=True)
    query_parser.add_argument("--manifest", type=Path)
    query_parser.add_argument("--decision-id")
    query_parser.add_argument("--decision-index", type=int)
    query_parser.add_argument("--node-id")
    query_parser.add_argument("--node-qid", help=argparse.SUPPRESS)
    query_parser.add_argument("--node-slot", type=int)
    query_parser.add_argument("--evidence-mask", type=int, default=0)
    query_parser.add_argument("--layer", type=int)
    query_parser.add_argument(
        "--receipt",
        type=Path,
        help="write the canonical bounded reason receipt as JSON",
    )
    return parser


def _main(argv: Sequence[str]) -> int:
    parser = _build_cli_parser()
    args = parser.parse_args(argv)
    try:
        snapshot = load_snapshot(args.snapshot)
        decisions = (
            load_required_decisions(args.decisions_path)
            if args.decisions_path
            else None
        )
        config = _cli_config(args)
        adapter = _cli_adapter(args)
        if args.command == "build":
            value = generate_table(
                args.output,
                snapshot,
                decisions,
                config=config,
                adapter=adapter,
                manifest=args.manifest,
            )
        elif args.command == "verify":
            value = verify_table(
                args.table,
                snapshot,
                decisions,
                config=config,
                adapter=adapter,
                manifest=args.manifest,
            )
        else:
            value = query(
                args.table,
                snapshot,
                decision_id=args.decision_id,
                decision_index=args.decision_index,
                start_node_id=args.node_id,
                start_node_qid=args.node_qid,
                start_node_slot=args.node_slot,
                evidence_mask=args.evidence_mask,
                layer=args.layer,
                required_decisions=decisions,
                config=config,
                adapter=adapter,
                manifest=args.manifest,
            )
        if args.command == "verify" and args.report is not None:
            _write_canonical_json(args.report, value)
        if args.command == "query" and args.receipt is not None:
            _write_canonical_json(args.receipt, value)
        sys.stdout.write(canonical_json_bytes(value).decode("utf-8"))
        return 0 if value.get("passed", True) else 1
    except KnowledgeQTableError as exc:
        sys.stderr.write(f"knowledge_q_table: {exc}\n")
        return 2


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
