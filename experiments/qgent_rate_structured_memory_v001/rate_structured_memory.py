"""Build and verify a policy-preserving quotient encoding of a compiled Q-table.

The source table contains one signed 32-bit score for each state-action pair.
For each state, this experiment separates

    V(s) = max_a Q(s, a)

from the relative advantages

    A(s, a) = Q(s, a) - V(s).

An action-independent offset does not change a greedy decision. The encoder
quantizes V to the nearest grid point and rounds every strictly negative
advantage downward. This guarantees that exact maxima remain zero and every
strictly suboptimal action remains negative.

The result is a deployment-time approximation of the compiled scores. It is
not a Bellman-invariant transformation and must not be substituted into
training or planning without a separate error analysis.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import zlib
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SOURCE_TABLE = ROOT / "assets/data/qgent_utilitarian_energy_100_v1.qtable"
SOURCE_REPORT = ROOT / "assets/data/qgent_utilitarian_energy_100_v1.report.json"
DEFAULT_ARTIFACT = ROOT / "assets/downloads/qgent-decision-quotient-q-v1.qdq"
DEFAULT_REPORT = (
    Path(__file__).with_name("results")
    / "qgent_rate_structured_memory_v001.report.json"
)

SCHEMA = "qgent-decision-quotient-q-memory-v1"
REPORT_SCHEMA = "qgent-rate-structured-memory-experiment-v1"
MAGIC = b"QDQ1"
HEADER_LIMIT = 64 * 1024
STREAM_LIMIT = 8 * 1024 * 1024
CODE_SENTINEL = np.int16(-32768)
QUANTIZATION_STEPS = (4, 8, 16, 32, 64, 128, 256, 512, 1024)
MAX_SCORE_ERROR = 400


class ArtifactError(ValueError):
    """Raised when a quotient artifact fails a structural or binding check."""


def canonical_json_bytes(value: Any, *, newline: bool = False) -> bytes:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return payload + (b"\n" if newline else b"")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def round_half_up(values: np.ndarray, step: int) -> np.ndarray:
    """Round signed integers to a grid, with half-grid ties toward +infinity."""

    return np.floor_divide(values.astype(np.int64) + step // 2, step)


def byte_shuffle(array: np.ndarray) -> bytes:
    contiguous = np.ascontiguousarray(array)
    width = contiguous.dtype.itemsize
    cells = contiguous.size
    return contiguous.view(np.uint8).reshape(cells, width).T.copy().tobytes()


def byte_unshuffle(payload: bytes, dtype: np.dtype[Any], count: int) -> np.ndarray:
    selected_dtype = np.dtype(dtype)
    expected = count * selected_dtype.itemsize
    if len(payload) != expected:
        raise ArtifactError(
            f"shuffled stream has {len(payload)} bytes, expected {expected}"
        )
    restored = (
        np.frombuffer(payload, dtype=np.uint8)
        .reshape(selected_dtype.itemsize, count)
        .T.copy()
        .reshape(-1)
    )
    return restored.view(selected_dtype)


def temporal_delta(array: np.ndarray) -> np.ndarray:
    source = np.asarray(array, dtype=np.int64)
    delta = np.empty(source.shape, dtype=np.int64)
    delta[0] = source[0]
    delta[1:] = source[1:] - source[:-1]
    if delta.min() < np.iinfo(np.int16).min or delta.max() > np.iinfo(np.int16).max:
        raise ValueError("temporal delta does not fit in signed 16 bits")
    return delta.astype("<i2")


def undo_temporal_delta(delta: np.ndarray) -> np.ndarray:
    restored = np.cumsum(delta.astype(np.int64), axis=0)
    if (
        restored.min() < np.iinfo(np.int16).min
        or restored.max() > np.iinfo(np.int16).max
    ):
        raise ArtifactError("decoded value does not fit in signed 16 bits")
    return restored.astype("<i2")


def bounded_decompress(payload: bytes, expected_bytes: int) -> bytes:
    if expected_bytes < 0 or expected_bytes > STREAM_LIMIT:
        raise ArtifactError("declared decompressed stream size is out of bounds")
    decompressor = zlib.decompressobj()
    restored = decompressor.decompress(payload, expected_bytes + 1)
    if len(restored) > expected_bytes or decompressor.unconsumed_tail:
        raise ArtifactError("compressed stream exceeds its declared bound")
    restored += decompressor.flush()
    if (
        len(restored) != expected_bytes
        or decompressor.unused_data
        or not decompressor.eof
    ):
        raise ArtifactError("compressed stream has invalid length or trailing data")
    return restored


def source_shape_and_sentinel(report: dict[str, Any]) -> tuple[tuple[int, ...], int]:
    shape = tuple(int(value) for value in report["compiled_q_table"]["shape"])
    if len(shape) < 3 or any(value <= 0 for value in shape):
        raise ValueError("source Q-table shape is invalid")
    sentinel = int(report["compiled_q_table"]["forbidden_sentinel"])
    return shape, sentinel


def load_source(
    table_path: Path = SOURCE_TABLE,
    report_path: Path = SOURCE_REPORT,
) -> tuple[bytes, np.ndarray, dict[str, Any], int]:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    shape, sentinel = source_shape_and_sentinel(report)
    payload = table_path.read_bytes()
    expected_bytes = int(np.prod(shape)) * np.dtype("<i4").itemsize
    if len(payload) != expected_bytes:
        raise ValueError(
            f"source table has {len(payload)} bytes, expected {expected_bytes}"
        )
    declared_hash = report["compiled_q_table"]["sha256"]
    if sha256_bytes(payload) != declared_hash:
        raise ValueError("source table does not match its report")
    table = np.frombuffer(payload, dtype="<i4").reshape(shape).copy()
    return payload, table, report, sentinel


def static_permitted_mask(table: np.ndarray, sentinel: int) -> np.ndarray:
    first = table[0] != sentinel
    if not np.all((table != sentinel) == first[None, ...]):
        raise ValueError(
            "the current codec requires an admissibility mask constant over time"
        )
    if not np.all(np.any(first, axis=-1)):
        raise ValueError("every state must permit at least one action")
    return first


def greedy_actions(table: np.ndarray, sentinel: int) -> np.ndarray:
    masked = np.where(table == sentinel, np.iinfo(np.int32).min, table)
    return np.argmax(masked, axis=-1)


def encode_components(
    table: np.ndarray,
    sentinel: int,
    step: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if step <= 0 or step % 2:
        raise ValueError("quantization step must be a positive even integer")
    mask = static_permitted_mask(table, sentinel)
    row_values = np.max(
        np.where(table == sentinel, np.iinfo(np.int32).min, table),
        axis=-1,
    ).astype(np.int64)
    value_codes = round_half_up(row_values, step)
    expanded_values = row_values[..., None]
    advantages = table.astype(np.int64) - expanded_values
    advantage_codes = np.full(table.shape, CODE_SENTINEL, dtype="<i2")
    permitted_codes = np.floor_divide(advantages[table != sentinel], step)
    if permitted_codes.min() <= int(CODE_SENTINEL):
        raise ValueError("advantage code collides with the reserved sentinel")
    if (
        value_codes.min() <= int(CODE_SENTINEL)
        or value_codes.max() > np.iinfo(np.int16).max
    ):
        raise ValueError("state-value code does not fit in signed 16 bits")
    advantage_codes[table != sentinel] = permitted_codes.astype("<i2")
    return value_codes.astype("<i2"), advantage_codes[:, mask], mask


def stream_descriptor(raw: bytes, compressed: bytes, cells: int) -> dict[str, Any]:
    return {
        "cells": cells,
        "dtype": "<i2",
        "uncompressed_bytes": len(raw),
        "compressed_bytes": len(compressed),
        "compressed_sha256": sha256_bytes(compressed),
    }


def build_artifact(
    table: np.ndarray,
    *,
    sentinel: int,
    step: int,
    source_sha256: str,
) -> bytes:
    values, permitted_advantages, mask = encode_components(table, sentinel, step)
    value_delta = temporal_delta(values)
    advantage_delta = temporal_delta(permitted_advantages)
    value_raw = byte_shuffle(value_delta)
    advantage_raw = byte_shuffle(advantage_delta)
    value_stream = zlib.compress(value_raw, level=9)
    advantage_stream = zlib.compress(advantage_raw, level=9)
    mask_bytes = np.packbits(
        mask.reshape(-1).astype(np.uint8), bitorder="little"
    ).tobytes()
    header = {
        "schema": SCHEMA,
        "shape": list(table.shape),
        "source_sha256": source_sha256,
        "source_dtype": "<i4",
        "forbidden_sentinel": sentinel,
        "code_sentinel": int(CODE_SENTINEL),
        "quantization_step": step,
        "value_quantizer": "floor((value + step/2) / step)",
        "advantage_quantizer": "floor((Q - max_permitted_Q) / step)",
        "temporal_transform": "first row followed by first differences",
        "byte_transform": "byte shuffle within each signed-16 stream",
        "compression": "zlib level 9",
        "static_mask_bits": int(mask.size),
        "static_mask_little_endian_hex": mask_bytes.hex(),
        "permitted_cells_per_time": int(np.sum(mask)),
        "value_stream": stream_descriptor(value_raw, value_stream, int(values.size)),
        "advantage_stream": stream_descriptor(
            advantage_raw,
            advantage_stream,
            int(permitted_advantages.size),
        ),
    }
    header_bytes = canonical_json_bytes(header)
    if len(header_bytes) > HEADER_LIMIT:
        raise ValueError("artifact header exceeds its fixed limit")
    return (
        MAGIC
        + struct.pack("<I", len(header_bytes))
        + header_bytes
        + value_stream
        + advantage_stream
    )


def parse_header(artifact: bytes) -> tuple[dict[str, Any], int]:
    if len(artifact) < 8 or artifact[:4] != MAGIC:
        raise ArtifactError("artifact magic is invalid")
    header_length = struct.unpack("<I", artifact[4:8])[0]
    if header_length == 0 or header_length > HEADER_LIMIT:
        raise ArtifactError("artifact header length is invalid")
    body_offset = 8 + header_length
    if body_offset > len(artifact):
        raise ArtifactError("artifact header is truncated")
    raw_header = artifact[8:body_offset]
    try:
        header = json.loads(raw_header)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ArtifactError("artifact header is not valid JSON") from error
    if canonical_json_bytes(header) != raw_header:
        raise ArtifactError("artifact header is not canonical JSON")
    if header.get("schema") != SCHEMA:
        raise ArtifactError("artifact schema is unsupported")
    return header, body_offset


def decode_artifact(
    artifact: bytes,
    *,
    expected_source_sha256: str,
) -> tuple[np.ndarray, dict[str, Any]]:
    header, body_offset = parse_header(artifact)
    if header.get("source_sha256") != expected_source_sha256:
        raise ArtifactError("artifact is not bound to the expected source table")
    shape = tuple(int(value) for value in header["shape"])
    if len(shape) < 3 or any(value <= 0 for value in shape):
        raise ArtifactError("artifact shape is invalid")
    step = int(header["quantization_step"])
    if step <= 0 or step % 2:
        raise ArtifactError("artifact quantization step is invalid")
    sentinel = int(header["forbidden_sentinel"])
    mask_bits = int(header["static_mask_bits"])
    expected_mask_bits = int(np.prod(shape[1:]))
    if mask_bits != expected_mask_bits:
        raise ArtifactError("artifact mask length does not match its shape")
    try:
        mask_bytes = bytes.fromhex(header["static_mask_little_endian_hex"])
    except (TypeError, ValueError) as error:
        raise ArtifactError("artifact mask is not valid hexadecimal") from error
    mask = (
        np.unpackbits(np.frombuffer(mask_bytes, dtype=np.uint8), bitorder="little")[
            :mask_bits
        ]
        .astype(bool)
        .reshape(shape[1:])
    )
    if not np.all(np.any(mask, axis=-1)):
        raise ArtifactError("artifact contains a state with no permitted action")

    value_meta = header["value_stream"]
    advantage_meta = header["advantage_stream"]
    value_length = int(value_meta["compressed_bytes"])
    advantage_length = int(advantage_meta["compressed_bytes"])
    if min(value_length, advantage_length) <= 0:
        raise ArtifactError("artifact stream length is invalid")
    if body_offset + value_length + advantage_length != len(artifact):
        raise ArtifactError("artifact stream lengths do not match the file")
    value_stream = artifact[body_offset : body_offset + value_length]
    advantage_stream = artifact[body_offset + value_length :]
    if sha256_bytes(value_stream) != value_meta["compressed_sha256"]:
        raise ArtifactError("state-value stream hash is invalid")
    if sha256_bytes(advantage_stream) != advantage_meta["compressed_sha256"]:
        raise ArtifactError("advantage stream hash is invalid")
    value_raw = bounded_decompress(value_stream, int(value_meta["uncompressed_bytes"]))
    advantage_raw = bounded_decompress(
        advantage_stream, int(advantage_meta["uncompressed_bytes"])
    )
    value_cells = int(value_meta["cells"])
    advantage_cells = int(advantage_meta["cells"])
    expected_value_cells = int(np.prod(shape[:-1]))
    expected_advantage_cells = shape[0] * int(np.sum(mask))
    if (
        value_cells != expected_value_cells
        or advantage_cells != expected_advantage_cells
    ):
        raise ArtifactError("artifact stream cell count is invalid")
    values_delta = byte_unshuffle(value_raw, np.dtype("<i2"), value_cells)
    advantages_delta = byte_unshuffle(advantage_raw, np.dtype("<i2"), advantage_cells)
    values = undo_temporal_delta(values_delta.reshape(shape[:-1]))
    permitted_advantages = undo_temporal_delta(
        advantages_delta.reshape(shape[0], int(np.sum(mask)))
    )
    if np.any(permitted_advantages == CODE_SENTINEL):
        raise ArtifactError("permitted advantage collides with code sentinel")

    codes = np.full(shape, CODE_SENTINEL, dtype="<i2")
    codes[:, mask] = permitted_advantages
    full_mask = np.broadcast_to(mask, shape)
    reconstructed = np.full(shape, sentinel, dtype="<i4")
    expanded_values = np.broadcast_to(values[..., None], shape).astype(np.int64)
    decoded_values = (expanded_values + codes.astype(np.int64)) * step
    permitted_values = decoded_values[full_mask]
    if (
        permitted_values.min() < np.iinfo(np.int32).min
        or permitted_values.max() > np.iinfo(np.int32).max
    ):
        raise ArtifactError("decoded score does not fit in signed 32 bits")
    reconstructed[full_mask] = permitted_values.astype("<i4")
    return reconstructed, header


def policy_only_control(table: np.ndarray, sentinel: int) -> dict[str, int]:
    actions = greedy_actions(table, sentinel).reshape(-1).astype(np.uint8)
    if actions.max() >= 16:
        raise ValueError("nibble control supports at most sixteen actions")
    packed = np.zeros((len(actions) + 1) // 2, dtype=np.uint8)
    packed |= actions[0::2]
    packed[: len(actions) // 2] |= actions[1::2] << 4
    payload = packed.tobytes()
    return {
        "raw_bytes": len(payload),
        "zlib_level_9_bytes": len(zlib.compress(payload, level=9)),
    }


def exact_lossless_control(table: np.ndarray, sentinel: int) -> dict[str, int | str]:
    mask = static_permitted_mask(table, sentinel)
    permitted = table[:, mask].astype(np.int64)
    delta = np.empty_like(permitted)
    delta[0] = permitted[0]
    delta[1:] = permitted[1:] - permitted[:-1]
    if delta.min() < np.iinfo(np.int32).min or delta.max() > np.iinfo(np.int32).max:
        raise ValueError("lossless control delta does not fit in signed 32 bits")
    transformed = byte_shuffle(delta.astype("<i4"))
    compressed = zlib.compress(transformed, level=9)
    return {
        "method": (
            "elide deterministic forbidden cells, temporal delta, "
            "byte shuffle, zlib level 9"
        ),
        "payload_only_bytes": len(compressed),
        "raw_permitted_value_bytes": int(permitted.size * 4),
    }


def nearest_advantage_rounding_control(
    table: np.ndarray,
    sentinel: int,
    step: int,
) -> dict[str, int | str]:
    permitted = table != sentinel
    values = np.max(
        np.where(permitted, table, np.iinfo(np.int32).min),
        axis=-1,
    ).astype(np.int64)
    advantages = table.astype(np.int64) - values[..., None]
    nearest_codes = round_half_up(advantages, step)
    rebuilt = np.full(table.shape, sentinel, dtype="<i4")
    rebuilt[permitted] = (nearest_codes[permitted] * step).astype("<i4")
    strict_to_zero = permitted & (advantages < 0) & (nearest_codes == 0)
    rows_with_collapsed_gap = np.any(strict_to_zero, axis=-1)
    return {
        "method": "round relative advantages to the nearest grid point",
        "strict_negative_cells_rounded_to_zero": int(np.sum(strict_to_zero)),
        "rows_with_collapsed_strict_gap": int(np.sum(rows_with_collapsed_gap)),
        "greedy_action_mismatches": int(
            np.sum(greedy_actions(table, sentinel) != greedy_actions(rebuilt, sentinel))
        ),
    }


def mutation_checks(artifact: bytes, source_sha256: str) -> dict[str, bool]:
    corrupted = bytearray(artifact)
    corrupted[-1] ^= 1
    corrupt_rejected = False
    try:
        decode_artifact(bytes(corrupted), expected_source_sha256=source_sha256)
    except ArtifactError:
        corrupt_rejected = True

    wrong_source_rejected = False
    try:
        decode_artifact(artifact, expected_source_sha256="0" * 64)
    except ArtifactError:
        wrong_source_rejected = True

    wrong_magic_rejected = False
    try:
        decode_artifact(b"BAD!" + artifact[4:], expected_source_sha256=source_sha256)
    except ArtifactError:
        wrong_magic_rejected = True
    return {
        "corrupt_stream_rejected": corrupt_rejected,
        "wrong_source_rejected": wrong_source_rejected,
        "wrong_magic_rejected": wrong_magic_rejected,
    }


def evaluate_candidate(
    table: np.ndarray,
    *,
    sentinel: int,
    step: int,
    source_sha256: str,
) -> tuple[bytes, dict[str, Any]]:
    artifact = build_artifact(
        table,
        sentinel=sentinel,
        step=step,
        source_sha256=source_sha256,
    )
    rebuilt, _ = decode_artifact(artifact, expected_source_sha256=source_sha256)
    permitted = table != sentinel
    error = np.abs(
        table[permitted].astype(np.int64) - rebuilt[permitted].astype(np.int64)
    )
    mismatches = int(
        np.sum(greedy_actions(table, sentinel) != greedy_actions(rebuilt, sentinel))
    )
    forbidden_changes = int(np.sum((rebuilt == sentinel) != (table == sentinel)))
    return artifact, {
        "quantization_step": step,
        "artifact_bytes": len(artifact),
        "maximum_absolute_score_error": int(error.max()),
        "mean_absolute_score_error": float(np.mean(error)),
        "root_mean_square_score_error": float(
            np.sqrt(np.mean(np.square(error.astype(np.float64))))
        ),
        "greedy_action_mismatches": mismatches,
        "forbidden_mask_changes": forbidden_changes,
        "theoretical_maximum_score_error": step // 2 + step - 1,
        "within_declared_error_budget": int(error.max()) <= MAX_SCORE_ERROR,
    }


def build_experiment() -> tuple[bytes, dict[str, Any]]:
    source_bytes, table, source_report, sentinel = load_source()
    source_sha = sha256_bytes(source_bytes)
    frontier = []
    artifacts: dict[int, bytes] = {}
    for step in QUANTIZATION_STEPS:
        artifact, metrics = evaluate_candidate(
            table,
            sentinel=sentinel,
            step=step,
            source_sha256=source_sha,
        )
        artifacts[step] = artifact
        frontier.append(metrics)

    eligible = [
        item
        for item in frontier
        if item["within_declared_error_budget"]
        and item["greedy_action_mismatches"] == 0
        and item["forbidden_mask_changes"] == 0
    ]
    if not eligible:
        raise RuntimeError("no quotient candidate satisfies the acceptance budget")
    selected = min(
        eligible,
        key=lambda item: (
            item["artifact_bytes"],
            item["maximum_absolute_score_error"],
        ),
    )
    selected_step = int(selected["quantization_step"])
    artifact = artifacts[selected_step]
    duplicate = build_artifact(
        table,
        sentinel=sentinel,
        step=selected_step,
        source_sha256=source_sha,
    )
    exact_control = exact_lossless_control(table, sentinel)
    policy_control = policy_only_control(table, sentinel)
    nearest_control = nearest_advantage_rounding_control(table, sentinel, selected_step)
    mutations = mutation_checks(artifact, source_sha)
    selected_beats_exact = len(artifact) < int(exact_control["payload_only_bytes"])
    accepted = (
        selected["greedy_action_mismatches"] == 0
        and selected["forbidden_mask_changes"] == 0
        and selected["maximum_absolute_score_error"] <= MAX_SCORE_ERROR
        and selected_beats_exact
        and artifact == duplicate
        and all(mutations.values())
    )
    report = {
        "schema": REPORT_SCHEMA,
        "classification": (
            "policy-preserving lossy encoding of a compiled synthetic Q-table"
        ),
        "source": {
            "table_schema": source_report["compiled_q_table"]["schema"],
            "shape": list(table.shape),
            "raw_bytes": len(source_bytes),
            "sha256": source_sha,
            "score_unit": source_report["compiled_q_table"]["score_unit"],
            "model_sha256": source_report["model"]["sha256"],
        },
        "declared_selection_rule": {
            "candidate_steps": list(QUANTIZATION_STEPS),
            "maximum_absolute_score_error": MAX_SCORE_ERROR,
            "required_greedy_action_mismatches": 0,
            "required_forbidden_mask_changes": 0,
            "objective": "smallest complete artifact satisfying every fidelity gate",
        },
        "rate_distortion_frontier": frontier,
        "selected": {
            **selected,
            "sha256": sha256_bytes(artifact),
            "deterministic_duplicate": artifact == duplicate,
            "size_reduction_vs_raw_table": 1 - len(artifact) / len(source_bytes),
            "size_reduction_vs_optimistic_exact_control": (
                1 - len(artifact) / int(exact_control["payload_only_bytes"])
            ),
        },
        "controls": {
            "strong_lossless_q_control": exact_control,
            "policy_only_non_q_control": {
                **policy_control,
                "scope": (
                    "stores only selected actions and cannot reconstruct "
                    "alternative Q scores"
                ),
            },
            "nearest_rounding_counterexample": nearest_control,
            "mutations": mutations,
        },
        "mathematical_receipt": {
            "deployment_equivalence": (
                "Q and Q+c(s) have the same greedy action at each state"
            ),
            "advantage_code": ("floor((Q(s,a)-max_b Q(s,b))/step)"),
            "preservation_argument": (
                "maximizers encode as zero; every strict nonmaximizer "
                "encodes at most negative one; the deterministic tie order "
                "is unchanged"
            ),
            "observed_action_mismatches": selected["greedy_action_mismatches"],
        },
        "acceptance": {
            "fidelity_gate_passed": (
                selected["maximum_absolute_score_error"] <= MAX_SCORE_ERROR
            ),
            "policy_preservation_gate_passed": (
                selected["greedy_action_mismatches"] == 0
            ),
            "density_gate_passed": selected_beats_exact,
            "mutation_gate_passed": all(mutations.values()),
            "experiment_accepted": accepted,
        },
        "assumptions": [
            (
                "The source consumer needs approximate compiled Q scores, not "
                "only the selected action."
            ),
            (
                "The admissibility mask is deterministic from state and "
                "constant across the table's time axis."
            ),
            (
                "A maximum score error of 400 declared milliunits is acceptable "
                "for this bounded display artifact."
            ),
        ],
        "nonclaims": [
            (
                "The encoding does not improve the learned policy or add "
                "knowledge to the source model."
            ),
            (
                "The quotient is policy-equivalent for greedy deployment, not "
                "Bellman-equivalent for retraining or replanning."
            ),
            (
                "The measured byte advantage is specific to this table, codec, "
                "and control implementation."
            ),
            (
                "The policy-only control is much smaller because it discards "
                "the values of unselected alternatives."
            ),
        ],
    }
    return artifact, report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-out", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--report-out", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args(argv)
    artifact, report = build_experiment()
    args.artifact_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.artifact_out.write_bytes(artifact)
    args.report_out.write_bytes(canonical_json_bytes(report, newline=True))
    print(
        json.dumps(
            {
                "accepted": report["acceptance"]["experiment_accepted"],
                "artifact_bytes": len(artifact),
                "artifact_sha256": report["selected"]["sha256"],
                "maximum_absolute_score_error": report["selected"][
                    "maximum_absolute_score_error"
                ],
                "greedy_action_mismatches": report["selected"][
                    "greedy_action_mismatches"
                ],
                "selected_step": report["selected"]["quantization_step"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if report["acceptance"]["experiment_accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
