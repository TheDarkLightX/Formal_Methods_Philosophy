---
title: "Hybrid geometry-changing loops"
layout: docs
kicker: Tutorial 31
description: "Study loops that first change ambiguity geometry and then compile or control the residue, rather than only learning a front-end for a verifier."
---

## The motivating contrast

Verifier-compilers are one important neuro-symbolic loop family. They try to learn a reusable symbolic front-end for an exact verifier. But they are not the only strong loops. Another family works differently. Instead of compiling the whole task family at once, it first changes the geometry of the task space and only then compiles or controls the smaller residue that remains. That is the design pattern this tutorial isolates.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Vocabulary note</p>
  <p><a href="{{ '/glossary/#quotient' | relative_url }}"><strong>Quotient</strong></a> means a partition of the task family into cases the current loop cannot yet tell apart. <a href="{{ '/glossary/#residue' | relative_url }}"><strong>Residue</strong></a> means the smaller leftover problem after that first partition. <a href="{{ '/glossary/#controller' | relative_url }}"><strong>Controller</strong></a> means the compact symbolic rule that handles that leftover problem. <a href="{{ '/glossary/#frontier' | relative_url }}"><strong>Frontier</strong></a> means the best checked tradeoff on a named bounded family.</p>
</div>

The front stage can take several forms. It might build a witness basis, apply a quotient map, change the temporal basis, or decompose the task family into structural regimes. The back stage then acts on whatever has been exposed by that reshaping step. It might ask a smaller sequence of questions, run a residual verifier, or compile a direct amount law for the cases that remain. The common idea is always the same: pay to simplify the geometry first, then solve a smaller problem second.

<figure class="fp-figure">
  <p class="fp-figure-title">Direct control versus hybrid control</p>
  {% include diagrams/hybrid-loop-comparison.svg %}
  <figcaption class="fp-figure-caption">
    The decisive difference is not only controller size. The hybrid loop pays
    for front-stage geometry change, settles a large mass of cases early, then
    uses a smaller residual controller.
  </figcaption>
</figure>

## Part I: the cleanest bounded example

The clearest example so far comes from requirements discovery. On exact missing-set identification with the same block-query language, a direct raw-family controller needs depth `n`, while a pair-basis plus block-separator residual controller needs only `ceil(log2 n)`. That is a real structural win on the controller side.

The gain comes from changing geometry first. The pair basis does not magically answer the whole problem. It reorganizes the family so that the remaining ambiguity collapses toward a singleton residue before the residual controller even starts. Once the loop reaches that smaller residue, the back-stage controller is solving a much easier problem than the direct controller was asked to solve at the start.

## Part II: why cost models matter

That does not mean the hybrid loop is automatically better in every regime.

Witness acquisition still costs something.

The bounded comparison line introduced a cleaner way to talk about that:

```text
U = alpha * pure_resolved_mass + beta * depth_saving - gamma * acquisition
```

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Formula refresher</p>
  <p><strong>`alpha`</strong> weights the value of cases settled early. <strong>`beta`</strong> weights the value of a smaller residual controller. <strong>`gamma`</strong> weights the cost of collecting the front-stage structure. The formula is therefore a scored tradeoff, not a universal law of nature. It says which loop wins under the chosen cost model.</p>
</div>

This matters because “better” becomes conditional. Some loops win when all cases are priced equally. Others win only when acquisition cost is expensive enough to matter. The right comparison is therefore never “which loop is smarter in the abstract.” It is always “which loop wins under the stated weights.”

<div class="fp-callout fp-callout-try">
  <p class="fp-callout-title">Hands-on exploration</p>
  <p>The <a href="{{ '/hybrid_loop_comparison_lab.html' | relative_url }}">Hybrid Loop Comparison Lab</a> lets the weighting question stay concrete by changing the front-stage acquisition cost and watching the preferred loop change with it.</p>
</div>

## Part III: graph-side regime compilers

The corrected graph line suggests a second kind of hybrid loop. Here the direct compiler does not come from one monolithic family. It comes from taking the maximum of several exact regimes, namely balanced star forests, repaired multipartite structure, and, on the checked small domain, one explicit point correction. That is already a geometry-changing loop because the frontier is being decomposed before anything is compiled.

Instead of learning one front-end for one verifier, the loop carves the frontier into exact regions and compiles those regions directly. On the checked high band, that overlap compresses into a piecewise compiler with a low plateau, a middle interval handled by the star-plus-leaf family, a near-top multipartite peak, and a top tie. The important point is not the list of regions by itself. The important point is that the competition between structural families has become a direct symbolic object that can be compiled.

<figure class="fp-figure">
  <p class="fp-figure-title">High-band overlap on the corrected graph line</p>
  {% include diagrams/graph-regime-overlap.svg %}
  <figcaption class="fp-figure-caption">
    The high checked band is now a genuine overlap zone. The exact compiler
    chooses between star-plus-low-edge and repaired multipartite rather than
    treating the graph line as one monolithic family.
  </figcaption>
</figure>

<div class="fp-callout fp-callout-try">
  <p class="fp-callout-title">Hands-on exploration</p>
  <p>The <a href="{{ '/graph_regime_compiler_lab.html' | relative_url }}">Graph Regime Compiler Lab</a> turns the regime-overlap story into a live piecewise compiler, so the reader can watch the frontier split into exact regions instead of only reading the description.</p>
</div>

## Part IV: the low-edge concentration mechanism

