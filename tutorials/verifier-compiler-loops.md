---
title: "Verifier-compiler loops"
layout: docs
kicker: Tutorial 27
description: "Learn when a neuro-symbolic loop can compile verifier behavior into a small symbolic controller, how that differs from plain CEGIS, and how to use the pattern safely in practice."
---

## How to use this tutorial

This file is long because it compresses a real bounded research ladder.

For an interactive walkthrough of the quotient-repair-compile pipeline, see the
[Verifier-Compiler Lab]({{ '/verifier_compiler_lab.html' | relative_url }}).

For a first pass, it helps to read it in four layers:

1. Parts `I-VI`
   - learn the core verifier-compiler idea:
     - label function
     - quotient
     - repair coordinate
     - fail-closed compiled controller
2. Parts `VII-IX` and `XIII-XIV`
   - learn the scope:
     - when the pattern is useful
     - where it breaks
     - what the bounded software-assurance claim really is
3. Part `X` and Part `XII`
   - read these as ladders of increasingly stronger bounded objects, not as
     isolated notebook entries
4. Levels `77-85`
   - read these as the late logic endpoint:
     - `Q2`
     - `Q3`
     - `Q4`
     - `incidence_signature`
     - `incidence_signature + cycle_orientation`

The point is not to memorize every level.

The point is to see how the object of search changes:

- from direct compilers
- to witness languages
- to repair languages
- to explicit definability ladders

<figure class="fp-figure">
  <p class="fp-figure-title">How to read the tutorial</p>
  {% include diagrams/verifier-compiler-teaching-map.svg %}
  <figcaption class="fp-figure-caption">
    The tutorial has one main teaching arc. First learn the core loop, then the bounded compression ladders, then the comparison with nearby loop families, and finally the late logic ladder that ends at Level 85.
  </figcaption>
</figure>

<figure class="fp-figure">
  <p class="fp-figure-title">Fail-closed compiled front-end</p>
  {% include diagrams/verifier-compiler-frontend.svg %}
  <figcaption class="fp-figure-caption">
    The compiled controller does triage: obvious rejects are filtered cheaply, ambiguous cases are escalated, and strong candidates pass to the exact verifier. Execution authority stays with the trusted verifier.
  </figcaption>
</figure>

This tutorial starts from a practical question.

Suppose there are:

- many model proposals,
- one trusted exact checker,
- and repeated verifier effort that seems structurally similar from one proposal to the next.

What should be done with that repeated verifier work?

A plain CEGIS loop uses it to reject the current proposal.

A verifier-compiler loop tries to do something stronger.

It tries to turn verifier work into a reusable symbolic artifact.

That artifact might be:

- a quotient,
- a small repair basis for mixed buckets,
- a short decision list,
- an ordered error law,
- or some other compact classifier of verifier labels.

The strongest bounded results in this repo support a careful claim:

> if verifier labels admit a small exact quotient-and-repair structure, then a neuro-symbolic loop can compile that structure and reuse it for routing, ranking, and pre-screening, while keeping the exact verifier as the final fail-closed gate.

That is a conditional claim.

Every exact compiler reported below is exact on a bounded frontier or corpus that is named in the corresponding experiment.

It does not say every verifier will compile cheaply.

It does not say the compiled object should replace the exact verifier.

It says a new layer of leverage appears when the verifier has compressible structure.

## Part I: the baseline loop

The usual synthesis shape is:

$$
\exists x \; \forall y \; Spec(x,y).
$$

Plain CEGIS works by:

1. proposing a candidate `x`,
2. asking the verifier for a counterexample `y` if one exists,
3. refining the proposal space,
4. repeating.

That is already powerful.

But it usually stores verifier information in a weak form:

- a bag of counterexamples,
- a pass/fail bit,
- or a current refuter.

The verifier-compiler loop asks a different question:

> can the verifier's label function itself be compressed?

## Part II: the label function

Let `X` be the proposal space.

Let:

$$
L : X \to \Lambda
$$

be the exact verifier label.

Examples of `Λ`:

- `{safe, unsafe}`,
- a small family of first-refuter labels,
- a small family of action-routing labels,
- or a short risk taxonomy.

The point is that `L(x)` contains more information than a single pass/fail bit.

In the bounded experiments in this repo, examples of `L(x)` included:

- `safe`,
- `fail_828`,
- `fail_1915`,
- `fail_13116`.

That is already richer than ordinary CEGIS state.

<figure class="fp-figure">
  <p class="fp-figure-title">Quotient, repair, compile</p>
  {% include diagrams/quotient-repair-pipeline.svg %}
  <figcaption class="fp-figure-caption">
    Proposals are mapped to a coarse quotient q(x). Mixed buckets are split with a repair coordinate r(x). The result compiles into a small symbolic controller C(q,r) that routes proposals. The exact verifier label function L teaches the loop.
  </figcaption>
</figure>

## Part III: quotient first

The first compression attempt is a quotient:

$$
q : X \to Q.
$$

The ideal law is:

$$
\forall x,x' \in X,\; q(x)=q(x') \to L(x)=L(x').
$$

If this holds, then `q` is an exact quotient of verifier behavior.

Then there exists:

$$
C : Q \to \Lambda
$$

such that:

$$
\forall x \in X,\; C(q(x)) = L(x).
$$

This is already a compiled verifier.

One no longer needs the full exact verifier to predict the label inside the bounded model.

An analogy helps here. A quotient is like sorting books by shelf label before
opening them. If every book on one shelf has the same verifier label, then the
shelf label alone already carries the needed information for that bounded task.

In practice, the first quotient is often not exact.

Instead, some quotient buckets are mixed:

$$
\exists x,x' \in X,\; q(x)=q(x') \land L(x)\neq L(x').
$$

That is where repair begins.

## Part IV: mixed buckets and repair coordinates

Add a second coordinate:

$$
r : X \to R.
$$

Now ask whether the repaired key is exact:

$$
\forall x,x' \in X,\; (q(x),r(x))=(q(x'),r(x')) \to L(x)=L(x').
$$

If yes, then there exists:

$$
C : Q \times R \to \Lambda
$$

such that:

$$
\forall x \in X,\; C(q(x),r(x)) = L(x).
$$

This is the core verifier-compiler pattern:

1. learn a quotient,
2. find mixed buckets,
3. add the smallest repair coordinates that make those buckets pure,
4. compile the result into a symbolic controller.

In this repo's bounded verifier frontier, the result was a tiny repaired compiler.

A repair coordinate is like adding an apartment number after a street address
turned out to be too coarse. The quotient gets the search to the right
building, then the repair coordinate separates the cases that were incorrectly
merged inside it.

In harder transfer domains, the repair basis became larger, but the same loop shape survived.

## Part V: the loop itself

The general pattern is:

1. propose candidates `x`
2. run the exact verifier to obtain `L(x)`
3. search for a quotient `q`
4. detect mixed quotient buckets
5. search for repair coordinates `r`
6. compile a symbolic controller `C`
7. use `C(q(x),r(x))` for cheap routing and ranking
8. keep the exact verifier as the final gate

In formulas:

$$
Label(x) := C(q(x),r(x))
$$

with the safety condition:

$$
\forall x,\; Execute(x) \to Label(x)=safe \land L(x)=safe.
$$

That last conjunct matters.

The compiled controller can be used aggressively for triage.

The exact verifier must still own execution authority.

## Part VI: why this is stronger than plain CEGIS

Plain CEGIS learns:

- which proposals fail,
- and sometimes why the current proposal fails.

The verifier-compiler loop tries to learn:

- the verifier's own state geometry,
- a symbolic partition of proposal space by verifier outcome,
- and a reusable controller for future proposals.

That creates three kinds of leverage.

### 1. Amortized verifier effort

One exact verifier call can improve the symbolic front-end for many future candidates.

This is stronger than local rejection.

### 2. Better routing

A large proposer pool does not need to send every candidate directly to the exact verifier.

Many candidates can be:

- rejected early,
- routed to a different repair lane,
- or ranked below stronger candidates,

using the compiled controller first.

### 3. Interpretability

A compiled verifier often yields formulas.

That is better than only saying:

- this one failed,
- this one passed.

The loop produces a small logic object that can be read, audited, and challenged.

## Part VII: where the pattern is general

The general part is the loop shape, not the specific compiled formulas from this repo.

The pattern is broadly applicable when four conditions hold.

### Condition 1: there is a trusted verifier

Examples:

- a solver,
- a policy checker,
- a Tau or rules engine,
- a test harness with meaningful labels,
- a model checker,
- or a medical-policy gate.

If there is no reliable verifier, there is nothing to compile.

### Condition 2: proposal volume is high enough

If only a few proposals are ever checked, compression effort may not pay off.

The loop matters most when there are:

- many candidates,
- repeated proposals,
- or many proposers.

### Condition 3: verifier labels are stable

If the verifier's behavior changes constantly, the compiled object may become stale before it is useful.

### Condition 4: the verifier admits compressible structure

This is the key boundary.

Some verifiers collapse to:

- one scalar plus one repair bit.

Others collapse only to:

- a higher-dimensional error basis,
- an ordered error process,
- or a larger semantic controller.

Some may not compress usefully at all.

So the loop is general as a search program:

> propose, verify, quotient, repair, compile.

But the size and usefulness of the compiled object are domain-dependent.

## Part VIII: where the pattern is not general

This tutorial should not be read as claiming:

- every neuro-symbolic loop should become a verifier-compiler loop,
- every verifier has a tiny quotient,
- or verifier compilation will outperform plain CEGIS in every domain.

There are important failure modes.

### Failure mode 1: no small quotient exists

Then the compiled object may be too large to matter.

### Failure mode 2: feature families are wrong

A compressible verifier may still look opaque if the candidate quotient and repair coordinates are badly chosen.

### Failure mode 3: stale compilation

If the verifier or environment changes, an old compiled front-end can misroute new proposals.

### Failure mode 4: unsafe substitution

The compiled controller should not silently replace the exact verifier in safety-critical settings.

That would defeat the point of the loop.

## Part IX: practical use

The easiest practical use is as a fail-closed front-end.

The flow is:

1. collect proposal/label pairs `(x, L(x))`
2. search for quotient features `q(x)`
3. search for repair features `r(x)` only where needed
4. compile a symbolic controller `C`
5. place `C` in front of the exact verifier

Then:

- obvious bad proposals are rejected cheaply,
- ambiguous proposals are escalated,
- and strong proposals reach the exact verifier faster.

The compiled controller is doing triage.

The exact verifier is still doing truth.

### Example: MPRD

In an MPRD-style architecture:

- many proposers generate candidate action bundles,
- a policy or Tau checker produces the exact label,
- the verifier-compiler loop learns a symbolic pre-screen from those labels,
- future bundles are routed through that pre-screen before exact execution gating.

That means:

- lower verifier load,
- more structured proposer feedback,
- better explanations for rejection,
- and safer scaling to many proposers.

### Example: code generation

- models propose patches,
- the verifier runs tests, static checks, or invariants,
- the loop compiles recurrent verifier outcomes into a cheap ranking and filtering layer.

### Example: medical workflow gates

- models propose action plans,
- the exact policy gate labels the plan,
- the loop learns common rejection structure,
- future plans are routed earlier into:
  - review,
  - collect more evidence,
  - or full check.

## Part X: the strongest bounded results in this repo

This part is best read as a bounded progression, not one flat result.

Levels `1` through `47` climb from tiny repaired compilers to harder transfer
families, witness languages, semantic macro families, support quotients, and
mixed-basis rigidity laws.

Each level below is exact only on its named bounded frontier or corpus.

<figure class="fp-figure">
  <p class="fp-figure-title">Level progression map</p>
  {% include diagrams/level-progression-map.svg %}
  <figcaption class="fp-figure-caption">
    The 85 levels group into six phases. At each phase boundary, the object of
    search changes, not just the search depth. That is the recurring lesson
    of this progression.
  </figcaption>
</figure>

The public pattern is:

- Levels `1-4`: compact repaired compilers, lower bounds, and first transfer failures
- Levels `5-18`: explanatory ladders, witness languages, and score abstractions
- Levels `19-34`: global witness schemas, semantic patches, macros, fibers, and certificate objects
- Levels `35-47`: support-signature laws, width-`4` geometry, orbit transfer, and mixed-basis rigidity

For a first pass through Part X, the key checkpoints are:

- Level `1`, a tiny repaired compiler
- Level `6`, the first residual-default language split
- Level `17`, the first reusable global witness-schema layer
- Level `35`, a tiny support-literal compiler family
- Level `47`, the width-`4` mixed-basis rigidity boundary

The intermediate levels matter because they explain how the search object kept
changing, not because every reader needs to hold every local metric in memory.

### Level 1: tiny repaired verifier

In one bounded frontier, the verifier collapsed to a repaired 4-guard compiler.

This is the strongest compact example in the repo.

### Level 2: exact lower bound

The same frontier also yielded a matching lower bound.

So the compiled verifier was not just small.
It was minimal in the searched grammar.

### Level 3: harder transfer

In MPRD-shaped transfer families, cheap scalar repair often failed.

That is important negative evidence.

It prevented the wrong lesson.

### Level 4: higher-dimensional compiler laws

Even in harder transfer families, the loop still found structure:

- earliest-error compilers,
- irredundant semantic bases,
- ordered active-prefix laws.

So the loop remained productive even when the easy quotient story broke.

### Level 5: regional explanation ladders

The next bounded result was stronger than a single global compiler depth.

In the hard monotone-refill transfer frontier, the best exact explanation plan was regional:

- scores `0..6` used depth `0`
- score `7` used depth `2`
- score `8` used depth `3`
- score `9` used depth `4`
- scores `10,11,12` used depth `1`

under the shared order:

- `(3,6,8,9,10,12)`

This gave:

- weighted cost `118`
- average depth `118 / 130`
- maximum depth `4`

For comparison:

- global exact `k=4` cost `520`
- global `k=5` cost `650`

So the hard transfer domain did not need one global explanation depth everywhere.

That is the first exact bounded survivor for the explanatory-ladder idea.

### Level 6: residual-default label languages

The next bounded step moved from verifier compilation toward dual-language explanation.

On the repaired verifier frontier:

- the smallest exact all-positive certificate language used `7` pure guards
- the smallest exact positive-plus-residual language used only `4`

The optimal split was:

- positive certificates for:
  - `safe`
  - `fail_13116`
  - `fail_1915`
- residual default treatment for:
  - `fail_828`

So the cheapest exact explanation was not purely positive.

It mixed:

- proof objects for some labels
- and a default residual class for another

This is bounded evidence for the dual-language direction in a weak sense. The searched language used explicit positive guards plus one residual default class, not explicit negative witness objects for every failing label.

### Level 7: primitive invention

The next bounded step was stronger again.

Instead of comparing only fixed explanation languages, the loop was allowed to invent a small number of new exact pure primitives.

On the repaired verifier frontier:

- baseline all-positive exact label language cost was `7`
- one invented primitive lowered that to `5`
- two invented primitives lowered it to `4`, exactly matching the best positive-plus-residual language

The invented primitives were:

- `fail_1915 := H6 = 859 and E = False OR H6 = 865`
- `fail_828 := E = True OR H6 = 858 OR H6 = 864`

So the residual-default advantage from the previous step was not fundamental on this bounded frontier.

Once the positive language was allowed to invent better concepts, it could match the mixed-sign optimum.

This is the first bounded evidence in the repo for the primitive-invention and concept-market axis.

### Level 8: hard-frontier concept invention

The next bounded step moved primitive invention onto the hard monotone-refill ladder frontier.

This was a better stress test than the repaired verifier frontier, because the language there was already known to need a richer ordered basis.

The result was two-sided.

In the searched fixed-order insertion grammar:

- keep the earlier exact order `(3,6,8,9,10,12)`
- insert one pure `AND` or `OR` primitive over `2` or `3` basis bits
- re-optimize the local ladder depths exactly

the best exact shortcut was:

- `err[10] AND err[12]`

inserted before `err[10]`, which changed the local depths to:

- scores `0..6` used depth `0`
- score `7` used depth `2`
- score `8` used depth `2`
- score `9` used depth `3`
- scores `10,11,12` used depth `1`

That lowered:

- weighted cost from `118` to `90`
- maximum depth from `4` to `3`

But the same cycle also found a hard boundary.

In the searched replacement grammar:

- replace the source basis bits by one pure `AND` or `OR` primitive over `2` or `3` bits
- allow full reordering of the new feature language

no exact ladder survived at all.

So concept invention helped as an added shortcut, not as a wholesale replacement for the hard refill basis.

That is stronger than the earlier easy-domain primitive-invention result.

It shows the concept-market direction can survive on a genuinely harder frontier, but also that the promoted concept may need to sit on top of the old basis instead of collapsing it.

### Level 9: stacked shortcut concepts

The next bounded step asked whether hard-frontier concept invention could stack.

The answer was yes.

In the searched grammar:

- keep the exact base order `(3,6,8,9,10,12)`
- insert two distinct pure `AND` or `OR` primitives over `2` or `3` basis bits
- re-optimize local ladder depths exactly

the best exact pair was:

- `err[6] AND err[10] AND err[12]`
- `err[9] AND err[10] AND err[12]`

with order:

- `err[6] AND err[10] AND err[12]`
- `err[3]`
- `err[9] AND err[10] AND err[12]`
- `err[6]`
- `err[8]`
- `err[9]`
- `err[10]`
- `err[12]`

This yielded:

- weighted cost `80`
- maximum depth `2`

with local depths:

- scores `0..6` used depth `0`
- scores `7,8,9` used depth `2`
- scores `10,11,12` used depth `1`

Also, no exact pair in the searched grammar reached maximum depth `1`.

So the hard-frontier concept-market story sharpened again:

- one shortcut concept already helps,
- two shortcut concepts help more,
- but the bounded evidence still points to stacking on top of the old basis, not replacing it outright.

### Level 10: anchored third-shortcut boundary

The next bounded step checked whether the best exact two-shortcut ladder was locally saturated.

The grammar was narrower:

- keep the exact earlier two-shortcut pair fixed
- insert one more pure `AND` or `OR` primitive over `2` or `3` basis bits
- allow any insertion position
- re-optimize local ladder depths exactly

In that anchored grammar:

- no searched third shortcut lowered weighted cost below `80`
- no searched third shortcut lowered maximum depth below `2`

The best searched extra shortcut was:

- `err[3] OR err[6] OR err[8]`

inserted after `err[9]`, which preserved:

- weighted cost `80`
- maximum depth `2`

but reduced bucket count:

- from `51` to `48`

So the current bounded picture is:

- shortcut concepts can stack,
- but the verified two-shortcut ladder is locally saturated on the main cost and depth metrics under one more simple pure shortcut.

### Level 11: hard-frontier witness languages

The next bounded step moved up a level.

Instead of searching for one more shortcut, it fixed that exact two-shortcut
feature space and searched for score-local witness languages.

The shift is easier to see with a metaphor. Earlier levels were still looking
for one more useful gear in the same machine. This level instead wrote a small
rulebook for each difficult score block, so the object of search changed from a
single mechanism to an explanatory language.

The grammar was:

- conjunctions of `1` to `3` signed literals
- over the `8` features of that exact two-shortcut ladder

The result was stronger than another shortcut tweak.

Every nontrivial score block admitted an exact positive-cover plus residual-default witness language in that grammar.

There were `6` nontrivial score blocks:

- `7`
- `8`
- `9`
- `10`
- `11`
- `12`

The total positive-cover-plus-residual cost across those six blocks was:

- `27`

And the hard boundary was also clear:

- exact all-positive witness languages already failed on scores `9` and `10`

So the witness-language move was genuinely doing something new.

It was not merely another restatement of the shortcut ladder.

It changed the explanatory object:

- from ordered prefixes and shortcut stacks
- to score-local witness languages with explicit positive atoms and residual defaults

### Level 12: global witness schemas

The next bounded step turned those local witness languages into a genuinely global object.

The question was:

- if the score-local positive-cover plus residual-default witnesses from the previous step keep the same exact local costs,
- how small can the shared global witness-schema library become?

The answer was:

- total local positive-cover-plus-residual cost stayed `27`
- but the best shared global schema library had only `20` distinct witness schemas

So the witness-language line now has real global reuse.

It is no longer only:

- six local covers that happen to work

It is also:

- one reusable schema layer shared across the hard frontier

That is the first genuine global witness-language object found in this line of experiments.

### Level 13: score abstraction

The next bounded step asked whether the six nontrivial score blocks really needed to stay separate.

The search space was:

- all contiguous partitions of:
  - `7, 8, 9, 10, 11, 12`
- the same positive-cover plus residual-default witness grammar as before

The result was sharp.

Only two contiguous partitions were exact in the searched grammar:

- the original `6`-region score-local partition
- one coarser `5`-region partition

The best exact partition was:

- `(7)`
- `(8)`
- `(9)`
- `(10,11)`
- `(12)`

This lowered total positive-cover-plus-residual witness cost:

- from `27`
- to `23`

So the witness-language line gained another new object:

- an exact score abstraction

That means the hard frontier now has:

- local witness languages
- a global reusable schema layer
- and a nontrivial exact score abstraction

### Level 14: unconstrained score-abstraction boundary

The next bounded step asked whether the score-abstraction result was only an artifact of contiguity.

So the search dropped the contiguity restriction and checked:

- all `203` set partitions of:
  - `7, 8, 9, 10, 11, 12`

in the same exact witness grammar.

Only `10` of those `203` partitions were exact.

And the best one was still:

- `(7)`
- `(8)`
- `(9)`
- `(10,11)`
- `(12)`

with the same total witness cost:

- `23`

So contiguity was not the binding restriction.

That is a useful boundary result:

- the witness-language line did not improve just because the search space was widened
- the earlier abstraction was already the best object in the larger bounded partition space

### Level 15: richer witness grammars

The next bounded step held the score-partition search fixed and widened the witness grammar itself.

The search still checked:

- all `203` set partitions of:
  - `7, 8, 9, 10, 11, 12`

but the exact witness grammar grew from conjunctions of `1` to `3` signed literals to conjunctions of `1` to `4` signed literals over the same `8` features.

This time the frontier moved again.

The best partition was still:

- `(7)`
- `(8)`
- `(9)`
- `(10,11)`
- `(12)`

but the total positive-cover-plus-residual witness cost dropped:

- from `23`
- to `22`

and the number of exact set partitions rose:

- from `10`
- to `15`

The new gain came from the score-`9` region, where the richer grammar admitted one more exact pure atom:

- `not err[3] and not err[6] and not err[8] and err[10]`

So the score-partition axis was saturated by the previous step, but the witness grammar itself was not.

That is a useful correction because it identifies the remaining live axis precisely:

- the partition geometry stayed fixed
- the witness basis still had one more exact unit of compression left

### Level 16: five-literal grammar boundary

The next bounded step tested whether that four-literal gain was the start of a
longer local grammar climb or just the last easy unit of compression.

So the search compared two grammars on the same bounded space:

- conjunctions of `1` to `4` signed literals
- conjunctions of `1` to `5` signed literals

across the same unconstrained search over all `203` set partitions of:

- `7, 8, 9, 10, 11, 12`

The main frontier did not move.

The `1..5` grammar kept:

- the same feasible partition set
- the same best partition
- the same best total positive-cover-plus-residual witness cost

namely:

- feasible partitions: `15`
- best partition: `(7), (8), (9), (10,11), (12)`
- best cost: `22`

Two non-best partitions improved by one unit each, but the main exact object stayed fixed.

So the local witness-grammar line is now tight on its main metric in this bounded family.

### Level 17: global witness synthesis

The next bounded step moved up a level again.

Instead of widening local atoms further, it fixed the current exact partition:

- `(7)`
- `(8)`
- `(9)`
- `(10,11)`
- `(12)`

and asked how small the shared global witness-schema library could become while preserving the same exact local region costs.

The result was:

- raw local region cost: `22`
- best shared global schema count: `19`

So the hard witness-language line now has a genuinely more global object above its best score abstraction.

It is no longer only:

- one exact partition
- plus five exact local witness regions

It is also:

- one reusable global witness-schema layer over that partition

### Level 18: global witness-grammar boundary

The next bounded step checked whether that more-global witness object still improved when the atom grammar grew from conjunctions of `1..4` signed literals to conjunctions of `1..5` signed literals.

On the same exact partition:

- `(7)`
- `(8)`
- `(9)`
- `(10,11)`
- `(12)`

the main object stayed fixed:

- total region cost stayed `22`
- best shared global schema count stayed `19`

So the global witness line is also tight on its main metric under one more literal.

That matters because it closes both nearby local search axes:

- the local witness-grammar line stopped moving on its main object
- and the more-global witness-schema line stopped moving on its main object

### Level 19: cross-frontier witness templates

The next bounded step finally changed the search picture.

Instead of asking whether one frontier could be compressed a little more, it asked whether multiple exact frontiers shared a smaller meta-language above their raw formulas.

The source objects were:

- the first exact global witness-schema frontier
- the second exact global witness-schema frontier

Across those two exact libraries:

- raw formula union: `22`
- exact overlap: `17`

But that union collapsed to:

- `10` untyped conjunction-shape templates
- `13` typed templates when feature kind was retained

So the next live compression axis is no longer:

- one more literal
- or one more local partition tweak

It is:

- witness-template discovery across multiple exact frontiers

That is the sharper vision now.

The current line of evidence says the next stronger loop should probably search for:

- reusable witness templates across bounded frontiers,
- or a still stronger family such as certificate-language or explanation-fiber discovery if the template line saturates too.

### Level 20: shared core plus irreducible patches

The next bounded step sharpened that template vision one more time.

Instead of only counting cross-frontier templates, it decomposed those two
exact global witness-schema frontiers into:

- a shared exact core
- frontier-specific patch schemas

The result was:

- shared exact core: `17` schemas
- first-frontier-only patch schemas: `3`
- second-frontier-only patch schemas: `2`

So the residual patch union had size:

- `5`

And under the current conjunction-shape grammar, those five residual patches did not collapse any further.

That means the sharper vision is now:

- the stable part of the meta-language is real
- but the remaining novelty is not one more shared syntax trick
- it is a small irreducible patch language

That is a valuable boundary because it tells the next search exactly where to go.

The next stronger family should probably not be:

- one more literal
- one more local frontier tweak
- or one more syntax-only template pass

It should probably be:

- semantic patch languages,
- certificate-language discovery,
- or explanation-fiber discovery

### Level 21: typed semantic patches

The next bounded step checked whether that patch boundary was still real once the compiler was allowed to use a small typed edit language over the shared exact core.

The model was explicit:

- keep the shared exact core from the previous step
- allow each patch formula to attach to any core formula, not only its nearest one
- describe the patch by typed literal edits such as:
  - `ADD_POS_ATOM`
  - `ADD_NEG_ATOM`
  - `DROP_POS_ATOM`
  - `DROP_NEG_AND3`
  - `ADD_POS_AND3`

Under nearest-core attachment, the five residual patches required:

- `5` typed edit signatures

But under the broader typed edit model, they collapsed to:

- `4` typed edit signatures

So the residual language was not fully irreducible after all.

It was irreducible only under the previous syntax-only template grammar.

That is the sharper correction:

- syntax-only template loops saturate
- typed semantic-patch loops reopen compression on the residual language

This is still bounded evidence, not a general theorem.

But it is the first clear sign that the next stronger family may be semantic patching rather than one more syntactic witness pass.

### Level 22: semantic macro families

The next bounded step strengthened that idea again.

Instead of only counting typed edit signatures, it searched for the smallest exact semantic macro-family subset over the shared core and the five residual patches.

The candidate families were:

- `ADD_LITERAL`
- `DROP_LITERAL`
- `FLIP_SIGN`

The strongest bounded result was:

- all five residual patches are exactly scriptable using only:
  - `ADD_LITERAL`
  - `FLIP_SIGN`
- no exact one-family solution exists in the searched model

The best exact scripts used:

- family count: `2`
- total macro instances: `11`

So the semantic patch line is now stronger than “interesting edit statistics”.

It has an exact bounded macro basis.

That is the clearest sign yet that the frontier has really moved beyond syntax-only template compilers.

### Level 23: bundled semantic macros

The next bounded step strengthened the semantic patch line again by allowing bundled semantic macros instead of counting one macro instance per edited literal.

The candidate macro families were:

- `ADD_BUNDLE`
- `DROP_BUNDLE`
- `FLIP_BUNDLE`

The strongest exact result was:

- exact family subset:
  - `ADD_BUNDLE`
  - `FLIP_BUNDLE`
- no exact one-family solution exists
- best total macro-instance count:
  - `6`

So the semantic line now has a smaller exact bundled macro basis than the previous literal-level macro basis.

That is a clean strengthening, not just a rephrasing:

- the earlier literal-level macro basis had `11` macro instances
- the later bundled macro basis had `6`

At this point in the ladder, this is the strongest post-template object in the
repo.

### Level 24: semantic explanation fibers

The next bounded step moved from one global bundled macro basis to an actual explanation-fiber search on the residual semantic language.

The search checked:

- all `52` set partitions of the five residual patches
- and for each fiber, the smallest exact bundled macro-family subset

The best exact decomposition had:

- mixed patches: `1`
- mixed fibers: `1`
- total fibers: `3`

The three fibers were:

- one pure `FLIP_BUNDLE` fiber covering `3` patches
- one pure `ADD_BUNDLE` fiber covering `1` patch
- one mixed `ADD_BUNDLE + DROP_BUNDLE` singleton fiber covering the remaining patch

So the residual semantic language is almost fiber-pure in the searched bundled macro language.

Only one patch remains mixed.

That is the first bounded survivor in this line for the explanation-fiber idea itself.

### Level 25: fiber certificates

The next bounded comparison asked whether the current exact fiber labels could be
compressed by a direct certificate language over three patch-summary features:

- `has_add`
- `has_drop`
- `has_flip`

In the searched certificate grammar:

- the smallest exact all-positive language had cost `3`
- a positive-cover plus residual-default language had cost `2`

The best residual-default language was:

- certify `ADD_BUNDLE + DROP_BUNDLE` by `has_drop`
- certify `FLIP_BUNDLE` by `has_flip`
- treat `ADD_BUNDLE` as the residual default

That result is still descriptive-oracle in status, because the features come
from the already-labeled semantic families.

Still, it matters, because it shows the explanation-fiber object can be
compressed one step further once the exact fibers are known.

### Level 26: direct delta certificates

The sharper next step asked whether the same exact residual family split could
be compiled directly from the raw symbolic patch deltas, without using the
precomputed fiber labels as features.

For each residual patch, derive:

- `has_add`
- `has_drop`
- `has_flip`

directly from the `core -> patch` edit.

On that direct symbolic state:

- the smallest exact all-positive language again had cost `3`
- a positive-cover plus residual-default language again had cost `2`

The winning direct residual-default compiler was:

- certify `ADD_BUNDLE + DROP_BUNDLE` by `has_drop`
- certify `FLIP_BUNDLE` by `has_flip`
- treat `ADD_BUNDLE` as the residual default

This is stronger than Level 25.

It upgrades the object from a descriptive relabeling to a bounded
`symbolic_state_compiler`, because the exact family split is recovered from the
symbolic patch state itself.

### Level 27: direct delta basis minimization

