---
title: "Counterexample-guided requirements discovery"
layout: docs
kicker: Tutorial 30
description: "Recover missing requirements from witnesses, observation quotients, and minimal separator policies, then study the bounded results that show when counterexamples alone are enough and when follow-up questions are structurally necessary."
---

<details open>
<summary><strong>Road map</strong></summary>

This tutorial studies missing requirements rather than buggy implementations.

- **Parts I-II**: requirement atoms, omission families, witness libraries, and the observation map
- **Parts III-IV**: the three recovery steps, scoped omissions, and the role of the ambiguity quotient
- **Parts V-VI**: the pair basis, separator languages, and the practical workflow
- **Part VII**: what the bounded results have already established

</details>

## The core problem

A specification can fail in two very different ways.

1. A stated requirement is implemented badly.
2. A requirement is missing from the specification itself.

This tutorial is about the second case.

The central question is:

When counterexamples expose missing constraints, how much can be recovered from
the witness structure alone, and when is a stakeholder oracle actually needed?

The bounded analysis in this repo turns that question into a small formal loop.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Vocabulary Note</p>
  <ul>
    <li><strong>Witness</strong> means a small signature that exposes a missing requirement pattern.</li>
    <li><strong>Quotient</strong> means the grouping induced by the current observation state, not a numerical quotient.</li>
    <li><strong>Residual controller</strong> means the small follow-up question policy that handles the ambiguity left after the first grouping.</li>
  </ul>
</div>

## Part I: the basic objects

Let:

- `R` be a bounded set of requirement atoms
- `M ⊆ R` be the hidden missing set, where `⊆` means "is a subset of"
- `W` be a witness library of admissible signatures

Each witness signature is itself a subset of requirement atoms.

The right loop state after saturated counterexample collection is:

```text
O_W(M) = {S in W | S ⊆ M}
```

That is the observation map.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Quick Logic Refresher</p>
  <ul>
    <li><strong>`⊆`</strong> means "is a subset of". So <code>M ⊆ R</code> means every missing requirement in <code>M</code> comes from the larger requirement set <code>R</code>.</li>
    <li><strong>`S ⊆ M`</strong> means the witness signature <code>S</code> is a subset of the hidden missing set <code>M</code>.</li>
    <li><strong>`|`</strong> means "such that", so the set builder reads: all signatures <code>S</code> in <code>W</code> such that <code>S</code> fits inside <code>M</code>.</li>
    <li><strong>`M ~ M'`</strong> below means the current loop state cannot distinguish the two missing sets.</li>
  </ul>
</div>

This is the first major correction to the vague workflow description:

- ask a checker
- collect a counterexample
- ask a human what was missing

The loop should be analyzed through `O_W(M)`, not only through one example at a
time.

## Part II: ambiguity classes

Once the observation map is explicit, the hidden targets inherit a quotient:

```text
M ~ M'  iff  O_W(M) = O_W(M')
```

Two missing sets that induce the same observation state are indistinguishable
to the loop at that stage.

The right recovery question is then how much of the hidden family has already
collapsed under the current observation state, not just whether a
counterexample arrived.

## Part III: the three recovery steps

The bounded analysis now has a clean three-step ladder.

### Step 1: direct atomic recovery

If every missing requirement has a singleton witness, direct pure recovery can
work.

That is the first step.

### Step 2: structured pure recovery

Even without singleton witnesses, pure recovery can still succeed if the full
observation map is injective on the omission family.

This is the first important correction from this analysis.

The real bottleneck is whether the full stored observation state already
separates the hidden targets, not only whether singleton witnesses exist.

### Step 3: question-policy recovery

If the observation map is not injective, the loop needs follow-up questions.

Rather than asking "should a human be consulted?", the design question becomes:
what is the smallest separator language that breaks the remaining ambiguity
classes?

## Part IV: omission scope matters

One of the strongest results in this tutorial line is that omission scope changes the
geometry sharply.

On unrestricted omission families, singleton witnesses remain a global
bottleneck.

On scoped families, especially pair-lobotomy families, oracle help becomes
strictly stronger. For instance, if the omission family is restricted so that
at most two requirements can be missing at once, the observation map becomes
injective much earlier than on the unrestricted family, and the separator
language needed to close the remaining gap shrinks accordingly.

So requirements discovery is not one monolithic task.

The omission family is part of the model and part of the loop design.

## Part V: pair basis plus separators

The pair basis is the clearest middle step found so far.

Once all pair witnesses are present:

- the residual ambiguity collapses to singleton uncertainty
- the remaining difficulty moves to separator language

The bounded ladder then becomes:

- pair-subset queries, no help
- singleton-membership queries, linear depth
- block-intersection queries, logarithmic depth

That is the clearest current example of a loop getting stronger because it:

1. changes geometry first
2. then uses a stronger residual controller

<figure class="fp-figure">
  <p class="fp-figure-title">Counterexamples, quotient, then separator policy</p>
  {% include diagrams/requirements-loop-ladder.svg %}
  <figcaption class="fp-figure-caption">
    The pair basis does the large geometric compression. Only then do block
    questions finish the remaining work.
  </figcaption>
</figure>

**Interactive lab**

- [Requirements Loop Geometry Lab]({{ '/requirements_loop_geometry_lab.html' | relative_url }})

## Part VI: the practical workflow

The bounded results suggest a practical discipline for requirements-discovery loops.

1. Fix the omission family.
2. Define the admissible witness library.
3. Compute the observation quotient.
4. Ask whether pure structured recovery already works.
5. Only then design the smallest separator language above the remaining
   ambiguity classes.

That is much cleaner than treating stakeholder follow-up as one undifferentiated
escape hatch.

The point is not to remove people from the loop. The point is to ask the
smallest, sharpest question that is still structurally necessary.

## Part VII: what the bounded results have achieved

The stable bounded ladder is now strong enough to teach as one coherent line.

It includes:

**Recovery and quotient structure:**
- recoverability laws
- the observation-quotient correction
- scoped omission-family effects

**Witness and basis results:**
- witness-arity threshold laws
- pair-basis sufficiency

**Separator and controller results:**
- separator expressivity
- singleton substitution
- the geometry prerequisite for logarithmic block separators

Together those results support one clean claim:

Counterexample-guided requirements discovery is a geometry problem.

The important questions are:

- what can the witness state already distinguish?
- what ambiguity remains?
- what extra questions are minimally necessary to close the gap?

## Related tutorials

- [Tutorial 29: Loop-space geometry]({{ '/tutorials/loop-space-geometry/' | relative_url }})
- [Tutorial 31: Hybrid geometry-changing loops]({{ '/tutorials/hybrid-geometry-changing-loops/' | relative_url }})
- [Tutorial 27: Verifier-compiler loops]({{ '/tutorials/verifier-compiler-loops/' | relative_url }})
