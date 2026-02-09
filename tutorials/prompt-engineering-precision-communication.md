---
title: Prompt engineering and precision communication
layout: docs
kicker: Tutorial 9
description: How to reduce ambiguity, specify constraints, and turn natural language intent into checkable structure, with a controlled-Lojban transpiler demo.
---

In this tutorial, prompt engineering is treated as precision communication under uncertainty.
The goal is not clever wording. The goal is behavior that is stable enough to evaluate for a stated scope.

This tutorial builds a small controlled-language transpiler (in the browser) and uses it to make one practical claim:

- prompts become more reliable when goals, constraints, and checks are explicit, and when a representation change is stated as an obligation rather than as a suggestion.

This is not a guarantee of correctness. The point is to reduce ambiguity and to make evaluation possible.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Assumption hygiene (scope first)</p>
  <ul>
    <li><strong>Assumption A:</strong> the task can be specified as structured fields (goal, constraints, checks, output format).</li>
    <li><strong>Assumption B:</strong> the recipient (human or model) follows those fields as constraints rather than as suggestions.</li>
    <li><strong>Conditional claim:</strong> if A and B hold, then ambiguity reduces and evaluation becomes easier.</li>
  </ul>
</div>

## Part I: what "prompt engineering" is

In this series, a "prompt" is a specification boundary.
It can be small (one sentence) or large (a structured contract), but it always plays the same role:

- declare intent,
- constrain the allowed solution space,
- make success and failure testable.

Prompt optimization is the practice of iterating this boundary until results are stable enough to trust for the intended scope.

## Part II: precision communication beats cleverness

One common way to improve reliability is to remove hidden defaults.

Bad prompt example:

```text
Build a Lojban transpiler that turns Lojban into a formal spec or code.
```

Why it fails:

- "transpiler" is underspecified (what subset, what grammar, what output),
- "formal spec" is underspecified (JSON, TLA+, Lean, Tau, plain Markdown),
- constraints are missing (dependencies, performance, error handling),
- evaluation is missing (tests, examples, acceptance criteria).

Better prompt example (still plain English):

```text
Goal: implement a browser-only demo transpiler for a controlled subset of Lojban.

Scope:
- Input uses real Lojban markers:
  - optional sentence prefix ".i"
  - key-value statements using "zoi ... du zoi ..."
- Supported keys: goal, problem, domain_a, why_intractable, target_domain_b, mapping_f, preserve, solve_in_b, inverse_mapping, validation.
- Unknown keys must produce warnings (or errors in strict mode), never crashes.

Outputs:
- JSON spec (pretty-printed).
- Markdown spec skeleton.
- TypeScript interface + stub function.

Constraints:
- No external libraries.
- Deterministic behavior given the same input text.

Evaluation:
- Include a sample input that exercises all keys.
- Show parse errors and warnings.
```

This prompt is "better" because it can be checked. It turns taste questions into explicit constraints.

## Part III: Lojban (what it is, and what it is not)

Lojban is a constructed language designed to reduce certain forms of ambiguity in syntax and parsing.
It does not eliminate all ambiguity:

- meaning still depends on definitions and shared context,
- real-world referents still require grounding (what the words point to),
- users can still underspecify a request.

The relevance to prompts is not that Lojban is a magic solution.
The relevance is the design principle: make structure explicit so interpretation has fewer degrees of freedom.

This tutorial uses a controlled subset of Lojban for the demo. It relies on a few real Lojban mechanisms:

- `.i` as a visible sentence boundary,
- `du` for explicit key equals value statements,
- `zoi ...` for quoting free text.

It is not a general Lojban parser. It is a small, intentionally constrained format designed to be easy to transpile into structured specs.

## Part IV: a high precision prompt template

The following prompt expresses the "change of representation" move without math symbols.
It is meant to be typed and read aloud.

