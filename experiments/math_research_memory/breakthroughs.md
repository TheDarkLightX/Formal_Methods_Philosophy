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

### New survivor: hard residual-budget schema ladder

Bounded result:

- bounded domain:
  - the same hard merged-region witness frontier from `v44`, `v46`, `v80`, and
    `v81`
- compared objects:
  - fixed residual budgets on the exact `v44` partition
  - global shared-schema optimization across all regions at each budget
- strongest result:
  - strict all-positive certification is still impossible
  - best exact shared-schema count by residual budget:
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
  - the same exact total-cost ladder survives:
    - `28`
    - `26`
    - `24`
    - `23`
    - `22`
  - every feasible rung improves by exactly `1` schema relative to `v81`

Why it mattered:

- this strengthens the hard residual-budget line from a local accounting result
  into a global schema-sharing law
- the full residual budget does not just approach the older witness optimum
- it lands exactly on the `v46` shared-schema optimum

Boundary learned:

- this is still a fixed-partition result on one hard frontier
- the next honest step is:
  - richer certificate grammars with local residual structure on the same hard
    frontier
  - or transfer of the global residual-budget law to a second hard frontier

### New survivor: hard partition-aware residual-budget frontier

Bounded result:

- bounded domain:
  - the same hard `v38` witness frontier from `v44` through `v82`
- searched object:
  - score partition
  - exact residual-region budget
  - global shared-schema objective
- strongest result:
  - the fixed `v44` partition is not globally optimal for budgets `1` through
    `4`
  - best exact shared-schema ladder becomes:
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
  - exact total-cost ladder remains:
    - `28`
    - `26`
    - `24`
    - `23`
    - `22`
  - low-budget optima merge scores as:
    - `(7,12)`
    - `(9,10)`

Why it mattered:

- this is the first hard-frontier result where partition itself becomes part of
  the residual-budget loop
- the earlier fixed partition was a survivor, but not the global optimum under
  the stronger shared-schema objective

Boundary learned:

- this is still one hard frontier in one grammar
- the next honest step is:
  - richer certificate grammars on the same joint search
  - or transfer of the same partition-aware residual-budget search to a second
    hard frontier

### New survivor: hard critical-region certificate widening boundary

Bounded result:

- bounded domain:
  - the same hard `v38` witness frontier reused through `v83`
  - the exact union of score regions appearing in the `v83` optimal partitions
- searched object:
  - strict all-positive certificates
  - compare the `1..4` literal grammar against the `1..5` literal grammar
- strongest result:
  - only one critical region changes:
    - `(10,11)`
  - `(10,11)` flips from:
    - impossible in `1..4`
    - exact cost `6` in `1..5`
  - every other critical region keeps the same minimal exact cost

Why it mattered:

- this separates a uniform logic failure from a localized grammar failure
- the current hard-frontier wall is partly grammatical
- but the evidence is still scoped to the critical-region union rather than the
  full widened joint search

Boundary learned:

- this is not yet a full rerun of the `v83` partition-aware search in the wider
  grammar
- the next honest step is:
  - rerun the joint search under the widened certificate grammar
  - or test whether the same localized grammar wall appears on a second hard
    frontier

### New survivor: hard widened-certificate partition-aware residual-budget frontier

Bounded result:

- bounded domain:
  - the same hard `v38` witness frontier reused through `v84`
- searched object:
  - full `v83` joint search over score partitions and residual budgets
  - residual-default witness regions in the `1..4` literal grammar
  - strict certificate regions in the widened `1..5` literal grammar
- strongest result:
  - a zero-residual exact rung now exists:
    - shared schemas `25`
    - total cost `29`
    - partition:
      - `(7,12)`
      - `(8)`
      - `(9)`
      - `(10,11)`
  - budgets `1` and `2` improve over `v83` by:
    - one schema
    - one total-cost unit
  - budgets `3`, `4`, and `5` are unchanged

Why it mattered:

- this shows the localized `v84` grammar relief was not only a local artifact
- it changes the actual hard-frontier joint search
- but only in the low-residual regime

Boundary learned:

- the widened certificate grammar does not move the high-residual end of the
  frontier
- the next honest step is:
  - transfer the same widened-certificate search to a second hard frontier
  - or search richer certificate grammars for budgets `3` and above

### New survivor: high-residual widened-certificate saturation boundary

Bounded result:

- bounded domain:
  - the same hard `v38` witness frontier reused through `v85`
- searched object:
  - high-residual slice of the partition-aware residual-budget frontier
  - residual-default witnesses in the `1..4` literal grammar
  - strict certificates widened from `1..5` to `1..6` literals
- strongest result:
  - budgets `3`, `4`, and `5` do not move at all
  - exact high-residual ladder stays:
    - `3`:
      - shared schemas `20`
      - total cost `24`
    - `4`:
      - shared schemas `19`
      - total cost `23`
    - `5`:
      - shared schemas `19`
      - total cost `22`

Why it mattered:

- this turns the `v85` high end from an empirical plateau into an exact
  saturation boundary
- the remaining obstruction in that regime is no longer exposed by this
  literal-width increase

Boundary learned:

- the next honest move is no longer another small width increase
- it is:
  - transfer to a second hard frontier
  - or a genuinely richer certificate language

### New survivor: low-residual widened-certificate saturation boundary

Bounded result:

- bounded domain:
  - the same hard `v38` witness frontier reused through `v86`
- searched object:
  - low-residual slice of the partition-aware residual-budget frontier
  - residual-default witnesses in the `1..4` literal grammar
  - strict certificates widened from `1..5` to `1..6` literals
- strongest result:
  - budgets `0`, `1`, and `2` do not move at all
  - exact low-residual ladder stays:
    - `0`:
      - shared schemas `25`
      - total cost `29`
    - `1`:
      - shared schemas `23`
      - total cost `27`
    - `2`:
      - shared schemas `21`
      - total cost `25`

Why it mattered:

- this closes the last open slice on the current literal-width axis
- the full hard partition-aware residual-budget ladder is now locally saturated
  against widening strict certificates from `1..5` to `1..6` literals

Boundary learned:

- another small width increase is no longer the honest next move on this
  frontier
- the next honest move is:
  - transfer to a second hard frontier
  - or a genuinely richer certificate language

### New survivor: lab-followup partition-aware residual-budget transfer frontier

Bounded result:

- bounded domain:
  - the residual-consistent unique-behavior frontier from `v26`
  - mixed score blocks:
    - `1`
    - `2`
    - `3`
    - `4`
- searched object:
  - partition-aware residual-budget witness-language search
  - `1..4` signed conjunctions over the five holdout error bits
  - same grammar for strict certificates and residual-default witnesses
- strongest result:
  - exact schema-first ladder:
    - `0`:
      - shared schemas `5`
      - total cost `5`
    - `1`:
      - shared schemas `4`
      - total cost `4`
    - `2`:
      - shared schemas `4`
      - total cost `5`
    - `3`:
      - shared schemas `4`
      - total cost `7`
    - `4`:
      - shared schemas `6`
      - total cost `10`
  - best exact budget is:
    - `1`
  - best partition:
    - one merged residual-default region over:
      - `(1,2,3,4)`

Why it mattered:

- this is a real transfer result for the residual-budget witness-language loop
- the same loop shape survives on a second domain
- but the exact geometry changes sharply:
  - refill preferred a descending ladder
  - lab-followup prefers one merged exception layer

Boundary learned:

- transfer does not preserve the same residual-budget law shape
- the next honest move is:
  - compare this transfer object against a richer certificate language
  - or explain semantically why one merged residual region is optimal here

### New survivor: lab-followup widened-certificate saturation boundary

Bounded result:

- bounded domain:
  - the exact lab-followup transfer frontier from `v88`
- searched object:
  - same partition-aware residual-budget search
  - residual-default witnesses stay in the `1..4` literal grammar
  - strict certificates widen from `1..4` to `1..5` literals
- strongest result:
  - nothing moves
  - exact ladder stays:
    - `0`:
      - shared schemas `5`
      - total cost `5`
    - `1`:
      - shared schemas `4`
      - total cost `4`
    - `2`:
      - shared schemas `4`
      - total cost `5`
    - `3`:
      - shared schemas `4`
      - total cost `7`
    - `4`:
      - shared schemas `6`
      - total cost `10`

Why it mattered:

- this shows the merged transfer object from `v88` is not a `1..4`
  certificate-grammar artifact
- the whole lab-followup ladder is already locally saturated on this
  literal-width axis

Boundary learned:

- the next honest move is not one more literal on this frontier
- it is:
  - a richer certificate language
  - or a semantic invariant explaining the merged residual region

### New survivor: lab-followup unsafe earliest-error residual law

Bounded result:

- bounded domain:
  - the full unsafe block of the toy lab-followup frontier
  - holdout scores:
    - `0`
    - `1`
    - `2`
    - `3`
    - `4`
- searched object:
  - exact all-positive and residual-default witness languages
  - `1..4` signed conjunctions over the five ordered holdout error bits
- strongest result:
  - exact score-free earliest-error residual-default language:
    - default:
      - `(0,0,1)`
    - certify:
      - `(0,1,0)` by `not e1 and e2`
      - `(0,1,1)` by `not e1 and not e2 and e3`
      - `(1,1,0)` by `not e1 and not e2 and not e3 and e4`
      - `(1,1,1)` by `not e1 and not e2 and not e3 and not e4`
  - unsafe behavior count:
    - `163`
  - exact residual-default cost:
    - `4`
  - exact all-positive cost:
    - `5`

Why it mattered:

- this gives a semantic explanation for the merged residual region from `v88`
- the lab-followup transfer frontier now has a direct score-free explanatory
  law, not only a residual-budget optimum

Boundary learned:

- the next honest move is:
  - compare this explanatory law against a richer certificate language
  - or search for an analogous score-free law on the refill frontier

### New survivor: refill maximal score-free merged-subunion boundary

Bounded result:

- bounded domain:
  - the hard refill frontier from `v29` to `v46`
  - nontrivial scores:
    - `7`
    - `8`
    - `9`
    - `10`
    - `11`
    - `12`
- searched object:
  - all merged score subunions
  - exact all-positive and residual-default score-free witness languages
  - `1..4` signed conjunctions over the `v42` feature surface
- strongest result:
  - residual-default feasible merged subunions:
    - `13`
  - size profile:
    - `1 -> 6`
    - `2 -> 6`
    - `3 -> 1`
  - all-positive feasible merged subunions:
    - `10`
  - unique maximal exact merged subunion:
    - `(9,10,12)`
  - on `(9,10,12)`:
    - exact all-positive presentation:
      - impossible
    - exact residual-default cost:
      - `10`

Why it mattered:

- this is the clean contrast with `v90`
- the lab-followup frontier admits a whole unsafe-block score-free law
- the refill frontier does not, it only admits sparse exact merged islands in
  the same style of search

Boundary learned:

- the next honest move is:
  - a richer score-free certificate language on refill
  - or a small semantic grammar that enlarges the maximal exact refill subunion

### New survivor: unlock taxonomy for the mature witness-language line

Bounded result:

- bounded domain:
  - the published mature witness-language line:
    - `v78` through `v91`
- searched object:
  - intervention taxonomy over:
    - family comparisons
    - residual-budget search
    - schema sharing
    - partition search
    - grammar widening
    - transfer
    - semantic explanation search
- strongest result:
  - new-axis interventions:
    - cycles:
      - `9`
    - gain cycles:
      - `5`
    - gain-events:
      - `16`
  - same-axis widening:
    - cycles:
      - `5`
    - gain cycles:
      - `2`
    - gain-events:
      - `4`

Why it mattered:

- this turns the recent progression into a cleaner law
- the mature frontier moved when the object of search changed
- it usually did not move much when the current grammar was only widened

Boundary learned:

- the next honest loop family should add a deeper search object
- the strongest next target is:
  - temporal monitor-cell obligation carving on Tau specs

### New survivor: staged temporal monitor-cell obligation quotient

Bounded result:

- bounded domain:
  - the safety-action fragment of
    `medical_retest_protocol_tracker_v1.tau`
  - ordered decision-list controller family over four semantic predicates
  - total candidates:
    - `5832`
- searched object:
  - flat two-step trace obligations
  - symbolic monitor-cell obligations
  - staged comparison after flat step-1 carving
- strongest result:
  - raw whole-family comparison:
    - flat behavior classes:
      - `73`
    - monitor-cell behavior classes:
      - `168`
    - exact partition match:
      - `false`
  - after flat step-1 carving:
    - surviving candidates:
      - `108`
    - flat residual classes:
      - `12`
    - monitor-cell residual classes:
      - `12`
    - exact partition match:
      - `true`
    - exact spec-class match:
      - `true`

Why it mattered:

- this is the first temporal obligation result that survived as a real object
- it shows symbolic state obligations are best introduced in stages
- that lesson transfers back to software engineering:
  - concrete failing tests first
  - symbolic obligation cells or fibers second

Boundary learned:

- Tau did produce a useful side-branch law
- but the main frontier should now move back to higher-leverage software loops,
  not stay inside Tau-specific detail

### New survivor: dependency-aware obligation-fibered repair

Bounded result:

- bounded domain:
  - two software-shaped patch corpora with three edit sites:
    - `guard`
    - `bounds`
    - `transform`
  - `27` patches per corpus
  - three unit-test fibers
- searched object:
  - monolithic patch search
  - naive independent fiber repair
  - dependency-aware fiber repair
- strongest result:
  - on the separable corpus:
    - monolithic average cost:
      - `39.0`
    - naive fibered:
      - exact on `27 / 27`
      - cost:
        - `15.0`
    - dependency-aware:
      - exact on `27 / 27`
      - cost:
        - `9.0`
  - on the overlap corpus:
    - monolithic average cost:
      - `35.851851851851855`
    - naive fibered:
      - exact on `16 / 27`
    - dependency-aware:
      - exact on `27 / 27`
      - cost:
        - `9.0`

Why it mattered:

- this is the first software-engineering-shaped survivor in the current main
  line
- it shows the next object is not only a verifier-side quotient
- it is a dependency graph over repair fibers

Boundary learned:

- naive independent fibering is not enough once failure fibers overlap
- the first exact correction is dependency-aware fibering

### New survivor: certificate-carrying repair basis

Bounded result:

- bounded domain:
  - the two bounded software patch corpora from `v94`
  - three local observation tokens:
    - `guard`
    - `bounds`
    - `transform`
- searched object:
  - minimal exact certificate bases over those local tokens
- strongest result:
  - on both corpora:
    - no singleton basis is exact
    - no pair basis is exact
    - the unique minimal exact basis is:
      - `guard`
      - `bounds`
      - `transform`
  - certificate verification cost:
    - `3`
  - `v94` dependency-aware search cost:
    - `9.0`

Why it mattered:

- this is the first exact software-engineering witness-language result in the
  current main line
- it upgrades the object from:
  - search over repair fibers
  - to direct verification of patch-plus-witness

Boundary learned:

- on this bounded corpus, patch-plus-witness strictly beats dependency-aware
  fiber search
- but the witness language still has a clean exact lower bound:
  - three local observation tokens

### New survivor: certificate-to-patch decoder graph

Bounded result:

- bounded domain:
  - the same two software patch corpora from `v94` and `v95`
  - three witness observations:
    - `guard_obs`
    - `bounds_obs`
    - `transform_obs`
- searched object:
  - exact symbolic decoders from witness observations back to patch fields
- strongest result:
  - separable family:
    - unique minimal exact decoder cost:
      - `3`
    - decoder:
      - `guard <- guard_obs`
      - `bounds <- bounds_obs`
      - `transform <- transform_obs`
  - overlap family:
    - unique minimal exact decoder cost:
      - `4`
    - decoder:
      - `guard <- guard_obs`
      - `bounds <- bounds_obs, transform_obs`
      - `transform <- transform_obs`

Why it mattered:

- this is the first exact repair-language compiler in the software branch
- the witness from `v95` no longer only verifies the patch
- it now compiles back into the patch through a tiny decoder graph

Boundary learned:

- overlap does not destroy local decoding
- it inserts one extra dependency edge into the decoder graph

### New survivor: shared repair-language template

Bounded result:

- bounded domain:
  - the two exact decoder graphs from `v96`
  - `9` possible decoder edges
- searched object:
  - shared base decoder graph plus family deltas
  - both additive and signed-edit template models
- strongest result:
  - unique minimum in both models:
    - base:
      - `guard_obs -> guard`
      - `bounds_obs -> bounds`
      - `transform_obs -> transform`
    - separable family:
      - no delta
    - overlap family:
      - `transform_obs -> bounds`
  - total cost:
    - `4`

Why it mattered:

- this is the first exact shared repair-language grammar in the software branch
- the two family decoders from `v96` are not isolated objects
- they compress into one common base language with one sparse family patch

Boundary learned:

- overlap does not need a new grammar family
- it only adds one delta edge to the shared base template

### New survivor: shared repair-program macro language

Bounded result:

- bounded domain:
  - the two exact software decoder targets from `v97`
  - macro grammar:
    - `6` permutation matchings
    - `3` fanouts
    - `3` fanins
    - `9` single-edge patches
- searched object:
  - exact macro programs for each family target
  - one shared additive macro template plus family deltas
- strongest result:
  - separable family:
    - minimal exact macro cost:
      - `1`
    - unique program:
      - `MATCH_ID`
  - overlap family:
    - minimal exact macro cost:
      - `2`
    - unique program:
      - `MATCH_ID`
      - `SINGLE[transform_obs->bounds]`
  - unique exact shared macro template:
    - base:
      - `MATCH_ID`
    - overlap delta:
      - `SINGLE[transform_obs->bounds]`
    - total cost:
      - `2`

Why it mattered:

- this is the first exact patch-program macro language in the software branch
- the shared local decoder from `v97` is no longer only a graph template
- it compresses into one reusable instruction plus one sparse patch macro

Boundary learned:

- no exact single-macro program exists for the overlap family
- no cost-`1` shared macro template exists in the searched grammar
- the software branch still follows the same deeper rule:
  discover the reusable exact language, then patch only the residual

### New survivor: repair-schema basis

Bounded result:

