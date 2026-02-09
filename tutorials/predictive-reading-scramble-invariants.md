---
title: "Predictive reading: scrambled words, invariants, and proof"
layout: docs
kicker: Tutorial 8
description: An interactive word-scramble app and a scoped proof that decoding scrambled words requires contextual prediction, not letter perception alone.
---

You can raed tihs snetcene esaliy, eevn tguohh the itenranl lttrees are jmulbed.
Why does that work, and when does it *stop* working?

This tutorial does two things:

1. Build an interactive scrambler that checks invariants as it runs.
2. Prove a small impossibility result about decoding.

> **Claim (scoped):** In the model defined here, local letter features are not enough
> to uniquely decode every scrambled word. In ambiguous cases, a successful decoder
> must use additional information, such as sentence context or prior probabilities.

This is not a full theory of human reading. It is a narrow claim about one
transformation and one observation function.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Assumption hygiene (scope first)</p>
  <ul>
    <li><strong>Assumption A:</strong> the scrambler preserves first letter, last letter, length, and letter multiset (a "bag of letters")</li>
    <li><strong>Assumption B:</strong> there exist distinct words with the same preserved features (a collision)</li>
    <li><strong>Conditional claim:</strong> if A and B hold, then those local features cannot uniquely determine the intended word, and disambiguation requires extra information (for example, sentence context)</li>
  </ul>
</div>

<figure class="fp-figure" style="margin-top: var(--space-lg)">
  <p class="fp-figure-title">The scramble transformation at a glance</p>
  {% include diagrams/scramble-invariants.svg %}
  <figcaption class="fp-figure-caption">
    Blue cells are boundary anchors (first and last letter). They never move.
    Orange cells are interior letters. They get shuffled by a permutation.
    All three invariants (length, boundary, letter multiset) are preserved by construction.
  </figcaption>
</figure>

## Part I: what is known, and what is not

The viral "Cambridge study proves internal letters don't matter" meme overstates the evidence considerably.

- Rawlinson's 1976 thesis is often cited as early evidence for robust word recognition under internal-letter perturbation.
- Later experimental work (Rayner et al. 2006, Johnson & Eisler 2012) confirms that readers *can* decode scrambled text, but with measurable costs in speed and accuracy.

The defensible takeaway is narrower than the meme suggests:

- readers tolerate certain perturbations,
- reading performance degrades (it is not free),
- context and prediction help recover meaning (this is the key lever).

This tutorial uses that background as motivation. The formal results below are about
the scrambler and its invariants, not a general cognitive model of reading.

## Part II: app, scramble a paragraph while preserving readability

The app below lets the transformation be explored directly. Paste a paragraph, set a
scramble probability and a seed, and then compare the output with the invariant checks.

<div class="fp-card" style="padding: var(--space-lg); margin-top: var(--space-md)">
  <h3 class="fp-card-title">Predictive Reading Scrambler</h3>
  <p class="fp-card-text">
    Paste text, set scramble probability, and inspect invariant checks.
    Eligible tokens are alphabetic words with length 4 or more. Punctuation and whitespace stay fixed.
  </p>

  <label for="pr-input" style="display:block; font-weight:600; margin-top:12px">Input paragraph</label>
  <textarea id="pr-input" rows="8" style="width:100%; margin-top:6px"></textarea>

  <div style="display:grid; gap:12px; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); margin-top:12px">
    <div>
      <label for="pr-intensity" style="display:block; font-weight:600">Scramble probability</label>
      <input id="pr-intensity" type="range" min="0" max="100" step="1" value="65" style="width:100%" />
      <div class="fp-card-text"><span id="pr-intensity-value">65</span>% chance to scramble an eligible word</div>
    </div>
    <div>
      <label for="pr-seed" style="display:block; font-weight:600">Seed (repeatable runs)</label>
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

Here is the core logic used by the app above. It is a pure function given its RNG.
`scrambleProb` is a probability in `[0, 1]`.

```javascript
const scrambleWord = (word, scrambleProb, rng) => {
  if (word.length <= 3) return word;
  if (rng() >= scrambleProb) return word;

  const chars = word.split("");
  const start = 1;
  const end = chars.length - 1;
  const n = end - start;
  if (n < 2) return word;

  const pool = chars.slice(start, end);
  for (let i = pool.length - 1; i > 0; i -= 1) {
    const j = Math.floor(rng() * (i + 1));
    [pool[i], pool[j]] = [pool[j], pool[i]];
  }

  for (let i = 0; i < pool.length; i += 1) {
    chars[start + i] = pool[i];
  }

  // Avoid no-op shuffles when possible.
  if (chars.join("") === word && pool.length > 1) {
    const first = chars[start];
    for (let i = start; i < end - 1; i += 1) {
      chars[i] = chars[i + 1];
    }
    chars[end - 1] = first;
  }

  return chars.join("");
};
```