```text
Goal:
- Solve a problem in Domain A.

Problem statement:
- Describe the problem in one paragraph.

Why the direct approach is hard:
- State why a direct solution is intractable (time, state explosion, complexity class, missing observability).

Representation change:
- Choose an easier Domain B.
- Describe a mapping f from A to B.
- List the structure that must be preserved (examples: distances, ordering, safety invariants, interface behavior).

Solve in Domain B:
- Describe a method in B and what artifact it produces (equations, solution object, proof, code).

Translate back:
- Describe how to map the solution artifact back into A (an inverse map, or a reconstruction procedure).

Validation and stress tests:
- List checks that must pass after translating back.
- List failure modes and how to detect them.

Output format:
- Specify exactly what to output (JSON, code files, proof outline, test cases).
```

This template is a prompt, and it is also a general engineering move.
When the direct route explodes, change the representation, then enforce obligations that make the change safe.

Terminology note:

- if the mapping is intended to be lossless and reversible, it is closer to an isomorphism,
- if the mapping is intentionally lossy (abstraction, quotienting), it is closer to a homomorphism or a reduction,
- in the lossy case, the prompt must specify what information is allowed to be discarded and how correctness is checked after translating back.

## Part V: change of representation and state explosion rhyme

Two common intractability patterns:

- **representation intractability:** the model is right, but the representation makes solving hard,
- **state explosion:** the representation is operationally correct, but the state space is too large to explore directly.

In both cases, leverage comes from a structured move:

- map to something smaller or easier,
- solve there,
- map back,
- prove or test that the mapping preserved what matters.

This is the same shape as decomposition:

```text
If global verification is intractable, decompose the system into modules,
then verify local obligations and a composition rule.
```

The core discipline is the same as in isomorphism and abstraction:

- treat a mapping as a claim until obligations are checked,
- write down what must be preserved,
- add an explicit gate or check.

## Part VI: reformulation tactics as prompt recipes

This section upgrades four common "breakthrough" moves into precise prompt templates.
Each tactic is useful when the direct route is intractable, but each one has a failure mode, so each one includes stress tests.

### 1. Constraint relaxation (temporary constraint dropping)

Concept:

- many hard problems are hard because the constraints fight each other,
- temporarily drop the hardest constraint, solve the relaxed problem, then repair.

Example (scope note):

- for a routing problem, a relaxation can produce a lower bound or a scaffold (for example, a spanning structure),
- the relaxed solution is not guaranteed to be repairable into an optimal constrained solution, but it often provides leverage.

Precision prompt template (plain English):

```text
Mode: Constraint relaxation

1. List constraints: C1, C2, ...
2. Choose the hardest constraint: Chard.
3. Define relaxed problem P' = P without Chard.
4. Solve P' to get S_relaxed.
5. Measure violation of Chard by S_relaxed (a cost or a witness).
6. Repair: propose a concrete modification that reduces violation while keeping other constraints satisfied.
7. Iterate until violation is acceptable or no progress is possible.

Output:
- The relaxed solution, the repair steps, and the final constrained solution.

Checks:
- A clear "pass/fail" check for every constraint.
```

Controlled Lojban encoding (for the demo transpiler):

```text
.i zoi gy mode gy du zoi gy constraint_relaxation gy
.i zoi gy constraints gy du zoi gy C1: ...; C2: ...; C3: ... gy
.i zoi gy chard gy du zoi gy ... gy
.i zoi gy relaxed_problem gy du zoi gy ... gy
.i zoi gy s_relaxed gy du zoi gy ... gy
.i zoi gy violation_measure gy du zoi gy ... gy
.i zoi gy repair_plan gy du zoi gy ... gy
.i zoi gy checks gy du zoi gy ... gy
```

### 2. Inversion (reverse-engineering the conditions)

Concept:

- instead of building the solution forward, assume a target state is already true,
- solve for the conditions that must have made it true, or for the easiest way it fails.

Slogan (attribution note):

- this move is sometimes summarized by "always invert", a phrase often attributed to Carl Gustav Jacobi.