- bounded domain:
  - a `7`-family software transfer atlas:
    - `1` separable family
    - `6` single-overlap families
  - schema-family search over:
    - `MATCH`
    - `FANOUT`
    - `FANIN`
    - `SINGLE`
- searched object:
  - the smallest exact schema basis under an MDL-like objective:
    schema-basis size plus total instance count across the atlas
- strongest result:
  - singleton exactness:
    - only `SINGLE` is exact
    - but description length:
      - `28`
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

Why it mattered:

- this is the first exact transfer law in the software branch
- the `v98` macro result is not only a two-family coincidence
- the branch now has a reusable schema basis above concrete macro programs

Boundary learned:

- `MATCH` alone is not exact
- `FANIN` and `FANOUT` alone are not exact
- `SINGLE` alone is exact but too expensive
- the smallest reusable exact law is:
  one local-match schema plus one sparse cross-edge patch schema

### New survivor: two-overlap repair-schema obstruction

Bounded result:

- bounded domain:
  - widened software transfer atlas:
    - `1` separable family
    - `6` one-overlap families
    - `15` two-overlap families
  - schema-family search over:
    - `MATCH`
    - `FANOUT`
    - `FANIN`
    - `SINGLE`
- strongest result:
  - the `v99` basis `MATCH + SINGLE` remains exact
  - but it is no longer MDL-optimal:
    - description length:
      - `57`
    - total instance cost:
      - `55`
  - the new exact optimum is:
    - `MATCH`
    - `FANIN`
    - `FANOUT`
    - `SINGLE`
    - description length:
      - `53`
    - total instance cost:
      - `49`

Why it mattered:

- this is the first exact transfer obstruction in the software branch
- the old law does not become false
- it becomes suboptimal once bundled row and column overlap appears

Boundary learned:

- the first obstruction is semantic and geometric, not arbitrary
- row bundles make `FANOUT` pay
- column bundles make `FANIN` pay
- the next frontier should explain that jump semantically, not only by wider
  atlas counts

### New survivor: two-overlap semantic motif law

Bounded result:

- bounded domain:
  - the `15` two-overlap software families from `v100`
- searched object:
  - smallest exact semantic feature basis over:
    - `same_obs`
    - `same_field`
    - `swap_pair`
- strongest result:
  - no singleton basis is exact
  - no pair basis is exact
  - the unique minimal exact basis is:
    - `same_obs`
    - `same_field`
    - `swap_pair`
  - exact rule:
    - row bundle:
      - cost `2`
    - column bundle:
      - cost `2`
    - swap pair:
      - cost `2`
    - all other families:
      - cost `3`

Why it mattered:

- this is the first exact semantic explanation of the first software transfer
  obstruction
- the branch now has:
  - a transfer law,
  - an obstruction,
  - and a compact motif language explaining that obstruction

Boundary learned:

- the first semantic basis size is `3`
- neither row/column structure alone nor swap structure alone is enough
- the next frontier is to compile these motifs into a semantic schema language

### New survivor: semantic repair-schema language

Bounded result:

- bounded domain:
  - the same `22` software families from `v100`
- searched object:
  - smallest exact basis in the semantic schema grammar:
    - `DIAGONAL`
    - `SINGLE`
    - `BUNDLE2`
    - `SWAP2`
- strongest result:
  - unique exact optimum:
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

Why it mattered:

- this is the first exact semantic schema language in the software branch
- the branch now has:
  - a transfer law,
  - an obstruction,
  - a motif law,
  - and a semantic compile step above that motif law

Boundary learned:

- dropping `SINGLE` destroys exactness
- dropping `BUNDLE2` raises description length to `58`
- dropping `SWAP2` raises description length to `55`
- dropping `DIAGONAL` preserves exactness but explodes description length to
  `96`

### New survivor: motif-routed repair compiler

Bounded result:

- bounded domain:
  - the same `22` software families from `v102`
- searched object:
  - smallest exact residual-default router over:
    - `extra0`
    - `extra1`
    - `same_obs`
    - `same_field`
    - `swap_pair`
    - `bundle_motif`
- strongest result:
  - no `1`-branch router is exact
  - no `2`-branch router is exact
  - the first exact router has:
    - `3` branches
  - one exact minimal router:
    - `extra0 -> DIAGONAL`
    - `swap_pair -> DIAGONAL+SWAP_PAIR`
    - `bundle_motif -> BUNDLE2+DIAGONAL`
    - default:
      - `DIAGONAL+SINGLE`

Why it mattered:

- this is the first actual repair policy in the software branch
- the branch now has:
  - a semantic schema language
  - and a compact routed compiler above it

Boundary learned:

- the semantic language really does collapse into a small policy
- but not below three branches in the searched predicate library

### New survivor: typed motif-kind direct repair compiler

Bounded result:

- bounded domain:
  - the same `22` software families from `v102` and `v103`
- searched object:
  - smallest exact typed world-state basis for the full minimal repair program
  - typed coordinate library:
    - `extra_count`
    - `same_obs`
    - `same_field`
    - `swap_pair`
    - `bundle_motif`
    - `motif_kind`
- strongest result:
  - exact direct compiler from raw extra-edge sets
  - unique exact singleton basis:
    - `motif_kind`
  - exact singleton law:
    - `none -> DIAGONAL`
    - `single -> DIAGONAL+SINGLE`
    - `bundle -> DIAGONAL+BUNDLE2`
    - `swap -> DIAGONAL+SWAP2`
    - `other -> DIAGONAL+DOUBLE_SINGLE`
  - exact match count:
    - `22 / 22`
  - total instance cost:
    - `49`

Why it mattered:

- this is the first direct compiler in the software branch
- the branch no longer stops at:
  - a certificate basis,
  - a schema language,
  - or a routed schema policy
- it now has a direct construction law from raw bounded inputs to the full
  minimal repair program

Boundary learned:

- no other searched singleton coordinate is exact
- the next frontier is not another local router refinement
- it is transfer to richer bug families or stronger reformulation above
  `motif_kind`

### New survivor: support-signature direct repair compiler

Bounded result:

- bounded domain:
  - full up-to-three-overlap software atlas
  - family count:
    - `42`
- searched object:
  - smallest exact typed support-signature basis for a direct repair-program
    compiler
  - searched coordinates:
    - `extra_count`
    - `obs_profile`
    - `field_profile`
    - `max_obs`
    - `max_field`
    - `swap_pairs`
    - `same_obs`
    - `same_field`
- strongest result:
  - no singleton is exact
  - no pair basis is exact
  - first exact basis size:
    - `3`
  - exact basis count:
    - `5`
  - preferred symmetric basis:
    - `obs_profile`
    - `field_profile`
    - `swap_pairs`
  - exact match count:
    - `42 / 42`
  - total instance cost:
    - `111`

Why it mattered:

- this is the first real transfer law above the singleton motif compiler
- the direct-compiler story survives the richer atlas
- the state basis deepens from one typed motif coordinate to one small support
  signature

Boundary learned:

- the singleton motif law is a real local optimum, not a universal law
- the next frontier is not another one-off motif category
- it is canonicalization or further transfer above the size-`3` support
  signature

### New survivor: canonical support-signature direct compiler

Bounded result:

- bounded domain:
  - the same `42` software families from `v105`
- searched object:
  - canonical quotient above the exact size-`3` support bases
- strongest result:
  - unique exact singleton basis:
    - `support_signature := (sort(obs_profile, field_profile), swap_pairs)`
  - no other singleton in the augmented coordinate library is exact
  - support-signature count:
    - `8`

Why it mattered:

- the transfer law from `v105` is not only small
- it also admits a true symmetry quotient
- this is the cleanest canonical direct compiler in the branch so far

Boundary learned:

- the next frontier is not another equivalent size-`3` basis
- it is either scalarization above the quotient or transfer beyond the current
  orbit family

### New survivor: four-scalar support law

Bounded result:

- bounded domain:
  - the same `42` software families from `v106`
- searched object:
  - smallest exact scalar basis above the canonical support quotient
- strongest result:
  - no `1`-scalar basis is exact
  - no `2`-scalar basis is exact
  - no `3`-scalar basis is exact
  - first exact basis size:
    - `4`
  - exact size-`4` basis count:
    - `3`
  - preferred basis:
    - `extra_count`
    - `max_obs`
    - `max_field`
    - `swap_pairs`

Why it mattered:

- the canonical support quotient scalarizes again
- the direct compiler now has:
  - a canonical quotient
  - and a compact scalar law above it

Boundary learned:

- the next frontier is not more scalar thinning inside the same tiny library
- it is either a semantic collapse of the exact size-`4` bases or a richer
  transfer domain

### New survivor: three-scalar max-support law

Bounded result:

- bounded domain:
  - the same `42` software families from `v107`
- searched object:
  - semantic scalar collapse above the four-scalar law
- strongest result:
  - no singleton scalar is exact
  - no pair basis is exact
  - first exact basis size:
    - `3`
  - unique exact basis:
    - `extra_count`
    - `max_support`
    - `swap_pairs`

Why it mattered:

- the four-scalar law was not final
- the direct compiler now has an exact three-scalar semantic law above the
  canonical support quotient

Boundary learned:

- the next frontier is not another axis-specific scalar tweak
- it is either a further semantic orbit collapse or a richer transfer domain

### New survivor: two-coordinate support-orbit law

Bounded result:

- bounded domain:
  - the same `42` software families from `v108`
- searched object:
  - smallest exact semantic orbit law above the three-scalar max-support law
- strongest result:
  - no singleton orbit coordinate is exact
  - first exact basis size:
    - `2`
  - unique exact basis:
    - `extra_count`
    - `support_kind`

Why it mattered:

- the support ladder collapsed again
- the software branch now had an exact two-coordinate direct compiler law

Boundary learned:

- the next frontier is not more orbit thinning inside the same atlas
- it is the first richer transfer where one unique repair shape may stop
  surviving

### New survivor: menu-valued support-signature law

Bounded result:

- bounded domain:
  - full software atlas with up to four off-diagonal overlaps
- searched object:
  - exact menu-valued repair law once one unique minimal repair shape is no
    longer guaranteed
- strongest result:
  - canonical library:
    - unique exact singleton:
      - `support_signature`
  - raw support library:
    - no singleton is exact
    - no pair is exact
    - unique exact basis:
      - `obs_profile`
      - `field_profile`
      - `swap_pairs`
  - support-signature states:
    - `11`
  - distinct exact menus:
    - `11`

Why it mattered:

- the first real obstruction above the direct compiler line did not destroy the
  symbolic law
- it changed the target from one chosen repair shape to an exact menu of
  minimal repair shapes

Boundary learned:

- the next frontier is transfer of the menu law, not another local tie-breaker

### New survivor: full-atlas support-signature menu law

Bounded result:

- bounded domain:
  - all `64` subsets of the six off-diagonal repair edges
- searched object:
  - transfer of the menu-valued support-signature law to the full atlas
- strongest result:
  - canonical library:
    - unique exact singleton:
      - `support_signature`
  - raw support library:
    - no singleton is exact
    - no pair is exact
    - unique exact basis:
      - `obs_profile`
      - `field_profile`
      - `swap_pairs`
  - support-signature states:
    - `13`
  - distinct exact menus:
    - `13`

Why it mattered:

- the menu-valued repair law transfers farther than the last direct compiler
- the deeper software object is now clearly a support-signature indexed repair
  menu

Boundary learned:

- the next frontier is either a canonical menu-to-shape tie-breaker or a richer
  bug corpus

### New survivor: normalized support-signature direct compiler family

Bounded result:

- bounded domain:
  - full software atlas over all `64` off-diagonal subsets
- searched object:
  - exact normalized direct compilers above the full-atlas menu law
- strongest result:
  - for all four searched normal forms:
    - canonical library:
      - unique exact singleton:
        - `support_signature`
    - raw support library:
      - no singleton is exact
      - no pair is exact
      - first exact basis:
        - `obs_profile`
        - `field_profile`
        - `swap_pairs`
  - ambiguous families:
    - `40`
  - structural coincidence:
    - `bundle_first` equals `fewest_families`

Why it mattered:

- the menu law is not only descriptive
- it supports a whole family of exact normalized direct compilers
- the software branch now has a stronger post-menu object than a single
  arbitrary canonical repair

Boundary learned:

- the next frontier is not whether normalization exists
- it is the smallest semantic condition that decides which normal form is the
  right one

### New survivor: perfect-swap-cover selector law

Bounded result:

- bounded domain:
  - ambiguous slice of the full software atlas
- searched object:
  - smallest exact selector for whether the exact menu admits a pure-swap normal
    form
- strongest result:
  - exact menu admits a pure-swap normal form iff:
    - `perfect_swap_cover := (extra_count = 2 * swap_pairs)`
  - in the searched selector library:
    - unique exact singleton:
      - `perfect_swap_cover`
  - pure-swap families:
    - `4`
  - pure-swap support signatures:
    - `2`

Why it mattered:

- the post-menu normalized family now has an exact semantic selector above it
- the pure-swap regime is already controlled by one direct Boolean law

Boundary learned:

- the next frontier is the smallest exact selector for bundle-first versus
  swap-first on the full ambiguous slice

### New survivor: bundle-vs-swap disagreement selector law

Bounded result:

- bounded domain:
  - ambiguous slice of the full software atlas
- searched object:
  - smallest exact selector for when the two preferred structural normal forms,
    `bundle_first` and `swap_first`, disagree
- strongest result:
  - no singleton is exact
  - no pair is exact
  - first exact basis size:
    - `3`
  - minimal exact basis count:
    - `8`
  - preferred exact basis:
    - `extra_count`
    - `swap_pairs`
    - `balanced_profiles`
  - preferred exact state count:
    - `7`
  - label histogram:
    - `diff -> 16`
    - `same -> 24`

Why it mattered:

- this is the first exact intrinsic selector above the normalized compiler
  family
- the disagreement between two structurally meaningful normal forms is not
  accidental, and not controlled by any singleton or pair semantic selector in
  the searched library
- but it still collapses to a tiny exact three-coordinate state

Boundary learned:

- the next frontier is the smallest exact selector for bundle-first versus
  single-first on the same ambiguous slice
- or a richer bounded bug corpus where the current disagreement law may break

### New survivor: canonical ambiguity quotient law

Bounded result:

- bounded domain:
  - ambiguous slice of the full software atlas
- searched object:
  - common exact quotient above all pairwise normalized-compiler
    disagreements
- strongest result:
  - among the six pairwise comparisons:
    - constant pairs:
      - `bundle_first` vs `fewest_families -> same`
      - `swap_first` vs `single_first -> diff`
    - non-constant pairs:
      - `4`
  - for all four non-constant pairs:
    - first exact basis size:
      - `3`
    - common minimal exact basis count:
      - `8`
    - preferred common basis:
      - `extra_count`
      - `swap_pairs`
      - `balanced_profiles`
    - preferred quotient state count:
      - `7`

Why it mattered:

- this is stronger than a selector for one special regime or one pairwise
  disagreement
- the remaining ambiguity above the normalized family is not arbitrary
- it factors through one shared exact quotient

Boundary learned:

- the next frontier is the smallest semantic presentation of the common
  7-state ambiguity quotient
- or a richer bounded bug corpus where the shared quotient may fail

### New survivor: support-gap ambiguity law

Bounded result:

- bounded domain:
  - ambiguous slice of the full software atlas
- searched object:
  - smaller semantic presentation of the common ambiguity quotient from v115
- strongest result:
  - no singleton is exact
  - first exact basis size:
    - `2`
  - exact minimal basis count:
    - `1`
  - unique exact basis:
    - `balanced_profiles`
    - `support_gap`
  - preferred state count:
    - `6`
  - disagreement-signature classes:
    - `3`

Why it mattered:

- the shared ambiguity quotient from v115 was not the end of the line
- the post-menu ambiguity layer collapses again in a richer semantic library
- the strongest current software object is now a unique exact size-2 semantic
  law above the whole normalized family

Boundary learned:

- the next frontier is the smallest semantic presentation of the three
  disagreement-signature classes themselves
- or a richer bounded bug corpus where the support-gap law may fail

### New survivor: three-guard ambiguity-class law

Bounded result:

- bounded domain:
  - ambiguous slice of the full software atlas
- searched object:
  - smallest exact branch program for the three disagreement-signature classes
    above v116
- strongest result:
  - no `0`-guard, `1`-guard, or `2`-guard program is exact
  - first exact program:
    - `3` guards
  - exact law:
    - `support_gap = 0 -> class_2`
    - `balanced_profiles and support_gap = 1 -> class_3`
    - `unbalanced_profiles and support_gap = 2 -> class_2`
    - default:
      - `class_1`

Why it mattered:

- the ambiguity layer is now compiled into a tiny executable symbolic program
- this is closer to a usable assurance-time routing component than a quotient
  table alone

Boundary learned:

- the next frontier is the smallest semantic meaning of the three class labels
- or a richer bounded bug corpus where the class law may fail

### New survivor: anchored outlier decomposition law

Bounded result:

- bounded domain:
  - six semantic states induced by `balanced_profiles` and `support_gap`
- searched object:
  - semantic decomposition of the ambiguity layer above the
    `bundle_first = fewest_families` anchor
- strongest result:
  - exact `swap_outlier` bit:
    - first exact program:
      - `2` guards
  - exact `single_outlier` bit:
    - first exact program:
      - `2` guards
  - ambiguity layer decomposes into:
    - anchor
    - `swap_outlier`
    - `single_outlier`

Why it mattered:

- the ambiguity layer is now interpretable, not only executable
- this is closer to a real assurance-time routing contract for repair loops

Boundary learned:

- the next frontier is a smaller joint program for the full anchored
  decomposition
- or a richer bounded bug corpus where the current decomposition may fail

### New survivor: two-clause ambiguity-class law

Bounded result:

- bounded domain:
  - six class states induced by `balanced_profiles` and `support_gap`
- searched object:
  - smaller exact class-level program in a richer clause grammar
- strongest result:
  - no `0`-clause or `1`-clause program is exact
  - first exact classifier:
    - `2` ordered clauses
  - exact law:
    - `balanced_profiles and support_gap = 1 -> class_3`
    - `support_gap = 0 or unbalanced_profiles and support_gap = 2 -> class_2`
    - default:
      - `class_1`

