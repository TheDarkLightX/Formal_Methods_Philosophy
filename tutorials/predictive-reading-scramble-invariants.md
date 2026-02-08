---
title: "Predictive reading: scrambled words, invariants, and proof"
layout: docs
kicker: Tutorial 8
description: An interactive word-scramble app and a scoped proof that decoding scrambled words requires contextual prediction, not letter perception alone.
---

You can raed tihs snetcene esaliy, eevn tguohh the itenranl lttrees are jmulbed.
Why does that work? And when does it *stop* working?

This tutorial builds a small interactive app and a pair of formal proofs to answer
those questions precisely:

> **Claim (scoped):** In a specific model of scrambled-word decoding, successful
> reading requires prediction from context — not just local letter perception.

The claim is deliberately narrow. It is not a full theory of human reading.
It is one sharp result about one transformation.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Assumption hygiene (scope first)</p>
  <ul>
    <li><strong>Assumption A:</strong> the scrambling transformation preserves first letter, last letter, length, and letter multiset</li>
    <li><strong>Assumption B:</strong> some distinct words share those same preserved features</li>
    <li><strong>Conditional claim:</strong> if A and B hold, then local features are insufficient for unique decoding, and context-based prediction is required</li>
  </ul>
</div>

<figure class="fp-figure" style="margin-top: var(--space-lg)">
  <p class="fp-figure-title">The scramble transformation at a glance</p>
  {% include diagrams/scramble-invariants.svg %}
  <figcaption class="fp-figure-caption">
    Blue cells are boundary anchors (first and last letter) — they never move.
    Orange cells are interior letters — they get shuffled by a random permutation.
    All three invariants (length, boundary, letter multiset) are preserved by construction.
  </figcaption>
</figure>

## Part I: what is known — and what is not

The viral "Cambridge study proves internal letters don't matter" meme overstates the evidence considerably.

- Rawlinson's 1976 thesis is often cited as early evidence for robust word recognition under internal-letter perturbation.
- Later experimental work (Rayner et al. 2006, Johnson & Eisler 2012) confirms readers *can* decode scrambled text — but with measurable cost in speed and accuracy.

The defensible takeaway is narrower than the meme suggests:

- readers tolerate certain perturbations,
- reading performance degrades (it is not free),
- context and prediction help recover meaning — this is the key lever.

## Part II: app — scramble a paragraph while preserving readability

The best way to build intuition is to try it yourself. The app below scrambles any paragraph you paste in, while keeping first and last letters fixed. Adjust the intensity slider and watch readability degrade.

<div class="fp-card" style="padding: var(--space-lg); margin-top: var(--space-md)">
  <h3 class="fp-card-title">Predictive Reading Scrambler</h3>
  <p class="fp-card-text">
    Paste text, adjust scramble intensity, and inspect invariant checks.
    The app keeps first and last letters fixed for words of length 4 or more.
  </p>

  <label for="pr-input" style="display:block; font-weight:600; margin-top:12px">Input paragraph</label>
  <textarea id="pr-input" rows="8" style="width:100%; margin-top:6px"></textarea>

  <div style="display:grid; gap:12px; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); margin-top:12px">
    <div>
      <label for="pr-intensity" style="display:block; font-weight:600">Scramble intensity</label>
      <input id="pr-intensity" type="range" min="0" max="100" step="1" value="65" style="width:100%" />
      <div class="fp-card-text"><span id="pr-intensity-value">65</span>% internal-position shuffle probability</div>
    </div>
    <div>
      <label for="pr-seed" style="display:block; font-weight:600">Seed (deterministic runs)</label>
      <input id="pr-seed" type="number" value="42" style="width:100%" />
    </div>
  </div>

  <div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:12px">
    <button id="pr-run" type="button">Scramble</button>
    <button id="pr-reset" type="button">Reset sample</button>
    <button id="pr-copy" type="button">Copy output</button>
  </div>

  <label for="pr-output" style="display:block; font-weight:600; margin-top:12px">Scrambled output</label>
  <textarea id="pr-output" rows="8" readonly style="width:100%; margin-top:6px"></textarea>

  <pre id="pr-stats" style="margin-top:12px; white-space:pre-wrap"></pre>

  <div style="overflow:auto; margin-top:10px">
    <table>
      <thead>
        <tr>
          <th>Original</th>
          <th>Scrambled</th>
          <th>Len</th>
          <th>Boundary</th>
          <th>Bag</th>
        </tr>
      </thead>
      <tbody id="pr-details"></tbody>
    </table>
  </div>
