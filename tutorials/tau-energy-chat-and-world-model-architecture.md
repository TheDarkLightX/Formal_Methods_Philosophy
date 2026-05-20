---
title: "TauEnergy Chat and World-Model Architecture"
layout: docs
kicker: Tutorial 61
description: "Learn how a Tau-facing chatbot can use an LLM for interface work, TauEnergy for advisory search ordering, TauJEPA for future-failure pressure, and Tau for verification."
---

This tutorial explains the architecture behind a Tau-facing assistant.

The core split is:

```text
LLM: talk, explain, translate
TauEnergy: rank structured candidates
TauJEPA: rank likely future failures
Tau: verify syntax and semantics
```

The assistant can be useful only if this boundary stays explicit.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Scope</p>
  <p>This is an architecture tutorial, not a deployment claim. The current workbench demonstrates advisory route ranking and replayable training reports. A production Tau assistant would need stronger grammar-drift tests, broader route-family coverage, security review, and separate governance authority.</p>
</div>

## 1. The problem

A user may ask a Tau-facing chatbot for many different things:

```text
explain this Tau formula
draft a Tau specification
find a likely optimizer route
generate witness cases
turn a Tau Net idea into an experiment proposal
repair a stale syntax example
```

An LLM can help with the language part.
It can summarize, explain, and draft.

But the LLM should not become the authority for Tau syntax, Tau semantics,
optimizer correctness, or Tau Net governance.

The architecture therefore separates interface from authority.

## 2. Four layers

### Layer 1: LLM interface

The LLM receives the human request and produces a structured packet:

```text
intent
candidate tasks
assumptions
required checks
possible repairs
```

It can also explain the output after checks finish.

The LLM is best used where language is the hard part:

- translating informal goals,
- naming assumptions,
- drafting tutorial text,
- explaining failed checks,
- proposing candidate families for later verification.

### Layer 2: TauEnergy

TauEnergy scores structured candidates.

Examples:

```text
which optimizer route should be checked first?
which witness family should be generated next?
which repair candidate is closest to checker-ready?
which training example family is missing?
```

The input is structured.
The output is a scalar score or ranking.
The authority is zero.

### Layer 3: TauJEPA

TauJEPA is a future-failure ranker.

It asks:

```text
What is likely to break if this proposal moves forward?
```

Examples of future pressures:

- syntax drift after Tau grammar changes,
- missing witness fields,
- route-family overfitting,
- broad Tau Net proposal without rollback,
- model authority overclaim,
- public tutorial claim that outruns the evidence.

TauJEPA is useful because many failures are predictable before a checker runs.
It still does not verify correctness.

### Layer 4: Tau and deterministic checks

Tau and route-specific deterministic checks decide the Tau-facing claims:

```text
does the current grammar accept this?
does the formula status match?
does the route result match Tau or a certificate?
does fallback remain available?
```

This layer is the authority layer.

## 3. The work packet

A safe chatbot response should become a work packet, not an execution command.

Example packet:

```text
intent: improve route selection for ordered-BDD-shaped formulas
proposal: add targeted measured ordered-BDD examples
assumption: current features expose enough BDD shape
TauEnergy task: rank route candidates
TauJEPA task: rank likely failure modes
Tau task: check formulas and statuses
certificate task: compare route result against Tau status
fallback: use Tau-native default route
publication rule: report metrics only
```

The packet is useful because every authority-bearing claim points to a checker.

## 4. Why this is a world model

The word "world model" can be misleading, so scope it carefully.

In this tutorial, the world is not the entire real world.
The world is a bounded Tau workbench:

```text
formula families
route candidates
semantic guards
checker outcomes
training examples
syntax versions
failure modes
fallback paths
```

TauEnergy models which route is likely to be useful.
TauJEPA models which future failure is likely to matter.
Tau checks the current formal object.

That bounded model lets the assistant discuss state space:

```text
What route families have evidence?
Which family is weakest under holdout?
Which examples should be generated next?
Which claim is safe to publish?
Which claim needs a replay gate?
```

## 5. Syntax drift

Tau syntax changes.
That is a central training problem.

A grammar-aware training row should carry:

```text
grammar snapshot
grammar hash
generated formula or command family
Tau check result
route labels
failure reason if rejected
```

When the grammar hash changes, old syntax rows become stale until regenerated
and checked again.

This is why the workbench records grammar manifests in training reports.

The safe rule is:

```text
stale grammar row -> training candidate only
current Tau accepts row -> usable checked row
```

## 6. What can be trained?

Several models can be trained, but they should have different jobs.

```text
Tau-aware LLM
```

Learns explanation style, syntax patterns, repair suggestions, and work-packet
format.

```text
TauEnergy
```

Learns route ordering, witness-family priority, repair-candidate priority, or
checker scheduling.

```text
TauJEPA
```

Learns likely future failure modes from past rejected proposals, syntax drift,
missing receipts, and weak holdout families.

The verifier boundary stays the same for all three.

## 7. Developer workflow

A Tau developer can use the architecture as a proposal loop:

```text
describe a possible optimization
-> LLM turns it into a structured route proposal
-> TauJEPA lists likely failure modes
-> TauEnergy ranks experiments to run first
-> scripts generate or load Tau examples
-> Tau checks syntax and formula status
-> deterministic route checks label examples
-> training report measures whether ordering improved
-> public snapshot publishes only safe metrics
```

The loop can produce positive evidence, negative evidence, or a new curriculum.

The ordered-BDD result is an example of the third case.
The stress report identified a weak family, then the curriculum targeted that
family.

## 8. Non-claims

This architecture does not claim:

- the chatbot can execute Tau actions,
- TauEnergy can certify optimizer correctness,
- TauJEPA can prove future safety,
- a custom LLM will remain current after Tau syntax changes,
- public metrics prove production readiness,
- Tau Net governance can be bypassed by a model score.

Those are authority overclaims.

## 9. What to remember

The useful pattern is:

```text
human intent
-> LLM work packet
-> TauEnergy ranking
-> TauJEPA failure pressure
-> Tau or certificate check
-> fallback or replayable result
```

The assistant becomes useful by making the work easier to order, explain, and
stress-test.
It becomes unsafe if the model score is treated as the decision.

Related tutorial:
[TauEnergy Workbench: Replayable Training]({{ '/tutorials/tau-energy-workbench-replayable-training/' | relative_url }}).