Why it mattered:

- this is a clean software example where a better symbolic language beats a
  wider search over the old grammar
- the ambiguity layer now has a smaller exact classifier than the last
  conjunction-only program

Boundary learned:

- the next frontier is a smaller joint program for the anchor plus both
  outlier bits
- or a richer bounded bug corpus where the same two-clause law may fail

### New survivor: anchor-shape law

Bounded result:

- bounded domain:
  - six anchor states induced by `balanced_profiles` and `support_gap`
- searched object:
  - direct symbolic compiler for the stable anchor
    `bundle_first = fewest_families`
- strongest result:
  - no `0`-, `1`-, or `2`-guard program is exact
  - first exact program:
    - `3` guards
  - exact law:
    - `balanced_profiles and support_gap = 2 -> BUNDLE2+BUNDLE2+DIAGONAL+SWAP2`
    - `support_gap >= 2 -> BUNDLE2+BUNDLE2+DIAGONAL`
    - `balanced_profiles -> BUNDLE2+BUNDLE2+BUNDLE2+DIAGONAL`
    - default:
      - `BUNDLE2+DIAGONAL+SWAP2`

Why it mattered:

- the same semantic state now controls both the ambiguity layer and the anchor
  repair family
- this turns the branch into a more complete formal routing kernel for the
  bounded repair atlas

Boundary learned:

- the next frontier is the smallest exact joint program for the anchor plus
  both outlier bits
- or a richer bounded bug corpus where the anchored routing kernel may fail

### New survivor: anchored routing kernel law

Bounded result:

- bounded domain:
  - full `40`-family ambiguous slice of the software atlas
- searched object:
  - direct exact kernel:
    - `AnchorShape`
    - `SwapOutlier`
    - `SingleOutlier`
- strongest result:
  - no singleton coordinate in the searched semantic library is exact
  - the unique exact minimal basis has size `2`:
    - `balanced_profiles`
    - `support_gap`
  - no `0`-, `1`-, `2`-, `3`-, or `4`-guard joint program is exact
  - first exact joint program:
    - `5` guards

Why it mattered:

- the software branch now has one direct bounded kernel object, not only a
  stack of adjacent exact laws
- the same semantic basis now controls:
  - ambiguity signature
  - anchor shape
  - outlier bits
  - the full anchored routing kernel

Boundary learned:

- the next frontier is the exact menu law above the anchored kernel regions
- or a richer bounded bug corpus where the size-`2` basis stops being exact

### New survivor: anchored kernel menu law

Bounded result:

- bounded domain:
  - full `40`-family ambiguous slice of the software atlas
- searched object:
  - exact repair menu above the anchored routing kernel
- strongest result:
  - the size-`2` kernel basis:
    - `(balanced_profiles, support_gap)`
    - is exact for routing but not for the full menu
  - no singleton coordinate in the searched semantic library is exact
  - the first exact menu basis has size `3`
  - preferred exact refinement:
    - `(balanced_profiles, support_gap, high_overlap)`
  - the only splitting kernel state is:
    - `(True, 0)`
  - first exact direct menu program:
    - `6` guards

Why it mattered:

- this is the first clean boundary above the direct kernel
- the current software branch now separates:
  - exact normalized routing
  - exact menu reconstruction
- the extra structure needed above the kernel is only one semantic bit

Boundary learned:

- the next frontier is a menu-selector law above the exact menu states
- or a richer bounded bug corpus where the menu refinement fails

### New survivor: logic replay correction law

Bounded result:

- bounded domain:
  - full `40`-family ambiguous slice of the software atlas
- searched object:
  - actual `bundle_first` anchor and true joint kernel under logic replay
- strongest result:
  - actual `bundle_first` anchor is not definable in:
    - `(balanced_profiles, support_gap)`
  - true joint kernel is also not definable there
  - the clean split state is:
    - `(True, 0)`
  - `high_overlap := (extra_count >= 5)` is the first searched repair bit
  - both actual anchor and true kernel first become exact in:
    - `(balanced_profiles, support_gap, high_overlap)`

Why it mattered:

- this exposed a real overclaim in the earlier software kernel story
- it separated normalized quotient summaries from true definability theorems
- it gave the first honest logic boundary above the software ambiguity layer

Boundary learned:

- `Q2` survives for relations and routed ambiguity
- `Q3` is the first honest theory for actual selectors and kernels
- the next frontier is a full target-family phase diagram

### New survivor: software definability phase diagram law

Bounded result:

- bounded domain:
  - full `40`-family ambiguous slice of the software atlas
- searched object:
  - smallest exact theory for each current software target
- strongest result:
  - `Q2 = (balanced_profiles, support_gap)` exactly controls:
    - `ambiguity_class`
    - `swap_outlier`
    - `single_outlier`
    - `bundle_vs_swap`
    - `bundle_vs_single`
    - `swap_vs_fewest`
    - `single_vs_fewest`
  - `Q3 = (balanced_profiles, support_gap, high_overlap)` first controls:
    - `bundle_first`
    - `fewest_families`
    - `swap_first`
    - `single_first`
    - `true_kernel`
    - `menu`
  - no searched non-constant target currently needs a theory beyond `Q3`

Why it mattered:

- the software branch now has a clean logic hierarchy instead of one flat
  kernel story
- this is the strongest current logic-level object in the software line

Boundary learned:

- the next honest frontier is the first target that forces a theory beyond
  `Q3`
- or a canonical selector law inside the exact `Q3` menu states

### New survivor: common commitment-tier witness law

Bounded result:

- bounded domain:
  - full `40`-family ambiguous slice of the software atlas
- searched object:
  - one common `Q2` witness pair for all current `Q3` commitment targets
- strongest result:
  - the witness state is:
    - `(balanced_profiles = True, support_gap = 0)`
  - it contains:
    - `3` low-overlap families
    - `1` high-overlap family
  - every low-overlap family separates from the unique high-overlap family on:
    - `bundle_first`
    - `fewest_families`
    - `swap_first`
    - `single_first`
    - `true_kernel`
    - `menu`

Why it mattered:

- the `Q3` boundary is not six separate target-by-target accidents
- one common witness state forces the whole commitment tier
- this is the cleanest model-theoretic object in the current software branch

Boundary learned:

- the next honest frontier is the first target that truly escapes `Q3`
- or a canonical selector law inside the exact `Q3` commitment states

### New survivor: software target-algebra closure law

Bounded result:

- bounded domain:
  - full `40`-family ambiguous slice of the software atlas
- searched object:
  - closure of the current software target family under exact quotients
- strongest result:
  - relation algebra:
    - unique minimal basis:
      - `(balanced_profiles, support_gap)`
    - exact state count:
      - `6`
  - commitment algebra:
    - minimal basis size:
      - `3`
    - preferred exact basis:
      - `(balanced_profiles, support_gap, high_overlap)`
    - exact state count:
      - `7`
  - full current target algebra:
    - also minimal basis size:
      - `3`
    - same preferred basis:
      - `(balanced_profiles, support_gap, high_overlap)`
    - same exact state count:
      - `7`

Why it mattered:

- the current software branch is no longer only a collection of definability
  facts
- it now has a closed finite target algebra
- the present logic really does stop at `Q3` for the whole current family

Boundary learned:

- the next honest frontier is the first richer target family that escapes `Q3`
- or a canonical selector theorem inside the `Q3` states

### New survivor: richer selector-family closure law

Bounded result:

- bounded domain:
  - full `40`-family ambiguous slice of the software atlas
- searched object:
  - richer structural selector family built from lexicographic orders of
    length `1..3`
- strongest result:
  - raw selectors:
    - `85`
  - unique selector behaviors:
    - `10`
  - the full richer selector-family target still has:
    - minimal exact basis size `3`
    - preferred exact basis `(balanced_profiles, support_gap, high_overlap)`
    - exact state count `7`

Why it mattered:

- this shows the current software closure at `Q3` is not fragile
- even a much richer selector family still stays inside the same quotient

Boundary learned:

- the next honest frontier is a genuinely richer target family that escapes
  `Q3`
- not another selector variant from the same structural family

### New survivor: support-geometry phase diagram law

Bounded result:

- bounded domain:
  - full `40`-family ambiguous slice of the software atlas
- strongest result:
  - `support_signature` already has:
    - minimal exact basis size `3`
    - preferred exact basis `(balanced_profiles, support_gap, high_overlap)`
    - exact state count `7`
  - `oriented_support_pair` is not exact in `Q3`, but first becomes exact at:
    - basis size `2`
    - preferred basis `(extra_count, orientation)`
    - exact state count `8`
  - `raw_extra_edge_family` still escapes the full searched
    symmetric-plus-orientation library

Why it mattered:

- this is the first real logic escape beyond `Q3`
- it shows that `Q3` already captures symmetric support geometry, not only
  commitment targets
- the next missing semantic dimension is orientation

Boundary learned:

- the next frontier is the first theory that recovers raw family identity
- not another target inside the current symmetric closure

### New survivor: row-column incidence completion law

Bounded result:

- bounded domain:
  - full `40`-family ambiguous slice of the software atlas
- strongest result:
  - raw family identity first becomes exact at:
    - basis size `5`
  - no basis of size `4` or smaller is exact
  - preferred exact basis:
    - `(out_guard, out_bounds, out_transform, in_guard, in_bounds)`
  - exact state count:
    - `40`
  - minimal exact basis count:
    - `24`

Why it mattered:

- the theory above orientation is not brute-force family lookup
- raw family identity already closes in a row-column incidence language
- the software logic stack now has a real explanation tier above `Q4`

Boundary learned:

- the next frontier is a smaller semantic quotient above incidence
- or transfer of the incidence law to a richer atlas

### New survivor: incidence-signature singleton law

Bounded result:

- bounded domain:
  - full `40`-family ambiguous slice of the software atlas
- strongest result:
  - raw family identity first becomes exact at:
    - basis size `1`
  - unique exact singleton:
    - `incidence_signature = (out_profile, in_profile)`
  - exact state count:
    - `40`

Why it mattered:

- the size-`5` incidence law from v129 was only a scalar presentation
- the real logic object is one canonical incidence-signature quotient

Boundary learned:

- the next frontier is whether that singleton survives on the full atlas
- or the first transfer obstruction if it does not

### New survivor: cycle-orientation incidence extension law

Bounded result:

- bounded domain:
  - full `64`-family off-diagonal software atlas
- strongest result:
  - the singleton incidence-signature law fails on exactly one obstruction
    bucket:
    - `((1,1,1),(1,1,1))`
    - the two opposite off-diagonal `3`-cycles
  - first exact basis size:
    - `2`
  - preferred exact basis:
    - `(incidence_signature, cycle_orientation)`

Why it mattered:

- the transfer obstruction is tiny and explicit
- the next logic tier above incidence-signature is one cycle-orientation bit

Boundary learned:

- the next frontier is a richer atlas where the cycle-orientation repair fails
- or a smaller semantic account of the cycle bit

### New survivor: complement-threshold and governed-profit law

Bounded result:

- same model capability does not force equal activation or equal profit
- active threshold sets:
  - `low -> {open}`
  - `high -> {open, extractive}`
- exact platform region law:
  - `extractive_revenue >= open_revenue iff n_low <= 4 * n_high`
- `MPRD` gate result:
  - the top illicit strategy can be forbidden while a positive-profit admissible
    strategy survives

Why it mattered:

- this is the first bounded exact profit-agent object in the repo
- it moves the discussion from metaphor to a checked game
- it shows that complement scarcity and admissibility both matter immediately

Boundary learned:

- the next frontier is not more prose about platform power
- it is a two-stage game with user best responses and passive ownership

### New survivor: hold-up and passive-ownership threshold law

Bounded result:

- user best response by extraction level:
  - `open -> active`
  - `moderate -> active`
  - `high -> passive`
  - `maximal -> passive`
- best active effort:
  - `open -> e3`
  - `moderate -> e2`
  - `high -> e1`
  - `maximal -> e0`
- platform revenue:
  - `open -> 4`
  - `moderate -> 12`
  - `high -> 0`
  - `maximal -> 0`
- unique platform optimum:
  - `moderate`

Why it mattered:

- this is the first bounded formal hold-up theorem in the profit-agent branch
- it shows that full platform capture is not automatically revenue-maximizing
- it makes passive ownership a real strategic response, not only a rhetorical
  possibility

Boundary learned:

- the next frontier is heterogeneous complements plus passive ownership
- or demand closure, who buys output if platform capture rises and active user
  income falls

### New survivor: heterogeneous-complement passive-ownership region law

Bounded result:

- `open` keeps both complement classes active
- `moderate` keeps only high-complement users active
- `high` and `maximal` are dominated because both classes switch to passive
  ownership there
- exact region law:
  - `moderate_revenue >= open_revenue iff 2 * n_low <= 9 * n_high`

Why it mattered:

- this is the first checked phase boundary for post-AGI platform economics in
  the repo
- it shows that complement mix, not only intelligence, controls the platform's
  optimal regime
- passive ownership changes the equilibrium qualitatively rather than only by a
  small payoff perturbation

Boundary learned:

- the next frontier is demand closure or a richer ownership game
- not more informal argument about whether equal intelligence kills profit

### New survivor: demand-closure ownership law

Bounded and checked result:

- in the one-unit household demand model:
  - `S = (m + 1) * n`
  - `D = n + b`
- exact theorem:
  - `D >= S iff b >= m * n`

Why it mattered:

- this is the first generic arithmetic theorem in the post-AGI economics line
- it makes the macro question precise:
  concentrated claims fail once extra output outgrows owner self-consumption
- broad passive claims or transfers become mathematically necessary in this
  model

Boundary learned:

- the next frontier is richer demand functions or integration back into the
  platform game
- not more verbal argument about who buys output

### New survivor: private-optimum versus closure phase diagram

Bounded and checked result:

- in the integrated platform-plus-demand toy economy:
  - `open` clears iff `n_high = 0`
  - `moderate` clears iff `n_high <= n_low`
  - `moderate` is privately optimal iff `2 * n_low <= 9 * n_high`
- therefore, for `n_high > 0`:
  - a privately optimal and demand-clearing regime exists iff
    `n_high <= n_low and 2 * n_low <= 9 * n_high`
  - when it exists, it is `moderate`

Why it mattered:

- this is the first integrated micro-plus-macro phase diagram in the
  profit-agent branch
- it proves that platform-private optimality and demand closure can diverge
- it gives an exact band where the private optimum is also socially viable

Boundary learned:

- the next frontier is richer demand or ownership structure
- not more informal argument about whether platform incentives alone stabilize
  the economy

### New survivor: active-owner share ceiling

Bounded and checked result:

- with `h` total households and `n` active owner households producing `2`
  units each:
  - closure holds iff `h >= 2 * n`
  - equivalently, `n <= h / 2`
- for any positive-household economy:
  - not `h >= 2 * h`

Why it mattered:

- this is the first exact theorem in the profit-agent branch that directly
  answers the universal-principal question
- it shows that once active-owner output exceeds one unit, universal active
  ownership fails under the one-unit demand cap
- it reframes the design problem around active versus passive roles, not only
  around intelligence levels

Boundary learned:

- the next frontier is richer demand or endogenous active/passive choice
- not more informal argument about whether everyone simply becomes an
  entrepreneur

### New survivor: symmetric coordination law

Bounded and checked result:

- with identical households in the double-output model:
  - strict active preference implies `n = h`
  - strict passive preference implies `n = 0`
  - indifference leaves `n` free
- closure then implies:
  - strict active preference gives no positive-household clearing equilibrium
  - strict passive preference gives only the zero-production equilibrium
  - nontrivial clearing appears only in the indifference case, with
    `n <= h / 2`

Why it mattered:

- this is the first actual coordination theorem in the profit-agent branch
- it shows that equal incentives can be the problem, not the solution
- a stable nontrivial regime requires either coordination, differentiated
  complements, or explicit rationing

Boundary learned:

- the next frontier is differentiated households or explicit coordination
  mechanisms
- not more informal talk about universal profit agents without role selection

### New survivor: uniform-price impossibility and quota implementability

Bounded and checked result:

- in the symmetric double-output model:
  - `0 < n < h and individual stability imply delta = 0`
  - so uniform pricing alone cannot implement a positive interior individually
    stable regime unless it creates exact indifference
- with a hard quota `q` under strict active preference:
  - `n = min(h, q)`
  - closure holds iff `h >= 2 * q`, equivalently `q <= h / 2`

Why it mattered:

- this is the first mechanism-design theorem in the profit-agent branch
- it separates price coordination from slot allocation
- it shows that a real allocation device can implement the interior regime
  that prices alone fail to select

Boundary learned:

- the next frontier is differentiated agents or richer allocation mechanisms
- not more informal talk about prices solving coordination by themselves

### New survivor: heterogeneous price-selection law

Bounded and checked result:

- in the two-type double-output model:
  - `a_low < p < a_high -> n_low = 0 and n_high = H`
  - the high-only regime clears iff `L + H >= 2 * H`, equivalently `H <= L`

Why it mattered:

- this is the first exact result showing that heterogeneous complements rescue
  uniform pricing
- one price can now implement a nontrivial interior regime
- but only if the selected high-complement group is not a majority

Boundary learned:

- the next frontier is mechanism composition or richer permit systems
- not more homogeneous analysis once complement heterogeneity is present

### New survivor: price-plus-quota composition law

Bounded and checked result:

- in the same two-type model:
  - price selects the high type
  - a hard quota `q` selects the active count
  - closure holds iff `L + H >= 2 * q`, equivalently `q <= (L + H) / 2`

Why it mattered:

- this is the first mechanism-composition theorem in the branch
- it separates selection from allocation cleanly
- it shows that price alone and quota alone are not the final objects, the
  deeper object is the composed mechanism

Boundary learned:

- the next frontier is lotteries, permits, or endogenous quota choice
- not more one-stage mechanism analysis

### New survivor: intermediate-demand multiplier law

Bounded and checked result:

- in the scalar software-only multiplier model:
  - `Y = alpha * Y + F`
  - `alpha = a / b`
  - `F = H + A_term + C + X`
- exact laws:
  - `a < b and F = 0 imply Y = 0`
  - `a < b and F > 0 imply Y > 0`

