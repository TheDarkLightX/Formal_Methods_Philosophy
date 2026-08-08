#!/usr/bin/env python3
from __future__ import annotations

import random
import unittest
from dataclasses import replace
from itertools import combinations, permutations, product

from semantic_conflict_hypergraph_v1 import (
    BruteForcePropositionalOracle,
    EdgeSubject,
    EpochContext,
    OracleResult,
    Proposal,
    ProposalRecord,
    ResolutionBudget,
    ResolutionBudgetExceeded,
    SUPPORTED_RESOLUTION_POLICY,
    UnknownVerdictError,
    Verdict,
    certify_sealed_epoch,
    conflict_edge_record,
    digest,
    enumerate_all_muses_bruteforce,
    resolution_budget_root,
    resolve_by_implicit_hitting_set,
    seal_epoch,
    verify_resolution_certificate,
)


class AlwaysUnknownOracle:
    def check(self, _proposals):
        return OracleResult(Verdict.UNKNOWN, reason="bounded procedure exhausted")


class SemanticConflictHypergraphTests(unittest.TestCase):
    def make_example_oracle(self) -> BruteForcePropositionalOracle:
        return BruteForcePropositionalOracle(
            ("a", "b"),
            {
                "P": lambda model: model["a"],
                "Q": lambda model: model["b"],
                "R": lambda model: (not model["a"]) or (not model["b"]),
                "S": lambda model: not model["a"],
            },
        )

    def make_example_proposals(self) -> tuple[Proposal, ...]:
        return (
            Proposal("P", 100),
            Proposal("Q", 50),
            Proposal("R", 1),
            Proposal("S", 2),
        )

    def make_example_records(self) -> tuple[ProposalRecord, ...]:
        return tuple(
            ProposalRecord(
                proposal,
                digest({"formula": proposal.proposal_id}),
            )
            for proposal in self.make_example_proposals()
        )

    def make_context(
        self, budget: ResolutionBudget | None = None
    ) -> EpochContext:
        active_budget = budget or ResolutionBudget()
        return EpochContext(
            domain_id="tau-governance-test",
            epoch_id="epoch-7",
            base_law_root=digest({"base": "true"}),
            oracle_semantics_id="tau-reference-oracle-v1",
            resolution_policy_id=SUPPORTED_RESOLUTION_POLICY,
            resource_budget_root=resolution_budget_root(active_budget),
        )

    def test_three_way_conflict_and_mixed_edges(self) -> None:
        graph = enumerate_all_muses_bruteforce(
            self.make_example_oracle(), ("P", "Q", "R", "S")
        )
        self.assertEqual(
            graph.edges,
            (frozenset({"P", "S"}), frozenset({"P", "Q", "R"})),
        )

    def test_implicit_hitting_set_finds_global_optimum(self) -> None:
        result = resolve_by_implicit_hitting_set(
            self.make_example_oracle(),
            (
                Proposal("P", 100),
                Proposal("Q", 50),
                Proposal("R", 1),
                Proposal("S", 2),
            ),
        )
        self.assertEqual(result.accepted, frozenset({"P", "Q"}))
        self.assertEqual(result.rejected, frozenset({"R", "S"}))
        self.assertEqual(result.rejection_cost, 3)

    def test_dependency_closure_is_part_of_master_problem(self) -> None:
        oracle = BruteForcePropositionalOracle(
            ("a",),
            {
                "D": lambda model: model["a"],
                "P": lambda _model: True,
                "X": lambda model: not model["a"],
            },
        )
        result = resolve_by_implicit_hitting_set(
            oracle,
            (
                Proposal("D", 1),
                Proposal("P", 1, frozenset({"D"})),
                Proposal("X", 5),
            ),
        )
        self.assertEqual(result.rejected, frozenset({"D", "P"}))
        self.assertEqual(result.accepted, frozenset({"X"}))
        self.assertEqual(result.rejection_cost, 2)

    def test_single_unsatisfiable_vertex(self) -> None:
        oracle = BruteForcePropositionalOracle(("a",), {"X": lambda _model: False})
        result = resolve_by_implicit_hitting_set(oracle, (Proposal("X", 7),))
        self.assertEqual(result.rejected, frozenset({"X"}))
        self.assertEqual(result.accepted, frozenset())

    def test_conflict_free_batch_rejects_nothing(self) -> None:
        oracle = BruteForcePropositionalOracle(
            ("a",), {"A": lambda model: model["a"], "T": lambda _model: True}
        )
        result = resolve_by_implicit_hitting_set(
            oracle, (Proposal("A", 1), Proposal("T", 1))
        )
        self.assertEqual(result.rejected, frozenset())
        self.assertEqual(result.accepted, frozenset({"A", "T"}))

    def test_unknown_fails_closed(self) -> None:
        with self.assertRaises(UnknownVerdictError):
            resolve_by_implicit_hitting_set(
                AlwaysUnknownOracle(), (Proposal("A", 1),)
            )

    def test_inconsistent_base_is_rejected(self) -> None:
        oracle = BruteForcePropositionalOracle(
            ("a",), {"A": lambda _model: True}, base=lambda _model: False
        )
        with self.assertRaisesRegex(ValueError, "base law must be satisfiable"):
            resolve_by_implicit_hitting_set(oracle, (Proposal("A", 1),))

    def test_budget_exhaustion_fails_closed(self) -> None:
        oracle = BruteForcePropositionalOracle(
            ("a",),
            {
                "A": lambda model: model["a"],
                "B": lambda model: not model["a"],
            },
        )
        with self.assertRaises(ResolutionBudgetExceeded):
            resolve_by_implicit_hitting_set(
                oracle,
                (Proposal("A", 1), Proposal("B", 1)),
                ResolutionBudget(max_iterations=4, max_master_candidates_per_iteration=1),
            )

    def test_edge_identity_binds_complete_subject(self) -> None:
        base = EdgeSubject(
            domain_id="tau-governance-test",
            epoch_id="epoch-7",
            base_law_root="a" * 64,
            proposal_set_root="b" * 64,
            oracle_semantics_id="tau-0.7.0-alpha-401d756b",
        )
        edge_id = conflict_edge_record(base, {"P", "Q", "R"})["edge_id"]
        mutations = (
            replace(base, domain_id="other-domain"),
            replace(base, epoch_id="epoch-8"),
            replace(base, base_law_root="c" * 64),
            replace(base, proposal_set_root="d" * 64),
            replace(base, oracle_semantics_id="tau-other-build"),
        )
        for changed_subject in mutations:
            with self.subTest(changed_subject=changed_subject):
                self.assertNotEqual(
                    edge_id,
                    conflict_edge_record(
                        changed_subject, {"P", "Q", "R"}
                    )["edge_id"],
                )

    def test_all_arrival_permutations_have_one_resolution_root(self) -> None:
        oracle = self.make_example_oracle()
        context = self.make_context()
        records = self.make_example_records()
        observed = set()

        for arrival_order in permutations(records):
            sealed = seal_epoch(context, arrival_order)
            certificate = certify_sealed_epoch(oracle, sealed)
            self.assertTrue(
                verify_resolution_certificate(oracle, sealed, certificate)
            )
            observed.add(
                (
                    sealed.proposal_set_root,
                    certificate.accepted,
                    certificate.rejected,
                    certificate.resolution_root,
                )
            )

        self.assertEqual(len(observed), 1)
        only = observed.pop()
        self.assertEqual(only[1], ("P", "Q"))
        self.assertEqual(only[2], ("R", "S"))

    def test_identical_redelivery_is_idempotent(self) -> None:
        context = self.make_context()
        records = self.make_example_records()
        once = seal_epoch(context, records)
        repeated = seal_epoch(context, records + (records[0], records[2]))
        self.assertEqual(once, repeated)

    def test_conflicting_duplicate_proposal_id_fails_closed(self) -> None:
        context = self.make_context()
        records = self.make_example_records()
        conflicting = ProposalRecord(
            records[0].proposal,
            digest({"formula": "different-payload"}),
        )
        with self.assertRaisesRegex(ValueError, "conflicting records"):
            seal_epoch(context, records + (conflicting,))

    def test_manifest_root_binds_payload_cost_and_dependencies(self) -> None:
        context = self.make_context()
        records = self.make_example_records()
        baseline = seal_epoch(context, records).proposal_set_root
        mutations = (
            ProposalRecord(
                records[0].proposal,
                digest({"formula": "mutated"}),
            ),
            ProposalRecord(
                replace(records[0].proposal, reject_cost=101),
                records[0].payload_hash,
            ),
            ProposalRecord(
                replace(
                    records[0].proposal,
                    dependencies=frozenset({"Q"}),
                ),
                records[0].payload_hash,
            ),
        )
        for changed in mutations:
            with self.subTest(changed=changed):
                changed_records = (changed,) + records[1:]
                self.assertNotEqual(
                    baseline,
                    seal_epoch(context, changed_records).proposal_set_root,
                )

    def test_certificate_root_binds_epoch_semantics(self) -> None:
        oracle = self.make_example_oracle()
        records = self.make_example_records()
        context = self.make_context()
        baseline = certify_sealed_epoch(
            oracle, seal_epoch(context, records)
        ).resolution_root
        mutations = (
            replace(context, domain_id="other-domain"),
            replace(context, epoch_id="epoch-8"),
            replace(context, base_law_root=digest({"base": "other"})),
            replace(context, oracle_semantics_id="other-oracle"),
        )
        for changed_context in mutations:
            with self.subTest(changed_context=changed_context):
                changed = certify_sealed_epoch(
                    oracle, seal_epoch(changed_context, records)
                )
                self.assertNotEqual(baseline, changed.resolution_root)

    def test_unsupported_policy_and_budget_mismatch_fail_closed(self) -> None:
        oracle = self.make_example_oracle()
        records = self.make_example_records()
        context = self.make_context()
        unsupported = replace(context, resolution_policy_id="unknown-policy")
        with self.assertRaisesRegex(ValueError, "unsupported resolution policy"):
            certify_sealed_epoch(oracle, seal_epoch(unsupported, records))

        other_budget = ResolutionBudget(max_iterations=64)
        with self.assertRaisesRegex(ValueError, "resource budget"):
            certify_sealed_epoch(
                oracle, seal_epoch(context, records), other_budget
            )

    def test_rehashed_semantic_certificate_mutation_is_rejected(self) -> None:
        oracle = self.make_example_oracle()
        sealed = seal_epoch(self.make_context(), self.make_example_records())
        certificate = certify_sealed_epoch(oracle, sealed)
        mutated = replace(
            certificate,
            accepted=("P", "Q", "R"),
            rejected=("S",),
            rejection_cost=2,
            resolution_root="",
        )
        mutated = replace(
            mutated, resolution_root=digest(mutated.payload())
        )
        with self.assertRaises(ValueError):
            verify_resolution_certificate(oracle, sealed, mutated)

    def test_random_small_instances_against_exhaustive_optimum(self) -> None:
        rng = random.Random(0)
        for nvars in (1, 2, 3):
            assignments = list(product((False, True), repeat=nvars))
            names = tuple(chr(ord("a") + index) for index in range(nvars))
            assignment_index = {assignment: i for i, assignment in enumerate(assignments)}

            for nprops in range(1, 6):
                for _case in range(30):
                    predicates = {}
                    for index in range(nprops):
                        table = tuple(bool(rng.getrandbits(1)) for _ in assignments)

                        def predicate(
                            model,
                            table=table,
                            names=names,
                            assignment_index=assignment_index,
                        ):
                            key = tuple(model[name] for name in names)
                            return table[assignment_index[key]]

                        predicates[f"p{index}"] = predicate

                    oracle = BruteForcePropositionalOracle(names, predicates)
                    vertices = tuple(sorted(predicates))
                    graph = enumerate_all_muses_bruteforce(oracle, vertices)

                    for size in range(nprops + 1):
                        for combo in combinations(vertices, size):
                            subset = frozenset(combo)
                            self.assertEqual(
                                oracle.check(subset).verdict is Verdict.SAT,
                                graph.is_independent(subset),
                            )

                    costs = {vertex: rng.randint(0, 9) for vertex in vertices}
                    result = resolve_by_implicit_hitting_set(
                        oracle,
                        tuple(Proposal(vertex, costs[vertex]) for vertex in vertices),
                    )

                    best = None
                    best_key = None
                    for size in range(nprops + 1):
                        for combo in combinations(vertices, size):
                            rejected = frozenset(combo)
                            accepted = frozenset(set(vertices) - set(rejected))
                            if oracle.check(accepted).verdict is not Verdict.SAT:
                                continue
                            key = (
                                sum(costs[vertex] for vertex in rejected),
                                len(rejected),
                                tuple(combo),
                            )
                            if best_key is None or key < best_key:
                                best = rejected
                                best_key = key
                    self.assertEqual(result.rejected, best)


if __name__ == "__main__":
    unittest.main(verbosity=2)
