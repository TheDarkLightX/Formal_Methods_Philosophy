#!/usr/bin/env python3
"""Bounded reference model for an ADD-only semantic conflict hypergraph.

Tau is represented by a tri-valued consistency-oracle interface. The bundled
demo uses a tiny exhaustive propositional oracle so that the hypergraph and
implicit hitting-set algorithm can be replayed without third-party packages.

This is a reference model, not a network protocol or a Tau proof checker.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass, field
from enum import Enum
from itertools import combinations, product
from math import inf
from typing import Any, Protocol

ProposalId = str
ProposalSet = frozenset[ProposalId]
EDGE_SCHEMA = "formal-philosophy.tau-semantic-conflict-edge.v1"
PROPOSAL_MANIFEST_SCHEMA = (
    "formal-philosophy.tau-semantic-proposal-manifest.v1"
)
RESOLUTION_CERTIFICATE_SCHEMA = (
    "formal-philosophy.tau-semantic-resolution-certificate.v1"
)
RESOURCE_BUDGET_SCHEMA = "formal-philosophy.tau-resolution-budget.v1"
SUPPORTED_RESOLUTION_POLICY = (
    "minimum-reject-cost-then-cardinality-then-lexicographic"
    "+sorted-mus-v1"
)


def _require_sha256(value: str, name: str) -> None:
    if len(value) != 64:
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")
    try:
        parsed = bytes.fromhex(value)
    except ValueError as error:
        raise ValueError(
            f"{name} must be a lowercase SHA-256 digest"
        ) from error
    if len(parsed) != 32 or value != value.lower():
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")


class Verdict(Enum):
    SAT = "SAT"
    UNSAT = "UNSAT"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class OracleResult:
    verdict: Verdict
    witness: object | None = None
    reason: str | None = None


class ConsistencyOracle(Protocol):
    """Monotone consistency oracle relative to one fixed base law."""

    def check(self, proposals: ProposalSet) -> OracleResult:
        ...


@dataclass(frozen=True)
class Proposal:
    proposal_id: ProposalId
    reject_cost: int = 1
    dependencies: frozenset[ProposalId] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        object.__setattr__(self, "dependencies", frozenset(self.dependencies))
        if not self.proposal_id:
            raise ValueError("proposal_id must be non-empty")
        if self.reject_cost < 0:
            raise ValueError("reject_cost must be non-negative")
        if self.proposal_id in self.dependencies:
            raise ValueError("a proposal cannot depend on itself")


@dataclass(frozen=True)
class ProposalRecord:
    """One content-bound proposal entry in a canonical epoch manifest."""

    proposal: Proposal
    payload_hash: str

    def __post_init__(self) -> None:
        _require_sha256(self.payload_hash, "payload_hash")

    def manifest_entry(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal.proposal_id,
            "payload_hash": self.payload_hash,
            "reject_cost": self.proposal.reject_cost,
            "dependencies": sorted(self.proposal.dependencies),
        }


@dataclass(frozen=True)
class ResolutionBudget:
    max_iterations: int = 128
    max_master_candidates_per_iteration: int = 1_000_000

    def __post_init__(self) -> None:
        if self.max_iterations <= 0:
            raise ValueError("max_iterations must be positive")
        if self.max_master_candidates_per_iteration <= 0:
            raise ValueError(
                "max_master_candidates_per_iteration must be positive"
            )


@dataclass(frozen=True)
class Resolution:
    accepted: ProposalSet
    rejected: ProposalSet
    discovered_edges: tuple[ProposalSet, ...]
    rejection_cost: int
    iterations: int


@dataclass(frozen=True)
class EdgeSubject:
    """The complete semantic subject bound into a conflict-edge identity."""

    domain_id: str
    epoch_id: str
    base_law_root: str
    proposal_set_root: str
    oracle_semantics_id: str

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            if not isinstance(value, str) or not value:
                raise ValueError(f"{name} must be a non-empty string")


@dataclass(frozen=True)
class EpochContext:
    """The semantic and policy context shared before an epoch is resolved."""

    domain_id: str
    epoch_id: str
    base_law_root: str
    oracle_semantics_id: str
    resolution_policy_id: str
    resource_budget_root: str

    def __post_init__(self) -> None:
        for name in (
            "domain_id",
            "epoch_id",
            "oracle_semantics_id",
            "resolution_policy_id",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise ValueError(f"{name} must be a non-empty string")
        _require_sha256(self.base_law_root, "base_law_root")
        _require_sha256(self.resource_budget_root, "resource_budget_root")


@dataclass(frozen=True)
class SealedEpoch:
    """A canonical finite ADD snapshot. Arrival order is no longer semantic."""

    context: EpochContext
    records: tuple[ProposalRecord, ...]
    proposal_set_root: str


@dataclass(frozen=True)
class CertifiedResolution:
    """A replayable, subject-bound result for one sealed reference epoch."""

    context: EpochContext
    proposal_set_root: str
    budget: ResolutionBudget
    accepted: tuple[ProposalId, ...]
    rejected: tuple[ProposalId, ...]
    discovered_edges: tuple[tuple[ProposalId, ...], ...]
    edge_ids: tuple[str, ...]
    rejection_cost: int
    iterations: int
    resolution_root: str

    def payload(self) -> dict[str, Any]:
        edges = [
            {"edge_id": edge_id, "members": list(members)}
            for edge_id, members in zip(
                self.edge_ids, self.discovered_edges, strict=True
            )
        ]
        return {
            "schema": RESOLUTION_CERTIFICATE_SCHEMA,
            "subject": {
                **asdict(self.context),
                "proposal_set_root": self.proposal_set_root,
            },
            "budget": asdict(self.budget),
            "accepted": list(self.accepted),
            "rejected": list(self.rejected),
            "discovered_edges": edges,
            "rejection_cost": self.rejection_cost,
            "iterations": self.iterations,
            "final_batch_check": {"verdict": Verdict.SAT.value},
        }

    def record(self) -> dict[str, Any]:
        return {**self.payload(), "resolution_root": self.resolution_root}


class UnknownVerdictError(RuntimeError):
    """A required oracle query did not produce a Boolean verdict."""


class ResolutionBudgetExceeded(RuntimeError):
    """Exact bounded search exhausted its declared resource budget."""


class ConflictHypergraph:
    """A clutter whose vertices are proposals and edges are minimal conflicts."""

    def __init__(self, vertices: Iterable[ProposalId]) -> None:
        ordered = tuple(sorted(set(vertices)))
        if not ordered:
            raise ValueError("hypergraph needs at least one vertex")
        self.vertices: tuple[ProposalId, ...] = ordered
        self._vertex_set = frozenset(ordered)
        self._edges: set[ProposalSet] = set()

    @property
    def edges(self) -> tuple[ProposalSet, ...]:
        return tuple(
            sorted(self._edges, key=lambda edge: (len(edge), tuple(sorted(edge))))
        )

    def add_minimal_edge(self, edge: Iterable[ProposalId]) -> bool:
        candidate = frozenset(edge)
        if not candidate:
            raise ValueError("a conflict edge cannot be empty")
        if not candidate <= self._vertex_set:
            unknown = sorted(candidate - self._vertex_set)
            raise ValueError(f"edge contains unknown vertices: {unknown}")
        if any(existing <= candidate for existing in self._edges):
            return False
        self._edges = {
            existing for existing in self._edges if not candidate < existing
        }
        self._edges.add(candidate)
        return True

    def is_independent(self, candidate: Iterable[ProposalId]) -> bool:
        selected = frozenset(candidate)
        return not any(edge <= selected for edge in self._edges)

    def is_hitting_set(self, rejected: Iterable[ProposalId]) -> bool:
        removed = frozenset(rejected)
        return all(bool(edge & removed) for edge in self._edges)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def resolution_budget_root(budget: ResolutionBudget) -> str:
    return digest(
        {"schema": RESOURCE_BUDGET_SCHEMA, "limits": asdict(budget)}
    )


def seal_epoch(
    context: EpochContext, arrivals: Iterable[ProposalRecord]
) -> SealedEpoch:
    """Canonicalize one pending ADD set without mutating the active law.

    Re-delivery of an identical record is idempotent. Reuse of one proposal ID
    for different content or policy metadata fails closed as equivocation.
    """

    by_id: dict[ProposalId, ProposalRecord] = {}
    for record in arrivals:
        proposal_id = record.proposal.proposal_id
        existing = by_id.get(proposal_id)
        if existing is not None and existing != record:
            raise ValueError(
                f"conflicting records for proposal_id {proposal_id}"
            )
        by_id[proposal_id] = record

    records = tuple(by_id[key] for key in sorted(by_id))
    manifest = {
        "schema": PROPOSAL_MANIFEST_SCHEMA,
        "proposals": [record.manifest_entry() for record in records],
    }
    return SealedEpoch(
        context=context,
        records=records,
        proposal_set_root=digest(manifest),
    )


def conflict_edge_record(
    subject: EdgeSubject, members: Iterable[ProposalId]
) -> dict[str, Any]:
    """Create a domain-separated edge identity bound to the complete subject."""

    ordered_members = sorted(set(members))
    if not ordered_members:
        raise ValueError("a conflict edge cannot be empty")
    payload = {
        "schema": EDGE_SCHEMA,
        "subject": asdict(subject),
        "members": ordered_members,
    }
    return {**payload, "edge_id": digest(payload)}


def _require_boolean(result: OracleResult, context: str) -> Verdict:
    if result.verdict is Verdict.UNKNOWN:
        detail = f": {result.reason}" if result.reason else ""
        raise UnknownVerdictError(
            f"oracle returned UNKNOWN during {context}{detail}"
        )
    return result.verdict


def shrink_to_mus(
    oracle: ConsistencyOracle, candidate: Iterable[ProposalId]
) -> ProposalSet:
    """Deterministically shrink an UNSAT set to a subset-minimal UNSAT set."""

    current = set(candidate)
    if not current:
        raise ValueError("cannot extract a MUS from the empty set")
    initial = _require_boolean(oracle.check(frozenset(current)), "MUS precondition")
    if initial is not Verdict.UNSAT:
        raise ValueError("MUS extraction requires an UNSAT candidate")

    for proposal_id in sorted(current):
        trial = frozenset(current - {proposal_id})
        verdict = _require_boolean(
            oracle.check(trial), f"MUS deletion of {proposal_id}"
        )
        if verdict is Verdict.UNSAT:
            current.remove(proposal_id)

    mus = frozenset(current)
    if _require_boolean(oracle.check(mus), "MUS soundness audit") is not Verdict.UNSAT:
        raise RuntimeError("MUS soundness audit failed")
    for proposal_id in sorted(mus):
        verdict = _require_boolean(
            oracle.check(mus - {proposal_id}),
            f"MUS minimality audit for {proposal_id}",
        )
        if verdict is not Verdict.SAT:
            raise RuntimeError("MUS minimality audit failed")
    return mus


def enumerate_all_muses_bruteforce(
    oracle: ConsistencyOracle, vertices: Sequence[ProposalId]
) -> ConflictHypergraph:
    """Completely enumerate MUSes for small test batches only."""

    empty_verdict = _require_boolean(oracle.check(frozenset()), "base-law precondition")
    if empty_verdict is not Verdict.SAT:
        raise ValueError("the fixed base law must be satisfiable")
    graph = ConflictHypergraph(vertices)
    ordered = tuple(sorted(set(vertices)))
    for size in range(1, len(ordered) + 1):
        for combo in combinations(ordered, size):
            subset = frozenset(combo)
            if not graph.is_independent(subset):
                continue
            verdict = _require_boolean(oracle.check(subset), "complete enumeration")
            if verdict is Verdict.UNSAT:
                graph.add_minimal_edge(subset)
    return graph


def _dependencies_satisfied(
    accepted: ProposalSet,
    dependencies: Mapping[ProposalId, ProposalSet],
) -> bool:
    return all(dependencies[proposal_id] <= accepted for proposal_id in accepted)


def minimum_weight_hitting_set(
    vertices: Sequence[ProposalId],
    edges: Sequence[ProposalSet],
    costs: Mapping[ProposalId, int],
    dependencies: Mapping[ProposalId, ProposalSet],
    max_candidates: int,
) -> ProposalSet:
    """Solve the bounded exact master problem with deterministic tie-breaking."""

    ordered = tuple(sorted(set(vertices)))
    vertex_set = frozenset(ordered)
    for vertex in ordered:
        if vertex not in costs:
            raise ValueError(f"missing rejection cost for {vertex}")
        if costs[vertex] < 0:
            raise ValueError("rejection costs must be non-negative")
        if vertex not in dependencies:
            raise ValueError(f"missing dependency set for {vertex}")
        if not dependencies[vertex] <= vertex_set:
            unknown = sorted(dependencies[vertex] - vertex_set)
            raise ValueError(f"unknown dependencies for {vertex}: {unknown}")

    best: ProposalSet | None = None
    best_key: tuple[float, int, tuple[str, ...]] = (inf, 0, ())
    candidates_checked = 0

    for size in range(len(ordered) + 1):
        for combo in combinations(ordered, size):
            candidates_checked += 1
            if candidates_checked > max_candidates:
                raise ResolutionBudgetExceeded(
                    "exact hitting-set candidate budget exhausted"
                )
            rejected = frozenset(combo)
            accepted = vertex_set - rejected
            if not _dependencies_satisfied(accepted, dependencies):
                continue
            if not all(edge & rejected for edge in edges):
                continue
            key = (float(sum(costs[v] for v in rejected)), len(rejected), combo)
            if key < best_key:
                best = rejected
                best_key = key

    if best is None:
        raise RuntimeError("no dependency-closed hitting set exists")
    return best


def resolve_by_implicit_hitting_set(
    oracle: ConsistencyOracle,
    proposals: Sequence[Proposal],
    budget: ResolutionBudget | None = None,
) -> Resolution:
    """Find a minimum-cost safe, dependency-closed correction set.

    Discovered MUSes become cutting planes. The final whole-batch SAT result is
    the safety boundary. Search-budget exhaustion and UNKNOWN both fail closed.
    """

    active_budget = budget or ResolutionBudget()
    by_id = {proposal.proposal_id: proposal for proposal in proposals}
    if len(by_id) != len(proposals):
        raise ValueError("duplicate proposal_id")
    vertices = tuple(sorted(by_id))
    if not vertices:
        verdict = _require_boolean(oracle.check(frozenset()), "base-law precondition")
        if verdict is not Verdict.SAT:
            raise ValueError("the fixed base law must be satisfiable")
        return Resolution(frozenset(), frozenset(), (), 0, 0)

    vertex_set = frozenset(vertices)
    costs = {key: proposal.reject_cost for key, proposal in by_id.items()}
    dependencies = {
        key: proposal.dependencies for key, proposal in by_id.items()
    }
    for proposal_id, required in dependencies.items():
        if not required <= vertex_set:
            unknown = sorted(required - vertex_set)
            raise ValueError(f"unknown dependencies for {proposal_id}: {unknown}")

    base_verdict = _require_boolean(oracle.check(frozenset()), "base-law precondition")
    if base_verdict is not Verdict.SAT:
        raise ValueError("the fixed base law must be satisfiable")

    graph = ConflictHypergraph(vertices)
    iterations = 0

    while True:
        iterations += 1
        if iterations > active_budget.max_iterations:
            raise ResolutionBudgetExceeded("implicit resolver iteration budget exhausted")

        rejected = minimum_weight_hitting_set(
            vertices,
            graph.edges,
            costs,
            dependencies,
            active_budget.max_master_candidates_per_iteration,
        )
        accepted = vertex_set - rejected
        if not _dependencies_satisfied(accepted, dependencies):
            raise RuntimeError("master solver returned a dependency-invalid set")

        verdict = _require_boolean(
            oracle.check(accepted), "final accepted-batch check"
        )
        if verdict is Verdict.SAT:
            return Resolution(
                accepted=accepted,
                rejected=rejected,
                discovered_edges=graph.edges,
                rejection_cost=sum(costs[v] for v in rejected),
                iterations=iterations,
            )

        mus = shrink_to_mus(oracle, accepted)
        if not graph.add_minimal_edge(mus):
            raise RuntimeError("oracle/hypergraph inconsistency: repeated unhit MUS")


def certify_sealed_epoch(
    oracle: ConsistencyOracle,
    sealed_epoch: SealedEpoch,
    budget: ResolutionBudget | None = None,
) -> CertifiedResolution:
    """Resolve one sealed epoch and bind the result to its complete subject."""

    active_budget = budget or ResolutionBudget()
    if sealed_epoch.context.resolution_policy_id != SUPPORTED_RESOLUTION_POLICY:
        raise ValueError("unsupported resolution policy")
    if (
        sealed_epoch.context.resource_budget_root
        != resolution_budget_root(active_budget)
    ):
        raise ValueError("resource budget does not match the sealed epoch")

    proposals = tuple(record.proposal for record in sealed_epoch.records)
    resolution = resolve_by_implicit_hitting_set(
        oracle, proposals, active_budget
    )

    final_verdict = _require_boolean(
        oracle.check(resolution.accepted),
        "certified final accepted-batch check",
    )
    if final_verdict is not Verdict.SAT:
        raise RuntimeError("cannot certify a non-SAT accepted batch")

    edge_subject = EdgeSubject(
        domain_id=sealed_epoch.context.domain_id,
        epoch_id=sealed_epoch.context.epoch_id,
        base_law_root=sealed_epoch.context.base_law_root,
        proposal_set_root=sealed_epoch.proposal_set_root,
        oracle_semantics_id=sealed_epoch.context.oracle_semantics_id,
    )
    discovered_edges = tuple(
        tuple(sorted(edge)) for edge in resolution.discovered_edges
    )
    edge_ids = tuple(
        conflict_edge_record(edge_subject, edge)["edge_id"]
        for edge in discovered_edges
    )

    fields = {
        "context": sealed_epoch.context,
        "proposal_set_root": sealed_epoch.proposal_set_root,
        "budget": active_budget,
        "accepted": tuple(sorted(resolution.accepted)),
        "rejected": tuple(sorted(resolution.rejected)),
        "discovered_edges": discovered_edges,
        "edge_ids": edge_ids,
        "rejection_cost": resolution.rejection_cost,
        "iterations": resolution.iterations,
    }
    unsigned = CertifiedResolution(**fields, resolution_root="")
    return CertifiedResolution(
        **fields, resolution_root=digest(unsigned.payload())
    )


def verify_resolution_certificate(
    oracle: ConsistencyOracle,
    sealed_epoch: SealedEpoch,
    certificate: CertifiedResolution,
) -> bool:
    """Fail closed unless a certificate replays for the exact sealed epoch."""

    if certificate.context != sealed_epoch.context:
        raise ValueError("certificate context does not match sealed epoch")
    if certificate.proposal_set_root != sealed_epoch.proposal_set_root:
        raise ValueError("certificate proposal root does not match sealed epoch")
    if certificate.context.resolution_policy_id != SUPPORTED_RESOLUTION_POLICY:
        raise ValueError("unsupported resolution policy")
    if (
        certificate.context.resource_budget_root
        != resolution_budget_root(certificate.budget)
    ):
        raise ValueError("certificate resource budget root is invalid")
    if digest(certificate.payload()) != certificate.resolution_root:
        raise ValueError("resolution root is invalid")

    records = {
        record.proposal.proposal_id: record
        for record in sealed_epoch.records
    }
    vertices = frozenset(records)
    accepted = frozenset(certificate.accepted)
    rejected = frozenset(certificate.rejected)
    if accepted & rejected or accepted | rejected != vertices:
        raise ValueError("accepted and rejected sets do not partition the epoch")
    dependencies = {
        key: record.proposal.dependencies for key, record in records.items()
    }
    if not _dependencies_satisfied(accepted, dependencies):
        raise ValueError("accepted set is not dependency-closed")
    expected_cost = sum(
        records[key].proposal.reject_cost for key in rejected
    )
    if certificate.rejection_cost != expected_cost:
        raise ValueError("rejection cost is invalid")

    if len(certificate.discovered_edges) != len(certificate.edge_ids):
        raise ValueError("edge IDs and edge members have different lengths")
    edge_subject = EdgeSubject(
        domain_id=certificate.context.domain_id,
        epoch_id=certificate.context.epoch_id,
        base_law_root=certificate.context.base_law_root,
        proposal_set_root=certificate.proposal_set_root,
        oracle_semantics_id=certificate.context.oracle_semantics_id,
    )
    previous_key: tuple[int, tuple[str, ...]] | None = None
    for members, edge_id in zip(
        certificate.discovered_edges, certificate.edge_ids, strict=True
    ):
        edge = frozenset(members)
        key = (len(edge), tuple(members))
        if not edge or not edge <= vertices:
            raise ValueError("certificate contains an invalid conflict edge")
        if tuple(sorted(edge)) != members:
            raise ValueError("conflict edge members are not canonical")
        if previous_key is not None and key <= previous_key:
            raise ValueError("conflict edges are not in canonical order")
        previous_key = key
        if conflict_edge_record(edge_subject, edge)["edge_id"] != edge_id:
            raise ValueError("conflict edge ID is invalid")
        if _require_boolean(
            oracle.check(edge), "certificate edge soundness"
        ) is not Verdict.UNSAT:
            raise ValueError("certificate edge is not UNSAT")
        for proposal_id in sorted(edge):
            if _require_boolean(
                oracle.check(edge - {proposal_id}),
                "certificate edge minimality",
            ) is not Verdict.SAT:
                raise ValueError("certificate edge is not minimal")
        if not edge & rejected:
            raise ValueError("rejected set does not hit a disclosed edge")

    if _require_boolean(
        oracle.check(accepted), "certificate final accepted-batch check"
    ) is not Verdict.SAT:
        raise ValueError("certificate accepted batch is not SAT")

    replay = resolve_by_implicit_hitting_set(
        oracle,
        tuple(record.proposal for record in sealed_epoch.records),
        certificate.budget,
    )
    expected = (
        tuple(sorted(replay.accepted)),
        tuple(sorted(replay.rejected)),
        tuple(tuple(sorted(edge)) for edge in replay.discovered_edges),
        replay.rejection_cost,
        replay.iterations,
    )
    actual = (
        certificate.accepted,
        certificate.rejected,
        certificate.discovered_edges,
        certificate.rejection_cost,
        certificate.iterations,
    )
    if actual != expected:
        raise ValueError("certificate does not match deterministic replay")
    return True


class BruteForcePropositionalOracle:
    """Tiny deterministic oracle for finite examples and tests."""

    def __init__(
        self,
        variable_names: Sequence[str],
        predicates: Mapping[
            ProposalId, Callable[[Mapping[str, bool]], bool]
        ],
        base: Callable[[Mapping[str, bool]], bool] | None = None,
    ) -> None:
        self.variables = tuple(variable_names)
        self.predicates = dict(predicates)
        self.base = base or (lambda _assignment: True)

    def check(self, proposals: ProposalSet) -> OracleResult:
        unknown = proposals - self.predicates.keys()
        if unknown:
            return OracleResult(
                Verdict.UNKNOWN, reason=f"unknown proposals: {sorted(unknown)}"
            )

        for bits in product((False, True), repeat=len(self.variables)):
            assignment = dict(zip(self.variables, bits, strict=True))
            if self.base(assignment) and all(
                self.predicates[proposal_id](assignment)
                for proposal_id in sorted(proposals)
            ):
                return OracleResult(Verdict.SAT, witness=assignment)
        return OracleResult(Verdict.UNSAT)


def demo() -> None:
    oracle = BruteForcePropositionalOracle(
        variable_names=("a", "b"),
        predicates={
            "P": lambda model: model["a"],
            "Q": lambda model: model["b"],
            "R": lambda model: (not model["a"]) or (not model["b"]),
            "S": lambda model: not model["a"],
        },
    )

    vertices = ("P", "Q", "R", "S")
    graph = enumerate_all_muses_bruteforce(oracle, vertices)
    expected_edges = (frozenset({"P", "S"}), frozenset({"P", "Q", "R"}))
    if graph.edges != expected_edges:
        raise RuntimeError("unexpected conflict hypergraph")

    proposals = (
        Proposal("P", reject_cost=100),
        Proposal("Q", reject_cost=50),
        Proposal("R", reject_cost=1),
        Proposal("S", reject_cost=2),
    )
    resolution = resolve_by_implicit_hitting_set(oracle, proposals)
    if resolution.accepted != frozenset({"P", "Q"}):
        raise RuntimeError("unexpected accepted set")
    if resolution.rejected != frozenset({"R", "S"}):
        raise RuntimeError("unexpected rejected set")

    budget = ResolutionBudget()
    context = EpochContext(
        domain_id="tau-governance-reference",
        epoch_id="epoch-1",
        base_law_root=digest({"base": "true"}),
        oracle_semantics_id="bounded-propositional-reference-v1",
        resolution_policy_id=SUPPORTED_RESOLUTION_POLICY,
        resource_budget_root=resolution_budget_root(budget),
    )
    records = tuple(
        ProposalRecord(
            proposal,
            digest({"formula": proposal.proposal_id}),
        )
        for proposal in proposals
    )
    sealed_epoch = seal_epoch(context, reversed(records))
    certificate = certify_sealed_epoch(oracle, sealed_epoch, budget)
    if not verify_resolution_certificate(oracle, sealed_epoch, certificate):
        raise RuntimeError("resolution certificate verification failed")

    for size in range(len(vertices) + 1):
        for combo in combinations(vertices, size):
            subset = frozenset(combo)
            sat = oracle.check(subset).verdict is Verdict.SAT
            if sat != graph.is_independent(subset):
                raise RuntimeError("MUS reconstruction check failed")

    print("vertices:", list(vertices))
    print("minimal conflict hyperedges:", [sorted(edge) for edge in graph.edges])
    print("accepted:", sorted(resolution.accepted))
    print("rejected:", sorted(resolution.rejected))
    print("rejection cost:", resolution.rejection_cost)
    print(
        "MUS cuts discovered during resolution:",
        [sorted(edge) for edge in resolution.discovered_edges],
    )
    print("iterations:", resolution.iterations)
    print("proposal set root:", sealed_epoch.proposal_set_root)
    print("resolution root:", certificate.resolution_root)
    print("all reference assertions passed")


if __name__ == "__main__":
    demo()