Why it mattered:

- this is the first theorem in the economics branch that explicitly separates
  intermediate agent demand from final sinks
- it corrects the earlier opening by showing that human attention is not the
  only possible sink
- but it keeps the real conservation law: circular intermediate trade alone
  does not sustain output

Boundary learned:

- the next frontier is a small network model of sinks and intermediate flows
- not more talk as if all demand had to be human, or as if all agent trade were
  automatically final demand

### New survivor: zero-employee company entry ceiling law

Bounded and checked result:

- in the symmetric zero-employee software-firm branch:
  - legal shell creation is nonbinding
  - final sink bundle remains `F = H + A_term + C + X`
  - total profit is `Pi_total = F - N * c`
- exact laws:
  - `Pi_total >= 0 iff F >= N * c`
  - `Pi_total > 0 iff F > N * c`

Why it mattered:

- this is the first direct theorem about zero-employee firm count rather than
  only about sinks or coordination
- it shows that even if agents can create whole firms with no human employees,
  sustainable firm count is still capped by sink size and operating cost
- it turns the thought experiment into a real economic ceiling law

Boundary learned:

- the next frontier is discovery bottlenecks, slot rents, and asymmetric access
- not more prose that treats firm creation itself as the scarce step

### New survivor: discovery-slot redistribution law

Bounded and checked result:

- in the zero-employee-firm branch with fixed sink bundle:
  - `Pi_total = F - N * c`
  - this total is independent of slot count `q`
  - slot-holder margin numerator is `M_slot = F - q * c`
- exact laws:
  - `M_slot > 0 iff F > q * c`
  - `Pi_undiscovered = -c`

Why it mattered:

- this is the first clean theorem about discovery power in the branch
- it shows that a platform or protocol bottleneck can change who captures the
  gains without changing total surplus
- it turns "platform eats the economy" into an exact routing and slot-rent
  question

Boundary learned:

- the next frontier is asymmetric routing, auctions, or governed slot
  allocation
- not more talk as if bottlenecks automatically create new value

### New survivor: incumbent-rent machine lockout law

Bounded and checked result:

- in the two-period machine-adoption branch:
  - social machine-path premium is `2 * A - 2 * tau1 + lam`
  - private incumbent-controller machine premium is
    `2 * A - 2 * tau1 + lam - 2 * rho`
- exact laws:
  - social machine path beats always-human iff `2 * A + lam >= 2 * tau1`
  - incumbent privately adopts machine iff
    `2 * A + lam >= 2 * tau1 + 2 * rho`
  - therefore the exact lockout wedge is:
    - `2 * A + lam >= 2 * tau1`
    - `2 * A + lam < 2 * tau1 + 2 * rho`

Why it mattered:

- this is the first exact theorem in the economics branch that combines
  reliability advantage, trust learning, incumbent rents, and lock-in
- it shows that better machines can still be blocked even after the trust
  branch becomes dynamically favorable
- it turns the adoption problem into a concrete institutional wedge, not only a
  psychology-of-trust story

Boundary learned:

- the next frontier is explicit assurance design or compensation mechanisms
- or richer repeated games where routing, deployment, and trust update together

### New survivor: assurance-package adoption law

Bounded and checked result:

- in the same two-period machine-adoption branch with package levers:
  - packaged private machine premium is
    `2 * A - 2 * tau1 + lam + 2 * d + g - 2 * rho - k`
- exact laws:
  - packaged private adoption iff
    `2 * A + lam + 2 * d + g >= 2 * tau1 + 2 * rho + k`
  - if baseline adoption is blocked, the package flips rejection into adoption
    iff
    `2 * d + g - k >= (2 * tau1 + 2 * rho) - (2 * A + lam)`

Why it mattered:

- this is the first exact software-design theorem in the economics branch
- it says audit lift, learning lift, and package cost are not interchangeable
- it turns the trust discussion into a real design inequality rather than a
  loose recommendation to "build trust"

Boundary learned:

- the next frontier is package composition, liability shifts, or social versus
  private package choice
- or richer repeated games where the package changes routing or deployment too

### New survivor: assurance-lever coefficient law

Bounded and checked result:

- with package levers `d`, `g`, and `ell` and linear cost
  `k = c_d * d + c_g * g + c_ell * ell`:
  - private adoption holds iff
    `2 * A + lam + (2 - c_d) * d + (1 - c_g) * g + (2 - c_ell) * ell >= 2 * tau1 + 2 * rho`
- equal-cost corollary:
  - if `c_d = c_g = c_ell = 1`, then
    `2 * A + lam + d + ell >= 2 * tau1 + 2 * rho`
  - so `g` drops out of the private adoption region

Why it mattered:

- this is the first exact coefficient theorem for distinct assurance levers in
  the economics branch
- it shows that predeployment trust lift and liability offset buy more private
  adoption than delayed learning when costs are comparable
- it sharpens the software-design question from "add trust" to "which trust
  levers actually move adoption"

Boundary learned:

- the next frontier is endogenous package choice, subsidy, or regulation
- or repeated games where assurance affects routing and deployment, not only
  trust

### New survivor: assurance-subsidy implementation law

Bounded and checked result:

- in the two-period assurance branch:
  - social package choice holds iff
    `2 * A + lam + 2 * d + g >= 2 * tau1 + k`
  - private package adoption holds iff
    `2 * A + lam + 2 * d + g >= 2 * tau1 + 2 * rho + k`
  - minimal implementing subsidy is
    `max(0, 2 * tau1 + 2 * rho + k - (2 * A + lam + 2 * d + g))`
- strict divergence wedge:
  - the package is socially preferred but privately rejected
  - and the exact bridge satisfies `0 < s_star <= 2 * rho`

Why it mattered:

- this is the first exact theorem about who pays for assurance in the economics
  branch
- it shows that once a package is socially worthwhile, the remaining problem is
  a bounded rent wedge, not an undefined trust fog
- it turns subsidy or mandate talk into a precise implementation quantity

Boundary learned:

- the next frontier is endogenous sponsorship and bargaining over that bridge
- or repeated games where assurance interacts with routing and deployment

### New survivor: requirements recoverability law

Bounded and checked result:

- witness-space model:
  - requirement universe:
    - `R`
  - witness library:
    - `W`
  - missing set:
    - `M`
  - admissible signatures:
    - `A_W(M) = {S in W | S ⊆ M}`
- exact local laws:
  - pure singleton-driven recovery succeeds iff:
    - `∀r in M, {r} in W`
  - oracle-assisted recovery succeeds iff:
    - `⋃ A_W(M) = M`
- exhaustive bounded check:
  - `|R| = 3`
  - all `128` witness libraries
  - all `7` nonempty missing sets
- key counts:
  - global all-missing-set recoverability:
    - pure:
      - `16`
    - oracle-assisted:
      - `16`
  - scoped pair-lobotomy recoverability:
    - pure:
      - `16`
    - oracle-assisted:
      - `36`
    - strict oracle-only advantage:
      - `20`

Why it mattered:

- this is the first exact requirements-discovery object in the current repo
  line
- it shows that recoverability is controlled by witness geometry and omission
  scope, not by vague prompt quality alone
- it gives a clean algebraic role to the stakeholder oracle:
  - not magic recovery
  - exact disambiguation over the exposed witness cover

Boundary learned:

- if singleton omissions remain in scope, oracle help does not remove the need
  for singleton witnesses
- stakeholder assistance becomes strictly stronger only once the omission family
  is scoped, for example by pair-lobotomy
- the next frontier is not another generic CEGIS loop, it is the ambiguity
  quotient and minimal question policy above this witness-space law

### New survivor: observation-quotient loop law

Bounded and checked result:

- observation geometry:
  - requirement universe:
    - `R`
  - witness library:
    - `W`
  - omission family:
    - `F`
  - observation map:
    - `O_W(M) = A_W(M) = {S in W | S ⊆ M}`
- exact loop laws:
  - pure structured recovery succeeds iff:
    - `O_W` is injective on `F`
  - minimal worst-case post-observation question budget is:
    - `max_C depth*(C)` over the ambiguity classes of `~_W,F`
- exhaustive `|R| = 4` check over all `32768` witness libraries:
  - pair-lobotomy family:
    - atomic singleton rule recoverable libraries:
      - `2048`
    - structured observation-quotient recoverable libraries:
      - `19424`
    - strict structured advantage:
      - `17376`
  - all-nonempty family:
    - atomic singleton rule recoverable libraries:
      - `2048`
    - structured observation-quotient recoverable libraries:
      - `3072`
- pair-only witness library:
  - recovers every missing pair with:
    - zero extra questions
  - but on the unrestricted family:
    - singleton omissions collapse to one ambiguity class
    - exact worst-case question budget is `3`

Why it mattered:

- this is the first exact loop-state geometry result in the requirements
  discovery branch
- it shows that the right loop object is not "counterexample plus optional
  oracle"
- it is:
  - an observation map
  - an ambiguity quotient
  - and a minimal separating question policy

Boundary learned:

- atomic witness recovery is a real lower rung, not the full loop
- pair witnesses can already be enough if the loop stores the full observation
  family
- the next frontier is exact question-policy synthesis and richer query
  languages

### New survivor: staged temporal label-function law

Bounded and checked result:

- temporal label pair:
  - flat two-step trace label:
    - `L_trace`
  - symbolic monitor-cell label:
    - `L_cell`
- exhaustive bounded family:
  - `5832` temporal controllers
  - `144` flat two-step traces
  - `36` monitor cells
- full family:
  - trace behavior classes:
    - `73`
  - monitor-cell behavior classes:
    - `168`
  - exact partition match:
    - `false`
  - monitor-cell labels strictly refine trace labels:
    - `true`
- staged slice after first-step carving:
  - surviving candidates:
    - `108`
  - residual trace classes:
    - `12`
  - residual monitor-cell classes:
    - `12`
  - exact partition match:
    - `true`

Why it mattered:

- this is the first exact temporal label-space result in the current loop-space
  line
- it shows that a richer symbolic label basis can be exact only after the loop
  has already carved away early bad states
- it adds a new loop-space move:
  - staged basis change in label space

Boundary learned:

- temporal labels are not automatically the right global state basis
- they can become exact later in the loop, after concrete carving
- the next frontier is to characterize when basis changes should fire and how
  they interact with observation quotients

### New survivor: uniform witness ladder law

Bounded and checked result:

- requirement universe:
  - `|R| = n`
- uniform witness library:
  - `W_k = {S ⊆ R | |S| = k}`
- observation map:
  - `O_k(M) = {S in W_k | S ⊆ M}`
- exhaustive checks:
  - all `2 <= n <= 6`
  - all `1 <= k <= n`
  - all nonempty omission sets
- exact laws:
  - lower rung collapse:
    - `O_k(M) = ∅` iff `|M| < k`
  - upper rung exactness:
    - if `|M| >= k` and `|M'| >= k` and `O_k(M) = O_k(M')`, then `M = M'`
  - pair-witness singleton budget:
    - exact worst-case requirement-membership budget:
      - `n - 1`

Why it mattered:

- this is the first exact witness-arity ladder in the current loop-space line
- it turns witness language design into an exact geometric control knob
- it shows that higher-arity witnesses raise an observability threshold instead
  of merely adding noisy evidence

Boundary learned:

- high witness arity does not rescue omission layers below the threshold
- those lower layers still need either questions or a different witness basis
- the next frontier is the exact question-budget geometry on the collapsed
  lower rung

### New survivor: lower-rung membership budget law

Bounded and checked result:

- same uniform witness library:
  - `W_k = {S ⊆ R | |S| = k}`
- collapsed lower rung:
  - `L_{n,k} = {M ⊆ R | 1 <= |M| < k}`
- follow-up query language:
  - requirement-membership only
- brute-force decision-tree checks:
  - all `2 <= n <= 7`
  - all `2 <= k <= n`
- compressed dynamic-program checks:
  - all `2 <= n <= 12`
  - all `2 <= k <= n`
- exact budget law:
  - `budget_mem(n, 2) = n - 1`
  - `budget_mem(n, k) = n` for `3 <= k <= n`
- exact consequence:
  - pair witnesses are query-optimal among all non-singleton uniform witness
    generators under membership-only follow-up

Why it mattered:

- this is the first exact tradeoff law between witness language and follow-up
  query language in the current loop-space line
- it shows that "more witness arity" is not a monotone improvement once the
  lower rung must be finished by questions
- it upgrades the geometry story from a simple threshold ladder to a real
  design surface

Boundary learned:

- higher-arity uniform witnesses help on the upper rung, but can worsen the
  lower-rung completion cost
- pair witnesses are special, not because they observe everything, but because
  they leave the cheapest ambiguous remainder under membership queries
- the next frontier is richer follow-up query languages and mixed-arity witness
  families

### New survivor: pair-basis sufficiency law

Bounded and checked result:

- mixed witness library:
  - `W_A = {S ⊆ R | |S| ∈ A}`
- scanned arity sets:
  - every `A ⊆ {2, ..., n}` with `2 ∈ A`
- omission family:
  - all nonempty omission sets
- follow-up query language:
  - requirement-membership only
- exhaustive checks:
  - all `2 <= n <= 7`
  - all mixed arity sets containing `2`
- exact laws:
  - ambiguity partition:
    - `partition(W_A, F_all) = partition(W_{ {2} }, F_all)`
  - worst-case budget:
    - `budget_mem(W_A, F_all) = n - 1`

Why it mattered:

- this is the first exact basis-sufficiency result in the current loop-space
  line
- it shows that pair witnesses are not only locally good, they are a complete
  bounded basis for this recovery-plus-query regime
- it sharply narrows the meaningful tool-combination search:
  - if pairs are present, stacking more uniform higher-arity generators is not
    the next move

Boundary learned:

- the next useful search axis is richer separator questions
- or non-uniform witness families, not more uniform higher-arity layers above
  the pair basis
- this makes the loop-space geometry more concrete:
  - some regions collapse to the same effective basis

### New survivor: separator expressivity law above the pair basis

Bounded and checked result:

- pair witness basis:
  - `W_2 = {S ⊆ R | |S| = 2}`
- residual ambiguity class:
  - all singleton omissions
- compared separator languages:
  - pair-subset queries
  - singleton-membership queries
  - block-intersection queries
- brute-force decision-tree checks:
  - all `2 <= n <= 8`
- exact ladder:
  - pair-subset:
    - unrecoverable
  - singleton-membership:
    - `n - 1`
  - block-intersection:
    - `ceil(log2 n)`

Why it mattered:

- this is the first exact cross-axis expressivity ladder in the current
  loop-space line
- it shows that after the right witness basis lands, the next gains come from
  separator language, not more of the same witness machinery
- it gives a concrete compression jump:
  - linear residual completion
  - down to logarithmic residual completion

Boundary learned:

- richer syntax alone is not enough:
  - pair-subset queries still fail completely on the singleton residue
- the query language has to align with the geometry of the remaining ambiguity
- the next frontier is richer separator families and non-uniform witness bases

### New survivor: singleton witness substitution law

Bounded and checked result:

- singleton witness basis:
  - `W_T = {{r} | r ∈ T}`
- omission family:
  - all nonempty omission sets
- follow-up query language:
  - requirement-membership only
- brute-force decision-tree checks:
  - all `2 <= n <= 8`
  - all singleton witness counts `0 <= |T| <= n`
- exact law:
  - `budget_mem(W_T, F_all) = n - |T|`

Why it mattered:

- this is the first exact witness-query substitution law in the current
  loop-space line
- it shows that atomic witnesses and atomic questioning live on one linear
  tradeoff axis
- it clarifies the later pair-basis results:
  - pair witnesses are not just prepaid questions
  - they reshape the ambiguity geometry itself

Boundary learned:

- without a geometry-changing witness basis, even richer block queries do not
  beat the raw `n`-bit identification burden on the full omission family
- the logarithmic block-query gain only appears after the pair basis has
  already compressed the residual class to singletons
- the next frontier is now clearly mixed witness and separator designs

### New survivor: geometry prerequisite law for block separators

Bounded and checked result:

- query language:
  - block-intersection queries
- compared families:
  - raw nonempty omission family
  - singleton residue after pair-basis observation
- brute-force checks:
  - raw family:
    - all `2 <= n <= 5`
    - exact budget:
      - `n`
  - singleton residue:
    - all `2 <= n <= 8`
    - exact budget:
      - `ceil(log2 n)`

Why it mattered:

- this is the cleanest current cross-stage law in the loop-space branch
- it shows that separator language alone is not the source of the logarithmic
  gain
- the gain comes from a hybrid loop:
  - first change the geometry of ambiguity
  - then apply an expressive residual controller

Boundary learned:

- direct separator upgrades without a geometry-changing witness stage can still
  be stuck at linear identification cost
- this strengthens the case that some hybrid quotient-question loops are better
  candidates than plain verifier-compilation on requirements-style tasks

### New survivor: atomic geometry invariance law

Bounded and checked result:

- singleton witness basis:
  - `W_T = {{r} | r ∈ T}`
- omission family:
  - all nonempty omission sets
- compared follow-up languages:
  - singleton-membership
  - block-intersection
- brute-force checks:
  - all `2 <= n <= 5`
  - all singleton witness counts `0 <= |T| <= n`
- exact law:
  - `budget_atom(W_T, F_all) = budget_block(W_T, F_all) = n - |T|`

Why it mattered:

- this closes off a large false frontier
- richer questioning alone does not beat the atomic witness axis
- the first real nonlinear gain comes only when the witness basis changes the
  ambiguity geometry, as the pair basis does

Boundary learned:

- do not keep searching for better loops inside:
  - singleton witnesses
  - plus fancier separators
- move the search to non-uniform geometry-changing witness families and hybrid
  residual controllers

### New survivor: complement witness pure-mass law

Bounded and checked result:

- partition:
  - `R = T ⊔ U`
- mixed witness library:
  - `W_{T,U} = {{t} | t ∈ T} ∪ {U}`
- branch condition:
  - `|U| >= 2`
- brute-force checks:
  - all `3 <= n <= 5`
  - all splits with `|U| >= 2`
- exact laws:
  - `pure_classes(W_{T,U}) = 2^|T|`
  - `budget_block(W_{T,U}, F_all) = |U|`

