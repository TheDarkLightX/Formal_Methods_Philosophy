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
