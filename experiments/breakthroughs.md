# Breakthroughs Memory

## 2026-03-26

### Survivor: closure-guided coupled policy

Bounded result:

- on every `3x3` boolean relation, closure-gain scheduling matched the exact optimal verifier policy for total steps and total online obligation checks
- on every `3x4` boolean relation, the same held
- on `4x4`, closure-gain remained near-optimal but not exact on all relations under the fixed proposer `x_t = min(C_t)`
- on `4x4`, if the proposer instead chose the surviving candidate with maximal singleton closure and the verifier used closure-gain scheduling, the coupled policy matched the exact bounded optimum on every relation checked exhaustively

Why it mattered:

- the first loop result was mostly a correction about state representation
- this result identifies the actual leverage point as verifier-side scheduling
- the stronger result shows the proposer and verifier are coupled, and that the same closure geometry can drive both sides

Boundary learned:

- state dualization alone did not create a stronger candidate-elimination loop
- verifier scheduling alone created a stronger bounded policy
- co-designed proposer and verifier policies created an even stronger bounded policy

### New survivor: obligation-targeted witness routing

Bounded result:

- the closure-guided coupled policy can be factored exactly into:
  - an obligation-only controller over `y`
  - plus a witness router that picks an exposing `x`
- on exhaustive `4x4`, this routed formulation matches the coupled policy on every relation
- on exhaustive `4x4`, it is also exact-optimal for steps and checks

Why it mattered:

- this changes the role split in the neuro-symbolic loop
- the formal side can choose the obligation target directly
- the existential side can be used to route to the chosen obligation rather than only to propose the final solution

### New survivor: obligation-side policy iteration

Bounded result:

- let `pi_0` be the routed obligation controller
- define `pi_{k+1}` by one-step policy improvement using the exact value function of `pi_k`
- on exhaustive `4x4`, `pi_2` matched the exact bounded-optimal check policy on all `65536` relations
- on sampled `5x5` and `6x6` holdouts in the cycle, `pi_2` also matched the exact optimum on every sampled relation

Why it mattered:

- this is the first result that looks like a real loop law rather than only a good heuristic
- it suggests the obligation side admits fast convergence under policy improvement
- it gives a concrete higher-leverage loop:
  propose a controller, evaluate it formally, improve it, repeat

### Boundary: single third tie-break clause family exhausted

Bounded result:

- start from the exact bounded two-clause dominance language
- search a third tie-break clause family over:
  - equal `gain`
  - equal `child_best_gain`
  - equal `next_uncovered`
  - `cut_gain_min ∈ {1,2}`
  - `next_size_drop_min ∈ {1,2}`
  - `max_child_cut_drop ∈ {0,1,2}`
  - `min_child_sum_drop ∈ {0,1,2,3,4,5}`
  - `min_child_best_singleton_gain ∈ {0,1}`
  - `origin_guard ∈ {any, core, repair}`
  - four local rank modes
- `184` clauses fixed at least one of the remaining sampled larger-root residuals
- many clauses fixed all `3` residuals at the holdout-root level
- but `0` clauses fixed all `3` while preserving every exhaustive reachable nonterminal `4x4` state of the exact bounded core

Why it mattered:

- this is a clean negative result, not just a failed guess
- it shows the current frontier is no longer “tune one more threshold”
- it forces the next loop to change language:
  - richer clause programs
  - Bellman-derived guards
  - or repair synthesis over a larger controller language

### New survivor: repair-program CEGIS frontier

Bounded result:

- search object:
  - ordered pairs of tie-break clauses above the exact bounded two-clause controller
- proposal loop:
  - pick the lexicographically simplest pair consistent with the sampled larger-root residuals and the current bank
- verifier:
  - exhaustive reachable nonterminal `4x4` states
- loop trace:
  - iteration `1`: `7104` viable pairs, first counterexample at mask `828`
  - iteration `2`: `1152` viable pairs, second counterexample at mask `1915`
  - iteration `3`: `576` viable pairs, safe pair found

Safe pair found:

- clause `1`:
  - `cut_gain_min = 1`
  - `next_size_drop_min = 1`
  - `max_child_cut_drop = 1`
  - `min_child_best_singleton_gain = 1`
  - `min_child_sum_drop = 0`
  - `origin_guard = any`
  - `rank = cut_bestsingleton_next`
- clause `2`:
  - `cut_gain_min = 1`
  - `next_size_drop_min = 1`
  - `max_child_cut_drop = 1`
  - `min_child_best_singleton_gain = 0`
  - `min_child_sum_drop = 4`
  - `origin_guard = any`
  - `rank = cut_bestsingleton_next`

Why it mattered:

- this is a real higher-order neuro-symbolic loop
- the existential side is no longer proposing only a controller
- it is synthesizing a short **repair program** over a controller language
- the verifier is not merely rejecting candidates, it is teaching the repair language by growing a bank of failing bounded states

Boundary learned:

- the first safe repair program generalized poorly:
  - `5x5`: `2945 / 3000`
  - `6x6`: `876 / 900`
- so the next loop must separate:
  - safety on the bounded core
  - selection among safe repair programs by a larger-domain ranking objective

### New survivor: shared-bank multi-proposer frontier

Bounded result:

- search space:
  - `7104` residual-consistent repair-program pairs
- proposer family:
  - `lex`
  - `singleton`
  - `childsum`
  - `aggressive`
  - `bestsingleton_rank`

Single-proposer outcomes:

- `childsum` found a safe repair program in:
  - `2` exact verifier calls
  - bank size `1`
- every other single proposer needed:
  - `3` exact verifier calls
  - bank size `2`

Best two-proposer portfolio:

- `childsum + aggressive`
- found the same safe repair program in:
  - `3` exact verifier calls
  - `2` synchronous rounds
  - bank size `2`

Why it mattered:

- this gives the first bounded answer to the scaling question
- adding proposers does not automatically beat the best proposer
- the gain comes from:
  - proposer diversity
  - shared counterexample memory
  - centralized exact refutation

Boundary learned:

- in this bounded slice, the best single proposer still dominates the best portfolio on exact verifier calls
- raw proposer count is therefore the wrong scaling metric
- the right metric is verified progress under a shared bank

### New survivor: bank-then-rank frontier

Bounded result:

- start from the `v12` bank:
  - mask `828`, candidates `(0,1,2,3)`, target `0`
  - mask `1915`, candidates `(0,1,2)`, target `2`
- keep only repair-program pairs consistent with:
  - the sampled larger-root residuals
  - the banked bounded counterexamples
- viable frontier size:
  - `576`
- rank that frontier by larger sampled-root score
- certify in rank order against the exhaustive reachable nonterminal `4x4` verifier

The first ranked viable pair was already safe:

- clause `1`:
  - `cut_gain_min = 1`
  - `next_size_drop_min = 1`
  - `max_child_cut_drop = 2`
  - `min_child_sum_drop = 2`
  - `min_child_best_singleton_gain = 1`
  - `origin_guard = core`
  - `rank = cut_next_childsum`
- clause `2`:
  - `cut_gain_min = 1`
  - `next_size_drop_min = 1`
  - `max_child_cut_drop = 1`
  - `min_child_sum_drop = 4`
  - `min_child_best_singleton_gain = 0`
  - `origin_guard = any`
  - `rank = cut_next_childsum`

Holdout score:

- `5x5`: `2945 / 3000`
- `6x6`: `876 / 900`

Why it mattered:

- this is the cleanest factorization found so far
- once the bounded bank is informative enough, safety and value can be separated
- the loop becomes:
  - learn bank
  - rank viable frontier
  - certify top candidate

Boundary learned:

- the staged factorization worked in this bounded slice
- but it did not improve larger sampled-root value beyond the best safe repairs already known
- so the next frontier is probably bank quality or proposer specialization, not more ranking alone

### New survivor: minimal-bank synthesis frontier

Bounded result:

- search space:
  - `7104` residual-consistent repair-program pairs