Why it mattered:

- this is the first exact non-uniform geometry-changing law in the current
  loop-space line
- it shows that one higher-arity complement witness can buy an exponential pure
  mass gain at fixed worst-case residual depth
- it gives the missing ranking dimension:
  - loops can differ not only by worst-case budget
  - but by how much of the space they resolve immediately

Boundary learned:

- budget alone is an incomplete objective for loop search
- the promising next frontier is sparse non-uniform pair-like witnesses with
  better pure-mass versus residual-depth tradeoffs

### New survivor: star-pair pure-mass law

Bounded and checked result:

- star-pair basis:
  - `W_star(a) = {{a, u} | u ∈ U}`
- anchored star basis:
  - `W_anchor_star(a) = {{a}} ∪ W_star(a)`
- omission family:
  - all nonempty omission sets
- residual questioning:
  - block-intersection
- checks:
  - pure-class counts:
    - all `3 <= n <= 8`
  - budget proof:
    - all `2 <= |U| <= 7`
    - lower bound from family size
    - upper bound from singleton-block queries
- exact laws:
  - `pure_classes(W_star) = 2^(n-1) - 1`
  - `pure_classes(W_anchor_star) = 2^(n-1)`
  - `budget_block(W_star, F_all) = n - 1`
  - `budget_block(W_anchor_star, F_all) = n - 1`

Why it mattered:

- this is the first exact sparse pair-like law that matches the atomic
  `n - 1` residual depth while buying exponential pure resolved mass
- it shows that anchored pair families are real loop candidates, not just
  presentation variants of atomic questioning

Boundary learned:

- sparse pair families can improve pure resolved mass without changing the
  worst-case residual depth
- the next search should look for wider pair geometries, not only isolated
  star constructions

### New survivor: biclique pure-mass and residual-family law

Bounded and checked result:

- partition:
  - `R = A ⊔ B`
- witness basis:
  - `W_biclique(A, B) = {{a, b} | a ∈ A, b ∈ B}`
- omission family:
  - all nonempty omission sets
- checks:
  - all `1 <= |A| <= |B| <= 5`
- exact laws:
  - `pure_classes(W_biclique) = (2^|A| - 1)(2^|B| - 1)`
  - `Residual(W_biclique) = P_+(A) ∪ P_+(B)`

Why it mattered:

- this turns the star law into one edge of a broader biclique ladder
- balanced bicliques buy much larger pure resolved mass at still sparse pair
  counts
- the residual class has a clean union-of-sides structure, which is the right
  target for the next residual-controller law

Boundary learned:

- pair-like loop search should move from isolated examples to graph-shaped
  witness families
- the next honest frontier is the residual-controller cost on the biclique
  side-only family

### New survivor: biclique residual-controller law

Bounded and checked result:

- residual family:
  - `P_+(A) ∪ P_+(B)`
- query language:
  - block-intersection
- coordinate order:
  - `a = |A| <= b = |B|`
- checks:
  - brute force:
    - all `1 <= a <= b <= 3`
  - exact proof-bounds:
    - all `1 <= a <= b <= 8`
- exact law:
  - `budget_block(P_+(A) ∪ P_+(B)) = ceil(log2((2^a - 1) + (2^b - 1)))`
  - equivalently:
    - `b` if `a = 1`
    - `b + 1` if `a >= 2`

Why it mattered:

- this closes the next rung after the biclique pure-mass law
- bicliques now come with both:
  - exact pure resolved mass
  - exact residual-controller depth
- that makes them a real loop family rather than a witness-family curiosity

Boundary learned:

- the side-only residual class is not an obstacle to exact analysis
- the next serious question is which biclique split is actually best

### New survivor: biclique balance extremal law

Bounded and checked result:

- fixed total size:
  - `n = a + b`
- biclique ladder:
  - `W_biclique(A, B)` with `a <= b`
- checks:
  - all `2 <= n <= 20`
- exact monotonicity:
  - `pure_classes(a, n-a)` increases strictly toward balance
  - `budget(a, n-a)` decreases weakly toward balance

Why it mattered:

- this is the first clean geometry design rule in the sparse pair branch
- stars are now understood as one extremal edge, not as the default sparse
  pair object
- balanced bicliques emerge as the strongest edge on:
  - pure resolved mass
  - residual-controller depth

Boundary learned:

- within the biclique family, move toward balance if extra witness edges are
  affordable
- the next honest frontier is a direct comparison between balanced bicliques
  and the pair-basis plus block-separator hybrid

### New survivor: balanced biclique versus pair-basis tradeoff law

Bounded and checked result:

- compare:
  - pair-basis hybrid
  - balanced biclique loop
- checks:
  - all `2 <= n <= 32`
- exact formulas:
  - pair basis:
    - `w_pair = n(n - 1)/2`
    - `pure_pair = 2^n - n - 1`
    - `depth_pair = ceil(log2 n)`
  - balanced biclique:
    - even `n = 2m`:
      - `w_bal = n^2/4`
      - `pure_bal = 2^n - 2^(n/2 + 1) + 1`
      - `depth_bal = n/2 + 1`
    - odd `n = 2m + 1`:
      - `w_bal = m(m + 1)`
      - `pure_bal = 2^n - 3*2^m + 1`
      - `depth_bal = m + 2`

Why it mattered:

- this is the first exact sparse-versus-dense tradeoff law inside the pair
  branch
- balanced bicliques emerge as the leading sparse exact alternative to the full
  pair basis

Boundary learned:

- balanced bicliques win on witness count
- pair basis wins on residual-controller depth
- future search should look for graph families that move this frontier

### New survivor: complete multipartite pure-mass law

Bounded and checked result:

- partition:
  - `R = P_1 ⊔ ... ⊔ P_t`
- witness basis:
  - all cross-block pairs
- checks:
  - all integer partitions of `2 <= n <= 8`
- exact laws:
  - `pure_classes = 2^n - 1 - sum_i(2^|P_i| - 1)`
  - `Residual = union_i P_+(P_i)`

Why it mattered:

- this unifies bicliques, balanced bicliques, and the full pair basis inside
  one exact graph-shaped family
- the pair branch now has a real algebra, not just named examples

Boundary learned:

- the next search should work inside the complete multipartite family before
  jumping to arbitrary graphs

### New survivor: balanced multipartite extremal law

Bounded and checked result:

- fix:
  - total size `n`
  - block count `t`
- compare:
  - all `t`-block integer partitions of `n`
- checks:
  - all `2 <= n <= 16`
  - all `1 <= t <= n`
- exact extremal rule:
  - balanced partitions maximize pure resolved mass
  - balanced partitions minimize residual-family size
  - balanced partitions maximize witness count

Why it mattered:

- this turns the multipartite family into a navigable design space
- balanced bicliques become one edge of a wider balanced multipartite program

Boundary learned:

- if staying inside complete multipartite pair witnesses, move toward balance
  first
- then adjust block count

### New survivor: balanced multipartite ladder law

Bounded and checked result:

- fix `n`
- for each `t`, take the balanced `t`-block multipartite partition
- checks:
  - all `2 <= n <= 32`
  - all `1 <= t <= n`
- exact monotonicity:
  - pure resolved mass increases with `t`
  - residual-family size decreases with `t`
  - witness count increases with `t`

Why it mattered:

- balanced bicliques and the full pair basis are now unified by one monotone
  ladder
- the sparse-versus-dense pair frontier is no longer just a biclique-versus
  pair comparison

Boundary learned:

- the next exact frontier is the residual-controller law for general balanced
  multipartite residual families
- after that, the honest comparison is balanced multipartite loops versus
  verifier-compilation style loops

### New survivor: balanced multipartite residual-controller law

Bounded and checked result:

- family:
  - balanced multipartite residual families
- query language:
  - block-intersection
- brute-force grid:
  - `2 <= n <= 7`
  - `2 <= t <= n`
- exact bounded law:
  - `budget_block(Residual_bal(n, t)) = ceil(log2 |Residual_bal(n, t)|)`

Why it mattered:

- this closes the controller rung for the balanced multipartite ladder on the
  first honest grid
- the middle multipartite rungs are now exact on both:
  - witness geometry
  - residual-controller cost

Boundary learned:

- the strongest remaining gap is no longer small-grid exactness
- it is either:
  - a general proof of the balanced residual-controller law
  - or a direct cross-family comparison against verifier-compilation style
    loops

### New survivor: balanced multipartite direct formula law

Bounded and checked result:

- balanced partition coordinates:
  - `n = t*q + r`
  - `q = floor(n / t)`
  - `r = n mod t`
- checks:
  - all `2 <= n <= 128`
  - all `1 <= t <= n`
- exact direct formulas:
  - `residual_size(n, t) = (t + r) * 2^q - t`
  - `pure_classes(n, t) = 2^n - (t + r) * 2^q + t - 1`
  - `witness_count(n, t) = n(n - 1)/2 - t*q*(q - 1)/2 - r*q`
- claim tier:
  - `direct_amount_compiler`

Why it mattered:

- this is the first direct-amount compiler on the loop-space geometry branch
- the balanced multipartite ladder is no longer just a descriptive family, it
  is directly computable from `(n, t)`

Boundary learned:

- the next serious gap is now the residual-controller side, not the witness
  geometry side
- the next honest comparison is balanced multipartite direct geometry versus
  verifier-compilation style loops

### New survivor: internal-clique pair witness law

Bounded and checked result:

- partition:
  - `R = C_1 ⊔ ... ⊔ C_t`
- witness basis:
  - all same-cluster pairs
- checks:
  - all integer partitions of `2 <= n <= 16`
- exact laws:
  - `Residual = {M != ∅ | |M ∩ C_i| <= 1 for every i}`
  - `residual_size = Π_i (1 + s_i) - 1`
  - `pure_classes = 2^n - Π_i (1 + s_i)`
  - `witness_count = Σ_i s_i(s_i - 1)/2`
- claim tier:
  - `direct_amount_compiler`

Why it mattered:

- this is a second exact graph-shaped pair loop family
- the pair-witness branch is no longer only a cross-block story

Boundary learned:

- balanced multipartite is one exact side of the pair-witness space
- internal-clique loops are another
- the next honest move is an exhaustive small-graph frontier check

### New survivor: pair-witness pure frontier correction law

Bounded and checked result:

- exhaustive simple graphs:
  - `2 <= n <= 7`
- comparison frontiers:
  - graph optimum
  - balanced multipartite
  - internal-clique cluster
- first strict balanced gap:
  - `(n, m) = (5, 6)`
  - `OPT_pure = 22`
  - `BAL_pure = 21`
- max checked balanced gap:
  - `(n, m) = (7, 12)`
  - `OPT_pure = 111`
  - `BAL_pure = 105`
  - gap `6`
- cluster exact-hit counts by `n`:
  - `2/2`, `3/3`, `5/5`, `6/7`, `9/9`, `10/13`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this is the first bounded proof that the balanced multipartite ladder is not
  the full pair-witness pure frontier
- internal-clique loops explain many optimum budgets, but strict gaps remain

Boundary learned:

- the next search should target the remaining optimal graph families outside
  both:
  - balanced multipartite
  - internal-clique cluster

### New survivor: cograph pair frontier law

Bounded and checked result:

- family:
  - labeled cograph pair witness bases
- comparison oracle:
  - exact global frontier from `v181`
- exact hit pattern:
  - full frontier hit for:
    - `2 <= n <= 4`
  - exactly one missed budget for each of:
    - `n = 5`
    - `n = 6`
    - `n = 7`
- exact misses:
  - `(5, 5) -> 21 versus 20`
  - `(6, 8) -> 50 versus 48`
  - `(7, 10) -> 109 versus 107`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this is the first strong recursive pair-loop family on the branch
- it strictly generalizes:
  - internal-clique loops
  - complete multipartite loops

Boundary learned:

- cographs are almost the right closure, but not the final one
- the remaining gap is small enough to search structurally

### New survivor: clique-bridge optimum law

Bounded and checked result:

- family:
  - `B(a, b)`, two cliques plus one bridge edge
- exact direct formulas:
  - `witness_count = C(a, 2) + C(b, 2) + 1`
  - `residual_size = (a + b) + ab - 1`
  - `pure_classes = 2^(a + b) - (a + b) - ab`
- exact bounded optimum law:
  - for every `a, b >= 1` with `a + b <= 7`,
    `B(a, b)` attains the exact global optimum at its own witness budget
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this is the first exact non-cograph repair above the recursive union-and-join
  family
- it cleanly explains the missed cograph budgets

Boundary learned:

- the live search is no longer for arbitrary graph masks
- the next plausible family is:
  - tree-of-cliques
  - or block-graph ladders

### New survivor: two-family frontier cover law

Bounded and checked result:

- shared checked domain:
  - `2 <= n <= 7`
- families:
  - cographs
  - clique bridges
- total exact frontier budgets:
  - `62`
- covered by the two-family union:
  - `62`
- bridge-only repairs are exactly:
  - `(5, 5)` with:
    - `21 versus 20`
  - `(6, 8)` with:
    - `50 versus 48`
  - `(7, 10)` with:
    - `109 versus 107`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this is the first compact frontier map for the strongest current
  pair-witness loops
- it turns the baseline from:
  - arbitrary small-graph search
  into:
  - two structured loop families

Boundary learned:

- any new family should now be compared against this two-family cover, not
  against the full graph space directly
- the next honest search target is the smallest recursive closure containing
  both:
  - cographs
  - clique bridges

### New survivor: bridge-cograph frontier law

Bounded and checked result:

- family:
  - bridge-cographs, generated from singletons by:
    - disjoint union
    - complete join
    - single-edge join
- shared checked domain:
  - `2 <= n <= 7`
- exact hit pattern:
  - full frontier hit on every checked `n`
- labeled family counts:
  - `2, 8, 64, 952, 22304, 716186`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this is the first single recursive family that covers the full checked
  pair-witness frontier
- it unifies the earlier survivors:
  - cographs
  - clique bridges

Boundary learned:

- the next honest move is no longer a broader graph-family search
- it is a compression search inside the bridge-cograph closure itself

### New survivor: twin-pendant frontier law

Bounded and checked result:

- family:
  - one-vertex growth by:
    - pendant
    - false twin
    - true twin
- shared checked domain:
  - `2 <= n <= 7`
- exact hit pattern:
  - full frontier hit on every checked `n`
- family counts:
  - `2, 6, 35, 308, 3662, 54089`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this is the first exact compressed subfamily inside the bridge-cograph
  closure
- it gives a much smaller recursive baseline for the branch

Boundary learned:

- the next search is a finer compression problem
- any new loop family should now beat the twin-pendant baseline, not just the
  bridge-cograph baseline

### New survivor: local move necessity law

Bounded and checked result:

- operator universe:
  - pendant
  - false twin
  - true twin
- shared checked domain:
  - `2 <= n <= 7`
- only the full triple hits:
  - `62 / 62`
- strongest strict subset:
  - `{false twin, true twin}`
  - `59 / 62`
  - misses exactly:
    - `(5, 5)`
    - `(6, 8)`
    - `(7, 10)`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this is the first checked minimality result for the compressed local grammar
- it shows the twin-pendant baseline is not trivially reducible by dropping
  one move

Boundary learned:

- the next search should target normal forms or finer semantic compression,
  not crude operator deletion

### New survivor: single-pendant frontier law

Bounded and checked result:

- operator baseline:
  - false twin
  - true twin
  - pendant
- shared checked domain:
  - `2 <= n <= 7`
- pendant budget `0`:
  - `59 / 62`
  - misses exactly:
    - `(5, 5)`
    - `(6, 8)`
    - `(7, 10)`
- pendant budget `1`:
  - `62 / 62`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this is the first checked normal-form compression inside the twin-pendant
  baseline
- it shows the bridge budgets need the possibility of pendant use, but only
  once

Boundary learned:

- the next search should target where that one pendant belongs, not whether
  many pendant events are needed

### New survivor: late-pendant frontier law

Bounded and checked result:

- baseline:
  - one-pendant twin growth
- shared checked domain:
  - `2 <= n <= 7`
- final-step-only:
  - `61 / 62`
  - misses exactly:
    - `(7, 10)`
- final-two-steps:
  - `62 / 62`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this is the first checked placement rule inside the one-pendant normal form
- it shows the pendant can be delayed almost to the end without losing the
  checked frontier

Boundary learned:

- the next normal-form question is no longer rough timing
- it is which anchor the late pendant must use

### New survivor: root-anchored late-pendant law

Bounded and checked result:

- baseline:
  - one-pendant twin growth
- pendant anchor:
  - oldest existing vertex
- shared checked domain:
  - `2 <= n <= 7`
- root-anchored final-step-only:
  - `61 / 62`
  - misses exactly:
    - `(7, 10)`
- root-anchored final-two-steps:
  - `62 / 62`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this is the strongest checked anchor normal form on the branch so far
- it removes both:
  - arbitrary pendant count
  - arbitrary pendant anchor choice

Boundary learned:

- the remaining normal-form question is the special obstruction at:
  - `(7, 10)`
  under final-step root anchoring

### New survivor: final-step obstruction law

Bounded and checked result:

- focused budget:
  - `(n, m) = (7, 10)`
- exact optimum count:
  - `420`
- every exact optimum is leafless:
  - minimum degree `2`
  - degree multiset:
    - `[2, 2, 3, 3, 3, 3, 4]`
- best root-anchored final-step-only branch:
  - without pendant:
    - `107`
  - with pendant:
    - `107`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this is the first exact obstruction explanation on the branch
- it shows the miss is not accidental
- it is forced by a clean split between:
  - pendant-used leaf obstruction
  - no-pendant twin-only ceiling

Boundary learned:

- the next question is no longer why final-step root anchoring fails
- it is why one-step-earlier pendant use repairs the budget

### New survivor: pendant-true-twin repair law

Bounded and checked result:

- focused budget:
  - `(n, m) = (7, 10)`
- family:
  - root-anchored tail-window-two one-pendant twin growth
- exact global optimum:
  - `109`
- unique optimal final-two-step pattern:
  - `pendant -> true_twin`
- every other final-two-step pattern is capped at:
  - `107`
- optimal family states:
  - `2`
