"""Build an exact progressively decodable lookup representation of a Q table.

Rows are stored in descending score order. The first layer stores the exact
winning action. Each later rank layer stores the next action and its exact
adjacent score gap. A final calibration layer stores the maximum Q value.

The first k rank layers are sufficient for exact top-k identities and gaps.
Only all rank layers plus calibration reconstruct the full absolute Q table.
"""

from __future__ import annotations

import argparse
import json
import math
import struct
import sys
import zlib
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.qgent_rate_structured_memory_v001 import (
    rate_structured_memory as quotient,
)

DEFAULT_ARTIFACT = ROOT / "assets/downloads/qgent-signal-ladder-q-v1.slq"
DEFAULT_REPORT = (
    Path(__file__).with_name("results")
    / "qgent_signal_ladder_v001.report.json"
)
PROTOCOL_PATH = (
    Path(__file__).with_name("research")
    / "signal_ladder_protocol_v001.json"
)

SCHEMA = "qgent-signal-ladder-q-memory-v1"
REPORT_SCHEMA = "qgent-signal-ladder-experiment-v1"
PROTOCOL_SCHEMA = "qgent-signal-ladder-protocol-v1"
MAGIC = b"SLQ1"
HEADER_LIMIT = 128 * 1024
TOP_TWO_BYTE_LIMIT = 60_000
FULL_BYTE_LIMIT = 512 * 1024
ACTION_SENTINEL = 255
ROW_LIMIT = 1_000_000
ALLOWED_STREAM_DTYPES = {"|u1", "<u2", "<u4", "<i4"}


class SignalLadderError(ValueError):
    """Raised when a signal-ladder artifact fails closed."""


def verify_protocol(source_sha256: str | None = None) -> dict[str, Any]:
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    if protocol.get("schema") != PROTOCOL_SCHEMA:
        raise ValueError("unexpected signal-ladder protocol schema")
    if source_sha256 and protocol.get("source_sha256") != source_sha256:
        raise ValueError("protocol is bound to a different source table")
    return protocol


def compress_stream(
    *,
    label: str,
    raw: bytes,
    cells: int,
    dtype: str,
    transform: str,
    body_offset: int,
) -> tuple[bytes, dict[str, Any]]:
    compressed = zlib.compress(raw, level=9)
    return compressed, {
        "label": label,
        "cells": int(cells),
        "dtype": dtype,
        "transform": transform,
        "compression": "zlib level 9",
        "body_offset": body_offset,
        "uncompressed_bytes": len(raw),
        "compressed_bytes": len(compressed),
        "compressed_sha256": quotient.sha256_bytes(compressed),
    }