- verifier space:
  - `320927` exhaustive reachable nonterminal `4x4` states
  - compressed to `4263` unique state patterns
- exact result:
  - the first holdout-ranked residual-consistent pair is already safe
  - `first_safe_rank_without_bank = 1`
  - `unsafe_prefix_size = 0`
  - `minimal_bank_size = 0`

Winning pair:

- clause `1`:
  - `cut_gain_min = 1`
  - `next_size_drop_min = 1`
  - `max_child_cut_drop = 2`
  - `min_child_sum_drop = 2`
  - `min_child_best_singleton_gain = 1`
  - `origin_guard = core`
  - `rank = cut_next_childsum`
- clause `2`:
  - `cut_gain_min = 1`
  - `next_size_drop_min = 1`
  - `max_child_cut_drop = 1`
  - `min_child_sum_drop = 4`
  - `min_child_best_singleton_gain = 0`
  - `origin_guard = any`
  - `rank = cut_next_childsum`

Holdout score:

- `5x5`: `2945 / 3000`
- `6x6`: `876 / 900`

Why it mattered:

- this is a stronger correction than the `v14` staging story alone
- the bank can still help explain viable-frontier pruning, but it is not needed to make the winner safe in this bounded model
- the loop factorization collapses further:
  - rank the residual-consistent frontier
  - certify the top candidate

Boundary learned:

- the meaningful next frontier is no longer “better bank for the top winner”
- it is:
  - better value among safe winners,
  - bank usefulness for deeper ranks or alternative objectives,
  - or proposer specialization before the residual-consistent frontier is formed

### New survivor: obligation-fiber proposer frontier

Bounded result:

- by `v15`, the globally ranked residual-consistent frontier already returns a safe pair at call `1`
- therefore strict improvement on top-`1` exact-safe discovery is impossible for any specialized proposer in the same bounded model

Why it mattered:

- this is a clean negative boundary, not a failed search
- it closes one apparent scaling branch
- specialization might still matter for:
  - top-`k` diversity
  - alternative value objectives
  - pre-frontier proposal shaping
- but it has no remaining leverage on top-`1` exact-safe discovery here

### New survivor: winner-certificate language frontier

Bounded result:

- domain:
  - `7104` residual-consistent repair-program pairs
- atom language:
  - `17` winner-feature equalities
- exact certificate search:
  - no isolating conjunction of size `≤ 5`
  - minimal certificate size `= 6`
  - exact minimal solutions found: `3`

Representative minimal certificate:

- `holdout_total = 3821`
- `c1.max_child_cut_drop = 2`
- `c1.min_child_sum_drop = 2`
- `c1.origin_guard = core`
- `c1.rank = cut_next_childsum`
- `c2.rank = cut_next_childsum`

Why it mattered:

- this is the first actual certificate-language object in the current loop family
- the certificate is small but nontrivial
- it shows that the staged loop can end not only in a safe winner, but in a compact witness that isolates that winner inside the residual-consistent frontier

Boundary learned:

- the certificate is for the winner, not for the whole safe set
- so the next deeper frontier is:
  - certify larger safe regions,
  - or synthesize certificate languages that apply to classes of safe repair programs rather than one winner

### New survivor: safe-region certificate frontier

Bounded result:

- frontier size:
  - `7104` residual-consistent repair-program pairs
- safe subset size:
  - `288`
- atom language size:
  - `17`
- exact region-certificate search:
  - size-`1` safe-region certificates exist
  - maximal size-`1` safe support:
    - `288`
  - minimal region-certificate size:
    - `1`
  - size-`1` solutions found:
    - `3`

Representative size-`1` region certificates:

- `holdout_total = 3821`
- `holdout_5_hits = 2945`
- `holdout_6_hits = 876`

Why it mattered:

- this is stronger than the winner-certificate result
- the winner itself requires `6` atoms to isolate exactly,
- but the whole safe top block is certified by a single score atom
- it reveals a clean two-level structure:
  - safe region is simple
  - within that region, winner selection is harder

Boundary learned:

- the next frontier is no longer “does a region certificate exist?”
- it is:
  - certify deeper safe regions beyond the top-score block,
  - explain why the top-score block and the safe set coincide in this bounded model,
  - or search for certificate languages for lower-ranked safe strata

### New survivor: score-safety collapse frontier

Bounded result:

- frontier size:
  - `7104`
- safe subset size:
  - `288`
- exact scalar-block analysis:
  - `Safe(x) <-> holdout_total(x) = 3821`
  - equivalently:
    - `Safe(x) <-> holdout_5_hits(x) = 2945`
    - `Safe(x) <-> holdout_6_hits(x) = 876`

Top score blocks:

- `holdout_total = 3821`: `288` items, all safe
- next block, `3796`: `288` items, all unsafe

Why it mattered:

- this is stronger than the region-certificate phrasing
- exact bounded safety collapses to maximizing one sampled score inside the residual-consistent frontier
- the universal verifier is still what established the collapse, but once learned, the safe set is described by a single scalar equality

Boundary learned:

- the next frontier is not “is the top block safe?”
- it is:
  - why this scalar collapse occurs,
  - whether lower strata admit similar exact descriptions,
  - and whether the same collapse can be induced in MPRD-like policy spaces

### New survivor: score-block staircase frontier

Bounded result:

- there are `10` score blocks in the residual-consistent frontier
- every score block is pure
- the top block:
  - `holdout_total = 3821`
  - size `288`
  - all safe
- every lower block:
  - all unsafe
  - one shared first verifier refuter

Representative lower blocks:

- `3796`:
  - size `288`
  - shared first refuter:
    - mask `13116`
    - candidates `(0,1,2,3)`
    - target `0`
- `3775`:
  - size `288`
  - shared first refuter:
    - mask `1915`
    - candidates `(0,1,2)`
    - target `2`
- `3762`:
  - size `1872`
  - shared first refuter:
    - mask `828`
    - candidates `(0,1,2,3)`
    - target `0`

Why it mattered:

- the frontier is not only region-certifiable
- it has a staircase geometry:
  - one pure score block at a time
  - one dominant refuter at a time
- that is much more structured than a generic safe/unsafe partition

Boundary learned:

- the next frontier is to explain this staircase geometrically, not just record it
- or to test whether the same staircase form appears in larger or different bounded families

### New survivor: scalar refuter quotient frontier

Bounded result:

- the full first-refuter label is an exact function of:
  - `holdout_total`
  - `holdout_5_hits`
- it is **not** an exact function of:
  - `holdout_6_hits`

Why it mattered:

- this upgrades the staircase from a descriptive pattern to a quotient law
- the bounded refuter partition is one-dimensional under at least two scalar coordinates
- so after residual consistency, the loop state can be quotiented much further than just safe versus unsafe

Critical exception:

- `holdout_6_hits = 859` mixes two refuter classes:
  - `(mask 1915, candidates (0,1,2), target 2)`
  - `(mask 828, candidates (0,1,2,3), target 0)`

Why that exception matters:

- it shows not every scalar score is equally expressive
- the quotient is real, but coordinate-sensitive

### New survivor: arithmetic refuter logic frontier

Bounded result:

- the four `v21` refuter labels admit exact arithmetic decision lists over the two expressive scalar coordinates
- over `holdout_total`:
  - `T > 3796 -> safe`
  - `T > 3775 -> fail_13116`
  - `T ≡ 3 (mod 23) -> fail_1915`
  - `else -> fail_828`
- over `holdout_5_hits`:
  - `H5 > 2927 -> safe`
  - `H5 > 2910 -> fail_13116`
  - `H5 ≡ 3 (mod 17) -> fail_1915`
  - `else -> fail_828`
- in both cases the minimal exact list length in the searched grammar is `3`

Why it mattered:

- this is the first small logic presentation of the whole four-way refuter partition
- the scalar quotient now has a readable arithmetic form, not only a block table
- `holdout_6_hits` remains the obstruction coordinate because `859` is mixed

Boundary learned:

- the next frontier is to explain the arithmetic, not only record it
- or to find the smallest second coordinate that repairs the `859` collision