</div>

## Part III: core scrambling logic

Here is the core logic that powers the app above. It is deliberately minimal — a pure function with no side effects.

```javascript
function scrambleWord(word, intensity, rng) {
  if (word.length <= 3) return word;

  const chars = word.split("");
  const positions = [];
  for (let i = 1; i < chars.length - 1; i += 1) {
    if (rng() < intensity) positions.push(i);
  }
  if (positions.length < 2) return word;

  const pool = positions.map((i) => chars[i]);
  for (let i = pool.length - 1; i > 0; i -= 1) {
    const j = Math.floor(rng() * (i + 1));
    [pool[i], pool[j]] = [pool[j], pool[i]];
  }
  positions.forEach((pos, k) => {
    chars[pos] = pool[k];
  });
  return chars.join("");
}
```

The function preserves boundary letters by construction: the `for` loop starts at index `1` and stops before `chars.length - 1`, so indices `0` and `n-1` are never touched. The Fisher–Yates shuffle on the selected pool guarantees a uniformly random permutation — a bijection — which preserves the letter multiset.

## Part IV: invariants as logic statements

Now we can state exactly what the transformation preserves. These are not empirical observations — they follow directly from how `T` is defined.

For each word transformation `T(w) = w'`:

```text
I1 (Length):      len(w') = len(w)
I2 (Boundary):    if len(w) >= 4 then first(w') = first(w) and last(w') = last(w)
I3 (Multiset):    if len(w) >= 4 then bag(w') = bag(w)
I4 (Non-word):    punctuation/whitespace tokens are unchanged
```

The app verifies these invariants at runtime and flags any violations.

## Part V: two proof modes — formal and empirical

This chapter relies on two distinct notions of proof:

- **Formal proof:** establishes properties of the scrambling transformation itself.
- **Empirical proof-by-witness:** demonstrates that humans can read certain scrambled sentences, evidenced by observed comprehension.

The app supports both:

- invariant checks support the formal part,
- human reading outcomes support the empirical part.

### Part V.A: formal proof (scoped model)

Model definitions:

- Let `Sigma*` be strings over an alphabet.
- For word `w = c0 c1 ... c(n-1)` with `n >= 4`, choose a subset `S` of internal indices `{1..n-2}`.
- Let `pi` be a bijection on `S`.
- Transformation `T` keeps positions outside `S` fixed and permutes characters at positions in `S` according to `pi`.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Theorem 1 — invariants I1–I3 hold for all transformed words</p>
  <p><strong>Proof sketch:</strong></p>
  <ol>
    <li><code>T</code> only reassigns characters to existing positions, so length is unchanged (<strong>I1</strong>).</li>
    <li>Indices <code>0</code> and <code>n-1</code> are never in <code>S</code>, so first and last letters are unchanged (<strong>I2</strong>).</li>
    <li>A permutation is a bijection, so it preserves element counts in the permuted set. Non-permuted positions stay unchanged. Therefore the full letter multiset is preserved (<strong>I3</strong>). ∎</li>
  </ol>
</div>

### What the math means in plain language

The formal model says: pick a word, leave the first and last letters alone, and rearrange some of the middle letters. The three invariants are precise ways of saying:

1. **Length is unchanged** — no letters are added or removed, so the scrambled word has the same number of characters.
2. **Boundaries are unchanged** — the first and last letters stay put, which is why scrambled words still "look right" at a glance.
3. **Letter inventory is unchanged** — the same letters are present in the same quantities, just in different positions. Think of it like shuffling cards within a fixed frame.

The proof works because a permutation (a rearrangement) is a bijection — it moves things around without duplicating or losing any. If you shuffle five cards, you still have five cards, and each card appears exactly once.

<div class="fp-callout fp-callout-warn" style="margin-top: var(--space-lg)">
  <p class="fp-callout-title">Theorem 2 — context-free decoding is not sufficient in general</p>
  <p>Define the observation function:</p>
  <pre style="background:transparent; border:none; padding:0"><code>Obs(w) = (first(w), last(w), len(w), bag(w))</code></pre>
  <p>
    Assumption B gives at least one ambiguous pair <code>u ≠ v</code> with <code>Obs(u) = Obs(v)</code>.
    Concrete example: <strong>salt</strong> and <strong>slat</strong>.
  </p>
  <p>
    Suppose a decoder <code>D</code> uses only <code>Obs</code>.
    Because <code>Obs(u) = Obs(v)</code>, we get <code>D(Obs(u)) = D(Obs(v))</code>.
    So <code>D</code> cannot output both <code>u</code> and <code>v</code> correctly in their respective contexts.
  </p>
  <p>
    Therefore, a successful decoder in ambiguous cases must use extra information
    beyond <code>Obs</code> — such as sentence context or prior probability.
    <strong>This is the predictive component.</strong> ∎
  </p>