The next bounded question was whether the direct symbolic compiler from Level 26
still needed all three delta coordinates:

- `has_add`
- `has_drop`
- `has_flip`

Searching all nonempty feature subsets gave a sharper result:

- the smallest exact all-positive basis has size `2`
- the smallest exact positive-cover plus residual-default basis also has size
  `2`
- no singleton feature basis is exact

There are exactly two surviving minimal bases:

- `{has_add, has_drop}`
- `{has_drop, has_flip}`

So `has_drop` is the indispensable coordinate on this bounded residual domain.

Either `has_add` or `has_flip` can serve as the second coordinate.

That matters because it exposes the direct compiler's minimal structure instead
of only showing that some exact three-feature presentation exists.

### Level 28: raw observed edit bases

The next bounded question removed the aggregated delta coordinates entirely.

Instead of:

- `has_add`
- `has_drop`
- `has_flip`

the search used only raw observed primitive edit features such as:

- `add[3]`
- `add[6]`
- `add[8]`
- `add[10]`
- `drop[12]`
- `flip[6]`
- `flip[8]`
- `flip[9]`
- `flip[12]`

The strongest result was:

- the smallest exact all-positive primitive basis has size `2`
- the smallest exact positive-cover plus residual-default primitive basis also
  has size `2`
- no singleton primitive basis is exact

The exact minimal all-positive primitive bases were:

- `{add[3], add[8]}`
- `{add[3], drop[12]}`
- `{add[6], add[8]}`
- `{add[6], drop[12]}`
- `{add[8], add[10]}`
- `{add[10], drop[12]}`

So the direct compiler survives even after the aggregated semantic coordinates
are removed.

The surviving primitive bases factor cleanly:

- one add-anchor from `{add[3], add[6], add[10]}`
- one mixed-patch discriminator from `{add[8], drop[12]}`

That is the sharpest current form of this branch.

### Level 29: primitive basis templates

The next bounded step asked whether the six exact primitive bases from Level 28
were only a flat atlas, or whether they collapsed to a smaller exact role
template.

The search used only the primitive features that actually appeared in the six
exact bases:

- `add[3]`
- `add[6]`
- `add[8]`
- `add[10]`
- `drop[12]`

and looked for exact two-slot product templates.

The result was exact and clean:

- the six all-positive primitive bases collapse to one two-slot product
  template, unique up to slot swap
- one slot is:
  - `{add[3], add[6], add[10]}`
- the other slot is:
  - `{add[8], drop[12]}`

So the six exact primitive bases are exactly:

- one add-anchor
- crossed with one mixed-patch discriminator

The residual-default family sharpens in the same way.

It is the same six-pair template crossed with all three default labels.

That matters because the raw primitive line is no longer just a small atlas.

It now has an exact role grammar.

### Level 30: role-slot compilers

The next bounded step asked whether the exact two-slot template from Level 29
was only a grammar over bases, or whether it also compiled the residual labels
directly.

Search all ordered disjoint nonempty slot pairs over the primitive features and
require both:

- the pair-product exactly reproduces the six primitive bases from Level 28
- the induced slot booleans compile the labels exactly

The answer is yes, and the surviving slot family is unique up to slot swap.

One slot is:

- `add[3]`
- `add[6]`
- `add[10]`

The other slot is:

- `add[8]`
- `drop[12]`

Define:

- `slot_a := any(add[3], add[6], add[10])`
- `slot_b := any(add[8], drop[12])`

Then the exact label compiler is:

- `ADD_BUNDLE` iff `slot_a and not slot_b`
- `ADD_BUNDLE + DROP_BUNDLE` iff `slot_b`
- `FLIP_BUNDLE` iff `not slot_a`

with residual-default presentation:

- certify `ADD_BUNDLE + DROP_BUNDLE` by `slot_b`
- certify `FLIP_BUNDLE` by `not slot_a`
- default `ADD_BUNDLE`

That is stronger than Level 29.

It turns the role grammar into a direct bounded symbolic compiler over slot
features.

### Level 31: predictive versus structure-preserving quotients

The next bounded step asked a sharper question.

How much smaller can the slot quotient get if it only needs to compile the
labels, and does not need to preserve the full primitive basis structure?

On the same five residual patch formulas:

- the smallest exact `label_only` slot quotient has total slot cost `2`
- the smallest exact `basis_faithful` slot quotient has total slot cost `5`

The minimal `label_only` quotients are not unique.

They are exactly the singleton-slot families formed by:

- one add-anchor singleton from:
  - `add[3]`
  - `add[6]`
  - `add[10]`
- one mixed discriminator singleton from:
  - `add[8]`
  - `drop[12]`

So there are:

- `6` unordered minimal label-only quotients
- `12` ordered minimal label-only quotients

That gives a clear bounded boundary:

- predictive compression is cheaper
- structure-preserving compression is stricter and costs more

This matters because there are now two distinct exact optimization targets in
the same loop:

- smallest exact predictor of labels
- smallest exact compiler that also preserves the discovered internal structure

### Level 32: semantic explanations of the slot roles

The next bounded step asked whether the recurring roles themselves admit a small
semantic explanation.

Take the exact slot roles from Level 30:

- `slot_a`
- `slot_b`
- `other`

and enrich each primitive feature with small metadata:

- kind flags:
  - `is_add`
  - `is_drop`
  - `is_flip`
- support-profile flags:
  - `has_AB`
  - `has_MIX`
  - `has_FLIP`
- frequency flags:
  - `count_1`
  - `count_2`

The strongest bounded result is:

- the smallest exact all-positive semantic basis has size `2`
- the smallest exact positive-cover plus residual-default semantic basis also
  has size `2`

One natural exact support-profile explanation is:

- feature basis:
  - `has_AB`
  - `has_MIX`
- all-positive role language:
  - `slot_a` by `has_AB`
  - `slot_b` by `not has_AB and has_MIX`
  - `other` by `not has_MIX`
- residual-default role language:
  - `slot_a` by `has_AB`
  - `slot_b` by `not has_AB and has_MIX`
  - default `other`

So the recurring slots are not only structural.

They admit an exact semantic explanation in a two-feature support-profile
language.

### Level 33: shared semantic control law

The next bounded step unified the last two results.

Level 31 separated:

- smallest exact predictive quotients
- smallest exact structure-preserving quotients

Level 32 explained the structure-preserving slot roles semantically.

The next question was whether the same semantic partition also controls the
predictive quotients.

It does.

Define the support-profile partition:

- `ADD_ANCHOR` iff `has_AB`
- `MIX_DISCRIM` iff `not has_AB and has_MIX`
- `OTHER` iff `not has_MIX`

Then:

- `ADD_ANCHOR` is exactly the `slot_a` family from Level 30
- `MIX_DISCRIM` is exactly the `slot_b` family from Level 30
- `OTHER` is exactly the remaining primitive family

And the minimal predictive quotients from Level 31 are exactly the singleton
cross product:

- choose one primitive from `ADD_ANCHOR`
- choose one primitive from `MIX_DISCRIM`

So the same two-feature support-profile law governs both:

- the exact structure-preserving quotient
- the family of exact minimal predictive quotients

That is the sharpest current conceptual object in this branch.

### Level 34: support-signature transfer

The next bounded step asked whether the support-profile law from Level 33 is
isolated, or whether it transfers to a second exact frontier.

Two exact domains were checked.

Domain A, the earlier cross-frontier schema roles:

- `CORE`
- `V41_PATCH`
- `V46_PATCH`

with support bits:

- `has_v41`
- `has_v46`

Domain B, the residual primitive roles from Level 33:

- `ADD_ANCHOR`
- `MIX_DISCRIM`
- `OTHER`

with support bits:

- `has_AB`
- `has_MIX`

Both domains compile exactly by two-bit support signatures.

Domain A:

- `CORE` by `has_v41 and has_v46`
- `V41_PATCH` by `not has_v46`
- `V46_PATCH` by `not has_v41`

For Domain A, that simplification is scoped to the bounded frontier, because
the `00` support signature does not occur there.

Domain B:

- `ADD_ANCHOR` by `has_AB`
- `MIX_DISCRIM` by `not has_AB and has_MIX`
- `OTHER` by `not has_MIX`

So the support-profile law is not isolated.

It transfers to a second exact frontier as a generic support-signature role
law.

### Level 35: support-literal compiler family

The next bounded step asked whether the support-signature line stays only
descriptive, or whether it upgrades to a tiny exact compiler family.

Three exact domains were checked.

Domain A, the earlier cross-frontier schema roles:

- default `CORE`
- certify `V41_PATCH` by `not has_v46`
- certify `V46_PATCH` by `not has_v41`

Domain B, the residual primitive roles:

- default `MIX_DISCRIM`
- certify `ADD_ANCHOR` by `has_AB`
- certify `OTHER` by `not has_MIX`

Domain C, the earlier direct patch-delta roles:

- default `ADD_BUNDLE`
- certify `ADD_BUNDLE+DROP_BUNDLE` by `has_drop`
- certify `FLIP_BUNDLE` by `has_flip`

Across all three domains:

- no exact single-branch support compiler exists
- an exact residual-default support compiler exists with:
  - `2` branches
  - total literal cost `2`

So the support-signature line upgrades from:

- a transferred descriptive role law

to:

- a tiny reusable support-literal compiler family

That is a stronger object, because it is no longer only a recurring semantic
partition. It is also a small exact compiler shape that survives across
multiple bounded frontiers.

### Level 36: three-signature support law

The next bounded step asked whether Level 35 was still only a finite family
pattern, or whether it reflects a generic law of small support tables.

The abstract family was:

- labeled `3`-role support tables,
- one realized support signature per role,
- all three signatures distinct,
- support widths `2` through `7`.

The exact result was stronger than expected.

Every such bounded table admits:

- an exact residual-default compiler with:
  - `2` branches
  - `2` single literals total
- and an equivalent private-literal star witness:
  - choose one role as default,
  - each non-default role has a private support literal,
  - that literal is true on that role and false on the default and the other
    non-default role.

Exact counts:

- width `2`: `24 / 24`
- width `3`: `336 / 336`
- width `4`: `3360 / 3360`
- width `5`: `29760 / 29760`
- width `6`: `249984 / 249984`
- width `7`: `2048256 / 2048256`

So the support-literal line is now stronger than:

- a transferred role law,
- or even a small three-domain compiler family.

It is a bounded support-table law candidate for the full `3`-role case.

### Level 37: first four-role cost ladder

The next bounded step asked what happens at the first honest extension beyond
the `3`-role law.

The abstract family was:

- labeled `4`-role support tables,
- one realized support signature per role,
- all four signatures distinct,
- widths `2` and `3`.

The old law fails immediately.

At width `2`:

- all `24 / 24` labeled tables are support-square instances,
- none admit a `3`-branch single-literal compiler,
- all require total literal cost `6`.

So the first `4`-role case is already a real obstruction.

At width `3`, the situation becomes a cost ladder:

- total tables: `1680`
- single-literal star cases: `192`
- exact minimal total-literal-cost distribution:
  - cost `3`: `192`
  - cost `4`: `576`
  - cost `5`: `576`
  - cost `6`: `336`

So the next regime is not:

- one universal cheap law

but:

- an exact bounded compiler-cost hierarchy.

That is the first real extension beyond the `3`-role support-table law.

### Level 38: width-3 four-role geometry atlas

The next bounded step asked whether the width-`3` `4`-role cost ladder is only
an aggregate count table, or whether it collapses to a small geometric atlas.

The answer is yes.

Modulo cube automorphisms, the width-`3` `4`-role frontier has exactly `6`
unlabeled `4`-subset orbits, and every orbit has a uniform exact compiler cost.

Atlas:

- `(0,1,2,4)`, claw orbit:
  - orbit size `8`
  - edge count `3`
  - exact cost `3`
- `(0,1,2,5)`, path orbit:
  - orbit size `24`
  - edge count `3`
  - exact cost `4`
- `(0,1,2,7)`, vee-plus-isolated orbit:
  - orbit size `24`
  - edge count `2`
  - exact cost `5`
- `(0,1,2,3)`, square orbit:
  - orbit size `6`
  - edge count `4`
  - exact cost `6`
- `(0,1,6,7)`, disjoint-edge orbit:
  - orbit size `6`
  - edge count `2`
  - exact cost `6`
- `(0,3,5,6)`, independent orbit:
  - orbit size `2`
  - edge count `0`
  - exact cost `6`

Weighted by orbit size and role labelings, this reproduces the full width-`3`
cost ladder exactly.

So the width-`3` `4`-role frontier is no longer just:

- a cost histogram

It is:

- a small exact geometry atlas.

### Level 39: width-3 invariant law

The next bounded step asked whether the six-orbit atlas still needs to be read
as an atlas, or whether a smaller invariant law already predicts the orbit
cost.

Two refinements matter here.

First:

- the full degree sequence is already an exact singleton invariant on this
  width-`3` frontier

But second:

- among the searched scalar invariants, no singleton one is exact
- the simplest exact scalar law found is the pair:
  - `(edge_count, max_degree)`

Exact cost rule:

- `(3,3) -> 3`
- `(3,2) -> 4`
- `(2,2) -> 5`
- otherwise `-> 6`

So the width-`3` `4`-role frontier now has three levels:

- exact cost histogram
- exact six-orbit geometry atlas
- exact two-scalar invariant law

That is a real compression ladder, not just a sequence of unrelated examples.

### Level 40: width-4 support-profile law

The next bounded step moved from width `3` to width `4`, but kept the same
abstract family:

- labeled `4`-role support tables
- one distinct realized support signature per role

At width `4`, the first question was whether the new cost histogram hides a
small exact support-profile law.

For each role, define its minimal unique-support size as the fewest support bits
needed to distinguish that role from the other realized roles.

Then sort the four per-role sizes into one profile.

On the full width-`4` bounded family:

- only `6` sorted profiles occur:
  - `(1,1,1,1)`
  - `(1,1,1,2)`
  - `(1,1,1,3)`
  - `(1,1,2,2)`
  - `(1,2,2,2)`
  - `(2,2,2,2)`
- exact counts:
  - `(1,1,1,1)`: `384`
  - `(1,1,1,2)`: `4608`
  - `(1,1,1,3)`: `3840`
  - `(1,1,2,2)`: `18432`
  - `(1,2,2,2)`: `13056`
  - `(2,2,2,2)`: `3360`

And the exact minimal compiler cost is determined by the profile:

- cost `3` for:
  - `(1,1,1,1)`
  - `(1,1,1,2)`
  - `(1,1,1,3)`
- cost `4` for `(1,1,2,2)`
- cost `5` for `(1,2,2,2)`
- cost `6` for `(2,2,2,2)`

Equivalently:

- exact minimal cost = the sum of the three smallest profile entries

So the width-`4` frontier is not only:

- a wider cost table

It already has:

- a small exact support-profile law

That is the cleanest step upward from the width-`3` invariant law.

### Level 41: width-4 support-count law

The next bounded step asked whether the six-profile width-`4` law still needed
all six explicit profiles, or whether exact cost already collapsed to a smaller
scalar.

Within the searched profile-derived statistic library, the smallest surviving
exact scalar was:

- `count_private_roles`

meaning:

- the number of roles whose minimal unique-support size is `1`

Exact cost law:

- `4 -> 3`
- `3 -> 3`
- `2 -> 4`
- `1 -> 5`
- `0 -> 6`

So the earlier profile law collapses again.

The width-`4` frontier is not only:

- a six-profile law

It is also:

- a one-scalar private-role-count law for exact cost

### Level 42: width-4 profile-pair law

The next bounded step kept the same six-profile frontier, but changed the
target.

Instead of asking for exact cost, it asked for the smallest searched basis that
reconstructs the full profile itself.

No searched singleton scalar was exact.

But the pair:

- `count_private_roles`
- `max_support_size`