### New survivor: mixed-bucket repair frontier

Bounded result:

- the only mixed scalar obstruction on the `holdout_6_hits` side is the bucket `859`
- in the searched simple feature library, it is repaired by exactly one feature:
  - `E(x) := p1_4(x) = p2_4(x)`
- the pair `(holdout_6_hits, E)` is an exact quotient for the full refuter partition

Why it mattered:

- the obstruction is local rather than global
- one tiny repair bit is enough to restore exactness
- this is the first clean “quotient plus repair bit” object in the current loop

Boundary learned:

- the next frontier is to compile the repaired quotient into the smallest exact verifier logic

### New survivor: repaired verifier compiler frontier

Bounded result:

- the repaired quotient has `10` reachable states
- it compiles to an exact bounded decision list with `4` guards:
  - `H6 = 859 ∧ E = False -> fail_1915`
  - `H6 = 865 -> fail_1915`
  - `H6 = 869 -> fail_13116`
  - `H6 > 869 -> safe`
  - `else -> fail_828`

Why it mattered:

- this is the clearest verifier-compiler object found so far
- the loop no longer ends only with a verified candidate
- it ends with a small compiled verifier logic

Boundary learned:

- the next frontier is not more compression by brute force
- it is conceptual explanation, or transfer of this compiler pattern to a broader neuro-symbolic loop

### New survivor: verifier compiler lower-bound frontier

Bounded result:

- in the repaired `(H6, E)` quotient, no exact decision list with `3` guards or fewer exists in the searched grammar
- the lower-bound witness is structural:
  - `safe` has only a singleton pure branch
  - `fail_13116` has only a singleton pure branch
  - the two `fail_1915` states require two distinct singleton pure branches
- therefore at least `4` labeled guards are necessary
- `v24` attains `4`, so the bounded compiler is exact-minimal

Why it mattered:

- the verifier-compiler object now has both an exact upper bound and an exact lower bound
- that turns it into a much stronger tutorial object

Boundary learned:

- the next frontier is transfer, not more bounded squeezing on this same quotient

### New survivor: MPRD transfer boundary frontier

Bounded result:

- in the toy lab-followup MPRD controller family:
  - `5283` unique controller behaviors are realized
  - `164` remain after residual consistency on the chosen 3-state training set
- on that viable frontier, the first-refuter partition does not collapse to:
  - `holdout score + 1` simple behavior feature
  - `holdout score + 2` simple behavior features
  - `holdout score + 3` simple behavior features
- the first exact repair in the searched library appears at `4` predicted-action features

Why it mattered:

- this is a real transfer boundary
- the quotient-and-repair verifier-compiler pattern is strong, but not automatically cheap in every bounded policy family

Boundary learned:

- future transfer claims need bounded evidence, not analogy alone

### New survivor: MPRD semantic repair frontier

Bounded result:

- in the same toy MPRD lab-followup transfer case:
  - no exact semantic repair exists with `1`, `2`, or `3` features
  - the first exact semantic repair appears at `4` mistake-indicator bits:
    - `err[(0, 0, 1)]`
    - `err[(0, 1, 0)]`
    - `err[(0, 1, 1)]`
    - `err[(1, 1, 0)]`

Why it mattered:

- the transfer boundary is now interpretable
- the first exact repair is not a bag of arbitrary behavior IDs
- it is a small semantic basis over the holdout mistakes

Boundary learned:

- the transfer is still not cheap
- but it is structured enough to teach

### New survivor: earliest-error compiler frontier

Bounded result:

- in the toy MPRD lab-followup transfer case:
  - `FirstRefuter(x)` is exactly the earliest holdout error in the fixed holdout order
  - `holdout score + any 4 of the 5 ordered error bits` is exact
  - every searched `holdout score + 3-bit` subbasis fails

Why it mattered:

- the transfer case now has a clean symbolic law
- the first-refuter partition is not just repaired by features, it is compiled by earliest error
- this is the strongest positive transfer-side object so far

Boundary learned:

- the transfer compiler is higher-dimensional than the abstract verifier compiler
- so the pattern generalizes, but not always with the same compression ratio

### New survivor: monotone refill transfer frontier

Bounded result:

- in a second MPRD-shaped domain, a monotone refill-style controller family:
  - `14` guards
  - `1640` unique behaviors
  - `130` residual-consistent viable behaviors
- no exact semantic repair exists with `5` holdout error bits or fewer
- the first exact semantic basis in the searched library appears at `6` holdout error bits

Why it mattered:

- this is the strongest current evidence that transfer cost depends sharply on policy shape
- it prevents overgeneralizing from the earlier toy lab-followup transfer

Boundary learned:

- the verifier-compiler loop is still the best pattern found,
- but its compressed object can become much higher-dimensional in some domains

### New survivor: horn-closed refill basis frontier

Bounded result:

- in the monotone refill transfer case, the exact 6-bit semantic basis from `v29` remains minimal even after allowing all exact single- and pair-Horn implications among the 13 holdout error bits
- the basis `{3,6,8,9,10,12}` closes to `11` of the `13` error bits
- the only non-derivable bits are `5` and `11`
- no Horn-closed basis of size `5` or less is exact

Why it mattered:

- it separates logical derivability from exact classifier size
- it shows that Horn closure alone does not remove the refill transfer cost

Boundary learned:

- the next question is not whether the basis can be made smaller by closure
- it is whether the surviving 6 bits are all essential

### New survivor: irredundant refill Horn basis frontier

Bounded result:

- the Horn-closed 6-bit basis remains exact
- dropping any one retained bit destroys exact first-refuter classification
- the first mixed bucket witnesses are:
  - drop `3` -> hold score `7`, labels `(0,0,1,0)` and `(0,1,0,0)`
  - drop `6` -> hold score `8`, labels `(0,0,1,0)` and `(1,0,0,0)`
  - drop `8` -> hold score `7`, labels `(0,0,0,0)` and `(1,0,0,0)`
  - drop `9` -> hold score `10`, labels `(1,0,1,0)` and `(1,0,1,1)`
  - drop `10` -> hold score `11`, labels `(1,0,1,1)` and `(1,1,0,0)`
  - drop `12` -> hold score `8`, labels `(0,0,0,0)` and `(1,0,0,0)`
- adding either non-derivable bit `5` or `11` preserves exactness but only refines already-pure buckets

Why it mattered:

- the refill frontier now has a clean logic decomposition:
  - six bits are essential,
  - two more are independent but not needed for exact labels
- this is a stronger explanation than simply reporting that size `6` is minimal

Boundary learned:

- the transfer cost is now explained at the basis level
- the next step is presentation, not more blind compression search

### New survivor: ordered refill basis compiler frontier

Bounded result:

- in the monotone refill transfer case, the essential basis `B = {3,6,8,9,10,12}` admits an ordered active-prefix compiler
- no order is exact with only the first `3` active basis bits
- `504 / 720` orders are exact with the first `4` active basis bits
- `720 / 720` orders are exact with the first `5` active basis bits
- the best `k=3` order misses by one bad bucket

Why it mattered:

- this is the cleanest positive compiler law found so far in the hard refill transfer domain
- it shows that the verifier-compiler loop still finds structure even after the cheap quotient-and-repair story has failed

Boundary learned:

- the remaining question is now conceptual, not empirical:
- why does `k=5` become order-invariant while `k=4` stays order-sensitive?

### New survivor: k4 refill order law frontier

Bounded result:

- in the monotone refill transfer case, the `k=4` ordered-basis compiler frontier has an exact structural law
- let `F4(σ)` be the first four positions of an order `σ` on `B = {3,6,8,9,10,12}`
- then `Exact_4(σ)` holds iff:
  - `3 ∈ F4(σ)` and `F4(σ)` contains at least one of `{6,8}`, or
  - `3 ∉ F4(σ)`, both `6` and `8` lie in `F4(σ)`, and `3` appears before the unique omitted bit from `{9,10,12}`
- this criterion matches all `720` orders exactly

Why it mattered:

- it turns the `k=4` split from an observation into a formula
- the refill transfer branch now has:
  - a minimal basis,
  - an irredundancy law,
  - an ordered compiler law,
  - and an exact criterion for the order-sensitive boundary

Boundary learned:

- the main remaining work is presentation and transfer, not more local search in this same bounded family

### New survivor: regional refill ladder frontier

Bounded result:

- in the monotone refill transfer case, the best exact regional ladder uses shared order `(3,6,8,9,10,12)` with local depths:
  - scores `0..6` -> `0`
  - score `7` -> `2`
  - score `8` -> `3`
  - score `9` -> `4`
  - scores `10,11,12` -> `1`
- weighted online cost is `118`
- average depth is `118 / 130`
- maximum depth is `4`
- no exact regional ladder exists with maximum depth `3`
- this beats global exact depth assignments by a large margin:
  - global `k=4` cost `520`
  - global `k=5` cost `650`

Why it mattered:

- this is the first exact bounded survivor for the explanatory-ladder idea
- it shows the hard refill domain does not require one global explanation depth everywhere
- verifier-compilers are now better understood as one rung inside a broader adaptive ladder

Boundary learned:

- the next step is to test witness-language or ladder transfer in another family,
- not to keep squeezing this same refill domain locally

### New survivor: mixed-sign label language frontier

Bounded result:

- on the repaired verifier frontier:
  - the smallest exact all-positive certificate language uses `7` pure guards
  - the smallest exact mixed-sign language uses only `4`
- the optimal mixed-sign split is:
  - positive certificates for `safe`, `fail_13116`, and `fail_1915`
  - default residual class for `fail_828`

Why it mattered:

- this is the first bounded evidence for the dual-language direction
- it shows that exact explanation can be cheaper when the system is allowed to mix:
  - positive proofs for some labels
  - and negative or residual treatment for another

Boundary learned:

- the next step is to search for explicit negative witness objects,
- not only a default residual label

### New survivor: primitive-invention label frontier

Bounded result:

- on the repaired verifier frontier:
  - baseline all-positive exact language cost is `7`
  - one invented pure primitive lowers the cost to `5`
  - two invented pure primitives lower the cost to `4`
- the best invented primitives are:
  - `fail_1915 := H6 = 859 and E = False OR H6 = 865`
  - `fail_828 := E = True OR H6 = 858 OR H6 = 864`

Why it mattered:

- this is the first bounded evidence for the primitive-invention and concept-market axis
- it shows that fixed-language comparisons can understate what an exact loop can achieve
- exact concept invention can match the best mixed-sign explanation cost on this frontier

Boundary learned:

- the next step is to repeat this on a harder frontier where invented primitives are not just unions of a few pure atoms

### New survivor: refill concept-market frontier

Bounded result:

- on the hard monotone refill transfer frontier:
  - baseline exact ladder from `v34` has weighted cost `118` and maximum depth `4`
- in the searched fixed-order insertion grammar:
  - keep the exact order `(3,6,8,9,10,12)`
  - insert one pure `AND` or `OR` primitive over `2` or `3` basis bits
  - re-optimize local ladder depths exactly
  - the best exact shortcut is:
    - `err[10] AND err[12]`
    - inserted before `err[10]`
  - this lowers weighted cost to `90`
  - and lowers maximum depth to `3`
- in the searched replacement grammar:
  - replace source basis bits by one pure `AND` or `OR` primitive over `2` or `3` bits
  - allow full reordering
  - exact count is `0`

Why it mattered:

- this is the first hard-frontier survivor for the concept-market direction
- concept invention is no longer only an easy repaired-verifier phenomenon
- but the shape matters:
  - the winning concept acts as a shortcut on top of the old basis
  - not as a smaller replacement language

Boundary learned:

- the next question is whether two invented shortcut concepts can lower the hard ladder again,
- or whether the next real jump now requires witness-language discovery instead of more local concept search

### New survivor: refill two-concept ladder frontier

Bounded result:

- on the hard monotone refill transfer frontier:
  - baseline exact ladder from `v34` has weighted cost `118` and maximum depth `4`
  - the one-shortcut result from `v37` lowers this to weighted cost `90` and maximum depth `3`
- in the searched two-shortcut insertion grammar:
  - keep the exact base order `(3,6,8,9,10,12)`
  - insert two distinct pure `AND` or `OR` primitives over `2` or `3` basis bits
  - re-optimize local ladder depths exactly
  - the best exact pair is:
    - `err[6] AND err[10] AND err[12]`
    - `err[9] AND err[10] AND err[12]`
  - this lowers weighted cost to `80`
  - and lowers maximum depth to `2`
  - no exact pair in the searched grammar reaches maximum depth `1`

Why it mattered:

- this is the first bounded evidence that hard-frontier concept invention can stack
- the result is materially stronger than the one-shortcut frontier
- the hard refill ladder now looks like a layered concept-market object, not only a fixed ordered basis

Boundary learned:

- the next local question is whether a third shortcut can beat max depth `2`
- but the broader question is whether this line should now stop and yield to witness-language discovery

### New survivor: anchored third-shortcut boundary frontier

Bounded result:

- keep the exact `v38` pair fixed:
  - `err[6] AND err[10] AND err[12]`
  - `err[9] AND err[10] AND err[12]`
- in the searched anchored third-shortcut grammar:
  - insert one more pure `AND` or `OR` primitive over `2` or `3` basis bits
  - allow arbitrary insertion position
  - re-optimize local ladder depths exactly
- searched candidate count `612`
- no searched third shortcut lowers:
  - weighted cost below `80`
  - or maximum depth below `2`
- the best searched extra shortcut is:
  - `err[3] OR err[6] OR err[8]`
  - which keeps cost `80` and max depth `2`
  - but improves bucket total from `51` to `48`

Why it mattered:

- this is the first clean bounded saturation result for the local hard-frontier shortcut line
- it says the verified two-shortcut ladder is locally stable on the main online metrics under one more simple pure shortcut

Boundary learned:

- the next step should probably not be another small anchored shortcut tweak
- the real choice is:
  - global three-shortcut search
  - or moving up to witness-language discovery

### New survivor: score-local witness frontier with residual defaults

Bounded result:

- fix the exact `v38` feature space
- search witness atoms that are conjunctions of `1` to `3` signed literals over those `8` features
- on the six nontrivial score blocks:
  - every block admits an exact positive-cover plus residual-default witness language
  - total positive-cover-plus-residual cost is `27`
- exact all-positive witness languages fail on:
  - score `9`
  - score `10`

Why it mattered:

- this is the first hard-frontier witness-language result after the local shortcut line saturated
- it shows the next level up is real, not only a slogan
- positive-cover plus residual-default witness languages expose structure that one more local shortcut no longer improves

Boundary learned:

- the next step is a true global witness-language cycle, not another small anchored shortcut tweak

### New survivor: global witness-schema frontier

Bounded result:

- keep the exact local witness costs from `v40`
- search over all exact score-local positive-cover plus residual-default witness choices in the same grammar
- minimize the size of the shared global witness-schema library
- strongest result:
  - local positive-cover-plus-residual cost `27`
  - best shared global schema count `20`

Why it mattered:

- this is the first genuine global witness-language object in the hard-frontier line
- it shows the witness-language result is not only six local facts
- there is a real reusable schema layer above them

Boundary learned:

- the next question is whether richer witness grammars or score abstractions can lower the shared schema count further

### New survivor: score-abstraction witness frontier

Bounded result:

- search all contiguous partitions of the nontrivial scores:
  - `7, 8, 9, 10, 11, 12`
- use the same exact positive-cover plus residual-default witness grammar as `v40`
- strongest exact partition:
  - `(7)`, `(8)`, `(9)`, `(10,11)`, `(12)`
- total witness cost drops:
  - from `27`
  - to `23`
- only two contiguous partitions are exact in the searched space:
  - the `6`-region score-local partition
  - this `5`-region merged partition

Why it mattered:

