#!/usr/bin/env python3
"""Build a small, deterministic Wikidata graph for a GlassMind planner.

The network client is deliberately a narrow shell.  Parsing, ordering, and
the breadth-first bound are deterministic and can be exercised with a local
fetcher, so tests never contact Wikidata.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence
from urllib.parse import urlencode
from urllib.error import HTTPError
from urllib.request import Request, urlopen


DEFAULT_ENDPOINT = "https://www.wikidata.org/w/api.php"
DEFAULT_USER_AGENT = "GlassMind-256/1.0 (https://github.com/TheDarkLightX/FormalPhilosophy; bounded educational snapshot)"
QID_PATTERN = re.compile(r"^Q[1-9][0-9]*$")
PID_PATTERN = re.compile(r"^P[1-9][0-9]*$")
MAX_API_BATCH = 50
MAX_SEEDS = 64
MAX_RELATIONS = 32
MAX_RESPONSE_BYTES = 32 * 1024 * 1024
SNAPSHOT_VERSION = 1


class SnapshotError(ValueError):
    """Raised when a seed pack or bounded build parameter is invalid."""


def _is_qid(value: Any) -> bool:
    return type(value) is str and QID_PATTERN.fullmatch(value) is not None


def _is_pid(value: Any) -> bool:
    return type(value) is str and PID_PATTERN.fullmatch(value) is not None


def _bounded_int(name: str, value: Any, low: int, high: int) -> int:
    if type(value) is not int or not low <= value <= high:
        raise SnapshotError(f"{name} must be an integer in [{low}, {high}]")
    return value


def _canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_seed_pack(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    try:
        pack = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SnapshotError("seed pack is not valid UTF-8 JSON") from exc
    if not isinstance(pack, dict):
        raise SnapshotError("seed pack must be a JSON object")
    _validate_seed_pack(pack)
    return pack, raw


def _validate_seed_pack(pack: Mapping[str, Any]) -> None:
    if pack.get("schema_version") != 1:
        raise SnapshotError("seed pack schema_version must be 1")
    for field in ("seed_qids", "goal_proposals", "relation_pids"):
        if not isinstance(pack.get(field), list):
            raise SnapshotError(f"seed pack field {field!r} must be a list")
    if len(pack["seed_qids"]) + len(pack["goal_proposals"]) > MAX_SEEDS:
        raise SnapshotError(f"seed pack may contain at most {MAX_SEEDS} QID proposals")
    if not 1 <= len(pack["relation_pids"]) <= MAX_RELATIONS:
        raise SnapshotError(
            f"seed pack must contain between 1 and {MAX_RELATIONS} relation PIDs"
        )
    qids: list[str] = []
    for field in ("seed_qids", "goal_proposals"):
        for value in pack[field]:
            qid = value.get("qid") if isinstance(value, dict) else value
            if not _is_qid(qid):
                raise SnapshotError(f"invalid QID in {field}: {qid!r}")
            qids.append(qid)
            if isinstance(value, dict):
                for text_field in ("role", "hypothesis"):
                    if text_field in value and not isinstance(value[text_field], str):
                        raise SnapshotError(
                            f"{field} {text_field!r} must be a string when present"
                        )
    if len(qids) != len(set(qids)):
        raise SnapshotError("seed and goal QIDs must be unique")
    pids: list[str] = []
    for pid in pack["relation_pids"]:
        value = pid.get("pid") if isinstance(pid, dict) else pid
        if not _is_pid(value):
            raise SnapshotError(f"invalid PID in relation_pids: {value!r}")
        pids.append(value)
        if isinstance(pid, dict) and "label" in pid and not isinstance(pid["label"], str):
            raise SnapshotError("relation PID labels must be strings when present")
    if len(pids) != len(set(pids)):
        raise SnapshotError("relation PIDs must be unique")
    if "hypotheses" in pack and not isinstance(pack["hypotheses"], list):
        raise SnapshotError("hypotheses must be a list")
    if "quarantined_proposals" in pack and not isinstance(pack["quarantined_proposals"], list):
        raise SnapshotError("quarantined_proposals must be a list")


def _seed_qids(pack: Mapping[str, Any]) -> tuple[str, ...]:
    values = []
    for field in ("seed_qids", "goal_proposals"):
        for item in pack[field]:
            values.append(item.get("qid") if isinstance(item, dict) else item)
    return tuple(sorted(set(values)))


def _relation_pids(pack: Mapping[str, Any]) -> tuple[str, ...]:
    values = [item.get("pid") if isinstance(item, dict) else item for item in pack["relation_pids"]]
    return tuple(sorted(set(values)))


def _validate_limits(limits: Mapping[str, Any]) -> dict[str, int]:
    checked = {
        "max_nodes": _bounded_int("max_nodes", limits.get("max_nodes", 100), 1, 10000),
        "min_nodes": _bounded_int("min_nodes", limits.get("min_nodes", 1), 1, 10000),
        "max_requests": _bounded_int("max_requests", limits.get("max_requests", 20), 1, 1000),
        "max_depth": _bounded_int("max_depth", limits.get("max_depth", 2), 0, 20),
        "batch_size": _bounded_int("batch_size", limits.get("batch_size", 20), 1, MAX_API_BATCH),
        "max_targets_per_entity": _bounded_int(
            "max_targets_per_entity",
            limits.get("max_targets_per_entity", 12),
            1,
            256,
        ),
    }
    if checked["min_nodes"] > checked["max_nodes"]:
        raise SnapshotError("min_nodes must not exceed max_nodes")
    return checked


def _claim_edges(entity: Mapping[str, Any], relation_pids: set[str]) -> set[tuple[str, str, str]]:
    source = entity.get("id")
    if not _is_qid(source):
        return set()
    edges: set[tuple[str, str, str]] = set()
    claims = entity.get("claims", {})
    if not isinstance(claims, dict):
        return edges
    for pid in sorted(relation_pids):
        if not _is_pid(pid) or not isinstance(claims.get(pid), list):
            continue
        for claim in claims[pid]:
            if not isinstance(claim, dict) or claim.get("rank") == "deprecated":
                continue
            value = claim.get("mainsnak", {}).get("datavalue", {}) if isinstance(claim.get("mainsnak"), dict) else {}
            target = value.get("value", {}).get("id") if value.get("type") == "wikibase-entityid" and isinstance(value.get("value"), dict) else None
            if _is_qid(target):
                edges.add((source, pid, target))
    return edges


def _node(entity: Mapping[str, Any]) -> dict[str, Any] | None:
    qid = entity.get("id")
    if not _is_qid(qid):
        return None
    labels = entity.get("labels", {})
    descriptions = entity.get("descriptions", {})
    label = labels.get("en", {}).get("value") if isinstance(labels, dict) and isinstance(labels.get("en"), dict) else None
    description = descriptions.get("en", {}).get("value") if isinstance(descriptions, dict) and isinstance(descriptions.get("en"), dict) else None
    result: dict[str, Any] = {
        "qid": qid,
        "label": label if type(label) is str else None,
        "description": description if type(description) is str else None,
        "revision": {},
    }
    if type(entity.get("lastrevid")) is int:
        result["revision"]["lastrevid"] = entity["lastrevid"]
    if type(entity.get("modified")) is str:
        result["revision"]["modified"] = entity["modified"]
    return result


def _extract_entities(response: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    if "error" in response:
        error = response["error"]
        code = error.get("code", "unknown") if isinstance(error, dict) else "unknown"
        info = error.get("info", "no details") if isinstance(error, dict) else str(error)
        raise SnapshotError(f"Wikidata API error {code}: {info}")
    entities = response.get("entities", {})
    if not isinstance(entities, dict):
        raise SnapshotError("API response entities must be an object")
    return {qid: entity for qid, entity in entities.items() if _is_qid(qid) and isinstance(entity, dict) and not entity.get("missing", False)}


def traverse(
    seed_qids: Sequence[str],
    relation_pids: Sequence[str],
    limits: Mapping[str, Any],
    fetch: Callable[[tuple[str, ...]], Mapping[str, Any]],
) -> dict[str, Any]:
    """Perform deterministic BFS using a caller-supplied response fetcher."""
    checked_limits = _validate_limits(limits)
    if any(not _is_qid(qid) for qid in seed_qids) or any(not _is_pid(pid) for pid in relation_pids):
        raise SnapshotError("invalid traversal QID or PID")
    if not seed_qids:
        raise SnapshotError("traversal requires at least one seed QID")
    canonical_seeds = tuple(sorted(set(seed_qids)))
    if len(canonical_seeds) > checked_limits["max_nodes"]:
        raise SnapshotError("max_nodes is smaller than the number of unique seeds")

    nodes: dict[str, dict[str, Any]] = {}
    edges: set[tuple[str, str, str]] = set()
    missing: set[str] = set()
    pending = set(canonical_seeds)
    scheduled = set(canonical_seeds)
    requested: set[str] = set()
    request_count = 0
    truncated = False
    relation_set = set(relation_pids)

    for depth in range(checked_limits["max_depth"] + 1):
        current = sorted(pending - requested)
        pending = set()
        if not current:
            break
        for start in range(0, len(current), checked_limits["batch_size"]):
            batch = tuple(current[start : start + checked_limits["batch_size"]])
            if request_count >= checked_limits["max_requests"]:
                truncated = True
                pending.update(current[start:])
                break
            request_count += 1
            requested.update(batch)
            response = fetch(batch)
            returned = _extract_entities(response)
            for qid in batch:
                if qid not in returned:
                    missing.add(qid)
            for qid in sorted(returned):
                parsed = _node(returned[qid])
                if parsed is None:
                    missing.add(qid)
                    continue
                nodes.setdefault(qid, parsed)
                entity_edges = sorted(_claim_edges(returned[qid], relation_set))
                if len(entity_edges) > checked_limits["max_targets_per_entity"]:
                    truncated = True
                for edge in entity_edges[: checked_limits["max_targets_per_entity"]]:
                    target = edge[2]
                    if target not in scheduled:
                        if depth >= checked_limits["max_depth"]:
                            truncated = True
                            continue
                        if len(scheduled) >= checked_limits["max_nodes"]:
                            truncated = True
                            continue
                        scheduled.add(target)
                    edges.add(edge)
                    if target not in requested:
                        pending.add(target)
            if request_count >= checked_limits["max_requests"] and (
                start + checked_limits["batch_size"] < len(current) or pending
            ):
                truncated = True
                pending.update(current[start + checked_limits["batch_size"] :])
                break
        if request_count >= checked_limits["max_requests"]:
            break

    if pending or scheduled - requested:
        truncated = True
    final_qids = set(nodes)
    canonical_edges = [{"source": source, "pid": pid, "target": target} for source, pid, target in sorted(edges) if source in final_qids and target in final_qids]
    return {
        "nodes": [nodes[qid] for qid in sorted(nodes)],
        "edges": canonical_edges,
        "missing_qids": sorted(missing),
        "truncated": truncated,
        "request_count": request_count,
    }


class WikidataClient:
    def __init__(self, endpoint: str = DEFAULT_ENDPOINT, cache_dir: Path | None = None, timeout: float = 10.0, retries: int = 2, maxlag: int = 5, request_delay: float = 0.25, user_agent: str = DEFAULT_USER_AGENT):
        if not endpoint.startswith("https://"):
            raise SnapshotError("endpoint must use HTTPS")
        if type(timeout) not in (int, float) or not 0.1 <= timeout <= 120:
            raise SnapshotError("timeout must be in [0.1, 120]")
        self.endpoint, self.cache_dir, self.timeout = endpoint, cache_dir, timeout
        self.retries = _bounded_int("retries", retries, 0, 10)
        self.maxlag = _bounded_int("maxlag", maxlag, 1, 120)
        if type(request_delay) not in (int, float) or not 0.0 <= request_delay <= 10.0:
            raise SnapshotError("request_delay must be in [0, 10]")
        self.request_delay = float(request_delay)
        self.user_agent = user_agent

    def fetch(self, qids: tuple[str, ...]) -> Mapping[str, Any]:
        if not qids or len(qids) > MAX_API_BATCH or any(not _is_qid(qid) for qid in qids):
            raise SnapshotError("invalid API batch")
        params = {"action": "wbgetentities", "format": "json", "formatversion": "2", "ids": "|".join(sorted(qids)), "props": "info|labels|descriptions|claims", "languages": "en", "languagefallback": "0", "maxlag": str(self.maxlag)}
        cache_key = _sha256_bytes(_canonical_json(params))
        cache_path = self.cache_dir / f"{cache_key}.json" if self.cache_dir else None
        if cache_path and cache_path.exists():
            try:
                cached = json.loads(cache_path.read_text(encoding="utf-8"))
                if not isinstance(cached, dict):
                    raise SnapshotError("cached API response must be an object")
                _extract_entities(cached)
                return cached
            except (OSError, ValueError, SnapshotError):
                # A stale error envelope or partial cache entry is never evidence.
                pass
        encoded = urlencode(params).encode("ascii")
        request = Request(self.endpoint + "?" + encoded.decode("ascii"), headers={"User-Agent": self.user_agent, "Accept": "application/json"})
        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                with urlopen(request, timeout=self.timeout) as response:
                    raw = response.read(MAX_RESPONSE_BYTES + 1)
                    if len(raw) > MAX_RESPONSE_BYTES:
                        raise SnapshotError("Wikidata response exceeds the byte bound")
                    payload = json.loads(raw.decode("utf-8"))
                if not isinstance(payload, dict):
                    raise SnapshotError("API response must be an object")
                _extract_entities(payload)
                if cache_path:
                    cache_path.parent.mkdir(parents=True, exist_ok=True)
                    cache_path.write_bytes(_canonical_json(payload))
                if self.request_delay:
                    time.sleep(self.request_delay)
                return payload
            except (OSError, ValueError, SnapshotError) as exc:
                last_error = exc
                if attempt < self.retries:
                    delay = min(15.0, 0.5 * (2**attempt))
                    if isinstance(exc, HTTPError) and exc.code == 429:
                        retry_after = exc.headers.get("Retry-After")
                        try:
                            delay = max(delay, min(30.0, float(retry_after)))
                        except (TypeError, ValueError):
                            delay = max(delay, 5.0)
                    time.sleep(delay)
        raise SnapshotError(f"Wikidata request failed after {self.retries + 1} attempts: {last_error}") from last_error


def build_snapshot(pack: Mapping[str, Any], seed_pack_bytes: bytes, *, limits: Mapping[str, Any], fetch: Callable[[tuple[str, ...]], Mapping[str, Any]], retrieved_at: str, endpoint: str | None = None) -> dict[str, Any]:
    _validate_seed_pack(pack)
    try:
        parsed_time = datetime.fromisoformat(retrieved_at.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise SnapshotError("retrieved_at must be an ISO-8601 UTC timestamp") from exc
    if not retrieved_at.endswith("Z") or parsed_time.utcoffset() is None or parsed_time.utcoffset().total_seconds() != 0:
        raise SnapshotError("retrieved_at must be an ISO-8601 UTC timestamp ending in Z")
    checked_limits = _validate_limits(limits)
    seed_qids = _seed_qids(pack)
    graph = traverse(seed_qids, _relation_pids(pack), checked_limits, fetch)
    if len(graph["nodes"]) < checked_limits["min_nodes"]:
        raise SnapshotError(
            f"snapshot produced {len(graph['nodes'])} nodes, below min_nodes={checked_limits['min_nodes']}"
        )
    present_qids = {node["qid"] for node in graph["nodes"]}
    unresolved_seed_qids = sorted(set(seed_qids) - present_qids)
    if limits.get("require_all_seeds", False) is True and unresolved_seed_qids:
        raise SnapshotError(
            "snapshot is missing required seed QIDs: " + ", ".join(unresolved_seed_qids)
        )
    graph_bytes = _canonical_json({"nodes": graph["nodes"], "edges": graph["edges"]})
    fetch_owner = getattr(fetch, "__self__", None)
    resolved_endpoint = endpoint or getattr(fetch, "endpoint", None) or getattr(fetch_owner, "endpoint", None) or "fixture://local"
    observed_properties = sorted({edge["pid"] for edge in graph["edges"]})
    return {
        "snapshot_version": SNAPSHOT_VERSION,
        "provenance": {
            "endpoint": resolved_endpoint,
            "retrieved_at": retrieved_at,
            "seed_pack_sha256": _sha256_bytes(seed_pack_bytes),
            "canonical_graph_sha256": _sha256_bytes(graph_bytes),
            "license": "CC0-1.0",
            "nonclaims": ["This bounded snapshot does not validate the LLM seed proposals.", "It is neither complete nor a correctness proof of Wikidata facts.", "Freshness and coverage are limited by the configured traversal bounds."],
        },
        "limits": checked_limits,
        "counts": {
            "nodes": len(graph["nodes"]),
            "edges": len(graph["edges"]),
            "declared_properties": len(_relation_pids(pack)),
            "observed_properties": len(observed_properties),
            "requests": graph["request_count"],
        },
        "graph": {"nodes": graph["nodes"], "edges": graph["edges"]},
        "missing_qids": graph["missing_qids"],
        "unresolved_seed_qids": unresolved_seed_qids,
        "seed_coverage": {
            "present": len(seed_qids) - len(unresolved_seed_qids),
            "required": len(seed_qids),
        },
        "truncated": graph["truncated"],
    }


def _main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build", help="download and build a bounded snapshot")
    build.add_argument("--seed-pack", type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)
    build.add_argument("--cache-dir", type=Path)
    build.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    build.add_argument("--retrieved-at", required=True, help="UTC timestamp captured by the caller")
    build.add_argument("--max-nodes", type=int, default=100)
    build.add_argument("--min-nodes", type=int, default=1)
    build.add_argument("--max-requests", type=int, default=20)
    build.add_argument("--max-depth", type=int, default=2)
    build.add_argument("--batch-size", type=int, default=20)
    build.add_argument("--max-targets-per-entity", type=int, default=12)
    build.add_argument("--maxlag", type=int, default=5)
    build.add_argument("--retries", type=int, default=2)
    build.add_argument("--timeout", type=float, default=10.0)
    build.add_argument("--request-delay", type=float, default=0.25)
    build.add_argument("--require-all-seeds", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "build":
        pack, raw = load_seed_pack(args.seed_pack)
        client = WikidataClient(
            endpoint=args.endpoint,
            cache_dir=args.cache_dir,
            timeout=args.timeout,
            retries=args.retries,
            maxlag=args.maxlag,
            request_delay=args.request_delay,
        )
        snapshot = build_snapshot(pack, raw, limits=vars(args), fetch=client.fetch, retrieved_at=args.retrieved_at, endpoint=client.endpoint)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(_canonical_json(snapshot))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