The low-edge analysis changed character at this point. It no longer has only a family compiler. It now has a proof-shaped hybrid with two distinct stages. First each connected component is starified. Then the resulting star sizes are balanced.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Advanced detail</p>
  <p>Part IV is the densest section of the tutorial. The reader only needs the reshape-then-balance picture on a first pass. The rest of the section explains how local move language, depth bounds, and finite alphabets refine that same story.</p>
</div>

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Graph vocabulary note</p>
  <p><strong>Star</strong> means the graph-theory shape with one hub vertex and several leaf vertices attached to it. <strong>Starify</strong> means reshape a component into that form. <strong>Balance star sizes</strong> means redistribute leaves so the component stars are as even in size as the model allows. A <strong>pendant subtree</strong> is a subtree hanging off the rest of the graph at one attachment point. A <strong>hub-target move</strong> is a local move that pushes mass toward a hub rather than away from it.</p>
</div>

The first stage survives in a surprisingly clean form on the checked tree domain. An improving pendant-subtree move can always be chosen so that it moves a pendant subtree with one internal fork toward a hub. That hub-target form survives, while the weaker leaf-only and pendant-star-only variants fail. The second stage is then exact balancing on the star-family side. So the hybrid is not merely an interpretation placed on top of the data. It is a two-stage mechanism whose first half and second half can each be stated precisely.

### The composed two-stage result

This subsection sharpens the depth bound and move alphabet. It can be skipped on a first reading without losing the main hybrid picture.

The low-edge line is another hybrid, but of a different kind. It begins with a concentration stage and only then applies an exact balancing stage. The newer composition result says that this is not merely a convenient interpretation. On the checked low-edge forest family, it is the surviving mechanism.

The tree-side subproblem sharpens that claim. The concentration path itself can stay inside the smaller local move language, so the method does not need to fall back to arbitrary pendant-subtree moves after the first step. The newest checked refinement is stronger again: the path survives even if each step is restricted to a smallest available hub-target move of the same form.

That controller now has an exact checked depth cutoff. On the checked tree domain, the smallest surviving branching-depth bound is `2`. The cutoff is not arbitrary. A terminal-cherry ladder family, a tree family built by stacking terminal cherry attachments, witnesses it because the `h = 2` case is exactly the shape that forces depth `2`. The positive side is exact too. Every move selected by that depth-2 controller belongs to a finite rooted alphabet consisting of leaves, cherries, three-leaf stars, broom-1 shapes, and broom-2 shapes. Here the broom names refer to two small rooted tree templates with one long handle and a short branching head. That alphabet is already minimal on the checked domain, so no proper subset survives.

### The exceptional route also fits the hybrid pattern

One checked two-fan state still escapes the stable local controller, namely `NTF(2, 8, 2)` on `n = 13`. At first that looked like bad news for compression because it introduced a special route through several named intermediate families.

The newer result reverses that impression. The route now has a compact amount law. On the feeder side, the exact count splits into a Fibonacci term plus a four-step periodic correction. If `B(r, t)` names that feeder count, then the full route deficit is simply the star amount minus `B(r, t)`:

```text
Delta(r, t) = 2^(r + t + 5) - 1 - B(r, t)
```

So even the exceptional case ends up following the same hybrid pattern. The loop first moves into better structural coordinates and then exposes a much smaller symbolic mechanism there. The special case did not break the hybrid picture. It forced the hybrid picture to become more explicit.

<figure class="fp-figure">
  <p class="fp-figure-title">Low-edge concentration and balancing</p>
  {% include diagrams/low-edge-concentration.svg %}
  <figcaption class="fp-figure-caption">
    The low-edge analysis is a hybrid too. It first concentrates component
    shape, then applies an exact size-balancing law.
  </figcaption>
</figure>

## Part V: what this means for loop search

The strongest future loop candidates are unlikely to be single-stage loops. The current bounded evidence points toward three recurring patterns: a quotient stage followed by a residual controller, a regime decomposition followed by a direct compiler, and a concentration stage followed by exact balancing. Those patterns look different on the surface, but they all express the same idea. The front stage pays an acquisition cost to reshape the problem, and the back stage reaps the savings on a smaller residue. In short, these loops reshape first and solve the smaller residue second.

## Part VI: what these bounded results have achieved

This tutorial line can now teach two broad lessons about loop design. The first is that geometry change can beat direct control, but only when the comparison is priced honestly. The pair-basis plus block-separator example remains the cleanest case, and the cost model from Part II explains why witness acquisition and residual savings have to be evaluated together rather than separately.

The second is that hybrid loops come in more than one exact form. Some become regime compilers, as on the graph line, where the frontier itself decomposes into exact regions. Others become concentration processes, as on the low-edge line, where a reshape stage exposes a much smaller balancing law. Together, those lessons justify hybrid geometry-changing loops as a tutorial line in their own right.

## Related tutorials

This page sits closest to [Tutorial 27: Verifier-compiler loops]({{ '/tutorials/verifier-compiler-loops/' | relative_url }}), [Tutorial 29: Loop-space geometry]({{ '/tutorials/loop-space-geometry/' | relative_url }}), and [Tutorial 30: Counterexample-guided requirements discovery]({{ '/tutorials/counterexample-guided-requirements-discovery/' | relative_url }}). Tutorial 27 is the best comparison if the question is when a front-end can be compiled directly. Tutorial 29 is the better next step if the focus is loop-space shape. Tutorial 30 is the better next step if the interest is requirements discovery as a geometry-changing loop.