reconstructs the entire six-profile law exactly.

So the width-`4` line now has a clean split:

- exact cost needs only one scalar:
  - `count_private_roles`
- exact full profile needs two scalars:
  - `count_private_roles`
  - `max_support_size`

That is a stronger compression ladder than the raw profile statement alone.

### Level 43: width-4 orbit transfer

The next bounded step asked whether the new width-`4` support-count laws were
only artifacts of the labeled-table presentation.

So it changed the presentation, but not the family:

- unlabeled `4`-subsets of the `4`-cube
- quotiented by cube automorphisms
- exhaustive orbit count:
  - `19`

Then it rechecked the two width-`4` support-count laws.

They survived unchanged.

Exact cost on the orbit family is still determined by:

- `count_private_roles`

And exact full support profile on the orbit family is still reconstructed by:

- `count_private_roles`
- `max_support_size`

So the width-`4` line now has a genuine transfer result.

The support-count laws are not only:

- compressed descriptions of one labeled frontier

They are also:

- stable exact laws across two bounded presentations of the same family

### Level 44: width-4 orbit mixed basis

The next bounded step finally hit the first genuine width-`4` geometric
obstruction.

The support-count laws from Levels 41 to 43 still control:

- exact cost
- exact full support profile

But they do not determine the full orbit class.

Within the searched mixed basis library:

- no singleton basis is exact
- the first exact pairs are:
  - `count_private_roles` plus `distance_multiset`
  - `count_size2_roles` plus `distance_multiset`

So the first width-`4` obstruction is small but real:

- support counts are not enough for orbit reconstruction
- one geometric multiset completes the job exactly

### Level 45: width-4 scalarized mixed law

The next bounded step asked whether that mixed basis still needed the full
distance multiset, or whether the orbit class already collapsed to a small
scalar support-plus-geometry law.

Inside the searched scalar feature library:

- no singleton scalar is exact
- no scalar pair is exact
- exact scalar triples do exist

One preferred exact triple is:

- `count_private_roles`
- `max_degree`
- `diameter`

Equivalent exact triples also survive with:

- `count_size2_roles` in place of `count_private_roles`
- or `isolated_count` in place of `max_degree`

So the first genuine width-`4` orbit obstruction still compresses to a tiny
three-scalar law.

### Level 46: width-4 broad-scalar minimality

The next bounded step stress-tested that three-scalar law against a much wider
scalar support-plus-geometry library.

The widened library included:

- support-count scalars
- support-sum scalars
- graph-degree scalars
- component scalars
- distance scalars
- per-distance count scalars
- simple parity and quadratic-degree summary scalars

Total searched scalar features:

- `21`

The main result stayed fixed:

- no searched singleton scalar is exact
- no searched scalar pair is exact
- exact scalar triples do exist

So that earlier three-scalar object was not an artifact of a narrow feature
menu.

Within this broader bounded search, the first exact scalar basis still has size
`3`.

### Level 47: width-4 mixed-basis rigidity

The next bounded step turned back to the non-scalar side and asked whether the
mixed basis from Level 44 was one choice among many.

Inside the widened tuple-aware mixed library:

- support-count coordinates
- full support profile
- degree sequence
- component sizes
- distance multiset

the only nontrivial exact pair bases were:

- `count_private_roles` plus `distance_multiset`
- `count_size2_roles` plus `distance_multiset`

So the first width-`4` obstruction is not only small.

It is also rigid in the searched mixed basis space.

## Part XI: where verifier-compilers fit among other loop families

This part is comparative.

It is not another long proof ladder for its own sake.
The teaching question is:

> when is verifier compilation the right object, and when should the search move
> to a richer loop family?

The short answer is:

- verifier-compilers are one strong child of a larger witness-language program
- some frontiers move only when the local witness contract changes
- other frontiers move only when the whole object of search changes

That is why this part matters.

Not unconditionally.

It is the strongest loop family found so far in this repo's bounded experiments.

But that is a local result, not a universal theorem.

The right way to say it is:

> verifier-compiler loops are a strong meta-loop above CEGIS when verifier behavior is compressible enough to yield a reusable symbolic artifact.

There may be stronger loops in other problem families.

The main candidates are:

### 1. Certificate-lifting loops

If:

$$
Good(x) \iff \exists c\; Cert(c,x),
$$

then the alternation:

$$
\exists x\; \forall y\; Spec(x,y)
$$

can collapse into:

$$
\exists x\; \exists c\; Cert(c,x).
$$

That would be stronger than verifier compilation.

It would change the quantifier structure of the problem itself.

### 2. Abstraction-synthesis loops

If one can synthesize a quotient on the obligation side before verification, the universal burden itself may shrink.

### 3. Explanatory ladder loops

Instead of forcing one global explanation language, a ladder loop can assign:

- scalar quotients to easy regions,
- ordered bases to harder regions,
- richer certificate or strategy languages only where needed.

The regional refill result above is the first bounded evidence that this idea is real.

### 4. Dual-language discovery loops

Instead of insisting that every exact explanation must be positive, a dual-language loop can search for:

- positive witness languages on one side
- negative or refuter languages on the other

The residual-default label result above is the first bounded evidence that this idea can reduce exact explanation cost, even before explicit negative refuter objects are introduced.

### 5. Primitive-invention loops

Instead of choosing only from a fixed explanation language, a primitive-invention loop can promote new exact concepts when they:

- are verifier-valid,
- reduce explanation cost,
- and recur enough to be worth keeping

The primitive-invention results above are bounded evidence that this can materially change the exact language frontier.

The hard refill concept-market result adds an important refinement:

- some invented concepts help as shortcuts inside a richer existing language,
- but the same concepts may fail if forced to replace the old basis outright.

The stacked hard-frontier result adds one more refinement:

- concept invention can compound,
- but the current bounded evidence still favors shortcut layers over basis replacement.

The anchored third-shortcut boundary adds another refinement:

- local shortcut search can saturate on the main online metrics even while minor internal compression remains.

The hard-frontier witness-language result adds one more refinement:

- once local shortcut search saturates, exact positive-cover plus residual-default witness languages can still reveal structure that the shortcut line no longer improves.

The global witness-schema result adds another:

- once exact local witness languages exist, they can be compressed into a smaller reusable global schema library.

The score-abstraction result adds one more:

- some neighboring score regions can merge exactly, so the witness-language line now compresses both across schemas and across score blocks.

The unconstrained score-partition result adds a boundary:

- the current score abstraction is robust even after the contiguity restriction is removed.

### 6. Minimal witness-language discovery

There is a stronger umbrella above verifier compilation:

> search for the smallest exact language in which local witnessing is allowed.

That language does not need to be a decision-list language.

It may instead be:

- an all-positive witness language,
- a residual-default witness language,
- an ordered classifier language,
- or some richer certificate or policy language.

The bounded phase-diagram level gives the first explicit evidence for this
umbrella on one fixed repaired verifier frontier.

On the same `10` exact quotient states, three different optima survive once the
local witness contract is fixed:

- smallest all-positive unordered language:
  - invented positive-cover family
  - cost `4`
- smallest unordered residual-default language:
  - mixed atom-cover family
  - cost `4`
- smallest ordered exact classifier:
  - decision-list compiler
  - guard count `4`

So the answer to "what is the best exact language?" is not absolute even on
this bounded frontier.

It depends on what counts as a valid local witness.

That is the sharpest current reason to treat verifier-compilers as one important
child of a larger program rather than as the final umbrella.

The harder refill frontier then sharpens the same point.

There the exact families no longer tie.

Instead they form a strict bounded ladder:

- score-local residual-default witnesses:
  - cost `27`
- merged-region residual-default witnesses:
  - cost `22`
- shared global witness-schema language:
  - size `19`

Local all-positive witnesses already fail on the hardest score blocks:

- `9`
- `10`

So on the harder frontier, widening the local witness contract does not merely
change which exact family is preferred.

It strictly lowers the exact description size.

The next bounded comparison checked whether exact decomposition should replace
the label-level witness language on that same hard partition.

It did not.

Exact bit-fiber decomposition survives, but it is strictly worse:

- bit-fiber total cost:
  - `24`
- label-level total cost:
  - `22`
- bit-fiber shared schema count:
  - `21`
- label-level shared schema count:
  - `19`

So on the current hard frontier, decomposition is a real exact family, but not
the smallest exact language family found in this search.

The next comparison checked a stricter certificate family on the same hard
partition:

- exact all-positive certificates
- with no residual default

That family fails even earlier.

In the searched `1..4` literal conjunction grammar, all-positive certificates
already fail on region `(10,11)`.

Even on the four regions where they do survive, they are still larger:

- feasible-region certificate cost:
  - `23`
- feasible-region shared schema count:
  - `21`

So on this hard frontier, residual-default witness languages are not only a
compression trick.

They are necessary in the searched certificate grammar.

The next bounded comparison asked how much local residual structure is actually
needed on that same hard partition.

Strict all-positive certification is impossible, but exactness already returns
once one region is allowed residual-default witnessing.

That first residual region is forced:

- `(10,11)`

Then the best exact cost falls in a strict residual-budget ladder:

- `1` residual region:
  - cost `28`
  - shared schemas `26`
- `2` residual regions:
  - cost `26`
  - shared schemas `24`
- `3` residual regions:
  - cost `24`
  - shared schemas `22`
- `4` residual regions:
  - cost `23`
  - shared schemas `21`
- `5` residual regions:
  - cost `22`
  - shared schemas `20`

So on this hard frontier, residual structure is locally budgetable.

It is not an all-or-nothing switch.

The next bounded comparison kept the same hard partition and the same residual
budget, but changed the objective from local witness count to global
schema-sharing cost.

That sharpened every feasible rung by one more schema:

- `1` residual region:
  - shared schemas `25`
  - total cost `28`
- `2` residual regions:
  - shared schemas `23`
  - total cost `26`
- `3` residual regions:
  - shared schemas `21`
  - total cost `24`
- `4` residual regions:
  - shared schemas `20`
  - total cost `23`
- `5` residual regions:
  - shared schemas `19`
  - total cost `22`

So the hard frontier has a stronger law than the earlier schema-sharing step
alone suggested:

- the residual-budget ladder survives under global schema sharing
- every feasible rung improves by exactly one schema
- and the full-budget endpoint lands on the earlier global optimum `19`

The next bounded comparison removed one more hidden assumption:

- that the old score partition should stay fixed while residual budget is
  varied

That assumption fails on the same hard frontier.

Once score partition and residual structure are searched jointly, the best
shared-schema ladder becomes:

- budget `1`:
  - shared schemas `24`
  - total cost `28`
  - partition:
    - `(7,12)`
    - `(8)`
    - `(9,10)`
    - `(11)`
- budget `2`:
  - shared schemas `22`
  - total cost `26`
  - same partition
- budget `3`:
  - shared schemas `20`
  - total cost `24`
  - partition:
    - `(7,12)`
    - `(8)`
    - `(9)`
    - `(10,11)`
- budget `4`:
  - shared schemas `19`
  - total cost `23`
  - same four-region partition
- budget `5`:
  - shared schemas `19`
  - total cost `22`
  - original five-region partition returns

So the sharper hard-frontier law is now:

- fixed-partition residual budgeting was not globally optimal
- low residual budgets want merged score regions
- the old score partition only returns at full residual budget

The next bounded comparison asked a sharper question.

Was the remaining hard-frontier ceiling really a logic wall, or only a grammar
wall?

Instead of rerunning the full joint search in a widened grammar, the check
focused on the exact union of score regions that actually appear in the
earlier joint residual-budget search:

- `(7,12)`
- `(8)`
- `(9,10)`
- `(11)`
- `(9)`
- `(10,11)`
- `(7)`
- `(12)`

On that exact critical-region set, widening strict all-positive certificates
from the `1..4` literal conjunction grammar to the `1..5` literal conjunction
grammar changes only one region:

- `(10,11)`:
  - `1..4` literals:
    - impossible
  - `1..5` literals:
    - exact
    - total cost `6`

Every other critical region keeps the same minimal exact cost.

So the current hard-frontier ceiling is not a uniform failure of all-positive
certification.

It is partly a grammar wall, localized at `(10,11)`.

That is still a bounded critical-region result, not yet a full rerun of the
joint residual-budget search in the widened grammar.

The next bounded comparison did that full rerun.

Residual-default witness regions stayed in the `1..4` literal grammar, while
strict certificate regions widened to the `1..5` literal grammar.

This time the localized critical-region change propagated to the full joint frontier, but
only at low residual budgets.

The widened exact ladder became:

- budget `0`:
  - shared schemas `25`
  - total cost `29`
  - partition:
    - `(7,12)`
    - `(8)`
    - `(9)`
    - `(10,11)`
- budget `1`:
  - shared schemas `23`
  - total cost `27`
  - same partition
- budget `2`:
  - shared schemas `21`
  - total cost `25`
  - same partition
- budget `3`:
  - shared schemas `20`
  - total cost `24`
  - same partition
- budget `4`:
  - shared schemas `19`
  - total cost `23`
  - same partition
- budget `5`:
  - shared schemas `19`
  - total cost `22`
  - original five-region all-residual partition returns

Compared with the earlier joint residual-budget search:

- a zero-residual exact rung now exists
- budgets `1` and `2` each improve by:
  - one schema
  - one total-cost unit
- budgets `3`, `4`, and `5` do not move

So the sharpest hard-frontier law is now:

- the old ceiling was partly grammatical
- widening certificates changes the actual joint frontier
- but only in the low-residual regime
- once residual budget is large enough, the old frontier had already
  found the right object

The next bounded comparison tested whether the unchanged high-residual end was
still blocked only by literal width.

Strict certificates widened again, from the `1..5` literal grammar to the
`1..6` literal grammar, while residual-default witness regions stayed in the
`1..4` grammar.

This time nothing moved at budgets `3`, `4`, or `5`.

The exact high-residual ladder stayed:

- budget `3`:
  - shared schemas `20`
  - total cost `24`
- budget `4`:
  - shared schemas `19`
  - total cost `23`
- budget `5`:
  - shared schemas `19`
  - total cost `22`

So the current hard-frontier law is sharper still:

- the low-residual regime was grammar-blocked
- the high-residual regime is locally saturated along this literal-width axis
- the next honest move is no longer “one more literal”
- it is either:
  - transfer to a second hard frontier
  - or a genuinely richer certificate language

One exact slice still remained after the later certificate-widening step: the
low-residual end under the same
`1..6` certificate widening.

That slice also did not move.

The exact low-residual ladder stayed:

- budget `0`:
  - shared schemas `25`
  - total cost `29`
- budget `1`:
  - shared schemas `23`
  - total cost `27`
- budget `2`:
  - shared schemas `21`
  - total cost `25`

So the full hard partition-aware residual-budget ladder is now closed on this
literal-width axis:

- widening strict certificates from `1..5` to `1..6` literals does not move
  any residual budget
- the low-residual gains in the earlier widened-certificate step were real
- but they were already fully captured at width `5`

That is the honest stopping point for this grammar family on this frontier.

The next honest move after that closure was transfer.

The same partition-aware residual-budget search was moved to the earlier toy
lab-followup MPRD frontier, using the mixed score blocks `1,2,3,4` and the
same `1..4` signed-conjunction witness grammar over holdout error bits.

This time the loop survived, but with a different exact geometry.

The schema-first ladder became:

- budget `0`:
  - shared schemas `5`
  - total cost `5`
  - one merged strict-certificate region
- budget `1`:
  - shared schemas `4`
  - total cost `4`
  - one merged residual-default region over all mixed scores
- budget `2`:
  - shared schemas `4`
  - total cost `5`
- budget `3`:
  - shared schemas `4`
  - total cost `7`
- budget `4`:
  - shared schemas `6`
  - total cost `10`

