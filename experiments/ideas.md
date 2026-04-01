# Ideas Memory

## Active

### Counterexample scheduling and proposer coupling in Galoisized CEGIS

Hypothesis:

- closure-gain scheduling may be exact or nearly exact on wider bounded domains than naive counterexample selection

Current status:

- survived `3x3` and `3x4` exhaustively
- survived `4x4` as a strong near-optimal heuristic, but not exact
- new survivor:
  - pairing a singleton-closure proposer with a closure-gain verifier was exact on exhaustive `4x4`

Next ideas:

- characterize the `5x5` failure family for the coupled policy
- test one-step versus two-step lookahead policies
- test whether the coupled exactness extends to other proposer heuristics derived from closure geometry

### Obligation-targeted witness routing

Hypothesis:

- a coupled proposer/verifier policy may compress into a pure obligation controller plus a witness router

Current status:

- survived exhaustive `4x4`
- survived random `5x5` equivalence checks between pair policy and route policy

Next ideas:

- search for a stronger obligation-only score that beats the current route controller on `5x5`
- connect the routing view to LLMs explicitly, where the model synthesizes witnesses for chosen obligations

### Obligation-side policy iteration

Hypothesis:

- policy iteration over the obligation controller may converge much faster than expected on these finite domains

Current status:

- `pi_1` was already much stronger than the base routed controller
- `pi_2` was exact on exhaustive `4x4`
- `pi_2` was exact on all sampled `5x5` and `6x6` holdouts tested so far

Next ideas:

- search for a structural reason why two improvement rounds suffice on `4x4`
- test `7x7` random domains
- look for a compressed description of `pi_2` that removes explicit dynamic-programming backpropagation

### Controller compression frontier

Hypothesis:

- the improved obligation controller may admit a short direct symbolic score

Current status:

- tested local lexicographic scores of depth at most `3` over `20` signed local features
- no exact compression found on exhaustive `4x4` nonterminal roots
- best replayed root formulas:
  - `(max_gain, max_child_best_gain)`
  - `(min_next_uncovered, max_child_best_gain)`
- bounded hit rate:
  - `65391 / 65535`

Next ideas:

- characterize the remaining `144` exceptional roots
- move from root-only compression to statewise compression
- test piecewise controllers and certificate-augmented controller languages

### Exception-carved controller distillation

Hypothesis:

- a near-exact local controller may become exact once a very small number of repeated failure motifs are promoted into explicit exception branches

Current status:

- the `144` root failures of the best flat controller collapsed to one repeated motif
- a two-branch symbolic controller became exact on exhaustive `4x4` nonterminal roots

Next ideas:

- test the same failure-motif distillation pattern on full candidate-state graphs, not only roots
- search for a short controller language that subsumes both the base rule and the exception branch
- check whether similar repeated motifs appear on sampled `5x5` and `6x6` roots

### Lookahead-dominance controller

Hypothesis:

- the exact motif exception may compress into a generic comparative dominance rule

Current status:

- yes on bounded `4x4`
- exact on exhaustive roots and exhaustive reachable nonterminal states
- also improves the flat base controller on sampled `5x5` and `6x6` roots
- quick extra corroboration:
  - on sampled reachable `5x5` states, it matched all tested states at density `0.3` and `0.7`
  - and closed the full sampled gap at density `0.5`

Next ideas:

- derive the dominance clause directly from the bounded Bellman equations
- search a small family of dominance clauses instead of hand-fixing one
- test sampled deeper states for `5x5` and `6x6`, not only roots

Current refinement:

- the exact bounded dominance rule is not unique
- a small exact clause family exists on exhaustive reachable `4x4` states
- best sampled larger-root generalizer in that family:
  - `gain_loss = 1`
  - `child_gain_min = 2`
  - `child_cut_min = 0`
  - `next_delta = 1`
  - `next_mode in {eq, ge}`

New next ideas:

- search small multi-clause dominance languages
- score them on sampled deeper `5x5` and `6x6` states

Boundary learned:

- a nearby one-clause repair search around the best exact core did not beat the core while preserving exhaustive `4x4` exactness
- so the next frontier is probably not “one more nearby clause”
- it is likely:
  - richer clause languages
  - deeper-state sampled repair
  - or proof-derived clauses

### Two-clause dominance language

Hypothesis:

- a deeper-lookahead second clause can improve out-of-domain sampled performance while preserving the exact bounded core

Current status:

- yes
- with core fixed to `(1,2,0,1,eq)`, the best safe repair in the targeted family is `(2,3,0,2,eq)`
- sampled lift:
  - `5x5`: `2998 -> 2999`
  - `6x6`: `895 -> 898`

Next ideas:

- search three-clause languages
- score repairs on sampled deeper states, not only roots
- derive the second clause from Bellman residual structure instead of failure mining

### Third-clause tie-break frontier

Hypothesis:

- one more local tie-break clause might close the last sampled larger-root misses without weakening the exact bounded two-clause core

Current status:

- bounded negative result
- within the tested single-clause tie-break family:
  - `184` clauses fixed at least one residual
  - many clauses fixed all `3` sampled residuals
  - `0` clauses fixed all `3` while preserving every exhaustive reachable nonterminal `4x4` state

Why this matters:

- the controller-language frontier is now real
- the next gain probably does not come from one more local threshold tweak
- it likely requires:
  - a richer clause language
  - a short repair program
  - or a Bellman-derived residual guard

Next ideas:

- synthesize short repair programs over clause languages with CEGIS
- search richer controller languages than one extra clause
- derive residual guards from Bellman differences instead of residual mining

### Repair-program CEGIS frontier

Hypothesis:

- once single local clauses saturate, the next useful object is a short repair program over the clause language

Current status:

- survived on the bounded model
- the banked CEGIS loop found a safe ordered pair after two exhaustive `4x4` counterexamples:
  - iteration `1`: `7104` viable pairs
  - iteration `2`: `1152`
  - iteration `3`: `576`, safe pair found

Why this matters:

- this is a better neuro-symbolic loop shape than plain controller search
- the verifier is teaching a repair language by emitting bounded counterexample states
- the existential side is searching over short programs, not only over direct controller objects

Boundary learned:

- the lexicographically simplest safe pair generalized worse than `v10`
- so the next frontier is not “does a safe repair program exist?”
- it is:
  - how to rank safe repair programs
  - how to inject larger-domain signals without weakening the exact bounded core

Next ideas:

- add an explicit larger-domain ranking objective to the repair-program loop
- search Bellman-derived ranking signals for safe repair programs
- learn a residual guard that decides when the repair program should fire

### Shared-bank multi-proposer frontier

Hypothesis:

- multiple proposers should help only if they contribute ranking diversity under a shared counterexample bank

Current status:

- survived on the bounded repair-program search
- best single proposer:
  - `childsum`
  - safe repair program in `2` exact verifier calls
  - bank size `1`
- best two-proposer portfolio:
  - `childsum + aggressive`
  - same safe repair program
  - `3` exact verifier calls
  - `2` rounds
  - bank size `2`

Why this matters:

- it makes the scaling law more precise
- proposer multiplicity alone is not the leverage
- diversity plus shared falsification is the leverage

Next ideas:

- rank proposers by expected verifier savings, not raw diversity
- assign proposers to obligation fibers instead of generic ranking rules
- turn the bounded result into an MPRD-facing formula for verified progress per second

### Bank-then-rank frontier

Hypothesis:

- once the bounded counterexample bank is strong enough, larger-domain ranking can be applied after safety pruning rather than mixed into the search from the start

Current status:

- survived on the bounded repair-program search
- after the `v12` bank, the viable frontier had size `576`
- the top larger-domain ranked viable pair was already exact-safe on the exhaustive reachable nonterminal `4x4` verifier

Why this matters:

- it gives the cleanest staged loop so far:
  - learn bank
  - rank viable frontier
  - certify top candidate
- it shows safety synthesis and value ranking can separate once the bank is informative enough

Boundary learned:

- the staged loop did not improve holdout value beyond the best safe repairs already known
- so the next gain likely comes from:
  - better bank construction
  - obligation-partitioned proposers
  - or better value signals before the bank is complete

Next ideas:

- search for bank-building policies that improve the viable frontier quality
- partition proposers by obligation fibers before ranking
- test staged loops in MPRD-like settings

### Minimal-bank synthesis frontier

Hypothesis:

- the staged loop may need fewer bounded counterexamples than the discovered `v12` bank, possibly even none for the eventual winner

Current status:

- survived, with a stronger-than-expected correction
- exact bounded result:
  - residual-consistent frontier size: `7104`
  - unique bounded verifier pattern count: `4263`
  - first safe rank without any bank: `1`
  - minimal teaching bank size for the winner: `0`

Why this matters:

- the bank is not the essential object for top-`1` winner selection in this bounded model
- the top ranked residual-consistent repair program is already safe
- this simplifies the current best loop shape

Next ideas:

- top-`k` teaching banks rather than top-`1`
- bank value under alternative objectives
- fiber-specialized proposers before residual consistency

### Obligation-fiber proposer frontier

Hypothesis:

- specialization by obligation fiber might reduce exact-safe discovery calls

Current status:

- falsified for the current top-`1` objective
- once the global frontier already returns a safe winner at call `1`, no specialization can strictly improve that objective

Why this matters:

- it closes one tempting but now-unproductive branch
- future specialization work should be about:
  - top-`k` diversity
  - alternative objectives
  - or proposal shaping before the frontier is formed

### Winner-certificate language frontier

Hypothesis:

- the safe winner might admit a small exact certificate inside the residual-consistent frontier

Current status:

- survived
- exact bounded result:
  - `17` available atomic winner-features
  - no exact certificate of size `≤ 5`
  - exact certificates exist at size `6`
  - `3` minimal certificates found

Why this matters:

- it is the first real certificate-language object in the current loop family
- it converts the safe winner into a compact explanatory artifact

Next ideas:

- region certificates, not only winner certificates
- certificate languages that imply safety for multiple repair programs

### Safe-region certificate frontier

Hypothesis:

- a small conjunction of winner-feature atoms might certify a whole safe region, not only the winner

Current status:

- survived, strongly
- exact bounded result:
  - safe subset size: `288`
  - size-`1` region certificates exist
  - each certifies the entire safe top block

Why this matters:

- the loop now has a clean two-level certificate story:
  - region certificate is simple
  - winner certificate is harder

Next ideas:

- search lower-ranked safe strata
- explain why top score and safety coincide here
- try to port region-certificate search to MPRD-style policy classes

### Score-safety collapse frontier

Hypothesis:

- inside the residual-consistent frontier, exact safety may coincide with maximizing one sampled score

Current status:

- survived strongly
- exact bounded result:
  - `Safe(x) <-> holdout_total(x) = 3821`
  - and equivalently for the `5x5` and `6x6` score coordinates

Why this matters:

- the loop now has a scalar-collapse layer
- after residual consistency, the universal property is described by a one-dimensional argmax set

Next ideas:

- explain the collapse structurally
- search anti-certificates for the next unsafe stratum

### Score-block staircase frontier

Hypothesis:

- the next unsafe strata may also be simple, with one dominant refuter per block

Current status:

- survived strongly
- exact bounded result:
  - all `10` score blocks are pure
  - each lower block has a single shared first refuter

Why this matters:

- the frontier has a staircase geometry, not just one safe top block
- this suggests a deeper quotient or anti-certificate structure

Next ideas:

- derive the staircase from the controller language
- or test whether the same staircase appears in nearby bounded domains

### Scalar refuter quotient frontier

Hypothesis:

- the full first-refuter label might be an exact function of one sampled score coordinate

Current status:

- survived for:
  - `holdout_total`
  - `holdout_5_hits`
- failed for:
  - `holdout_6_hits`

Why this matters:

- the frontier admits a one-dimensional quotient for the full refuter partition
- but not every score coordinate supports that quotient

Next ideas:

- characterize the `holdout_6_hits = 859` mixed bucket
- search the smallest two-coordinate quotient that repairs it

### Arithmetic refuter logic frontier

Hypothesis:

- the exact scalar quotients may admit a tiny arithmetic decision list, not only a lookup table over score blocks

Current status:

- survived strongly for:
  - `holdout_total`
  - `holdout_5_hits`
- failed for:
  - `holdout_6_hits`, because `859` is still mixed

Why this matters:

- it compresses the full refuter partition into short bounded formulas
- it suggests the staircase has an arithmetic presentation, not only a descriptive one

Next ideas:

- explain the origin of the moduli `23` and `17`
- search the smallest second coordinate that separates the mixed `859` bucket

### Mixed-bucket repair frontier

Hypothesis:

- the `holdout_6_hits = 859` collision might be repaired by one small second coordinate rather than a large multi-feature quotient

Current status:

- survived strongly
- exact bounded result:
  - `E(x) := p1_4(x) = p2_4(x)` repairs the mixed bucket exactly
  - `(holdout_6_hits, E)` is an exact quotient for the full refuter partition

Why this matters:

- it turns the scalar failure into a local repair law
- it suggests a generic quotient-and-repair loop pattern

Next ideas:

- compile the repaired quotient into the smallest exact verifier logic

### Repaired verifier compiler frontier

Hypothesis:

- once the quotient is repaired, the verifier side may compile to a very small exact decision list

Current status:

- survived strongly
- exact bounded result:
  - the repaired quotient compiles to a `4`-guard exact decision list

Why this matters:

- this is the strongest bounded version of the verifier-compiler idea so far
- it suggests a standalone tutorial object, not just another subsection

Next ideas:

- explain the `4`-guard compiler conceptually
- or test whether the same quotient-and-compiler pattern appears in an MPRD-like bounded policy space

### Verifier compiler lower-bound frontier

Hypothesis:

- the repaired verifier compiler may already be minimal in the searched guard language

Current status:

- survived strongly
- exact bounded result:
  - no exact compiler with `3` guards or fewer exists
  - the `4`-guard compiler is minimal

Why this matters:

- the verifier-compiler loop now has an exact lower-bound witness, not only a discovered upper bound

Next ideas:

- transfer the same quotient-and-repair compiler pattern into a broader bounded policy space

### MPRD transfer boundary frontier

Hypothesis:

- the verifier-compiler pattern might transfer cheaply to a toy MPRD policy family

Current status:

- survived as a negative boundary
- exact bounded result:
  - no exact repair with `1`, `2`, or `3` simple behavior features
  - first exact repair at `4` predicted-action features

Why this matters:

- it prevents overgeneralizing from the abstract frontier
- it suggests that transfer needs domain-shaped feature design, not just generic reuse

Next ideas:

- search semantically structured repair features for the MPRD case
- or teach the positive and negative boundary together in a standalone verifier-compiler tutorial

### MPRD semantic repair frontier

Hypothesis:

- even if cheap transfer fails, the first exact repair may still have a semantic basis rather than an opaque one

Current status:

- survived strongly
- exact bounded result:
  - first exact semantic repair at `4` mistake-indicator bits

Why this matters:

- it makes the transfer boundary teachable
- it suggests the MPRD case may need semantic feature design rather than generic feature search

Next ideas:

- search for a smaller semantic quotient over those four mistake bits
- or turn the whole verifier-compiler story into a standalone tutorial with explicit boundaries

### Earliest-error compiler frontier

Hypothesis:

- the MPRD semantic repair basis may itself collapse to an earliest-error law

Current status:

- survived strongly
- exact bounded result:
  - earliest holdout error gives the full first-refuter label
  - `holdout score + any 4 of 5 ordered error bits` is exact
  - no searched `holdout score + 3-bit` basis is exact

Why this matters:

- the transfer case now has a genuine compiler law, not only a feature-repair boundary
- it makes the MPRD negative boundary more constructive

Next ideas:

- teach the positive abstract compiler and the higher-dimensional MPRD compiler together
- or search for a second bounded MPRD family to test whether earliest-error structure is common

### Monotone refill transfer frontier

Hypothesis:

- a second MPRD-shaped domain may reveal a much higher transfer cost than the earlier lab-followup toy

Current status:

- survived strongly
- exact bounded result:
  - no exact semantic repair with `5` holdout error bits or fewer
  - first exact semantic basis at `6` holdout error bits

Why this matters:

- it shows the verifier-compiler loop has domain-sensitive compression cost
- it strengthens the case for teaching transfer boundaries explicitly

Next ideas:

- stop searching and turn the full loop family into its own tutorial
- or search one last semantically stronger feature family for the refill case

### Horn-closed refill basis frontier

Hypothesis:

- the exact 6-bit monotone refill basis from `v29` may shrink once exact Horn implications among the holdout error bits are allowed

Current status:

- survived as a negative boundary
- exact bounded result:
  - the same 6-bit basis remains minimal
  - its Horn closure reaches `11` of `13` error bits
  - the only non-derivable bits are `5` and `11`
  - no Horn-closed basis of size `5` or less is exact

Why this matters:

- it shows that logical implication closure and classifier compression come apart
- it keeps the refill transfer frontier honest

Next ideas:

- test whether all six retained bits are essential
- or extract a formula-level explanation for the two non-derivable bits

### Irredundant refill Horn basis frontier

Hypothesis:

- even if Horn closure does not shrink the refill basis, some retained bits may still be redundant for exact first-refuter classification

Current status:

- survived strongly
- exact bounded result:
  - the 6-bit Horn-closed basis is irredundant
  - dropping any retained bit destroys exactness
  - the non-derivable bits `5` and `11` are not required for exact labels, although they can split already-pure buckets

Why this matters:

- it gives the transfer boundary a cleaner logic shape
- the refill case is no longer just “expensive”
- it now has an essential basis and a separate set of logically independent but classifier-unnecessary bits

Next ideas:

- write this up as formulas in the tutorial
- or stop discovery and promote the verifier-compiler loop with the transfer boundary explained

### Ordered refill basis compiler frontier

Hypothesis:

- the six essential refill basis bits may still admit an ordered truncated compiler law, even though cheap quotient repair failed

Current status:

- survived strongly
- exact bounded result:
  - no order is exact with the first `3` active basis bits
  - some orders are exact with the first `4` active basis bits
  - every order is exact with the first `5` active basis bits

Why this matters:

- it gives the refill frontier a positive ordered-compiler object, not only a transfer-cost boundary
- it suggests a stronger tutorial arc:
  - tiny quotient compiler
  - higher-dimensional earliest-error compiler
  - irredundant ordered-basis compiler

Next ideas:

- explain the `k=5` order-invariance law
- or stop the search and promote the verifier-compiler tutorial with this stronger transfer-side result

### k4 refill order law frontier

Hypothesis:

- the `k=4` exact orders in the monotone refill compiler frontier may admit a small exact structural criterion instead of remaining a case-by-case fact

Current status:

- survived strongly
- exact bounded result:
  - the full `k=4` exactness split over all `720` orders is captured by a two-case structural law

Why this matters:

- it upgrades the refill compiler from a numerical fact to a symbolic one
- it strengthens the case that verifier-compiler loops can produce formula-level objects even in harder transfer domains

Next ideas:

- stop the search and write the standalone verifier-compiler tutorial
- or test whether another transfer family also admits an exact order law

### Regional refill ladder frontier

Hypothesis:

- the hard monotone refill transfer domain may admit a nonuniform explanation ladder even if no single cheap global language works everywhere

Current status:

- survived strongly
- exact bounded result:
  - the best shared-order regional ladder has weighted cost `118`, average depth `118 / 130`, and maximum depth `4`
  - no exact regional ladder exists with maximum depth `3`
  - this is far cheaper than global exact depth `4` or `5`

Why this matters:

- it is the first clean exact survivor for the explanatory-ladder idea
- it answers the “special use case” objection directly:
  - the verifier compiler can be one rung of a broader adaptive loop

Next ideas:

- run witness-language discovery on an existing bounded frontier
- or test whether another family also admits a strong regional ladder

### Mixed-sign label language frontier

Hypothesis:

- exact explanation may be cheaper when some labels are certified positively and one label is treated as the residual negative class

Current status:

- survived strongly
- exact bounded result:
  - all-positive certificate cover cost `7`
  - best mixed-sign language cost `4`
  - optimal split:
    - positive for `safe`, `fail_13116`, `fail_1915`
    - residual default for `fail_828`

Why this matters:

- it is the first real bounded support for the dual-language idea
- it shows that “explain everything positively” is not always the cheapest exact language

Next ideas:

- search for explicit negative witness objects instead of only a residual default
- or move to a harder witness-language discovery experiment beyond the repaired verifier frontier

### Primitive-invention label frontier

Hypothesis:

- exact concept invention may reduce explanation cost even when the fixed language seems already well-understood

Current status:

- survived strongly
- exact bounded result:
  - one invented primitive lowers all-positive cost from `7` to `5`
  - two invented primitives lower it from `7` to `4`, matching the mixed-sign optimum from `v35`

Why this matters:

- this is the first real bounded support for the primitive-invention and concept-market direction
- it shows that some of the apparent advantage of mixed-sign languages can disappear once the positive language is allowed to invent better concepts

Next ideas:

- run primitive invention on a harder frontier where the best new primitives are not obvious unions
- or combine invented positive primitives with explicit negative refuters in the next dual-language cycle