The function preserves boundary letters by construction. It only shuffles the slice
from index `1` through `chars.length - 2`, so the first and last characters are never
changed. The Fisher-Yates shuffle produces a permutation (a bijection), which preserves
the letter multiset.

## Part IV: invariants as logic statements

Now we can state exactly what the transformation preserves. These are not empirical observations; they follow directly from how `T` is defined.

For each word transformation `T(w) = w'`:

```text
I1 (Length):      len(w') = len(w)
I2 (Boundary):    if len(w) >= 4 then first(w') = first(w) and last(w') = last(w)
I3 (Multiset):    if len(w) >= 4 then bag(w') = bag(w)
I4 (Non-word):    punctuation/whitespace tokens are unchanged
```

The app verifies these invariants at runtime and flags any violations.

## Part V: two proof modes (formal and empirical)

This chapter relies on two distinct notions of proof:

- **Formal proof:** establishes properties of the scrambling transformation itself.
- **Empirical proof-by-witness:** demonstrates that humans can read certain scrambled sentences, evidenced by observed comprehension.

The app supports both:

- invariant checks support the formal part,
- human reading outcomes support the empirical part.

### Part V.A: formal proof (scoped model)

Model definitions:

- Let `Sigma*` be strings over an alphabet.
- For word `w = c0 c1 ... c(n-1)` with `n >= 4`, choose a permutation `pi` of the interior indices `{1..n-2}`.
- Transformation `T` keeps indices `0` and `n-1` fixed and permutes the interior according to `pi`.
- In the app, the scramble probability slider controls whether `T` applies a non-identity permutation to a word on a given run.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Theorem 1: invariants I1 through I3 hold for all transformed words</p>
  <p><strong>Proof sketch:</strong></p>
  <ol>
    <li><code>T</code> only reassigns characters to existing positions, so length is unchanged (<strong>I1</strong>).</li>
    <li>Indices <code>0</code> and <code>n-1</code> are fixed by definition, so first and last letters are unchanged (<strong>I2</strong>).</li>
    <li>A permutation is a bijection, so it preserves element counts in the permuted positions. Therefore the full letter multiset is preserved (<strong>I3</strong>). ∎</li>
  </ol>
</div>

### What the math means in plain language

The formal model says: pick a word, leave the first and last letters alone, and rearrange some of the middle letters. The three invariants are precise ways of saying:

1. **Length is unchanged.** No letters are added or removed, so the scrambled word has the same number of characters.
2. **Boundaries are unchanged.** The first and last letters stay put, which is why scrambled words still "look right" at a glance.
3. **Letter inventory is unchanged.** The same letters are present in the same quantities, just in different positions. Think of it like shuffling cards within a fixed frame.

The proof works because a permutation (a rearrangement) is a bijection: it moves things around without duplicating or losing any. If you shuffle five cards, you still have five cards, and each card appears exactly once.

<div class="fp-callout fp-callout-warn" style="margin-top: var(--space-lg)">
  <p class="fp-callout-title">Theorem 2: context-free decoding is not sufficient in general</p>
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
    beyond <code>Obs</code>, such as sentence context or prior probability.
    <strong>This is the predictive component.</strong> ∎
  </p>
</div>

### What Theorem 2 means in plain language

Consider the words **salt** and **slat**. Both start with `s`, end with `t`, have 4 letters, and contain exactly `{a, l, s, t}`. If you scrambled either word, the result could look like `slat` or `salt`, and there is no way to tell which original was intended by looking at the scrambled letters alone.

A reader (human or machine) that sees `slat` in isolation cannot know whether the writer meant "salt" or "slat." The ambiguity can be resolved using context: in *"add the slat to taste"*, the intended word is almost certainly *salt*, while in *"a slat in the fence"*, it is *slat*.

This is not a contrived edge case. English has many such collisions: **calm** and **clam** (`c...m`, 4 letters, `{a, c, l, m}`), **trail** and **trial** (`t...l`, 5 letters, `{a, i, l, r, t}`), **united** and **untied** (`u...d`, 6 letters, `{d, e, i, n, t, u}`). As the candidate vocabulary grows, collisions become more likely.

