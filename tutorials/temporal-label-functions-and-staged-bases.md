---
title: "Temporal label functions and staged bases"
layout: docs
kicker: Tutorial 32
description: "A narrow tutorial on temporal label functions, monitor-cell labels, and why a richer label basis can be useful only after the right first-stage carving."
---

<details open>
<summary><strong>Road map</strong></summary>

This tutorial is narrower than the previous three. It focuses on one bounded
lesson that turned out to matter for loop design.

- **Parts I-II**: what a label function is, and why basis choice should be treated as a first-class loop axis
- **Parts III-IV**: the stable bounded temporal result and the geometry analogy
- **Part V**: why this small result still matters for larger loop search

</details>

## Why this tutorial exists

Many neuro-symbolic loops talk about labels as if there were one natural basis.

Typical examples are:

- pass or fail
- accepted or rejected
- flat trace classes

The temporal result shows that this picture is too simple.

Sometimes a richer temporal basis is not globally useful. But after the right
first-stage carving, it becomes exact.

That makes temporal labels a staged basis-change tool.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Vocabulary Note</p>
  <ul>
    <li><strong>Quotient</strong> means the grouping of cases that remain indistinguishable under the current label basis.</li>
    <li><strong>Residue</strong> means the smaller family left after the first carve.</li>
    <li><strong>Carve</strong> means the first coarse split of the task family before switching to a finer second-stage basis.</li>
    <li><strong>Controller</strong> means the compact symbolic rule used after that carve, not a physical control device.</li>
  </ul>
</div>

## Part I: a label function is a choice of coordinates

A label function says how the loop sees the task family.

If the labels are too coarse, different hidden structures collapse together.
If the labels are too fine, the loop may pay too much complexity too early.

So the real question is not:

- are temporal labels richer?

It is:

- when is a richer temporal basis the right basis?

The easiest analogy is coordinate choice in geometry.

A polar coordinate system can be the right tool for one subproblem and the
wrong tool for another. Temporal monitor labels can behave the same way.

## Part II: the bounded result

The stable bounded temporal result in this repo is small but sharp:

- raw monitor-cell labels strictly refine flat two-step trace labels on the
  full temporal controller family
- after first-step carving, the two label functions become partition-equivalent

So the richer temporal basis really does carry more information.

But the same result also shows that the extra information is not automatically the
right starting basis for the whole family.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Quick Logic Refresher</p>
  <ul>
    <li><strong>Partition-equivalent</strong> means two label functions cut the family into the same groups, even if they use different names.</li>
    <li><strong>Quotient</strong> means the grouped version of the family after cases that look the same under the current labels are merged.</li>
    <li><strong>Residue</strong> means the smaller family that remains after the first carve.</li>
  </ul>
</div>

<figure class="fp-figure">
  <p class="fp-figure-title">Temporal basis shift</p>
  {% include diagrams/temporal-label-basis-shift.svg %}
  <figcaption class="fp-figure-caption">
    The richer temporal basis is strictly finer on the full family, but after
    the first carve it no longer buys a finer partition.
  </figcaption>
</figure>

**Interactive lab**

- [Temporal Label Basis Lab]({{ '/temporal_label_basis_lab.html' | relative_url }})

## Part III: what this changes in loop design

This result is small, but it changes how basis choice should be treated.

Loop comparison should ask:

- what label basis is being used?
- what quotient does that basis induce?
- at what stage does that basis become exact?

That is a more useful question than simply asking whether one label set is
“richer” than another.

The temporal result suggests a staged design pattern:

1. carve the task family
2. switch to the richer temporal basis
3. compile or control the smaller residue

## Part IV: why this still matters

This tutorial is narrower than the others in the new sequence, but it does
real work.

It establishes that loop-space geometry includes:

- witness language
- separator language
- and label basis

That matters for larger loop families because it warns against a common mistake:

- assuming that the finest available basis is automatically the best global
  basis

The bounded result says that basis choice can itself be staged.

## Related tutorials

- [Tutorial 29: Loop-space geometry]({{ '/tutorials/loop-space-geometry/' | relative_url }})
- [Tutorial 31: Hybrid geometry-changing loops]({{ '/tutorials/hybrid-geometry-changing-loops/' | relative_url }})
- [Tutorial 27: Verifier-compiler loops]({{ '/tutorials/verifier-compiler-loops/' | relative_url }})

A richer label basis is not always a globally better basis. Sometimes the right
loop is:

- carve first
- switch basis second
- compile the residue third