</div>

### What Theorem 2 means in plain language

Consider the words **salt** and **slat**. Both start with `s`, end with `t`, have 4 letters, and contain exactly `{a, l, s, t}`. If you scrambled either word, the result could look like `slat` or `salt` — and there is no way to tell which original was intended by looking at the scrambled letters alone.

A reader (human or machine) that sees `slat` in isolation cannot know whether the writer meant "salt" or "slat." The only way to resolve the ambiguity is to use surrounding context: *"pass the slat"* almost certainly means *salt*, while *"a slat in the fence"* means *slat*.

This is not a contrived edge case. English has many such collisions: **calm** and **clam** (`c...m`, 4 letters, `{a, c, l, m}`), **trail** and **trial** (`t...l`, 5 letters, `{a, i, l, r, t}`), **united** and **untied** (`u...d`, 6 letters, `{d, e, i, n, t, u}`). The longer the dictionary, the more collisions appear.

This is the core insight: **local letter features are not enough; prediction from context is required.**

<figure class="fp-figure" style="margin-top: var(--space-lg)">
  <p class="fp-figure-title">Why context-free decoding fails</p>
  {% include diagrams/obs-ambiguity.svg %}
  <figcaption class="fp-figure-caption">
    Two distinct words ("salt" and "slat") produce identical observations under Obs().
    A context-free decoder D cannot distinguish them — sentence context is required
    to resolve the ambiguity. This is the formal core of Theorem 2.
  </figcaption>
</figure>

### Part V.B: empirical proof-by-witness (human readability)

Theorem 2 shows context is *logically necessary* in ambiguous cases. But can humans actually *use* that context in practice? This is an empirical question, and it requires a different kind of evidence.

Statement under test:

```text
S(alpha, corpus, population):
Humans in this population can read text transformed by T_alpha on this corpus
with non-trivial success.
```

Operational evidence protocol:

```text
1. Choose a corpus and scramble level alpha.
2. Present the transformed text to readers.
3. Measure at least one success metric:
   - comprehension questions,
   - word recovery accuracy,
   - reading time vs. baseline.
4. If success consistently exceeds a pre-registered threshold, accept S for that scope.
```

In this empirical sense, a human successfully reading scrambled sentences serves as the witness — that successful reading constitutes the proof event for the scoped claim.

## Part VI: stress tests and edge cases

The scramble-and-read pipeline is not universally robust. Three failure modes are worth testing:

- **Intensity too high:** at extreme scramble levels, even strong context cannot rescue reading — the signal-to-noise ratio collapses.
- **Rare vocabulary:** domain jargon and uncommon words increase ambiguity because the reader's prior is weaker.
- **Weak context:** short isolated tokens (labels, single-word captions) give the predictive system little to work with.

App gate:

```text
If invariant checks fail, the transformation implementation is wrong.
If invariants pass but readability is poor, adjust intensity or text domain.
```

## Part VII: relation to Godel-style results

This result is not a Godel-style incompleteness theorem — but there is a family resemblance worth noting.

- Godel incompleteness concerns the limits of formal axiomatic systems: there exist true statements that no finite proof within the system can derive.
- This chapter makes a narrower but structurally similar move: the formal model (Obs) provably cannot distinguish certain word pairs, so meaning recovery must come from outside the model — from context.

The analogy is limited. Godel operates over arithmetic and self-reference; Theorem 2 operates over a specific observation function. But the shared shape is:

- a formal system with definite boundaries,
- a demonstration that some truths lie beyond those boundaries,
- a pointer to where the extra information must come from.

## Part VIII: deeper insight as author hypothesis

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Author hypothesis (not a theorem)</p>
  <p>
    <strong>(H1)</strong> Humans and machines both read through prediction under uncertainty.<br/>
    <strong>(H2)</strong> Humans add a symbolic world-model layer that supports logic, abstraction,
    and compositional reasoning beyond local text decoding.
  </p>
  <p style="margin-top:8px; font-size:0.92em">
    <strong>Scope:</strong> structural similarity at the inference-pattern level, not identity of mechanisms.
    Assumption C (population-level): most humans can perform some cue-triggered autobiographical-symbolic recall
    for culturally familiar symbols, though intensity varies across individuals.
  </p>