This is the core insight: **local letter features are not enough; prediction from context is required.**

<figure class="fp-figure" style="margin-top: var(--space-lg)">
  <p class="fp-figure-title">Why context-free decoding fails</p>
  {% include diagrams/obs-ambiguity.svg %}
  <figcaption class="fp-figure-caption">
    Two distinct words ("salt" and "slat") produce identical observations under Obs().
    A context-free decoder D cannot distinguish them, so sentence context is required
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

In this mode, the witness is measured success on the task (for example, comprehension above a pre-registered threshold) for the stated scope.

## Part VI: stress tests and edge cases

The scramble-and-read pipeline is not universally robust. Three failure modes are worth testing:

- **Scramble probability too high:** at extreme scramble levels, even strong context cannot rescue reading. The signal-to-noise ratio collapses.
- **Rare vocabulary:** domain jargon and uncommon words increase ambiguity because the reader's prior is weaker.
- **Weak context:** short isolated tokens (labels, single-word captions) give the predictive system little to work with.

App gate:

```text
If invariant checks fail, the transformation implementation is wrong.
If invariants pass but readability is poor, adjust scramble probability or text domain.
```

## Part VII: Godel and the limits of a model

Godel's incompleteness theorems are about the limits of formal axiomatic systems. The result in this tutorial is
smaller in scope, but it has a family resemblance worth noting.

- Godel incompleteness concerns the limits of formal axiomatic systems: there exist true statements that no finite proof within the system can derive.
- This chapter makes a narrower but structurally similar move: the formal model (Obs) provably cannot distinguish certain word pairs, so meaning recovery must come from outside the model, from context.

The analogy is limited. Godel operates over arithmetic and self-reference; Theorem 2 operates over a specific observation function. But the shared shape is:

- a formal system with definite boundaries,
- a demonstration that some truths lie beyond those boundaries,
- a pointer to where the extra information must come from.

## Part VIII: discussion, beyond the formal model (optional)

This tutorial's formal content ends at Theorem 2. The rest of this section is interpretation and open questions.
It is included because Theorem 2 has a useful general shape: if a model throws away information (Obs is many-to-one),
then a successful decoder must supply extra information, often in the form of priors and context.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Discussion note (not proved here)</p>
  <p style="margin-top:8px; font-size:0.92em">
    Theorem 2 is a statement about an observation function and an impossibility of unique decoding from that
    observation alone. It does not, by itself, identify a mechanism in the brain, or a mechanism in a language model.
    Mechanism claims require separate empirical evidence.
  </p>
</div>

At a high level, both human reading and language-model decoding can be framed as inference under uncertainty:

```text
Human reading: infer the intended word from letters + sentence context + world priors.
LLM decoding:  predict the next token from token context + learned distributional priors.
```

Shared pattern: uncertainty in local signal → contextual prior resolves ambiguity → prediction drives decoding.

### What LLMs can (and cannot) do here

An LLM reading scrambled text faces the same ambiguity problem as a human reader, but resolves it differently.

**What LLMs can do well:**

- **Contextual prediction.** LLMs can use surrounding tokens to predict the most likely intended word. Given "add the slat to taste", a model's learned distribution strongly favors "salt", the same disambiguation a reader performs.
- **Pattern completion at scale.** Because LLMs have been trained on large corpora, they carry frequency priors. Common words and phrases are recovered more reliably than rare ones.
- **Robustness to mild scrambling.** Tokenizers may split scrambled words into subword pieces, but attention can still recover meaning from context when scrambling is moderate.

**Where LLMs fall short:**

- **Limited grounding.** A human reading "pass the salt" can draw on embodied experience, such as a dinner scene and the feel of a salt shaker. A language model resolves the ambiguity through learned statistical associations, unless it is connected to tools or sensory inputs.
- **Brittle under heavy scrambling.** As scrambling increases, the word can be split into unusual token fragments. Recovery becomes harder, even with strong surrounding context.
- **No persistent symbolic state.** In the base model, there is no durable memory across conversations. Each run starts from the prompt unless external memory is added.
- **Context window boundary.** Human reading draws on a lifetime of experience. A model's immediate conditioning is bounded by its context window, with longer-term priors implicit in its trained parameters.

### Where humans go further (open hypothesis, not proved here)

