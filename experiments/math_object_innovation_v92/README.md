# v92: unlock taxonomy for the mature witness-language line

## Question

After `v78` through `v91`, the line had accumulated many different kinds of
moves:

- family comparisons,
- residual-budget search,
- schema sharing,
- partition search,
- grammar widening,
- transfer,
- semantic explanation search.

The next question is meta-level but still bounded:

> which kinds of interventions actually moved the mature frontier, and which
> kinds mostly exposed ceilings?

That matters because the next loop family should add a new structural search
axis, not only repeat a move that is already saturating.

## Method

Bounded domain:

- the published mature witness-language and transfer line:
  - `v78` through `v91`

For each cycle, record:

- intervention class,
- whether it added a new structural search axis,
- whether it produced:
  - frontier gain,
  - local gain,
  - boundary only,
  - or saturation,
- the exact number of bounded gain-events when that was meaningful.

This is a descriptive-oracle meta-cycle over already published exact reports.

## Main bounded result

The strongest exact gains came from adding new search axes, not from widening
the current grammar.

Exact bounded counts:

- total events:
  - `14`
- new-axis interventions:
  - `9` cycles
  - `6` gain cycles
  - `16` gain-events
- same-axis widening:
  - `5` cycles
  - `2` gain cycles
  - `4` gain-events

Outcome counts:

- `frontier_gain`:
  - `6`
- `localized_gain`:
  - `1`
- `boundary`:
  - `3`
- `saturation`:
  - `3`
- `baseline_ordering`:
  - `1`

Most productive intervention classes:

1. `new_axis`
   - gain-events:
     - `15`
   - gain cycles:
     - `5`
2. `grammar_widening`
   - gain-events:
     - `4`
   - gain cycles:
     - `2`
   - saturation cycles:
     - `3`
3. `comparison_family`
   - gain-events:
     - `0`
   - boundary cycles:
     - `2`

The new-axis gains were:

- `v81`, residual-budget search
- `v82`, global schema sharing
- `v83`, joint partition plus residual-budget search
- `v88`, transfer as a first-class exact object
- `v90`, score-free semantic explanation search

The grammar-widening story was much weaker:

- `v84`, one critical-region local gain
- `v85`, one partial global low-residual gain
- `v86`, `v87`, `v89`, saturation

## Why it matters

This turns the recent progression into a cleaner law.

The frontier moved when the object of search changed:

- obligation,
- quotient,
- witness language,
- partition,
- schema library,
- semantic explanation object.

The frontier usually did not move much when the old formula grammar was merely
made wider.

So the next honest rabbit hole is not another literal sweep.

It is the next deeper object.

The strongest candidate is:

- temporal monitor-cell obligation carving on Tau specs

Then, above that:

- minimal witness-language discovery over temporal cells,
- semantic predicate invention when static witness grammars saturate.

## Status

Survivor. This is an exact bounded unlock taxonomy over the mature
witness-language line from `v78` to `v91`.

## Next

- package `v93` as temporal monitor-cell obligation carving on the Tau retest
  tracker safety fragment
- or search a small semantic predicate grammar that enlarges the maximal exact
  refill merged subset beyond `(9,10,12)`