So the transfer law is not “the same ladder in a second domain”.

It is sharper:

- residual structure transfers
- but here it transfers as one merged exception layer
- after budget `1`, extra exact residual regions do not improve schema count
  and they worsen total cost

That contrast matters.

The refill frontier preferred progressively larger residual budgets.

The lab-followup frontier prefers a single merged residual region and then
stops.

The next bounded check asked whether that merged transfer object was only a
`1..4` strict-certificate artifact.

Strict certificates were widened to the full `1..5` literal grammar, while
residual-default witnesses stayed in the `1..4` grammar.

Nothing moved.

The exact ladder stayed:

- budget `0`:
  - shared schemas `5`
  - total cost `5`
- budget `1`:
  - shared schemas `4`
  - total cost `4`
- budget `2`:
  - shared schemas `4`
  - total cost `5`
- budget `3`:
  - shared schemas `4`
  - total cost `7`
- budget `4`:
  - shared schemas `6`
  - total cost `10`

So the lab-followup transfer object is already locally saturated on this
literal-width axis as well.

That makes the contrast with refill sharper:

- refill had a grammar-sensitive low-residual regime
- lab-followup does not
- the merged residual region in lab-followup looks structural, not merely
  grammatical

The next bounded step was explanatory rather than grammatical.

On the full unsafe block of the lab-followup frontier, scores `0,1,2,3,4`,
there is already an exact score-free earliest-error residual law:

- default:
  - `h1`
- certify `h2` by:
  - `not e1 and e2`
- certify `h3` by:
  - `not e1 and not e2 and e3`
- certify `h4` by:
  - `not e1 and not e2 and not e3 and e4`
- certify `h5` by:
  - `not e1 and not e2 and not e3 and not e4`

This law is exact on all `163` unsafe behaviors.

Its residual-default cost is `4`.

The best exact all-positive presentation on the same unsafe block costs `5`.

So the merged residual region is no longer only an empirical optimum.

It is explained by a direct score-free earliest-error language on the unsafe
block itself.

That made the next comparison sharper:

> does the refill frontier admit anything analogous, once the same kind of
> score-free merged-region search is run on its nontrivial score set?

In the later hard-frontier witness grammar, the answer is no for the whole
nontrivial union.

The exact refill merged-subset search gives:

- residual-default feasible merged subunions:
  - `13`
- size profile:
  - `1 -> 6`
  - `2 -> 6`
  - `3 -> 1`
- all-positive feasible merged subunions:
  - `10`
- all-positive size profile:
  - `1 -> 6`
  - `2 -> 4`

So:

- no refill merged subunion of size `4`, `5`, or `6` is exact
- the whole nontrivial union fails
- every exact size-`3` or larger object needs residual-default witnessing

There is one unique maximal exact merged refill subunion:

- scores:
  - `(9,10,12)`
- row count:
  - `17`
- label count:
  - `10`
- exact all-positive presentation:
  - impossible
- best exact residual-default cost:
  - `10`

So the lab-followup explanatory law does not transfer as a whole
score-free law.

On the refill side, the same search finds only sparse exact merged islands, not
one unified explanatory block.

That makes the next meta-question unavoidable:

> which kinds of interventions actually moved the mature frontier, and which
> kinds mostly exposed ceilings?

The bounded later meta-scan answers that cleanly.

The biggest exact gains came from adding new structural search axes:

- residual-budget search,
- global schema sharing,
- joint partition search,
- transfer as a first-class exact object,
- score-free semantic explanation search.

By contrast, grammar widening was much weaker:

- one local critical-region gain,
- one partial global low-residual gain,
- then saturation.

So the later line teaches a sharper rule:

> the frontier moved when the object of search changed.

That points to the next honest research frontier:

- temporal obligation geometry on Tau specs,

not another literal-width sweep on the current static witness languages.

### 7. Meta-loop synthesis

One can try to synthesize the loop policy itself:

- proposer selection,
- verifier scheduling,
- repair grammar,
- ranking policy.

Those may become stronger in some domains.

So the honest answer is:

- best bounded loop family found here, yes
- obviously best in all domains, no

## Part XII: software repair languages

The main line did not stop with static witness languages.

The next bounded question was whether the same progression would survive on a
small software-engineering corpus, where the goal is not only to classify
labels but to recover repairs.

<figure class="fp-figure">
  <p class="fp-figure-title">Software repair compression ladder</p>
  {% include diagrams/software-repair-pipeline.svg %}
  <figcaption class="fp-figure-caption">
    The software branch replays the same meta-pattern: each phase changes the
    object of search. Monolithic patch search gives way to fiber decomposition,
    certificate-carrying verification, and finally a compiled repair language
    with shared templates and motif-routed direct construction.
  </figcaption>
</figure>

The bounded corpus used two tiny patch families over three edit sites:

- `guard`
- `bounds`
- `transform`

The two families were:

- `separable_patch_family`
- `overlap_patch_family`

The key difference was simple:

- in the separable family, the three unit-test fibers are genuinely independent
- in the overlap family, the `bounds` fiber overlaps with `transform`

That made the software branch a good test for higher-leverage loop families.

### Level 48: dependency-aware repair fibers

The first bounded comparison asked whether failure-fiber decomposition already
beats monolithic patch search, and what the first exact correction is once
those fibers overlap.

The three compared loop styles were:

1. monolithic patch search
2. naive independent fiber repair
3. dependency-aware fiber repair

The strongest exact result was:

- separable family:
  - monolithic average cost:
    - `39.0`
  - dependency-aware fiber cost:
    - `9.0`
  - exact on:
    - `27 / 27`
- overlap family:
  - monolithic average cost:
    - `35.851851851851855`
  - naive fiber repair:
    - exact on only `16 / 27`
  - dependency-aware fiber repair:
    - `9.0`
    - exact on:
      - `27 / 27`

The exact correction was:

- solve `transform` first
- then solve `guard` and `bounds` conditioned on it

So the first software survivor was not “more search”.

It was:

- a dependency graph over repair fibers

### Level 49: certificate-carrying repair

Once the fiber graph stabilized, the next bounded question was whether
dependency-aware search could be replaced by direct local verification if the
patch carried a small witness.

The witness language was the three local observation tokens:

- `guard`
- `bounds`
- `transform`

The strongest exact result was:

- no singleton certificate basis is exact
- no pair certificate basis is exact
- the unique minimal exact basis on both patch families is:
  - `guard`
  - `bounds`
  - `transform`
- certificate verification cost:
  - `3`

So the software ladder sharpened immediately:

- monolithic search:
  - about `36` to `39`
- dependency-aware fiber search:
  - `9`
- certificate-carrying verification:
  - `3`

This was the software version of the same deeper move seen earlier:

- stop searching only for the object
- search for the smallest exact language in which the object becomes locally
  witnessable

### Level 50: witness-to-patch decoders

The next bounded step asked whether the carried witness from Level 49 compiles
back into the patch through a tiny exact decoder graph.

The witness observations were:

- `guard_obs`
- `bounds_obs`
- `transform_obs`

The strongest exact result was:

- separable family:
  - minimal exact decoder cost:
    - `3`
  - decoder:
    - `guard <- guard_obs`
    - `bounds <- bounds_obs`
    - `transform <- transform_obs`
- overlap family:
  - minimal exact decoder cost:
    - `4`
  - decoder:
    - `guard <- guard_obs`
    - `bounds <- bounds_obs, transform_obs`
    - `transform <- transform_obs`

So overlap did not destroy local decoding.

It inserted exactly one extra dependency edge:

- `transform_obs -> bounds`

This is stronger than Level 49, because the witness no longer only verifies the
repair. It compiles back into the repair.

### Level 51: shared repair-language templates

The next bounded step moved one level higher again.

Instead of storing the two exact decoder graphs separately, it asked whether
they compress into one shared repair-language template plus small family
patches.

The strongest exact result was unique in both additive and signed-edit models:

- shared base:
  - `guard_obs -> guard`
  - `bounds_obs -> bounds`
  - `transform_obs -> transform`
- separable delta:
  - none
- overlap delta:
  - `transform_obs -> bounds`
- total template cost:
  - `4`

So the two software families do not need different grammars.

They need:

- one shared local decoder language
- plus one sparse residual patch

That is already a much stronger object than a family-specific decoder.

### Level 52: repair-program macros

The next bounded step compressed that shared template one level further.

The searched macro grammar was still natural and finite:

- `6` permutation matchings
- `3` fanout macros
- `3` fanin macros
- `9` single-edge patch macros

The strongest exact result was:

- separable target:
  - minimal exact macro cost:
    - `1`
  - unique program:
    - `MATCH_ID`
- overlap target:
  - minimal exact macro cost:
    - `2`
  - unique program:
    - `MATCH_ID`
    - `SINGLE[transform_obs->bounds]`

The best shared additive macro template was also unique:

- shared base:
  - `MATCH_ID`
- overlap patch:
  - `SINGLE[transform_obs->bounds]`
- total macro cost:
  - `2`

No cost-`1` shared macro template exists.

So the software branch now has a clean compression ladder:

- Level 51 raw edge-template cost:
  - `4`
- Level 52 macro-template cost:
  - `2`

That is the first exact patch-program macro language in the software branch.

Its lesson is the same one that kept moving the frontier elsewhere:

- discover the reusable exact language
- then patch only the residual difference

### Level 53: repair-schema transfer

The next bounded step asked whether the Level 52 macro result was only a
two-family coincidence.

To test that honestly, the search moved to a small transfer atlas:

- the separable family itself
- plus every one-overlap family obtained by adding exactly one off-diagonal
  decoder edge to the local diagonal base

That gives:

- `7` exact decoder targets

The search then moved one level higher again.

Instead of choosing concrete macro instances directly, it searched over schema
families:

- `MATCH`
- `FANOUT`
- `FANIN`
- `SINGLE`

The objective was MDL-like:

- exactness on the whole `7`-family atlas
- then minimize:
  - schema-basis size
  - plus total program-instance count across the atlas

The strongest exact result was:

- singleton schema bases:
  - `MATCH`
    - not exact
  - `FANOUT`
    - not exact
  - `FANIN`
    - not exact
  - `SINGLE`
    - exact
    - description length `28`
- unique exact optimum:
  - basis:
    - `MATCH`
    - `SINGLE`
  - basis size:
    - `2`
  - total instance cost:
    - `13`
  - description length:
    - `15`

The program shape under that exact optimum is uniform:

- separable family:
  - `MATCH_ID`
- every one-overlap family:
  - `MATCH_ID`
  - plus one `SINGLE[off_diagonal_edge]`

So the Level 52 law really does transfer.

The software branch now has a schema-basis result above the concrete macro
instances:

- one reusable local-match schema
- one sparse cross-edge patch schema

That is stronger than a two-family macro observation.

It is the first exact transfer law in the software branch.

### Level 54: first transfer obstruction

The next bounded step asked the first honest obstruction question:

> if the atlas is widened from one-overlap families to all families with up to
> two off-diagonal decoder edges, when does the Level 53 law stop being
> MDL-optimal?

The widened atlas contains:

- `1` separable family
- `6` one-overlap families
- `15` two-overlap families

The comparison kept the exact Level 53 basis explicit:

- `MATCH`
- `SINGLE`

That basis remains exact on the widened atlas.

But it is no longer MDL-optimal.

Its exact metrics are:

- description length:
  - `57`
- total instance cost:
  - `55`

The new exact optimum is:

- `MATCH`
- `FANIN`
- `FANOUT`
- `SINGLE`

with:

- description length:
  - `53`
- total instance cost:
  - `49`

So the first obstruction is not loss of exactness.

It is loss of compression.

The cost histograms make the change visible.

Under `MATCH + SINGLE`:

- cost `1`:
  - `1`
- cost `2`:
  - `9`
- cost `3`:
  - `12`

Under the exact optimum:

- cost `1`:
  - `1`
- cost `2`:
  - `15`
- cost `3`:
  - `6`

Some two-overlap families were already cheap under `MATCH + SINGLE`, because an
alternative matching can absorb both extra edges at once.

The actual gain comes from structured double overlaps:

- row-style overlaps compress via `FANOUT`
- column-style overlaps compress via `FANIN`

Examples:

- `plus[bounds_obs->guard,bounds_obs->transform]`
  - `FANOUT[bounds_obs]`
  - `MATCH_ID`
- `plus[guard_obs->bounds,transform_obs->bounds]`
  - `FANIN[bounds]`
  - `MATCH_ID`

So the first software transfer obstruction is semantic and geometric.

The Level 53 law survives as correctness, but not as optimal description.

### Level 55: semantic motif law

The next bounded step asked whether the Level 54 obstruction could be explained
semantically rather than by one more atlas statistic.

The domain was the `15` two-overlap families from Level 54.

The target label was simple:

- optimal exact program cost under the Level 54 best basis
  - either `2`
  - or `3`

The searched semantic motif features were:

- `same_obs`
  - the two extra edges share an observation row
- `same_field`
  - the two extra edges share a field column
- `swap_pair`
  - the two extra edges form a reciprocal two-row swap against the diagonal

The strongest exact result was:

- no singleton semantic basis is exact
- no pair semantic basis is exact
- the unique minimal exact basis is:
  - `same_obs`
  - `same_field`
  - `swap_pair`

So the first exact semantic basis size is:

- `3`

Its rule is exact:

- `same_obs=1, same_field=0, swap_pair=0`
  - cost `2`
- `same_obs=0, same_field=1, swap_pair=0`
  - cost `2`
- `same_obs=0, same_field=0, swap_pair=1`
  - cost `2`
- `same_obs=0, same_field=0, swap_pair=0`
  - cost `3`

So the Level 54 jump now has a small semantic explanation.

The richer basis from Level 54 is worth paying for exactly on three motif
types:

- row bundle
- column bundle
- swap pair

Everything else stays at cost `3`.

That is the first exact semantic law above the software transfer obstruction.

### Level 56: semantic schema language

The next bounded step compiled the Level 55 motif law itself into a smallest
exact semantic schema language on the whole atlas up to two overlaps.

The searched semantic schema grammar was:

- `DIAGONAL`
  - the local identity decoder
- `SINGLE`
  - one off-diagonal patch edge
- `BUNDLE2`
  - either a row bundle or a column bundle
- `SWAP2`
  - a reciprocal two-row swap pair

The strongest exact result was unique:

- basis:
  - `DIAGONAL`
  - `SINGLE`
  - `BUNDLE2`
  - `SWAP2`
- basis size:
  - `4`
- total instance cost:
  - `49`
- description length:
  - `53`

So the semantic language matches the best exact atlas cost from Level 54.

But it does so at the right abstraction layer:

- `FANIN` and `FANOUT` collapse into:
  - `BUNDLE2`
- swap-specific nonidentity matchings collapse into:
  - `SWAP2`

Example programs:

- separable family:
  - `DIAGONAL[MATCH_ID]`
- one-overlap family:
  - `DIAGONAL[MATCH_ID]`
  - plus one `SINGLE[...]`
- row-bundle two-overlap:
  - `DIAGONAL[MATCH_ID]`
  - `ROW_BUNDLE[...]`
- column-bundle two-overlap:
  - `DIAGONAL[MATCH_ID]`
  - `COL_BUNDLE[...]`
- swap-pair two-overlap:
  - `DIAGONAL[MATCH_ID]`
  - `SWAP_PAIR[...]`

The local boundaries are also clear:

- drop `SINGLE`
  - no exact basis
- drop `BUNDLE2`
  - description length rises to:
    - `58`
- drop `SWAP2`
  - description length rises to:
    - `55`
- drop `DIAGONAL`
  - exactness survives,
  - but description length jumps to:
    - `96`

So the software branch now has a full semantic compile step:

- not only a syntactic schema basis
- but a smallest exact semantic schema language above the obstruction

