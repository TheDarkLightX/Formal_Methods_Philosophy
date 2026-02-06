---
title: What makes a good software engineer, and what clean code means
layout: docs
kicker: Tutorial 7
description: In the agentic era, code provenance matters less than user outcomes, safety, maintainability, and clear design intent. This tutorial defines practical principles and checklists.
---

This tutorial argues for one practical thesis:

- Software engineering quality should be judged by outcomes and constraints, not by who wrote the code.

Code may be hand-written, generated, synthesized, or produced by an agent loop. The source can change. The standards cannot.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Mental pictures to keep</p>
  <ul>
    <li>Code provenance as a label, outcomes as the substance</li>
    <li>The user as the north star, the maintainer as a user of the codebase</li>
    <li>Golden rule as self-reference, diamond rule as preference discovery</li>
    <li>Taste as disciplined care under constraints</li>
    <li>Best practices as rails, not decoration</li>
  </ul>
</div>

## Part I: code-provenance agnosticism

Call this **engineering agnosticism**:

- Do not privilege code because a specific person wrote it.
- Do not reject code because an agent produced it.
- Evaluate code on behavior, safety, maintainability, and fit to user goals.

A concise evaluation frame:

```text
Quality = f(user outcomes, safety, maintainability, change cost)
```

Provenance still matters for audit trails and accountability, but provenance is not itself quality.

## Part II: golden rule, diamond rule, and why data matters

Two norms are often proposed:

- **Golden rule (weaker):** treat others how the engineer would want to be treated.
- **Diamond rule (recommended):** treat others how they want to be treated.

The practical difference is data.

Assumption A (explicit): for product software, the primary objective is user wellbeing through useful, safe, trustworthy outcomes.

Assumption B (explicit): user preferences are heterogeneous.

Conditional claim: if Assumptions A and B hold, the diamond rule dominates the golden rule for product decisions, because it uses observed user preferences instead of the engineer's own proxy preferences.

Stress tests:

- If there is only one user (the builder), golden and diamond collapse to the same target.
- If user preference conflicts with safety or law, safety and legal constraints remain hard gates.
- If user research is weak, both rules can fail, but the diamond workflow at least exposes the missing evidence.

Operational form of the diamond rule:

```text
1. Define target user segments and jobs-to-be-done.
2. Ship smallest viable change.
3. Measure task success, failures, support burden, and retention.
4. Keep, revise, or roll back based on evidence.
```

## Part III: software engineering as a utilitarian discipline

In this frame, software exists to solve problems in user lives, including the life of the future maintainer.

- Product code serves external users.
- Internal tooling serves internal users.
- Solo projects serve the author as user.

User-centered framing is often linked to statements by Steve Jobs (start from customer experience and work backward to technology) and Jeff Bezos (customer obsession as strategy). The common thread is that technology choices are downstream from user outcomes.

## Part IV: traditional and agentic engineering

The delivery stack is changing. Core accountability is not.

| Dimension | Traditional engineer | Agentic engineer |
|---|---|---|
| Code production | Mostly manual authoring | Human-plus-agent loop |
| Throughput | Limited by individual typing bandwidth | Amplified by automation and orchestration |
| Risk surface | Human slips and omissions | Human slips plus agent mis-specification |
| Control lever | Coding skill and review discipline | Spec quality, prompt quality, and verification rails |
| Success criterion | Reliable user outcomes | Reliable user outcomes |

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Author perspective</p>
  <p>
    I am an agentic neuro-symbolic software engineer. I have programmed for more than 20 years. Most of that time was not full-time professional software engineering. The agentic era made tools a force multiplier that changed what consistent delivery looked like.
  </p>
</div>

## Part V: what clean code means

Clean code is not primarily aesthetic. It is operational:

- easy to read correctly,
- easy to change safely,
- hard to misuse,
- explicit about intent and constraints.

A practical definition:

```text
Clean code minimizes future misunderstanding under realistic maintenance pressure.
```

This is why "code exists to produce user experience" and "clean code exists to produce maintainer experience" are compatible claims.

Taste matters in the agentic era, but taste should be interpreted as care plus evidence:

- care for user and maintainer wellbeing,
- care for edge cases and abuse cases,
- care for tradeoffs under real constraints.

## Part VI: best practices as means to the end

Best practice is not fashion. It is:

- the best currently known consensus process for a context,
- justified by evidence, incidents, or proofs,
- revised when better evidence appears.

Examples by category:

- **Correctness practices:** invariants, property testing, CEGIS loops, correct-by-construction modeling.
- **Security practices:** dependency scanning, threat modeling, known vulnerability checks, fuzzing for parser and input boundaries.
- **Design practices:** explicit interfaces, architecture decision records, documented invariants, bounded modules.
- **Operational practices:** observability, rollback paths, reproducible builds, release gates.

Assumption hygiene for best practices:

- Name the context where a practice applies.
- Name the failure mode it mitigates.
- Name the metric or test that confirms it helped.

### Technical measures for clean-code discipline

Metrics are not the goal, they are instrumentation for quality control.

```text
Engineering rule: do not optimize a metric without checking user outcomes.
```

Useful measures:

- **Cyclomatic complexity** estimates control-flow path count.

  ```text
  V(G) = E - N + 2P
  ```

  In practice, teams often use the approximation "number of branch points + 1" per function.

- **Cognitive complexity** estimates how hard code is to understand, with stronger penalties for nested control flow and flow breaks.

- **Shannon entropy** can quantify distributional complexity in tokens, identifiers, or change patterns:

  ```text
  H = -sum_i p_i * log2(p_i)
  ```

  This can flag over-compressed naming or noisy change patterns, but entropy alone does not define good design.

- **Shapley value attribution** can estimate each module's marginal contribution to a result metric (for example reliability lift, latency reduction, or defect reduction):

  ```text
  phi_i = average over subsets S of [ value(S union {i}) - value(S) ]
  ```

  This is useful for explaining contribution, but only when the value function is well-defined.

Practical interpretation:

- Cyclomatic and cognitive complexity are local maintainability signals.
- Entropy can be a structure signal.
- Shapley can be an attribution signal.
- None of these replaces user-success metrics.

### SOLID, proper abstraction, and language fit

SOLID remains useful as a design checklist:

- **S**ingle Responsibility,
- **O**pen-Closed,
- **L**iskov Substitution,
- **I**nterface Segregation,
- **D**ependency Inversion.

These are heuristics, not laws. The deeper question is abstraction fit:

- Does the abstraction match the problem constraints?
- Does it reduce accidental complexity?
- Does it make invariants easier to state and check?

Language choice is part of abstraction fit:

- Strong type systems can reduce whole classes of runtime mistakes.
- Functional style can reduce implicit state coupling in transformation-heavy logic.
- Systems languages can make resource control explicit where performance and safety are critical.

No language wins globally. The right language is the one that makes core constraints easiest to enforce and easiest to maintain.

### Uncle Bob's clean-code lens, and this tutorial's lens

Common ground with Uncle Bob's framing:

- readability is central,
- small, focused units are preferable,
- refactoring and testing are continuous obligations.

Difference in emphasis:

- Uncle Bob's lens is style-and-discipline centered.
- This tutorial adds an explicit user-outcome and evidence loop.

In this tutorial's framing, style quality without user impact measurement is incomplete, and user impact goals without maintainable style are fragile.

## Part VII: heuristics for prompt engineers in agentic workflows

Prompt quality becomes design quality when agents produce code.

Useful heuristics:

1. Start with user outcomes, not implementation preferences.
2. Specify non-negotiable constraints (safety, latency, cost, compliance).
3. Require explicit invariants and failure-mode analysis.
4. Demand tests and measurable acceptance criteria in the same request.
5. Require threat modeling for untrusted inputs.
6. Ask for rationale artifacts (tradeoffs, rejected alternatives, assumptions).
7. Enforce best-practice rails by checklist, not by hope.
8. Require deterministic reproduction steps for defects.
9. Ask for rollback strategy before rollout.
10. Treat prompt revisions as first-class engineering iterations.

### Style contract for agent-generated code

A prompt can include an explicit readability and maintainability contract:

```text
Contract:
- Keep cognitive complexity low.
- Keep cyclomatic complexity budgeted per function.
- Prefer pure functions for domain rules unless mutable state is required.
- Keep side effects at system boundaries.
- Use names that expose domain intent.
- Add tests for invariants and edge cases.
- Return a short rationale for non-obvious tradeoffs.
```

This does not force one aesthetic. It forces legibility and constraint clarity.

### Extract-and-explain test

A practical comprehension test for clean code:

1. Extract any non-trivial code block.
2. State its preconditions, postconditions, and invariants in plain language.
3. Explain the block to a second engineer or an analysis agent without opening the full project.
4. Verify that explanation predicts behavior on at least one normal case and one edge case.

If this test fails repeatedly, the code may function, but maintainability risk is high.

## Part VIII: design quality caps code quality

Code expresses the "how". Design expresses both "what" and "why".

When design quality is low, code quality is capped.

A lightweight design constitution can raise the floor:

- system purpose,
- user segments and priorities,
- hard constraints,
- safety invariants,
- tradeoff policy (what can be sacrificed, what cannot),
- evidence policy (what counts as done).

This can be a philosophy document, constitution, or core-principles file. The label matters less than the decision discipline it enforces.

## Part IX: a release checklist for clean, user-centered software

Before shipping, check:

1. Is the target user and task explicit?
2. Are safety and security gates explicit and tested?
3. Are assumptions labeled and stress-tested?
4. Are maintainers treated as users of this code?
5. Are best practices applied for this context?
6. Are acceptance metrics defined and observable?
7. Is there a rollback path?

If these checks pass, code quality is more likely to be durable across both traditional and agentic workflows.

## References

- [Tutorial 1: Approximate state tracking]({{ '/tutorials/approximate-state-tracking/' | relative_url }}), CEGIS and counterexample discipline
- [Tutorial 5: Reformulation and compression]({{ '/tutorials/reformulation-and-gates/' | relative_url }}), neuro-symbolic gates and evidence-first reasoning
- [Tutorial 6: MPRD and the algorithmic CEO]({{ '/tutorials/mprd-and-algorithmic-ceo/' | relative_url }}), policy-gated execution and invariant rails