Example:

- for "never crash", start from a specific crash story, then work backward into the smallest set of enabling conditions,
- convert those conditions into gates, tests, and hardening work.

Precision prompt template (plain English):

```text
Mode: Inversion

1. Pick end state: either the goal G, or a failure F.
2. List necessary precursors that must be true immediately before the end state.
3. Chain backward: repeatedly ask "what had to be true right before that?"
4. Stop when the chain hits present-day controllables (design choices, inputs, gates).
5. If chaining from failure F, negate each link into a safety requirement.

Output:
- A backward chain (G or F -> ... -> controllables),
- A set of gates and checks that block the failure chain or enable the goal chain.
```

Controlled Lojban encoding:

```text
.i zoi gy mode gy du zoi gy inversion gy
.i zoi gy end_state gy du zoi gy G or F gy
.i zoi gy precursors gy du zoi gy ... gy
.i zoi gy backward_chain gy du zoi gy ... gy
.i zoi gy gates gy du zoi gy ... gy
.i zoi gy checks gy du zoi gy ... gy
```

Note:

- "How would I break it?" is an inversion move. It is powerful when paired with a concrete refuter mechanism (fuzzing, adversarial tests, chaos engineering).

### 3. Dual problem (swap objectives or viewpoints)

Concept:

- many optimization and feasibility problems have a dual form,
- the dual is sometimes easier to solve or easier to bound, and the bound is still valuable.

Example:

- max flow has a min cut dual,
- a dual solution can certify a bound even when the primal solution is hard to construct.

Precision prompt template (plain English):

```text
Mode: Duality

1. State the primal problem as an explicit objective + constraints.
2. Construct a dual problem that produces:
   - either an equivalent optimum (when strong duality holds),
   - or a certified bound (when only weak duality holds).
3. Solve the dual (or compute the best bound available).
4. Map back: explain what the dual solution implies about the primal.
5. Stress-test the duality assumptions (convexity, constraint qualification, integrality gaps).

Output:
- Primal statement, dual statement, solution or bound, mapping explanation.
```

Controlled Lojban encoding:

```text
.i zoi gy mode gy du zoi gy duality gy
.i zoi gy primal gy du zoi gy ... gy
.i zoi gy dual gy du zoi gy ... gy
.i zoi gy assumptions gy du zoi gy ... gy
.i zoi gy map_back gy du zoi gy ... gy
```

### 4. Dimensionality reduction via invariants and symmetry

Concept:

- find what does not change (invariants),
- factor out symmetries (quotient), solve in the reduced space, then lift back.

Example:

- for many-body motion, conserved quantities and aggregate invariants (such as center of mass) can reduce complexity.

Precision prompt template (plain English):

```text
Mode: Invariants and symmetry

1. List candidate invariants (quantities that remain constant or monotone).
2. List symmetries (transformations that preserve behavior).
3. Define the reduced representation (quotient or projection).
4. Solve the reduced problem.
5. Lift the reduced solution back to the original domain.
6. Check that invariants and symmetry assumptions really hold.

Output:
- Invariants, symmetries, reduced model, lifted solution, and checks.
```

Controlled Lojban encoding:

```text
.i zoi gy mode gy du zoi gy invariants_symmetry gy
.i zoi gy invariants gy du zoi gy ... gy
.i zoi gy symmetries gy du zoi gy ... gy
.i zoi gy reduced_model gy du zoi gy ... gy
.i zoi gy lift_back gy du zoi gy ... gy
.i zoi gy checks gy du zoi gy ... gy
```

### Choosing a tactic (a quick decision guide)

- use constraint relaxation when the constraints conflict and a partial solution is easy to obtain,
- use inversion when starting forward feels blocked or when safety is the main goal,
- use duality when an optimization view is natural and assumptions can be made explicit,
- use invariants and symmetry when the system is large but has conserved quantities or repeating structure.

## Part VII: demo, a controlled-Lojban transpiler to structured specs