- this is the first exact score-abstraction result on the hard witness frontier
- the witness-language line now compresses both:
  - across reusable schemas
  - and across score blocks

Boundary learned:

- the next question is whether richer witness grammars or looser score abstractions can lower witness cost again

### New survivor: unconstrained score-abstraction boundary frontier

Bounded result:

- search all `203` set partitions of:
  - `7, 8, 9, 10, 11, 12`
- use the same exact positive-cover plus residual-default witness grammar as `v40` to `v42`
- only `10` partitions are exact
- the best partition remains:
  - `(7)`, `(8)`, `(9)`, `(10,11)`, `(12)`
- best total witness cost remains:
  - `23`

Why it mattered:

- this is a real boundary result on top of `v42`
- it shows the best score abstraction survives the larger unconstrained partition space

Boundary learned:

- the next likely gains need richer witness grammars, not only looser score partitioning

### New survivor: richer witness-grammar frontier

Bounded result:

- keep the `v43` unconstrained score-partition search fixed:
  - all `203` set partitions of `7, 8, 9, 10, 11, 12`
- enrich the witness-atom grammar:
  - conjunctions of `1` to `4` signed literals over the same `8` features
- strongest result:
  - feasible partition count rises:
    - from `10`
    - to `15`
  - the best partition remains:
    - `(7)`, `(8)`, `(9)`, `(10,11)`, `(12)`
  - best total witness cost drops:
    - from `23`
    - to `22`
  - the gain comes from one new exact pure atom in score `9`:
    - `not err[3] and not err[6] and not err[8] and err[10]`

Why it mattered:

- this is the first exact gain after the score-partition side saturated
- it shows the next improvement comes from the witness grammar, not from more partition freedom
- the witness-language line still has one bounded rung left in the current feature space

Boundary learned:

- `v43` saturated the partition axis, not the grammar axis
- the next honest frontier is richer witness grammars or more global witness-language synthesis

### New survivor: five-literal witness-grammar boundary frontier

Bounded result:

- compare the exact `1..4` and `1..5` witness grammars on the same `203` unconstrained score partitions
- strongest result:
  - feasible partition count stays:
    - `15`
  - best partition stays:
    - `(7)`, `(8)`, `(9)`, `(10,11)`, `(12)`
  - best total witness cost stays:
    - `22`
  - only two non-best partitions improve by one unit each

Why it mattered:

- this closes the local grammar axis on the main exact object
- it shows `v44` was a real gain, not the start of an unlimited local literal climb

Boundary learned:

- the next honest improvement needs a more global witness object, not one more literal

### New survivor: global witness-synthesis frontier

Bounded result:

- fix the exact `v44` partition:
  - `(7)`, `(8)`, `(9)`, `(10,11)`, `(12)`
- keep the exact `1..4` witness grammar from `v44`
- strongest result:
  - raw local region cost:
    - `22`
  - best shared global schema count:
    - `19`

Why it mattered:

- this is the first more-global witness object above the best hard score abstraction
- the line now has a reusable schema layer above its strongest local partition

Boundary learned:

- the next frontier is richer global synthesis, not more partition freedom

### New survivor: global witness-synthesis grammar boundary frontier

Bounded result:

- keep the exact `v46` partition fixed:
  - `(7)`, `(8)`, `(9)`, `(10,11)`, `(12)`
- compare global witness-synthesis with `1..4` versus `1..5` signed-literal atoms
- strongest result:
  - total region cost stays:
    - `22`
  - best shared global schema count stays:
    - `19`

Why it mattered:

- this closes the nearby global grammar axis on the main metric
- the witness-language line is now locally tight both below and above the best score abstraction

Boundary learned:

- the next honest progress needs a stronger loop family, not one more literal on the current family

### New survivor: cross-frontier witness-template frontier

Bounded result:

- source exact objects:
  - the exact global witness-schema library from `v41`
  - the exact global witness-schema library from `v46`
- raw formula union:
  - `22`
- exact overlap:
  - `17`
- untyped conjunction-shape templates:
  - `10`
- typed templates, keeping feature kind:
  - `13`

Why it mattered:

- this is the first survivor that sits above multiple exact frontiers instead of inside one frontier
- it changes the sharper vision from frontier-specific witness objects to a reusable witness-template language

Boundary learned:

- the next honest search object is a template compiler across frontiers, or a stronger family beyond templates

### New survivor: cross-frontier core-plus-patch frontier

Bounded result:

- decompose the exact global witness-schema frontiers from `v41` and `v46` into:
  - shared exact core
  - frontier-specific residual patches
- strongest result:
  - shared exact core:
    - `17`
  - `v41`-only patches:
    - `3`
  - `v46`-only patches:
    - `2`
  - residual patch union:
    - `5`
  - residual template count in the current conjunction-shape grammar:
    - `5`

Why it mattered:

- this sharpens the template vision from “there is overlap” to “there is a large stable core and a small irreducible patch language”
- it identifies exactly where syntax-only template loops stop helping

Boundary learned:

- the next honest family is semantic patching or a stronger explanatory language, not another syntax-only template pass

### New survivor: typed semantic-patch frontier

Bounded result:

- keep the shared exact core from `v49`:
  - `17` formulas
- keep the `5` residual patch formulas from `v49`
- compare:
  - nearest-core patch attachment
  - typed edit-signature search over all core attachments
- strongest result:
  - nearest-core attachment uses:
    - `5` signatures
  - typed edit-signature search uses:
    - `4` signatures
  - best total edit cost:
    - `15`

Why it mattered:

- this is the first survivor that moves beyond syntax-only template compilers on the residual language
- it shows the residual is not fully irreducible once typed edit semantics are allowed

Boundary learned:

- the next honest step is richer semantic patching or a stronger family beyond patching

### New survivor: semantic macro-family frontier

Bounded result:

- keep the shared exact core from `v49`:
  - `17`
- keep the residual patch set:
  - `5`
- search over semantic macro families:
  - `ADD_LITERAL`
  - `DROP_LITERAL`
  - `FLIP_SIGN`
- strongest result:
  - exact family count:
    - `2`
  - exact family subset:
    - `ADD_LITERAL`
    - `FLIP_SIGN`
  - no exact one-family solution exists
  - best total macro-instance count:
    - `11`

Why it mattered:

- this is the first exact bounded macro basis on the residual semantic-patch line
- it shows the frontier has really moved beyond syntax-only template compilers

Boundary learned:

- the next honest step is richer semantic patching or a comparison against stronger explanatory families

### New survivor: bundle semantic-macro frontier

Bounded result:

- keep the shared exact core from `v49`:
  - `17`
- keep the residual patch set:
  - `5`
- search over bundle macro families:
  - `ADD_BUNDLE`
  - `DROP_BUNDLE`
  - `FLIP_BUNDLE`
- strongest result:
  - exact family subset:
    - `ADD_BUNDLE`
    - `FLIP_BUNDLE`
  - no exact one-family solution exists
  - best total macro-instance count:
    - `6`

Why it mattered:

- this is a real strengthening of the semantic macro line, not only a reformulation
- bundled macro semantics cut the exact macro count from `11` to `6`

Boundary learned:

- the next honest step is either still richer semantic patching or a direct comparison against stronger loop families

### New survivor: semantic fiber decomposition frontier

Bounded result:

- search all `52` set partitions of the five residual patches
- within each fiber, search the smallest exact bundled macro-family subset
- strongest result:
  - mixed patches:
    - `1`
  - mixed fibers:
    - `1`
  - total fibers:
    - `3`
  - best decomposition:
    - pure `FLIP_BUNDLE` fiber of size `3`
    - pure `ADD_BUNDLE` fiber of size `1`
    - mixed `ADD_BUNDLE + DROP_BUNDLE` singleton fiber of size `1`

Why it mattered:

- this is the first exact bounded explanation-fiber object in the semantic patch line
- it shows the residual language is almost fiber-pure, not just globally compressible

Boundary learned:

- the remaining obstruction is only one mixed singleton patch under the searched bundled macro language