def ranked_rows(
    table: np.ndarray,
    sentinel: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    mask = quotient.static_permitted_mask(table, sentinel)
    full_mask = np.broadcast_to(mask, table.shape).reshape(
        -1,
        table.shape[-1],
    )
    rows = table.reshape(-1, table.shape[-1])
    row_count, action_count = rows.shape
    actions = np.full(
        (row_count, action_count),
        ACTION_SENTINEL,
        dtype=np.uint8,
    )
    gaps = np.zeros((row_count, action_count), dtype=np.int64)
    values = np.empty(row_count, dtype=np.int32)
    counts = full_mask.sum(axis=1).astype(np.uint8)
    for row_index, (row, permitted) in enumerate(
        zip(rows, full_mask, strict=True)
    ):
        allowed = np.flatnonzero(permitted)
        order = sorted(
            (int(action) for action in allowed),
            key=lambda action: (-int(row[action]), action),
        )
        actions[row_index, : len(order)] = order
        values[row_index] = int(row[order[0]])
        for rank in range(1, len(order)):
            gaps[row_index, rank] = (
                int(row[order[rank - 1]]) - int(row[order[rank]])
            )
    if np.any(gaps < 0):
        raise ValueError("ranked adjacent score gap is negative")
    return actions, gaps, values, counts


def build_artifact(
    table: np.ndarray,
    *,
    sentinel: int,
    source_sha256: str,
) -> tuple[bytes, dict[str, Any]]:
    if table.dtype != np.dtype("<i4"):
        table = np.asarray(table, dtype="<i4")
    actions, gaps, values, counts = ranked_rows(table, sentinel)
    mask = quotient.static_permitted_mask(table, sentinel)
    mask_bytes = np.packbits(
        mask.reshape(-1).astype(np.uint8),
        bitorder="little",
    ).tobytes()

    streams: list[dict[str, Any]] = []
    stream_payloads: list[bytes] = []
    rank_layers = []
    body_offset = 0
    prefix_body_bytes = []
    for rank in range(table.shape[-1]):
        active = counts > rank
        action_raw = actions[active, rank].tobytes()
        action_stream, action_meta = compress_stream(
            label=f"rank_{rank}_actions",
            raw=action_raw,
            cells=int(np.sum(active)),
            dtype="<u1",
            transform="none",
            body_offset=body_offset,
        )
        action_index = len(streams)
        streams.append(action_meta)
        stream_payloads.append(action_stream)
        body_offset += len(action_stream)
        gap_index: int | None = None
        if rank > 0:
            selected_gaps = gaps[active, rank]
            if int(selected_gaps.max(initial=0)) <= np.iinfo(np.uint16).max:
                gap_dtype = np.dtype("<u2")
            else:
                gap_dtype = np.dtype("<u4")
            gap_values = selected_gaps.astype(gap_dtype)
            gap_raw = quotient.byte_shuffle(gap_values)
            gap_stream, gap_meta = compress_stream(
                label=f"rank_{rank}_adjacent_gaps",
                raw=gap_raw,
                cells=int(np.sum(active)),
                dtype=gap_dtype.str,
                transform="byte shuffle",
                body_offset=body_offset,
            )
            gap_index = len(streams)
            streams.append(gap_meta)
            stream_payloads.append(gap_stream)
            body_offset += len(gap_stream)
        rank_layers.append(
            {
                "rank": rank,
                "active_rows": int(np.sum(active)),
                "action_stream_index": action_index,
                "gap_stream_index": gap_index,
            }
        )
        prefix_body_bytes.append(body_offset)

    value_shape = table.shape[:-1]
    value_grid = values.reshape(value_shape).astype(np.int64)
    value_delta = np.empty(value_shape, dtype=np.int64)
    value_delta[0] = value_grid[0]
    value_delta[1:] = value_grid[1:] - value_grid[:-1]
    if (
        value_delta.min() < np.iinfo(np.int32).min
        or value_delta.max() > np.iinfo(np.int32).max
    ):
        raise ValueError("calibration delta does not fit in signed 32 bits")
    value_raw = quotient.byte_shuffle(value_delta.astype("<i4"))
    value_stream, value_meta = compress_stream(
        label="absolute_maximum_q",
        raw=value_raw,
        cells=int(values.size),
        dtype="<i4",
        transform="time-axis delta then byte shuffle",
        body_offset=body_offset,
    )
    value_stream_index = len(streams)
    streams.append(value_meta)
    stream_payloads.append(value_stream)
    body_offset += len(value_stream)

    header = {
        "schema": SCHEMA,
        "shape": list(table.shape),
        "source_sha256": source_sha256,
        "source_dtype": "<i4",
        "forbidden_sentinel": int(sentinel),
        "action_sentinel": ACTION_SENTINEL,
        "tie_break": "lower action identifier first",
        "rank_definition": "descending Q score, then ascending action identifier",
        "gap_definition": "Q at previous rank minus Q at current rank",
        "static_mask_bits": int(mask.size),
        "static_mask_little_endian_hex": mask_bytes.hex(),
        "row_count": int(values.size),
        "action_count": int(table.shape[-1]),
        "rank_layers": rank_layers,
        "value_stream_index": value_stream_index,
        "streams": streams,
        "body_bytes": body_offset,
        "scope": {
            "rank_prefix": (
                "first k rank layers preserve exact top-k action identities "
                "and adjacent score gaps"
            ),
            "full": (
                "all rank layers plus absolute maximum reconstruct the exact table"
            ),
        },
    }
    header_bytes = quotient.canonical_json_bytes(header)
    if len(header_bytes) > HEADER_LIMIT:
        raise ValueError("signal-ladder header exceeds its fixed limit")
    artifact = (
        MAGIC
        + struct.pack("<I", len(header_bytes))
        + header_bytes
        + b"".join(stream_payloads)
    )
    file_prefix_bytes = [
        8 + len(header_bytes) + body_bytes
        for body_bytes in prefix_body_bytes
    ]
    layout = {
        "header_bytes": 8 + len(header_bytes),
        "rank_prefix_file_bytes": file_prefix_bytes,
        "full_file_bytes": len(artifact),
        "value_stream_bytes": len(value_stream),
    }
    return artifact, layout


def parse_artifact(
    artifact: bytes,
    *,
    expected_source_sha256: str,
) -> tuple[dict[str, Any], int]:
    if len(artifact) > FULL_BYTE_LIMIT:
        raise SignalLadderError("artifact exceeds its fixed file limit")
    if len(artifact) < 8 or artifact[:4] != MAGIC:
        raise SignalLadderError("artifact magic is invalid")
    header_length = struct.unpack("<I", artifact[4:8])[0]
    if header_length == 0 or header_length > HEADER_LIMIT:
        raise SignalLadderError("artifact header length is invalid")
    body_start = 8 + header_length
    if body_start > len(artifact):
        raise SignalLadderError("artifact header is truncated")
    raw_header = artifact[8:body_start]
    try:
        header = json.loads(raw_header)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SignalLadderError("artifact header is invalid JSON") from error
    if quotient.canonical_json_bytes(header) != raw_header:
        raise SignalLadderError("artifact header is not canonical JSON")
    if not isinstance(header, dict):
        raise SignalLadderError("artifact header is not an object")
    if header.get("schema") != SCHEMA:
        raise SignalLadderError("artifact schema is unsupported")
    if header.get("source_sha256") != expected_source_sha256:
        raise SignalLadderError("artifact is bound to a different source table")
    try:
        raw_shape = header.get("shape")
        if not isinstance(raw_shape, list) or any(
            type(value) is not int for value in raw_shape
        ):
            raise SignalLadderError("artifact shape is invalid")
        shape = tuple(raw_shape)
        if len(shape) < 2 or any(value <= 0 for value in shape):
            raise SignalLadderError("artifact shape is invalid")
        if not 1 <= shape[-1] <= ACTION_SENTINEL:
            raise SignalLadderError("artifact action count is invalid")
        row_count = math.prod(shape[:-1])
        if not 1 <= row_count <= ROW_LIMIT:
            raise SignalLadderError("artifact row count exceeds its bound")
        if int(header.get("row_count", -1)) != row_count:
            raise SignalLadderError("artifact row count is invalid")
        if int(header.get("action_count", -1)) != shape[-1]:
            raise SignalLadderError("artifact action count is invalid")
        if int(header.get("action_sentinel", -1)) != ACTION_SENTINEL:
            raise SignalLadderError("artifact action sentinel is invalid")
        sentinel = int(header["forbidden_sentinel"])
        if not np.iinfo(np.int32).min <= sentinel <= np.iinfo(np.int32).max:
            raise SignalLadderError("artifact forbidden sentinel is invalid")
        if int(header.get("body_bytes", -1)) != len(artifact) - body_start:
            raise SignalLadderError("artifact body length is invalid")

        streams = header.get("streams")
        if not isinstance(streams, list) or not streams:
            raise SignalLadderError("artifact stream registry is invalid")
        expected_offset = 0
        for stream in streams:
            if not isinstance(stream, dict):
                raise SignalLadderError("artifact stream descriptor is invalid")
            offset = int(stream.get("body_offset", -1))
            length = int(stream.get("compressed_bytes", -1))
            raw_length = int(stream.get("uncompressed_bytes", -1))
            cells = int(stream.get("cells", -1))
            dtype = np.dtype(stream.get("dtype"))
            if dtype.str not in ALLOWED_STREAM_DTYPES:
                raise SignalLadderError("artifact stream dtype is unsupported")
            if offset != expected_offset or length <= 0 or cells < 0:
                raise SignalLadderError("artifact stream layout is invalid")
            if raw_length != cells * dtype.itemsize:
                raise SignalLadderError("artifact stream cell size is invalid")
            if raw_length < 0 or raw_length > quotient.STREAM_LIMIT:
                raise SignalLadderError("artifact stream bound is invalid")
            digest = stream.get("compressed_sha256")
            if (
                not isinstance(digest, str)
                or len(digest) != 64
                or any(character not in "0123456789abcdef" for character in digest)
            ):
                raise SignalLadderError("artifact stream hash is invalid")
            expected_offset += length
        if expected_offset != int(header["body_bytes"]):
            raise SignalLadderError(
                "artifact stream lengths do not cover the body"
            )

        rank_layers = header.get("rank_layers")
        if not isinstance(rank_layers, list) or len(rank_layers) != shape[-1]:
            raise SignalLadderError("artifact rank-layer registry is invalid")
        used_indexes: set[int] = set()
        for rank, layer in enumerate(rank_layers):
            if not isinstance(layer, dict) or int(layer.get("rank", -1)) != rank:
                raise SignalLadderError("artifact rank-layer order is invalid")
            active_rows = int(layer.get("active_rows", -1))
            if not 0 <= active_rows <= row_count:
                raise SignalLadderError("artifact active-row count is invalid")
            action_index = int(layer.get("action_stream_index", -1))
            if not 0 <= action_index < len(streams):
                raise SignalLadderError("artifact action stream index is invalid")
            action_stream = streams[action_index]
            if (
                action_index in used_indexes
                or action_stream.get("label") != f"rank_{rank}_actions"
                or np.dtype(action_stream["dtype"]) != np.dtype("<u1")
                or action_stream.get("transform") != "none"
                or int(action_stream["cells"]) != active_rows
            ):
                raise SignalLadderError("artifact action stream role is invalid")
            used_indexes.add(action_index)
            gap_index = layer.get("gap_stream_index")
            if rank == 0:
                if gap_index is not None:
                    raise SignalLadderError("winner layer unexpectedly has a gap")
                continue
            gap_index = int(gap_index)
            if not 0 <= gap_index < len(streams):
                raise SignalLadderError("artifact gap stream index is invalid")
            gap_stream = streams[gap_index]
            if (
                gap_index in used_indexes
                or gap_stream.get("label") != f"rank_{rank}_adjacent_gaps"
                or np.dtype(gap_stream["dtype"]).str not in {"<u2", "<u4"}
                or gap_stream.get("transform") != "byte shuffle"
                or int(gap_stream["cells"]) != active_rows
            ):
                raise SignalLadderError("artifact gap stream role is invalid")
            used_indexes.add(gap_index)
        value_index = int(header.get("value_stream_index", -1))
        if not 0 <= value_index < len(streams) or value_index in used_indexes:
            raise SignalLadderError("artifact calibration stream index is invalid")
        value_stream = streams[value_index]
        if (
            value_stream.get("label") != "absolute_maximum_q"
            or np.dtype(value_stream["dtype"]) != np.dtype("<i4")
            or value_stream.get("transform")
            != "time-axis delta then byte shuffle"
            or int(value_stream["cells"]) != row_count
        ):
            raise SignalLadderError("artifact calibration stream role is invalid")
        used_indexes.add(value_index)
        if used_indexes != set(range(len(streams))):
            raise SignalLadderError("artifact contains an unreferenced stream")
        static_mask_from_header(header, shape)
    except SignalLadderError:
        raise
    except (KeyError, TypeError, ValueError, OverflowError) as error:
        raise SignalLadderError("artifact semantic header is invalid") from error
    return header, body_start


def static_mask_from_header(
    header: dict[str, Any],
    shape: tuple[int, ...],
) -> np.ndarray:
    bits = int(header["static_mask_bits"])
    expected_bits = math.prod(shape[1:])
    if bits != expected_bits:
        raise SignalLadderError("artifact mask length is invalid")
    try:
        raw = bytes.fromhex(header["static_mask_little_endian_hex"])
    except (TypeError, ValueError) as error:
        raise SignalLadderError("artifact mask is not hexadecimal") from error
    expected_bytes = (bits + 7) // 8
    if len(raw) != expected_bytes:
        raise SignalLadderError("artifact mask byte length is invalid")
    if bits % 8 and raw[-1] >> (bits % 8):
        raise SignalLadderError("artifact mask has nonzero padding bits")
    mask = (
        np.unpackbits(np.frombuffer(raw, dtype=np.uint8), bitorder="little")[:bits]
        .astype(bool)
        .reshape(shape[1:])
    )
    if not np.all(np.any(mask, axis=-1)):
        raise SignalLadderError("artifact mask forbids every action in a state")
    return mask


def decode_stream(
    artifact: bytes,
    header: dict[str, Any],
    body_start: int,
    stream_index: int,
) -> bytes:
    try:
        stream = header["streams"][stream_index]
    except (IndexError, TypeError) as error:
        raise SignalLadderError("artifact stream index is invalid") from error
    start = body_start + int(stream["body_offset"])
    end = start + int(stream["compressed_bytes"])
    compressed = artifact[start:end]
    if quotient.sha256_bytes(compressed) != stream["compressed_sha256"]:
        raise SignalLadderError("artifact stream hash is invalid")
    try:
        return quotient.bounded_decompress(
            compressed,
            int(stream["uncompressed_bytes"]),
        )
    except quotient.ArtifactError as error:
        raise SignalLadderError(str(error)) from error


def decode_rank_prefix(
    artifact: bytes,
    *,
    depth: int,
    expected_source_sha256: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, Any]]:
    header, body_start = parse_artifact(
        artifact,
        expected_source_sha256=expected_source_sha256,
    )
    shape = tuple(int(value) for value in header["shape"])
    action_count = shape[-1]
    if not 1 <= depth <= action_count:
        raise SignalLadderError("requested rank depth is invalid")
    mask = static_mask_from_header(header, shape)
    full_mask = np.broadcast_to(mask, shape).reshape(-1, action_count)
    counts = full_mask.sum(axis=1)
    row_count = int(header["row_count"])
    actions = np.full((row_count, depth), ACTION_SENTINEL, dtype=np.uint8)
    gaps = np.zeros((row_count, depth), dtype=np.int64)
    active_matrix = np.zeros((row_count, depth), dtype=bool)
    for rank in range(depth):
        layer = header["rank_layers"][rank]
        active = counts > rank
        active_matrix[:, rank] = active
        if int(layer["active_rows"]) != int(np.sum(active)):
            raise SignalLadderError("rank layer active-row count is invalid")
        action_index = int(layer["action_stream_index"])
        action_raw = decode_stream(
            artifact,
            header,
            body_start,
            action_index,
        )
        decoded_actions = np.frombuffer(action_raw, dtype=np.uint8)
        if len(decoded_actions) != int(np.sum(active)):
            raise SignalLadderError("rank action stream has the wrong length")
        actions[active, rank] = decoded_actions
        active_rows = np.flatnonzero(active)
        if np.any(decoded_actions >= action_count):
            raise SignalLadderError("rank stream contains an invalid action")
        if not np.all(full_mask[active_rows, decoded_actions]):
            raise SignalLadderError("rank stream contains a forbidden action")
        if rank > 0:
            prior = actions[active, :rank]
            if np.any(np.any(prior == decoded_actions[:, None], axis=1)):
                raise SignalLadderError("rank stream repeats an action")
            gap_index = layer["gap_stream_index"]
            if gap_index is None:
                raise SignalLadderError("rank layer is missing its gap stream")
            gap_meta = header["streams"][int(gap_index)]
            gap_dtype = np.dtype(gap_meta["dtype"])
            gap_raw = decode_stream(
                artifact,
                header,
                body_start,
                int(gap_index),
            )
            try:
                decoded_gaps = quotient.byte_unshuffle(
                    gap_raw,
                    gap_dtype,
                    int(np.sum(active)),
                ).astype(np.int64)
            except quotient.ArtifactError as error:
                raise SignalLadderError(str(error)) from error
            if np.any(decoded_gaps < 0):
                raise SignalLadderError("rank stream contains a negative gap")
            gaps[active, rank] = decoded_gaps
    return actions, gaps, active_matrix, header