### Refill concept-market frontier

Hypothesis:

- the hard monotone refill ladder from `v34` may still admit useful exact concept invention, but the useful concepts may have to sit on top of the old basis instead of replacing it

Current status:

- survived strongly
- exact bounded result:
  - best fixed-order shortcut concept:
    - `err[10] AND err[12]`
    - inserted before `err[10]`
  - weighted cost drops from `118` to `90`
  - maximum depth drops from `4` to `3`
  - no searched single-concept replacement language is exact at all

Why this matters:

- this is the first hard-frontier evidence for the concept-market idea
- it sharpens the theory:
  - concept invention can help without collapsing the old language
  - shortcut concepts and replacement concepts are different objects

Next ideas:

- search whether two shortcut concepts lower the hard ladder further
- or move to witness-language discovery, since local one-concept replacement is now a bounded dead end

### Refill two-concept ladder frontier

Hypothesis:

- the hard monotone refill ladder may admit stacked shortcut concepts that lower the exact ladder again, even if one shortcut cannot replace the old basis

Current status:

- survived strongly
- exact bounded result:
  - best pair:
    - `err[6] AND err[10] AND err[12]`
    - `err[9] AND err[10] AND err[12]`
  - weighted cost drops to `80`
  - maximum depth drops to `2`
  - no exact pair in the searched grammar reaches max depth `1`

Why this matters:

- hard-frontier concept invention is not only a one-step shortcut phenomenon
- the concept-market direction can stack under exact bounded pressure
- but the stacking still sits on top of the old basis instead of replacing it

Next ideas:

- test whether a third shortcut breaks the max-depth-2 barrier
- or stop local shortcut search and move to witness-language discovery

### Anchored third-shortcut boundary frontier

Hypothesis:

- the best exact two-shortcut refill ladder from `v38` may already be locally saturated on weighted cost and max depth under one more simple pure shortcut

Current status:

- survived strongly
- exact bounded result:
  - no searched anchored third shortcut lowers weighted cost below `80`
  - no searched anchored third shortcut lowers max depth below `2`
  - best extra shortcut:
    - `err[3] OR err[6] OR err[8]`
    - keeps cost `80` and max depth `2`
    - lowers bucket total from `51` to `48`

Why this matters:

- the local hard-frontier concept line now has a clear saturation signal
- minor internal compression is still available
- but the main ladder metrics do not improve in the searched anchored grammar

Next ideas:

- global three-shortcut search if more local concept pressure is still wanted
- otherwise move up one level to witness-language discovery

### Score-local witness frontier with residual defaults

Hypothesis:

- once the local hard-frontier shortcut line saturates, fixing the exact `v38` feature space may still support exact score-local witness languages with positive covers plus a residual default, and these may be cheaper than insisting on all-positive explanations

Current status:

- survived strongly
- exact bounded result:
  - every nontrivial score block admits an exact positive-cover plus residual-default witness language
  - total positive-cover-plus-residual cost is `27`
  - all-positive witness languages fail on score `9` and score `10`

Why this matters:

- this is the first hard-frontier witness-language result in the repo
- it confirms that moving up from shortcut tuning to language discovery is productive

Next ideas:

- search for a global witness language that composes the score-local ones
- or decide whether the global three-shortcut search is still worth running before moving further up the ladder

### Global witness-schema frontier

Hypothesis:

- the exact score-local positive-cover plus residual-default witnesses from `v40` may compress into a smaller reusable global witness-schema layer without increasing local cost

Current status:

- survived strongly
- exact bounded result:
  - local positive-cover-plus-residual cost stays `27`
  - best shared global schema count is `20`

Why this matters:

- this is the first genuine global witness-language object in the hard-frontier line
- it confirms that the move from local witness languages to global reuse is real

Next ideas:

- allow richer witness atoms or score abstractions and ask whether the shared schema library shrinks further
- or compare this global witness line directly against a global three-shortcut concept search

### Score-abstraction witness frontier

Hypothesis:

- the exact score-local witness languages from `v40` may admit a nontrivial exact score abstraction, not only a shared global schema layer

Current status:

- survived strongly
- exact bounded result:
  - best exact contiguous partition:
    - `(7)`, `(8)`, `(9)`, `(10,11)`, `(12)`
  - total positive-cover-plus-residual witness cost drops from `27` to `23`

Why this matters:

- the witness-language line now has both schema reuse and score abstraction
- it is no longer only a set of fixed local covers

Next ideas:

- allow richer witness atoms or non-contiguous score abstractions
- or compare the witness-language line directly against a global three-shortcut concept search

### Unconstrained score-abstraction boundary frontier

Hypothesis:

- the `v42` score abstraction may already be optimal even after the contiguity restriction is removed

Current status:

- survived strongly
- exact bounded result:
  - all `203` set partitions checked
  - only `10` are exact
  - the `v42` partition remains best with cost `23`

Why this matters:

- it turns the `v42` abstraction into a stronger bounded object
- the next likely leverage is richer witness grammars, not just more partition freedom

Next ideas:

- move to richer witness atoms
- or directly compare the witness-language line to a global three-shortcut concept search

### Richer witness-grammar frontier

Hypothesis:

- after `v43` saturates the score-partition axis, a richer exact witness-atom grammar may still lower the best hard-frontier witness cost

Current status:

- survived strongly
- exact bounded result:
  - the same best partition remains:
    - `(7)`, `(8)`, `(9)`, `(10,11)`, `(12)`
  - feasible partition count rises:
    - from `10`
    - to `15`
  - best total positive-cover-plus-residual witness cost drops:
    - from `23`
    - to `22`
  - the extra gain comes from the score-`9` region via:
    - `not err[3] and not err[6] and not err[8] and err[10]`

Why this matters:

- it separates the saturated axis from the still-live axis cleanly
- the partition geometry is stable, but the witness grammar was not yet exact-saturated

Next ideas:

- test whether a still richer grammar lowers cost again or only enlarges the exact feasible set
- or move up one level into more global witness-language synthesis

### Five-literal witness-grammar boundary frontier

Hypothesis:

- the `v44` gain may continue if the exact witness grammar grows from `1..4` to `1..5` signed literals

Current status:

- survived as a boundary
- exact bounded result:
  - feasible partition count stays `15`
  - best partition stays:
    - `(7)`, `(8)`, `(9)`, `(10,11)`, `(12)`
  - best total positive-cover-plus-residual witness cost stays `22`
  - only two non-best partitions improve by one unit each

Why this matters:

- it closes the local grammar axis on the main exact object
- the next honest gains need a more global witness object

Next ideas:

- search for a shared global witness-schema library above the exact `v44` partition
- or revisit local grammars only if a new objective makes the secondary improvements matter

### Global witness-synthesis frontier

Hypothesis:

- the exact `v44` partition may compress into a materially smaller shared global witness-schema library

Current status:

- survived strongly
- exact bounded result:
  - raw local region cost is `22`
  - best shared global schema count is `19`

Why this matters:

- this is the first more-global witness object above the best hard-frontier score abstraction
- it confirms that the next real compression axis is global witness sharing, not more local partition tweaking

Next ideas:

- allow a richer witness grammar and ask whether the global schema library shrinks further
- or search for reusable witness templates across multiple bounded frontiers

### Global witness-synthesis grammar boundary frontier

Hypothesis:

- the more-global witness object from `v46` may still improve when the atom grammar grows from `1..4` to `1..5` signed literals

Current status:

- survived as a boundary
- exact bounded result:
  - total region cost stays `22`
  - best shared global schema count stays `19`

Why this matters:

- it closes the nearby global grammar axis on the main metric
- the next honest move is a stronger loop family or a new abstraction, not one more literal

Next ideas:

- search for reusable witness templates across multiple bounded frontiers
- or shift to a stronger loop family such as certificate-language or explanation-fiber discovery

### Cross-frontier witness-template frontier

Hypothesis:

- multiple exact witness-schema frontiers may collapse into a smaller shared template language above their raw formulas

Current status:

- survived strongly
- exact bounded result:
  - raw formula union across `v41` and `v46` is `22`
  - exact overlap is `17`
  - untyped conjunction-shape templates drop that to `10`
  - typed templates keeping feature kind give `13`

Why this matters:

- it is the first more-global object above multiple exact frontiers
- it gives a sharper next vision than “one more literal”

Next ideas:

- search for reusable witness templates across more exact frontiers
- or jump to a stronger family if the template line saturates too quickly

### Cross-frontier core-plus-patch frontier

Hypothesis:

- the cross-frontier template result from `v48` may sharpen into a shared exact core plus a small patch language

Current status:

- survived strongly
- exact bounded result:
  - shared exact core is `17`
  - `v41` contributes `3` frontier-only patch schemas
  - `v46` contributes `2` frontier-only patch schemas
  - the `5` residual patches are template-irreducible in the current conjunction-shape grammar

Why this matters:

- it turns the template line into a cleaner compiler shape
- it also shows exactly where the syntax-only version saturates

Next ideas:

- move to semantic patch languages
- or jump to certificate-language / explanation-fiber discovery

### Typed semantic-patch frontier

Hypothesis:

- the residual patch language from `v49` may compress once patches are described by typed edits over the shared exact core rather than by syntax-only templates

Current status:

- survived strongly
- exact bounded result:
  - nearest-core attachment uses `5` signatures for `5` patches
  - typed edit-signature search lowers that to `4`
  - best total edit cost is `15`

Why this matters:

- it reopens the frontier after the syntax-only template boundary
- it suggests the next stronger loop may really be semantic patching

Next ideas:

- search richer semantic patch languages
- or compare this line directly against certificate-language and explanation-fiber loops

### Semantic macro-family frontier

Hypothesis:

- the residual semantic-patch line may collapse to a very small exact semantic macro basis

Current status:

- survived strongly
- exact bounded result:
  - all five residual patches are exactly scriptable using only:
    - `ADD_LITERAL`
    - `FLIP_SIGN`
  - no exact one-family solution exists
  - best total macro-instance count is `11`

Why this matters:

- it is the first exact semantic macro basis in this line
- it strengthens the case that the post-template frontier is really semantic patching

Next ideas:

- search richer semantic macro languages
- or compare this basis directly against certificate-language and explanation-fiber families

### Bundle semantic-macro frontier

Hypothesis:

- the exact semantic macro-family basis from `v51` may sharpen if same-family edits are bundled into one macro instance

Current status:

- survived strongly
- exact bounded result:
  - exact family subset:
    - `ADD_BUNDLE`
    - `FLIP_BUNDLE`
  - no exact one-family solution exists
  - best total macro-instance count drops:
    - from `11`
    - to `6`

Why this matters:

- it is the strongest current post-template object in the repo
- it shows the semantic patch line still has real headroom once bundling is allowed

Next ideas:

- test richer semantic macro languages
- or compare bundled semantic macros directly against certificate-language and explanation-fiber families

### Semantic fiber decomposition frontier

Hypothesis:

- the residual semantic patch language may decompose into mostly pure explanation fibers even if the global bundled basis remains mixed

Current status:

- survived strongly
- exact bounded result:
  - mixed patches `1`
  - mixed fibers `1`
  - total fibers `3`
  - best decomposition:
    - pure `FLIP_BUNDLE` fiber of size `3`
    - pure `ADD_BUNDLE` fiber of size `1`
    - mixed `ADD_BUNDLE + DROP_BUNDLE` singleton fiber of size `1`

Why this matters:

- it is the first exact bounded explanation-fiber object in this line
- it shows only one patch remains mixed under the searched bundled semantic macro language

Next ideas:

- enrich the bundled macro language and ask whether the last mixed singleton disappears
- or compare explanation fibers directly against certificate-language discovery

### Fiber-certificate frontier

Hypothesis:

- the exact `v53` explanation-fiber labels may admit a smaller exact certificate
  presentation over a tiny patch-summary feature set

Current status:

- survived strongly
- exact bounded result:
  - exact all-positive cost:
    - `3`
  - exact positive-cover plus residual-default cost:
    - `2`
  - winning residual-default language:
    - certify `ADD_BUNDLE + DROP_BUNDLE` by `has_drop`
    - certify `FLIP_BUNDLE` by `has_flip`
    - default `ADD_BUNDLE`

Why this matters:

- it shows the explanation-fiber object compresses one step further once the
  exact labels are fixed
- it is the cleanest certificate-side presentation of the `v53` line so far

Next ideas:

- remove dependence on the precomputed fiber labels,
- or compare certificates against a stronger direct symbolic compiler

### Direct delta-certificate frontier

Hypothesis:

- the same residual family split may be recoverable directly from symbolic
  patch-state deltas, without using the precomputed fiber labels as features

Current status:

- survived strongly
- exact bounded result:
  - exact all-positive cost:
    - `3`
  - exact positive-cover plus residual-default cost:
    - `2`
  - winning direct residual-default compiler:
    - certify `ADD_BUNDLE + DROP_BUNDLE` by `has_drop`
    - certify `FLIP_BUNDLE` by `has_flip`
    - default `ADD_BUNDLE`
- claim tier:
  - `symbolic_state_compiler`

Why this matters:

- this is the first point where the certificate line becomes a real bounded
  symbolic compiler instead of a relabeling result
- it sharpens the explanation-fiber branch without changing the bounded domain

Next ideas:

- test richer direct delta languages,
- or compare this compiler against certificate-language and explanation-fiber
  discovery on a larger residual family

### Direct delta basis frontier

Hypothesis:

- the exact `v55` direct symbolic compiler may survive on a smaller feature basis

Current status:

- survived strongly
- exact bounded result:
  - smallest exact all-positive basis size:
    - `2`
  - smallest exact positive-cover plus residual-default basis size:
    - `2`
  - exact minimal bases:
    - `has_add`, `has_drop`
    - `has_drop`, `has_flip`
  - no singleton basis is exact

Why this matters:

- it sharpens the direct symbolic compiler into a smaller exact object
- it identifies `has_drop` as the indispensable coordinate on this bounded
  residual domain

Next ideas:

- compare the two surviving minimal bases on a larger residual family,
- or search a richer direct delta language that resolves which second
  coordinate transfers better

### Raw edit-basis frontier

Hypothesis:

- the exact residual-family compiler may survive even after the aggregated
  delta coordinates are removed, using only raw observed edit primitives

Current status:

- survived strongly
- exact bounded result:
  - smallest exact all-positive primitive basis size:
    - `2`
  - smallest exact positive-cover plus residual-default primitive basis size:
    - `2`
  - no singleton primitive basis is exact
  - exact minimal all-positive bases:
    - `add[3]`, `add[8]`
    - `add[3]`, `drop[12]`
    - `add[6]`, `add[8]`
    - `add[6]`, `drop[12]`
    - `add[8]`, `add[10]`
    - `add[10]`, `drop[12]`

Why this matters:

- it shows the direct compiler is not leaning on hand-aggregated semantic
  coordinates
- it exposes a six-basis primitive family with a clean factorization:
  one add-anchor and one mixed-patch discriminator

Next ideas:

- compare the primitive-basis family against the aggregated-basis family on a
  larger residual set,
- or search whether richer raw primitive grammars collapse the six surviving
  bases to a smaller exact template family

### Primitive basis template frontier

Hypothesis:

- the six exact raw primitive bases from `v57` may collapse to a smaller exact
  role-template family

Current status:

- survived strongly
- exact bounded result:
  - one exact two-slot product template, unique up to slot swap
  - one slot:
    - `add[3]`, `add[6]`, `add[10]`
  - the other slot:
    - `add[8]`, `drop[12]`
  - the residual-default family is the same template crossed with all three
    default labels

Why this matters:

- it upgrades the raw primitive line from a small atlas to an exact role grammar
- it makes the six surviving bases structurally explainable

Next ideas:

- compare the aggregated and primitive template families on a larger residual
  set,
- or search whether the add-anchor slot and mixed-patch slot themselves admit a
  smaller exact semantic explanation

### Role-slot compiler frontier

Hypothesis:

- the exact `v58` role template may also compile the residual labels directly,
  not only the surviving primitive bases

Current status:

- survived strongly
- exact bounded result:
  - unique up to slot swap
  - slot `a`:
    - `add[3]`, `add[6]`, `add[10]`
  - slot `b`:
    - `add[8]`, `drop[12]`
  - exact all-positive compiler:
    - `ADD_BUNDLE` by `slot_a and not slot_b`
    - `ADD_BUNDLE + DROP_BUNDLE` by `slot_b`
    - `FLIP_BUNDLE` by `not slot_a`
  - exact positive-cover plus residual-default cost:
    - `2`

Why this matters:

- it upgrades the role-template object into a direct bounded symbolic compiler
- it is the sharpest current explanation of the residual-family line

Next ideas:

- compare the aggregated compiler and the slot compiler on a larger residual
  family,
- or search for a smaller exact semantic explanation of the two slots
  themselves

### Quotient boundary frontier

Hypothesis:

- the smallest exact slot quotient for direct label prediction may be strictly
  smaller than the smallest exact slot quotient that preserves the full
  primitive basis structure

Current status:

- survived strongly
- exact bounded result:
  - smallest `label_only` slot cost:
    - `2`
  - smallest `basis_faithful` slot cost:
    - `5`
  - minimal `label_only` family:
    - one add-anchor singleton from:
      - `add[3]`
      - `add[6]`
      - `add[10]`
    - one mixed discriminator singleton from:
      - `add[8]`
      - `drop[12]`
  - counts:
    - `6` unordered minimal label-only quotients
    - `12` ordered minimal label-only quotients

Why this matters:

- it cleanly separates two exact objectives in the same loop
- it shows why the structure-preserving compiler from `v59` should not be
  judged only by predictive compactness

Next ideas:

- test whether this predictive-versus-structure boundary persists on a larger
  residual family,
- or search for a semantic explanation of the recurring add-anchor and mixed
  discriminator roles

### Semantic slot frontier

Hypothesis:

- the exact `v59` slot roles may admit a small exact semantic explanation over
  primitive metadata

Current status:

- survived strongly
- exact bounded result:
  - smallest exact all-positive semantic basis size:
    - `2`
  - smallest exact positive-cover plus residual-default semantic basis size:
    - `2`
  - natural support-profile explanation:
    - feature basis:
      - `has_AB`
      - `has_MIX`
    - `slot_a` by `has_AB`
    - `slot_b` by `not has_AB and has_MIX`
    - `other` by `not has_MIX`

Why this matters:

- it is the first exact semantic explanation of the recurring slot roles
- it says the roles are support-profile objects, not only structural artifacts

Next ideas:

- test whether the same support-profile semantics persist on a larger residual
  family,
- or compare this semantic explanation layer against a larger transfer domain

### Shared role semantics frontier

Hypothesis:

- the same two-feature support-profile semantics may govern both the exact
  structure-preserving quotient and the exact minimal predictive quotients

Current status:

- survived strongly
- exact bounded result:
  - `ADD_ANCHOR` iff `has_AB`
  - `MIX_DISCRIM` iff `not has_AB and has_MIX`
  - `OTHER` iff `not has_MIX`
  - this partition exactly matches the `v59` slot roles
  - its singleton cross product exactly equals the unordered minimal
    `label_only` quotients from `v60`

Why this matters:

- it gives the branch a shared semantic control law
- it explains why the same add-anchor and mixed-discriminator roles keep
  reappearing across different exact objectives

Next ideas:

- test whether the same shared support-profile law persists on a larger
  residual family,
- or compare it against a larger transfer domain

### Support-signature transfer frontier

Hypothesis:

- the support-profile law from `v62` may transfer to a second exact frontier as
  a generic support-signature role law

Current status:

- survived strongly
- exact bounded result:
  - Domain A:
    - `CORE` by `has_v41 and has_v46`
    - `V41_PATCH` by `not has_v46`
    - `V46_PATCH` by `not has_v41`
  - Domain B:
    - `ADD_ANCHOR` by `has_AB`
    - `MIX_DISCRIM` by `not has_AB and has_MIX`
    - `OTHER` by `not has_MIX`

Why this matters:

- the support-profile law is not isolated to one residual-family branch
- it now looks like a generic support-signature role law

Next ideas:

- test whether the same support-signature law persists on a larger residual
  family or transfer domain,
- or search for a loop that discovers support-signature laws directly

### Support-literal compiler frontier

Hypothesis:

- the `v63` support-signature law may upgrade from a descriptive transfer result
  to a tiny exact compiler family

Current status:

- survived strongly
- exact bounded result:
  - Domain A, `v49` schema roles:
    - `V41_PATCH` by `not has_v46`
    - `V46_PATCH` by `not has_v41`
    - default `CORE`
  - Domain B, `v62` primitive roles:
    - `ADD_ANCHOR` by `has_AB`
    - `OTHER` by `not has_MIX`
    - default `MIX_DISCRIM`
  - Domain C, `v55` direct patch-delta roles:
    - `ADD_BUNDLE+DROP_BUNDLE` by `has_drop`
    - `FLIP_BUNDLE` by `has_flip`
    - default `ADD_BUNDLE`
  - no exact single-branch support compiler exists on any domain
  - all three domains admit an exact residual-default support compiler with:
    - branch count `2`
    - total literal cost `2`

Why this matters:

- the support-signature branch now has a tiny exact compiler family, not only a
  recurring semantic law
- it is the cleanest cross-frontier compiler object in the current branch

Next ideas:

- test whether the same support-literal family survives on a larger transfer
  domain with a compatible support surface,
- or search for a loop that discovers support-literal compilers directly from
  role tables

### Three-signature support law frontier

Hypothesis:

- the `v64` support-literal family may be a generic law of small support tables,
  not only a three-domain pattern

Current status:

- survived strongly
- exact bounded result:
  - every labeled `3`-role support table with one distinct realized signature
    per role in widths `2` through `7` admits:
    - an exact residual-default compiler with `2` branches and `2` single
      literals total
    - an equivalent private-literal star witness
  - exact counts:
    - width `2`: `24 / 24`
    - width `3`: `336 / 336`
    - width `4`: `3360 / 3360`
    - width `5`: `29760 / 29760`
    - width `6`: `249984 / 249984`
    - width `7`: `2048256 / 2048256`

Why this matters:

- the support-literal line is now a bounded support-table law candidate for the
  full `3`-role case
- it is stronger than a finite family pattern and sharper than the earlier
  transfer framing

Next ideas:

- move to the first `4`-role support-table failure family,
- or search for the smallest exact compiler law that survives before the first
  `4`-role obstruction

### Four-role support cost frontier

Hypothesis:

- the first `4`-role support-table case may replace the `3`-role law with an
  exact bounded cost ladder

Current status:

- survived strongly
- exact bounded result:
  - width `2`:
    - `24 / 24` labeled tables
    - single-literal star count `0`
    - all require total literal cost `6`
  - width `3`:
    - `1680` labeled tables
    - single-literal star count `192`
    - exact minimal total-literal-cost ladder:
      - cost `3`: `192`
      - cost `4`: `576`
      - cost `5`: `576`
      - cost `6`: `336`

Why this matters:

- it is the first honest extension beyond the `3`-role support law
- the `4`-role regime is already a real cost hierarchy, not just an isolated
  obstruction

Next ideas:

- classify the width-`3` ladder geometrically,
- or move to width `4` and search for the first new cost beyond `6`

### Width3 four-role geometry frontier

Hypothesis:

- the width-`3` `4`-role cost ladder may collapse to a small exact geometry
  atlas under cube automorphisms

Current status:

- survived strongly
- exact bounded result:
  - exactly `6` orbit classes
  - every orbit has a uniform exact compiler cost
  - atlas:
    - claw orbit `(0,1,2,4)`, cost `3`
    - path orbit `(0,1,2,5)`, cost `4`
    - vee-plus-isolated orbit `(0,1,2,7)`, cost `5`
    - square orbit `(0,1,2,3)`, cost `6`
    - disjoint-edge orbit `(0,1,6,7)`, cost `6`
    - independent orbit `(0,3,5,6)`, cost `6`

Why this matters:

- the first `4`-role cost hierarchy is now structural, not only numeric
- it is the cleanest object yet above the `v66` histogram

Next ideas:

- move to width `4` and search for the first new cost beyond `6`,
- or search for a small invariant family that predicts the orbit cost directly

### Width3 invariant law frontier

Hypothesis:

- the `v67` six-orbit atlas may admit a much smaller exact invariant law

Current status:

- survived strongly
- exact bounded result:
  - `degree_sequence` is already an exact singleton invariant
  - but among the searched scalar invariants, no singleton is exact
  - the simplest exact scalar basis found is:
    - `(edge_count, max_degree)`
  - exact scalar law:
    - `(3,3) -> 3`
    - `(3,2) -> 4`
    - `(2,2) -> 5`
    - otherwise `-> 6`

Why this matters:

- the width-`3` `4`-role frontier now has a real invariant law above the atlas
- it is the cleanest compression step after the orbit quotient

Next ideas:

- move to width `4` and search for the first new cost beyond `6`,
- or test whether a similarly small scalar law survives there

### Width4 support-profile frontier

Hypothesis:

- the width-`4` `4`-role cost histogram may already collapse to a small exact
  law over the per-role minimal unique-support profile

Current status:

- survived strongly
- exact bounded result:
  - only `6` sorted profiles occur:
    - `(1,1,1,1)`
    - `(1,1,1,2)`
    - `(1,1,1,3)`
    - `(1,1,2,2)`
    - `(1,2,2,2)`
    - `(2,2,2,2)`
  - exact counts:
    - `384`
    - `4608`
    - `3840`
    - `18432`
    - `13056`
    - `3360`
  - exact minimal compiler cost is:
    - the sum of the three smallest profile entries

Why this matters:

- width `4` already has a clean exact law, not only a wider histogram
- this is the first convincing structural object above the width-`3`
  scalar-invariant frontier

Next ideas:

- search for a smaller scalar or geometric law above the profile law,
- classify which width-`4` tables realize each of the six profiles,
- or find the first width-`4` phenomenon that escapes the current profile law

### Width4 support-count law frontier

Hypothesis:

- the width-`4` six-profile law may collapse again, with exact cost determined
  by a single profile-derived scalar

Current status:

- survived strongly
- exact bounded result:
  - exact cost is determined by:
    - `count_private_roles`
  - exact law:
    - `4 -> 3`
    - `3 -> 3`
    - `2 -> 4`
    - `1 -> 5`
    - `0 -> 6`

Why this matters:

- the width-`4` frontier is more structured than the raw six-profile summary
- exact control now has a one-scalar law

Next ideas:

- search whether the full profile also collapses to a tiny basis,
- or move to the width-`4` orbit space and ask whether geometry preserves the
  same private-role-count control law

### Width4 profile-pair law frontier

Hypothesis:

- although exact cost may need only one scalar, exact reconstruction of the
  six-profile width-`4` law may need a second one

Current status:

- survived strongly
- exact bounded result:
  - no searched singleton scalar reconstructs the full profile
  - the pair:
    - `count_private_roles`
    - `max_support_size`
    reconstructs it exactly

Why this matters:

- the width-`4` line now has a clean split:
  - one-scalar control
  - two-scalar structure

Next ideas:

- move to the width-`4` orbit space and test whether the same two-scalar law
  survives there,
- or search for the first genuine geometric obstruction not captured by these
  two support-count coordinates

### Width4 orbit support-count transfer frontier

Hypothesis:

- the width-`4` support-count laws may survive unchanged after passing from the
  labeled-table frontier to the unlabeled orbit frontier

Current status:

- survived strongly
- exact bounded result:
  - exact orbit cost is still determined by:
    - `count_private_roles`
  - exact orbit profile is still reconstructed by:
    - `count_private_roles`
    - `max_support_size`

Why this matters:

- the support-count line is not a one-presentation trick
- it survives across two bounded presentations of the same family

Next ideas:

- identify the first width-`4` geometric obstruction not already captured by
  these support-count laws,
- or search for a smaller orbit-side law above the current transfer object

### Width4 orbit mixed-basis frontier

Hypothesis:

- once support counts stop being enough for full orbit reconstruction, the
  missing information may still collapse to one tiny geometric basis object

Current status:

- survived strongly
- exact bounded result:
  - support counts alone do not determine orbit class
  - no searched singleton mixed basis is exact
  - the first exact mixed bases are:
    - `count_private_roles` plus `distance_multiset`
    - `count_size2_roles` plus `distance_multiset`

Why this matters:

- this is the first genuine width-`4` geometric obstruction after the transfer
  result
- it is still small enough to be treated as a bounded compiler object

Next ideas:

- scalarize the mixed basis if possible,
- or search for the first width-`4` orbit feature not already captured by
  support counts plus distance multiset

### Width4 orbit scalarized mixed-law frontier

Hypothesis:

- the first exact mixed orbit basis may still collapse to a tiny scalar
  support-plus-geometry law

Current status:

- survived strongly
- exact bounded result:
  - no searched singleton scalar is exact
  - no searched scalar pair is exact
  - exact scalar triples do exist
  - preferred exact triple:
    - `count_private_roles`
    - `max_degree`
    - `diameter`

Why this matters:

- the first genuine width-`4` geometric obstruction still compresses to a tiny
  scalar law
- the branch now has a very sharp mixed support-plus-geometry control object

Next ideas:

- test whether this three-scalar law is minimal in a broader feature library,
- or find the first width-`4` phenomenon that escapes it

### Width4 broad-scalar minimality frontier

Hypothesis:

- the `v74` three-scalar orbit law may remain minimal even after widening the
  scalar support-plus-geometry library substantially

Current status:

- survived strongly
- exact bounded result:
  - widened scalar feature count:
    - `21`
  - no searched singleton scalar is exact
  - no searched scalar pair is exact
  - exact scalar triples do exist
  - preferred exact triple remains:
    - `count_private_roles`
    - `max_degree`
    - `diameter`

Why this matters:

- the current three-scalar law is robust, not an artifact of a narrow search

Next ideas:

- search for the first width-`4` phenomenon that escapes the current
  three-scalar law,
- or prove stronger minimality in an even wider invariant library

### Width4 mixed-basis uniqueness frontier

Hypothesis:

- the `v73` mixed basis may actually be rigid, with distance multiset as the
  unique useful geometry summary in the searched tuple-aware library

Current status:

- survived strongly
- exact bounded result:
  - the only nontrivial exact pair bases are:
    - `count_private_roles` plus `distance_multiset`
    - `count_size2_roles` plus `distance_multiset`

Why this matters:

- the first width-`4` obstruction is not only small
- it is also rigid in the searched mixed basis space

Next ideas:

- search for the first width-`4` orbit feature that escapes both:
  - the current three-scalar law
  - the current rigid mixed basis family

### Minimal witness-language discovery frontier

Hypothesis:

- the deeper object is often not only the witness or the compiler
- it is the smallest exact language in which local witnessing is allowed

Current status:

- first bounded survivor now exists on the repaired `10`-state verifier
  frontier
- exact compared families:
  - pure positive atom covers
  - mixed residual-default atom covers
  - invented positive covers
  - ordered decision-list compiler
- exact phase diagram:
  - smallest all-positive unordered language:
    - invented positive-cover family
    - cost `4`
  - smallest unordered residual-default language:
    - mixed atom-cover family
    - cost `4`
  - smallest ordered exact classifier:
    - decision-list compiler
    - guard count `4`

Why this matters:

- this is the first explicit bounded evidence that verifier compilation is one
  child of a larger exact language-selection problem
- the answer to "best exact language" depends on the local witness contract

Next ideas:

- search over a larger bounded family of witness languages directly
- repeat the same phase-diagram comparison on a harder frontier
- test whether some frontiers favor certificate languages or decomposition
  languages over compilers and positive covers

Current refinement:

- the harder refill witness frontier no longer gives only a tie among exact
  families
- it yields a strict ladder:
  - score-local residual-default witnesses:
    - `27`
  - merged-region residual-default witnesses:
    - `22`
  - shared global witness-schema language:
    - `19`
- local all-positive witnesses already fail on:
  - `9`
  - `10`

New next ideas:

- search directly over a wider bounded witness-language grammar on the hard
  frontier
- compare witness-cover languages against certificate languages on one shared
  bounded corpus
- compare witness-cover languages against decomposition languages on one shared
  bounded corpus

New boundary learned:

- on the same hard merged-region frontier, exact bit-fiber decomposition is
  available but worse than the current label-level witness language:
  - total cost:
    - `24` vs `22`
  - shared schema count:
    - `21` vs `19`

Refined next ideas:

- compare witness-cover languages against certificate languages on the same hard
  frontier
- search richer decomposition languages that are not limited to raw label bits

Current refinement:

- the first hard certificate comparison now survives as a strict boundary
- in the searched `1..4` literal conjunction grammar, exact all-positive
  certificates already fail on:
  - `(10,11)`
- even on the feasible regions they are still larger:
  - certificate cost:
    - `23`
  - shared schemas:
    - `21`

New next ideas:

- search richer certificate languages on the same hard frontier
- test certificate languages that allow a small amount of local residual
  structure

Current refinement:

- the hard certificate comparison now sharpens into a residual-budget ladder on
  the same partition
- exactness returns as soon as one region is allowed residual-default
  witnessing
- that first residual region is forced:
  - `(10,11)`
- best exact total cost then drops strictly with residual budget:
  - `1`:
    - `28`
  - `2`:
    - `26`
  - `3`:
    - `24`
  - `4`:
    - `23`
  - `5`:
    - `22`

Why this matters:

- residual structure on the hard frontier is locally budgetable
- the right object is now more precise than "certificate versus witness"
- it is an exact residual-budgeted witness language

New next ideas:

- compare this local ladder against a more global shared-schema optimization
- search richer certificate grammars with local residual structure

Current refinement:

- the same hard residual-budget ladder survives after switching to a global
  shared-schema objective
- exact shared-schema count by residual budget is:
  - `1`:
    - `25`
  - `2`:
    - `23`
  - `3`:
    - `21`
  - `4`:
    - `20`
  - `5`:
    - `19`
- every feasible rung improves by exactly `1` schema relative to `v81`
- the full-budget endpoint recovers the earlier `v46` global optimum

Why this matters:

- the hard residual-budget story is now global, not only local
- schema sharing remains a live source of compression even after the budget
  ladder is known

New next ideas:

- search richer certificate grammars with local residual structure on the same
  hard frontier
- test whether a comparable global residual-budget law survives on a second
  hard frontier

Current refinement:

- the hard residual-budget law was still overconditioned on the fixed `v44`
  partition
- once score partition and residual structure are searched jointly, the best
  shared-schema ladder becomes:
  - `1`:
    - `24`
  - `2`:
    - `22`
  - `3`:
    - `20`
  - `4`:
    - `19`
  - `5`:
    - `19`
- exact total cost stays:
  - `28`
  - `26`
  - `24`
  - `23`
  - `22`
- low budgets prefer merged score regions:
  - `(7,12)`
  - `(9,10)`

Why this matters:

- the hard-frontier object is now partition-aware, not only budget-aware
- the earlier fixed partition was informative but not globally optimal under
  the stronger schema objective

New next ideas:

- test the same joint search in a richer certificate grammar
- transfer the same partition-aware residual-budget search to a second hard
  frontier

Current refinement:

- the hard-frontier certificate ceiling is partly grammatical rather than
  uniformly logical
- on the exact union of score regions appearing in the `v83` optimal
  partitions, widening strict all-positive certificates from `1..4` to `1..5`
  literals changes only:
  - `(10,11)`
- `(10,11)` flips from:
  - impossible
  - to exact cost `6`
- all other critical regions keep the same minimal exact cost

Why this matters:

- the current obstruction is more localized than it first appeared
- a widened certificate grammar can reopen the frontier without changing the
  rest of the critical-region geometry

New next ideas:

- rerun the full `v83` joint search in the widened certificate grammar
- compare that widened grammar against the current partition-aware
  residual-budget witness language on a second hard frontier

Current refinement:

- the localized `v84` grammar relief does propagate to the full joint frontier
- widening only the strict certificate side to `1..5` literals creates:
  - a zero-residual exact rung
- and improves:
  - budget `1`
  - budget `2`
- but budgets `3` and above stay fixed

Why this matters:

- the current hard-frontier ceiling was partly grammatical
- but only the low-residual regime was actually blocked by that grammar
- the higher-residual part of the frontier already had the right object

New next ideas:

- transfer the widened-certificate joint search to a second hard frontier
- or search a richer certificate grammar that might move budgets `3` and above

Current refinement:

- widening strict certificates from `1..5` to `1..6` literals does not move
  budgets `3`, `4`, or `5`
- exact high-residual ladder stays:
  - `20,24`
  - `19,23`
  - `19,22`

Why this matters:

- the low-residual regime was grammar-sensitive
- the high-residual regime is now locally saturated on the current
  literal-width axis

New next ideas:

- transfer the widened-certificate search to a second hard frontier
- or switch to a richer certificate language rather than one more literal

Current refinement:

- widening strict certificates from `1..5` to `1..6` literals does not move
  budgets `0`, `1`, or `2`
- exact low-residual ladder stays:
  - `25,29`
  - `23,27`
  - `21,25`

Why this matters:

- the literal-width story is now closed on this hard frontier
- the gains in `v85` were real, but already fully captured at width `5`
- the next barrier is no longer exposed by one more conjunction-width increase

New next ideas:

- transfer the widened-certificate search to a second hard frontier
- or switch to a genuinely richer certificate language

Current refinement:

- the partition-aware residual-budget witness-language loop does transfer to
  the toy lab-followup MPRD frontier
- but it transfers as a different exact object
- exact schema-first ladder:
  - `0 -> (5,5)`
  - `1 -> (4,4)`
  - `2 -> (4,5)`
  - `3 -> (4,7)`
  - `4 -> (6,10)`
- best exact budget is one merged residual-default region over:
  - `(1,2,3,4)`

Why this matters:

- transfer is real, but the residual-budget law shape is not invariant
- the right object on this frontier is one merged exception layer, not a
  descending residual ladder

New next ideas:

- compare this transfer object against a richer certificate language
- or explain semantically why the merged residual region is the optimum here

Current refinement:

- widening strict certificates from `1..4` to `1..5` literals does not move
  any rung of the lab-followup transfer ladder
- exact ladder stays:
  - `0 -> (5,5)`
  - `1 -> (4,4)`
  - `2 -> (4,5)`
  - `3 -> (4,7)`
  - `4 -> (6,10)`

Why this matters:

- the merged residual region from `v88` is not a narrow certificate-width
  artifact
- the lab-followup transfer object is already locally saturated on this
  literal-width axis

New next ideas:

- compare the transfer ladder against a richer certificate language
- or search for a semantic invariant explaining the merged residual region

Current refinement:

- the merged residual region on the lab-followup frontier is explained by a
  score-free earliest-error residual-default law on the whole unsafe block
- exact residual-default cost:
  - `4`
- exact all-positive cost:
  - `5`

Why this matters:

- the lab-followup transfer object now has a direct explanatory law
- this is stronger than only knowing that budget `1` is optimal

New next ideas:

- compare this explanatory law against a richer certificate language
- or search for an analogous score-free law on the refill frontier

Current refinement:

- the refill-side analog of `v90` fails on the whole nontrivial union in the
  current hard-frontier grammar
- exact residual-default merged subunions exist, but only:
  - `6` singletons
  - `6` pairs
  - `1` triple
- the unique maximal exact merged refill subunion is:
  - `(9,10,12)`
- that maximal triple still does not admit an exact all-positive presentation
- its best exact residual-default cost is:
  - `10`

Why this matters:

- the lab-followup earliest-error law is not the general score-free outcome
- refill still needs partitioning or richer languages
- the next useful search object is no longer a wider literal grammar, it is a
  richer score-free semantic language

New next ideas:

- search a small semantic grammar that might enlarge the maximal exact refill
  merged subset
- or compare that semantic line directly against richer certificate families

Current refinement:

- the mature witness-language line from `v78` to `v91` can now be summarized by
  one meta-rule:
  - the biggest exact gains came from adding a new search object
  - they did not mostly come from widening the current grammar
- exact counts:
  - new-axis interventions:
    - `9` cycles
    - `5` gain cycles
    - `16` gain-events
  - same-axis widening:
    - `5` cycles
    - `2` gain cycles
    - `4` gain-events

Why this matters:

- it gives a concrete criterion for choosing the next rabbit hole
- the next move should search over a deeper object than:
  - candidate
  - formula
  - fixed partition

New next ideas:

- temporal monitor-cell obligation carving on Tau specs
- minimal witness-language discovery over temporal cells
- semantic predicate invention for refill, if the temporal line stalls

Current refinement:

- the first temporal monitor-cell cycle survived only in staged form
- raw symbolic monitor cells are too strong on the whole bounded controller
  family
- after flat step-1 carving, the residual two-step temporal burden collapses
  exactly from:
  - `144` flat trace obligations
  - to `36` symbolic monitor cells
  - with the same `12` residual behavior classes

Why this matters:

- it sharpens how symbolic obligation objects should enter real software loops
- symbolic fibers should not necessarily replace raw failing tests from the
  start
- they may become exact only after earlier concrete carving

New next ideas:

- obligation-fibered repair on a bounded bug corpus
- certificate-carrying repair on the same corpus
- minimal repair-language discovery after failure fibers stabilize

Current refinement:

- the first software-engineering-shaped mainline survivor is
  dependency-aware obligation-fibered repair
- exact bounded law:
  - separable family:
    - monolithic:
      - `39.0`
    - dependency-aware fibered:
      - `9.0`
      - exact on `27 / 27`
  - overlap family:
    - naive fibered:
      - exact on `16 / 27`
    - dependency-aware fibered:
      - exact on `27 / 27`
      - average cost:
        - `9.0`

Why this matters:

- the first useful correction beyond plain fibering is not a wider test grammar
- it is a dependency edge between fibers
- that is exactly the kind of search-object shift that moved the frontier in
  earlier branches too

New next ideas:

- certificate-carrying repair on the same bounded patch corpus
- minimal repair-language discovery with the fiber dependency graph fixed

Current refinement:

- certificate-carrying repair survived on the same `v94` patch corpora
- exact bounded law:
  - no singleton certificate basis is exact
  - no pair certificate basis is exact
  - the unique minimal exact witness basis on both corpora is:
    - `guard`
    - `bounds`
    - `transform`
  - verification cost:
    - `3`
  - versus dependency-aware search:
    - `9.0`

Why this matters:

- the main software line has now moved from:
  - search over patch space
  - to search over repair fibers
  - to direct verification of patch-plus-witness
- that is the same deeper pattern already seen in the verifier-compiler branch

New next ideas:

- minimal repair-language discovery on top of the `v94` dependency graph and
  the `v95` witness basis
- or a richer bounded corpus where certificate bases might compress below one
  token per local fiber

Current refinement:

- the witness basis from `v95` now compiles back into the patch through a tiny
  exact decoder graph
- exact bounded law:
  - separable family:
    - minimal exact decoder cost:
      - `3`
  - overlap family:
    - minimal exact decoder cost:
      - `4`
    - unique extra dependency:
      - `transform_obs -> bounds`

Why this matters:

- the software line has now moved from:
  - patch search
  - to dependency-aware fiber search
  - to witness verification
  - to witness-to-patch compilation
- that is the strongest current software-shaped loop object in the repo

New next ideas:

- minimal repair-language discovery above the decoder graph
- richer bounded bug corpora to test whether the one-extra-edge law persists

Current refinement:

- the two exact decoders from `v96` now compress to one shared repair-language
  template
- exact bounded law:
  - base:
    - `guard_obs -> guard`
    - `bounds_obs -> bounds`
    - `transform_obs -> transform`
  - overlap delta:
    - `transform_obs -> bounds`
  - total template cost:
    - `4`

Why this matters:

- the software branch now has a genuine language object above the decoder graph
- separable and overlap do not need different grammars
- they need one shared local grammar plus one sparse patch

New next ideas:

- patch-program macro discovery on top of the shared template
- richer bounded bug corpora to test whether the same base-plus-one-delta law
  survives

Current refinement:

- the shared repair-language template from `v97` now compresses again into a
  tiny exact macro language
- exact bounded law:
  - separable family:
    - `MATCH_ID`
  - overlap family:
    - `MATCH_ID`
    - `SINGLE[transform_obs->bounds]`
  - unique exact shared macro template:
    - base:
      - `MATCH_ID`
    - overlap delta:
      - `SINGLE[transform_obs->bounds]`
    - total macro cost:
      - `2`
  - compression over `v97`:
    - `4 -> 2`

Why this matters:

- the software branch now has a real patch-program language, not only a shared
  edge template
- the current overlap correction is still sparse
- one reusable base instruction plus one residual patch is enough

New next ideas:

- search the smallest exact semantic patch-program language above the macro
  basis
- richer bounded bug corpora to test whether the same base-plus-one-patch law
  survives

Current refinement:

- the `v98` macro law now survives transfer to the full single-overlap decoder
  atlas
- exact bounded law:
  - singleton schema bases:
    - only `SINGLE` is exact
    - but description length:
      - `28`
  - unique exact MDL-optimal basis:
    - `MATCH`
    - `SINGLE`
  - basis size:
    - `2`
  - total instance cost:
    - `13`
  - description length:
    - `15`

Why this matters:

- the software branch now has its first transfer law above the macro level
- the right object is not only a concrete macro program
- it is a reusable schema basis:
  one local-match schema plus one sparse cross-edge patch schema

New next ideas:

- expand the overlap atlas and find the first obstruction to `MATCH + SINGLE`
- or search for a semantic schema language above the current syntactic basis

Current refinement:

- the first obstruction to the `v99` software transfer law now appears on the
  two-overlap atlas
- exact bounded law:
  - `MATCH + SINGLE` remains exact
  - but the new MDL-optimal basis is:
    - `MATCH`
    - `FANIN`
    - `FANOUT`
    - `SINGLE`
  - description length improves:
    - `57 -> 53`
  - total instance cost improves:
    - `55 -> 49`

Why this matters:

- the branch now has its first exact transfer obstruction
- the old law survives as correctness, but not as minimal description
- the first new structure is bundled row and column overlap

New next ideas:

- search the smallest exact semantic schema language that explains the
  `FANIN/FANOUT` jump
- or move to a richer bounded bug corpus where the same bundled overlap motif
  appears naturally

Current refinement:

- the `v100` transfer obstruction now has a unique minimal exact semantic
  explanation
- exact bounded law:
  - no singleton semantic basis is exact
  - no pair semantic basis is exact
  - unique minimal basis:
    - `same_obs`
    - `same_field`
    - `swap_pair`
  - rule:
    - row bundle, column bundle, or swap pair:
      - cost `2`
    - otherwise:
      - cost `3`

Why this matters:

- the branch has moved from syntax counts to motif semantics
- this is the right level for the next loop family
- it also gives a natural bridge to Morph-style reformulation search and
  ShapeForge-style world-model slices

New next ideas:

- semantic schema compilation for the three surviving motifs
- or a richer bounded software corpus where the same motifs appear as real
  repair structures

Current refinement:

- the `v101` motif law now compiles into a unique exact semantic schema
  language
- exact bounded law:
  - basis:
    - `DIAGONAL`
    - `SINGLE`
    - `BUNDLE2`
    - `SWAP2`
  - description length:
    - `53`
  - total instance cost:
    - `49`
  - same exact atlas cost as the best syntactic basis from `v100`

Why this matters:

- the branch now has a full semantic compile step
- this is the strongest current software loop object in the repo
- it is the right point to bring in Morph for reformulation search and
  ShapeForge for world-model slices

New next ideas:

- use Morph to search reformulations of the semantic schema language
- use ShapeForge to encode the motif slices and negative knowledge
- or move to a richer bounded software corpus where these motifs appear
  naturally

Current refinement:

- the `v102` semantic schema language now collapses into an exact routed repair
  compiler
- exact bounded law:
  - no `1`-branch router is exact
  - no `2`-branch router is exact
  - first exact router:
    - `extra0 -> DIAGONAL`
    - `swap_pair -> DIAGONAL+SWAP_PAIR`
    - `bundle_motif -> BUNDLE2+DIAGONAL`
    - default:
      - `DIAGONAL+SINGLE`

Why this matters:

- the branch now has a real loop object, not only a language object
- this is the strongest current software-engineering loop in the repo
- it is the right point to use ShapeForge and Morph for the next jump

New next ideas:

- use ShapeForge to encode the router cases as world-model slices and negative
  knowledge
- use Morph to search reformulations of the routed compiler
- or move to a richer bounded bug corpus where the same router law appears

Current refinement:

- the `v103` routed compiler now collapses one level further
- exact bounded law:
  - the full `22`-family software atlas admits an exact direct repair-program
    compiler from raw extra-edge sets
  - `motif_kind` is the unique exact singleton basis in the searched typed
    coordinate library
  - law:
    - `none -> DIAGONAL`
    - `single -> DIAGONAL+SINGLE`
    - `bundle -> DIAGONAL+BUNDLE2`
    - `swap -> DIAGONAL+SWAP2`
    - `other -> DIAGONAL+DOUBLE_SINGLE`

Why this matters:

- the software branch now has its first direct compiler
- this is the strongest current software loop object in the repo
- it is the cleanest current bridge from exact symbolic search to reusable
  repair-language loops

New next ideas:

- test whether `motif_kind` survives on a richer atlas with three overlaps
- use Morph to search stronger reformulations above the singleton motif state
- or move to a richer bounded software corpus where the same typed motif law
  survives

Current refinement:

- the singleton motif compiler now has a clean transfer correction
- exact bounded law on the full up-to-three-overlap atlas:
  - no singleton coordinate is exact
  - no pair basis is exact
  - first exact basis size:
    - `3`
  - preferred symmetric basis:
    - `obs_profile`
    - `field_profile`
    - `swap_pairs`
  - exact direct compiler still survives:
    - `42 / 42`
    - total instance cost `111`

Why this matters:

- the direct compiler survives transfer, but its state deepens
- the right next object is not another local motif
- it is a canonical support language above several equivalent exact size-`3`
  bases

New next ideas:

- use Morph to search whether the five exact size-`3` bases collapse to a
  smaller canonical support language
- test a richer atlas for the first obstruction beyond size `3`
- or move to a richer bounded software corpus where the same support-signature
  law survives

Current refinement:

- the `v105` transfer law now has a canonical quotient
- exact bounded law:
  - unique exact singleton basis:
    - `support_signature := (sort(obs_profile, field_profile), swap_pairs)`
  - support-signature count:
    - `8`

Why this matters:

- the transfer law is no longer only a small basis
- it now has a true symmetry quotient

New next ideas:

- search whether the canonical support quotient scalarizes again
- or push it into a richer atlas

Current refinement:

- the canonical support quotient now scalarizes
- exact bounded law:
  - no `1`-, `2`-, or `3`-scalar basis is exact
  - first exact basis size:
    - `4`
  - preferred basis:
    - `extra_count`
    - `max_obs`
    - `max_field`
    - `swap_pairs`

Why this matters:

- the direct software compiler now has both a canonical quotient and a compact
  scalar law
- this is the strongest software-engineering loop object in the repo so far

New next ideas:

- use Morph to search whether the three exact size-`4` scalar bases collapse to
  a smaller semantic scalar family
- test a richer atlas for the first obstruction beyond the 4-scalar law
- or move to a richer bounded software corpus and test whether the same scalar
  support law survives

Current refinement:

- the four-scalar law now collapses to a unique three-scalar semantic law
- exact bounded law:
  - no singleton scalar is exact
  - no pair scalar basis is exact
  - unique exact basis:
    - `extra_count`
    - `max_support`
    - `swap_pairs`

Why this matters:

- the direct compiler still had hidden symmetry left in it
- the software branch now has its strongest semantic scalar law so far

New next ideas:

- use Morph to search whether the three-scalar law collapses further into a
  smaller semantic orbit language
- test a richer atlas for the first obstruction beyond the max-support law
- or move to a richer bounded software corpus and test whether the same
  three-scalar law survives

Current refinement:

- the three-scalar law now collapses to an exact two-coordinate orbit law
- exact bounded law:
  - unique exact basis:
    - `extra_count`
    - `support_kind`

Why this matters:

- the support ladder still had hidden orbit symmetry left in it
- the direct software compiler became even smaller before the first real
  transfer obstruction appeared

New next ideas:

- push to the first richer atlas where one unique repair shape may stop being
  the right exact object
- or search the smallest exact law that survives after that transition

Current refinement:

- the first higher-order obstruction above the direct compiler line is now
  understood as a menu-valued exact repair language
- exact bounded law on the up-to-four-overlap atlas:
  - canonical library:
    - unique exact singleton:
      - `support_signature`
  - raw support library:
    - first exact basis:
      - `obs_profile`
      - `field_profile`
      - `swap_pairs`

Why this matters:

- symbolic structure did not disappear when the direct compiler stopped being
  unique
- the deeper object became a support-signature indexed menu of minimal repair
  shapes

New next ideas:

- transfer the menu law to the full off-diagonal atlas
- or search the first exact coordinate that collapses each menu back to one
  canonical repair shape

Current refinement:

- the menu-valued support law now survives on the full software atlas
- exact bounded law on all `64` off-diagonal subsets:
  - canonical library:
    - unique exact singleton:
      - `support_signature`
  - raw support library:
    - unique exact basis:
      - `obs_profile`
      - `field_profile`
      - `swap_pairs`

Why this matters:

- the menu law transfers farther than the last direct compiler
- the deeper software object is now clearly a support-signature indexed repair
  menu

New next ideas:

- search the first exact coordinate that collapses each full-atlas menu to one
  canonical repair shape
- or move to a richer bounded bug corpus and test whether the same menu law
  survives

Current refinement:

- the full-atlas menu law now supports a family of exact normalized direct
  compilers
- exact bounded result:
  - for all searched normal forms:
    - unique exact singleton:
      - `support_signature`
    - first exact raw basis:
      - `obs_profile`
      - `field_profile`
      - `swap_pairs`
  - ambiguous families:
    - `40`

Why this matters:

- exact menu discovery is not merely descriptive
- it can feed exact direct compilers once a deterministic normal form is fixed
- the preferred structural normal form is bundle-first, which matches
  fewest-families on the full ambiguous slice

New next ideas:

- search the smallest semantic condition that selects among competing normal
  forms
- or move to a richer bounded bug corpus and test whether the same
  menu-then-normalize loop survives

Current refinement:

- the normalized compiler family now has a one-bit semantic selector above it
- exact bounded law on the ambiguous full-atlas slice:
  - pure-swap normal form exists iff:
    - `perfect_swap_cover := (extra_count = 2 * swap_pairs)`
  - unique exact singleton:
    - `perfect_swap_cover`

Why this matters:

- the post-menu loop is not only a family of equally opaque normal forms
- one nontrivial regime inside it is already controlled by a direct symbolic
  selector

New next ideas:

- search the smallest exact selector for bundle-first versus swap-first on the
  full ambiguous slice
- or move to a richer bounded bug corpus and test whether the same selector
  pattern survives

Current refinement:

- the normalized compiler family now has an intrinsic exact disagreement law
- exact bounded law on the ambiguous full-atlas slice:
  - no singleton is exact
  - no pair is exact
  - first exact basis size:
    - `3`
  - preferred exact basis:
    - `extra_count`
    - `swap_pairs`
    - `balanced_profiles`
  - preferred exact state count:
    - `7`

Why this matters:

- the next layer above menu-then-normalize is no longer only a special-case
  regime selector
- the structural disagreement between two meaningful normal forms is itself a
  tiny exact symbolic object

New next ideas:

- search the smallest exact selector for bundle-first versus single-first on
  the same ambiguous slice
- or move to a richer bounded bug corpus and test whether the same
  disagreement law survives

Current refinement:

- the normalized family now has a shared exact ambiguity quotient above all
  meaningful pairwise disagreements
- exact bounded law on the ambiguous full-atlas slice:
  - constant pairs:
    - `bundle_first` vs `fewest_families -> same`
    - `swap_first` vs `single_first -> diff`
  - all four non-constant pairs share:
    - first exact basis size:
      - `3`
    - common preferred basis:
      - `extra_count`
      - `swap_pairs`
      - `balanced_profiles`
    - preferred quotient state count:
      - `7`

Why this matters:

- the post-menu ambiguity is no longer a bag of pair-specific selectors
- it has a common exact quotient, which is a much stronger loop object

New next ideas:

- search the smallest semantic presentation of the common 7-state ambiguity
  quotient
- or move to a richer bounded bug corpus and test whether the same shared
  quotient survives

Current refinement:

- the common ambiguity quotient now has a unique exact size-2 semantic
  presentation in the searched derived library
- exact bounded law on the ambiguous full-atlas slice:
  - no singleton is exact
  - unique exact minimal basis:
    - `balanced_profiles`
    - `support_gap`
  - preferred state count:
    - `6`
  - disagreement-signature classes:
    - `3`

Why this matters:

- the post-menu ambiguity layer is still compressible
- the current strongest software object is no longer the raw 7-state quotient
- it is a unique exact semantic law above the whole normalized family

New next ideas:

- search the smallest semantic presentation of the three disagreement-signature
  classes themselves
- or move to a richer bounded bug corpus and test whether the same support-gap
  law survives

Current refinement:

- the three disagreement-signature classes now compile to a tiny exact branch
  program
- exact bounded law:
  - no `0`-, `1`-, or `2`-guard program is exact
  - first exact program:
    - `3` guards
  - exact decision law:
    - `support_gap = 0 -> class_2`
    - `balanced_profiles and support_gap = 1 -> class_3`
    - `unbalanced_profiles and support_gap = 2 -> class_2`
    - default:
      - `class_1`

Why this matters:

- the strongest current software object is no longer only a quotient or a
  basis
- it is a tiny exact symbolic routing program

New next ideas:

- search the smallest semantic meaning of the three class labels
- or move to a richer bounded bug corpus and test whether the same class law
  survives

Current refinement:

- the ambiguity layer now has an anchored semantic decomposition
- exact bounded law:
  - anchor:
    - `bundle_first = fewest_families`
  - exact `swap_outlier` bit:
    - first exact program at `2` guards
  - exact `single_outlier` bit:
    - first exact program at `2` guards

Why this matters:

- the strongest current software object is now interpretable as a small routing
  contract
- that is better for assurance than opaque class labels alone

New next ideas:

- search for a smaller joint program that emits the anchor plus both outlier
  bits directly
- or move to a richer bounded bug corpus and test whether the same anchored
  decomposition survives

Current refinement:

- the ambiguity-class program now compresses further in a richer clause
  language
- exact bounded law:
  - no `0`-clause or `1`-clause program is exact
  - first exact classifier:
    - `2` ordered clauses
  - exact law:
    - `balanced_profiles and support_gap = 1 -> class_3`
    - `support_gap = 0 or unbalanced_profiles and support_gap = 2 -> class_2`
    - default:
      - `class_1`

Why this matters:

- one of the strongest recent software gains came from changing the symbolic
  language, not the corpus
- this sharpens the case for minimal witness-language discovery as the deeper
  loop family

New next ideas:

- search the smallest exact joint program for the anchor plus both outlier
  bits
- or move to a richer bounded bug corpus and test whether the same two-clause
  law survives

Current refinement:

- the stable anchor now has its own exact symbolic compiler over the same
  semantic state
- exact bounded law:
  - no `0`-, `1`-, or `2`-guard program is exact
  - first exact program:
    - `3` guards
  - exact anchor law:
    - `balanced_profiles and support_gap = 2 -> BUNDLE2+BUNDLE2+DIAGONAL+SWAP2`
    - `support_gap >= 2 -> BUNDLE2+BUNDLE2+DIAGONAL`
    - `balanced_profiles -> BUNDLE2+BUNDLE2+BUNDLE2+DIAGONAL`
    - default:
      - `BUNDLE2+DIAGONAL+SWAP2`

Why this matters:

- the branch now has a fuller anchored routing kernel, not only ambiguity
  selectors
- that is closer to a reusable formal software-assurance component

New next ideas:

- search a menu-selector law above the exact menu states
- or move to a richer bounded bug corpus and test whether the same size-`2`
  basis and one-bit menu refinement survive

Current refinement:

- the size-`2` semantic kernel basis is exact for routing but not for the full
  repair menu
- exact bounded law:
  - no singleton coordinate in the searched semantic library is exact
  - the first exact menu basis has size `3`
  - a preferred exact refinement is:
    - `(balanced_profiles, support_gap, high_overlap)`
  - the only splitting kernel state is:
    - `(True, 0)`
  - the first exact direct menu program has:
    - `6` guards

Why this matters:

- the current software branch now has its first clean boundary above the direct
  kernel
- that creates a sharper next object:
  - exact menu
  - then exact selector above the menu

New next ideas:

- search a menu-selector law above the exact menu states
- or move to a richer bounded bug corpus and test whether the menu refinement
  itself fails

Current refinement:

- logic replay exposed that the actual `bundle_first` anchor and the true
  joint kernel are not definable in:
  - `(balanced_profiles, support_gap)`
- both first become exact in:
  - `(balanced_profiles, support_gap, high_overlap)`

Why this matters:

- the software branch had been drifting toward a too-strong size-`2` kernel
  reading
- the logic replay turned that into a real definability boundary instead of a
  silent assumption

New next ideas:

- classify every live software target by its smallest exact theory
- or look for the first target that forces a theory beyond `Q3`

Current refinement:

- the live software targets now split into two exact definability tiers
- `Q2 = (balanced_profiles, support_gap)` controls:
  - ambiguity and disagreement targets
- `Q3 = (balanced_profiles, support_gap, high_overlap)` controls:
  - concrete selector, true-kernel, and menu targets
- no searched non-constant target currently needs a theory beyond `Q3`

Why this matters:

- this is the cleanest logic-level object in the software branch so far
- it makes the next rabbit hole precise:
  - either a new target beyond `Q3`
  - or a canonical selector inside `Q3`

New next ideas:

- search for the first software target that forces a theory beyond `Q3`
- or search a canonical selector law inside the exact `Q3` menu states

Current refinement:

- the same `Q2` state:
  - `(balanced_profiles = True, support_gap = 0)`
  is a common necessity witness for the whole `Q3` commitment tier
- every low-overlap family in that state separates from the unique
  high-overlap family on:
  - `bundle_first`
  - `fewest_families`
  - `swap_first`
  - `single_first`
  - `true_kernel`
  - `menu`

Why this matters:

- `high_overlap` is no longer just “the bit that fixes one split”
- it is the common witness that forces the whole current commitment tier past
  `Q2`

New next ideas:

- search for the first software target that truly escapes `Q3`
- or search for a canonical selector law inside the exact `Q3` commitment
  states

Current refinement:

- the current software target family is already algebraically closed at `Q3`
- relation algebra closes at:
  - `(balanced_profiles, support_gap)`
- commitment algebra closes at:
  - `(balanced_profiles, support_gap, high_overlap)`
- the full current target algebra closes at the same `Q3`

Why this matters:

- the present frontier is no longer “one more target from the same family”
- the next honest jump needs either:
  - a richer target family
  - or a theorem about canonical choice inside `Q3`

