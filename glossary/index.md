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

## Invariant

A property intended to hold for all reachable states. When it fails, a tool can often produce a counterexample trace showing how the failure is reached.

## Counterexample

A specific witness that refutes a universal claim. In software, it is often a concrete input and an execution trace.

## Abstraction

A mapping from concrete states to a smaller representation that discards detail while preserving the distinctions that matter for a chosen property.

More terms will be added as the tutorials grow.