<div class="fp-card" style="padding: var(--space-lg); margin-top: var(--space-md)">
  <h3 class="fp-card-title">Precision Prompt Transpiler (demo)</h3>
  <p class="fp-card-text">
    A controlled subset of Lojban for extracting key-value intent into a structured spec.
    It relies on a real Lojban key equals value pattern, but it is not a full Lojban parser.
  </p>

  <label for="pp-input" style="display:block; font-weight:600; margin-top:12px">Input</label>
  <textarea id="pp-input" rows="10" style="width:100%; margin-top:6px"></textarea>

  <div style="display:grid; gap:12px; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); margin-top:12px">
    <div>
      <label for="pp-format" style="display:block; font-weight:600">Output format</label>
      <select id="pp-format" style="width:100%">
        <option value="json">JSON spec</option>
        <option value="md">Markdown spec</option>
        <option value="ts">TypeScript stub</option>
      </select>
    </div>
    <div>
      <label for="pp-mode" style="display:block; font-weight:600">Parsing mode</label>
      <select id="pp-mode" style="width:100%">
        <option value="strict">Strict (unknown keys are errors)</option>
        <option value="warn">Warn (unknown keys preserved in extras)</option>
      </select>
    </div>
  </div>

  <div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:12px">
    <button id="pp-run" type="button">Transpile</button>
    <button id="pp-reset" type="button">Reset sample</button>
    <button id="pp-copy" type="button">Copy output</button>
  </div>

  <label for="pp-output" style="display:block; font-weight:600; margin-top:12px">Output</label>
  <textarea id="pp-output" rows="12" readonly style="width:100%; margin-top:6px"></textarea>

  <pre id="pp-notes" style="margin-top:12px; white-space:pre-wrap"></pre>
</div>

### Controlled input format (the "language")

The demo accepts three line formats:

1. Preferred: controlled-Lojban key equals value statements (`zoi ... du zoi ...`).
2. Also supported: controlled-Lojban tags (`fi'o me zoi ... zoi ...`).
3. Also supported: plain `key: value` lines.

The preferred controlled-Lojban pattern is:

```text
(.i)? zoi <kdelim> <key> <kdelim> du zoi <vdelim> <value> <vdelim>
```

Rules:

- `.i` is optional and is treated as a visible delimiter,
- each `zoi <delim> ... <delim>` uses a delimiter token such as `gy` or `by`,
- keys are case-insensitive and normalized (spaces become underscores),
- values are free text (they can be English, Lojban, or mixed),
- blank lines and `# comments` are ignored.

Parsing mode:

- Strict mode treats unknown keys and unrecognized lines as errors.
- Warn mode preserves unknown keys under `extras` and reports unrecognized lines as warnings.

Recognized keys (canonical fields):

- `goal`, `problem`, `domain_a`, `why_intractable`,
- `target_domain_b`, `mapping_f`, `preserve`,
- `solve_in_b`, `inverse_mapping`, `validation`.

Interpretation notes:

- `du` reads as "is identical to", and it is used here as "key equals value",
- the transpiler does not parse full Lojban grammar, it only extracts these key-value statements.

This is intentionally small. The point is not linguistic completeness, it is structural precision.

## Part VIII: prompt optimization as an engineering loop

Prompt optimization can be treated as a loop:

1. write a first prompt,
2. run it on a small suite of representative cases,
3. add constraints where outputs drift,
4. add checks where the cost of being wrong is high,
5. stop when behavior is stable enough for the scope.

In formal methods language, this is a refinement loop:

- add assumptions, constraints, and invariants to shrink the allowed behaviors,
- use counterexamples (bad outputs) as refuters that force the next refinement.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Science as selection (author quote)</p>
  <p>
    "Survival of the fittest hypothesis is the rule of science."
  </p>
  <p style="margin-top:8px; font-size:0.92em">
    <strong>Clarification:</strong> one more precise formulation is that hypotheses compete by making predictions and
    surviving strong attempts at refutation. Survivors are kept provisionally, within the scope of the tests run so far.
  </p>
  <p style="margin-top:8px; font-size:0.92em">
    <strong>Connection:</strong> this framing matches Karl Popper's emphasis on falsifiability and on progress by
    conjectures that face attempted refutations. Survival is provisional, and the point of tests is to try to break
    the hypothesis.
  </p>