One hypothesis is that reading often includes an integration step beyond local decoding:

- stories compress into symbols or concepts,
- symbols link into a structured concept graph (an internal worldview),
- operations run over symbols (if-then rules, branching, iteration, composition),
- symbols bind to autobiographical memory, affect, and multisensory traces (all five senses, emotional state, social context).

Concrete cultural-symbol example:

- Source story: *A Nightmare on Elm Street*.
- Compressed symbol: `FREDDY_GLOVE`.
- The symbol carries genre priors (horror), character identity, scenes, mood, and narrative constraints, not just the token itself.

```text
if symbol == FREDDY_GLOVE then tone := HORROR
if audience_age < threshold then reduce_intensity()
for motif in franchise_motifs: blend(motif, current_plot)
```

This is a conjectured mechanism-level story, not a result of Theorem 2. It is included to make one structural point:
decoding can be the first step in a longer pipeline that updates and queries a world-model.

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

### Prediction from scientific world models vs LLM language models

Assumption A7 (prediction target):

- scientific world models aim to predict physical observables under explicit assumptions,
- LLMs aim to predict token continuations under textual context.

Compare and contrast:

| Dimension | Human scientific prediction | LLM prediction |
|-----------|-----------------------------|----------------|
| **Model object** | Equations or theories about the physical world (for example, relativity, quantum theory) | Learned conditional distribution over tokens |
| **Primary target** | Future or unobserved physical quantities | Next token and downstream text continuation |
| **State representation** | World-model state with units, constraints, and causal structure | Context window of tokens and latent activations |
| **Validation** | Measurement, experiment, replication, error bars | Held-out text performance, task accuracy, calibration tests |
| **Failure mode** | Wrong assumptions, missing variables, model misspecification | Hallucination, context-window limits, spurious statistical patterns |

Compact prediction forms:

```text
Scientific-model style (abstract):
state_(t+1) = F_M(state_t, controls_t, disturbances_t)
observable_t = H_M(state_t)

LLM style:
token_n ~ Decode(P_theta(token_n | token_1..token_(n-1), prompt, retrieved_context))
```

Concrete scope note for the physics example:

- using equations such as E = mc^2 supports quantitative predictions inside the model's validity regime,
- this does not imply exact prediction of the full future state of the entire universe at practical resolution.

Interpretation:

- humans can use world models to predict non-linguistic reality directly, then compare with experiment,
- LLMs predict language directly, and can assist world prediction when connected to external models, tools, and data pipelines.

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

- agentic stacks with planners, tools, and memory can approximate parts of a human-like control loop,
- multimodal training and tool use can reduce some embodiment gaps,
- humans also rely on fast heuristics and often skip full deliberation,
- even with retrieval tools and memory layers, parity with human autobiographical grounding remains an open empirical question,
- the boundary is architectural and degree-based, not a claim that one side always outperforms on every task,
- whether current LLMs build and manipulate cultural symbols with the same depth and stability as human world-model symbols remains unresolved.

### Falsifiable predictions (for this discussion section)

1. As scramble probability rises, both humans and LLMs should rely more on context than local letter order.
2. With weak context, both should exhibit higher ambiguity and error rates on anagram-like collisions.
3. Strengthening context should recover performance more than strengthening isolated token visibility.
4. Tasks requiring narrative-to-symbol compression should favor systems with explicit world-model scaffolds.
5. Multi-step symbolic operations (rule chaining, branching, iterative refinement) should reveal a gap between pure next-token prediction and structured reasoning.
6. Cue-triggered retrieval with autobiographical and affective binding should show stronger human recall than text-only model recall.

## Part IX: what this proves, and what it does not

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Summary</p>
  <p><strong>Proved in this tutorial:</strong></p>
  <ul>
    <li>the scrambling transformation preserves formal invariants (Theorem 1),</li>
    <li>the observation map is not one-to-one in realistic cases: multiple words can look identical after scrambling,</li>
    <li>disambiguation therefore requires contextual prediction (Theorem 2).</li>
  </ul>
  <p style="margin-top:8px"><strong>Not proved here:</strong></p>
  <ul>
    <li>a full cognitive or neural theory of reading,</li>
    <li>exact predictive mechanisms in the brain,</li>
    <li>universal readability guarantees for all languages or scripts.</li>
  </ul>
</div>

The gap between "proved" and "not proved" is the honest boundary of this tutorial. The formal results are tight. Everything outside that scope requires separate evidence.

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