At this point in the software branch, that is the strongest object so far.

### Level 57: motif-routed repair compiler

The next bounded step asked the real loop question:

> does the Level 56 semantic language collapse to a tiny exact router that
> dispatches families into local repair schemas?

The target labels were the four semantic schema shapes from Level 56:

- `DIAGONAL`
- `DIAGONAL+SINGLE`
- `BUNDLE2+DIAGONAL`
- `DIAGONAL+SWAP_PAIR`

The searched semantic predicates were:

- `extra0`
- `extra1`
- `same_obs`
- `same_field`
- `swap_pair`
- `bundle_motif`

where:

- `bundle_motif := same_obs or same_field`

The strongest exact result was:

- no `1`-branch router is exact
- no `2`-branch router is exact
- the first exact router has:
  - `3` branches
- number of minimal routers:
  - `6`

One exact minimal router is:

- if `extra0`:
  - `DIAGONAL`
- else if `swap_pair`:
  - `DIAGONAL+SWAP_PAIR`
- else if `bundle_motif`:
  - `BUNDLE2+DIAGONAL`
- else:
  - `DIAGONAL+SINGLE`

So the software branch now has a true routed compiler:

- inspect motif
- route to a local semantic schema
- instantiate the repair program

That is the first point in this branch where the object is no longer only:

- a certificate,
- a decoder,
- a grammar,
- or a schema basis

It is a small exact repair policy.

### Level 58: typed motif-kind direct repair compiler

The next bounded step closed the remaining gap in the software branch:

> can the full minimal repair program be constructed directly from the raw
> extra-edge set, instead of routing only to coarse schema heads?

The searched typed coordinates were:

- `extra_count`
- `same_obs`
- `same_field`
- `swap_pair`
- `bundle_motif`
- `motif_kind`

Here `motif_kind` is the typed world-state summary over the raw extra-edge set:

- `none`
- `single`
- `bundle`
- `swap`
- `other`

The strongest exact result was:

- the full `22`-family atlas up to two overlaps admits an exact direct
  repair-program compiler from raw extra-edge sets
- among the searched typed coordinates:
  - `motif_kind` is the unique exact singleton basis
  - no other singleton coordinate is exact

Exact singleton law:

- `none -> DIAGONAL`
- `single -> DIAGONAL+SINGLE`
- `bundle -> DIAGONAL+BUNDLE2`
- `swap -> DIAGONAL+SWAP2`
- `other -> DIAGONAL+DOUBLE_SINGLE`

The direct constructor is:

- `none`:
  - `DIAGONAL[MATCH_ID]`
- `single`:
  - `DIAGONAL[MATCH_ID] + SINGLE[edge]`
- `bundle`:
  - `DIAGONAL[MATCH_ID] + BUNDLE2[shared obs or shared field]`
- `swap`:
  - `DIAGONAL[MATCH_ID] + SWAP_PAIR[obs pair]`
- `other`:
  - `DIAGONAL[MATCH_ID] + SINGLE[edge_1] + SINGLE[edge_2]`

Exact metrics:

- family count:
  - `22`
- exact match count:
  - `22 / 22`
- optimal total instance cost:
  - `49`
- constructed total instance cost:
  - `49`

This is the first direct compiler in the software branch.

The branch now has a much sharper object:

- inspect the overlap motif
- classify it into one typed semantic state
- instantiate the minimal repair program directly

That is stronger than the earlier routed schema compiler, because it no longer
stops at a schema head or oracle-backed label. It constructs the full minimal
program from raw bounded inputs.

### Level 59: support-signature direct repair compiler

The next bounded transfer question was the natural one:

> does the Level 58 singleton motif law survive on the richer atlas with up to
> three overlaps?

The answer was:

- not unchanged
- but the direct-compiler story survives

The searched typed support-signature coordinates were:

- `extra_count`
- `obs_profile`
- `field_profile`
- `max_obs`
- `max_field`
- `swap_pairs`
- `same_obs`
- `same_field`

The strongest exact result was:

- no singleton coordinate is exact in the searched library
- no pair basis is exact
- the first exact basis has size:
  - `3`
- exact basis count:
  - `5`

Preferred symmetric basis:

- `obs_profile`
- `field_profile`
- `swap_pairs`

Its exact rule is:

- `(0,0,0), (0,0,0), 0 -> DIAGONAL`
- `(1,0,0), (1,0,0), 0 -> DIAGONAL+SINGLE`
- `(1,1,0), (1,1,0), 0 -> DIAGONAL+DOUBLE_SINGLE`
- `(1,1,0), (1,1,0), 1 -> DIAGONAL+SWAP2`
- `(2,0,0), (1,1,0), 0` or `(1,1,0), (2,0,0), 0 -> DIAGONAL+BUNDLE2`
- `(1,1,1), (1,1,1), 0 -> DIAGONAL+TRIPLE_SINGLE`
- `(2,1,0), (2,1,0), 0 -> DIAGONAL+BUNDLE2+SINGLE`
- `(2,1,0), (1,1,1), 1` or `(1,1,1), (2,1,0), 1 -> DIAGONAL+SWAP2+SINGLE`

Exact metrics:

- family count:
  - `42`
- exact match count:
  - `42 / 42`
- constructed total instance cost:
  - `111`
- optimal total instance cost:
  - `111`

So the software branch now has a transfer ladder:

- up to two overlaps:
  - exact singleton direct compiler
- up to three overlaps:
  - exact support-signature direct compiler

That is a real deepening of the loop family.

The direct compiler survives transfer, but the state basis grows with the first
higher-order overlap motifs.

### Level 60: canonical support-signature direct compiler

The next bounded question was a symmetry question:

> do the exact size-3 transfer bases from Level 59 collapse once observation
> and field support are treated symmetrically?

The answer was yes.

Define the canonical quotient:

- `support_signature := (sort(obs_profile, field_profile), swap_pairs)`

The strongest exact result was:

- the exact size-3 transfer bases collapse to one exact singleton quotient
- unique exact singleton basis:
  - `support_signature`
- no other singleton in the augmented coordinate library is exact

Exact support-signature rule:

- `(((0,0,0),(0,0,0)),0) -> DIAGONAL`
- `(((1,0,0),(1,0,0)),0) -> DIAGONAL+SINGLE`
- `(((1,1,0),(1,1,0)),0) -> DIAGONAL+DOUBLE_SINGLE`
- `(((1,1,0),(1,1,0)),1) -> DIAGONAL+SWAP2`
- `(((1,1,0),(2,0,0)),0) -> DIAGONAL+BUNDLE2`
- `(((1,1,1),(1,1,1)),0) -> DIAGONAL+TRIPLE_SINGLE`
- `(((1,1,1),(2,1,0)),1) -> DIAGONAL+SWAP2+SINGLE`
- `(((2,1,0),(2,1,0)),0) -> DIAGONAL+BUNDLE2+SINGLE`

Support-signature count:

- `8`

So the Level 59 support law is not only exact. It also admits a canonical
singleton quotient.

### Level 61: four-scalar support law

The next bounded question was whether the canonical support quotient remained
tuple-heavy, or whether it scalarized again.

The searched scalar library was:

- `extra_count`
- `max_obs`
- `max_field`
- `swap_pairs`
- `same_obs`
- `same_field`

The strongest exact result was:

- no `1`-scalar basis is exact
- no `2`-scalar basis is exact
- no `3`-scalar basis is exact
- the first exact basis has size:
  - `4`
- exact size-`4` basis count:
  - `3`

Preferred exact basis:

- `extra_count`
- `max_obs`
- `max_field`
- `swap_pairs`

Its exact rule is:

- `0,0,0,0 -> DIAGONAL`
- `1,1,1,0 -> DIAGONAL+SINGLE`
- `2,1,1,0 -> DIAGONAL+DOUBLE_SINGLE`
- `2,1,1,1 -> DIAGONAL+SWAP2`
- `2,1,2,0` or `2,2,1,0 -> DIAGONAL+BUNDLE2`
- `3,1,1,0 -> DIAGONAL+TRIPLE_SINGLE`
- `3,1,2,1` or `3,2,1,1 -> DIAGONAL+SWAP2+SINGLE`
- `3,2,2,0 -> DIAGONAL+BUNDLE2+SINGLE`

So the software transfer ladder is now:

- local singleton motif compiler
- support-signature transfer compiler
- canonical singleton support quotient
- exact four-scalar law above that quotient

That is the strongest software-engineering loop object in the repo so far.

### Level 62: three-scalar max-support law

The next bounded question was whether the four-scalar law still carried hidden
axis-specific redundancy.

The searched semantic scalar library was:

- `extra_count`
- `max_support`
- `min_support`
- `support_gap`
- `swap_pairs`

where:

- `max_support := max(max_obs, max_field)`
- `min_support := min(max_obs, max_field)`
- `support_gap := max_support - min_support`

The strongest exact result was:

- no singleton scalar is exact
- no pair scalar basis is exact
- the first exact basis has size:
  - `3`
- unique exact basis:
  - `extra_count`
  - `max_support`
  - `swap_pairs`

Its exact rule is:

- `0,0,0 -> DIAGONAL`
- `1,1,0 -> DIAGONAL+SINGLE`
- `2,1,0 -> DIAGONAL+DOUBLE_SINGLE`
- `2,1,1 -> DIAGONAL+SWAP2`
- `2,2,0 -> DIAGONAL+BUNDLE2`
- `3,1,0 -> DIAGONAL+TRIPLE_SINGLE`
- `3,2,0 -> DIAGONAL+BUNDLE2+SINGLE`
- `3,2,1 -> DIAGONAL+SWAP2+SINGLE`

So the support ladder sharpened again:

- canonical support-signature quotient
- exact four-scalar law
- exact three-scalar semantic law

That is the strongest bounded software repair compiler family in the repo so
far.

### Level 63: two-coordinate support-orbit law

The next bounded question was whether the exact three-scalar law still carried a
hidden orbit quotient.

The searched orbit library was:

- `extra_count`
- `support_kind`
- `max_support`
- `swap_pairs`
- `all_distinct`
- `has_bundle`
- `has_swap`

where:

- `support_kind = plain` if `swap_pairs = 0` and `max_support = 1`
- `support_kind = bundle` if `swap_pairs = 0` and `max_support > 1`
- `support_kind = swap` if `swap_pairs > 0`

The strongest exact result was:

- no singleton orbit coordinate is exact
- the first exact basis has size:
  - `2`
- unique exact basis:
  - `extra_count`
  - `support_kind`

Its exact rule is:

- `0, plain -> DIAGONAL`
- `1, plain -> DIAGONAL+SINGLE`
- `2, plain -> DIAGONAL+DOUBLE_SINGLE`
- `2, bundle -> DIAGONAL+BUNDLE2`
- `2, swap -> DIAGONAL+SWAP2`
- `3, plain -> DIAGONAL+TRIPLE_SINGLE`
- `3, bundle -> DIAGONAL+BUNDLE2+SINGLE`
- `3, swap -> DIAGONAL+SWAP2+SINGLE`

So the software ladder sharpened again:

- canonical support-signature quotient
- exact three-scalar semantic law
- exact two-coordinate orbit law

### Level 64: menu-valued support-signature law

The next bounded transfer question was what survives once one unique minimal
repair shape no longer exists on the up-to-four-overlap atlas.

The exact target changed:

- not one chosen minimal repair shape
- but the full exact menu of minimal repair head-shapes in the semantic schema
  grammar

Canonical coordinate library:

- `support_signature`
- `obs_profile`
- `field_profile`
- `swap_pairs`

Raw support library:

- `obs_profile`
- `field_profile`
- `swap_pairs`

where:

- `support_signature := (sort(obs_profile, field_profile), swap_pairs)`

The strongest exact result was:

- the old direct orbit law no longer determines one unique minimal repair
  shape
- the canonical `support_signature` still determines the full exact menu of
  minimal repair head-shapes
- in the canonical coordinate library:
  - unique exact singleton:
    - `support_signature`
- in the raw support library:
  - no singleton is exact
  - no pair is exact
  - first exact basis size:
    - `3`
  - unique exact raw basis:
    - `obs_profile`
    - `field_profile`
    - `swap_pairs`

Menu counts on the `57`-family atlas:

- support-signature states:
  - `11`
- distinct exact menus:
  - `11`
- menu cardinality histogram:
  - `1 -> 24`
  - `2 -> 15`
  - `3 -> 12`
  - `5 -> 6`

So the first real obstruction above the direct compiler line was not a total
failure of symbolic structure. It was a change of target:

- from one chosen repair shape
- to an exact menu of minimal repair shapes

### Level 65: full-atlas support-signature menu law

The next bounded transfer question was whether the exact menu-valued law from
Level 64 survives on the full software atlas.

The bounded domain was:

- all subsets of the six off-diagonal repair edges
- family count:
  - `64`

The strongest exact result was:

- the menu-valued support law survives unchanged on the full atlas
- in the canonical coordinate library:
  - unique exact singleton:
    - `support_signature`
- in the raw support library:
  - no singleton is exact
  - no pair is exact
  - first exact basis size:
    - `3`
  - unique exact raw basis:
    - `obs_profile`
    - `field_profile`
    - `swap_pairs`

Full-atlas counts:

- support-signature states:
  - `13`
- distinct exact menus:
  - `13`
- menu cardinality histogram:
  - `1 -> 24`
  - `2 -> 15`
  - `3 -> 13`
  - `5 -> 6`
  - `6 -> 6`

The full off-diagonal family lands at:

- support signature:
  - `(((2, 2, 2), (2, 2, 2)), 3)`
- exact menu:
  - `BUNDLE2+BUNDLE2+BUNDLE2+DIAGONAL`
  - `BUNDLE2+BUNDLE2+DIAGONAL+SWAP2`
  - `DIAGONAL+SWAP2+SWAP2+SWAP2`

So the software lesson at this stage is:

- direct compilers can survive a long way
- when they stop being unique, the right exact object may be a menu-valued
  repair language
- and that menu law can still transfer farther than the direct compiler did

### Level 66: normalized support-signature direct compiler family

The next bounded question was whether the full-atlas menu law can restore direct
compilers once a deterministic normal form is chosen inside each exact menu.

The searched menu-local normal forms were:

- `bundle_first`
- `swap_first`
- `single_first`
- `fewest_families`

where:

- `bundle_first` maximizes `BUNDLE2`, then `SWAP2`, then minimizes `SINGLE`
- `swap_first` maximizes `SWAP2`, then `BUNDLE2`, then minimizes `SINGLE`
- `single_first` maximizes `SINGLE`
- `fewest_families` minimizes the number of distinct macro families

The strongest exact result was:

- for all four searched normal forms:
  - `support_signature` is the unique exact singleton in the canonical
    coordinate library
  - in the raw support library:
    - no singleton is exact
    - no pair is exact
    - the first exact basis is:
      - `obs_profile`
      - `field_profile`
      - `swap_pairs`

Ambiguity is real:

- ambiguous families:
  - `40`
- on all `40`, at least two normal forms disagree

Pairwise disagreement counts:

- `bundle_first` vs `swap_first`:
  - `16`
- `bundle_first` vs `single_first`:
  - `30`
- `bundle_first` vs `fewest_families`:
  - `0`
- `swap_first` vs `single_first`:
  - `40`
- `swap_first` vs `fewest_families`:
  - `16`
- `single_first` vs `fewest_families`:
  - `30`

So the preferred structural fact is:

- `bundle_first` and `fewest_families` coincide on all ambiguous families

That gives the software ladder at this stage:

- exact menu discovery
- exact support-signature transfer
- exact normalized direct compiler family above the menu law

The important lesson is:

- non-unique exact menus do not end the direct-compiler line
- they can become the substrate for a family of exact normalized direct
  compilers

