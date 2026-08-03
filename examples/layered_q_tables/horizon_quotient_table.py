"""Exact quotient storage for repeated horizon slabs in a layered Q table.

The quotient preserves every logical ``Q[h, state, action]`` query. It stores
each byte-distinct horizon slab once and maps every logical horizon to its
representative. This is lossless deduplication, not value approximation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

from .knowledge_q_table import canonical_json_bytes, file_sha256

MANIFEST_SCHEMA = "glassmind-horizon-quotient-manifest-v1"
REPORT_SCHEMA = "glassmind-horizon-quotient-verification-v1"
MAX_LOGICAL_LAYERS = 4096
MAX_STATES = 1 << 24
MAX_ACTIONS = 256
MAX_MANIFEST_BYTES = 1 << 20
MAX_EXACT_DIVERSITY_STATES = 1 << 20
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class HorizonQuotientError(ValueError):
    """The source table or quotient artifact violates its exact contract."""


def _load_table(path: str | Path) -> np.memmap:
    table_path = Path(path)
    if not table_path.is_file():
        raise HorizonQuotientError(f"table does not exist: {table_path}")
    try:
        table = np.load(table_path, mmap_mode="r", allow_pickle=False)
    except (OSError, ValueError) as exc:
        raise HorizonQuotientError("table is not a valid NPY array") from exc
    if table.ndim != 3:
        raise HorizonQuotientError("table shape must be [layer, state, action]")
    layers, states, actions = table.shape
    if not 1 <= layers <= MAX_LOGICAL_LAYERS:
        raise HorizonQuotientError("logical layer count is outside its bound")
    if not 1 <= states <= MAX_STATES:
        raise HorizonQuotientError("state count is outside its bound")
    if not 1 <= actions <= MAX_ACTIONS:
        raise HorizonQuotientError("action count is outside its bound")
    if table.dtype != np.dtype("<f4"):
        raise HorizonQuotientError("table dtype must be little-endian float32")
    if not table.flags.c_contiguous:
        raise HorizonQuotientError("table must use C order")
    for layer_id in range(layers):
        if not bool(np.all(np.isfinite(table[layer_id]))):
            raise HorizonQuotientError("table contains a non-finite value")
    return table


def _layer_digest(table: np.ndarray, layer_id: int) -> str:
    return hashlib.sha256(table[layer_id].tobytes(order="C")).hexdigest()


def _shape(value: Any, name: str) -> tuple[int, int, int]:
    if (
        type(value) is not list
        or len(value) != 3
        or any(type(item) is not int for item in value)
    ):
        raise HorizonQuotientError(f"{name} shape must contain three integers")
    layers, states, actions = value
    if not 1 <= layers <= MAX_LOGICAL_LAYERS:
        raise HorizonQuotientError(f"{name} layer count is outside its bound")
    if not 1 <= states <= MAX_STATES:
        raise HorizonQuotientError(f"{name} state count is outside its bound")
    if not 1 <= actions <= MAX_ACTIONS:
        raise HorizonQuotientError(f"{name} action count is outside its bound")
    return layers, states, actions


def _manifest_section(
    manifest: dict[str, Any], name: str, fields: set[str]
) -> dict[str, Any]:
    value = manifest.get(name)
    if type(value) is not dict or set(value) != fields:
        raise HorizonQuotientError(f"manifest {name} section has the wrong fields")
    return value


def _validate_manifest(manifest: dict[str, Any]) -> None:
    if set(manifest) != {
        "schema",
        "source",
        "quotient",
        "mapping",
        "savings",
        "claim_scope",
    }:
        raise HorizonQuotientError("manifest has missing or unknown fields")
    artifact_fields = {
        "file_name",
        "sha256",
        "shape",
        "dtype",
        "order",
        "raw_data_bytes",
        "npy_file_bytes",
    }
    source = _manifest_section(manifest, "source", artifact_fields)
    quotient = _manifest_section(manifest, "quotient", artifact_fields)
    source_shape = _shape(source["shape"], "source")
    quotient_shape = _shape(quotient["shape"], "quotient")
    for name, section, shape in (
        ("source", source, source_shape),
        ("quotient", quotient, quotient_shape),
    ):
        if type(section["file_name"]) is not str or not section["file_name"]:
            raise HorizonQuotientError(f"manifest {name} file name is invalid")
        if (
            type(section["sha256"]) is not str
            or SHA256_PATTERN.fullmatch(section["sha256"]) is None
        ):
            raise HorizonQuotientError(f"manifest {name} SHA-256 is invalid")
        if section["dtype"] != "<f4" or section["order"] != "C":
            raise HorizonQuotientError(f"manifest {name} array format is invalid")
        raw_bytes = int(np.prod(shape)) * np.dtype("<f4").itemsize
        if section["raw_data_bytes"] != raw_bytes:
            raise HorizonQuotientError(f"manifest {name} raw byte count is invalid")
        if (
            type(section["npy_file_bytes"]) is not int
            or section["npy_file_bytes"] < raw_bytes
        ):
            raise HorizonQuotientError(f"manifest {name} NPY byte count is invalid")

    mapping = _manifest_section(
        manifest,
        "mapping",
        {
            "logical_layers",
            "physical_layers",
            "representative_logical_layers",
            "logical_to_physical",
            "physical_layer_sha256",
            "fixed_point_representative_horizon",
            "first_aliased_tail_horizon",
            "equivalence",
        },
    )
    logical_layers = source_shape[0]
    physical_layers = quotient_shape[0]
    if mapping["logical_layers"] != logical_layers:
        raise HorizonQuotientError("manifest logical layer count is invalid")
    if mapping["physical_layers"] != physical_layers:
        raise HorizonQuotientError("manifest physical layer count is invalid")
    if quotient_shape[1:] != source_shape[1:]:
        raise HorizonQuotientError("source and quotient state-action shapes differ")
    layer_map = mapping["logical_to_physical"]
    if type(layer_map) is not list or len(layer_map) != logical_layers:
        raise HorizonQuotientError("logical layer map has the wrong length")
    if any(
        type(item) is not int or not 0 <= item < physical_layers for item in layer_map
    ):
        raise HorizonQuotientError("logical layer map contains an invalid index")
    representatives = mapping["representative_logical_layers"]
    if (
        type(representatives) is not list
        or len(representatives) != physical_layers
        or any(
            type(item) is not int or not 0 <= item < logical_layers
            for item in representatives
        )
        or any(layer_map[item] != index for index, item in enumerate(representatives))
    ):
        raise HorizonQuotientError("representative logical layers are invalid")
    digests = mapping["physical_layer_sha256"]
    if (
        type(digests) is not list
        or len(digests) != physical_layers
        or any(
            type(item) is not str or SHA256_PATTERN.fullmatch(item) is None
            for item in digests
        )
    ):
        raise HorizonQuotientError("physical layer digests are invalid")
    if mapping["equivalence"] != "byte-identical-float32-horizon-slabs":
        raise HorizonQuotientError("manifest declares an unsupported equivalence")
    fixed_point = _fixed_point_representative(layer_map)
    if mapping["fixed_point_representative_horizon"] != fixed_point:
        raise HorizonQuotientError("manifest fixed-point horizon is invalid")
    first_alias = (
        fixed_point + 1
        if fixed_point is not None and fixed_point + 1 < logical_layers
        else None
    )
    if mapping["first_aliased_tail_horizon"] != first_alias:
        raise HorizonQuotientError("manifest first aliased horizon is invalid")

    savings = _manifest_section(
        manifest,
        "savings",
        {"raw_bytes_avoided", "stored_fraction", "lossy"},
    )
    expected_avoided = source["raw_data_bytes"] - quotient["raw_data_bytes"]
    if (
        savings["raw_bytes_avoided"] != expected_avoided
        or savings["stored_fraction"]
        != quotient["raw_data_bytes"] / source["raw_data_bytes"]
        or savings["lossy"] is not False
    ):
        raise HorizonQuotientError("manifest savings section is invalid")
    claims = _manifest_section(
        manifest,
        "claim_scope",
        {
            "all_declared_logical_queries_preserved",
            "future_horizons_beyond_source_supported",
            "knowledge_increased",
            "capacity_recovered_for_future_states",
        },
    )
    if claims != {
        "all_declared_logical_queries_preserved": True,
        "future_horizons_beyond_source_supported": False,
        "knowledge_increased": False,
        "capacity_recovered_for_future_states": True,
    }:
        raise HorizonQuotientError("manifest claim scope is invalid")


def _canonical_manifest(path: str | Path) -> dict[str, Any]:
    raw = Path(path).read_bytes()
    if len(raw) > MAX_MANIFEST_BYTES:
        raise HorizonQuotientError("manifest exceeds its size bound")
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HorizonQuotientError("manifest is not valid UTF-8 JSON") from exc
    if type(value) is not dict or value.get("schema") != MANIFEST_SCHEMA:
        raise HorizonQuotientError("unsupported horizon-quotient manifest")
    try:
        canonical = canonical_json_bytes(value)
    except (TypeError, ValueError) as exc:
        raise HorizonQuotientError("manifest cannot be canonically encoded") from exc
    if raw != canonical:
        raise HorizonQuotientError("manifest is not canonical JSON")
    _validate_manifest(value)
    return value


def _atomic_json(path: str | Path, value: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{target.name}.", dir=target.parent
    )
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(canonical_json_bytes(value))
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o644)
        os.replace(temporary, target)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def _representatives(table: np.ndarray) -> tuple[list[int], list[int], list[str]]:
    representative_layers: list[int] = []
    layer_map: list[int] = []
    digests: list[str] = []
    by_digest: dict[str, list[int]] = {}
    for logical_layer in range(table.shape[0]):
        digest = _layer_digest(table, logical_layer)
        representative = None
        for physical_layer in by_digest.get(digest, []):
            source_layer = representative_layers[physical_layer]
            if np.array_equal(table[logical_layer], table[source_layer]):
                representative = physical_layer
                break
        if representative is None:
            representative = len(representative_layers)
            representative_layers.append(logical_layer)
            digests.append(digest)
            by_digest.setdefault(digest, []).append(representative)
        layer_map.append(representative)
    return representative_layers, layer_map, digests


def _fixed_point_representative(layer_map: list[int]) -> int | None:
    # A single final layer cannot establish a repeated tail. Require at least
    # one later logical horizon to alias the candidate representative.
    for logical_layer, representative in enumerate(layer_map[:-1]):
        if all(item == representative for item in layer_map[logical_layer:]):
            return logical_layer
    return None


def _final_horizon_diversity(table: np.ndarray) -> dict[str, Any]:
    states = int(table.shape[1])
    if states > MAX_EXACT_DIVERSITY_STATES:
        return {
            "exact": False,
            "reason": "state count exceeds the exact diversity-audit bound",
            "state_count": states,
            "unique_action_value_rows": None,
            "greedy_action_counts": None,
        }
    final = np.asarray(table[-1])
    unique_rows = len({row.tobytes(order="C") for row in final})
    greedy = np.argmax(final, axis=1)
    action_counts = np.bincount(greedy, minlength=table.shape[2])
    return {
        "exact": True,
        "reason": None,
        "state_count": states,
        "unique_action_value_rows": unique_rows,
        "greedy_action_counts": [int(item) for item in action_counts],
    }


def build_horizon_quotient(
    source_path: str | Path,
    quotient_path: str | Path,
    manifest_path: str | Path,
) -> dict[str, Any]:
    """Build a lossless quotient of byte-identical logical horizon slabs."""

    source_path = Path(source_path)
    quotient_path = Path(quotient_path)
    manifest_path = Path(manifest_path)
    if source_path.resolve() == quotient_path.resolve():
        raise HorizonQuotientError("source and quotient paths must differ")
    table = _load_table(source_path)
    representative_layers, layer_map, layer_digests = _representatives(table)
    physical_shape = (
        len(representative_layers),
        table.shape[1],
        table.shape[2],
    )

    quotient_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{quotient_path.name}.", dir=quotient_path.parent
    )
    os.close(descriptor)
    os.unlink(temporary)
    try:
        quotient = np.lib.format.open_memmap(
            temporary,
            mode="w+",
            dtype=np.dtype("<f4"),
            shape=physical_shape,
            fortran_order=False,
        )
        for physical_layer, logical_layer in enumerate(representative_layers):
            quotient[physical_layer] = table[logical_layer]
        quotient.flush()
        del quotient
        os.replace(temporary, quotient_path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise

    logical_raw_bytes = int(table.size * table.dtype.itemsize)
    physical_raw_bytes = int(np.prod(physical_shape) * table.dtype.itemsize)
    fixed_point = _fixed_point_representative(layer_map)
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "source": {
            "file_name": source_path.name,
            "sha256": file_sha256(source_path),
            "shape": list(table.shape),
            "dtype": "<f4",
            "order": "C",
            "raw_data_bytes": logical_raw_bytes,
            "npy_file_bytes": source_path.stat().st_size,
        },
        "quotient": {
            "file_name": quotient_path.name,
            "sha256": file_sha256(quotient_path),
            "shape": list(physical_shape),
            "dtype": "<f4",
            "order": "C",
            "raw_data_bytes": physical_raw_bytes,
            "npy_file_bytes": quotient_path.stat().st_size,
        },
        "mapping": {
            "logical_layers": int(table.shape[0]),
            "physical_layers": len(representative_layers),
            "representative_logical_layers": representative_layers,
            "logical_to_physical": layer_map,
            "physical_layer_sha256": layer_digests,
            "fixed_point_representative_horizon": fixed_point,
            "first_aliased_tail_horizon": (
                fixed_point + 1
                if fixed_point is not None and fixed_point + 1 < table.shape[0]
                else None
            ),
            "equivalence": "byte-identical-float32-horizon-slabs",
        },
        "savings": {
            "raw_bytes_avoided": logical_raw_bytes - physical_raw_bytes,
            "stored_fraction": physical_raw_bytes / logical_raw_bytes,
            "lossy": False,
        },
        "claim_scope": {
            "all_declared_logical_queries_preserved": True,
            "future_horizons_beyond_source_supported": False,
            "knowledge_increased": False,
            "capacity_recovered_for_future_states": True,
        },
    }
    _atomic_json(manifest_path, manifest)
    return manifest


def verify_horizon_quotient(
    source_path: str | Path,
    quotient_path: str | Path,
    manifest_path: str | Path,
    *,
    report_path: str | Path | None = None,
    state_chunk: int = 8192,
) -> dict[str, Any]:
    """Replay every logical cell through the quotient mapping."""

    if state_chunk < 1:
        raise HorizonQuotientError("state_chunk must be positive")
    source_path = Path(source_path)
    quotient_path = Path(quotient_path)
    manifest = _canonical_manifest(manifest_path)
    source = _load_table(source_path)
    quotient = _load_table(quotient_path)
    if file_sha256(source_path) != manifest["source"]["sha256"]:
        raise HorizonQuotientError("source SHA-256 does not match manifest")
    if file_sha256(quotient_path) != manifest["quotient"]["sha256"]:
        raise HorizonQuotientError("quotient SHA-256 does not match manifest")
    if list(source.shape) != manifest["source"]["shape"]:
        raise HorizonQuotientError("source shape does not match manifest")
    if list(quotient.shape) != manifest["quotient"]["shape"]:
        raise HorizonQuotientError("quotient shape does not match manifest")
    if source_path.name != manifest["source"]["file_name"]:
        raise HorizonQuotientError("source file name does not match manifest")
    if quotient_path.name != manifest["quotient"]["file_name"]:
        raise HorizonQuotientError("quotient file name does not match manifest")
    if source_path.stat().st_size != manifest["source"]["npy_file_bytes"]:
        raise HorizonQuotientError("source NPY byte count does not match manifest")
    if quotient_path.stat().st_size != manifest["quotient"]["npy_file_bytes"]:
        raise HorizonQuotientError("quotient NPY byte count does not match manifest")
    layer_map = manifest["mapping"]["logical_to_physical"]
    for physical_layer, expected_digest in enumerate(
        manifest["mapping"]["physical_layer_sha256"]
    ):
        if _layer_digest(quotient, physical_layer) != expected_digest:
            raise HorizonQuotientError("physical layer digest does not match manifest")

    mismatch_count = 0
    first_mismatch: dict[str, int] | None = None
    for logical_layer, physical_layer in enumerate(layer_map):
        for start in range(0, source.shape[1], state_chunk):
            stop = min(start + state_chunk, source.shape[1])
            unequal = (
                source[logical_layer, start:stop]
                != quotient[physical_layer, start:stop]
            )
            count = int(np.count_nonzero(unequal))
            mismatch_count += count
            if count and first_mismatch is None:
                row, action = np.argwhere(unequal)[0]
                first_mismatch = {
                    "logical_layer": logical_layer,
                    "state": start + int(row),
                    "action": int(action),
                }
    report = {
        "schema": REPORT_SCHEMA,
        "passed": mismatch_count == 0,
        "source_sha256": manifest["source"]["sha256"],
        "quotient_sha256": manifest["quotient"]["sha256"],
        "logical_shape": list(source.shape),
        "physical_shape": list(quotient.shape),
        "logical_values_checked": int(source.size),
        "mismatch_count": mismatch_count,
        "first_mismatch": first_mismatch,
        "raw_bytes_avoided": manifest["savings"]["raw_bytes_avoided"],
        "final_horizon_diversity": _final_horizon_diversity(source),
        "lossy": False,
    }
    if report_path is not None:
        _atomic_json(report_path, report)
    if mismatch_count:
        raise HorizonQuotientError(
            f"horizon quotient has {mismatch_count} mismatched values"
        )
    return report


def query_horizon_quotient(
    quotient_path: str | Path,
    manifest_path: str | Path,
    logical_layer: int,
    state: int,
    action: int,
) -> float:
    """Return one logical Q value from the physical quotient table."""

    manifest = _canonical_manifest(manifest_path)
    quotient = _load_table(quotient_path)
    if quotient_path.name != manifest["quotient"]["file_name"]:
        raise HorizonQuotientError("quotient file name does not match manifest")
    if file_sha256(quotient_path) != manifest["quotient"]["sha256"]:
        raise HorizonQuotientError("quotient SHA-256 does not match manifest")
    if list(quotient.shape) != manifest["quotient"]["shape"]:
        raise HorizonQuotientError("quotient shape does not match manifest")
    logical_shape = manifest["source"]["shape"]
    if type(logical_layer) is not int or not 0 <= logical_layer < logical_shape[0]:
        raise HorizonQuotientError("logical layer is outside the table")
    if type(state) is not int or not 0 <= state < logical_shape[1]:
        raise HorizonQuotientError("state is outside the table")
    if type(action) is not int or not 0 <= action < logical_shape[2]:
        raise HorizonQuotientError("action is outside the table")
    physical_layer = manifest["mapping"]["logical_to_physical"][logical_layer]
    return float(quotient[physical_layer, state, action])


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build")
    build.add_argument("--source", required=True)
    build.add_argument("--quotient", required=True)
    build.add_argument("--manifest", required=True)
    verify = subparsers.add_parser("verify")
    verify.add_argument("--source", required=True)
    verify.add_argument("--quotient", required=True)
    verify.add_argument("--manifest", required=True)
    verify.add_argument("--report", required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.command == "build":
        result = build_horizon_quotient(args.source, args.quotient, args.manifest)
    else:
        result = verify_horizon_quotient(
            args.source,
            args.quotient,
            args.manifest,
            report_path=args.report,
        )
    print(canonical_json_bytes(result).decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