New next ideas:

- search for the first richer software target that escapes `Q3`
- or search for a canonical selector theorem inside the exact `Q3` states

Current refinement:

- even a much richer structural selector family still closes at `Q3`
- searched selector library:
  - `85` raw lexicographic selectors of length `1..3`
- unique selector behaviors on the bounded corpus:
  - `10`
- preferred exact quotient still:
  - `(balanced_profiles, support_gap, high_overlap)`

Why this matters:

- the current software atlas is more saturated than it looked
- the next honest jump is no longer another selector variant

New next ideas:

- search for the first genuinely richer software target that escapes `Q3`
- or search for a selector theorem inside the exact `Q3` states

Current refinement:

- `Q3` already controls the full symmetric support geometry
- `support_signature` has preferred exact basis:
  - `(balanced_profiles, support_gap, high_overlap)`
- the first honest escape is orientation
- `oriented_support_pair` first becomes exact at:
  - `(extra_count, orientation)`
- raw family identity still escapes the searched symmetric-plus-orientation
  library

Why this matters:

- the current software logic is sharper than “relations versus commitments”
- it now has a clear theory ladder:
  - `Q2` for relations
  - `Q3` for commitments and symmetric support
  - `Q4` for oriented support

New next ideas:

- search the first theory that recovers exact raw family identity
- or search whether orientation is the unique first escape from `Q3`

Current refinement:

- raw family identity does recover without brute-force edge indicators
- the first exact completion law is row-column incidence
- preferred exact basis:
  - `(out_guard, out_bounds, out_transform, in_guard, in_bounds)`
- minimal exact basis size:
  - `5`
- minimal exact basis count:
  - `24`

Why this matters:

- there is now a real explanation tier above the semantic support stack
- the next theory after `Q4` is incidence, not raw family lookup

New next ideas:

- search for a smaller semantic quotient above incidence but below raw family
  identity
- or test the incidence law on a richer software atlas

Current refinement:

- the size-`5` scalar incidence law collapses to a unique singleton quotient
- exact singleton:
  - `incidence_signature = (out_profile, in_profile)`
- exact state count:
  - `40`

Why this matters:

- the software logic stack now has a canonical object above `Q4`
- this is a better proof target than the older scalar incidence basis

New next ideas:

- test whether the singleton incidence-signature law survives on the full atlas
- or find the first transfer obstruction if it fails

Current refinement:

- the singleton incidence-signature law almost transfers to the full atlas
- the only obstruction is the balanced `3`-cycle pair
- preferred full-atlas repair:
  - `(incidence_signature, cycle_orientation)`

Why this matters:

- the next theory above incidence-signature is only one cycle bit
- the transfer boundary is small and explicit, not diffuse

New next ideas:

- search for a richer atlas where incidence-signature plus one cycle bit breaks
- or search for a smaller semantic account of cycle orientation itself

Current refinement:

- the first bounded profit-agent game now exists
- same intelligence does not force equal activation thresholds
- exact region law:
  - `extractive_revenue >= open_revenue iff n_low <= 4 * n_high`
- governed profit survives after forbidding the top illicit strategy

Why this matters:

- it gives a real formal base for post-AGI economics rather than only prose
- `MPRD` changes the game by shrinking the feasible action set, not by killing
  profit

New next ideas:

- add passive ownership to the heterogeneous-complement game
- or add more strategy classes and ask when admissible-profit beats raw profit

Current refinement:

- the first bounded hold-up law now survives
- user best response shifts:
  - active at `open`, `moderate`
  - passive at `high`, `maximal`
- platform revenue is uniquely maximized at:
  - `moderate`

Why this matters:

- full expropriation is not automatically rational
- if passive claims exist, they can become the dominant user response before
  full capture

New next ideas:

- combine passive ownership with heterogeneous complements
- add demand closure:
  - if labor income falls and passive ownership is concentrated, who buys output?

Current refinement:

- the combined heterogeneous-complement plus passive-ownership game now has an
  exact phase boundary
- `open` includes both complement classes
- `moderate` keeps only high-complement users active
- exact boundary:
  - `moderate_revenue >= open_revenue iff 2 * n_low <= 9 * n_high`

Why this matters:

- this is the first real post-AGI economics phase diagram in the repo
- complement scarcity, not intelligence scarcity alone, controls who remains
  active under platform extraction

New next ideas:

- add demand closure and solve the mass-purchasing-power question
- or let passive ownership itself become strategic instead of fixed

Current refinement:

- the first demand-closure theorem now survives
- one-unit household demand model:
  - `S = (m + 1) * n`
  - `D = n + b`
  - `D >= S iff b >= m * n`

Why this matters:

- broad passive claims are not only a policy preference in this model
- they are the exact condition for clearing the extra output beyond owner
  self-consumption

New next ideas:

- replace the one-unit cap with a richer demand function
- or combine this theorem with the `v134` platform-composition boundary

Current refinement:

- the `v134` platform boundary and the `v135` demand-closure law now combine
  into one exact phase diagram
- for `n_high > 0`:
  - `open` never clears
  - `moderate` clears iff `n_high <= n_low`
  - `moderate` is privately optimal iff `2 * n_low <= 9 * n_high`
  - so a privately optimal and demand-clearing regime exists iff
    `n_high <= n_low and 2 * n_low <= 9 * n_high`

Why this matters:

- this is the first checked split between private platform incentives and macro
  viability in the repo
- it makes the social-stability question into an exact region law rather than
  a narrative concern

New next ideas:

- replace the one-unit cap with a richer demand function
- or make passive ownership itself strategic, then solve the new fixed point

Current refinement:

- the universal-principal question now has an exact answer in the double-output
  model
- with `h` total households and `n` active owners:
  - closure holds iff `h >= 2 * n`
  - equivalently, `n <= h / 2`
  - all-active positive-household regimes fail

Why this matters:

- it separates ownership of profit agents from active principalship
- the bounded model now says universal ownership may remain possible, but
  universal active ownership does not

New next ideas:

- replace the one-unit cap with richer household demand
- or let households choose active versus passive status strategically

Current refinement:

- the active-versus-passive split is now a checked coordination problem
- with identical households in the double-output model:
  - active payoff greater than passive gives only the all-active choice, which
    fails closure
  - passive payoff greater than active gives only zero production
  - nontrivial clearing first appears only under indifference, with `n <= h / 2`

Why this matters:

- universal profit agents do not by themselves solve role assignment
- the bounded model now says the real problem is coordinated interior splits,
  not only access to intelligence

New next ideas:

- add differentiated complements to the coordination game
- or formalize quotas, prices, or rationing as the coordination device

Current refinement:

- the first mechanism split now survives
- in the symmetric double-output model:
  - uniform pricing cannot implement a positive interior individually stable
    regime unless it creates exact indifference
  - hard quotas can implement the interior regime under strict active
    preference, with clearing exactly when `q <= h / 2`

Why this matters:

- the coordination problem is now formalized as a mechanism problem
- the next real question is which allocation devices survive once households
  differ

New next ideas:

- add differentiated complements to the mechanism game
- or replace hard quotas with prices plus lotteries or transferable permits

Current refinement:

- the homogeneous pricing impossibility is now split by complement
  heterogeneity
- in the two-type model:
  - `a_low < p < a_high` selects only the high type
  - that regime clears iff `H <= L`

Why this matters:

- heterogeneous complements let a uniform price implement a real interior
  regime
- but composition of types still matters, pricing is not enough by itself

New next ideas:

- compose pricing with quotas
- or replace uniform pricing with permits or lotteries when the high type is a
  majority

Current refinement:

- the first composed mechanism now survives
- price handles type selection
- quota handles count selection
- in the two-type middle-price region:
  - closure holds iff `q <= (L + H) / 2`

Why this matters:

- the branch now has a proper selection-versus-allocation split
- that is a deeper game-theoretic object than one-stage pricing or one-stage
  quotas

New next ideas:

- replace hard quotas with lotteries or transferable permits
- or make the quota itself a strategic platform choice

Current refinement:

- the zero-employee-firm opening now has a corrected sink law
- in the scalar software-only multiplier model:
  - `Y = alpha * Y + F`
  - `F = H + A_term + C + X`
  - `a < b and F = 0 imply Y = 0`
  - `a < b and F > 0 imply Y > 0`

Why this matters:

- human attention is not uniquely privileged
- crypto settlement and terminal agent demand can act as final sinks
- but circular intermediate demand still cannot replace final sinks

New next ideas:

- build a small network model with multiple sinks
- or distinguish terminal agent demand from intermediate agent demand more
  explicitly

Current refinement:

- the zero-employee software-firm branch now has a direct entry ceiling law:
  - `Pi_total = F - N * c`
  - `Pi_total >= 0 iff F >= N * c`
  - `Pi_total > 0 iff F > N * c`

Why this matters:

- legal-shell bottlenecks can be relaxed without removing the economic ceiling
- the right next object is no longer whether agent firms can be created
- it is how sink access is routed and who captures slot rents

New next ideas:

- discovery-slot theorem for zero-employee firms under platform bottlenecks
- or asymmetric-routing network models above the same sink bundle

Current refinement:

- the first discovery-bottleneck theorem now survives:
  - `Pi_total = F - N * c`
  - slot-holder margin numerator:
    - `M_slot = F - q * c`
  - exact law:
    - `M_slot > 0 iff F > q * c`

Why this matters:

- discovery rails are now explicit economic objects
- slot control redistributes gains without creating new aggregate surplus
- the next branch should focus on asymmetric routing or slot-sale mechanisms

New next ideas:

- slot-auction theorem for zero-employee firms
- or a small asymmetric-routing network where sink access is endogenous

Current refinement:

- the trust branch and the machine-control branch now connect to incumbent
  rents
- in the two-period no-reentry adoption model:
  - social machine adoption holds iff `2 * A + lam >= 2 * tau1`
  - private incumbent adoption holds iff
    `2 * A + lam >= 2 * tau1 + 2 * rho`
  - so a strict lockout wedge exists whenever:
    - `2 * A + lam >= 2 * tau1`
    - `2 * A + lam < 2 * tau1 + 2 * rho`

Why this matters:

- machine reliability and trust are not enough by themselves
- the identity of the chooser matters because adoption can destroy incumbent
  rents
- the next software-design question becomes how to lower `tau1`, raise `lam`,
  or offset `rho`

New next ideas:

- explicit assurance-package law with cost, trust lift, and audit lift
- or a repeated deployment game where routing and trust update together

Current refinement:

- the assurance-design branch now survives as an exact theorem
- with package levers `d`, `g`, and `k`:
  - packaged private adoption holds iff
    `2 * A + lam + 2 * d + g >= 2 * tau1 + 2 * rho + k`
  - above the baseline block, package success is exactly:
    `2 * d + g - k >= (2 * tau1 + 2 * rho) - (2 * A + lam)`

Why this matters:

- software design is now explicit in the model
- per-period trust lift and extra learning have different coefficients
- a package can be judged by whether it closes the exact shortfall, not by
  vague confidence language

New next ideas:

- separate audit, insurance, and liability shifting into distinct levers
- or make assurance-package choice endogenous for a platform or regulator

Current refinement:

- the distinct assurance levers now have exact private coefficients
- with linear cost:
  - trust lift `d` enters as `2 - c_d`
  - delayed learning `g` enters as `1 - c_g`
  - liability offset `ell` enters as `2 - c_ell`
- equal-cost corollary:
  - `2 * A + lam + d + ell >= 2 * tau1 + 2 * rho`
  - delayed learning `g` drops out

Why this matters:

- the branch now says which assurance levers actually buy adoption
- predeployment trust and liability structure can matter more than post-success
  learning

New next ideas:

- endogenous package choice by incumbents versus regulators
- or a repeated game where package choice also changes routing or deployment

Current refinement:

- the social-versus-private assurance split now has an exact bridge law
- social package choice survives when:
  - `2 * A + lam + 2 * d + g >= 2 * tau1 + k`
- private package choice survives only when:
  - `2 * A + lam + 2 * d + g >= 2 * tau1 + 2 * rho + k`
- the exact implementation bridge is:
  - `s_star = max(0, 2 * tau1 + 2 * rho + k - (2 * A + lam + 2 * d + g))`

Why this matters:

- the remaining obstruction after social viability is a rent wedge with an
  exact size
- the next question is no longer "is there a wedge?"
- it is who sponsors or bargains over that wedge

New next ideas:

- bargaining over package funding between incumbent, platform, and regulator
- or repeated games where assurance changes routing and deployment incentives

### Requirements recoverability frontier

Hypothesis:

- missing requirements are recoverable exactly when admissible counterexample
  signatures either isolate them directly or cover them under a scoped
  stakeholder-oracle loop

Current status:

- survived exhaustively on `|R| = 3`
- exact local laws:
  - pure recovery:
    - `∀r in M, {r} in W`
  - oracle-assisted recovery:
    - `⋃ A_W(M) = M`
- global all-missing-set family:
  - oracle help gives no extra coverage over pure singleton recovery
- scoped pair-lobotomy family:
  - oracle-assisted recoverable libraries:
    - `36`
  - pure recoverable libraries:
    - `16`
  - strict oracle-only advantage:
    - `20`

Why this matters:

- this is the first point where requirements discovery becomes a precise
  witness-space object in the repo
- it separates:
  - witness availability
  - omission-depth assumptions
  - stakeholder disambiguation power

Next ideas:

- derive the minimal stakeholder question budget from the admissible witness
  family
- search ambiguity quotients for larger `n` and larger `k`-lobotomy families
- compare oracle-assisted recoverability against direct certificate or witness
  languages on the same bounded corpus

### Observation-quotient loop geometry frontier

Hypothesis:

- the true loop object above requirements recoverability is the observation
  quotient induced by the witness library on a scoped omission family

Current status:

- survived exhaustively on `|R| = 4`
- exact laws:
  - structured recovery:
    - `O_W` injective on `F`
  - minimal worst-case post-observation question budget:
    - `max_C depth*(C)`
- exhaustive counts:
  - pair-lobotomy family:
    - atomic singleton rule recoverable libraries:
      - `2048`
    - structured observation-quotient recoverable libraries:
      - `19424`
  - all-nonempty family:
    - atomic singleton rule recoverable libraries:
      - `2048`
    - structured observation-quotient recoverable libraries:
      - `3072`
- representative correction:
  - pair-only witness library:
    - atomic pair-family recovery fails
    - structured pair-family recovery succeeds with question budget `0`
    - unrestricted-family question budget is `3`

Why this matters:

- this is the first exact statement that loop state geometry changes
  recoverability in the requirements branch
- it turns stakeholder questioning into a structured separator problem over an
  ambiguity quotient
- it suggests a broader loop space:
  - observation language
  - quotient geometry
  - query language
  - policy synthesis over that geometry

Next ideas:

- synthesize exact minimal question policies, not only their depth
- search richer query languages, such as pairwise comparison or subset queries
- test whether the same observation-quotient algebra transfers to repair or
  verifier-compiler witness languages

### Temporal label-function frontier

Hypothesis:

- temporal label functions form a separate loop-space axis, and the right
  symbolic label basis may appear only after earlier carving

Current status:

- survived exhaustively on the bounded retest-tracker controller family
- full family:
  - `L_cell` strictly refines `L_trace`
  - but does not match its partition
- staged slice after first-step carving:
  - `L_cell` and `L_trace` become partition-equivalent

Why this matters:

- it shows loop-space geometry is not static
- the loop can change basis in label space after earlier cuts
- this is different from:
  - changing the witness language
  - or changing the stored observation quotient

Next ideas:

- derive exact trigger laws for staged label-basis change
- search temporal label quotients on a second bounded domain
- compare temporal label-basis moves with verifier-compiler quotient-repair
  moves on one shared algebraic chart

Current refinement:

- the separate software survivors above the ambiguous slice now unify into one
  direct bounded kernel:
  - `Kernel(x) = (AnchorShape(x), SwapOutlier(x), SingleOutlier(x))`
- exact bounded law:
  - the unique exact minimal basis is still:
    - `balanced_profiles`
    - `support_gap`
  - no singleton coordinate in the searched semantic library is exact
  - no `0`-, `1`-, `2`-, `3`-, or `4`-guard joint program is exact
  - the first exact joint program has:
    - `5` guards

Why this matters:

- the software branch now has one direct exact kernel object, not only nearby
  partial laws
- this is the cleanest current bounded formal object for software assurance in
  the repo

New next ideas:

- search the exact menu law above the anchored kernel regions
- or move to a richer bounded bug corpus and test where the size-`2` basis
  stops being exact

### Uniform witness ladder frontier

Hypothesis:

- witness arity gives loop space an exact observability ladder, and the
  remaining open question is how much query language is needed below that
  threshold

Current status:

- survived exhaustively on uniform `k`-ary witness libraries
- lower layers:
  - every omission set with size below `k` collapses to empty observation
- upper layers:
  - every omission set with size at least `k` is exactly observable
- pair-witness special case:
  - singleton ambiguity budget is exactly:
    - `n - 1`

Why this matters:

- it gives one clean coordinate chart on loop space
- witness generation, observation storage, and question language can now be
  separated cleanly
- it suggests staged loops:
  - cheap witnesses set the threshold
  - questions or richer labels only need to operate below it

Next ideas:

- derive the exact requirement-membership budget for the entire lower rung
  `1 <= |M| < k`
- compare mixed-arity witness libraries against pure `k`-ary ladders
- search a joint law that combines witness-arity thresholds with staged
  temporal label-basis changes

### Lower-rung question geometry frontier

Hypothesis:

- the main loop-space tradeoff is not just where observability begins
- it is how the unresolved lower rung interacts with the chosen follow-up query
  language

Current status:

- exact membership-only law now survives:
  - `budget_mem(n, 2) = n - 1`
  - `budget_mem(n, k) = n` for every `3 <= k <= n`
- pair witnesses are therefore best among non-singleton uniform witness
  families when the loop can only ask requirement-membership questions

Why this matters:

- it gives the first exact threshold-versus-budget tradeoff in the current loop
  algebra program
- it suggests that tool invention should search jointly over:
  - witness language
  - label basis
  - stored observation geometry
  - follow-up query language
- it also suggests that new tools should target richer separator questions,
  not only stronger witness generators

Next ideas:

- compute exact budgets for richer question languages:
  - pair-membership
  - cardinality
  - partition or group-membership questions
- search mixed-arity witness families for Pareto improvements over the
  uniform ladder
- build one small loop-space geometry packet that unifies:
  - witness threshold ladders
  - observation quotients
  - staged temporal label-basis changes

### Pair-basis tool-combination frontier

Hypothesis:

- once pair witnesses are present, the next gains do not come from piling on
  more uniform higher-arity generators
- they must come from richer query languages, label bases, or non-uniform
  witness families

Current status:

- exact mixed-arity scan now survives:
  - every checked `W_A` with `2 ∈ A` matches the pair-only basis on:
    - ambiguity partition
    - worst-case membership-question budget

Why this matters:

- it collapses a large region of loop space to one effective basis
- it gives a concrete tool-design rule:
  - add the pair layer first
  - then stop adding uniform higher-arity layers unless the query language or
    objective changes
- it shifts invention pressure toward:
  - richer separator questions
  - non-uniform witness generators
  - staged basis changes

Next ideas:

- exact laws for pair-membership or small-group membership queries above the
  pair basis
- Pareto scans over non-uniform witness families
- a public tutorial or handoff packet on loop-space geometry once one more
  cross-axis survivor lands

### Separator expressivity frontier

Hypothesis:

- after the pair basis lands, the central loop-design problem is no longer
  witness generation
- it is the expressivity of the separator language above the singleton residue

Current status:

- exact ladder now survives:
  - pair-subset queries:
    - unrecoverable
  - singleton-membership:
    - `n - 1`
  - block-intersection:
    - `ceil(log2 n)`

Why this matters:

- it is the clearest current evidence that loop space has interacting axes
- the same witness basis can support:
  - no completion
  - linear completion
  - logarithmic completion
  depending only on separator language
- it suggests new tool invention should search separator families explicitly,
  not treat questioning as an afterthought

Next ideas:

- exact laws for:
  - pair-membership plus singleton-membership
  - block plus cardinality
  - small-group subset queries
- integrate separator expressivity into the reusable skill and the eventual
  public loop-geometry tutorial

### Witness-query substitution frontier

Hypothesis:

- one major loop-space axis is linear substitution between built-in atomic
  witnesses and later atomic interrogation
- the more interesting nonlinearity only starts when a witness basis changes
  the ambiguity geometry itself

Current status:

- exact singleton substitution law now survives:
  - `budget_mem(W_T, F_all) = n - |T|`
- cross-axis reading:
  - singleton witnesses buy linear budget rebates
  - pair witnesses buy a new residual geometry
  - block queries only become logarithmic on that reshaped geometry

Why this matters:

- it cleanly separates two kinds of loop improvement:
  - substitution along one axis
  - genuine geometric change across axes
- that is likely the right language for a public loop-space tutorial

Next ideas:

- scan non-uniform witness families for true Pareto improvements
- scan mixed separator families above the pair basis
- start writing the loop-space geometry tutorial or handoff packet