### Level 67: perfect-swap-cover selector law

The next bounded question was whether the ambiguous full-atlas slice admits a
tiny exact semantic selector above the normalized compiler family.

The target property was:

- whether the exact menu admits a pure-swap normal form

meaning a head-shape built only from:

- `DIAGONAL`
- `SWAP2`

The searched selector library was:

- `perfect_swap_cover`
- `extra_count`
- `swap_pairs`
- `balanced_profiles`
- `max_support`
- `obs_profile`
- `field_profile`

where:

- `perfect_swap_cover := (extra_count = 2 * swap_pairs)`

The strongest exact result was:

- on the ambiguous full-atlas slice, the exact menu admits a pure-swap normal
  form iff:
  - `perfect_swap_cover`
- in the searched selector library:
  - the unique exact singleton is:
    - `perfect_swap_cover`

Counts:

- ambiguous families:
  - `40`
- ambiguous support signatures:
  - `7`
- pure-swap families:
  - `4`
- pure-swap support signatures:
  - `2`

Pure-swap support signatures:

- `(((2, 1, 1), (2, 1, 1)), 2)`
- `(((2, 2, 2), (2, 2, 2)), 3)`

So the post-menu ladder sharpened again:

- exact menu discovery
- exact normalized direct compiler family
- exact one-bit semantic selector for the pure-swap regime

At this stage, that is the clearest software branch in the repo.

### Level 68: bundle-vs-swap disagreement selector law

The next bounded question was whether the ambiguous full-atlas slice admits a
tiny exact selector for when two structurally meaningful normal forms actually
diverge:

- `bundle_first`
- `swap_first`

This is a stricter target than Level 67. It no longer asks whether a special
pure-swap regime exists. It asks for the first exact law that predicts
disagreement inside the normalized compiler family itself.

The searched selector library was:

- `perfect_swap_cover`
- `extra_count`
- `swap_pairs`
- `balanced_profiles`
- `max_support`
- `obs_profile`
- `field_profile`

where:

- `perfect_swap_cover := (extra_count = 2 * swap_pairs)`
- `balanced_profiles := (obs_profile = field_profile)`

The strongest exact result was:

- on the ambiguous full-atlas slice:
  - no singleton selector is exact
  - no pair selector is exact
  - the first exact selector basis has size:
    - `3`
  - minimal exact basis count:
    - `8`

A preferred exact basis is:

- `extra_count`
- `swap_pairs`
- `balanced_profiles`

and it yields the exact `7`-state disagreement law:

- `(3, 0, True) -> same`
- `(3, 1, False) -> same`
- `(4, 1, False) -> diff`
- `(4, 1, True) -> same`
- `(4, 2, True) -> diff`
- `(5, 2, True) -> diff`
- `(6, 3, True) -> diff`

So the structural picture is now:

- with `3` extra overlaps, the two normal forms agree
- with `4` extra overlaps, they disagree exactly when either:
  - the profiles are unbalanced and there is one swap pair
  - or the overlap is perfectly swap-covered
- with `5` or `6` extra overlaps, they disagree

This is the first exact intrinsic selector above the normalized family. It
shows that:

- the disagreement is real
- it is not controlled by any singleton or pair semantic selector in the
  searched library
- but it still collapses to a tiny exact three-coordinate state

### Level 69: canonical ambiguity quotient law

The next bounded question was whether the previous disagreement selector is only
a one-off fact about one pair of normal forms, or whether a deeper shared
quotient controls the whole ambiguous normalized family.

The compared normal forms were:

- `bundle_first`
- `swap_first`
- `single_first`
- `fewest_families`

The target was:

- for each pair of normal forms, label each ambiguous family as:
  - `diff` if the two chosen normalized repair shapes differ
  - `same` otherwise

The strongest exact result was:

- among the six pairwise comparisons:
  - two are constant:
    - `bundle_first` vs `fewest_families` is always `same`
    - `swap_first` vs `single_first` is always `diff`
  - the other four are non-constant

For all four non-constant pairwise disagreements:

- the first exact basis size is:
  - `3`
- the common minimal exact basis family has count:
  - `8`
- a preferred common exact basis is:
  - `extra_count`
  - `swap_pairs`
  - `balanced_profiles`
- preferred quotient state count:
  - `7`

The four non-constant pairs are:

- `bundle_first` vs `swap_first`
- `bundle_first` vs `single_first`
- `swap_first` vs `fewest_families`
- `single_first` vs `fewest_families`

So the post-menu software object is no longer:

- one repair menu
- one normalized compiler
- one selector for one special regime
- one selector for one pairwise disagreement

It is:

- one common exact ambiguity quotient above the whole normalized family

That is stronger than Level 68. It says the remaining structural ambiguity is
not arbitrary. It factors through one shared exact state.

### Level 70: support-gap ambiguity law

The next bounded question was whether the common ambiguity quotient from Level
69 already has a smaller semantic presentation in a derived feature library.

The searched derived coordinates were:

- `extra_count`
- `swap_pairs`
- `balanced_profiles`
- `perfect_swap_cover`
- `support_gap`
- `bundle_load`
- `high_overlap`
- `max_support`
- `one_swap`
- `many_swaps`

where:

- `support_gap := extra_count - 2 * swap_pairs`
- `bundle_load := extra_count - swap_pairs`

The target was the full six-pair disagreement signature among:

- `bundle_first`
- `swap_first`
- `single_first`
- `fewest_families`

The strongest exact result was:

- no singleton coordinate is exact
- the first exact basis size is:
  - `2`
- exact minimal basis count:
  - `1`
- the unique exact minimal basis is:
  - `balanced_profiles`
  - `support_gap`

The exact rule has `6` states:

- `(False, 1) -> ('same', 'same', 'diff', 'same', 'diff', 'diff')`
- `(False, 2) -> ('same', 'diff', 'same', 'diff', 'diff', 'same')`
- `(True, 0) -> ('same', 'diff', 'same', 'diff', 'diff', 'same')`
- `(True, 1) -> ('same', 'diff', 'diff', 'diff', 'diff', 'diff')`
- `(True, 2) -> ('same', 'same', 'diff', 'same', 'diff', 'diff')`
- `(True, 3) -> ('same', 'same', 'diff', 'same', 'diff', 'diff')`

The full disagreement-signature target has only `3` distinct output classes, so
this is a genuine semantic compression of the ambiguity layer.

At this point, that is the strongest software result in the tutorial. The remaining
post-menu ambiguity is not only shared. In the searched semantic library, it
has a unique exact size-`2` presentation.

### Level 71: three-guard ambiguity-class law

The next bounded question was whether the three disagreement-signature classes
above Level 70 compile to a tiny exact branch program, or whether the size-`2`
semantic basis is already the final usable object.

The searched branch grammar used:

- atoms over:
  - `balanced_profiles`
  - `support_gap`
- conjunction guards of size up to `2`
- ordered decision lists with up to `3` guards

The strongest exact result was:

- no `0`-guard program is exact
- no `1`-guard program is exact
- no `2`-guard program is exact
- the first exact program has:
  - `3` guards

The exact decision law is:

- `support_gap = 0 -> class_2`
- `balanced_profiles and support_gap = 1 -> class_3`
- `unbalanced_profiles and support_gap = 2 -> class_2`
- default:
  - `class_1`

The class meanings are:

- `class_1`:
  - `('same', 'same', 'diff', 'same', 'diff', 'diff')`
- `class_2`:
  - `('same', 'diff', 'same', 'diff', 'diff', 'same')`
- `class_3`:
  - `('same', 'diff', 'diff', 'diff', 'diff', 'diff')`

So the software branch is no longer only:

- a shared ambiguity quotient
- or even a unique exact size-`2` semantic basis

It is:

- a tiny exact branch program for the ambiguity classes themselves

That is closer to the kind of object a formal software-assurance loop could
actually run inside a repair engine.

### Level 72: anchored outlier decomposition law

The next bounded question was whether the class labels from Level 71 have a
smaller semantic meaning than just `class_1`, `class_2`, and `class_3`.

The natural interpretation is to treat:

- `bundle_first = fewest_families`

as the anchor, then ask:

- when does `swap_first` peel away from the anchor?
- when does `single_first` peel away from the anchor?

The strongest exact result was:

- the ambiguity layer splits into two exact semantic outlier bits
- both outlier bits first become exact at:
  - `2` guards

Exact `swap_outlier` law:

- `balanced_profiles and support_gap >= 2 -> False`
- `unbalanced_profiles and support_gap = 1 -> False`
- default:
  - `True`

Exact `single_outlier` law:

- `support_gap = 0 -> False`
- `unbalanced_profiles and support_gap = 2 -> False`
- default:
  - `True`

So the ambiguity layer now has an explicit semantic decomposition:

- one anchor:
  - `bundle_first = fewest_families`
- one `swap_outlier` bit
- one `single_outlier` bit

This is stronger than Level 71. The class program is still exact, but now the
classes are interpretable:

- `single_outlier`
- `swap_outlier`
- `double_outlier`

### Level 73: two-clause ambiguity-class law

The next bounded question was whether the ambiguity-class program from Level 71
can be compressed further by changing the logic language rather than widening
the same conjunction grammar.

The searched clause grammar used:

- conjunction terms of size up to `2`
- clauses that are ORs of up to `2` conjunction terms
- ordered decision lists of up to `2` clauses

The strongest exact result was:

- no `0`-clause program is exact
- no `1`-clause program is exact
- the first exact classifier has:
  - `2` ordered clauses

The exact law is:

- `balanced_profiles and support_gap = 1 -> class_3`
- `support_gap = 0 or unbalanced_profiles and support_gap = 2 -> class_2`
- default:
  - `class_1`

So allowing one small disjunctive clause compresses the ambiguity-class program
from:

- `3` conjunction guards

to:

- `2` ordered clauses

This is one of the clearest software examples in the tutorial of a broader
lesson:

- the next exact survivor may come from a better symbolic language, not from a
  wider search over the old one

### Level 74: anchor-shape law

The next bounded question was whether the stable anchor from Level 72 also
admits a tiny exact symbolic summary over the same semantic state.

The anchor was:

- `bundle_first = fewest_families`

The strongest exact result was:

- the anchor repair family itself compiles to a tiny exact program over:
  - `balanced_profiles`
  - `support_gap`
- no `0`-guard program is exact
- no `1`-guard program is exact
- no `2`-guard program is exact
- the first exact program has:
  - `3` guards

The exact law is:

- `balanced_profiles and support_gap = 2 -> BUNDLE2+BUNDLE2+DIAGONAL+SWAP2`
- `support_gap >= 2 -> BUNDLE2+BUNDLE2+DIAGONAL`
- `balanced_profiles -> BUNDLE2+BUNDLE2+BUNDLE2+DIAGONAL`
- default:
  - `BUNDLE2+DIAGONAL+SWAP2`

Scope note:

- Level 77 later replays the actual `bundle_first` anchor on the full
  ambiguous slice and shows that this size-`2` reading is too strong if read
  as a true definability theorem for the actual anchor value
- the stronger truth is:
  - this level found a useful normalized anchor summary
  - the actual anchor first becomes exact only after adding `high_overlap`

So the branch now has a more complete anchored routing kernel:

- exact anchor compiler
- exact outlier bits above the anchor
- smaller exact class classifier in a richer clause language

That is stronger than having local selectors alone. It is now much closer to a
formal software-assurance controller over the bounded repair atlas.

### Level 75: anchored routing kernel law

The next bounded question was whether the separate survivors from Levels 70, 72,
and 74 really collapse to one direct kernel object:

- `AnchorShape`
- `SwapOutlier`
- `SingleOutlier`

The joint target was:

```text
Kernel(x) = (AnchorShape(x), SwapOutlier(x), SingleOutlier(x))
```

Scope note:

- this was the strongest direct kernel summary available before the logic
  replay
- Level 77 below shows that the stronger reading, that the actual
  `bundle_first` anchor and the true joint kernel are both definable in
  `(balanced_profiles, support_gap)`, is false on the full ambiguous slice
- what survives is the smaller ambiguity and routing layer over that size-`2`
  theory

The strongest exact result was:

- the full anchored routing kernel first becomes exact at the same unique
  size-`2` semantic basis as the earlier ambiguity-signature law:
  - `balanced_profiles`
  - `support_gap`
- no singleton coordinate in the searched semantic library is exact
- no `0`-, `1`-, `2`-, `3`-, or `4`-guard joint program is exact
- the first exact joint program has:
  - `5` guards

So at that stage, the branch appeared to have one exact direct kernel:

```text
Kernel(x) = K(balanced_profiles(x), support_gap(x))
```

with the exact joint program:

- `unbalanced_profiles and support_gap = 1 -> (BUNDLE2+DIAGONAL+SWAP2, False, True)`
- `unbalanced_profiles -> (BUNDLE2+BUNDLE2+DIAGONAL, True, False)`
- `support_gap = 0 -> (BUNDLE2+BUNDLE2+BUNDLE2+DIAGONAL, True, False)`
- `support_gap = 1 -> (BUNDLE2+BUNDLE2+BUNDLE2+DIAGONAL, True, True)`
- `support_gap = 2 -> (BUNDLE2+BUNDLE2+DIAGONAL+SWAP2, False, True)`
- default:
  - `(BUNDLE2+BUNDLE2+DIAGONAL, False, True)`

This still mattered because the last several software survivors were no longer
only a stack of adjacent laws. They appeared to unify into one bounded formal
object:

- basis
- anchor
- outlier bits
- joint direct kernel

### Level 76: anchored kernel menu law

The next bounded question was whether the same size-`2` semantic basis also
determines the full menu of minimal repair shapes.

It does not.

The strongest exact result was:

- the anchored routing kernel basis:
  - `(balanced_profiles, support_gap)`
  - is exact for routing
  - but not exact for the full repair menu
- the first exact menu basis has size `3`
- a preferred exact semantic refinement is:
  - `(balanced_profiles, support_gap, high_overlap)`
- no singleton coordinate in the searched semantic library is exact

where:

```text
high_overlap := (extra_count >= 5)
```

The boundary is clean:

- the only kernel state that splits is:
  - `(balanced_profiles = True, support_gap = 0)`
- it separates into:
  - a low-overlap exact menu
  - a high-overlap exact menu

So the first crack above the anchored routing kernel is structural and
localized, not a general collapse of the semantic state.

Correction note:

- Level 77 shows that `Q2 = (balanced_profiles, support_gap)` was already too
  weak for the actual `bundle_first` anchor and the true joint kernel
- that means the right logic reading here is not:
  - kernel in `Q2`, menu in `Q3`
- it is:
  - ambiguity and routed-outlier structure in `Q2`
  - actual selector, kernel, and menu structure first exact in `Q3`

On the preferred basis, the exact menu states compile to a `6`-guard direct
program:

- `unbalanced_profiles and support_gap = 1`
  - `BUNDLE2+DIAGONAL+SINGLE`
  - `BUNDLE2+DIAGONAL+SWAP2`
  - `DIAGONAL+SINGLE+SWAP2`
- `unbalanced_profiles`
  - `BUNDLE2+BUNDLE2+DIAGONAL`
  - `BUNDLE2+DIAGONAL+SWAP2`
- `support_gap = 0 and low_overlap`
  - `BUNDLE2+BUNDLE2+DIAGONAL`
  - `DIAGONAL+SWAP2+SWAP2`
- `support_gap = 0`
  - `BUNDLE2+BUNDLE2+BUNDLE2+DIAGONAL`
  - `BUNDLE2+BUNDLE2+DIAGONAL+SWAP2`
  - `DIAGONAL+SWAP2+SWAP2+SWAP2`
