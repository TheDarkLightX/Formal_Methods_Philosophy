---
title: Glossary
layout: docs
kicker: Reference
description: A compact vocabulary for thinking clearly about state, invariants, abstraction, and counterexamples.
---

This glossary is intentionally small. Each definition is phrased to support a mental picture, not just a dictionary meaning.

## State

A snapshot of “everything the system would need to know” to determine what can happen next. In practice, we choose a state representation that preserves the distinctions relevant to our question.

## State machine

A model of change over time: a set of states, an initial state, and a transition relation describing how the system can evolve.

## State space

The set `S` of all states a model allows. In analysis, a crucial subset is the reachable region: the states you can actually reach from the initial state by following transitions.

## Reachable

A state is reachable if there exists an execution (a sequence of transitions) from the initial state that leads to it. Many correctness claims are quantified over reachable states, not over all imaginable states.

## Invariant

A property intended to hold for all reachable states. When it fails, a tool can often produce a counterexample trace showing how the failure is reached.

## Counterexample

A specific witness that refutes a universal claim. In software, it is often a concrete input and an execution trace.

## Assumption hygiene

The discipline of not smuggling premises in as facts. State assumptions explicitly, scope claims to those assumptions, and prefer refuters, checks, or fail-closed gates when the assumption is safety-critical.

## Abstraction

A mapping from concrete states to a smaller representation that discards detail while preserving the distinctions that matter for a chosen property.

## Compression

A change of representation that preserves meaning. For a single state, it is a lossless re-encoding. For a set of states, it can be a symbolic encoding (for example, a formula that compactly represents many states at once).

## Isomorphism

A 1-to-1, structure-preserving mapping between two structures (with the same operations/relations in view). If two structures are isomorphic, they are “the same shape” up to renaming elements.

## Equivalence relation

A relation \(\sim\) that is reflexive, symmetric, and transitive. It groups objects into equivalence classes representing “different descriptions, same meaning.”

## Hypothesis class (hypothesis space)

The set \(H\) of candidates being considered, for example a family of models, a space of invariants, or a grammar of programs. Many learning, synthesis, and debugging loops can be described as searching \(H\) while refuters eliminate candidates.

## VC dimension

A capacity measure for a binary hypothesis class \(H\). The VC dimension \(\mathrm{VC}(H)\) is the largest \(m\) such that there exists a set of \(m\) inputs that \(H\) can label in all \(2^m\) possible ways (it can “shatter” that set). Higher VC dimension typically means more data is needed to generalize.

## Shattering

A hypothesis class \(H\) shatters a finite set \(S = \{x_1,\dots,x_m\}\) if, for every assignment of labels \(y : S \to \{0,1\}\), there exists some \(h \in H\) such that \(h(x_i) = y(x_i)\) for all \(i\). Informally, \(H\) can realize every possible labeling on \(S\).

## Fat-shattering dimension

A capacity measure for real-valued hypothesis classes. Instead of requiring exact 0/1 labelings, fat-shattering asks whether the class can separate points above or below chosen thresholds with a margin \(\gamma\). It is a VC-like notion used in learning theory for regression and margin-based classification.

## Canonicalizer

A function \(\mathrm{can} : X \to X\) that picks one representative from each equivalence class under a “same meaning” relation \(\sim\). Canonicalizers are a form of symmetry breaking. They reduce redundant search by ensuring equivalent objects map to the same canonical form.

## Decomposition

A representation choice that restricts candidates to be composed from smaller parts connected by an interface. When coupling is genuinely reduced, decomposition can shrink the effective hypothesis space and turn global search into more local reasoning and propagation.

## Tactic

A reusable move that changes a representation or adds structure to make a problem easier to solve, without changing the meaning of the question being asked. Examples include rewrites, symmetry breaking, invariant strengthening, and reductions to mature solvers.

More terms will be added as the tutorials grow.