### Geometry-prerequisite frontier

Hypothesis:

- the strongest loops in this branch are hybrid loops that first change
  ambiguity geometry, then run a small residual controller

Current status:

- exact block-query prerequisite law now survives:
  - raw family:
    - `n`
  - singleton residue after pair basis:
    - `ceil(log2 n)`

Why this matters:

- it is the cleanest current bounded argument that a loop can beat plain
  verifier-compilation by changing the state geometry before compilation
- it makes the likely next target more concrete:
  - hybrid quotient-question loops

Next ideas:

- search non-uniform geometry-changing witness bases
- compare residual controller sizes directly against verifier-compiler
  controllers on the same bounded families
- start a small candidate ranking for loops that look stronger than plain
  verifier-compilation

### Atomic-axis cutoff frontier

Hypothesis:

- purely atomic witness bases form one closed linear axis
- no richer separator language will make that axis genuinely nonlinear

Current status:

- exact invariance law now survives:
  - `budget_atom(W_T, F_all) = budget_block(W_T, F_all) = n - |T|`

Why this matters:

- it gives a concrete stopping rule for loop search
- do not spend more effort trying to beat verifier-compilation with:
  - singleton witnesses
  - plus richer but still geometry-neutral separators
- the promising region is now more sharply defined:
  - geometry-changing witnesses
  - then expressive residual controllers

Next ideas:

- search sparse non-uniform pair-like witness bases
- compare hybrid residual-controller size against direct verifier-compilers
- begin a public tutorial draft once one more non-uniform survivor lands

### Pure-mass frontier

Hypothesis:

- the next useful loop-ranking axis is immediate resolved mass, not only
  worst-case residual depth

Current status:

- exact complement-witness law now survives:
  - `pure_classes(W_{T,U}) = 2^|T|`
  - `budget_block(W_{T,U}, F_all) = |U|`

Why this matters:

- it gives the first exact reason that a sparse non-uniform witness family can
  be better than a plain verifier-compiler style loop even without improving
  worst-case depth
- it suggests a more honest ranking tuple for loops:
  - witness size
  - pure resolved mass
  - residual depth
  - residual controller size

Next ideas:

- search non-uniform pair-like families with better pure-mass constants
- compare loop families under the new ranking tuple
- start the tutorial draft once one more non-uniform law lands

### Sparse pair-geometry frontier

Hypothesis:

- sparse pair-like witness families may already be better loop candidates than
  plain verifier-compilers on some bounded families, because they can buy large
  pure resolved mass before the residual controller even starts

Current status:

- exact star-pair law now survives:
  - `pure_classes(W_star) = 2^(n-1) - 1`
  - `pure_classes(W_anchor_star) = 2^(n-1)`
  - both keep:
    - `budget_block = n - 1`
- exact biclique law now survives:
  - `pure_classes(W_biclique) = (2^|A| - 1)(2^|B| - 1)`
  - `Residual(W_biclique) = P_+(A) ∪ P_+(B)`

Why this matters:

- the star family is not isolated, it is one edge of a biclique ladder
- balanced bicliques look like stronger sparse pair candidates than stars
- the next ranking step is to solve the side-only residual controller exactly

Next ideas:

- solve the residual-controller budget on `P_+(A) ∪ P_+(B)`
- compare biclique loops against pair-basis plus block-separator hybrids
- use the graph view to search new pair witness families, not just ad hoc
  subset families

### Biclique design-rule frontier

Hypothesis:

- the sparse pair branch should not be searched uniformly
- once the biclique ladder is explicit, the best search direction should move
  toward balance

Current status:

- exact residual-controller law now survives:
  - `budget_block(P_+(A) ∪ P_+(B)) = ceil(log2((2^a - 1) + (2^b - 1)))`
- exact biclique balance law now survives:
  - pure mass increases strictly toward balance
  - residual budget decreases weakly toward balance

Why this matters:

- balanced bicliques are now the leading sparse pair candidate in this branch
- stars remain useful as the sparse edge, but no longer look like the best
  design point when witness count can increase

Next ideas:

- compare balanced bicliques directly against:
  - pair-basis plus block-separator hybrids
  - one-complement families
  - anchored star families
- search graph-shaped pair families that might beat balanced bicliques on the
  full ranking tuple

### Sparse-versus-dense pair frontier

Hypothesis:

- balanced bicliques may be the leading sparse exact loop in the pair branch,
  but not the final one

Current status:

- exact tradeoff law now survives:
  - balanced bicliques use about half as many pair witnesses as the full pair
    basis
  - they lose only a subexponential slice of pure resolved mass
  - they pay a much deeper residual controller

Why this matters:

- the search is no longer blind
- there is now a concrete frontier to beat:
  - the balanced biclique sparse tradeoff

Next ideas:

- search graph-shaped pair families between balanced bicliques and the full
  pair basis
- compare the best sparse pair loops directly against verifier-compilation
  style loops on the same bounded corpora

### Balanced multipartite frontier

Hypothesis:

- the real pair-witness design space is the balanced multipartite ladder, not
  just the biclique edge

Current status:

- exact complete multipartite pure law now survives
- exact balanced multipartite extremal law now survives
- exact balanced multipartite ladder law now survives

Why this matters:

- balanced bicliques are now just one rung
- the full pair basis is another rung
- the live question is what the residual-controller side looks like for the
  middle rungs

Next ideas:

- solve the residual-controller law for general balanced multipartite residual
  families
- compare low-`t`, medium-`t`, and high-`t` balanced multipartite loops against
  verifier-compilation style loops on shared bounded families

### Balanced multipartite controller frontier

Hypothesis:

- the balanced multipartite ladder may be the first loop family in this branch
  where both witness geometry and residual-controller cost stay exact across a
  broad continuum

Current status:

- exact bounded residual-controller law now survives on:
  - `2 <= n <= 7`
  - `2 <= t <= n`
  - with:
    - `budget_block = ceil(log2 residual_size)`

Why this matters:

- the balanced ladder is no longer only a witness-side story
- the next step can honestly shift from discovery to comparison

Next ideas:

- prove or extend the balanced residual-controller law
- compare balanced multipartite loops directly against verifier-compilation
  style loops on shared bounded corpora

### Direct-compiler frontier

Hypothesis:

- once a loop family has both direct witness-side formulas and an exact
  bounded controller law, it becomes a serious competitor to
  verifier-compilation style loops

Current status:

- exact direct formulas now survive for the balanced multipartite ladder:
  - residual size
  - pure resolved mass
  - witness count
- exact bounded controller law survives on:
  - `2 <= n <= 7`
  - `2 <= t <= n`

Why this matters:

- the balanced multipartite ladder is now partly a direct compiler, not just a
  search family
- the next step can be a direct cross-family comparison instead of another pure
  geometry scan

Next ideas:

- compare balanced multipartite direct geometry against verifier-compilation
  style loops on the same bounded corpora
- prove or extend the residual-controller law so the whole ladder becomes a
  direct compiler rather than only the witness side

### Internal-clique pair frontier

Hypothesis:

- same-cluster pair witnesses form a second exact pair-loop family, dual in
  spirit to the cross-block multipartite branch

Current status:

- exact internal-clique law now survives:
  - residual family:
    - one-choice-per-cluster
  - residual size:
    - `Π_i (1 + s_i) - 1`
  - pure classes:
    - `2^n - Π_i (1 + s_i)`
  - witness count:
    - `Σ_i s_i(s_i - 1)/2`

Why this matters:

- the pair-witness space already has more than one clean algebraic direction
- there is now a concrete dual family to compare against balanced multipartite

Next ideas:

- characterize extremal rules inside the internal-clique family
- compare internal-clique and balanced multipartite loops on shared witness
  budgets

### Pure frontier correction

Hypothesis:

- the balanced multipartite ladder is likely only one side of the global
  pair-witness pure frontier

Current status:

- exhaustive simple-graph scan now confirms strict balanced gaps on:
  - `(5, 6)`
  - `(6, 9)`
  - `(7, 12)`
  - `(7, 16)`
- internal-clique loops already match many optimum budgets:
  - all defined budgets for `n <= 4`
  - `6/7` for `n = 5`
  - `9/9` for `n = 6`
  - `10/13` for `n = 7`

Why this matters:

- stronger pair-witness loops already exist beyond the current balanced
  multipartite ladder
- the remaining gaps are now a concrete bounded search target

Next ideas:

- classify the remaining pure-optimal graph families outside both:
  - balanced multipartite
  - internal-clique cluster
- compare the best of those loops directly against verifier-compilation style
  loops on shared bounded corpora

### Cograph closure frontier

Hypothesis:

- recursive union-and-join closure should capture a large part of the optimal
  pair-witness frontier, because it already contains both:
  - cluster loops
  - multipartite loops

Current status:

- exact cograph frontier law now survives:
  - full hit on:
    - `2 <= n <= 4`
  - one miss each on:
    - `(5, 5)`
    - `(6, 8)`
    - `(7, 10)`

Why this matters:

- the branch now has a real recursive loop family, not only flat pair bases
- the remaining gap is small and structured

Next ideas:

- explain the missing rung structurally
- compare cograph loops directly against verifier-compilation style loops

### Clique-bridge repair frontier

Hypothesis:

- the missing rung above cographs is a small bridge gadget between otherwise
  exact witness cells

Current status:

- exact clique-bridge law now survives:
  - `B(a, b)` hits the exact global optimum for every:
    - `a, b >= 1`
    - `a + b <= 7`
- exact formulas survive for:
  - witness count
  - residual size
  - pure classes

Why this matters:

- this is a better loop family than plain cographs on the checked domain
- it suggests that a small amount of controlled non-cograph structure can be
  enough

Next ideas:

- tree-of-cliques ladders
- block-graph ladders
- compare:
  - cographs
  - clique bridges
  - verifier-compilers

### Two-family frontier cover baseline

Hypothesis:

- the checked optimal pair-witness frontier may already be compactly covered by
  a very small family basis

Current status:

- exact two-family cover now survives on:
  - `2 <= n <= 7`
- cographs plus clique bridges cover all:
  - `62`
  checked frontier budgets
- bridge-only repairs are exactly:
  - `(5, 5)`
  - `(6, 8)`
  - `(7, 10)`

Why this matters:

- the branch now has a compact frontier baseline
- new loop families should be judged against:
  - cographs
  - clique bridges
  rather than against generic graph search

Next ideas:

- find the smallest recursive closure containing both:
  - cographs
  - clique bridges
- test whether that closure is a better teaching object than either family
  alone
- compare the two-family baseline directly against verifier-compilation style
  loops

### Bridge-cograph recursive baseline

Hypothesis:

- the two-family cover may itself be compressible into one recursive closure

Current status:

- exact bridge-cograph frontier law now survives on:
  - `2 <= n <= 7`
- bridge-cographs are generated from:
  - disjoint union
  - complete join
  - single-edge join
- full checked frontier hit survives across all checked budgets

Why this matters:

- the branch now has a single recursive baseline instead of a two-family patch
- the next question is compression inside that closure, not whether a larger
  graph family exists

Next ideas:

- find a smaller exact subfamily inside bridge-cographs
- identify whether the frontier-optimal bridge-cographs admit a cleaner grammar
- compare the bridge-cograph baseline directly against verifier-compilation
  style loops

### Twin-pendant compressed baseline

Hypothesis:

- the bridge-cograph closure may admit a much smaller exact local growth
  grammar

Current status:

- exact twin-pendant frontier law now survives on:
  - `2 <= n <= 7`
- the new largest-labeled vertex is added only as:
  - a pendant
  - a false twin
  - a true twin
- full checked frontier hit still survives

Why this matters:

- the branch now has a compressed recursive baseline
- the next question is whether this grammar is still reducible, or already the
  right minimal teaching object

Next ideas:

- search whether one of:
  - pendant
  - false twin
  - true twin
  can be weakened or derived without losing frontier coverage
- compare the twin-pendant baseline directly against verifier-compilation style
  loops

### Twin-pendant move minimality

Hypothesis:

- one of the three local moves in the twin-pendant grammar might be redundant

Current status:

- exact move-necessity law now survives on:
  - `2 <= n <= 7`
- only the full triple:
  - pendant
  - false twin
  - true twin
  covers the whole checked frontier
- strongest strict subset is the twin-only pair, and it fails exactly on the
  old bridge budgets

Why this matters:

- the branch now has a checked-minimal operator baseline
- the next reduction target should be normal forms, not just dropping moves

Next ideas:

- search for canonical decomposition rules inside twin-pendant growth
- look for equivalence classes of growth traces that preserve frontier quality
- compare the checked-minimal grammar directly against verifier-compilation
  style loops

### One-pendant normal form

Hypothesis:

- the full twin-pendant baseline may still be compressible to one exceptional
  pendant event plus arbitrary twin growth

Current status:

- exact single-pendant frontier law now survives on:
  - `2 <= n <= 7`
- no-pendant twin growth fails exactly on the bridge budgets
- one pendant event restores the whole checked frontier

Why this matters:

- the branch now has a sharper normal-form target
- the next reduction question is where the one pendant belongs, not how many
  pendant events are needed

Next ideas:

- search for a canonical placement rule for the single pendant event
- test whether the pendant can be forced to occur before or after all twin
  moves without losing frontier coverage
- compare the one-pendant twin baseline directly against verifier-compilation
  style loops

### Late-pendant normal form

Hypothesis:

- the single pendant may be delayable to a short tail of the growth trace

Current status:

- exact late-pendant law now survives on:
  - `2 <= n <= 7`
- final-step-only fails only on:
  - `(7, 10)`
- final-two-steps already recover the whole checked frontier

Why this matters:

- the branch now has a sharper timing normal form
- the next reduction target is anchor choice, not coarse placement

Next ideas:

- search whether the late pendant can be forced to attach to a special anchor
  class
- search whether the `(7, 10)` miss identifies the only obstruction to
  final-step placement
- compare the late one-pendant baseline directly against verifier-compilation
  style loops

### Root-anchored late-pendant normal form

Hypothesis:

- the late pendant may be anchorable to a single canonical root vertex

Current status:

- exact root-anchored late-pendant law now survives on:
  - `2 <= n <= 7`
- root-anchored final-step-only fails only on:
  - `(7, 10)`
- root-anchored final-two-steps recover the whole checked frontier

Why this matters:

- the branch now has a much sharper anchor normal form
- the next reduction target is the special final-step obstruction, not generic
  anchor choice

Next ideas:

- analyze the `(7, 10)` witness to explain why root anchoring needs the
  penultimate step there
- compare root anchor against other successful anchor rules such as minimum
  degree
- compare the root-anchored late-pendant baseline directly against
  verifier-compilation style loops

### Exact obstruction at `(7,10)`

Hypothesis:

- the final-step root-anchor miss should decompose into a clean structural
  obstruction, not just a numerical gap

Current status:

- exact obstruction law now survives:
  - every optimum at `(7,10)` is leafless
  - the pendant-used final-step branch is blocked by that leaflessness
  - the no-pendant branch is capped at the twin-only ceiling

Why this matters:

- the branch now has an exact reason for the last miss
- the next question is constructive:
  - why penultimate-step pendant use fixes it

Next ideas:

- reconstruct an explicit penultimate-step repair trace for the optimum budget
- identify whether the repair always uses:
  - a pendant
  - followed by a true-twin lift
- compare the repaired normal form directly against verifier-compilation style
  loops

### Exact repair motif at `(7,10)`

Hypothesis:

- the repaired branch should collapse to one local motif, not many unrelated
  two-step endings

Current status:

- exact repair-motif law now survives:
  - only `pendant -> true_twin` reaches `109`
  - all other final-two-step patterns are capped at `107`
  - the optimum inside the family collapses to:
    - `2` traces
    - `1` graph

Why this matters:

- the branch now has its first exact constructive repair motif
- this suggests a new search direction:
  - motif libraries above compressed normal forms

Next ideas:

- search for other focused budgets where a single repair motif explains the
  last remaining miss
- compare motif-repaired compressed loops against verifier-compilation style
  loops

### Bridge-budget motif library

Hypothesis:

- the repaired bridge budgets may share a short exact motif ladder

Current status:

- exact motif-narrowing law now survives:
  - `(5, 5)`:
    - `pendant -> true_twin`
    - `true_twin -> pendant`
  - `(6, 8)`:
    - `pendant -> true_twin`
    - `true_twin -> pendant`
  - `(7, 10)`:
    - `pendant -> true_twin`

Why this matters:

- the branch now has a small exact motif library, not just one repaired budget
- this suggests that motif families may be a better search object than broader
  graph grammars

Next ideas:

- search for motif ladders on other repaired budget families
- compare motif-library loops directly against verifier-compilation style
  baselines

### Direct controller comparison frontier

Hypothesis:

- at least some hybrid loops now beat direct compiled controllers on a clean
  exact metric, not only by informal intuition

Current status:

- exact hybrid-controller advantage law now survives:
  - direct raw-family block controller:
    - `n`
  - hybrid pair-basis plus block residual controller:
    - `ceil(log2 n)`
  - scope:
    - controller depth only
    - pair observations treated as already available loop state

Why this matters:

- this is the first honest direct comparison theorem on the branch
- it supports the claim that some hybrid loops are stronger than plain direct
  controllers in a real bounded sense

Next ideas:

- extend the same style of comparison to motif-library loops
- search for cost models that combine:
  - witness acquisition
  - pure resolved mass
  - residual controller depth

### Weighted loop-value frontier

Hypothesis:

- the right comparison object is not raw controller size, but a weighted loop
  value that keeps acquisition, pure resolved mass, and residual depth
  separate

Current status:

- exact weighted hybrid-value law now survives:
  - `U = alpha * pure_resolved_mass + beta * depth_saving - gamma * acquisition`
  - pair-plus-block beats direct exactly on a closed-form boundary
  - pair-plus-block weakly dominates pair-plus-atom under unit weights, and
    strictly so for `n >= 4`

Why this matters:

- the branch now has an honest explicit cost model
- this is the right bridge from quotient-question loops to motif-library
  comparisons

Next ideas:

- assign the same three-part cost model to motif-library loops
- compare the best motif-library baseline directly against verifier-compilation
  style controllers

### Motif-side pricing frontier

Hypothesis:

- the motif branch should not be ranked only by raw witness count or pure mass
- it should admit the same weighted phase boundaries as the quotient-question
  branch

Current status:

- exact bridge-budget pricing law now survives for clique bridges:
  - clique-bridge beats direct on all three bridge budgets under unit weights
  - pair-plus-block still has the higher unit value
  - clique-bridge wins exactly when acquisition price is high enough

Why this matters:

- the branch now has its first motif-side phase boundary
- this is the first clean comparison where a motif family is competitive for a
  principled reason, not by style

Next ideas:

- price balanced multipartite and later motif families in the same way
- search for a motif family that beats pair-plus-block under unit or near-unit
  weights

### Balanced weighted frontier

Hypothesis:

- the balanced ladder should admit a clean family-level weighted frontier, not
  only isolated sparse-versus-dense tradeoffs

Current status:

- exact balanced weighted-frontier law now survives on the checked grid:
  - full pair is always unit-weight optimal or tied
  - from `n = 5` onward, a near-dense sparse rung already catches it at unit
    weights
  - and overtakes when:
    - `gamma > alpha`
    - under `alpha = beta = 1`

Why this matters:

- the branch now has a family-level weighted frontier, not just one motif-side
  pricing result
- this sharpens the next question:
  - can any exact family actually beat pair-plus-block on unit or near-unit
    weights

Next ideas:

- widen the same weighted pricing to more exact families
- search for the first unit-weight overtake, if it exists

### Pair-graph purity correction

Hypothesis:

- the graph-shaped pair branch should be rebuilt on the true observation map,
  not on the edge-containing proxy

Current status:

- exact correction now survives:
  - for pair-witness graphs under `O_G(M) = E(G[M])`,
    `M` is pure iff `M` is a total dominating set of `G`
  - exhaustive support:
    - `2 <= n <= 6`
  - proxy failures already appear on:
    - one-edge `n = 3`
    - clique-bridge `B(3, 2)`

Why this matters:

- this changes what graph-shaped loop quality is actually measuring
- the live graph object is total domination, not “contains a witness edge”

Next ideas:

- rebuild graph-family frontier search on total domination counts
- quarantine proxy-branch claims until revalidated

### Corrected balanced graph frontier

Hypothesis:

- the balanced complete multipartite ladder might survive the correction even
  if the older proxy graph branch does not

Current status:

- exact corrected frontier check now survives on:
  - `2 <= n <= 6`
- every balanced ladder budget hits the exhaustive true frontier on that
  domain

Why this matters:

- this restores one clean graph-family ladder as a trustworthy live candidate
- it narrows the next search target to non-balanced families that can beat the
  corrected balanced ladder

Next ideas:

- extend the corrected frontier to `n = 7`
- test whether any non-balanced graph family genuinely improves on the
  corrected balanced ladder

### Corrected complete multipartite frontier

Hypothesis:

- the full complete multipartite family may already be the right corrected
  graph-side baseline, not only the balanced slice

Current status:

- exact corrected frontier check now survives on:
  - `2 <= n <= 6`
- every complete multipartite budget hits the exhaustive true frontier on that
  domain

Why this matters:

- this is the cleanest trustworthy graph-family frontier on the branch so far
- it narrows the next search target to the uncovered budgets rather than the
  whole graph space

Next ideas:

- extend the corrected complete multipartite frontier to `n = 7`
- search uncovered budgets for genuinely non-complete-multipartite families

### Corrected complete multipartite extension

Hypothesis:

- the corrected complete multipartite frontier might survive at `n = 7`, not
  just `n <= 6`

Current status:

- exact corrected frontier extension now survives on:
  - `2 <= n <= 7`
- every represented complete multipartite budget still hits the exhaustive true
  frontier

Why this matters:

- the corrected graph baseline is now large enough to compare directly against
  the old proxy branch

Next ideas:

- search repaired edge families above the corrected multipartite baseline

### One-edge repaired multipartite branch

Hypothesis:

- a very small edge repair above complete multipartite graphs might already
  explain more of the corrected frontier

Current status:

- exact large-block edge invariance law now survives:
  - one internal edge inside a block of size at least `3` preserves true pure
    mass
- exact one-edge family cover law now survives:
  - complete multipartite plus one internal edge hits the true frontier at
    every budget it defines on `2 <= n <= 7`
- remaining uncovered `n = 7` budgets:
  - `2, 3, 4, 5, 8, 9`

Why this matters:

- this is the strongest corrected graph-family cover on the branch so far
- the live search target is now a very small uncovered budget set

Next ideas:

- search two-edge or other low-complexity repairs above the one-edge repaired
  multipartite baseline

### Two-edge repaired multipartite frontier

Hypothesis:

- two repaired internal edges above the multipartite baseline may already close
  most of the remaining corrected graph frontier

Current status:

- exact two-edge repaired-family cover now survives on:
  - `2 <= n <= 7`
- remaining uncovered `n = 7` budgets:
  - `3, 4, 5, 9`

Why this matters:

- the live corrected graph-side search target is now only four budgets
- this is the strongest repaired-family cover on the branch so far

Next ideas:

- search exact low-complexity families targeted only at:
  - `3, 4, 5, 9`

### Star-side decomposition

Hypothesis:

- the remaining high star-side holdouts should have a clean additive law

Current status:

- exact star-plus-leaf-graph law now survives:
  - `TD(G) = (2^k - 1) + TD(H)`
  - exhaustive support:
    - `1 <= k <= 6`
- this explains:
  - budget `8` as a star with leaf correction `TD(H) = 0`
  - budget `9` as a star with leaf correction `TD(H) = 1`

Why this matters:

- the star-side frontier is now a leaf-graph optimization problem

Next ideas:

- classify the best leaf graphs at fixed leaf-edge budget
- use that to attack budget `9` and related future holdouts directly

### Disconnected corrected graph product geometry

Hypothesis:

- the corrected graph branch should factor multiplicatively across disjoint
  components

Current status:

- exact product law now survives:
  - `TD(G union H) = TD(G) * TD(H)`
  - exhaustive support:
    - `1 <= |V(G)| <= 4`
    - `1 <= |V(H)| <= 4`

Why this matters:

- disconnected corrected graph search no longer needs to be treated as one
  flat frontier
- it gives the right algebra for low-edge component optimization

Next ideas:

- turn the low-edge side into a direct formula rather than another family scan

### Low-edge balanced star-forest regime

Hypothesis:

- the corrected low-edge frontier should be a balanced star-forest law

Current status:

- exact checked frontier law now survives on:
  - `2 <= n <= 7`
  - `0 <= m <= n - 1`
- threshold law:
  - frontier is `0` below `m < ceil(n / 2)`
- direct amount law above threshold:
  - `F_bal(n, m) = (2^(q - 1) - 1)^(c - r) * (2^q - 1)^r`
  - with:
    - `c = n - m`
    - `n = c*q + r`
- corrected `n = 7` consequences:
  - `m = 4 -> 3`
  - `m = 5 -> 21`
  - `m = 6 -> 63`
- leaf consequence:
  - `F_bal(6, 3) = 1`

Why this matters:

- the low-budget corrected holdouts:
  - `3, 4, 5`
  are no longer open
- together with the star-plus-leaf law, the corrected `n = 7`, budget `9`
  optimum is also explained

Next ideas:

- unify the corrected graph branch into a regime map:
  - low-edge balanced star forests
  - repaired multipartite families
  - star-plus-leaf corrections
- then search higher-budget exact families beyond the current repaired
  multipartite ladder

### Corrected small-n graph regime map

Hypothesis:

- the corrected graph branch may already admit a coherent small-`n` regime map

Current status:

- exact checked regime cover now survives on:
  - `2 <= n <= 7`
- every exact frontier budget is covered by at least one of:
  - low-edge balanced star forests
  - complete multipartite plus up to two internal edges
  - a star plus a low-edge leaf correction

Why this matters:

- the branch now ends in one clean synthesis object, not only local repairs

Next ideas:

- extend the regime cover beyond `n = 7`
- or compress the higher-budget repaired multipartite side into a cleaner
  direct law

### Repaired-multipartite additivity

Hypothesis:

- the corrected repaired multipartite side may decompose exactly by repaired
  blocks

Current status:

- exact additive law now survives on every nontrivial partition with:
  - `2 <= n <= 7`
- law:
  - `TD(G) = base(P_1, ..., P_t) + sum_i TD(H_i)`

Why this matters:

- the repaired multipartite side now has one clean structural law rather than
  only cover-style results

Next ideas:

- turn that additive law into a direct optimizer on a significant internal
  budget regime

### Low-edge repaired-multipartite optimizer

Hypothesis:

- the repaired multipartite side should admit a direct optimizer once every
  repaired block stays in the low-edge regime

Current status:

- exact optimizer now survives on every nontrivial partition with:
  - `2 <= n <= 7`
- law:
  - `OPT(parts; e_1, ..., e_t) = base(parts) + sum_i F_bal(s_i, e_i)`
  - for:
    - `0 <= e_i <= s_i - 1`

Why this matters:

- the corrected graph branch now has a direct amount law on one major repaired
  subfamily

Next ideas:

- extend the optimizer beyond the low-edge internal-budget regime
- or extend the corrected regime map beyond `n = 7`

### Repaired-multipartite recursive optimizer

Hypothesis:

- the repaired multipartite side should stay blockwise exact even without the
  low-edge restriction

Current status:

- exact recursive optimizer now survives on every nontrivial partition with:
  - `2 <= n <= 7`
- law:
  - `OPT_repaired(parts; e_1, ..., e_t) = base(parts) + sum_i OPT_graph(s_i, e_i)`

Why this matters:

- the repaired side is now reduced to the one-block frontier

Next ideas:

- compress the single-block frontier `OPT_graph(s, e)` itself
- or extend the corrected regime map beyond `n = 7`

### Threshold-to-split collapse on the corrected single-block frontier

Hypothesis:

- split graphs might recover the corrected single-block budgets missed by
  threshold graphs

Current status:

- false on the checked domain:
  - `2 <= n <= 7`
- stronger corrected survivor:
  - threshold and split graphs attain exactly the same frontier value at every
    checked budget
- shared miss budgets remain:
  - `n = 4`: `2, 4`
  - `n = 5`: `3, 6, 8`
  - `n = 6`: `3, 4, 8, 9, 10, 11, 12, 13`
  - `n = 7`: `4, 5, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19`

Why this matters:

- the corrected single-block search should not spend more effort inside the
  threshold-to-split ladder

Next ideas:

- search genuinely non-split single-block families
- or synthesize a direct regime map for `OPT_graph(s, e)`

### Corrected small-domain single-block compiler

Hypothesis:

- the corrected single-block frontier may already collapse to a direct
  max-over-regimes compiler on the checked small domain

Current status:

- yes on:
  - `2 <= n <= 7`
- exact compiler:
  - max of:
    - balanced star forests
    - complete multipartite plus up to two internal edges
    - full star plus low-edge leaf correction

Why this matters:

- the corrected graph branch now has a direct amount compiler, not only a
  regime cover

Next ideas:

- compress the third regime if possible
- or extend the direct law beyond `n = 7`

### One-point correction compression

Hypothesis:

- the full-star-plus-leaf regime may only be needed on a tiny exceptional set

Current status:

- yes on the checked domain:
  - `2 <= n <= 7`
- removing that regime leaves exactly one miss:
  - `(7, 9)`
- exact one-point compiler now survives:
  - balanced star forests
  - multipartite plus up to two internal edges
  - explicit correction `(7, 9) -> 64`

Why this matters:

- this is the cleanest small-domain endpoint on the corrected graph branch

Next ideas:

- explain why `(7, 9)` is exceptional
- or test whether that point-style correction persists beyond `n = 7`

### Exceptional point motif at `(7, 9)`

Hypothesis:

- the lone point correction in the corrected single-block compiler may have a
  unique structural shape

Current status:

- yes on the checked exceptional point:
  - `(7, 9)`
- every optimum is isomorphic to:
  - a full star plus a perfect matching on the six leaves
- optimal labeled graph count:
  - `105`
- optimal isomorphism type count:
  - `1`

Why this matters:

- the point correction is now structurally named

Next ideas:

- test whether this star-plus-perfect-matching motif persists on larger odd
  cases
- or derive a local reason why it appears exactly at `(7, 9)`

### Star-plus-perfect-matching family law

Hypothesis:

- the exceptional-point motif may itself admit a closed-form exact value law

Current status:

- yes
- for the family `F_r`:
  - `TD(F_r) = 2^(2r)`
- checked for:
  - `1 <= r <= 6`

Why this matters:

- the point correction is now attached to a reusable family, not just one
  named graph

Next ideas:

- compare the family with the checked frontier at odd points
- or search for nearby motif families that improve on it where it is not
  frontier-optimal

### Odd-line selector inside the current compiler family

Hypothesis:

- the odd-line behavior of the corrected compiler family may already admit a
  simple structural selector

Current status:

- yes on checked `1 <= r <= 8`
- on `n = 2r + 1`, `m = 3r`:
  - balanced star forests are never available
  - multipartite plus up to two internal edges is reachable iff `r <= 2`
  - star-plus-leaf has value `2^(2r)`
  - selector:
    - tie at `r = 1`
    - multipartite win at `r = 2`
    - star-plus-leaf only from `r >= 3`

Why this matters:

- the odd-line switch at `r = 3` is now explained inside the current compiler
  family

Next ideas:

- compare the star-plus-matching family to the true frontier at larger odd
  points
- or search nearby odd-line motif families

### Full-star-plus-low-edge family compiler

Hypothesis:

- the odd-line perfect-matching branch may be one slice of a wider exact
  star-plus-leaf band

Current status:

- yes on checked:
  - `2 <= n <= 8`
  - `n - 1 <= m <= 2n - 3`
- exact family law:
  - `OPT_star_leaf(n, m) = (2^(n - 1) - 1) + F_bal(n - 1, m - (n - 1))`
- below the leaf no-isolate threshold:
  - the family collapses to the plain star value

Why this matters:

- the star-plus-leaf branch is now a real reusable compiler family
- the odd-line matching case is one middle rung, not the whole story

Next ideas:

- compare the full-star-plus-low-edge family to the true frontier on the
  checked overlap
- or search where it stops being frontier-optimal away from the odd line

### High-band two-regime overlap compiler

Hypothesis:

- the checked high single-block band may reduce to a direct competition
  between only two exact regimes

Current status:

- yes on checked:
  - `2 <= n <= 7`
  - `n - 1 <= m <= 2n - 3`
- exact checked overlap compiler:
  - `OPT_graph(n, m) = max(OPT_star_leaf(n, m), multipartite_plus_two_internal(n, m))`
- representative selector rows:
  - `n = 7, m = 9`:
    - star-plus-low-edge
  - `n = 7, m = 10`:
    - repaired multipartite
  - `n = 7, m = 11`:
    - tie

Why this matters:

- the overlap band can now be taught as one real selector problem
- the graph-side hybrid story is cleaner than before

Next ideas:

- compress the selector into a direct arithmetic rule
- or test whether the same two-regime picture survives beyond the checked
  small domain

### High-band selector stripe map

Hypothesis:

- inside the checked two-regime overlap, the selector may already compress to
  one stripe plus a few exceptions

Current status:

- yes on checked:
  - unique star row:
    - `(7, 9)`
  - unique multipartite rows:
    - the stripe `m = 2n - 4`
    - plus `(6, 9)`
  - ties elsewhere

Why this matters:

- the hybrid graph branch is much easier to teach if the overlap is a selector
  map instead of a report table

Next ideas:

- search for a direct selector formula beyond the checked slice
- or explain why `(6, 9)` and `(7, 9)` are the first off-stripe exceptions

### Extended two-family overlap selector

Hypothesis:

- once the graph branch is reduced to the star-plus-low-edge and repaired
  multipartite family compilers, the selector may become piecewise simple on a
  wider checked domain

Current status:

- yes on checked:
  - ties at:
    - `m = n - 1, n, n + 1, 2n - 3`
  - multipartite-only at:
    - `m = 2n - 4`
  - star-only in the middle interval:
    - `n + 2 <= m <= 2n - 5`

Why this matters:

- the two-family overlap is no longer just a set of checked rows
- it now behaves like a real selector law

Next ideas:

- test whether the full frontier still agrees with this two-family max beyond
  the exact `v224` slice
- or derive the selector directly from the family formulas

### Extended two-family overlap family compiler

Hypothesis:

- the checked two-family graph overlap may itself collapse to a small direct
  amount compiler

Current status:

- yes on checked:
  - low plateau:
    - `2^(n - 1) - 1`
  - middle interval:
    - delegate to `OPT_star_leaf(n, m)`
  - near-top peak:
    - `3 * 2^(n - 2) - 3`
  - top tie:
    - `3 * 2^(n - 2) - 2`

Why this matters:

- this is a much cleaner teaching object than an overlap table or raw selector
  chart

Next ideas:

- test whether the full frontier still follows the same piecewise compiler
- or prove the same compiler directly from the family formulas

### Repaired-multipartite high-band law

Hypothesis:

- the repaired multipartite side of the overlap may have its own tiny direct
  compiler

Current status:

- yes on checked:
  - available at:
    - `m = n - 1, n, n + 1, 2n - 4, 2n - 3`
  - missing in the whole middle gap:
    - `n + 2 <= m <= 2n - 5`
  - exact values:
    - `2^(n - 1) - 1`
    - `3 * 2^(n - 2) - 3`
    - `3 * 2^(n - 2) - 2`

Why this matters:

- it explains one whole side of the widened overlap compiler directly

Next ideas:

- derive the widened overlap compiler from this law plus the star family law
- or compare the widened overlap compiler against the full frontier on the next
  honest exact slice

### Checked tree-star dominance

Hypothesis:

- the star may be the connected maximizer in the tree regime, which would make
  the low-edge star-forest law much less mysterious

Current status:

- yes on checked:
  - `2 <= n <= 8`
  - largest scan:
    - `262144` connected trees at `n = 8`
  - exact checked optimum:
    - `2^(n - 1) - 1`

Why this matters:

- it opens a proof-oriented rabbit hole instead of another frontier scan

Next ideas:

- search for a structural proof of tree-star dominance
- then lift that into a proof route for the balanced star-forest low-edge law

### Non-star tree extremal gap

Hypothesis:

- once the star is removed, the whole remaining tree family may already drop by
  an exact factor of two

Current status:

- yes on checked:
  - `4 <= n <= 8`
  - best non-star tree value:
    - `2^(n - 2)`
  - equality family:
    - double-stars

Why this matters:

- the tree branch now has a real second rung and a concrete equality family

Next ideas:

- search for a local concentration move that improves total-domination count
  toward double-stars and stars
- or prove the factor-of-two gap recursively

### Pendant-subtree concentration

Hypothesis:

- pendant-subtree transfers may be the right local move language on the tree
  branch, even though simple leaf transfers fail

Current status:

- yes on checked:
  - `4 <= n <= 8`
  - every non-star unlabeled class has a move with:
    - `TD(T') >= TD(T)`
    - `Phi(T') > Phi(T)`
  - every checked class reaches the star

Why this matters:

- this is the first proof-shaped concentration mechanism on the corrected tree
  branch

Next ideas:

- extend the checked concentration law beyond `n <= 8`
- search for a cleaner invariant than degree-square concentration

### Star-forest balancing

Hypothesis:

- the balanced star-forest formula may be exact because the star-family product
  is smoothing-improvable

Current status:

- yes on checked profiles:
  - balanced profile is the exact star-family optimizer
  - checked on:
    - `2 <= c <= 8`
    - `2c <= n <= 20`

Why this matters:

- it turns the low-edge formula into an exact family optimizer instead of only
  a frontier coincidence

Next ideas:

- combine component starification with this exact balancing law into one low-edge
  concentration mechanism

### Two-stage low-edge concentration

Hypothesis:

- the low-edge forest branch may be teachable as:
  - starify components
  - then balance star sizes

Current status:

- yes on checked:
  - `2 <= n <= 8`
  - `ceil(n / 2) <= m <= n - 1`
  - every unlabeled forest class is covered by the two-stage path schema

Why this matters:

- this gives the low-edge branch an actual mechanism, not only a frontier law

Next ideas:

- turn this into a visual tutorial sequence
- then return to the higher-budget graph side with a stronger proof scaffold

### Pendant-subtree concentration, `n = 9`

Hypothesis:

- the pendant-subtree concentration law may keep surviving well beyond the
  original checked tree range

Current status:

- yes on checked:
  - `n = 9`
  - full labeled scan:
    - `4,782,969`
  - unlabeled classes:
    - `47`
  - every class still reaches the star

Why this matters:

- the next honest branch is proof-oriented, not just “scan one more rung”

Next ideas:

- search for a structural proof of the pendant-subtree concentration law
- only if that stalls, push the scan one more rung

### Hub-target concentration

Hypothesis:

- the checked pendant-subtree law may admit a much cleaner target rule:
  always move toward a maximum-degree hub

Current status:

- yes on checked:
  - `n in {8, 9}`
  - every non-star class has an improving hub-target move
- stronger target simplifications fail on the same checked domain

Why this matters:

- the branch is now much more teachable and plausibly provable

Next ideas:

- search for a structural proof of the hub-target law
- then try to compress the source-side choice

### One-branch hub-target concentration

Hypothesis:

- the checked hub-target law may admit a source-side compression too:
  the moved subtree might only need one branching vertex

Current status:

- yes on checked:
  - `n in {8, 9}`
  - every non-star class has an improving hub-target move whose moved subtree
    has at most one branching vertex
- stronger source-side simplifications fail on the same checked domain:
  - leaf-only hub moves
  - pendant-star hub moves

Why this matters:

- the tree-side move language is now much smaller and more geometric
- the surviving local mechanism is close to a proof narrative:
  move a broom-like pendant subtree into a hub

Next ideas:

- search for a structural proof of the one-branch hub-target law
- test whether the source side compresses one more rung, for example by a
  depth bound or a unique branch-point rule

### One-branch hub-to-balance mechanism

Hypothesis:

- once one-branch hub-target concentration survives on components, the full
  low-edge forest branch should inherit a cleaner two-stage mechanism

Current status:

- yes on checked:
  - `2 <= n <= 8`
  - positive low-edge forests
  - stage 1: one-branch hub-target concentration on connected components
  - stage 2: exact balancing on the star-family side

Why this matters:

- the low-edge branch is now teachable as one compact mechanism
- it is no longer only a compiler fit and no longer only a generic monotone
  path claim

Next ideas:

- search for a direct proof of the full low-edge mechanism from:
  - one-branch hub concentration
  - star-size balancing

### One-branch hub-target concentration path

Hypothesis:

- the smaller move language from `v237` might already be complete enough to run
  the whole checked tree concentration path

Current status:

- yes on checked:
  - `n in {8, 9}`
  - every unlabeled tree class reaches the star through finite monotone
    one-branch hub-target moves

Why this matters:

- the tree-side branch no longer needs arbitrary pendant-subtree moves even for
  the full path, not just for a single local step
- this is much closer to a proof-grade local rewrite system

Next ideas:

- search for a structural proof of the one-branch hub-target path law
- then lift that proof into the full low-edge forest mechanism

### Minimal-size one-branch hub-target path

Hypothesis:

- the restricted rewrite system from `v239` might survive one more local
  restriction, using only smallest available one-branch hub-target moves

Current status:

- yes on checked:
  - `n in {8, 9}`
  - every unlabeled tree class still reaches the star through finite monotone
    minimal-size one-branch hub-target moves

Why this matters:

- the tree-side branch now looks less like a loose rewrite family and more like
  a local controller
- this is the strongest proof-oriented compression on the checked tree branch
  so far

Next ideas:

- search for a structural proof of the minimal-size path law
- then test whether that minimal rule lifts cleanly to the low-edge forest
  mechanism

### Depth-2 cutoff for the minimal tree controller

Hypothesis:

- the minimal one-branch hub-target controller from `v240` may admit a finite
  exact branch-depth cutoff