</div>

At the core, both systems face the same decoding problem:

```text
Human reading: infer the intended word from letters + sentence context + world priors.
LLM decoding:  predict the next token from token context + learned distributional priors.
```

Shared pattern: uncertainty in local signal → contextual prior resolves ambiguity → prediction drives decoding.

### What LLMs can — and cannot — do here

An LLM reading scrambled text faces the same ambiguity problem as a human reader, but resolves it differently.

**What LLMs can do well:**

- **Contextual prediction.** LLMs excel at using surrounding tokens to predict the most likely intended word. Given "pass the slat," an LLM's learned distribution strongly favors "salt" — the same disambiguation a human performs.
- **Pattern completion at scale.** Because LLMs have been trained on vast corpora, they carry implicit frequency priors. Common words and phrases are recovered more reliably than rare ones, mirroring human behavior.
- **Robustness to mild scrambling.** Tokenizers may split scrambled words into subword pieces, but the attention mechanism can still recover meaning from context when scrambling is moderate.

**Where LLMs fall short:**

- **No grounded world model.** A human reading "pass the salt" can draw on embodied experience — the weight of a salt shaker, the taste of salt, a dinner scene. An LLM resolves the ambiguity statistically, without sensory grounding.
- **Brittle under heavy scrambling.** As scramble intensity rises, tokenization breaks down. A heavily scrambled word may become out-of-vocabulary tokens that the model cannot recover, even with strong context.
- **No stable symbolic compression.** Humans compress entire narratives into reusable symbols (as described in H2). LLMs do not maintain persistent symbolic representations across conversations — each context window is a fresh start unless external memory is attached.
- **Context window boundary.** Human predictive reading draws on a lifetime of priors. LLM prediction is bounded by the context window and the statistical patterns frozen at training time.

### Where humans go further (H2)

The hypothesis claims humans add a symbolic layer on top of prediction:

- stories compress into symbols or concepts,
- symbols link into a structured concept graph (an internal worldview),
- operations run over symbols (if-then rules, branching, iteration, composition),
- symbols bind to autobiographical memory, affect, and multisensory traces (all five senses, emotional state, social context).

Concrete cultural-symbol example:

- Source story: *A Nightmare on Elm Street*.
- Compressed symbol: `FREDDY_GLOVE`.
- The symbol carries genre priors (horror), character identity, scenes, mood, and narrative constraints — not just the token itself.

```text
if symbol == FREDDY_GLOVE then tone := HORROR
if audience_age < threshold then reduce_intensity()
for motif in franchise_motifs: blend(motif, current_plot)
```

The hypothesis is that humans routinely perform an internal version of this compress-and-manipulate pipeline — sometimes as rapid scene-level recall, sometimes as higher-level abstract reasoning. In this framing, reading goes beyond text decoding: it integrates decoded meaning into a symbolic model that can be inspected and manipulated.

### Human cognition vs. LLM inference

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Scoping assumptions</p>
  <ul>
    <li><strong>A3 (memory selection):</strong> human memory is selective and compression-oriented, prioritizing salient episodes over exhaustive recording. Vivid recall for highlights coexists with sparse encoding of routine intervals.</li>
    <li><strong>A4 (LLM scope):</strong> the comparison target is a text-first autoregressive transformer at inference time, without direct sensorimotor embodiment.</li>
    <li><strong>A5 (terminology):</strong> "thinking" = control loop over world-model state, goals, and actions; "LLM inference" = conditional token prediction over a context window.</li>
  </ul>
</div>

LLM inference in brief: input text → tokens → vectors → layered attention + MLP → probability distribution `P(t_n | t_1..t_{n-1})` → decoding rule selects next token → repeat.

| Dimension | Human cognition | LLM inference |
|-----------|----------------|---------------|
| **Input** | Continuous multimodal stream (vision, hearing, touch, smell, taste) | Discrete token sequences |
| **Memory** | Autobiographical, affective, embodied, persistent | Context-window bounded (unless external memory attached) |
| **Symbol grounding** | Lived events, social stakes, multisensory traces | Statistical co-occurrence (unless tool feedback loops provided) |
| **Perspective** | Multiple socially situated viewpoints (empathy-linked) | Generated from learned textual patterns |
| **Control loop** | Observation → world-model state update → goal evaluation → counterfactual simulation → action | Context → next-token distribution → decode → append → repeat |
| **Intermediate steps** | Reasoning can proceed without producing words | Behavior exposed as generated tokens |

