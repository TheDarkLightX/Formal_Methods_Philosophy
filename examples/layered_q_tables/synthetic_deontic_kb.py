"""Build a deterministic, non-authoritative synthetic deontic problem bank.

The corpus is a falsification and training fixture.  It is not law, ethics,
world truth, or permission to perform an external effect.  Luna-Max proposed
the semantic axes and seed families; this module only expands the frozen
template bank.  A separate module, ``synthetic_deontic_oracle.py``, owns the
release verdict and deliberately does not import this generator.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import platform
import sys
import zlib
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

TEMPLATE_SCHEMA = "synthetic-deontic-template-bank-v1"
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
NONCLAIMS = (
    "not_complete_deontic_logic",
    "not_ethics",
    "not_external_authority",
    "not_law",
    "not_population_frequency",
    "not_world_truth",
)


class SyntheticDeonticError(ValueError):
    """A deterministic generator or template-bank rejection."""


class _DuplicateKeyError(ValueError):
    pass


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKeyError(key)
        result[key] = value
    return result


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="ascii"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=lambda token: (_ for _ in ()).throw(
                SyntheticDeonticError(f"non-finite JSON token {token}")
            ),
        )
    except (OSError, UnicodeError, json.JSONDecodeError, _DuplicateKeyError) as exc:
        raise SyntheticDeonticError(f"invalid template bank: {exc}") from exc
    if type(value) is not dict:
        raise SyntheticDeonticError("template bank must be an object")
    return value


def _require_keys(value: Mapping[str, object], keys: set[str], path: str) -> None:
    actual = set(value)
    if actual != keys:
        raise SyntheticDeonticError(
            f"{path} fields mismatch: missing={sorted(keys-actual)} "
            f"extra={sorted(actual-keys)}"
        )


def load_template_bank(path: Path) -> dict[str, Any]:
    bank = _load_json(path)
    _require_keys(
        bank,
        {
            "schema",
            "profile_id",
            "authoritative_status",
            "generation_method",
            "factorization",
            "nonclaims",
            "axes",
            "domains",
            "norm_graphs",
        },
        "template_bank",
    )
    if bank["schema"] != TEMPLATE_SCHEMA or bank["profile_id"] != PROFILE_ID:
        raise SyntheticDeonticError("template schema or profile mismatch")
    if bank["authoritative_status"] != "synthetic_non_authoritative":
        raise SyntheticDeonticError("template authority boundary mismatch")
    factorization = bank["factorization"]
    if type(factorization) is not dict:
        raise SyntheticDeonticError("factorization must be an object")
    if factorization.get("record_count") != EXPECTED_RECORD_COUNT:
        raise SyntheticDeonticError("factorization record count mismatch")
    if factorization.get("ordinal_order") != list(AXIS_NAMES):
        raise SyntheticDeonticError("factorization ordinal order mismatch")
    domains = bank["domains"]
    graphs = bank["norm_graphs"]
    axes = bank["axes"]
    if type(domains) is not list or len(domains) != AXIS_SIZES[0]:
        raise SyntheticDeonticError("exactly eight domain seeds are required")
    if type(graphs) is not list or len(graphs) != AXIS_SIZES[1]:
        raise SyntheticDeonticError("exactly eight norm-graph seeds are required")
    if type(axes) is not dict:
        raise SyntheticDeonticError("axes must be an object")
    expected_axis_lengths = dict(zip(AXIS_NAMES[2:], AXIS_SIZES[2:]))
    if set(axes) != set(expected_axis_lengths):
        raise SyntheticDeonticError("axis names mismatch")
    for name, size in expected_axis_lengths.items():
        values = axes[name]
        if type(values) is not list or len(values) != size:
            raise SyntheticDeonticError(f"axis {name} must contain {size} values")
        if any(type(item) is not str for item in values) or len(set(values)) != size:
            raise SyntheticDeonticError(f"axis {name} values must be unique strings")
    for collection_name, rows in (("domains", domains), ("norm_graphs", graphs)):
        identifiers = [row.get("id") for row in rows if type(row) is dict]
        if len(identifiers) != len(rows) or any(type(item) is not str for item in identifiers):
            raise SyntheticDeonticError(f"{collection_name} need string IDs")
        if len(set(identifiers)) != len(identifiers):
            raise SyntheticDeonticError(f"duplicate {collection_name} ID")
    if sorted(bank["nonclaims"]) != list(NONCLAIMS):
        raise SyntheticDeonticError("template nonclaims mismatch")
    return bank


def unrank_ordinal(ordinal: int) -> tuple[int, int, int, int, int, int, int]:
    if type(ordinal) is not int or not 0 <= ordinal < EXPECTED_RECORD_COUNT:
        raise SyntheticDeonticError("ordinal must be an integer in [0, 65535]")
    remainder = ordinal
    reversed_coordinates: list[int] = []
    for size in reversed(AXIS_SIZES[1:]):
        remainder, coordinate = divmod(remainder, size)
        reversed_coordinates.append(coordinate)
    coordinates = [remainder, *reversed(reversed_coordinates)]
    if len(coordinates) != len(AXIS_SIZES):
        raise AssertionError("internal coordinate arity mismatch")
    return tuple(coordinates)  # type: ignore[return-value]


def rank_coordinate(coordinate: Sequence[int]) -> int:
    if len(coordinate) != len(AXIS_SIZES):
        raise SyntheticDeonticError("coordinate arity mismatch")
    result = 0
    for value, size in zip(coordinate, AXIS_SIZES):
        if type(value) is not int or not 0 <= value < size:
            raise SyntheticDeonticError("coordinate component out of range")
        result = result * size + value
    return result


def _axis_values(bank: Mapping[str, Any], coordinate: Sequence[int]) -> dict[str, str]:
    return {
        "domain": bank["domains"][coordinate[0]]["id"],
        "norm_graph": bank["norm_graphs"][coordinate[1]]["id"],
        **{
            name: bank["axes"][name][coordinate[index]]
            for index, name in enumerate(AXIS_NAMES[2:], 2)
        },
    }


def _clock(time_mode: str) -> dict[str, object]:
    values: dict[str, tuple[int, int, str, str]] = {
        "atemporal": (0, 0, "not_applicable", "T"),
        "before_window": (0, 2, "unperformed", "T"),
        "at_deadline_unperformed": (2, 2, "unperformed", "T"),
        "at_deadline_performed": (2, 2, "performed", "T"),
        "after_deadline_unperformed": (3, 2, "unperformed", "T"),
        "after_deadline_performed": (3, 2, "performed", "T"),
        "unknown_clock": (0, 2, "unknown", "U"),
        "contradictory_clock": (2, 2, "both", "B"),
    }
    try:
        now_tick, deadline_tick, performance, observation_truth = values[time_mode]
    except KeyError as exc:
        raise SyntheticDeonticError(f"unknown time mode {time_mode}") from exc
    return {
        "id": "clock0",
        "mode": time_mode,
        "now_tick": now_tick,
        "deadline_tick": deadline_tick,
        "performance": performance,
        "observation_truth": observation_truth,
    }


def _truth_code(premise_truth: str) -> str:
    return {"true": "T", "false": "F", "unknown": "U", "both": "B"}[
        premise_truth
    ]


def _exception_truth(exception_mode: str) -> str:
    return {
        "absent": "F",
        "supported_true": "T",
        "supported_false": "F",
        "unknown_support": "U",
    }[exception_mode]


def _performance_truth(clock: Mapping[str, object]) -> str:
    return {
        "performed": "T",
        "unperformed": "F",
        "unknown": "U",
        "both": "B",
        "not_applicable": "U",
    }[str(clock["performance"])]


def _priority_values(mode: str, norm_count: int) -> tuple[list[int], list[list[str]]]:
    if mode == "equal_rank":
        return [1] * norm_count, []
    if mode == "n0_gt_n1":
        priorities = [2, 1, *([2] if norm_count == 3 else [])]
        edges = [["norm_n0", "norm_n1"]]
        if norm_count == 3:
            edges.append(["norm_n2", "norm_n1"])
        return priorities, edges
    if mode == "n1_gt_n0":
        priorities = [1, 2, *([1] if norm_count == 3 else [])]
        edges = [["norm_n1", "norm_n0"]]
        if norm_count == 3:
            edges.append(["norm_n1", "norm_n2"])
        return priorities, edges
    if mode == "cyclic_priority":
        edges = [["norm_n0", "norm_n1"], ["norm_n1", "norm_n0"]]
        if norm_count == 3:
            edges.extend([["norm_n1", "norm_n2"], ["norm_n2", "norm_n1"]])
        return [1] * norm_count, edges
    raise SyntheticDeonticError(f"unknown priority mode {mode}")


def _world(domain: Mapping[str, Any], axis: Mapping[str, str]) -> dict[str, object]:
    actor_ids = list(domain["actors"])
    action_rows = []
    action_by_role: dict[str, str] = {}
    for role, raw in sorted(domain["actions"].items()):
        action_id, actor_id, kind = raw
        action_by_role[role] = action_id
        action_rows.append(
            {"role": role, "id": action_id, "actor_id": actor_id, "kind": kind}
        )
    relation_kind, source_role, target_role = domain["relation"]
    clock = _clock(axis["time"])
    facts = [
        {
            "id": "fact_premise",
            "predicate": domain["premise_predicate"],
            "args": [actor_ids[0]],
            "truth": _truth_code(axis["premise_truth"]),
            "evidence_id": "synthetic_evidence_premise",
        },
        {
            "id": "fact_exception",
            "predicate": "exception_supported",
            "args": [actor_ids[1]],
            "truth": _exception_truth(axis["exception"]),
            "evidence_id": "synthetic_evidence_exception",
        },
        {
            "id": "fact_primary_performed",
            "predicate": "primary_action_performed",
            "args": [action_by_role["primary"]],
            "truth": _performance_truth(clock),
            "evidence_id": "synthetic_evidence_clock",
        },
    ]
    return {
        "domain_id": domain["id"],
        "actors": sorted(actor_ids),
        "actions": sorted(action_rows, key=lambda row: row["id"]),
        "relations": [
            {
                "id": "relation_domain",
                "kind": relation_kind,
                "source_action_id": action_by_role[source_role],
                "target_action_id": action_by_role[target_role],
            }
        ],
        "facts": sorted(facts, key=lambda row: row["id"]),
        "clock": clock,
    }


def _norms(
    graph: Mapping[str, Any],
    world: Mapping[str, Any],
    axis: Mapping[str, str],
) -> tuple[list[dict[str, object]], list[list[str]], list[list[str]]]:
    action_by_role = {row["role"]: row["id"] for row in world["actions"]}
    actor_by_role = {row["role"]: row["actor_id"] for row in world["actions"]}
    priorities, priority_edges = _priority_values(
        axis["priority"], len(graph["norms"])
    )
    result: list[dict[str, object]] = []
    for index, raw in enumerate(graph["norms"]):
        local_id, operator, action_role, condition, temporal, repair = raw
        norm_id = f"norm_{local_id}"
        if condition == "premise":
            condition_value: dict[str, str] = {
                "kind": "fact",
                "fact_id": "fact_premise",
            }
        elif condition.startswith("violation:"):
            condition_value = {
                "kind": "violation",
                "norm_id": f"norm_{condition.split(':', 1)[1]}",
            }
        else:
            raise SyntheticDeonticError(f"unsupported condition {condition}")
        temporal_value: dict[str, str] = (
            {"kind": "atemporal"}
            if temporal == "atemporal"
            else {"kind": "deadline", "clock_id": "clock0"}
        )
        repair_value: dict[str, str] = (
            {"kind": "none"}
            if repair == "none"
            else {
                "kind": "ctd",
                "primary_norm_id": f"norm_{repair.split(':', 1)[1]}",
            }
        )
        exception_value: dict[str, str] = (
            {"kind": "none"}
            if index != 1 or axis["exception"] == "absent"
            else {"kind": "unless", "fact_id": "fact_exception"}
        )
        result.append(
            {
                "id": norm_id,
                "operator": operator,
                "subject_id": actor_by_role[action_role],
                "action_id": action_by_role[action_role],
                "condition": condition_value,
                "temporal": temporal_value,
                "priority": priorities[index],
                "exception": exception_value,
                "repair": repair_value,
                "revision": {
                    "number": 1,
                    "status": axis["revision"] if index == 0 else "active",
                },
            }
        )
    conflicts = [
        [f"norm_{left}", f"norm_{right}", kind]
        for left, right, kind in graph["conflicts"]
    ]
    return sorted(result, key=lambda row: row["id"]), sorted(conflicts), sorted(priority_edges)


def _condition_truth(norm: Mapping[str, Any], facts: Mapping[str, str], violated: set[str]) -> str:
    condition = norm["condition"]
    if condition["kind"] == "fact":
        return facts[condition["fact_id"]]
    if condition["kind"] == "violation":
        return "T" if condition["norm_id"] in violated else "F"
    raise SyntheticDeonticError("unknown condition kind")


def _priority_reachable(edges: set[tuple[str, str]], source: str, target: str) -> bool:
    frontier = [source]
    seen: set[str] = set()
    while frontier:
        current = frontier.pop()
        if current == target:
            return True
        if current in seen:
            continue
        seen.add(current)
        frontier.extend(right for left, right in edges if left == current)
    return False


def _candidate_result(core: Mapping[str, Any]) -> dict[str, object]:
    facts = {row["id"]: row["truth"] for row in core["world"]["facts"]}
    clock = core["world"]["clock"]
    active: set[str] = set()
    defeated: set[str] = set()
    satisfied: set[str] = set()
    violated: set[str] = set()
    activated_ctd: set[str] = set()
    reasons: set[str] = set()
    norms = {row["id"]: row for row in core["norms"]}

    def preliminarily_activate(norm: Mapping[str, Any]) -> bool:
        norm_id = norm["id"]
        if norm["revision"]["status"] == "revoked":
            defeated.add(norm_id)
            reasons.add("revoked_norm_ignored")
            return False
        truth = _condition_truth(norm, facts, violated)
        if truth == "F":
            defeated.add(norm_id)
            return False
        if truth == "U":
            reasons.add("unknown_norm_condition")
            return False
        if truth == "B":
            reasons.add("inconsistent_norm_condition")
            return False
        exception = norm["exception"]
        if exception["kind"] == "unless":
            exception_truth = facts[exception["fact_id"]]
            if exception_truth == "T":
                defeated.add(norm_id)
                reasons.add("supported_exception_defeats_norm")
                return False
            if exception_truth == "U":
                reasons.add("unknown_exception_support")
                return False
            if exception_truth == "B":
                reasons.add("inconsistent_exception_support")
                return False
        temporal = norm["temporal"]
        if temporal["kind"] == "deadline":
            observation = clock["observation_truth"]
            if observation == "U":
                reasons.add("unknown_clock")
                return False
            if observation == "B":
                reasons.add("contradictory_clock")
                return False
            now_tick = clock["now_tick"]
            deadline_tick = clock["deadline_tick"]
            performed = facts["fact_primary_performed"]
            if performed == "T" and now_tick >= deadline_tick:
                satisfied.add(norm_id)
                reasons.add("deadline_obligation_satisfied")
                return False
            if performed == "F" and now_tick >= deadline_tick and norm["operator"] == "O":
                violated.add(norm_id)
                reasons.add("deadline_obligation_violated")
        active.add(norm_id)
        if norm["repair"]["kind"] == "ctd":
            activated_ctd.add(norm_id)
            reasons.add("ctd_repair_activated")
        return True

    for norm_id in sorted(norms):
        if norms[norm_id]["condition"]["kind"] == "fact":
            preliminarily_activate(norms[norm_id])
    for norm_id in sorted(norms):
        if norms[norm_id]["condition"]["kind"] == "violation":
            preliminarily_activate(norms[norm_id])

    edges = {tuple(edge) for edge in core["priority_edges"]}
    for left, right, _kind in core["norm_conflicts"]:
        if left not in active or right not in active:
            continue
        left_wins = _priority_reachable(edges, left, right)
        right_wins = _priority_reachable(edges, right, left)
        if left_wins and not right_wins:
            active.remove(right)
            defeated.add(right)
            reasons.add("priority_defeat")
        elif right_wins and not left_wins:
            active.remove(left)
            defeated.add(left)
            reasons.add("priority_defeat")
        else:
            reasons.add("unresolved_norm_conflict")

    required = {
        norms[norm_id]["action_id"]
        for norm_id in active
        if norms[norm_id]["operator"] == "O"
    }
    forbidden = {
        norms[norm_id]["action_id"]
        for norm_id in active
        if norms[norm_id]["operator"] == "F"
    }
    permitted = {
        norms[norm_id]["action_id"]
        for norm_id in active
        if norms[norm_id]["operator"] == "P"
    } | required
    if required & forbidden or permitted & forbidden:
        reasons.add("unresolved_modal_conflict")
    if len(required) > 1:
        reasons.add("multiple_exclusive_obligations")
    unresolved_codes = {
        code
        for code in reasons
        if code
        in {
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
    }
    if unresolved_codes:
        status = "unresolved"
        fallback = "escalate"
    elif required or permitted - forbidden:
        status = "resolved"
        fallback = "none"
    else:
        status = "unresolved"
        fallback = "abstain"
        reasons.add("no_positive_norm")
    return {
        "status": status,
        "required_action_ids": sorted(required),
        "forbidden_action_ids": sorted(forbidden),
        "permitted_action_ids": sorted(permitted - forbidden),
        "active_norm_ids": sorted(active),
        "defeated_norm_ids": sorted(defeated),
        "satisfied_norm_ids": sorted(satisfied),
        "violated_norm_ids": sorted(violated),
        "activated_ctd_norm_ids": sorted(activated_ctd),
        "fallback": fallback,
        "reason_codes": sorted(reasons),
    }


def _kernel_projection(axis: Mapping[str, str], graph: Mapping[str, Any]) -> dict[str, object]:
    reasons: list[str] = []
    if graph["compatibility"] != "kernel_projection":
        reasons.append("ctd_or_deadline_semantics_unsupported")
    if axis["priority"] != "equal_rank":
        reasons.append("priority_semantics_metadata_only")
    if axis["exception"] != "absent":
        reasons.append("exception_semantics_metadata_only")
    if axis["revision"] != "active":
        reasons.append("revision_semantics_unsupported")
    if axis["premise_truth"] == "both":
        reasons.append("four_valued_inconsistency_unsupported")
    return {
        "status": "exact_supported" if not reasons else "unsupported_quarantine",
        "reason_codes": reasons or ["bounded_kernel_projection_available"],
    }


def _counterfactuals(axis: Mapping[str, str]) -> list[dict[str, str]]:
    return [
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
    ]


def generate_record(bank: Mapping[str, Any], ordinal: int) -> dict[str, object]:
    coordinate = unrank_ordinal(ordinal)
    axis = _axis_values(bank, coordinate)
    domain = bank["domains"][coordinate[0]]
    graph = bank["norm_graphs"][coordinate[1]]
    world = _world(domain, axis)
    norms, conflicts, priority_edges = _norms(graph, world, axis)
    action_ids = sorted(row["id"] for row in world["actions"])
    core = {
        "profile_id": PROFILE_ID,
        "world": world,
        "norms": norms,
        "norm_conflicts": conflicts,
        "priority_edges": priority_edges,
        "query": {
            "decision_id": f"decision_{domain['id']}_{graph['id']}",
            "alternatives": action_ids,
            "omission_admissible": False,
            "fallback": "abstain_or_escalate",
        },
    }
    signature = sha256_bytes(canonical_json_bytes(core))
    candidate = _candidate_result(core)
    eligible = set(candidate["required_action_ids"]) | set(candidate["permitted_action_ids"])
    negative = {
        "rejected_action_ids": sorted(set(action_ids) - eligible),
        "unresolved_codes": sorted(
            code
            for code in candidate["reason_codes"]
            if "unknown" in code
            or "inconsistent" in code
            or "unresolved" in code
            or "multiple" in code
        ),
        "counterfactuals": _counterfactuals(axis),
    }
    profile_hash = sha256_bytes(canonical_json_bytes(bank))
    record_without_hash: dict[str, object] = {
        "schema": RECORD_SCHEMA,
        "ordinal": ordinal,
        "coordinate_id": f"sdkv0-{ordinal:04x}",
        "coordinate": axis,
        "stable_id": f"sdk1-{signature}",
        "semantic_signature_sha256": signature,
        "generator_profile_sha256": profile_hash,
        "authority": {
            "status": "synthetic_non_authoritative",
            "source_kind": "generated_fixture",
            "issuer_id": "none",
            "jurisdiction_id": "none",
            "truth_status": "not_asserted",
            "may_authorize_external_effects": False,
            "may_be_cited_as_law": False,
        },
        "semantic_core": core,
        "generator_candidate_result": candidate,
        "negative_knowledge": negative,
        "kernel_v1_projection": _kernel_projection(axis, graph),
        "nonclaims": list(NONCLAIMS),
    }
    record_hash = sha256_bytes(canonical_json_bytes(record_without_hash))
    return {**record_without_hash, "record_sha256": record_hash}


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(canonical_json_bytes(value))
    os.replace(temporary, path)


def build_corpus(
    template_bank_path: Path,
    output_dir: Path,
    manifest_path: Path,
) -> dict[str, object]:
    bank = load_template_bank(template_bank_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    temporary_paths = {
        prefix: output_dir / f"part-{prefix}.jsonl.gz.tmp"
        for prefix in SHARD_PREFIXES
    }
    final_paths = {
        prefix: output_dir / f"part-{prefix}.jsonl.gz"
        for prefix in SHARD_PREFIXES
    }
    raw_handles: dict[str, Any] = {}
    gzip_handles: dict[str, gzip.GzipFile] = {}
    shard_hashers = {prefix: hashlib.sha256() for prefix in SHARD_PREFIXES}
    shard_counts = Counter()
    shard_bytes = Counter()
    coverage = {name: Counter() for name in AXIS_NAMES}
    signatures: set[str] = set()
    record_ids: set[str] = set()
    root_rows: list[list[object]] = []
    try:
        for prefix in SHARD_PREFIXES:
            raw = temporary_paths[prefix].open("wb")
            raw_handles[prefix] = raw
            gzip_handles[prefix] = gzip.GzipFile(
                filename="",
                mode="wb",
                compresslevel=9,
                fileobj=raw,
                mtime=0,
            )
        for ordinal in range(EXPECTED_RECORD_COUNT):
            record = generate_record(bank, ordinal)
            signature = str(record["semantic_signature_sha256"])
            record_id = str(record["stable_id"])
            if signature in signatures or record_id in record_ids:
                raise SyntheticDeonticError("duplicate semantic signature or stable ID")
            signatures.add(signature)
            record_ids.add(record_id)
            payload = canonical_json_bytes(record) + b"\n"
            prefix = signature[0]
            gzip_handles[prefix].write(payload)
            shard_hashers[prefix].update(payload)
            shard_counts[prefix] += 1
            shard_bytes[prefix] += len(payload)
            for name in AXIS_NAMES:
                coverage[name][record["coordinate"][name]] += 1
            root_rows.append([ordinal, record["record_sha256"]])
    finally:
        for handle in gzip_handles.values():
            handle.close()
        for handle in raw_handles.values():
            if not handle.closed:
                handle.close()
    for prefix in SHARD_PREFIXES:
        os.replace(temporary_paths[prefix], final_paths[prefix])
    if len(signatures) != EXPECTED_RECORD_COUNT:
        raise SyntheticDeonticError("corpus signature count mismatch")
    corpus_root = sha256_bytes(canonical_json_bytes(root_rows))
    semantic_set_root = sha256_bytes(
        b"".join(bytes.fromhex(signature) for signature in sorted(signatures))
    )
    shards = []
    for prefix in SHARD_PREFIXES:
        path = final_paths[prefix]
        shards.append(
            {
                "prefix": prefix,
                "file": path.name,
                "records": shard_counts[prefix],
                "uncompressed_bytes": shard_bytes[prefix],
                "uncompressed_sha256": shard_hashers[prefix].hexdigest(),
                "compressed_bytes": path.stat().st_size,
                "compressed_sha256": file_sha256(path),
            }
        )
    manifest: dict[str, object] = {
        "schema": MANIFEST_SCHEMA,
        "status": "generation_only_pending_independent_oracle",
        "authoritative_status": "synthetic_non_authoritative",
        "record_schema": RECORD_SCHEMA,
        "record_count": EXPECTED_RECORD_COUNT,
        "factorization": {
            "axis_names": list(AXIS_NAMES),
            "axis_sizes": list(AXIS_SIZES),
            "product": EXPECTED_RECORD_COUNT,
        },
        "hashes": {
            "template_bank_sha256": file_sha256(template_bank_path),
            "generator_source_sha256": file_sha256(Path(__file__)),
            "generator_profile_sha256": sha256_bytes(canonical_json_bytes(bank)),
            "corpus_root_sha256": corpus_root,
            "semantic_set_root_sha256": semantic_set_root,
        },
        "coverage": {
            name: dict(sorted(counter.items())) for name, counter in coverage.items()
        },
        "sharding": {
            "method": "first_hex_of_full_semantic_signature",
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
        "nonclaims": list(NONCLAIMS),
    }
    _write_json(manifest_path, manifest)
    return manifest


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build", help="build all 65,536 records")
    build.add_argument("--template-bank", type=Path, required=True)
    build.add_argument("--output-dir", type=Path, required=True)
    build.add_argument("--manifest", type=Path, required=True)
    sample = subparsers.add_parser("sample", help="emit one generated record")
    sample.add_argument("--template-bank", type=Path, required=True)
    sample.add_argument("--ordinal", type=int, required=True)
    return parser


def _main(argv: Sequence[str]) -> int:
    args = _build_parser().parse_args(argv)
    try:
        bank = load_template_bank(args.template_bank)
        if args.command == "sample":
            result: object = generate_record(bank, args.ordinal)
        else:
            result = build_corpus(args.template_bank, args.output_dir, args.manifest)
        sys.stdout.buffer.write(canonical_json_bytes(result) + b"\n")
        return 0
    except SyntheticDeonticError as exc:
        sys.stderr.write(f"synthetic_deontic_kb: {exc}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