- `support_gap = 1`
  - `BUNDLE2+BUNDLE2+BUNDLE2+DIAGONAL`
  - `BUNDLE2+BUNDLE2+DIAGONAL+SINGLE`
  - `BUNDLE2+BUNDLE2+DIAGONAL+SWAP2`
  - `BUNDLE2+DIAGONAL+SINGLE+SWAP2`
  - `BUNDLE2+DIAGONAL+SWAP2+SWAP2`
  - `DIAGONAL+SINGLE+SWAP2+SWAP2`
- `support_gap = 2`
  - `BUNDLE2+BUNDLE2+DIAGONAL+SINGLE`
  - `BUNDLE2+BUNDLE2+DIAGONAL+SWAP2`
  - `BUNDLE2+DIAGONAL+SINGLE+SINGLE`
  - `BUNDLE2+DIAGONAL+SINGLE+SWAP2`
  - `DIAGONAL+SINGLE+SINGLE+SWAP2`
- default:
  - `BUNDLE2+BUNDLE2+DIAGONAL`
  - `BUNDLE2+DIAGONAL+SINGLE`

### How to read Levels 77-85

Levels `77` through `85` are the current logic endpoint of this tutorial.

They are best read as one bounded definability ladder over the software atlases
used in those levels, not as nine unrelated observations.

The shared question is:

```text
what is the smallest searched theory in which the current target becomes exact?
```

The ladder that survives on the current bounded atlases is:

- `Q2 = (balanced_profiles, support_gap)` for relations and routed-outlier structure
- `Q3 = (balanced_profiles, support_gap, high_overlap)` for actual selector, kernel, and menu commitments
- `Q4 = (extra_count, orientation)` for oriented support geometry
- `incidence_signature = (out_profile, in_profile)` for ambiguous-slice raw family identity
- `incidence_signature + cycle_orientation` for full off-diagonal raw family identity

<figure class="fp-figure">
  <p class="fp-figure-title">Definability ladder</p>
  {% include diagrams/definability-ladder.svg %}
  <figcaption class="fp-figure-caption">
    Each tier is the smallest searched theory in which its class of targets
    becomes exact. The tower widens downward: coarser theories control simpler
    targets, while finer targets require richer theories.
  </figcaption>
</figure>

One way to picture this ladder is as a map legend that keeps gaining one new
symbol each time the older legend blurs two regions together. `Q2` separates
the broad regions, `Q3` marks commitment structure, `Q4` adds direction, and
the incidence signature plus one cycle bit resolves the last look-alike pair.

<figure class="fp-figure">
  <p class="fp-figure-title">Late logic ladder</p>
  {% include diagrams/verifier-compiler-logic-ladder.svg %}
  <figcaption class="fp-figure-caption">
    The late endpoint is a definability ladder. `Q2` controls relation targets, `Q3` adds commitment and symmetric-support structure, `Q4` adds orientation, and incidence plus one cycle bit completes the full raw family identity on the bounded atlas.
  </figcaption>
</figure>

So the logic does not just get "bigger" at each step.
It changes what kind of object is being tracked:

- relation targets
- commitment targets
- symmetric versus oriented support geometry
- raw family identity
- transfer obstruction under atlas extension

### Level 77: logic replay correction law

The next bounded question was whether the software branch should really be read
through definability rather than only through compact branch programs.

The logic replay did expose a real overclaim.

On the full ambiguous slice, the actual `bundle_first` anchor is **not**
definable in:

```text
Q2(x) = (balanced_profiles(x), support_gap(x))
```

The same failure propagates to the true joint kernel:

```text
Kernel_true(x) = (AnchorShape_bundle_first(x), SwapOutlier(x), SingleOutlier(x))
```

The clean counterexample is the `Q2` state:

```text
(balanced_profiles = True, support_gap = 0)
```

which contains two different actual `bundle_first` anchor shapes:

- `BUNDLE2+BUNDLE2+DIAGONAL`
- `BUNDLE2+BUNDLE2+BUNDLE2+DIAGONAL`

The first searched bit that repairs the split is:

```text
high_overlap := (extra_count >= 5)
```

So the corrected theory is:

```text
Q3(x) = (balanced_profiles(x), support_gap(x), high_overlap(x))
```

and both:

- actual `bundle_first` anchor shape
- true joint kernel

first become exact in `Q3`.

This is the strongest logic-level correction in the software branch so far,
because it separates:

- a useful normalized quotient
- from a true definability theorem about the actual selector and kernel

### Level 78: software definability phase diagram law

Once the `Q2` versus `Q3` correction was explicit, the next bounded question
was which current software targets really live in which theory.

That produces a clean phase diagram.

The current targets split into two exact definability tiers.

The `Q2` tier is:

```text
Q2 = (balanced_profiles, support_gap)
```

and it exactly controls:

- `ambiguity_class`
- `swap_outlier`
- `single_outlier`
- `bundle_vs_swap`
- `bundle_vs_single`
- `swap_vs_fewest`
- `single_vs_fewest`

Two additional selector relations are degenerate constants on this corpus:

- `bundle_vs_fewest = True`
- `swap_vs_single = False`

The `Q3` tier is:

```text
Q3 = (balanced_profiles, support_gap, high_overlap)
```

and it first controls:

- `bundle_first`
- `fewest_families`
- `swap_first`
- `single_first`
- `true_kernel`
- `menu`

No searched non-constant target in the current software family requires a
theory beyond `Q3`.

So the logic-first read of the software branch is now:

```text
Q2 controls relations
Q3 controls realizations
```

That is a stronger and cleaner loop-family object than the earlier flat
“kernel plus menu” reading.

### Level 79: common commitment-tier witness law

The next bounded question was whether the `Q3` boundary was really a collection
of separate target-by-target failures, or whether one common witness state
already forces the whole commitment tier.

It does.

Inside the `Q2` state:

```text
(balanced_profiles = True, support_gap = 0)
```

the ambiguous slice contains:

- `3` low-overlap families
- `1` high-overlap family

and every low-overlap family separates from the unique high-overlap family on
every current `Q3` target:

- `bundle_first`
- `fewest_families`
- `swap_first`
- `single_first`
- `true_kernel`
- `menu`

So the extra bit:

```text
high_overlap := (extra_count >= 5)
```

is not only needed for one selector.

It is a common necessity witness for the whole commitment tier.

This sharpens the logic hierarchy again:

- `Q2` controls relations
- `Q3` controls commitments
- one common witness state forces that split

That is the cleanest model-theoretic object in the current software branch.

### Level 80: software target-algebra closure law

The next bounded question was whether the current software branch still hid a
larger target algebra above the separate `Q2` and `Q3` facts, or whether the
current target family was already closed.

It is already closed.

The relation algebra is:

- `ambiguity_class`
- `swap_outlier`
- `single_outlier`
- `bundle_vs_swap`
- `bundle_vs_single`
- `swap_vs_fewest`
- `single_vs_fewest`

and it is uniquely and minimally controlled by:

```text
Q2 = (balanced_profiles, support_gap)
```

with `6` exact states.

The commitment algebra is:

- `bundle_first`
- `fewest_families`
- `swap_first`
- `single_first`
- `true_kernel`
- `menu`

and it is minimally controlled by a size-`3` quotient, with:

```text
Q3 = (balanced_profiles, support_gap, high_overlap)
```

as a preferred exact basis with `7` states.

The full current target algebra, relations plus commitments together, is also
minimally controlled by a size-`3` quotient, again with `Q3` as a preferred
exact basis.

So the current software logic is already algebraically closed at `Q3`.

That means the next honest frontier is no longer another target from the same
family. It is:

- a genuinely richer target family that escapes `Q3`
- or a selector theorem inside the exact `Q3` states

### Level 81: richer selector-family closure law

The next bounded question was whether that closure was fragile.

So instead of reusing only the hand-chosen selector targets, the search widened
to a richer structural selector family:

- all lexicographic selector orders of length `1..3`
- over:
  - `bundle_max`
  - `swap_max`
  - `single_max`
  - `single_min`
  - `families_min`

That gives:

- `85` raw selectors
- collapsing to `10` unique selector behaviors on the bounded corpus

The strongest result was that even this richer selector family still first
becomes exact at size `3`, and:

```text
Q3 = (balanced_profiles, support_gap, high_overlap)
```

remains a preferred `7`-state exact basis.

So no searched richer selector in this family escapes `Q3`.

This sharpens the frontier again:

- the current software atlas is more saturated than it looked
- the next real jump must come from a genuinely richer target family
- not from another selector variant inside the same closure

So the software branch now has a clearer stack:

- exact kernel
- exact localized boundary above the kernel
- exact menu refinement above that boundary

### Level 82: support-geometry phase diagram law

The next bounded question was what the first honest escape from `Q3` actually
looks like.

The answer is not a richer selector.
It is support orientation.

The symmetric support target is:

```text
support_signature
```

and it already closes at:

```text
Q3 = (balanced_profiles, support_gap, high_overlap)
```

with:

- minimal exact basis size `3`
- preferred exact state count `7`

So `Q3` does not only control commitment targets.
It already controls the full symmetric support geometry on the ambiguous slice.

The first real escape is the oriented support target:

```text
oriented_support_pair = (obs_profile, field_profile)
```

That target is not definable in `Q3`.
The clean witness states are:

- `(False, 1, False)`
- `(False, 2, False)`

Each contains both orientations of the same symmetric support shape.

The first exact orientation theory in the searched library is:

```text
Q4 = (extra_count, orientation)
```

with:

- minimal exact basis size `2`
- preferred exact state count `8`

A conservative extension of `Q3` by the orientation bit is also exact, but it
is redundant.

At the same time, raw family identity still escapes the full searched
symmetric-plus-orientation library.

So the logic ladder sharpens again:

- `Q2` for relations
- `Q3` for commitments and symmetric support
- `Q4` for oriented support
- raw family identity still beyond the current semantic library

### Level 83: row-column incidence completion law

The next bounded question was whether raw family identity needs brute-force edge
indicators, or whether a smaller structural theory can recover it.

It can.

The first exact completion law is a row-column incidence theory.

Using only:

- row degrees:
  - `out_guard`
  - `out_bounds`
  - `out_transform`
- column degrees:
  - `in_guard`
  - `in_bounds`
  - `in_transform`
- auxiliaries:
  - `extra_count`
  - `support_gap`

the raw family target first becomes exact at size `5`.

No basis of size `4` or smaller is exact.

A preferred symmetric exact basis is:

```text
(out_guard, out_bounds, out_transform, in_guard, in_bounds)
```

with:

- minimal exact basis size `5`
- minimal exact basis count `24`
- preferred exact state count `40`

The basis families break down as:

- `6` pure degree bases
- `9` `extra_count` substitution bases
- `9` `support_gap` substitution bases

So the next theory above the semantic stack is not “memorize the family”.
It is incidence.

The current logic picture is now:

- `Q2` controls relations
- `Q3` controls commitments and symmetric support
- `Q4` controls oriented support
- row-column incidence completes raw family identity

### Level 84: incidence-signature singleton law

The next bounded question was whether the size-`5` incidence law from Level 83
was still more complicated than necessary.

It was.

The raw family target on the ambiguous slice collapses again to one canonical
tuple quotient:

```text
incidence_signature = (out_profile, in_profile)
```

This is the unique exact singleton in the searched tuple-aware incidence
library.

So on the ambiguous slice:

- minimal exact basis size: `1`
- unique exact singleton:
  - `incidence_signature`
- exact state count: `40`

and the obvious nearby singletons are not exact:

- `out_profile`
- `in_profile`
- `extra_count`
- `support_gap`
- `orientation`

So the right logic object above `Q4` is not really “five degree counts”.
It is one bipartite incidence signature.

### Level 85: cycle-orientation incidence extension law

The next bounded question was whether the singleton incidence-signature law from
Level 84 transfers to the full off-diagonal atlas.

Almost, but not quite.

It fails on exactly one obstruction bucket:

```text
incidence_signature = ((1,1,1),(1,1,1))
```

That bucket contains exactly the two opposite off-diagonal `3`-cycles.

So on the full `64`-family atlas:

- no singleton in the searched library is exact
- the first exact basis size is `2`
- exact size-`2` bases are:
  - `(incidence_signature, cycle_orientation)`
  - `(incidence_signature, has_guard_to_bounds)`
  - `(incidence_signature, has_guard_to_transform)`

The preferred semantic basis is:

```text
(incidence_signature, cycle_orientation)
```

So the transfer obstruction is not diffuse.
It is one clean cycle-orientation bit.

That sharpens the current logic ladder again:

- `Q2` for relations
- `Q3` for commitments and symmetric support
- `Q4` for oriented support
- `incidence_signature` for ambiguous-slice raw family identity
- `incidence_signature + cycle_orientation` for full-atlas raw family identity

## Part XIII: what this means for software assurance and performance

These loops do help software assurance, but the scope matters.

What they can already do in a bounded formal setting:

- turn a repair search space into explicit obligation fibers
- attach small local witnesses to candidate repairs
- compile those witnesses back into symbolic repair rules
- compress families of local repairs into shared repair languages
- expose exactly where ambiguity remains, and which symbolic features control
  it

That is useful for correct-by-construction work in at least three ways.

First, it changes when verification happens.

Instead of:

- search for a patch
- run the full checker at the end

the loop becomes:

- search for a repair witness
- check the witness locally
- compile the witness into a repair shape
- keep the exact bounded verifier as the fail-closed outer gate

If the witness language is exact on the modeled corpus, many wrong repairs are
cut off before full end-to-end checking.

Second, it changes what gets reused.

The reusable object is often not:

- one patch

It is:

- a repair language
- a decoder
- a support quotient
- an ambiguity quotient

Those are higher-leverage assets for formal software assurance because they can
be checked once per bounded model and then reused across many cases inside that
model.

Third, it can reduce search effort inside the bounded loop.

That bounded gain does not come from dropping formal checks. It comes from:

- shrinking the search object
- routing cases into smaller exact fibers
- replacing large lookups with tiny symbolic compilers
- reducing the number of candidate repairs that need full evaluation
- sometimes switching to a better symbolic language when the old grammar
  saturates

That is why the software branch kept improving when the object of search
changed:

- monolithic patch search
- dependency-aware repair fibers
- certificate-carrying repair
- witness-to-patch compilation
- shared repair-language templates
- exact ambiguity quotients

The honest limit is:

- these are bounded exact laws, not universal program-repair theorems

So they are not yet full correct-by-construction repair for arbitrary code.

They are better understood as:

- exact formal loop components
- discovered on bounded corpora
- suitable for promotion into stronger proof pipelines later
- including small symbolic routing kernels that can sit in front of heavier
  verification or synthesis stages

## Part XIV: what this tutorial really teaches

The deepest lesson is not:

> compile every verifier.

It is:

> treat verifier behavior as a mathematical object worth compressing.

Sometimes that object is tiny.
Sometimes it is not.

But once the possibility is visible, a new kind of neuro-symbolic leverage appears:

- proposal generation on one side,
- exact labels on the other,
- compression of verifier structure in the middle.

That is the verifier-compiler loop.

It is more general than one special example.

It is less general than a universal law of all neuro-symbolic systems.

That is the right scope.

## Next honest frontiers

The current public endpoint is Level `85`, the cycle-orientation incidence
extension law.

On the current evidence, the next honest frontiers are:

- a richer software atlas where `incidence_signature + cycle_orientation` stops being exact
- a smaller semantic account of `cycle_orientation` itself, instead of treating it only as a repair bit
- additional Lean receipts for the later logic ladder, especially the incidence and transfer steps

## References inside this repo

- [Tutorial 25: Quantifier factoring and neuro-symbolic loop engineering]({{ '/tutorials/quantifier-factoring-and-neuro-symbolic-loops/' | relative_url }})
- [Tutorial 26: Galois loops and obligation carving]({{ '/tutorials/galois-loops-and-obligation-carving/' | relative_url }})