### New survivor: fiber-certificate frontier

Bounded result:

- keep the exact `v53` explanation-fiber labels on the five residual patches
- search certificate languages over:
  - `has_add`
  - `has_drop`
  - `has_flip`
- strongest result:
  - exact all-positive cost:
    - `3`
  - exact positive-cover plus residual-default cost:
    - `2`
  - winning residual-default language:
    - certify `ADD_BUNDLE + DROP_BUNDLE` by `has_drop`
    - certify `FLIP_BUNDLE` by `has_flip`
    - default `ADD_BUNDLE`

Why it mattered:

- the explanation-fiber object now has a smaller exact certificate presentation
- it shows the fiber line compresses one step further once the exact family
  labels are known

Boundary learned:

- this is still descriptive-oracle, because the features come from the
  precomputed fiber labels

### New survivor: direct delta-certificate frontier

Bounded result:

- keep the same five residual patch formulas
- derive direct symbolic features from each `core -> patch` edit:
  - `has_add`
  - `has_drop`
  - `has_flip`
- strongest result:
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

Why it mattered:

- the same exact residual family split can now be recovered directly from
  symbolic patch deltas
- this is the first point where the certificate line upgrades from descriptive
  relabeling to a direct bounded symbolic compiler

Boundary learned:

- the current compiler is still oracle-dependent because the residual symbolic
  state comes from the earlier frontier

### New survivor: direct delta basis frontier

Bounded result:

- keep the exact `v55` direct symbolic residual-family compiler
- search all nonempty subsets of:
  - `has_add`
  - `has_drop`
  - `has_flip`
- strongest result:
  - smallest exact all-positive basis size:
    - `2`
  - smallest exact positive-cover plus residual-default basis size:
    - `2`
  - exact minimal bases:
    - `has_add`, `has_drop`
    - `has_drop`, `has_flip`
  - no singleton basis is exact

Why it mattered:

- this exposes the direct compiler's minimal internal structure
- it shows the compiler is not only exact, it is exact on a smaller basis than
  the original three-coordinate presentation

Boundary learned:

- the bounded data does not select a unique second coordinate
- `has_drop` is essential, but transfer is still needed to decide whether
  `has_add` or `has_flip` is the stronger companion

### New survivor: raw edit-basis frontier

Bounded result:

- remove the aggregated direct delta coordinates
- search exact compilers over raw observed primitive edits:
  - `add[3]`
  - `add[6]`
  - `add[8]`
  - `add[10]`
  - `drop[12]`
  - `flip[6]`
  - `flip[8]`
  - `flip[9]`
  - `flip[12]`
- strongest result:
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

Why it mattered:

- the direct symbolic compiler survives after the aggregated semantic
  coordinates are removed
- this is the sharpest direct symbolic object in the current residual-family
  line

Boundary learned:

- the primitive search still leaves a family of six minimal bases
- the next honest step is transfer or template compression, not another local
  basis shrink claim

### New survivor: primitive basis template frontier

Bounded result:

- keep the six exact raw primitive all-positive bases from `v57`
- search exact two-slot product templates over:
  - `add[3]`
  - `add[6]`
  - `add[8]`
  - `add[10]`
  - `drop[12]`
- strongest result:
  - exact two-slot product template, unique up to slot swap
  - one slot:
    - `add[3]`, `add[6]`, `add[10]`
  - the other slot:
    - `add[8]`, `drop[12]`
  - the residual-default family is the same six-pair template crossed with all
    three default labels

Why it mattered:

- the raw primitive line now has an exact role grammar instead of only a small
  atlas of surviving bases
- this is the first exact template object above the direct primitive bases

Boundary learned:

- the template is still descriptive-oracle
- the next honest step is transfer or a deeper explanation of the two slots

### New survivor: role-slot compiler frontier

Bounded result:

- keep the exact raw primitive basis family from `v57`
- search disjoint nonempty slot pairs over the primitive features
- require both:
  - exact reproduction of the six primitive bases
  - exact direct label compilation
- strongest result:
  - unique up to slot swap
  - slot `a`:
    - `add[3]`, `add[6]`, `add[10]`
  - slot `b`:
    - `add[8]`, `drop[12]`
  - exact all-positive label compiler:
    - `ADD_BUNDLE` by `slot_a and not slot_b`
    - `ADD_BUNDLE + DROP_BUNDLE` by `slot_b`
    - `FLIP_BUNDLE` by `not slot_a`
  - residual-default presentation:
    - certify `ADD_BUNDLE + DROP_BUNDLE` by `slot_b`
    - certify `FLIP_BUNDLE` by `not slot_a`
    - default `ADD_BUNDLE`

Why it mattered:

- this upgrades the exact role grammar into a direct bounded symbolic compiler
- it is the sharpest current object in the residual-family line

Boundary learned:

- the next honest step is transfer to a larger residual family or a semantic
  explanation of why these two slots are the right ones

### New survivor: quotient boundary frontier

Bounded result:

- keep the same five residual patch formulas and raw primitive edit features
- compare:
  - smallest exact `label_only` slot quotient
  - smallest exact `basis_faithful` slot quotient
- strongest result:
  - exact `label_only` slot cost:
    - `2`
  - exact `basis_faithful` slot cost:
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

Why it mattered:

- this is the cleanest boundary result in the current branch
- it separates predictive compression from structure-preserving compression on
  the same raw symbolic state

Boundary learned:

- the next honest step is no longer another local shrink
- it is transfer or semantic explanation of why the same two role families keep
  reappearing

### New survivor: semantic slot frontier

Bounded result:

- keep the exact `v59` slot roles:
  - `slot_a`
  - `slot_b`
  - `other`
- search the smallest exact metadata basis over:
  - `is_add`
  - `is_drop`
  - `is_flip`
  - `has_AB`
  - `has_MIX`
  - `has_FLIP`
  - `count_1`
  - `count_2`
- strongest result:
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

Why it mattered:

- this is the first exact semantic explanation of why the recurring slot roles
  exist
- it sharpens the branch from structural quotients to semantic role laws

Boundary learned:

- the support-profile explanation is still descriptive-oracle
- the next honest step is transfer to a larger residual family or a larger
  domain with the same semantic metadata

### New survivor: shared role semantics frontier

Bounded result:

- define the support-profile partition:
  - `ADD_ANCHOR` iff `has_AB`
  - `MIX_DISCRIM` iff `not has_AB and has_MIX`
  - `OTHER` iff `not has_MIX`
- strongest result:
  - this partition exactly matches the exact `v59` slot roles
  - its singleton cross product exactly equals the unordered minimal
    `label_only` quotients from `v60`

Why it mattered:

- it is the first exact shared semantic control law across both exact
  objectives in the branch
- it unifies the predictive and structure-preserving sides of the residual
  family line

Boundary learned:

- the law is still bounded and oracle-dependent
- the next honest step is transfer to a larger residual family or transfer
  domain

### New survivor: support-signature transfer frontier

Bounded result:

- Domain A, earlier cross-frontier schema roles from `v49`:
  - `CORE`
  - `V41_PATCH`
  - `V46_PATCH`
  - support bits:
    - `has_v41`
    - `has_v46`
- Domain B, residual primitive roles from `v62`:
  - `ADD_ANCHOR`
  - `MIX_DISCRIM`
  - `OTHER`
  - support bits:
    - `has_AB`
    - `has_MIX`
- strongest result:
  - both domains compile exactly by two-bit support signatures
  - Domain A:
    - `CORE` by `has_v41 and has_v46`
    - `V41_PATCH` by `not has_v46`
    - `V46_PATCH` by `not has_v41`
  - Domain B:
    - `ADD_ANCHOR` by `has_AB`
    - `MIX_DISCRIM` by `not has_AB and has_MIX`
    - `OTHER` by `not has_MIX`

Why it mattered:

- the support-profile law from `v62` is not only local to the residual-family
  branch
- it transfers to a second exact frontier as a generic support-signature role
  law

Boundary learned:

- the transfer is still bounded and oracle-dependent
- the next honest step is a larger residual family or a loop that discovers
  support-signature laws directly

### New survivor: support-literal compiler frontier

Bounded result:

- three exact domains were checked:
  - Domain A:
    - `v49` cross-frontier schema roles
    - support bits `has_v41`, `has_v46`
  - Domain B:
    - `v62` residual primitive roles
    - support bits `has_AB`, `has_MIX`
  - Domain C:
    - `v55` direct patch-delta roles
    - support bits `has_add`, `has_drop`, `has_flip`
- strongest result:
  - no exact single-branch support compiler exists on any domain
  - every domain admits an exact residual-default support compiler with:
    - `2` branches
    - total literal cost `2`
- preferred exact compilers:
  - Domain A:
    - `V41_PATCH` by `not has_v46`
    - `V46_PATCH` by `not has_v41`
    - default `CORE`
  - Domain B:
    - `ADD_ANCHOR` by `has_AB`
    - `OTHER` by `not has_MIX`
    - default `MIX_DISCRIM`
  - Domain C:
    - `ADD_BUNDLE+DROP_BUNDLE` by `has_drop`
    - `FLIP_BUNDLE` by `has_flip`
    - default `ADD_BUNDLE`

Why it mattered:

- the support-signature branch is no longer only a transferred role law
- it now has a tiny exact compiler family across three bounded frontiers
- this is the sharpest reusable object yet in the support-signature line

Boundary learned:

- the result is still bounded and mostly oracle-dependent
- the next honest step is larger transfer, or a loop that discovers
  support-literal compilers directly from role tables

### New survivor: three-signature support law frontier

Bounded result:

- abstract family:
  - labeled `3`-role support tables
  - one distinct realized support signature per role
  - support widths `2` through `7`
- strongest result:
  - every table in the bounded family admits:
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
- the three live support domains from `v64` are exact instances of the same
  law

Why it mattered:

- the support-literal line is now stronger than a three-domain family pattern
- it is a bounded support-table law candidate for the whole `3`-role case
- this is the sharpest generic result yet in the support-signature branch

Boundary learned:

- the law is still bounded and support-table based
- the next honest step is the first `4`-role obstruction or extension

### New survivor: four-role support cost frontier

Bounded result:

- abstract family:
  - labeled `4`-role support tables
  - one distinct realized support signature per role
  - support widths `2` and `3`
- width `2`:
  - `24 / 24` labeled tables
  - no single-literal star cases
  - exact minimal total literal cost:
    - `6` for all `24`
- width `3`:
  - `1680` labeled tables
  - single-literal star cases:
    - `192`
  - exact minimal total-literal-cost ladder:
    - cost `3`: `192`
    - cost `4`: `576`
    - cost `5`: `576`
    - cost `6`: `336`

Why it mattered:

- the `3`-role support law fails immediately for `4` roles
- the next regime is not another uniform cheap law
- it is an exact bounded compiler-cost ladder

Boundary learned:

- the next honest step is geometric classification of the width-`3` ladder, or
  width `4`

### New survivor: width3 four-role geometry frontier

Bounded result:

- abstract family:
  - labeled `4`-role support tables
  - one distinct realized support signature per role
  - width `3`
  - quotient by cube automorphisms on unlabeled `4`-subsets
- strongest result:
  - exactly `6` orbit classes
  - every orbit has a uniform exact compiler cost
  - atlas:
    - `(0,1,2,4)`, claw, cost `3`
    - `(0,1,2,5)`, path, cost `4`
    - `(0,1,2,7)`, vee-plus-isolated, cost `5`
    - `(0,1,2,3)`, square, cost `6`
    - `(0,1,6,7)`, disjoint-edge, cost `6`
    - `(0,3,5,6)`, independent, cost `6`

Why it mattered:

- the width-`3` `4`-role frontier is now a small exact geometry atlas
- the `v66` cost ladder was not only a histogram
- this is the cleanest structural object yet on the `4`-role line

Boundary learned:

- the next honest step is width `4`, or a smaller invariant family that
  predicts the orbit cost directly

### New survivor: width3 invariant law frontier

Bounded result:

- bounded domain:
  - the exact six-orbit width-`3` atlas from `v67`
  - searched invariants:
    - `edge_count`
    - `max_degree`
    - `leaf_count`
    - `isolated_count`
    - `connected`
    - `component_sizes`
    - `degree_sequence`
- strongest result:
  - `degree_sequence` is already an exact singleton invariant
  - but among the searched scalar invariants, no singleton is exact
  - the simplest exact scalar basis is:
    - `(edge_count, max_degree)`
  - exact scalar law:
    - `(3,3) -> 3`
    - `(3,2) -> 4`
    - `(2,2) -> 5`
    - otherwise `-> 6`

Why it mattered:

- the width-`3` `4`-role frontier now has a real invariant law above the atlas
- this turns the geometry object into a cleaner compression ladder

Boundary learned:

- the next honest step is width `4`, or testing whether a similarly small
  scalar law survives there

### New survivor: width4 support-profile frontier

Bounded result:

- abstract family:
  - labeled `4`-role support tables
  - one distinct realized support signature per role
  - width `4`
- per-role statistic:
  - minimal unique-support size, the fewest support bits needed to distinguish
    one role from the other three
- strongest result:
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
  - exact cost law:
    - the minimal compiler cost is the sum of the three smallest profile
      entries
    - so the cost ladder is:
      - `3`
      - `4`
      - `5`
      - `6`

Why it mattered:

- the width-`4` frontier did not immediately fragment into an opaque histogram
- it already admits a small exact support-profile law
- this is the cleanest upward extension of the width-`3` scalar invariant line

Boundary learned:

- the next honest step is no longer “does width `4` have structure at all?”
- it is:
  - whether a smaller scalar or geometric law sits above this profile law,
  - or where the first true obstruction beyond the six-profile family appears

### New survivor: width4 support-count law frontier

Bounded result:

- input frontier:
  - the exact six-profile width-`4` support-profile object from `v69`
- searched scalar library:
  - `count_private_roles`
  - `count_size2_roles`
  - `count_size3_roles`
  - `max_support_size`
  - `sum_support_sizes`
  - `sum_three_smallest`
  - `smallest_support_size`
- strongest result:
  - exact cost already collapses to one scalar:
    - `count_private_roles`
  - exact law:
    - `4 -> 3`
    - `3 -> 3`
    - `2 -> 4`
    - `1 -> 5`
    - `0 -> 6`

Why it mattered:

- the width-`4` line is cleaner than the raw six-profile statement
- exact cost does not need the whole profile
- it only needs the count of roles with private one-bit witnesses

Boundary learned:

- full profile reconstruction still needs more than one scalar
- so cost control and structure reconstruction have separated objectives

### New survivor: width4 profile-pair law frontier

Bounded result:

- input frontier:
  - the exact six-profile width-`4` support-profile object from `v69`
- strongest result:
  - no searched singleton scalar reconstructs the full profile exactly
  - the pair:
    - `count_private_roles`
    - `max_support_size`
    does reconstruct it exactly

Why it mattered:

- this completes the width-`4` compression ladder
- exact cost needs one scalar
- exact full profile needs two scalars

Boundary learned:

- the next honest step is no longer support-profile compression alone
- it is whether the width-`4` orbit space admits a similarly small law

### New survivor: width4 orbit support-count transfer frontier

Bounded result:

- abstract family:
  - unlabeled `4`-subsets of the `4`-cube
  - quotiented by cube automorphisms
  - exhaustive orbit count:
    - `19`
- strongest result:
  - the exact width-`4` support-count laws from `v70` and `v71` survive
    unchanged:
    - exact cost is determined by `count_private_roles`
    - exact full profile is reconstructed by:
      - `count_private_roles`
      - `max_support_size`

Why it mattered:

- the support-count line is no longer a one-presentation artifact
- it survives across:
  - the labeled-table frontier
  - the unlabeled orbit frontier

Boundary learned:

- the next honest step is no longer “does the law transfer?”
- it is where the first width-`4` geometric obstruction appears beyond this
  transferred law

### New survivor: width4 orbit mixed-basis frontier

Bounded result:

- bounded domain:
  - the full width-`4` unlabeled orbit family, `19` orbits
- strongest result:
  - support counts alone do not determine orbit class
  - no searched singleton mixed basis is exact
  - the first exact mixed bases are:
    - `count_private_roles` plus `distance_multiset`
    - `count_size2_roles` plus `distance_multiset`

Why it mattered:

- this is the first genuine width-`4` geometric obstruction after the
  transferred support-count laws
- the obstruction is still tiny, because one geometric multiset finishes orbit
  reconstruction exactly

Boundary learned:

- support counts are enough for cost and profile, but not for full orbit class
- the next honest step is whether the mixed basis can be scalarized further

### New survivor: width4 orbit scalarized mixed-law frontier

Bounded result:

- bounded domain:
  - the full width-`4` unlabeled orbit family, `19` orbits
- searched scalar support-plus-geometry library:
  - `count_private_roles`
  - `count_size2_roles`
  - `max_degree`
  - `isolated_count`
  - `diameter`
- strongest result:
  - no searched singleton scalar is exact
  - no searched scalar pair is exact
  - exact scalar triples do exist
  - preferred exact triple:
    - `count_private_roles`
    - `max_degree`
    - `diameter`

Why it mattered:

- the first genuine width-`4` obstruction still collapses to a tiny scalar law
- the branch now has:
  - transferred support-count laws
  - one mixed support-plus-geometry basis
  - one exact scalarized mixed law

Boundary learned:

- the next honest step is the first width-`4` phenomenon that escapes this
  three-scalar mixed law, or a proof that the current scalar law is minimal in
  a wider feature library

### New survivor: width4 broad-scalar minimality frontier

Bounded result:

- bounded domain:
  - the full width-`4` unlabeled orbit family, `19` orbits
- widened scalar support-plus-geometry library:
  - `21` searched scalar features
- strongest result:
  - no searched singleton scalar is exact
  - no searched scalar pair is exact
  - exact scalar triples do exist
  - preferred exact triple remains:
    - `count_private_roles`
    - `max_degree`
    - `diameter`

Why it mattered:

- the `v74` three-scalar law was not an artifact of a too-small scalar library
- the first exact scalar basis still has size `3` under a much broader bounded
  search

Boundary learned:

- the next honest step is no longer “was there a hidden scalar pair?”
- it is:
  - the first width-`4` phenomenon that escapes the three-scalar law
  - or stronger minimality in an even wider invariant library

### New survivor: width4 mixed-basis uniqueness frontier

Bounded result:

- bounded domain:
  - the full width-`4` unlabeled orbit family, `19` orbits
- widened tuple-aware mixed library:
  - support-count coordinates
  - full support profile
  - degree sequence
  - component sizes
  - distance multiset
- strongest result:
  - the only nontrivial exact pair bases are:
    - `count_private_roles` plus `distance_multiset`
    - `count_size2_roles` plus `distance_multiset`

Why it mattered:

- the first width-`4` obstruction is not just small
- it is also rigid in the searched mixed basis space

Boundary learned:

- the next honest step is the first width-`4` phenomenon that escapes both:
  - the current three-scalar law
  - the current rigid mixed basis family

### New survivor: minimal witness-language phase diagram

Bounded result:

- bounded domain:
  - the repaired `10`-state `(H6, E)` verifier frontier reused from `v24`,
    `v35`, and `v36`
- compared exact language families:
  - pure positive atom covers
  - mixed atom covers with residual default
  - invented positive covers
  - ordered decision-list compiler
- strongest result:
  - no single universally best exact language survives once the witness
    semantics are fixed
  - smallest all-positive unordered language:
    - invented positive-cover family
    - cost `4`
  - smallest unordered residual-default language:
    - mixed atom-cover family
    - cost `4`
  - smallest ordered exact classifier:
    - decision-list compiler
    - guard count `4`

Why it mattered:

- this is the first explicit bounded phase diagram in the repo for
  `minimal witness-language discovery`
- verifier compilation is still a strong survivor, but it now sits inside a
  larger exact language-selection problem

Boundary learned:

- this result compares only four already-surviving language families on one
  bounded frontier
- the next honest step is:
  - direct search over a larger bounded witness-language family
  - or the same phase-diagram comparison on a harder frontier where the current
    exact families no longer tie at cost `4`

### New survivor: hard witness-language phase diagram

Bounded result:

- bounded domain:
  - the hard refill witness frontier reused from `v40`, `v44`, and `v46`
- compared exact language families:
  - score-local residual-default witnesses
  - merged-region residual-default witnesses
  - shared global witness-schema language
- strongest result:
  - the harder frontier yields a strict exact ladder:
    - score-local residual-default witnesses:
      - cost `27`
    - merged-region residual-default witnesses:
      - cost `22`
    - shared global witness-schema language:
      - size `19`
  - local all-positive witnesses already fail on:
    - `9`
    - `10`

Why it mattered:

- `v77` showed a frontier where several exact language families tie once the
  witness contract is fixed
- this harder frontier shows a stronger phenomenon:
  widening the witness contract strictly lowers exact description size

Boundary learned:

- the compared families are still previously surviving exact objects rather than
  a direct larger-grammar language search
- the next honest step is:
  - direct search over a wider witness-language family on the same hard
    frontier
  - or comparison against certificate or decomposition languages, not only
    witness-cover languages

### New survivor: hard decomposition-language boundary

Bounded result:

- bounded domain:
  - the same hard merged-region witness frontier from `v44` and `v46`
- compared families:
  - exact bit-fiber decomposition
  - exact label-level witness language
- strongest result:
  - bit-fiber decomposition survives exactly
  - but it is strictly worse:
    - bit-fiber total cost:
      - `24`
    - label-level total cost:
      - `22`
    - bit-fiber shared schema count:
      - `21`
    - label-level shared schema count:
      - `19`

Why it mattered:

- the next family comparison is now grounded
- decomposition is not only imaginable, it is executable and exact on the same
  bounded corpus
- but on this frontier it does not beat the current label-level witness
  language

Boundary learned:

- this compares raw bit-fiber decomposition against the current label-level
  witness family
- the next honest step is:
  - certificate-language comparison on the same hard frontier
  - or richer decomposition languages that are not limited to raw label bits

### New survivor: hard certificate-language boundary

Bounded result:

- bounded domain:
  - the same hard merged-region witness frontier from `v44`
- compared families:
  - exact all-positive certificates
  - exact residual-default witness language
- strongest result:
  - the searched all-positive certificate family is not exact everywhere
  - it already fails on region:
    - `(10,11)`
  - even on the four feasible regions it is still larger:
    - feasible-region certificate cost:
      - `23`
    - feasible-region shared schema count:
      - `21`

Why it mattered:

- this is stronger than only saying residual-default witnessing is cheaper
- on the hard frontier, the stricter all-positive certificate family is not
  even exact in the searched grammar

Boundary learned:

- this rules out one natural certificate family on the same hard frontier
- the next honest step is:
  - richer certificate languages on the same bounded corpus
  - or certificate languages with a small amount of local residual structure

### New survivor: hard local residual-budget ladder

Bounded result:

- bounded domain:
  - the same hard merged-region witness frontier from `v44` and `v80`
- compared families:
  - all-positive certificate regions
  - residual-default witness regions
  - mixed locally on the exact `v44` partition
- strongest result:
  - strict all-positive certification is impossible
  - exactness already returns once:
    - `1` residual region is allowed
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

Why it mattered:

- this strengthens `v80` from a hard failure into an exact ladder
- on this frontier residual structure is neither free nor all-or-nothing
- it has a bounded entry threshold and then a strict cost curve

Boundary learned:

- this is still local residual budgeting on one fixed partition
- the next honest step is:
  - compare against a more global shared-schema optimization on the same hard
    frontier
  - or search richer certificate languages with local residual structure