- optimal family graphs:
  - `1`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this is the first exact constructive repair motif on the branch
- it turns the last repaired miss into a local semantic law, not just an
  existential family hit
- it shows the repair works by:
  - penultimate root pendant
  - final true-twin lift of the new pendant leaf

Boundary learned:

- the next frontier is no longer broadening the local grammar again
- it is searching for more exact repair motifs, or comparing this repaired
  compressed loop directly against verifier-compilation style baselines

### New survivor: bridge-budget motif narrowing law

Bounded and checked result:

- family:
  - root-anchored tail-window-two one-pendant twin growth
- focused repaired bridge budgets:
  - `(5, 5)`
  - `(6, 8)`
  - `(7, 10)`
- exact optimal motif library:
  - `(5, 5)`:
    - `pendant -> true_twin`
    - `true_twin -> pendant`
  - `(6, 8)`:
    - `pendant -> true_twin`
    - `true_twin -> pendant`
  - `(7, 10)`:
    - `pendant -> true_twin`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this is the first exact motif ladder on the branch
- it shows the repaired budgets are not isolated accidents
- the optimal repair library narrows in a structured way as the bridge budget
  deepens

Boundary learned:

- the next search object should be motif libraries, not only broader growth
  grammars
- direct loop comparison against verifier-compilation style baselines is now
  better motivated

### New survivor: hybrid controller advantage law

Bounded and checked result:

- task:
  - exact missing-set identification over `F_all`
- shared separator language:
  - block-intersection queries
- direct raw-family controller depth:
  - `n`
- hybrid pair-basis plus block residual-controller depth:
  - `ceil(log2 n)`
- exact depth gap:
  - `n - ceil(log2 n)`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this is the first exact scoped controller-size win over a plain direct
  controller on the branch
- it turns the earlier intuition into a real comparison theorem
- it shows a hybrid quotient-question loop can beat a direct compiled
  controller under the same separator language

Boundary learned:

- this is not yet a full end-to-end cost claim
- it is conditional on pair observations already being available as loop state
- the next direct comparison should target the newer motif-library branch

### New survivor: weighted hybrid-value law

Bounded and checked result:

- task:
  - exact missing-set identification over `F_all`
- weighted loop value:
  - `U = alpha * pure_resolved_mass + beta * depth_saving - gamma * acquisition`
- exact pair-basis ingredients:
  - `A_pair(n) = C(n, 2)`
  - `P_pair(n) = 2^n - n - 1`
  - `G_block(n) = n - ceil(log2 n)`
  - `G_atom(n) = 1`
- exact win conditions:
  - pair-plus-block beats direct iff:
    - `alpha * (2^n - n - 1) + beta * (n - ceil(log2 n)) > gamma * C(n, 2)`
  - pair-plus-atom beats direct iff:
    - `alpha * (2^n - n - 1) + beta > gamma * C(n, 2)`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this is the first explicit cost-model law on the branch
- it replaces vague “stronger loop” talk with a precise weighted boundary
- it also shows that pair-plus-block weakly dominates pair-plus-atom under
  unit weights, and strictly so for `n >= 4`

Boundary learned:

- the next comparison should price motif libraries in the same three-part way:
  - acquisition
  - pure resolved mass
  - residual controller depth

### New survivor: bridge-budget weighted pricing law

Bounded and checked result:

- motif family:
  - clique-bridge witness loops
- focused budgets:
  - `(5, 5)`
  - `(6, 8)`
  - `(7, 10)`
- under unit weights:
  - clique-bridge beats direct on all three
  - pair-plus-block still has the higher value
- exact switching boundaries against pair-plus-block:
  - `(5, 5)`:
    - `5 * gamma > 5 * alpha + beta`
  - `(6, 8)`:
    - `7 * gamma > 7 * alpha + beta`
  - `(7, 10)`:
    - `11 * gamma > 11 * alpha + 2 * beta`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this is the first exact weighted pricing result for the motif branch itself
- it shows motif loops are not only decorative alternatives
- they win exactly when acquisition price is high enough

Boundary learned:

- the next motif comparison should widen beyond clique bridges
- balanced multipartite and later motif libraries should be priced in the same
  framework

### New survivor: balanced ladder weighted frontier law

Bounded and checked result:

- family:
  - balanced multipartite ladder
- checked exact grid:
  - `2 <= n <= 7`
- full pair basis versus every balanced sparse rung:
  - full pair is always unit-weight optimal or tied
- minimal sparse takeover threshold under `alpha = beta = 1`:
  - `n = 4`:
    - `1.5`
  - `n = 5`:
    - `1.0`
  - `n = 6`:
    - `1.0`
  - `n = 7`:
    - `1.0`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this is the first family-level weighted frontier law for the balanced ladder
- it shows the dense pair endpoint is not universally best
- it is only unit-weight best on the checked grid
- near-dense sparse rungs can overtake as soon as acquisition price rises

Boundary learned:

- the next question is no longer whether sparse balanced rungs can compete
- it is whether any exact family can beat pair-plus-block under unit or
  near-unit weights

### New survivor: pair-graph total-domination correction law

Bounded and checked result:

- full pair-witness graph observation:
  - `O_G(M) = E(G[M])`
- exact corrected purity criterion:
  - `M is pure iff M is a total dominating set of G`
- exhaustive graph checks:
  - `2 <= n <= 6`
  - no counterexample
- representative proxy failures:
  - one-edge graph on `3` vertices:
    - true pure: `0`
    - proxy: `2`
  - clique-bridge `B(3, 2)`:
    - true pure: `9`
    - proxy: `21`
- claim tier:
  - `direct_amount_compiler`

Why it mattered:

- this repairs the graph-shaped pair branch at its root
- it identifies the real graph-theoretic object behind exact purity
- it quarantines the edge-containing proxy as a local heuristic, not a live
  exact metric

Boundary learned:

- graph-family frontier claims from the proxy branch must be rebuilt on total
  domination before reuse

### New survivor: corrected balanced-ladder frontier law

Bounded and checked result:

- family:
  - balanced complete multipartite ladder
- corrected true purity metric:
  - `pure_classes_true(G) = TD(G)`
- exhaustive graph domain:
  - `2 <= n <= 6`
- exact corrected frontier result:
  - every balanced ladder budget hits the true frontier
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this is the first trustworthy graph-family frontier result after the
  correction
- the balanced ladder survives the move back to the true observation quotient
- the earlier balanced gaps were proxy artifacts

Boundary learned:

- the next live question is whether any non-balanced family really beats the
  corrected balanced ladder, not whether the proxy graph branch looked richer

### New survivor: corrected complete-multipartite frontier law

Bounded and checked result:

- family:
  - full complete multipartite graphs
- corrected true purity metric:
  - `pure_classes_true(G) = TD(G)`
- exhaustive graph domain:
  - `2 <= n <= 6`
- exact corrected frontier result:
  - every represented complete multipartite budget hits the true frontier
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this strengthens the corrected graph branch beyond the balanced slice
- it turns the next search target into a concrete set of uncovered budgets
- it is the cleanest trustworthy graph-family frontier on the branch so far

Boundary learned:

- the next live families should target budgets not representable by complete
  multipartite graphs

### New survivor: corrected complete-multipartite frontier extension law

Bounded and checked result:

- family:
  - full complete multipartite graphs
- corrected true purity metric:
  - `pure_classes_true(G) = TD(G)`
- exhaustive graph domain:
  - `2 <= n <= 7`
- exact corrected frontier result:
  - every represented complete multipartite budget hits the true frontier
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this extends the corrected graph baseline to the same `n = 7` ceiling as the
  older proxy branch
- it makes the corrected branch large enough to compare honestly against old
  claims

Boundary learned:

- new graph-side families should be judged against the corrected `n <= 7`
  multipartite baseline, not the old proxy frontier

### New survivor: multipartite large-block edge invariance law

Bounded and checked result:

- start with a complete multipartite graph
- add one internal edge inside a block of size at least `3`
- exhaustive partition checks:
  - `2 <= n <= 7`
- exact result:
  - corrected true pure mass is unchanged
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this is the first exact low-complexity repair law above the corrected
  multipartite baseline
- it exposes a genuine one-edge family axis instead of a vague graph search

Boundary learned:

- the next step is to compare the whole repaired family, not only the
  invariance law in isolation

### New survivor: corrected one-edge multipartite frontier cover law

Bounded and checked result:

- family:
  - complete multipartite
  - plus one internal edge
- corrected true purity metric:
  - `pure_classes_true(G) = TD(G)`
- exhaustive graph domain:
  - `2 <= n <= 7`
- exact corrected frontier result:
  - every budget defined by the family hits the true frontier
- remaining uncovered `n = 7` budgets:
  - `2, 3, 4, 5, 8, 9`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this is the strongest corrected graph-family cover on the branch so far
- it shrinks the live uncovered set to a small explicit target

Boundary learned:

- the next honest search is for two-edge or other low-complexity repairs above
  the one-edge repaired multipartite baseline

### New survivor: corrected two-edge multipartite frontier cover law

Bounded and checked result:

- family:
  - complete multipartite
  - plus up to two internal edges
- corrected true purity metric:
  - `pure_classes_true(G) = TD(G)`
- exhaustive graph domain:
  - `2 <= n <= 7`
- exact corrected frontier result:
  - every defined family budget hits the true frontier
- remaining uncovered `n = 7` budgets:
  - `3, 4, 5, 9`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this strengthens the repaired-family cover again
- it shrinks the live graph-side target to only four budgets at `n = 7`

Boundary learned:

- the next low-complexity families should target exactly:
  - `3, 4, 5, 9`

### New survivor: star-plus-leaf-graph decomposition law

Bounded and checked result:

- family:
  - star on `k` leaves
  - plus arbitrary leaf graph `H`
- exact decomposition:
  - `TD(G) = (2^k - 1) + TD(H)`
- exhaustive leaf-graph checks:
  - `1 <= k <= 6`
- representative corrected consequences:
  - shared-leaf two-edge repair:
    - `63`
  - perfect matching repair:
    - `64`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- it turned the star-side holdouts into a leaf-language problem
- it separated the universal star contribution from the leaf correction

Boundary learned:

- the next step was no longer broad frontier coverage
- it was the low-edge leaf optimizer and the disconnected product geometry

### New survivor: disjoint-union total-domination product law

Bounded and checked result:

- for disjoint simple graphs `G` and `H`:
  - `TD(G union H) = TD(G) * TD(H)`
- exhaustive graph-pair checks:
  - `1 <= |V(G)| <= 4`
  - `1 <= |V(H)| <= 4`
- claim tier:
  - `symbolic_state_compiler`

Why it mattered:

- this is the first exact product law on the corrected graph branch
- disconnected corrected graph search can now be treated componentwise
- it gives the right algebra for the low-edge side

Boundary learned:

- the next honest move was not another disconnected family scan
- it was a direct low-edge frontier law using the product structure

### New survivor: balanced star-forest low-edge frontier law

Bounded and checked result:

- exhaustive simple graph domain:
  - `2 <= n <= 7`
  - `0 <= m <= n - 1`
- exact threshold law:
  - frontier is `0` when `m < ceil(n / 2)`
- exact low-edge frontier law:
  - frontier is `F_bal(n, m)` when `ceil(n / 2) <= m <= n - 1`
- direct formula:
  - `c = n - m`
  - `n = c*q + r`
  - `F_bal(n, m) = (2^(q - 1) - 1)^(c - r) * (2^q - 1)^r`
- representative corrected `n = 7` values:
  - `m = 4 -> 3`
  - `m = 5 -> 21`
  - `m = 6 -> 63`
- leaf consequence:
  - `F_bal(6, 3) = 1`
- claim tier:
  - `direct_amount_compiler`

Why it mattered:

- the corrected low-budget holdouts `3`, `4`, and `5` are now closed
- combined with the star-plus-leaf law, the corrected `n = 7`, budget `9`
  optimum is also explained
- the low-edge side now has a real direct formula, not only family coverage

Boundary learned:

- the next honest frontier is no longer the low-budget repaired-family gap
- it is a cleaner corrected regime map and higher-budget exact families beyond
  the current repaired multipartite ladder

### New survivor: corrected small-n graph regime-cover law

Bounded and checked result:

- checked exact graph domain:
  - `2 <= n <= 7`
- every exact true frontier budget is covered by at least one of:
  - low-edge balanced star forests
  - complete multipartite plus up to two internal edges
  - a star plus a low-edge leaf correction
- representative `n = 7` assignments:
  - `m = 4 ->` low-edge balanced star forest
  - `m = 9 ->` star plus low-edge leaf correction
  - `m = 12 ->` repaired multipartite
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- the corrected graph branch now has one coherent small-`n` regime map
- this is a stronger stopping point than a pile of local repaired-family laws

Boundary learned:

- the next honest move is no longer to clean up the low-budget side
- it is to extend the regime cover beyond `n = 7`, or to compress the
  higher-budget repaired multipartite side into a cleaner direct law

### New survivor: multipartite repaired-block additivity law

Bounded and checked result:

- family:
  - complete multipartite graph
  - plus arbitrary internal graph `H_i` inside each block
- checked exact domain:
  - every nontrivial partition with `2 <= n <= 7`
- exact additive law:
  - `TD(G) = base(P_1, ..., P_t) + sum_i TD(H_i)`
- claim tier:
  - `symbolic_state_compiler`

Why it mattered:

- this is the cleanest repaired multipartite compression on the corrected graph
  branch so far
- it subsumes both:
  - the star-plus-leaf law
  - and the large-block one-edge invariance law

Boundary learned:

- the next honest move was no longer another repaired-family patch
- it was a direct optimizer on a significant internal-budget regime

### New survivor: low-edge repaired-multipartite optimizer law

Bounded and checked result:

- family:
  - complete multipartite graph plus low-edge internal block repairs
- checked exact domain:
  - every nontrivial partition with `2 <= n <= 7`
- exact optimizer:
  - `OPT(parts; e_1, ..., e_t) = base(parts) + sum_i F_bal(s_i, e_i)`
  - for:
    - `0 <= e_i <= s_i - 1`
- claim tier:
  - `direct_amount_compiler`

Why it mattered:

- the repaired multipartite side now has a true direct amount law on a large
  structured subfamily
- the corrected graph branch is no longer only:
  - a regime map
  - plus a family cover
- it now also has a real direct optimizer on one major regime

Boundary learned:

- the next honest frontier is beyond the low-edge internal-budget regime
- or extension of the corrected regime map beyond `n = 7`

### New survivor: repaired-multipartite recursive optimizer law

Bounded and checked result:

- family:
  - complete multipartite graph plus arbitrary internal block budgets
- checked exact domain:
  - every nontrivial partition with `2 <= n <= 7`
- exact recursive optimizer:
  - `OPT_repaired(parts; e_1, ..., e_t) = base(parts) + sum_i OPT_graph(s_i, e_i)`
- claim tier:
  - `symbolic_state_compiler`

Why it mattered:

- this removes the low-edge restriction from the repaired multipartite
  optimizer story
- the repaired side is now cleanly reduced to the standalone block frontier

Boundary learned:

- the next honest compression target is not multipartite coupling
- it is the single-block frontier `OPT_graph(s, e)`

### New survivor: threshold-split collapse law on the corrected single-block frontier

Bounded and checked result:

- corrected single-block domain:
  - `2 <= n <= 7`
- threshold and split graphs attain exactly the same frontier value at every
  edge budget