Compact formal sketches:

```text
Human-style:  wm_state_next = Update(wm_state, observation)
              action = argmax_a ExpectedUtility(a | wm_state, goals, constraints)

LLM-style:    token_n ~ Decode(P_theta(token_n | token_1..token_(n-1), prompt))
```

Terminology note:

- many formal references use the word "belief" for uncertain world-model state, but this tutorial uses "world-model state" for readability.

### Model-level vs system-level distinction

To keep terms precise:

- model-level LLM behavior is next-token inference,
- system-level behavior can include planning, memory, tools, and policy constraints around the model.

Assumption A6 (intervention criterion):

- a process is counted as task-level thinking only if controlled changes in goals, constraints, or world-model assumptions produce systematic policy changes, not only stylistic text changes.

Minimal intervention checks:

1. Goal-flip check: keep observations fixed, change only the goal, verify action policy changes in the expected direction.
2. Constraint-tightening check: keep goals fixed, tighten safety constraints, verify previously allowed actions are blocked.
3. Counterfactual check: modify one causal assumption in the world model, verify downstream plan revisions are coherent.

Compact objective contrast:

```text
Human-style control objective (abstract):
choose policy pi to maximize expected long-horizon utility under goals and constraints.

Model-level LLM objective at inference:
choose next token with high conditional probability under P_theta(. | context).
```

Practical reading of the distinction:

- an LLM can produce text that describes a plan,
- an agentic stack can execute a plan with tools and memory,
- human cognition integrates planning with embodied perception and lived value structure.

### Stress-test notes

- Agentic stacks with planners, tools, and memory can approximate parts of a human-like control loop.
- Multimodal training and tool use can reduce some embodiment gaps.
- Humans also rely on fast heuristics and often skip full deliberation.
- Even with retrieval tools and memory layers, parity with human autobiographical grounding remains an open empirical question.
- The boundary is architectural and degree-based, not a claim that one side always outperforms on every task.
- Whether current LLMs build and manipulate cultural symbols with the same depth and stability as human world-model symbols remains unresolved.

### Falsifiable predictions

1. As scramble intensity rises, both humans and LLMs should rely more on context than local letter order.
2. With weak context, both should exhibit higher ambiguity and error rates on anagram-like collisions.
3. Strengthening context should recover performance more than strengthening isolated token visibility.
4. Tasks requiring narrative-to-symbol compression should favor systems with explicit world-model scaffolds.
5. Multi-step symbolic operations (rule chaining, branching, iterative refinement) should reveal a gap between pure next-token prediction and structured reasoning.
6. Cue-triggered retrieval with autobiographical and affective binding should show stronger human recall than text-only model recall.

## Part IX: what this proves — and what it does not

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Summary</p>
  <p><strong>Proved in this tutorial:</strong></p>
  <ul>
    <li>the scrambling transformation preserves formal invariants (Theorem 1),</li>
    <li>the observation map is non-injective in realistic cases — multiple words can look identical after scrambling,</li>
    <li>disambiguation therefore requires contextual prediction (Theorem 2).</li>
  </ul>
  <p style="margin-top:8px"><strong>Not proved here:</strong></p>
  <ul>
    <li>a full cognitive or neural theory of reading,</li>
    <li>exact predictive mechanisms in the brain,</li>
    <li>universal readability guarantees for all languages or scripts.</li>
  </ul>
</div>

The gap between "proved" and "not proved" is the honest boundary of this tutorial. The formal results are tight. Everything beyond them — including the author hypothesis in Part VIII — is clearly labeled as conjecture.

## References

- Matt Davis, "The Cambridge email hoax", MRC CBU (historical/context note):
  <https://www.mrc-cbu.cam.ac.uk/personal/matt.davis/cmabridge/>
- Matt Davis, note on Rawlinson thesis:
  <https://www.mrc-cbu.cam.ac.uk/personal/matt.davis/Cmabrigde/rawlinson.html>
- Rayner, White, Johnson, Liversedge (2006), "Raeding wrods with jubmled lettres":
  <https://pubmed.ncbi.nlm.nih.gov/16507057/>
- Johnson and Eisler (2012), evidence on transposed-letter effects:
  <https://pubmed.ncbi.nlm.nih.gov/23089042/>

<script src="{{ '/assets/js/predictive-reading.js' | relative_url }}"></script>