def decode_full_table(
    artifact: bytes,
    *,
    expected_source_sha256: str,
) -> tuple[np.ndarray, dict[str, Any]]:
    header, body_start = parse_artifact(
        artifact,
        expected_source_sha256=expected_source_sha256,
    )
    shape = tuple(int(value) for value in header["shape"])
    action_count = shape[-1]
    actions, gaps, active, _ = decode_rank_prefix(
        artifact,
        depth=action_count,
        expected_source_sha256=expected_source_sha256,
    )
    value_index = int(header["value_stream_index"])
    value_meta = header["streams"][value_index]
    value_raw = decode_stream(
        artifact,
        header,
        body_start,
        value_index,
    )
    try:
        value_delta = quotient.byte_unshuffle(
            value_raw,
            np.dtype(value_meta["dtype"]),
            int(header["row_count"]),
        ).reshape(shape[:-1])
    except quotient.ArtifactError as error:
        raise SignalLadderError(str(error)) from error
    values = np.cumsum(value_delta.astype(np.int64), axis=0).reshape(-1)
    sentinel = int(header["forbidden_sentinel"])
    rebuilt = np.full(
        (int(header["row_count"]), action_count),
        sentinel,
        dtype="<i4",
    )
    current = values.copy()
    for rank in range(action_count):
        selected = active[:, rank]
        if rank > 0:
            current[selected] -= gaps[selected, rank]
        selected_rows = np.flatnonzero(selected)
        selected_actions = actions[selected, rank]
        selected_values = current[selected]
        if (
            selected_values.min(initial=0) < np.iinfo(np.int32).min
            or selected_values.max(initial=0) > np.iinfo(np.int32).max
        ):
            raise SignalLadderError("decoded score is outside signed 32 bits")
        rebuilt[selected_rows, selected_actions] = selected_values.astype("<i4")
    return rebuilt.reshape(shape), header