- shared miss budgets against the full corrected frontier:
  - `n = 4`: `2, 4`
  - `n = 5`: `3, 6, 8`
  - `n = 6`: `3, 4, 8, 9, 10, 11, 12, 13`
  - `n = 7`: `4, 5, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this closes the threshold-to-split ladder on the corrected single-block
  branch
- it means the next honest search must move to genuinely non-split families,
  not just a slightly larger clique-independent grammar

Boundary learned:

- do not spend more search budget on split-only refinements of the corrected
  single-block frontier
- the next target is a non-split family or a direct regime law for
  `OPT_graph(s, e)`

### New survivor: corrected small-domain single-block regime compiler law

Bounded and checked result:

- checked domain:
  - `2 <= n <= 7`
- exact direct amount compiler:
  - `OPT_graph(n, m)` equals the maximum of:
    - balanced star forests
    - complete multipartite plus up to two internal edges
    - full star plus low-edge leaf correction
- claim tier:
  - `direct_amount_compiler`

Why it mattered:

- this upgrades the corrected graph branch from a descriptive regime cover to
  a true direct evaluator on the checked single-block domain

Boundary learned:

- the next question is no longer whether those three regimes cover the checked
  frontier
- it is whether the third regime is broadly necessary

### New survivor: one-point corrected single-block compiler law

Bounded and checked result:

- checked domain:
  - `2 <= n <= 7`
- removing the full-star-plus-leaf regime leaves exactly one miss:
  - `(7, 9)`
- exact one-point direct compiler:
  - `OPT_graph(n, m)` equals the maximum of:
    - balanced star forests
    - complete multipartite plus up to two internal edges
    - the point correction `(7, 9) -> 64`
- claim tier:
  - `direct_amount_compiler`

Why it mattered:

- this is the cleanest current small-domain object on the corrected graph
  branch
- it makes the branch much easier to teach honestly

Boundary learned:

- the next target is not another broad family patch
- it is the meaning or extension of the exceptional point `(7, 9)`

### New survivor: exceptional point structure law at `(7, 9)`

Bounded and checked result:

- corrected exceptional point:
  - `(n, m) = (7, 9)`
- exact optimum:
  - `64`
- every optimal graph is isomorphic to:
  - a full star plus a perfect matching on the six leaves
- optimal labeled graph count:
  - `105`
- optimal isomorphism type count:
  - `1`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- the point correction in the one-point compiler is now structurally explained
- the branch ends on a named motif, not on a mysterious scalar patch

Boundary learned:

- the next honest move is not to search more small-domain patches
- it is to test whether the star-plus-perfect-matching motif generalizes

### New survivor: star-plus-perfect-matching total-domination law

Bounded and checked result:

- family:
  - one center joined to `2r` leaves
  - plus a perfect matching on the leaves
- exact law:
  - `TD(F_r) = 2^(2r)`
- checked for:
  - `1 <= r <= 6`
- claim tier:
  - `direct_amount_compiler`

Why it mattered:

- the exceptional-point motif from `v218` is now a reusable exact family law
- it can be named and reasoned about directly, rather than only by one
  special case

Boundary learned:

- the live question is no longer whether the family has a clean formula
- it is how that family interacts with the true frontier beyond the checked
  point `(7, 9)`

### New survivor: odd-line regime selector law in the corrected compiler family

Bounded and checked result:

- on the line:
  - `n = 2r + 1`
  - `m = 3r`
- balanced star forests are never available
- multipartite plus up to two internal edges is reachable iff:
  - `r <= 2`
- star-plus-leaf has exact value:
  - `2^(2r)`
- selector pattern on checked `1 <= r <= 8`:
  - tie at `r = 1`
  - multipartite win at `r = 2`
  - star-plus-leaf as the only available regime for `r >= 3`
- claim tier:
  - `direct_amount_compiler`

Why it mattered:

- this is the cleanest current explanation of why the corrected compiler
  switches character at `r = 3`
- it turns the odd-line branch into a real selector law, not just local
  observations

Boundary learned:

- the next honest question is frontier-optimality, not regime availability

### New survivor: full-star-plus-low-edge family compiler law

Bounded and checked result:

- checked family band:
  - `2 <= n <= 8`
  - `n - 1 <= m <= 2n - 3`
- exact direct family compiler:
  - `OPT_star_leaf(n, m) = (2^(n - 1) - 1) + F_bal(n - 1, m - (n - 1))`
- below the leaf no-isolate threshold:
  - the family collapses to the plain star value
- representative checked rows:
  - `n = 7, m = 8 -> 63`
  - `n = 7, m = 9 -> 64`
  - `n = 7, m = 11 -> 94`
- claim tier:
  - `direct_amount_compiler`

Why it mattered:

- the star-plus-leaf side is no longer only an odd-line motif family
- it is now a reusable exact compiler on a whole checked band

Boundary learned:

- the next honest question is where this family is frontier-optimal, not only
  family-optimal

### New survivor: high-band two-regime overlap compiler law

Bounded and checked result:

- checked overlap band:
  - `2 <= n <= 7`
  - `n - 1 <= m <= 2n - 3`
- exact checked frontier:
  - `OPT_graph(n, m) = max(OPT_star_leaf(n, m), multipartite_plus_two_internal(n, m))`
- representative selector rows:
  - `n = 7, m = 9`:
    - star-plus-low-edge wins alone
  - `n = 7, m = 10`:
    - repaired multipartite wins alone
  - `n = 7, m = 11`:
    - tie
- claim tier:
  - `direct_amount_compiler`

Why it mattered:

- the checked high single-block band now has a much cleaner exact teaching
  object
- the live competition on that band is between two regimes only

Boundary learned:

- the next honest question is whether the selector between those two regimes
  admits a direct arithmetic rule

### New survivor: checked high-band selector stripe law

Bounded and checked result:

- on the checked overlap slice:
  - `4 <= n <= 7`
  - `n - 1 <= m <= 2n - 3`
- unique star row:
  - `(7, 9)`
- unique multipartite rows:
  - the stripe `m = 2n - 4`
  - plus `(6, 9)`
- every other checked row:
  - tie
- claim tier:
  - `checked_selector_map`

Why it mattered:

- the graph-side overlap is now closer to a true selector law than a raw table
- that makes the hybrid graph story more tutorial-ready

Boundary learned:

- the next honest question is whether this checked selector pattern survives
  beyond the small domain

### New survivor: extended two-family overlap selector law

Bounded and checked result:

- on the family-comparison domain:
  - `7 <= n <= 12`
  - `n - 1 <= m <= 2n - 3`
- ties at:
  - `m = n - 1, n, n + 1, 2n - 3`
- unique multipartite win at:
  - `m = 2n - 4`
- unique star-plus-low-edge win on:
  - `n + 2 <= m <= 2n - 5`
- claim tier:
  - `direct_amount_compiler`

Why it mattered:

- the graph-side hybrid selector is now structurally simple on a much wider
  checked two-family domain
- that is a better object for both tutorialization and future frontier scans

Boundary learned:

- the next honest question is whether the full corrected frontier still agrees
  with this two-family selector beyond the smaller exact slice

### New survivor: extended two-family overlap family-compiler law

Bounded and checked result:

- on the family-comparison domain:
  - `7 <= n <= 12`
  - `n - 1 <= m <= 2n - 3`
- exact piecewise compiler:
  - `2^(n - 1) - 1` on the low plateau
  - `OPT_star_leaf(n, m)` on the middle interval
  - `3 * 2^(n - 2) - 3` at the near-top peak
  - `3 * 2^(n - 2) - 2` at the top tie point
- claim tier:
  - `direct_amount_compiler`

Why it mattered:

- the graph-side overlap no longer needs to be taught as a selector table
- it is now a direct piecewise compiler on the wider checked two-family domain

Boundary learned:

- the next honest question is whether the full corrected frontier itself still
  agrees with this piecewise two-family compiler beyond the exact `v224` slice

### New survivor: repaired-multipartite high-band availability and formula law

Bounded and checked result:

- on the repaired multipartite family domain:
  - `7 <= n <= 20`
  - `n - 1 <= m <= 2n - 3`
- availability exactly at:
  - `m = n - 1, n, n + 1, 2n - 4, 2n - 3`
- exact gap:
  - no repaired multipartite graph on `n + 2 <= m <= 2n - 5`
- exact values:
  - `2^(n - 1) - 1`
  - `3 * 2^(n - 2) - 3`
  - `3 * 2^(n - 2) - 2`
- claim tier:
  - `direct_amount_compiler`

Why it mattered:

- this explains the multipartite side of the graph overlap directly
- it also turns the family itself into a tiny direct compiler on the checked
  high band

Boundary learned:

- the next honest question is whether the full corrected frontier still
  follows the same widened overlap compiler

### New survivor: checked tree-star dominance law

Bounded and checked result:

- on connected labeled trees:
  - `2 <= n <= 8`
  - `m = n - 1`
- exact checked best value:
  - `2^(n - 1) - 1`
- attained by:
  - the star `K_{1, n - 1}`
- largest checked tree domain:
  - `262144` connected trees at `n = 8`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this is the first clear proof-oriented component law behind the low-edge
  star-forest branch
- it points toward a less brute-force explanation of the low-edge frontier

Boundary learned:

- the next honest question is whether this tree-star dominance can be lifted
  into a proof of the balanced star-forest low-edge law

### New survivor: non-star tree extremal gap law

Bounded and checked result:

- on connected non-star trees:
  - `4 <= n <= 8`
  - `m = n - 1`
- exact checked non-star maximum:
  - `2^(n - 2)`
- equality family:
  - double-stars
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this sharpens the tree branch into a true extremal ladder
- it also identifies the whole equality family, not only the top star

Boundary learned:

- the next honest question is whether a local improvement law drives arbitrary
  trees toward the double-star and star extremal families

### New survivor: widened overlap family compiler

Bounded and checked result:

- on the corrected two-family overlap:
  - `7 <= n <= 20`
  - `n - 1 <= m <= 2n - 3`
- exact direct compiler:
  - `2^(n - 1) - 1` on `n - 1 <= m <= n + 1`
  - `OPT_star_leaf(n, m)` on `n + 2 <= m <= 2n - 5`
  - `3 * 2^(n - 2) - 3` at `m = 2n - 4`
  - `3 * 2^(n - 2) - 2` at `m = 2n - 3`
- claim tier:
  - `direct_amount_compiler`

Why it mattered:

- the corrected high-band overlap is now a direct compiler, not only a family
  selector

Boundary learned:

- the next honest question is whether the low-edge side can be turned into a
  proof-shaped concentration mechanism with the same level of clarity

### New survivor: pendant-subtree concentration law

Bounded and checked result:

- on connected trees:
  - `4 <= n <= 8`
  - `m = n - 1`
- every non-star unlabeled class has a pendant-subtree transfer with:
  - `TD(T') >= TD(T)`
  - `Phi(T') > Phi(T)`
- every checked tree class reaches the star through the directed improving
  move graph
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- leaf transfers were too weak
- pendant-subtree transfers survive and give the first clean monotone move law
  on the corrected tree branch

Boundary learned:

- the next honest question is how to combine this with star-size balancing on
  forests

### New survivor: star-forest balancing law

Bounded and checked result:

- on star forests with:
  - `c` components
  - each size at least `2`
- the balanced size profile is the exact optimizer of the star-family product
- exhaustive profile checks match the closed form on:
  - `2 <= c <= 8`
  - `2c <= n <= 20`
- claim tier:
  - `direct_amount_compiler`

Why it mattered:

- the balanced star-forest formula is now an exact family optimizer, not only a
  checked frontier fit

Boundary learned:

- the next honest question is whether component starification and exact
  balancing compose into one low-edge mechanism

### New survivor: two-stage low-edge concentration law

Bounded and checked result:

- on positive low-edge forests:
  - `2 <= n <= 8`
  - `ceil(n / 2) <= m <= n - 1`
- every unlabeled forest class admits a finite monotone path to the balanced
  star forest by:
  - starifying components
  - then balancing star sizes
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- the low-edge branch now has a proof-shaped concentration story, not only a
  frontier table

Boundary learned:

- the next honest question is whether the checked tree concentration law can be
  extended beyond `n <= 8`

### New survivor: pendant-subtree concentration, `n = 9` extension

Bounded and checked result:

- on connected trees with:
  - `n = 9`
  - `m = n - 1`
- full labeled scan:
  - `4,782,969` Prüfer codes
- unlabeled classes:
  - `47`
- every non-star class has an improving pendant-subtree move
- every class reaches the star through the improving move graph
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this pushes the tree concentration branch past the tiny checked range
- it makes the low-edge proof path look materially more stable

Boundary learned:

- the next honest question is now proof, not only more scanning

### New survivor: hub-target pendant-subtree law

Bounded and checked result:

- on connected trees with:
  - `n in {8, 9}`
  - `m = n - 1`
- every non-star unlabeled class has an improving pendant-subtree transfer
  whose reattachment target is a maximum-degree vertex
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this compresses the move language from “some improving move exists” to
  “move a pendant subtree toward a hub”

Boundary learned:

- the next honest question is whether the source side can be compressed too,
  or whether the branch is ready for proof work

### New survivor: one-branch hub-target pendant-subtree law

Bounded and checked result:

- on connected trees with:
  - `n in {8, 9}`
  - `m = n - 1`
- every non-star unlabeled class has an improving pendant-subtree transfer
  whose reattachment target is a maximum-degree hub and whose moved subtree has
  at most one branching vertex
- stronger source-side simplifications fail on the same checked domain:
  - leaf-only hub moves
  - pendant-star hub moves
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this is the first source-side compression after the hub-target law
- it turns the surviving tree move into a much smaller geometric object

Boundary learned:

- the next honest step is proof, not another random move-language scan

### New survivor: one-branch hub-to-balance low-edge mechanism law

Bounded and checked result:

- on positive low-edge forests with:
  - `2 <= n <= 8`
  - `ceil(n / 2) <= m <= n - 1`
- every unlabeled forest class admits a finite monotone path to the balanced
  star forest by composing:
  - one-branch hub-target concentration on components
  - exact star-size balancing
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this upgrades the low-edge side from separate ingredients to one compact
  two-stage mechanism

Boundary learned:

- the next honest step is a structural proof of the composed mechanism

### New survivor: one-branch hub-target concentration path law

Bounded and checked result:

- on connected trees with:
  - `n in {8, 9}`
  - `m = n - 1`
- every unlabeled tree class reaches the star through a finite monotone path
  using only one-branch hub-target improving moves
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this upgrades `v237` from a one-step local refinement to a complete checked
  restricted rewrite system on the tree branch

Boundary learned:

- the next honest step is a structural proof of the one-branch hub-target path
  law, not another local move search

### New survivor: minimal-size one-branch hub-target path law

Bounded and checked result:

- on connected trees with:
  - `n in {8, 9}`
  - `m = n - 1`
- every unlabeled tree class reaches the star through a finite monotone path
  using only minimal-size one-branch hub-target improving moves
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this sharpens the restricted rewrite system into a smallest-move controller
  candidate

Boundary learned:

- the next honest step is proof, not more ad hoc local restrictions

### New survivor: depth-2 cutoff for the minimal tree controller

Bounded and checked result:

- on connected trees with:
  - `n in {8, 9}`
  - `m = n - 1`
- for minimal-size one-branch hub-target moves:
  - branch-depth bound `0` fails
  - branch-depth bound `1` fails
  - branch-depth bound `2` survives
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this is the first exact local depth threshold on the checked tree branch

Boundary learned:

- the next honest step is a structural proof of the depth-2 cutoff

### New survivor: depth-2 hub-to-balance low-edge mechanism law

Bounded and checked result:

- on positive low-edge forests with:
  - `2 <= n <= 8`
  - `ceil(n / 2) <= m <= n - 1`
- every unlabeled forest class admits a finite monotone path to the balanced
  star forest by composing:
  - minimal-size one-branch hub-target concentration with branch-depth bound `2`
  - exact star-size balancing
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- the full low-edge branch now inherits the sharper local controller

Boundary learned:

- the next honest step is a proof of the depth-2 local controller and its
  composition

### New survivor: terminal-cherry ladder depth law

Bounded and checked result:

- on the terminal-cherry ladder family, checked on `h = 0..5`:
  - the smallest one-branch hub-target improving move has exact size `h + 3`
  - for `h >= 1`, its unique branch point lies at exact depth `h`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this gives the depth cutoff a family-level explanation instead of only a scan
  table

Boundary learned:

- the `h = 2` ladder rung is the clean negative witness for the depth-1
  controller

### New survivor: exact template necessity law for the depth-2 tree controller

Bounded and checked result:

- on connected trees with:
  - `n in {8, 9}`
  - `m = n - 1`
- the exact subset lattice of the depth-2 template controller has:
  - survivor count:
    - `1`
  - minimal surviving template count:
    - `5`
- so the unique surviving subset is the full alphabet:
  - `leaf`
  - `cherry`
  - `three_leaf_star`
  - `broom_1`
  - `broom_2`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- the finite rewrite alphabet from `v245` is not only descriptive
- on the checked branch it is already minimal

Boundary learned:

- the next honest step is a structural proof of necessity and sufficiency for
  the full five-template controller

### New survivor: template-specific obstruction witnesses

Bounded and checked result:

- on connected trees with:
  - `n in {8, 9}`
  - `m = n - 1`
- every template in the five-template depth-2 controller has an explicit
  failing witness when removed
- first checked failures:
  - `broom_2`:
    - `n = 9`
  - `broom_1`:
    - `n = 8`
  - `three_leaf_star`:
    - `n = 9`
  - `cherry`:
    - `n = 8`
  - `leaf`:
    - `n = 8`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- the necessity side of the proof branch now has named witness shapes, not only
  a subset-lattice count

Boundary learned:

- the next honest step is to explain those five obstruction witnesses
  structurally

### New survivor: first obstruction-family taxonomy

Bounded and checked result:

- on the first checked obstruction catalog from `v247`:
  - `cherry` matches `terminal_cherry_ladder(1)`
  - `broom_1` matches `terminal_cherry_ladder(1)`
  - `broom_2` matches `terminal_cherry_ladder(2)`
  - `three_leaf_star` matches `subdivided_double_star(3, 3)`
  - `leaf` matches `endpoint_leaf_path(6)`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- the obstruction side is no longer only a list of five witnesses
- it collapses into a small named family taxonomy

Boundary learned:

- the next honest step is to compress that family list into a smaller macro
  taxonomy

### New survivor: two-macro-family obstruction taxonomy

Bounded and checked result:

- on the same first obstruction catalog:
  - `broom_2`, `broom_1`, `three_leaf_star`, and `cherry` are all one-ended
    terminal-fan obstructions
  - `leaf` is a two-ended endpoint-leaf obstruction
- macro family count:
  - `2`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this is the first proof-shaped obstruction taxonomy on the tree branch
- the necessity side now splits into:
  - one-ended terminal-fan failures
  - two-ended endpoint-leaf failures

Boundary learned:

- the next honest step is to turn that two-way obstruction split into a
  structural proof strategy

### Boundary result: non-leaf terminal-fan coverage is almost exact

Bounded and checked result:

- on connected trees with:
  - `n in {8, 9}`
  - `m = n - 1`
- deleting:
  - `broom_2`
  - `broom_1`
  - `three_leaf_star`
  leaves only terminal-fan failing classes
- deleting `cherry`:
  - still leaves only terminal-fan failing classes at `n = 8`
  - but has one non-terminal-fan exception at `n = 9`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this turns the non-leaf obstruction side into one almost-exact family law
  plus one localized exception

Boundary learned:

- the next honest step is to classify the unique cherry-side exception

### New survivor: unique cherry-side exception law

Bounded and checked result:

- on the same checked tree branch:
  - the only non-terminal-fan non-leaf exception appears when `cherry` is
    removed
  - it is unique
  - it matches a split-arm cherry shape:
    - hub with two direct leaves
    - one short arm ending in a leaf
    - one longer arm ending in a terminal cherry
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- the non-leaf necessity side is now essentially solved as:
  - terminal-fan family
  - plus one split-arm cherry exception

Boundary learned:

- the next honest step is a proof that reduces the non-leaf side to this
  decomposition

### New survivor: non-leaf threshold classifier on normalized terminal-fan coordinates

Bounded and checked result:

- on connected trees with:
  - `n in {8, 9}`
  - `m = n - 1`
- after deleting one non-leaf template from the checked depth-2 controller,
  the terminal-fan component of the failing set is exactly:
  - `cherry`: `u = 2`, `p >= 2`, `v >= 2`
  - `broom_1`: `u = 2`, `p >= 3`, `v >= 2`
  - `broom_2`: `u = 2`, `p >= 4`, `v >= 2`
  - `three_leaf_star`: `u = 3`, `p >= 2`, `v >= 3`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this replaces the terminal-fan shape catalog with one exact inequality
  classifier on normalized coordinates

Boundary learned:

- the remaining non-leaf gap is only the cherry-side split-arm correction term

### New survivor: full non-leaf exact classifier

Bounded and checked result:

- on the same checked tree domain, the full non-leaf failing set is exactly:
  - `broom_2`: the threshold slice `u = 2`, `p >= 4`, `v >= 2`
  - `broom_1`: the threshold slice `u = 2`, `p >= 3`, `v >= 2`
  - `three_leaf_star`: the threshold slice `u = 3`, `p >= 2`, `v >= 3`
  - `cherry`: the threshold slice `u = 2`, `p >= 2`, `v >= 2`
    plus `split_arm_cherry(2)`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- the descriptive search side of the non-leaf controller analysis is now
  closed by an exact checked classifier

Boundary learned:

- the next honest step is proof, not more catalog building

### New survivor: non-leaf obstruction ladder law

Bounded and checked result:

- on the normalized threshold rules from `v253`:
  - `broom_2 ⊊ broom_1 ⊊ cherry`
  - `three_leaf_star` is disjoint from that two-fan ladder
- so the four non-leaf deleted templates factor into:
  - a strict path-length ladder on the two-fan line
  - one disjoint fan-size gate
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this is the first small coordinate picture for the non-leaf side
- it turns four case labels into one ladder plus one orthogonal upgrade

Boundary learned:

- the next honest step is proof of the ladder and gate, not more case
  enumeration

### New survivor: terminal-fan selector and descent law

Bounded and checked result:

- on the checked non-leaf terminal-fan states:
  - `NTF(2, 2, v)` selects `cherry`
  - `NTF(2, 3, v)` selects `broom_1`
  - `NTF(2, 4, v)` selects `broom_2`
  - and the selected move sends:
    - `NTF(2, p, v) -> NTF(2, p - 1, v + 1)`
- the checked fan-size gate also has an exact selected descent:
  - `NTF(3, 2, 3)` selects `three_leaf_star`
  - and moves to `NTF(3, 1, 4)`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- this is the first mechanism-level explanation of the non-leaf threshold rules
- the threshold picture is now a small selected rewrite system

Boundary learned:

- the next honest step is to explain the obstruction slices as cuts in this
  descent system

### New survivor: two-fan deletion cut law

Bounded and checked result:

- on the checked two-fan line:
  - deleting `cherry` blocks exactly `p >= 2`
  - deleting `broom_1` blocks exactly `p >= 3`
  - deleting `broom_2` blocks exactly `p >= 4`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- the nested two-fan threshold slices are now explained as exact cuts in the
  checked selected descent ladder

Boundary learned:

- the next honest step is proof of the ladder and its cuts, not more threshold
  fitting

### New survivor: split-arm feeder law

Bounded and checked result:

- on the checked tree domain:
  - source state `split_arm_cherry(2)`
  - unique selected move template `leaf`
  - unique selected target `NTF(2, 2, 4)`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- the cherry-side correction is now a feeder into the bottom two-fan rung, not
  a stray extra case

Boundary learned:

- the next honest step is to close the whole cherry side as ladder cut plus
  feeder

### New survivor: cherry-side feeder-cut closure

Bounded and checked result:

- on the checked tree domain, the full `cherry`-deleted failing set is exactly:
  - the two-fan ladder cut `p >= 2`
  - plus the feeder state `split_arm_cherry(2)`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- the cherry-side correction term is now mechanistically integrated into the
  same picture as the threshold ladder

Boundary learned:

- the next honest step is proof of:
  - the two-fan ladder
  - the feeder relation
  - the fan-size gate

### New survivor: checked terminal-fan controller family law

Bounded and checked result:

- on the checked family domain:
  - `8 <= n <= 12`
  - two-fan line `NTF(2, p, v)`
  - three-fan gate line `NTF(3, 2, v)`
- the controller law is:
  - `p = 2`: `cherry`, target `NTF(2, 1, v + 1)`
  - `p = 3`: `broom_1`, target `NTF(2, 2, v + 1)`
  - `p = 4`: `broom_2`, target `NTF(2, 3, v + 1)`
  - `p >= 5`: no depth-2 selected move on the checked range
  - `NTF(3, 2, v)`: `three_leaf_star`, target `NTF(3, 1, v + 1)`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- the non-leaf controller is now a checked family law, not only isolated local
  rows

Boundary learned:

- the next honest step is to explain the first checked deviation at the
  symmetric edge `NTF(2, 8, 2)` on `n = 13`

### New survivor: split-arm feeder family law

Bounded and checked result:

- on the checked family `split_arm_cherry(k)` with `2 <= k <= 6`:
  - selected template `leaf`
  - selected target `NTF(2, 2, k + 2)`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- the cherry-side correction is now one member of a feeder family, not a lone
  special case

Boundary learned:

- the next honest step is a structural explanation of that feeder family and
  its attachment to the two-fan ladder

### New survivor: unique checked two-fan anomaly

Bounded and checked result:

- on the checked two-fan family:
  - `8 <= n <= 18`
  - `NTF(2, p, v)`
- there is exactly one deviation from the stable controller law:
  - `NTF(2, 8, 2)` on `n = 13`
  - selected template `broom_2`
  - target outside the terminal-fan family
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- the stable two-fan controller now has one named exception instead of a vague
  cloud of possible misses

Boundary learned:

- the next honest step is to explain that anomaly structurally

### New survivor: checked stable two-fan controller with one anomaly

Bounded and checked result:

- on the checked two-fan family `8 <= n <= 18`:
  - `p = 2`: `cherry`, target `NTF(2, 1, v + 1)`
  - `p = 3`: `broom_1`, target `NTF(2, 2, v + 1)`
  - `p = 4`: `broom_2`, target `NTF(2, 3, v + 1)`
  - `p >= 5`: no selected depth-2 move
  - one checked exception:
    - `NTF(2, 8, 2)` on `n = 13`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- the proof target is now stable enough to be attacked directly:
  - one law
  - one exception

Boundary learned:

- the next honest step is to explain the anomaly target family

### New survivor: bridge-fan-tail feeder family law

Bounded and checked result:

- on the checked bridge-fan-tail family `BFT(r, t)`:
  - checked range:
    - `2 <= r <= 6`
    - `1 <= t <= 5`
    - `n = r + t + 6 <= 15`
  - every checked row with `t >= 2`:
    - selects `leaf`
    - targets exactly `BFT(r + 1, t - 1)`
  - every checked row with `t = 1`:
    - selects `broom_1`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- the anomaly target now sits inside a checked feeder family with a recursive
  local rule

Boundary learned:

- the next honest step is to connect the anomaly entry state itself to this
  family

### New survivor: anomaly entry into the bridge-fan-tail feeder chain

Bounded and checked result:

- every checked selected move from the unique anomaly state:
  - source:
    - `NTF(2, 8, 2)` on `n = 13`
  - template:
    - `broom_2`
  - target:
    - exactly `BFT(2, 5)`
- checked feeder chain:
  - `BFT(2, 5) -> BFT(3, 4) -> BFT(4, 3) -> BFT(5, 2) -> BFT(6, 1)`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- the anomaly is no longer a loose exception
- it is an entry point into a named feeder chain

Boundary learned:

- the next honest step is a structural proof of:
  - the feeder law
  - the anomaly entry move
  - the base-line handoff to the remaining necessity cases

### New survivor: bridge-fan-tail base-line handoff law

Bounded and checked result:

- on the checked base line `BFT(r, 1)` with `2 <= r <= 6`:
  - selected template `broom_1`
  - selected target exactly `BFS(r + 2)`
  - where `BFS(s)` is:
    - left hub with `2` leaves
    - bridge of length `2` edges
    - right star with `s` leaves
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- the feeder chain now hands off into a second named family instead of ending
  in an unnamed base case

Boundary learned:

- the next honest step is to prove the handoff and classify the next local rule
  on `BFS(s)`

### New survivor: bridge-fan-star handoff law

Bounded and checked result:

- on the checked bridge-fan-star family `BFS(s)` with `4 <= s <= 10`:
  - selected template `cherry`
  - selected target exactly `ADS(s + 1)`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- the anomaly route now continues through another named family instead of
  stopping at the `BFS` handoff

Boundary learned:

- the next honest step is to classify the local controller on `ADS`

### New survivor: adjacent-double-star handoff law

Bounded and checked result:

- on the checked adjacent-double-star family `ADS(q)` with `4 <= q <= 11`:
  - selected template `leaf`
  - selected target exactly `OLAS(q + 1)`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- the route now continues through a one-leaf family rather than dissolving into
  an unnamed residual shape

Boundary learned:

- the next honest step is to test whether `OLAS` lands directly in the star

### New survivor: one-leaf-adjacent-star to star law

Bounded and checked result:

- on the checked one-leaf-adjacent-star family `OLAS(k)` with `5 <= k <= 11`:
  - selected template `leaf`
  - selected target is the star on the same `n`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- the named anomaly route now closes to the star

Boundary learned:

- the next honest step is to compress the full route as one object

### New survivor: anomaly-to-star named route law

Bounded and checked result:

- the unique anomaly `NTF(2, 8, 2)` factors through the checked named route:
  - `BFT(2, 5)`
  - `BFT(3, 4)`
  - `BFT(4, 3)`
  - `BFT(5, 2)`
  - `BFT(6, 1)`
  - `BFS(8)`
  - `ADS(9)`
  - `OLAS(10)`
  - star on the same `n = 13`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- the anomaly is no longer just attached to one feeder family
- it is now a compact named route to the star

Boundary learned:

- the next honest step is structural proof of the family handoffs and of the
  route composition

### New survivor: bridge-fan-tail route compiler law

Bounded and checked result:

- on the checked bridge-fan-tail family:
  - `2 <= r <= 6`
  - `1 <= t <= 5`
  - `r + t <= 7`
- the exact route to the star compiles from `(r, t)` alone
- exact route word:
  - `leaf^(t - 1) broom_1 cherry leaf leaf`
- exact route length:
  - `t + 3`
- claim tier:
  - `symbolic_state_compiler`

Why it mattered:

- this is the first small symbolic controller on the anomaly-side route itself
- it compresses a stack of local family laws into one reusable route object

Boundary learned:

- the next honest step is to widen the checked tail and then widen the whole
  route compiler

### New survivor: extended downstream tail-controller law

Bounded and checked result:

- on the checked downstream families:
  - `BFS(s)` for `4 <= s <= 15`
  - `ADS(q)` for `4 <= q <= 15`
  - `OLAS(k)` for `5 <= k <= 16`
- exact local laws remain:
  - `BFS(s) -> ADS(s + 1)` by `cherry`
  - `ADS(q) -> OLAS(q + 1)` by `leaf`
  - `OLAS(k) -> star` by `leaf`
- so the composed tail
  - `BFS(s) -> ADS(s + 1) -> OLAS(s + 2) -> star`
  is checked for `4 <= s <= 14`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- the downstream half of the route is now a wider reusable controller block,
  not only a small local chain

Boundary learned:

- the next honest step is to widen the bridge-fan-tail route compiler so it
  can consume that larger tail

### New survivor: wider bridge-fan-tail route compiler law

Bounded and checked result:

- on the checked bridge-fan-tail rectangle:
  - `2 <= r <= 7`
  - `1 <= t <= 5`
  - `n = r + t + 6 <= 18`
- the exact route to the star still compiles from `(r, t)` alone
- exact route word stays:
  - `leaf^(t - 1) broom_1 cherry leaf leaf`
- exact route length stays:
  - `t + 3`
- claim tier:
  - `symbolic_state_compiler`

Why it mattered:

- the route compiler survives on a materially wider checked domain
- that turns it from a narrow anomaly-side curiosity into a more serious loop
  object

Boundary learned:

- the next honest step is proof of the feeder law, the widened tail controller,
  and the widened route compiler composition

### New survivor: extended unique two-fan anomaly law

Bounded and checked result:

- on the checked two-fan family:
  - `8 <= n <= 20`
- there is still exactly one deviation from the stable controller law:
  - `NTF(2, 8, 2)` on `n = 13`
- the new checked rows:
  - `n = 19`
  - `n = 20`
  add no new anomaly states
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- the anomaly now looks structurally isolated on a wider checked domain
- the stable two-fan controller plus one named escape route remains the right
  live picture

Boundary learned:

- the next honest step is to prove the stable law and the unique escape
  structurally, not just extend rows

### New survivor: downstream tail amount law

Bounded and checked result:

- on the checked downstream route families:
  - `TD(BFS(s)) = 7 * 2^s - 3`
  - `Phi(BFS(s)) = s^2 + 3s + 16`
  - `TD(ADS(q)) = 2^(q + 2)`
  - `Phi(ADS(q)) = q^2 + 3q + 12`
  - `TD(OLAS(k)) = 2^(k + 1)`
  - `Phi(OLAS(k)) = k^2 + 3k + 6`
  - `TD(star_n) = 2^(n - 1) - 1`
  - `Phi(star_n) = n(n - 1)`
- exact checked tail gains:
  - `BFS(s) -> ADS(s + 1)`:
    - `TD` gain `= 2^s + 3`
    - `Phi` gain `= 2s`
  - `ADS(q) -> OLAS(q + 1)`:
    - `TD` gain `= 0`
    - `Phi` gain `= 2q - 2`
  - `OLAS(k) -> star_{k + 3}`:
    - `TD` gain `= 2^(k + 1) - 1`
    - `Phi` gain `= 2k`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- the downstream half of the route is now an exact amount ladder
- the middle step is now explained cleanly:
  - no `TD` gain
  - but still positive `Phi` gain

Boundary learned:

- the next honest step is to use these formulas in a structural proof of the
  widened tail controller, and then look for an amount law on `BFT`

### New survivor: bridge-fan-tail amount compiler law

Bounded and checked result:

- on the checked bridge-fan-tail strip:
  - `2 <= r <= 7`
  - `1 <= t <= 10`
- total-domination amount is determined exactly by:
  - base formulas:
    - `TD(BFT(r, 1)) = 7 * 2^(r + 2) - 7`
    - `TD(BFT(r, 2)) = 7 * 2^(r + 2)`
    - `TD(BFT(r, 3)) = 21 * 2^(r + 1) - 7`
    - `TD(BFT(r, 4)) = 21 * 2^(r + 2) - 21`
  - recurrence for `t >= 5`:
    - `TD(BFT(r, t)) = TD(BFT(r, t - 1)) + TD(BFT(r, t - 3)) + TD(BFT(r, t - 4))`
- claim tier:
  - `direct_amount_compiler`

Why it mattered:

- this is the first exact amount compiler on the feeder side
- the route no longer depends only on checked move laws, because the feeder
  quantities themselves now compress exactly

Boundary learned:

- the next honest step is to combine the feeder amount compiler with the
  downstream tail amount law and see whether the whole anomaly-side route has a
  single exact amount compiler

### New survivor: anomaly-route amount compiler law

Bounded and checked result:

- on the checked strip:
  - `2 <= r <= 7`
  - `1 <= t <= 10`
- define:
  - `Delta(r, t) = TD(star_{r + t + 6}) - TD(BFT(r, t))`
- exact base formulas:
  - `Delta(r, 1) = 9 * 2^(r + 2) + 6`
  - `Delta(r, 2) = 25 * 2^(r + 2) - 1`
  - `Delta(r, 3) = 107 * 2^(r + 1) + 6`
  - `Delta(r, 4) = 107 * 2^(r + 2) + 20`
- exact recurrence for `t >= 5`:
  - `Delta(r, t) = Delta(r, t - 1) + Delta(r, t - 3) + Delta(r, t - 4) + 5 * 2^(r + t + 1) + 2`
- claim tier:
  - `direct_amount_compiler`

Why it mattered:

- this is the first exact amount compiler for the whole anomaly-side route
- the route no longer appears only as:
  - one feeder amount compiler
  - plus one tail amount compiler
- it also has one direct deficit compiler from source family coordinates alone

Boundary learned:

- the next honest step is structural proof of the whole-route compiler
- this is close to a new tutorial threshold, but the proof step is still the
  cleaner breakpoint

### New survivor: anomaly-route Fibonacci-periodic decomposition

Bounded and checked result:

- on the bridge-fan-tail strip:
  - `2 <= r <= 7`
  - `1 <= t <= 10`
- feeder amount separates exactly into:
  - a Fibonacci channel
  - a period-4 channel
- exact formula:
  - `B(r, t) = A_r * F_t + B_r * F_{t + 1} + C_r * cos(pi t / 2) + A_r * sin(pi t / 2)`
- exact coefficients:
  - `A_r = (14 / 5) * (3 * 2^r - 1)`
  - `B_r = (7 / 5) * (8 * 2^r - 1)`
  - `C_r = (14 / 5) * (2^r - 2)`
- whole-route deficit becomes:
  - `Delta(r, t) = 2^(r + t + 5) - 1 - B(r, t)`
- the inhomogeneous forcing term from `v277` is exactly the residue of the star
  sequence against the feeder recurrence:
  - `5 * 2^(r + t + 1) + 2`
- claim tier:
  - `direct_amount_compiler`

Why it mattered:

- this is the first decomposition on the anomaly route that exposes mechanism
  instead of only recurrence shape
- the whole route now separates into:
  - a universal exponential target term
  - minus a Fibonacci-periodic feeder term

Boundary learned:

- this is closer to a tutorial breakpoint than the earlier recurrence-only
  result
- the clean next step is still a structural proof or conceptual derivation of
  the same decomposition

### New survivor: finite rewrite alphabet for the depth-2 tree controller

Bounded and checked result:

- on connected trees with:
  - `n in {8, 9}`
  - `m = n - 1`
- every move selected by the minimal-size one-branch hub-target depth-2
  controller belongs to one rooted template alphabet:
  - `leaf`
  - `cherry`
  - `three_leaf_star`
  - `broom_1`
  - `broom_2`
- rooted canonical codes:
  - `()`
  - `(()())`
  - `(()()())`
  - `((()()))`
  - `(((()())))`
- claim tier:
  - `descriptive_oracle`

Why it mattered:

- the tree-side controller is now more explicit than a raw depth cutoff
- the live local rewrite rule can be searched by finite template cases instead
  of arbitrary rooted subtrees

Boundary learned:

- the next honest step is a structural proof that those five templates are
  sufficient for the checked branch
