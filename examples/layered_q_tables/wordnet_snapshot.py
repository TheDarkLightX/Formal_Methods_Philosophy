"""Convert a pinned Open English WordNet release into a bounded fact graph.

The converter reads a local gzip-compressed GWA-LMF XML file. It never fetches
network data. The source hash, release metadata, roots, relation allowlist, and
all traversal limits are explicit inputs. WordNet relations remain directed
lexical assertions. A downstream planner may browse them in reverse, but that
does not assert an inverse predicate.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
import zlib
from collections.abc import Mapping, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any, BinaryIO

from examples.layered_q_tables.knowledge_q_table import (
    CANONICAL_SNAPSHOT_SCHEMA,
    canonical_json_bytes,
    canonicalize_snapshot,
)

PACK_SCHEMA = "glassmind-wordnet-seeds-v1"
ADAPTER_VERSION = "glassmind-oewn-lmf-adapter-v1"
EXPECTED_RELEASE_VERSION = "2025"
EXPECTED_PACK_LICENSE = "CC-BY-4.0"
EXPECTED_XML_LICENSE = "https://creativecommons.org/licenses/by/4.0"
SYNSET_PATTERN = re.compile(r"^oewn-[0-9]{8}-[nvars]$")
RELATION_PATTERN = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
MAX_SEED_PACK_BYTES = 1024 * 1024
MAX_COMPRESSED_BYTES = 64 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 512 * 1024 * 1024
MAX_ROOTS = 64
MAX_RELATIONS = 32
MAX_SOURCE_SYNSETS = 200_000
MAX_SOURCE_EDGES = 2_000_000
_ALLOWED_OEWN_DOCTYPE = (
    b'<!doctype lexicalresource system '
    b'"http://globalwordnet.github.io/schemas/wn-lmf-1.3.dtd">'
)
_DOCTYPE_MARKER = b"<!doctype"
_DANGEROUS_XML_ASCII_MARKERS = (
    b"<!entity",
    b"<!element",
    b"<!attlist",
    b"<!notation",
    b"<![",
)


def _encoded_xml_marker(marker: bytes, width: int, offset: int) -> bytes:
    return b"".join(
        b"\x00" * offset
        + bytes((byte,))
        + b"\x00" * (width - offset - 1)
        for byte in marker
    )


_DANGEROUS_XML_MARKERS = _DANGEROUS_XML_ASCII_MARKERS + tuple(
    _encoded_xml_marker(marker, width, offset)
    for marker in _DANGEROUS_XML_ASCII_MARKERS + (_DOCTYPE_MARKER,)
    for width in (2, 4)
    for offset in range(width)
)
_XML_SCAN_TAIL_BYTES = max(
    len(_ALLOWED_OEWN_DOCTYPE),
    *(len(marker) for marker in _DANGEROUS_XML_MARKERS),
) - 1


class WordNetSnapshotError(ValueError):
    """A source, proposal pack, bound, or canonical graph failed validation."""


class _BoundedReader:
    def __init__(self, raw: BinaryIO, limit: int) -> None:
        self.raw = raw
        self.limit = limit
        self.count = 0
        self._scan_pending = b""
        self._allowed_doctype_seen = False

    def _scan_xml_declarations(self, data: bytes) -> None:
        pending = self._scan_pending + data.lower()
        if any(marker in pending for marker in _DANGEROUS_XML_MARKERS):
            raise WordNetSnapshotError("WordNet XML contains a forbidden DTD/entity declaration")
        while True:
            start = pending.find(_DOCTYPE_MARKER)
            if start < 0:
                break
            end = pending.find(b">", start)
            if end < 0:
                self._scan_pending = pending[start:]
                return
            declaration = pending[start : end + 1]
            if declaration != _ALLOWED_OEWN_DOCTYPE or self._allowed_doctype_seen:
                raise WordNetSnapshotError(
                    "WordNet XML contains a forbidden DTD/entity declaration"
                )
            self._allowed_doctype_seen = True
            pending = pending[:start] + pending[end + 1 :]
        self._scan_pending = pending[-_XML_SCAN_TAIL_BYTES:]

    def read(self, size: int = -1) -> bytes:
        if size == 0:
            return b""
        remaining = self.limit - self.count
        if remaining < 0:
            raise WordNetSnapshotError("uncompressed WordNet XML exceeds its byte bound")
        request_size = remaining + 1 if size < 0 else min(size, remaining + 1)
        data = self.raw.read(request_size)
        self.count += len(data)
        if self.count > self.limit:
            raise WordNetSnapshotError("uncompressed WordNet XML exceeds its byte bound")
        self._scan_xml_declarations(data)
        return data


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _sha256_stream(handle: BinaryIO) -> str:
    digest = hashlib.sha256()
    while chunk := handle.read(1024 * 1024):
        digest.update(chunk)
    return digest.hexdigest()


def _sha256_file(path: Path) -> str:
    with path.open("rb") as handle:
        return _sha256_stream(handle)


def _validate_timestamp(value: Any) -> str:
    if type(value) is not str or not value.endswith("Z"):
        raise WordNetSnapshotError("retrieved_at must be an ISO-8601 UTC timestamp ending in Z")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise WordNetSnapshotError("retrieved_at must be a valid ISO-8601 timestamp") from exc
    if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise WordNetSnapshotError("retrieved_at must denote UTC")
    return value


def _bounded_int(name: str, value: Any, low: int, high: int) -> int:
    if type(value) is not int or not low <= value <= high:
        raise WordNetSnapshotError(f"{name} must be an integer in [{low}, {high}]")
    return value


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise WordNetSnapshotError(f"duplicate seed-pack JSON key: {key!r}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> None:
    raise WordNetSnapshotError(f"non-finite seed-pack JSON constant is forbidden: {value}")


def load_seed_pack(path: Path) -> dict[str, Any]:
    try:
        raw = Path(path).read_bytes()
        if len(raw) > MAX_SEED_PACK_BYTES:
            raise WordNetSnapshotError("WordNet seed pack exceeds its byte bound")
        pack = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_json_keys,
            parse_constant=_reject_json_constant,
        )
    except WordNetSnapshotError:
        raise
    except (OSError, TypeError, UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise WordNetSnapshotError("WordNet seed pack must be UTF-8 JSON") from exc
    validate_seed_pack(pack)
    return pack


def validate_seed_pack(pack: Any) -> None:
    if type(pack) is not dict or set(pack) != {
        "schema",
        "source",
        "seed_synsets",
        "goal_synsets",
        "relations",
        "assumptions",
        "quarantined_proposals",
    }:
        raise WordNetSnapshotError("WordNet seed pack has missing or unknown fields")
    if pack["schema"] != PACK_SCHEMA:
        raise WordNetSnapshotError(f"WordNet seed pack schema must be {PACK_SCHEMA}")
    source = pack["source"]
    if type(source) is not dict or set(source) != {
        "name",
        "version",
        "url",
        "license",
        "expected_sha256",
    }:
        raise WordNetSnapshotError("WordNet source record has missing or unknown fields")
    if any(type(source[field]) is not str or not source[field] for field in source):
        raise WordNetSnapshotError("WordNet source fields must be non-empty strings")
    if source["version"] != EXPECTED_RELEASE_VERSION:
        raise WordNetSnapshotError(
            f"WordNet source release version must be {EXPECTED_RELEASE_VERSION}"
        )
    if source["license"] != EXPECTED_PACK_LICENSE:
        raise WordNetSnapshotError(
            f"WordNet source license must be {EXPECTED_PACK_LICENSE}"
        )
    if SHA256_PATTERN.fullmatch(source["expected_sha256"]) is None:
        raise WordNetSnapshotError("WordNet expected_sha256 must be lowercase SHA-256")
    if not source["url"].startswith("https://"):
        raise WordNetSnapshotError("WordNet source URL must use HTTPS")

    roots: list[str] = []
    for field in ("seed_synsets", "goal_synsets"):
        values = pack[field]
        if type(values) is not list:
            raise WordNetSnapshotError(f"{field} must be a list")
        for index, item in enumerate(values):
            if type(item) is not dict or set(item) != {"id", "label", "role"}:
                raise WordNetSnapshotError(f"{field}[{index}] has an invalid shape")
            if type(item["id"]) is not str or SYNSET_PATTERN.fullmatch(item["id"]) is None:
                raise WordNetSnapshotError(f"{field}[{index}].id is not an OEWN synset")
            if any(type(item[name]) is not str or not item[name] for name in ("label", "role")):
                raise WordNetSnapshotError(f"{field}[{index}] text fields must be non-empty")
            roots.append(item["id"])
    if not roots or len(roots) > MAX_ROOTS or len(roots) != len(set(roots)):
        raise WordNetSnapshotError("WordNet root synsets must be unique and bounded")

    relations = pack["relations"]
    if (
        type(relations) is not list
        or not 1 <= len(relations) <= MAX_RELATIONS
    ):
        raise WordNetSnapshotError("WordNet relation allowlist is invalid")
    if any(type(item) is not str or RELATION_PATTERN.fullmatch(item) is None for item in relations):
        raise WordNetSnapshotError("WordNet relation allowlist is invalid")
    if len(relations) != len(set(relations)):
        raise WordNetSnapshotError("WordNet relation allowlist is invalid")
    for field in ("assumptions", "quarantined_proposals"):
        if type(pack[field]) is not list or len(pack[field]) > 64:
            raise WordNetSnapshotError(f"{field} must be a bounded list")
    for index, assumption in enumerate(pack["assumptions"]):
        if type(assumption) is not str or not assumption:
            raise WordNetSnapshotError(f"assumptions[{index}] must be a non-empty string")
    for index, proposal in enumerate(pack["quarantined_proposals"]):
        if type(proposal) is not dict or set(proposal) != {"proposal", "reason"}:
            raise WordNetSnapshotError(f"quarantined_proposals[{index}] has an invalid shape")
        if any(
            type(proposal[field]) is not str or not proposal[field]
            for field in ("proposal", "reason")
        ):
            raise WordNetSnapshotError(
                f"quarantined_proposals[{index}] text fields must be non-empty"
            )


def _parse_source(
    source_path: Path,
    *,
    expected_sha256: str,
    relation_allowlist: set[str],
) -> tuple[dict[str, str], dict[str, dict[str, Any]], dict[str, tuple[tuple[str, str], ...]]]:
    try:
        source_path = Path(source_path)
        if not source_path.is_file():
            raise WordNetSnapshotError("WordNet source file does not exist")

        with source_path.open("rb") as source_handle:
            source_handle.seek(0, 2)
            compressed_size = source_handle.tell()
            if compressed_size > MAX_COMPRESSED_BYTES:
                raise WordNetSnapshotError(
                    "compressed WordNet source exceeds its byte bound"
                )
            source_handle.seek(0)
            source_sha256 = _sha256_stream(source_handle)
            if source_sha256 != expected_sha256:
                raise WordNetSnapshotError(
                    "WordNet source hash does not match the pinned release"
                )
            source_handle.seek(0)

            entry_labels: dict[str, str] = {}
            synset_records: dict[str, dict[str, Any]] = {}
            lexicon_meta: dict[str, str] = {}
            seen_entry_ids: set[str] = set()
            stack: list[ET.Element] = []
            lexicon_count = 0
            source_synset_count = 0
            source_relation_count = 0

            with gzip.GzipFile(fileobj=source_handle, mode="rb") as compressed:
                bounded = _BoundedReader(compressed, MAX_UNCOMPRESSED_BYTES)
                for event, element in ET.iterparse(bounded, events=("start", "end")):
                    tag = _local_name(element.tag)
                    if event == "start":
                        stack.append(element)
                        if tag == "Lexicon":
                            lexicon_count += 1
                            if lexicon_count > 1:
                                raise WordNetSnapshotError(
                                    "WordNet source must contain exactly one Lexicon"
                                )
                            lexicon_meta = {
                                field: element.attrib.get(field, "")
                                for field in (
                                    "id",
                                    "label",
                                    "language",
                                    "license",
                                    "version",
                                    "url",
                                )
                            }
                        elif tag == "Synset":
                            source_synset_count += 1
                            if source_synset_count > MAX_SOURCE_SYNSETS:
                                raise WordNetSnapshotError(
                                    "WordNet synset count exceeds its source bound"
                                )
                        elif tag == "SynsetRelation":
                            source_relation_count += 1
                            if source_relation_count > MAX_SOURCE_EDGES:
                                raise WordNetSnapshotError(
                                    "WordNet relation count exceeds its source bound"
                                )
                        continue

                    if tag == "LexicalEntry":
                        entry_id = element.attrib.get("id")
                        if type(entry_id) is str and entry_id:
                            if entry_id in seen_entry_ids:
                                raise WordNetSnapshotError(
                                    "WordNet source contains duplicate lexical-entry IDs"
                                )
                            seen_entry_ids.add(entry_id)
                            lemma = next(
                                (
                                    child
                                    for child in element
                                    if _local_name(child.tag) == "Lemma"
                                ),
                                None,
                            )
                            label = (
                                lemma.attrib.get("writtenForm")
                                if lemma is not None
                                else None
                            )
                            if type(label) is str and label:
                                entry_labels[entry_id] = label
                    elif tag == "Synset":
                        synset_id = element.attrib.get("id")
                        if type(synset_id) is str and SYNSET_PATTERN.fullmatch(synset_id):
                            if synset_id in synset_records:
                                raise WordNetSnapshotError(
                                    "WordNet source contains duplicate synset IDs"
                                )
                            member_ids = element.attrib.get("members", "").split()
                            definition = next(
                                (
                                    "".join(child.itertext()).strip()
                                    for child in element
                                    if _local_name(child.tag) == "Definition"
                                ),
                                "",
                            )
                            relation_rows = sorted(
                                {
                                    (
                                        child.attrib.get("relType", ""),
                                        child.attrib.get("target", ""),
                                    )
                                    for child in element
                                    if _local_name(child.tag) == "SynsetRelation"
                                    and child.attrib.get("relType")
                                    in relation_allowlist
                                    and type(child.attrib.get("target")) is str
                                    and SYNSET_PATTERN.fullmatch(
                                        child.attrib.get("target", "")
                                    )
                                }
                            )
                            synset_records[synset_id] = {
                                "members": member_ids,
                                "definition": definition,
                                "relations": relation_rows,
                                "part_of_speech": element.attrib.get(
                                    "partOfSpeech", ""
                                ),
                                "ili": element.attrib.get("ili", ""),
                                "lexfile": element.attrib.get("lexfile", ""),
                            }

                    if tag in {"LexicalEntry", "Synset"}:
                        element.clear()
                        if len(stack) >= 2:
                            try:
                                stack[-2].remove(element)
                            except ValueError:
                                pass
                    stack.pop()

            if lexicon_count != 1:
                raise WordNetSnapshotError(
                    "WordNet source must contain exactly one Lexicon"
                )

            nodes: dict[str, dict[str, Any]] = {}
            adjacency: dict[str, tuple[tuple[str, str], ...]] = {}
            for synset_id in sorted(synset_records):
                record = synset_records[synset_id]
                aliases = sorted(
                    {
                        entry_labels[entry_id]
                        for entry_id in record["members"]
                        if entry_id in entry_labels
                    }
                )
                nodes[synset_id] = {
                    "id": synset_id,
                    "label": aliases[0] if aliases else None,
                    "description": record["definition"] or None,
                    "provenance": {
                        "source_record": synset_id,
                        "part_of_speech": record["part_of_speech"],
                        "ili": record["ili"],
                        "lexfile": record["lexfile"],
                        "aliases": aliases,
                    },
                }
                adjacency[synset_id] = tuple(record["relations"])
    except WordNetSnapshotError:
        raise
    except (ET.ParseError, OSError, EOFError, UnicodeError, ValueError, zlib.error) as exc:
        raise WordNetSnapshotError("WordNet source is not valid bounded gzip XML") from exc
    return lexicon_meta, nodes, adjacency


def build_snapshot(
    source_path: Path,
    pack: Mapping[str, Any],
    *,
    retrieved_at: str,
    max_nodes: int,
    min_nodes: int,
    max_depth: int,
    max_relations_per_node: int,
) -> dict[str, Any]:
    validate_seed_pack(pack)
    retrieved_at = _validate_timestamp(retrieved_at)
    max_nodes = _bounded_int("max_nodes", max_nodes, 1, 4096)
    min_nodes = _bounded_int("min_nodes", min_nodes, 1, max_nodes)
    max_depth = _bounded_int("max_depth", max_depth, 0, 32)
    max_relations_per_node = _bounded_int(
        "max_relations_per_node", max_relations_per_node, 1, 64
    )
    roots = tuple(
        sorted(
            item["id"]
            for field in ("seed_synsets", "goal_synsets")
            for item in pack[field]
        )
    )
    if len(roots) > max_nodes:
        raise WordNetSnapshotError("max_nodes is smaller than the declared roots")

    lexicon, all_nodes, adjacency = _parse_source(
        source_path,
        expected_sha256=pack["source"]["expected_sha256"],
        relation_allowlist=set(pack["relations"]),
    )
    missing_ids = sorted(set(roots) - set(all_nodes))
    if missing_ids:
        raise WordNetSnapshotError("pinned WordNet roots are missing: " + ", ".join(missing_ids))
    if lexicon.get("version") != EXPECTED_RELEASE_VERSION:
        raise WordNetSnapshotError(
            f"WordNet release version must be exactly {EXPECTED_RELEASE_VERSION}"
        )
    if lexicon.get("license") != EXPECTED_XML_LICENSE:
        raise WordNetSnapshotError(
            "WordNet source license must be exactly the expected CC-BY license"
        )
    expected_labels = {
        item["id"]: item["label"]
        for field in ("seed_synsets", "goal_synsets")
        for item in pack[field]
    }
    for synset_id, expected_label in expected_labels.items():
        aliases = all_nodes[synset_id]["provenance"]["aliases"]
        if expected_label.casefold() not in {item.casefold() for item in aliases}:
            raise WordNetSnapshotError(
                f"seed label {expected_label!r} does not identify {synset_id}"
            )

    selected = set(roots)
    frontier = set(roots)
    truncated = False
    for depth in range(max_depth + 1):
        if not frontier:
            break
        next_frontier: set[str] = set()
        for source in sorted(frontier):
            rows = adjacency.get(source, ())
            if len(rows) > max_relations_per_node:
                truncated = True
            for _, target in rows[:max_relations_per_node]:
                if target not in all_nodes or target in selected:
                    continue
                if depth >= max_depth or len(selected) >= max_nodes:
                    truncated = True
                    continue
                selected.add(target)
                next_frontier.add(target)
        frontier = next_frontier
    if len(selected) < min_nodes:
        raise WordNetSnapshotError(
            f"bounded traversal produced {len(selected)} nodes, below min_nodes={min_nodes}"
        )
    nodes = [all_nodes[synset_id] for synset_id in sorted(selected)]
    edges: list[dict[str, Any]] = []
    for source in sorted(selected):
        rows = adjacency.get(source, ())
        for relation, target in rows[:max_relations_per_node]:
            if target in selected:
                edges.append(
                    {
                        "source": source,
                        "relation": relation,
                        "target": target,
                        "source_direction": "oewn_synset_relation_source_to_target",
                        "provenance": {
                            "adapter": ADAPTER_VERSION,
                            "source_record": source,
                        },
                    }
                )
    edges.sort(
        key=lambda item: (
            item["source"],
            item["relation"],
            item["target"],
            item["source_direction"],
        )
    )
    graph = {"nodes": nodes, "edges": edges}
    snapshot = {
        "schema": CANONICAL_SNAPSHOT_SCHEMA,
        "provenance": {
            "source_name": pack["source"]["name"],
            "source_version": pack["source"]["version"],
            "source_url": pack["source"]["url"],
            "source_sha256": pack["source"]["expected_sha256"],
            "license": pack["source"]["license"],
            "retrieved_at": retrieved_at,
            "adapter": ADAPTER_VERSION,
            "canonical_graph_sha256": hashlib.sha256(canonical_json_bytes(graph)).hexdigest(),
            "nonclaims": [
                "WordNet relations are attributed lexical links, not formal proofs or normative rules.",
                "Reverse graph browsing does not assert an inverse lexical predicate.",
                "The bounded graph is incomplete and absence of a path is not a real-world negative claim.",
            ],
        },
        "counts": {"nodes": len(nodes), "edges": len(edges)},
        "graph": graph,
        "missing_ids": [],
        "truncated": truncated,
        "slot_policy": {"mode": "explicit_abstain_only"},
    }
    try:
        return canonicalize_snapshot(snapshot)
    except WordNetSnapshotError:
        raise
    except ValueError as exc:
        raise WordNetSnapshotError(
            "generated WordNet snapshot failed canonical validation"
        ) from exc


def _write_atomic(path: Path, payload: bytes) -> None:
    temporary_path: Path | None = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=path.parent,
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        temporary_path.replace(path)
    except OSError as exc:
        raise WordNetSnapshotError("WordNet snapshot output could not be written") from exc
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass
            except OSError:
                pass


def _main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--seed-pack", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--retrieved-at", required=True)
    parser.add_argument("--max-nodes", type=int, default=256)
    parser.add_argument("--min-nodes", type=int, default=256)
    parser.add_argument("--max-depth", type=int, default=6)
    parser.add_argument("--max-relations-per-node", type=int, default=12)
    args = parser.parse_args(argv)
    try:
        pack = load_seed_pack(args.seed_pack)
        snapshot = build_snapshot(
            args.source,
            pack,
            retrieved_at=args.retrieved_at,
            max_nodes=args.max_nodes,
            min_nodes=args.min_nodes,
            max_depth=args.max_depth,
            max_relations_per_node=args.max_relations_per_node,
        )
        _write_atomic(args.output, canonical_json_bytes(snapshot))
        return 0
    except WordNetSnapshotError as exc:
        sys.stderr.write(f"wordnet_snapshot: {exc}\n")
        return 2


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