Current status:

- yes on checked:
  - `d = 0` fails
  - `d = 1` fails
  - `d = 2` survives
  - checked on `n in {8, 9}`

Why this matters:

- this is the first exact local depth threshold on the checked tree branch
- the local controller now has a real finite shape cutoff, not only a grammar

Next ideas:

- search for a structural proof that depth `2` is sufficient and depth `1` is
  not
- then lift the depth-2 controller into the low-edge forest mechanism

### Depth-2 hub-to-balance mechanism

Hypothesis:

- once the tree-side controller has an exact checked depth cutoff, the full
  low-edge forest mechanism should inherit that sharper controller

Current status:

- yes on checked:
  - `2 <= n <= 8`
  - positive low-edge forests
  - stage 1: minimal-size one-branch hub-target concentration with branch-depth
    bound `2`
  - stage 2: exact star-size balancing

Why this matters:

- the low-edge branch now has a sharper executable controller candidate

Next ideas:

- prove the depth-2 tree controller
- then prove the composed low-edge mechanism

### Terminal-cherry ladder explanation

Hypothesis:

- the depth cutoff from `v242` may be explained by a named obstruction family,
  not only by isolated small examples

Current status:

- yes on checked terminal-cherry ladders:
  - minimal move size is exactly `h + 3`
  - branch depth is exactly `h`
  - checked on `h = 0..5`

Why this matters:

- the `h = 2` rung cleanly explains why depth `1` fails and depth `2` survives
  on the checked tree branch
- the cutoff now has a family-level geometric witness

Next ideas:

- use the terminal-cherry ladder as the negative side of a proof for the
  depth-2 cutoff
- then search for the matching positive proof template

### Exact template necessity

Hypothesis:

- the finite rewrite alphabet from `v245` might still contain slack, so a
  smaller exact controller subset could survive

Current status:

- no on checked connected trees with `n in {8, 9}`:
  - the exact subset lattice has one survivor only
  - the full five-template alphabet is the unique surviving subset

Why this matters:

- the local controller is already minimal at the template level on the checked
  branch
- the proof frontier is now sharper, necessity and sufficiency for one explicit
  five-template basis

Next ideas:

- prove necessity template-by-template
- prove sufficiency of the full five-template controller
- then lift that proof into the low-edge forest mechanism

### Template-specific obstruction witnesses

Hypothesis:

- each necessary template should have a small explicit failure witness when
  removed

Current status:

- yes on checked connected trees with `n in {8, 9}`:
  - every removed template has a failing witness
  - first failures:
    - `broom_2` and `three_leaf_star` first fail at `n = 9`
    - `broom_1`, `cherry`, and `leaf` first fail at `n = 8`

Why this matters:

- the proof branch no longer needs to argue necessity abstractly
- it can now target five explicit obstruction shapes

Next ideas:

- group the five witnesses into a smaller structural taxonomy
- then prove the full controller by necessity and sufficiency

### First obstruction-family taxonomy

Hypothesis:

- the five first obstruction witnesses may already collapse into a small family
  list

Current status:

- yes on the checked first-witness catalog:
  - `terminal_cherry_ladder(h)` covers `cherry`, `broom_1`, `broom_2`
  - `subdivided_double_star(3, 3)` covers `three_leaf_star`
  - `endpoint_leaf_path(6)` covers `leaf`

Why this matters:

- the proof branch is no longer stuck with five unrelated witness shapes

Next ideas:

- compress those families into a smaller macro taxonomy
- then use that split to organize the proof

### Two-macro-family obstruction split

Hypothesis:

- the obstruction side may really separate into one-ended versus two-ended
  failures

Current status:

- yes on the checked first obstruction catalog:
  - four templates are one-ended terminal-fan obstructions
  - `leaf` is the only two-ended endpoint-leaf obstruction

Why this matters:

- the proof search can now be split by obstruction polarity, not only by raw
  template name

Next ideas:

- prove the one-ended terminal-fan side
- prove the two-ended endpoint-leaf side
- then combine them into the full controller proof

### Non-leaf terminal-fan boundary

Hypothesis:

- all non-leaf failing classes might already be terminal-fans

Current status:

- almost, but not fully:
  - exact for `broom_2`, `broom_1`, `three_leaf_star`
  - exact for `cherry` at `n = 8`
  - one non-terminal-fan exception for `cherry` at `n = 9`

Why this matters:

- the non-leaf side is now one near-complete family law plus one localized
  exception

Next ideas:

- classify the unique cherry-side exception
- then reduce the non-leaf proof to that decomposition

### Unique cherry-side exception

Hypothesis:

- the lone non-terminal-fan exception on the non-leaf side might itself be one
  small named family

Current status:

- yes on checked:
  - exception count is `1`
  - it matches `split_arm_cherry(2)`

Why this matters:

- the non-leaf necessity side is now almost proof-ready

Next ideas:

- prove the terminal-fan side
- prove the split-arm cherry exception
- then integrate both into the full controller proof

### Non-leaf threshold slices

Hypothesis:

- the terminal-fan side may be controlled by a simple inequality rule on
  normalized coordinates, not only by named examples

Current status:

- yes on checked connected trees with `n in {8, 9}`:
  - `cherry`: `u = 2`, `p >= 2`, `v >= 2`
  - `broom_1`: `u = 2`, `p >= 3`, `v >= 2`
  - `broom_2`: `u = 2`, `p >= 4`, `v >= 2`
  - `three_leaf_star`: `u = 3`, `p >= 2`, `v >= 3`

Why this matters:

- the non-leaf side is now an exact threshold classifier on normalized
  terminal-fan coordinates

Next ideas:

- prove the threshold slices structurally
- explain why `cherry`, `broom_1`, and `broom_2` form a nested path-length
  ladder

### Full non-leaf exact classifier

Hypothesis:

- the full non-leaf failing set may now be closed exactly by adding the
  cherry-side correction term to the threshold picture

Current status:

- yes on checked connected trees with `n in {8, 9}`:
  - three deleted templates are exact threshold slices
  - `cherry` is its threshold slice plus `split_arm_cherry(2)`

Why this matters:

- the descriptive search side of the non-leaf controller analysis is now
  finished

Next ideas:

- prove the threshold slices
- prove the split-arm cherry correction term
- then fold both into the five-template necessity proof

### Non-leaf obstruction ladder

Hypothesis:

- the four non-leaf threshold rules may already collapse into one smaller
  coordinate picture

Current status:

- yes on the checked domain:
  - `broom_2 ⊊ broom_1 ⊊ cherry`
  - `three_leaf_star` is disjoint from that ladder

Why this matters:

- the non-leaf side now looks like one path-length ladder on the two-fan line
  plus one fan-size gate

Next ideas:

- prove the path-length ladder structurally
- prove the fan-size gate structurally
- then integrate both with the split-arm cherry correction

### Terminal-fan selected descent

Hypothesis:

- the non-leaf threshold slices may come from a small deterministic local
  rewrite on the terminal-fan states

Current status:

- yes on the checked non-leaf states:
  - `NTF(2, p, v)` with `p in {2, 3, 4}` selects the template at rung `p`
  - and moves to `NTF(2, p - 1, v + 1)`
  - `NTF(3, 2, 3)` selects `three_leaf_star` and moves to `NTF(3, 1, 4)`

Why this matters:

- the non-leaf side is now a rewrite ladder plus one fan-size gate, not only a
  threshold table

Next ideas:

- prove the selected descent law structurally
- then prove the obstruction slices as cuts in that descent system

### Two-fan ladder cuts

Hypothesis:

- the nested two-fan threshold slices may be exactly the cut sets of the
  selected descent ladder

Current status:

- yes on the checked two-fan line:
  - deleting `cherry` blocks exactly `p >= 2`
  - deleting `broom_1` blocks exactly `p >= 3`
  - deleting `broom_2` blocks exactly `p >= 4`

Why this matters:

- the nested thresholds now have a direct mechanistic explanation

Next ideas:

- prove the cut law on the two-fan descent ladder
- then combine it with the fan-size gate and split-arm cherry correction

### Split-arm feeder

Hypothesis:

- the unique cherry-side correction may feed into the two-fan ladder by one
  selected move

Current status:

- yes on checked:
  - `split_arm_cherry(2)` selects `leaf`
  - and moves to `NTF(2, 2, 4)`

Why this matters:

- the cherry-side correction is now attached to the ladder by a direct local
  mechanism

Next ideas:

- prove the feeder relation structurally
- then combine it with the two-fan cut law

### Cherry-side feeder-cut closure

Hypothesis:

- the full cherry-deleted failing set may now close as ladder cut plus feeder

Current status:

- yes on checked:
  - full `cherry`-deleted failing set is exactly:
    - `NTF(2, p, v)` with `p >= 2`
    - plus `split_arm_cherry(2)`

Why this matters:

- the cherry side is now one mechanistic picture, not threshold table plus
  exception note

Next ideas:

- prove the two-fan ladder
- prove the feeder relation
- prove the fan-size gate
- then combine all three into the five-template necessity proof

### Checked terminal-fan controller family

Hypothesis:

- the selected rows on the non-leaf terminal-fan side may already extend to a
  checked family law

Current status:

- yes on checked `8 <= n <= 12`:
  - `p = 2`: `cherry`
  - `p = 3`: `broom_1`
  - `p = 4`: `broom_2`
  - `p >= 5`: no depth-2 selected move on the checked range
  - `NTF(3, 2, v)`: `three_leaf_star`

Why this matters:

- the non-leaf controller is now described by a checked family law, not only a
  few low-size examples

Next ideas:

- explain the first checked deviation at `NTF(2, 8, 2)` on `n = 13`
- prove the stable family law structurally

### Split-arm feeder family

Hypothesis:

- the cherry-side feeder might extend to a small family

Current status:

- yes on checked `split_arm_cherry(k)` with `2 <= k <= 6`:
  - selected template `leaf`
  - target `NTF(2, 2, k + 2)`

Why this matters:

- the cherry-side correction is now one member of a checked feeder family

Next ideas:

- prove the feeder family structurally
- attach it to the two-fan ladder proof

### Unique checked two-fan anomaly

Hypothesis:

- the stable two-fan controller may have one real checked anomaly rather than a
  broader hidden failure region

Current status:

- yes on checked `8 <= n <= 18`:
  - the only deviation is `NTF(2, 8, 2)` on `n = 13`
  - selected template `broom_2`
  - target outside the terminal-fan family

Why this matters:

- the stable law is sharper than expected
- the anomaly can be studied as one concrete entry state

Next ideas:

- explain the anomaly target structurally
- test whether it enters a named feeder family

### Bridge-fan-tail feeder family

Hypothesis:

- the anomaly target may sit inside a small family with a recursive local rule

Current status:

- yes on the checked bridge-fan-tail family `BFT(r, t)`:
  - checked range:
    - `2 <= r <= 6`
    - `1 <= t <= 5`
    - `n = r + t + 6 <= 15`
  - for `t >= 2`:
    - selected template `leaf`
    - selected target `BFT(r + 1, t - 1)`
  - for `t = 1`:
    - selected template `broom_1`

Why this matters:

- the anomaly target now belongs to a checked feeder family rather than a
  singleton oddity

Next ideas:

- prove the feeder law structurally
- classify the `t = 1` base-line handoff

### Anomaly entry into the feeder chain

Hypothesis:

- the unique anomaly state may be the entry point into the bridge-fan-tail
  family

Current status:

- yes:
  - `NTF(2, 8, 2)` enters `BFT(2, 5)` by a checked `broom_2` move
  - then the checked family chain continues:
    - `BFT(2, 5) -> BFT(3, 4) -> BFT(4, 3) -> BFT(5, 2) -> BFT(6, 1)`

Why this matters:

- the anomaly is now part of a mechanism, not a dead-end exception

Next ideas:

- prove the anomaly entry move
- prove the feeder family
- connect the base line to the remaining necessity proof

### Bridge-fan-tail base-line handoff

Hypothesis:

- the `BFT(r, 1)` base line may hand off to a simple named family instead of an
  unnamed target shape

Current status:

- yes on checked `2 <= r <= 6`:
  - `BFT(r, 1)` selects `broom_1`
  - and lands exactly in `BFS(r + 2)`
  - where `BFS(s)` is the bridge-fan-star family

Why this matters:

- the anomaly chain is now explicit through two named families

Next ideas:

- prove the `BFT(r, 1) -> BFS(r + 2)` handoff
- classify the next local rule on `BFS(s)`
- then fold both into the full necessity proof

### Bridge-fan-star handoff

Hypothesis:

- the `BFS` family may itself have a clean exact local rule

Current status:

- yes on checked `4 <= s <= 10`:
  - `BFS(s)` selects `cherry`
  - and lands exactly in `ADS(s + 1)`

Why this matters:

- the anomaly route now continues through another named family

Next ideas:

- classify the local controller on `ADS`

### Adjacent-double-star handoff

Hypothesis:

- the `ADS` family may have a small exact local rule too

Current status:

- yes on checked `4 <= q <= 11`:
  - `ADS(q)` selects `leaf`
  - and lands exactly in `OLAS(q + 1)`

Why this matters:

- the route stays symbolic and named rather than widening into a residual atlas

Next ideas:

- classify the local controller on `OLAS`

### One-leaf-adjacent-star collapse

Hypothesis:

- the `OLAS` family may collapse directly to the star

Current status:

- yes on checked `5 <= k <= 11`:
  - `OLAS(k)` selects `leaf`
  - and lands directly in the star

Why this matters:

- the named route now closes all the way to the star

Next ideas:

- compress the whole anomaly route as one object

### Anomaly-to-star named route

Hypothesis:

- the anomaly may now factor through a full named route to the star

Current status:

- yes:
  - `NTF(2, 8, 2)`
  - `BFT(2, 5)`
  - `BFT(3, 4)`
  - `BFT(4, 3)`
  - `BFT(5, 2)`
  - `BFT(6, 1)`
  - `BFS(8)`
  - `ADS(9)`
  - `OLAS(10)`
  - star on `n = 13`

Why this matters:

- the anomaly is now a compact named route, not just a local feeder plus
  leftover cases

Next ideas:

- prove the family handoffs structurally
- prove the route composition
- then feed the route proof into the five-template necessity proof

### Bridge-fan-tail route compiler

Hypothesis:

- the route from `BFT(r, t)` to the star may compile from the family
  coordinates alone

Current status:

- yes on checked:
  - `2 <= r <= 6`
  - `1 <= t <= 5`
  - `r + t <= 7`
- exact route word:
  - `leaf^(t - 1) broom_1 cherry leaf leaf`
- exact route length:
  - `t + 3`

Why this matters:

- this is a real symbolic controller object on the anomaly-side route, not
  only a named path

Next ideas:

- widen the downstream tail window
- then widen the whole route compiler

### Extended downstream tail controller

Hypothesis:

- the downstream route families may stay exact on a noticeably wider checked
  window

Current status:

- yes on checked:
  - `BFS(s)` for `4 <= s <= 15`
  - `ADS(q)` for `4 <= q <= 15`
  - `OLAS(k)` for `5 <= k <= 16`
- composed tail is checked for:
  - `4 <= s <= 14`
  - `BFS(s) -> ADS(s + 1) -> OLAS(s + 2) -> star`

Why this matters:

- the back half of the route is now a reusable tail controller block

Next ideas:

- widen the bridge-fan-tail rectangle so the larger tail can actually be used

### Wider bridge-fan-tail route compiler

Hypothesis:

- the bridge-fan-tail route compiler may survive on a wider checked rectangle

Current status:

- yes on checked:
  - `2 <= r <= 7`
  - `1 <= t <= 5`
  - `n = r + t + 6 <= 18`
- exact route word stays:
  - `leaf^(t - 1) broom_1 cherry leaf leaf`
- exact route length stays:
  - `t + 3`

Why this matters:

- the route compiler is no longer confined to the tiny anomaly-adjacent slice

Next ideas:

- prove the feeder law structurally
- prove the widened tail controller structurally
- prove the widened route compiler by composition

### Extended unique two-fan anomaly law

Hypothesis:

- the single checked anomaly on the two-fan line may persist beyond the old
  `n <= 18` window

Current status:

- yes on checked:
  - `8 <= n <= 20`
- there is still exactly one deviation from the stable controller law:
  - `NTF(2, 8, 2)` on `n = 13`

Why this matters:

- the stable two-fan controller plus one named escape state now looks more
  like a real persistence law

Next ideas:

- prove the stable two-fan law structurally
- prove why the unique escape survives
- then compose that with the widened route compiler

### Downstream tail amount law

Hypothesis:

- the named downstream route may already admit exact amount formulas, not only
  checked handoff rules

Current status:

- yes on checked:
  - `TD(BFS(s)) = 7 * 2^s - 3`
  - `TD(ADS(q)) = 2^(q + 2)`
  - `TD(OLAS(k)) = 2^(k + 1)`
  - `TD(star_n) = 2^(n - 1) - 1`
  - with matching exact `Phi` formulas too
- the middle step:
  - `ADS(q) -> OLAS(q + 1)`
  is exactly `TD`-neutral but still `Phi`-positive

Why this matters:

- the downstream tail is now a counted mechanism, not only a checked move
  chain

Next ideas:

- use the amount formulas to shorten the tail proof
- then search for a comparable amount law on `BFT`

### Bridge-fan-tail amount compiler

Hypothesis:

- the feeder family `BFT(r, t)` may already have a short exact amount
  recurrence

Current status:

- yes on checked:
  - `2 <= r <= 7`
  - `1 <= t <= 10`
- exact base formulas:
  - `TD(BFT(r, 1)) = 7 * 2^(r + 2) - 7`
  - `TD(BFT(r, 2)) = 7 * 2^(r + 2)`
  - `TD(BFT(r, 3)) = 21 * 2^(r + 1) - 7`
  - `TD(BFT(r, 4)) = 21 * 2^(r + 2) - 21`
- exact recurrence:
  - `TD(BFT(r, t)) = TD(BFT(r, t - 1)) + TD(BFT(r, t - 3)) + TD(BFT(r, t - 4))`

Why this matters:

- the feeder family now has an exact amount compiler, not only a checked move
  chain

Next ideas:

- combine the feeder compiler with the downstream tail amount law
- test whether the whole anomaly-side route has a single exact amount
  compiler

### Anomaly-route amount compiler

Hypothesis:

- the whole anomaly-side route may have one exact amount compiler, not only one
  feeder compiler plus one tail compiler

Current status:

- yes on checked:
  - `2 <= r <= 7`
  - `1 <= t <= 10`
- define:
  - `Delta(r, t) = TD(star_{r + t + 6}) - TD(BFT(r, t))`
- exact base formulas:
  - `Delta(r, 1) = 9 * 2^(r + 2) + 6`
  - `Delta(r, 2) = 25 * 2^(r + 2) - 1`
  - `Delta(r, 3) = 107 * 2^(r + 1) + 6`
  - `Delta(r, 4) = 107 * 2^(r + 2) + 20`
- exact recurrence:
  - `Delta(r, t) = Delta(r, t - 1) + Delta(r, t - 3) + Delta(r, t - 4) + 5 * 2^(r + t + 1) + 2`

Why this matters:

- the whole anomaly-side route now has a single exact amount compiler on the
  checked strip

Next ideas:

- prove the whole-route compiler structurally
- if that proof lands, consider whether the route line has crossed the next
  tutorial threshold

### Anomaly-route Fibonacci-periodic decomposition

Hypothesis:

- the whole anomaly-side route may have a cleaner object than the checked
  inhomogeneous recurrence from `v277`
- namely:
  - an exponential star target term
  - minus a feeder term that decomposes into Fibonacci growth and a period-4
    residue

Current status:

- yes on checked `2 <= r <= 7`, `1 <= t <= 10`
- exact feeder formula:
  - `B(r, t) = A_r * F_t + B_r * F_{t + 1} + C_r * cos(pi t / 2) + A_r * sin(pi t / 2)`
- exact route deficit:
  - `Delta(r, t) = 2^(r + t + 5) - 1 - B(r, t)`
- exact forcing interpretation:
  - the term `5 * 2^(r + t + 1) + 2` is exactly the residue of the star target
    sequence against the feeder recurrence

Why this matters:

- this is the first anomaly-route law that looks like a real symbolic
  decomposition, not only a checked compiler surface

Next ideas:

- derive the same decomposition structurally from the recurrence factorization
- decide whether that proof step is enough to trigger a new tutorial pass

### Finite rewrite alphabet for the depth-2 controller

Hypothesis:

- the surviving depth-2 minimal controller may collapse further, not to one
  unique move shape, but to a finite rooted template alphabet

Current status:

- yes on checked connected trees with `n in {8, 9}`:
  - every selected move belongs to one of:
    - `leaf`
    - `cherry`
    - `three_leaf_star`
    - `broom_1`
    - `broom_2`

Why this matters:

- the live controller is now concrete enough for template-by-template proof
  search
- the ladder family from `v244` gives the negative side, and the finite
  template alphabet now gives a plausible positive side

Next ideas:

- prove that the five-template alphabet is sufficient on the checked branch
- then compose that template proof with exact star-size balancing
