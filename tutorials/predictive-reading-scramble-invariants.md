---
title: Predictive reading (scrambled words, invariants, proof, and app)
layout: docs
kicker: Tutorial 8
description: An interactive word-scramble app plus a scoped proof that decoding scrambled words requires predictive context, not only local letter perception.
---

This tutorial builds a small app and uses it to make one precise claim:

- In a specific model of scrambled-word decoding, successful reading requires prediction from context.

The claim is scoped. It is not a full theory of human reading.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Assumption hygiene (scope first)</p>
  <ul>
    <li>Assumption A: the scrambling transformation preserves first letter, last letter, length, and letter multiset</li>
    <li>Assumption B: some different words share those same preserved features</li>
    <li>Conditional claim: if A and B hold, then local features are insufficient for unique decoding, and context-based prediction is required</li>
  </ul>
</div>

## Part I: what is known, and what is not

The viral "Cambridge study proves internal letters do not matter" meme overstates the result.

- Rawlinson's 1976 thesis is often cited as early evidence for robust word recognition under internal-letter perturbation.
- Later experiments show readers can still read scrambled text, but with measurable cost.

So the reliable statement is narrower:

- readers tolerate certain perturbations,
- reading performance degrades,
- context and prediction help recover meaning.

## Part II: app, scramble a paragraph but keep readability rails

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

## Part III: code example (from the app)

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

This function preserves boundaries and applies only a permutation to selected internal positions.

## Part IV: invariants as logic statements

For each word transformation `T(w) = w'`:

```text
I1 (Length):      len(w') = len(w)
I2 (Boundary):    if len(w) >= 4 then first(w') = first(w) and last(w') = last(w)
I3 (Multiset):    if len(w) >= 4 then bag(w') = bag(w)
I4 (Non-word):    punctuation/whitespace tokens are unchanged
```

The app checks these invariants at runtime and reports pass/fail.

## Part V: two proof modes (formal and empirical)

This chapter uses two different notions of proof:

- **Formal proof:** proves properties of the scrambling transformation.
- **Empirical proof-by-witness:** shows humans can read some scrambled sentences by observed successful reading/comprehension.

The app supports both:

- invariant checks support the formal part,
- human reading outcomes support the empirical part.

### Part V.A formal proof (scoped model)

Model definitions:

- Let `Sigma*` be strings over an alphabet.
- For word `w = c0 c1 ... c(n-1)` with `n >= 4`, choose a subset `S` of internal indices `{1..n-2}`.
- Let `pi` be a bijection on `S`.
- Transformation `T` keeps positions not in `S` fixed and permutes characters at positions in `S` by `pi`.

### Theorem 1: invariants I1-I3 hold for all transformed words

Proof sketch:

1. `T` only reassigns characters to existing positions, so length is unchanged (`I1`).
2. Indices `0` and `n-1` are never in `S`, so first and last letters are unchanged (`I2`).
3. A permutation is a bijection, so it preserves element counts in the permuted set. Non-permuted positions stay unchanged. Therefore the full letter multiset is preserved (`I3`).

QED.

### Theorem 2: context-free decoding is not sufficient in general

Define observation function:

```text
Obs(w) = (first(w), last(w), len(w), bag(w))
```

Assumption B gives at least one ambiguous pair `u != v` with `Obs(u) = Obs(v)`.
Concrete example: `salt` and `slat`.

Suppose a decoder `D` uses only `Obs`.
Because `Obs(u) = Obs(v)`, `D(Obs(u)) = D(Obs(v))`.
So `D` cannot output both `u` and `v` correctly in their respective contexts.

Therefore, a successful decoder in ambiguous cases must use extra information beyond `Obs`, such as sentence context or prior probability.

This is the predictive component.

QED.

### Part V.B empirical proof-by-witness (human readability)

Statement under test:

```text
S(alpha, corpus, population):
Humans in this population can read text transformed by T_alpha on this corpus
with non-trivial success.
```

Operational evidence protocol:

```text
1. Choose corpus and scramble level alpha.
2. Show transformed text to readers.
3. Measure at least one success metric:
   - comprehension questions,
   - word recovery accuracy,
   - reading time vs baseline.
4. If success is consistently above a pre-registered threshold, accept S for that scope.
```

In this empirical sense, a human successfully reading scrambled sentences is the witness. That witness is the proof event for the scoped statement.

## Part VI: stress tests and failure modes

- If scrambling is too strong, readability collapses.
- If text has many rare words or domain jargon, ambiguity rises.
- If context is weak (short isolated tokens), predictive recovery drops.

App gate:

```text
If invariant checks fail, the transformation implementation is wrong.
If invariants pass but readability is poor, adjust intensity or text domain.
```

## Part VII: relation to Godel-style results

This is not a Godel-style theorem.

- Godel incompleteness is about limits of formal axiomatic systems.
- This chapter combines a formal proof about a transformation with empirical evidence about human behavior.

Closest connection in spirit:

- both separate "what can be derived inside a formal system" from "what is true in a broader semantic or empirical setting".

## Part VIII: deeper insight as author hypothesis

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Author hypothesis (Dana Edwards)</p>
  <p>
    Dana Edwards' hypothesis is that human reading and LLM text processing share a common predictive core:
    both recover meaning by combining partial local signal with context-dependent prediction.
  </p>
</div>

Scope and caution:

- This is a hypothesis, not a theorem proved in this tutorial.
- The claim is structural similarity at the inference pattern level, not identity of mechanisms.

One compact comparison:

```text
Human reading (roughly): infer intended word from letters + sentence context + world priors.
LLM decoding: predict next token from token context + learned distributional priors.
```

Shared pattern:

- uncertainty in local signal,
- contextual prior resolves ambiguity,
- prediction drives decoding.

Important differences:

- humans use grounded multimodal cognition and biological perception,
- LLMs operate in tokenized vector spaces learned from text corpora,
- failure modes and generalization properties differ.

Falsifiable predictions for this hypothesis:

1. As scramble intensity rises, both humans and LLMs should rely more on context than local letter order.
2. With weak context, both should show higher ambiguity/error on anagram-like collisions.
3. Strengthening context should recover performance more than strengthening isolated token visibility.

## Part IX: what this proves, and what it does not prove

Proved in this tutorial:

- the scrambling transformation preserves formal invariants,
- the observation map is non-injective in realistic cases,
- disambiguation requires contextual prediction in those cases.

Not proved here:

- a full cognitive or neural theory of reading,
- exact predictive mechanisms in the brain,
- universal readability guarantees for all languages or scripts.

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