</div>

## Part IX: build a prompt optimizer (app)

A prompt optimizer is not a magic phrase generator. It is a small engineering loop:

1. represent the prompt as structured fields,
2. emit a canonical prompt from those fields,
3. evaluate on a small suite of cases,
4. refine constraints and checks until behavior is stable enough for the scope.

This page includes a small browser demo that does the first two steps deterministically. It lints an input prompt for missing structure, then rewrites it into a standard template.

Limits:

- the demo cannot infer missing requirements,
- the rewrite improves clarity, but it does not certify correctness,
- the only reliable notion of "better" comes from explicit checks.

### Demo: Prompt Optimizer (template and lint)

<div class="fp-card" style="padding: var(--space-lg); margin-top: var(--space-md)">
  <h3 class="fp-card-title">Prompt Optimizer (demo)</h3>
  <p class="fp-card-text">
    A deterministic prompt linter and template rewrite.
    It does not call a language model. It only surfaces missing structure and emits a canonical template.
  </p>

  <label for="po-input" style="display:block; font-weight:600; margin-top:12px">Input prompt</label>
  <textarea id="po-input" rows="10" style="width:100%; margin-top:6px"></textarea>

  <div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:12px">
    <button id="po-run" type="button">Optimize</button>
    <button id="po-reset" type="button">Reset sample</button>
    <button id="po-copy" type="button">Copy output</button>
  </div>

  <label for="po-output" style="display:block; font-weight:600; margin-top:12px">Optimized prompt</label>
  <textarea id="po-output" rows="14" readonly style="width:100%; margin-top:6px"></textarea>

  <pre id="po-notes" style="margin-top:12px; white-space:pre-wrap"></pre>
</div>

### How the optimizer works (implementation sketch)

The demo implements two passes:

- a **lint** pass that checks for missing elements (constraints, checks, output format),
- a **rewrite** pass that emits a prompt with standard sections and explicit placeholders.

In pseudocode:

```text
input_prompt -> lint -> warnings
input_prompt -> rewrite -> optimized_prompt_template
```

Minimal implementation steps:

1. Add UI elements with stable IDs (`po-input`, `po-output`, `po-run`, `po-notes`).
2. Implement two pure functions, `lint(prompt)` and `rewrite(prompt)`.
3. Wire a button click to run lint plus rewrite and render the output.
4. Include the script with a deferred tag at the bottom of the page.

Core loop (simplified):

```javascript
const run = () => {
  const prompt = input.value || "";
  const { warnings } = lint(prompt);
  output.value = rewrite(prompt);
  notes.textContent = warnings.map((w) => `- ${w}`).join("\n");
};
```

### Extending to automatic optimization with a model (optional)

Fully automatic optimization can wrap the same idea around a model that proposes rewrites:

1. generate N candidate prompt rewrites,
2. run each candidate on the same test cases,
3. score outputs with a rubric,
4. keep the best prompt, repeat for K rounds.

This is an engineering loop. It is only as reliable as the evaluation suite and the rubric.
For safety, keep API keys out of client-side code and call the model through a small server-side proxy, or run locally.

## References (optional starting points)

- Lojban overview: <https://lojban.org/>
- Karl Popper, *The Logic of Scientific Discovery* (falsifiability and demarcation).
- Karl Popper, *Conjectures and Refutations* (science as conjecture plus attempted refutation).

<script src="{{ '/assets/js/prompt-precision.js' | relative_url }}" defer></script>
<script src="{{ '/assets/js/prompt-optimizer.js' | relative_url }}" defer></script>