def mutation_checks(artifact: bytes, source_sha256: str) -> dict[str, bool]:
    corrupted = bytearray(artifact)
    corrupted[-1] ^= 1
    header_length = struct.unpack("<I", artifact[4:8])[0]
    body_start = 8 + header_length
    semantic_header = json.loads(artifact[8:body_start])
    semantic_header["row_count"] += 1
    semantic_header_bytes = quotient.canonical_json_bytes(semantic_header)
    semantic_mutation = (
        artifact[:4]
        + struct.pack("<I", len(semantic_header_bytes))
        + semantic_header_bytes
        + artifact[body_start:]
    )
    checks = {}
    for name, candidate, expected in (
        ("corrupt_stream_rejected", bytes(corrupted), source_sha256),
        ("wrong_source_rejected", artifact, "0" * 64),
        ("wrong_magic_rejected", b"BAD!" + artifact[4:], source_sha256),
        ("semantic_header_rejected", semantic_mutation, source_sha256),
    ):
        rejected = False
        try:
            decode_full_table(candidate, expected_source_sha256=expected)
        except SignalLadderError:
            rejected = True
        checks[name] = rejected
    return checks


def build_experiment() -> tuple[bytes, dict[str, Any]]:
    source_bytes, table, source_report, sentinel = quotient.load_source()
    source_sha = quotient.sha256_bytes(source_bytes)
    protocol = verify_protocol(source_sha)
    artifact, layout = build_artifact(
        table,
        sentinel=sentinel,
        source_sha256=source_sha,
    )
    duplicate, duplicate_layout = build_artifact(
        table,
        sentinel=sentinel,
        source_sha256=source_sha,
    )
    source_actions, source_gaps, _, source_counts = ranked_rows(table, sentinel)
    top_one, _, active_one, _ = decode_rank_prefix(
        artifact,
        depth=1,
        expected_source_sha256=source_sha,
    )
    top_two, top_two_gaps, active_two, _ = decode_rank_prefix(
        artifact,
        depth=2,
        expected_source_sha256=source_sha,
    )
    rebuilt, _ = decode_full_table(
        artifact,
        expected_source_sha256=source_sha,
    )
    one_active = active_one[:, 0]
    two_active = source_counts > 1
    winner_mismatches = int(
        np.sum(top_one[one_active, 0] != source_actions[one_active, 0])
    )
    runner_mismatches = int(
        np.sum(top_two[two_active, 1] != source_actions[two_active, 1])
    )
    margin_mismatches = int(
        np.sum(top_two_gaps[two_active, 1] != source_gaps[two_active, 1])
    )
    prefix_activity_mismatches = int(
        np.sum(active_two[:, 1] != two_active)
    )
    permitted = table != sentinel
    score_mismatches = int(np.sum(rebuilt[permitted] != table[permitted]))
    forbidden_changes = int(np.sum((rebuilt == sentinel) != (table == sentinel)))
    mutations = mutation_checks(artifact, source_sha)
    exact_control = quotient.exact_lossless_control(table, sentinel)
    policy_control = quotient.policy_only_control(table, sentinel)
    decision_quotient_bytes = quotient.DEFAULT_ARTIFACT.stat().st_size
    top_one_bytes = int(layout["rank_prefix_file_bytes"][0])
    top_two_bytes = int(layout["rank_prefix_file_bytes"][1])
    accepted = (
        winner_mismatches == 0
        and runner_mismatches == 0
        and margin_mismatches == 0
        and prefix_activity_mismatches == 0
        and score_mismatches == 0
        and forbidden_changes == 0
        and top_two_bytes <= TOP_TWO_BYTE_LIMIT
        and len(artifact) <= FULL_BYTE_LIMIT
        and artifact == duplicate
        and layout == duplicate_layout
        and all(mutations.values())
    )
    rank_rows = []
    for layer, prefix_bytes in zip(
        range(1, table.shape[-1] + 1),
        layout["rank_prefix_file_bytes"],
        strict=True,
    ):
        rank_rows.append(
            {
                "loaded_rank_layers": layer,
                "preserves": (
                    "winner only"
                    if layer == 1
                    else f"exact top-{layer} actions and adjacent gaps"
                ),
                "complete_prefix_bytes": int(prefix_bytes),
            }
        )
    report = {
        "schema": REPORT_SCHEMA,
        "classification": (
            "exact progressive lookup representation of a compiled synthetic Q table"
        ),
        "protocol": {
            "schema": protocol["schema"],
            "sha256": quotient.sha256_bytes(PROTOCOL_PATH.read_bytes()),
            "exploratory_disclosure": protocol["exploratory_disclosure"],
        },
        "source": {
            "table_schema": source_report["compiled_q_table"]["schema"],
            "shape": list(table.shape),
            "rows": int(np.prod(table.shape[:-1])),
            "raw_bytes": len(source_bytes),
            "sha256": source_sha,
        },
        "artifact": {
            "schema": SCHEMA,
            "bytes": len(artifact),
            "sha256": quotient.sha256_bytes(artifact),
            "header_bytes": layout["header_bytes"],
            "rank_prefixes": rank_rows,
            "top_one_prefix_bytes": top_one_bytes,
            "top_two_prefix_bytes": top_two_bytes,
            "value_stream_bytes": layout["value_stream_bytes"],
            "deterministic_duplicate": artifact == duplicate,
        },
        "fidelity": {
            "winner_mismatches": winner_mismatches,
            "runner_up_mismatches": runner_mismatches,
            "best_to_runner_up_gap_mismatches": margin_mismatches,
            "prefix_activity_mismatches": prefix_activity_mismatches,
            "full_permitted_score_mismatches": score_mismatches,
            "full_forbidden_mask_changes": forbidden_changes,
        },
        "controls": {
            "policy_only_payload": policy_control,
            "decision_quotient_complete_artifact_bytes": decision_quotient_bytes,
            "strong_lossless_q_payload": exact_control,
            "scope_warning": (
                "The policy control answers less, while the strong lossless "
                "control is not independently prefix-addressable by rank."
            ),
        },
        "mutations": mutations,
        "mathematical_receipt": {
            "ordered_actions": "a_1,...,a_m with Q(a_1)>=...>=Q(a_m)",
            "adjacent_gap": "g_j=Q(a_j)-Q(a_{j+1})>=0",
            "prefix_scope": (
                "a depth-k prefix recovers a_1,...,a_k and every difference "
                "Q(a_i)-Q(a_j) for 1<=i<j<=k by summing adjacent gaps"
            ),
            "full_reconstruction": (
                "Q(a_j)=V-sum_{i=1}^{j-1}g_i after loading V=max_a Q(a)"
            ),
        },
        "acceptance": {
            "winner_gate_passed": winner_mismatches == 0,
            "top_two_gate_passed": (
                runner_mismatches == 0
                and margin_mismatches == 0
                and prefix_activity_mismatches == 0
            ),
            "full_exact_gate_passed": (
                score_mismatches == 0 and forbidden_changes == 0
            ),
            "top_two_size_gate_passed": top_two_bytes <= TOP_TWO_BYTE_LIMIT,
            "full_size_gate_passed": len(artifact) <= FULL_BYTE_LIMIT,
            "mutation_gate_passed": all(mutations.values()),
            "experiment_accepted": accepted,
        },
        "nonclaims": protocol["nonclaims"],
    }
    return artifact, report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-out", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--report-out", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--protocol-check", action="store_true")
    args = parser.parse_args(argv)
    if args.protocol_check:
        _, _, source_report, _ = quotient.load_source()
        protocol = verify_protocol(source_report["compiled_q_table"]["sha256"])
        print(
            json.dumps(
                {
                    "protocol_schema": protocol["schema"],
                    "protocol_sha256": quotient.sha256_bytes(
                        PROTOCOL_PATH.read_bytes()
                    ),
                    "status": "FROZEN_AND_CONSISTENT",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    artifact, report = build_experiment()
    args.artifact_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.artifact_out.write_bytes(artifact)
    args.report_out.write_bytes(
        quotient.canonical_json_bytes(report, newline=True)
    )
    print(
        json.dumps(
            {
                "accepted": report["acceptance"]["experiment_accepted"],
                "artifact_bytes": len(artifact),
                "artifact_sha256": report["artifact"]["sha256"],
                "top_one_prefix_bytes": report["artifact"][
                    "top_one_prefix_bytes"
                ],
                "top_two_prefix_bytes": report["artifact"][
                    "top_two_prefix_bytes"
                ],
                "full_score_mismatches": report["fidelity"][
                    "full_permitted_score_mismatches"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if report["acceptance"]["experiment_accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
