# Workflow Memory

## 2026-03-26

- Active frontier: Galoisized CEGIS, after the candidate-trajectory equality result.
- Strong correction learned: lattice CEGIS and BOC-max are best treated as one loop family in dual coordinates, not as two separate stronger algorithms.
- New cycle target: counterexample scheduling inside that loop family.
- Deeper correction learned during the cycle: the strongest bounded result was not verifier-side scheduling alone, it was proposer/verifier coupling through the same closure geometry.
- Bounded domain chosen:
  - exhaustive `3x3`, `3x4`, `4x4` boolean relations
  - random holdout `5x5`, `6x6`
- Required evidence:
  - exact dynamic-programming optimum on bounded domains
  - replayable scheduler comparison
  - explicit failure boundary when the strongest heuristic stops being exact

Next frontier after this cycle:

- understand why closure-gain is exact on `3x3` and `3x4`,
- characterize the `4x4` and `5x5` failure families under the coupled policy,
- test whether a slightly richer lookahead policy closes the remaining gap.

## 2026-03-26, second cycle

- New structural target: obligation-targeted witness routing.
- Strongest new compression:
  - the coupled closure policy can be written as an obligation controller plus a witness router.
- Why it matters:
  - it gives the existential engine a new role, not final-solution search but witness synthesis for targeted obligations.

Next frontier after v02:

- search for a stronger obligation-only controller that closes more of the `5x5` gap,
- test whether route-targeted witness synthesis gives a practical architecture for LLM plus formal-tool loops.

## 2026-03-26, third cycle

- New structural target: policy iteration over obligation-targeted witness routing.
- Strongest result:
  - `pi_2` reached exact bounded optimum on exhaustive `4x4`.
- This is the first candidate that looks like a proper loop law:
  - initialize with a geometry-guided controller,
  - evaluate it exactly on the bounded state space,
  - improve,
  - repeat.

Next frontier after v03:

- explain why two rounds were enough on `4x4`,
- test larger random domains,
- see whether the policy-improvement loop can be approximated by a learned value model without losing too much exactness.

## 2026-03-27, controller-language frontier

- New structural target: exact bounded symbolic controller compression beyond the `v10` two-clause language.
- Strongest bounded correction learned:
  - a single third tie-break clause can repair the remaining sampled larger-root residuals,
  - but within the tested family no such clause preserves every exhaustive reachable nonterminal `4x4` state of the exact bounded two-clause core.
- Bounded domain used:
  - exhaustive reachable nonterminal `4x4` states, `320927`
  - sampled `5x5` roots, seed `99`
  - sampled `6x6` roots, seed `123`

Next frontier after v11:

- richer controller languages, not another single local tie-break clause in the same family,
- short repair programs over clauses,
- or Bellman-derived guards that justify when a residual repair should fire.

## 2026-03-27, repair-program synthesis frontier

- New structural target: synthesize a short repair program over the tie-break clause language, rather than one more local clause.
- Strongest bounded result:
  - a banked CEGIS loop found a safe ordered clause pair after two exhaustive `4x4` counterexamples.
- Strongest correction learned:
  - safety alone is not enough,
  - the lexicographically simplest safe repair program generalized worse than the simpler `v10` two-clause language on larger sampled roots.

Next frontier after v12:

- add explicit larger-domain ranking or value objectives to the repair-program loop,
- separate safety synthesis from generalization selection,
- search for Bellman-derived guards or scores that rank safe repair programs without losing the exact bounded core.

## 2026-03-27, multi-proposer frontier

- New structural target: multiple proposers over the `v12` repair-program search, all sharing one bounded verifier and one counterexample bank.
- Strongest bounded result:
  - the best single proposer, `childsum`, finds a safe repair program in `2` exact verifier calls with bank size `1`
  - the best two-proposer portfolio needs `3` calls, `2` rounds, and bank size `2`
- Strongest correction learned:
  - proposer multiplicity alone does not dominate the best proposer
  - the real leverage is proposer diversity plus shared falsification

Next frontier after v13:

- portfolio selection by explicit value or holdout ranking, not just safe-pair discovery,
- obligation-partitioned proposer portfolios rather than generic ranking diversity,
- and MPRD-style scaling laws stated in terms of verified progress, not raw proposal count.

## 2026-03-27, bank-then-rank frontier

- New structural target: separate bounded safety synthesis from larger-domain value ranking.
- Strongest bounded result:
  - after the two-bank counterexample set from `v12`, the top holdout-ranked viable repair program was already safe on the exhaustive reachable nonterminal `4x4` verifier.
- Strongest correction learned:
  - once the bank is informative enough, the loop can factor into:
    - bank learning
    - value ranking over the viable frontier
    - one final exact safety check

Next frontier after v14:

- improve the bank itself, not only the ranking,
- test obligation-partitioned proposers that specialize in different fibers before the bank is complete,
- and see whether MPRD can exploit the same staged factorization.

## 2026-03-27, minimal-bank synthesis frontier

- New structural target: exact teaching-bank synthesis for the staged repair-program loop.
- Strongest bounded result:
  - after ranking all `7104` residual-consistent repair-program pairs by larger-domain score,
  - the first ranked pair was already safe on the exhaustive reachable nonterminal `4x4` verifier,
  - so the exact minimal teaching bank for the winner is `0`.
- Strongest correction learned:
  - the bank is not doing the work for the top winner in this bounded model
  - the stronger loop shape is:
    - form residual-consistent frontier
    - rank it
    - certify the top candidate

Next frontier after v15:

- test whether banks matter for:
  - top-`k` safe value, not only top-`1`
  - alternative objectives besides the current holdout score
  - or proposer specialization before residual consistency is enforced
- proceed to obligation-fiber proposer specialization

## 2026-03-27, obligation-fiber proposer frontier

- New structural target: obligation-fiber proposer specialization after the `v15` top-`1` collapse.
- Strongest bounded result:
  - no specialized proposer can strictly improve top-`1` exact-safe discovery, because the global frontier already returns a safe winner at call `1`.
- Strongest correction learned:
  - specialization has no remaining leverage on this objective in the current bounded model.

Next frontier after v16:

- move the leverage question from proposer specialization to certificate objects,
- ask whether the winning safe repair program admits a small exact certificate language

## 2026-03-27, winner-certificate language frontier

- New structural target: exact winner certificate search over the residual-consistent frontier.
- Strongest bounded result:
  - the winning safe repair program is not isolated by any conjunction of at most `5` atomic winner-features
  - there exist exact isolating certificates of size `6`
- Strongest correction learned:
  - the loop can end in a compact winner certificate, not only in a safe winner

Next frontier after v17:

- move from winner certificates to region certificates,
- search certificate languages that capture classes of safe repair programs rather than a single winner

## 2026-03-27, safe-region certificate frontier

- New structural target: exact region certificates over the residual-consistent repair-program frontier.
- Strongest bounded result:
  - there are size-`1` safe-region certificates,
  - each certifies the full `288`-pair safe top block with zero unsafe spillover.
- Strongest correction learned:
  - safe region certification is much simpler than winner isolation.

Next frontier after v18:

- explain the coincidence between the top-score block and the safe set,
- search for certificate languages for lower-ranked safe strata,
- or lift the same region-certificate idea into MPRD-style policy spaces

## 2026-03-27, score-safety collapse frontier

- New structural target: exact scalar-block explanation of the safe region.
- Strongest bounded result:
  - safety coincides exactly with the maximal sampled score block.
- Strongest correction learned:
  - the safe top region is not only certificate-simple,
  - it is exactly the argmax set of the sampled score coordinates in this bounded model.

Next frontier after v19:

- explain why the score collapse happens,
- or search the next lower unsafe stratum for a comparably simple anti-certificate

## 2026-03-27, score-block staircase frontier

- New structural target: lower-stratum anti-certificates after the scalar safety collapse.
- Strongest bounded result:
  - every score block is pure,
  - and every lower block has a single shared first refuter.
- Strongest correction learned:
  - the frontier is not merely safe-top versus unsafe-rest,
  - it is a staircase of pure blocks.

Next frontier after v20:

- explain the staircase from the controller language or verifier geometry,
- or test whether the same staircase law survives in a larger bounded family

## 2026-03-27, scalar refuter quotient frontier

- New structural target: exact quotient coordinates for the full first-refuter partition.
- Strongest bounded result:
  - `holdout_total` and `holdout_5_hits` are exact quotient coordinates,
  - `holdout_6_hits` is not.
- Strongest correction learned:
  - the scalar collapse is coordinate-sensitive,
  - but stronger than the earlier safety-only collapse because it carries the entire refuter label.

Next frontier after v21:

- explain why `holdout_total` and `holdout_5_hits` are sufficient while `holdout_6_hits` fails,
- or search for the smallest multi-coordinate quotient that repairs the `holdout_6_hits` exception

## 2026-03-27, arithmetic refuter logic frontier

- New structural target: exact arithmetic decision lists for the four first-refuter labels.
- Strongest bounded result:
  - `holdout_total` admits an exact length-`3` decision list:
    - `T > 3796 -> safe`
    - `T > 3775 -> fail_13116`
    - `T ≡ 3 (mod 23) -> fail_1915`
    - `else -> fail_828`
  - `holdout_5_hits` admits an exact length-`3` decision list:
    - `H5 > 2927 -> safe`
    - `H5 > 2910 -> fail_13116`
    - `H5 ≡ 3 (mod 17) -> fail_1915`
    - `else -> fail_828`
- Strongest correction learned:
  - the scalar quotient is not only descriptive,
  - it has a small arithmetic presentation on the two expressive coordinates,
  - while `holdout_6_hits` still fails because the bucket `859` is mixed.

Next frontier after v22:

- explain where the moduli `23` and `17` come from,
- search the smallest second coordinate that repairs the `holdout_6_hits = 859` collision,
- or derive the same arithmetic law from the verifier-side block geometry instead of discovering it by search.

## 2026-03-27, mixed-bucket repair frontier

- New structural target: repair the only mixed scalar obstruction left on the `holdout_6_hits` side.
- Strongest bounded result:
  - the mixed bucket `holdout_6_hits = 859` is repaired by exactly one feature in the searched simple feature library:
    - `E(x) := p1_4(x) = p2_4(x)`
  - the pair `(holdout_6_hits, E)` is an exact quotient for the full refuter partition.
- Strongest correction learned:
  - the obstruction was local,
  - and one tiny repair bit was enough to restore exactness.

Next frontier after v23:

- compile the repaired quotient into the smallest exact verifier logic,
- then ask whether the compiled verifier is small enough to justify a standalone verifier-compiler tutorial.

## 2026-03-27, repaired verifier compiler frontier

- New structural target: compile the repaired `(holdout_6_hits, E)` quotient into a minimal exact decision list.
- Strongest bounded result:
  - the repaired quotient has `10` reachable states,
  - and it compiles to an exact bounded decision list with `4` guards:
    - `H6 = 859 ∧ E = False -> fail_1915`
    - `H6 = 865 -> fail_1915`
    - `H6 = 869 -> fail_13116`
    - `H6 > 869 -> safe`
    - `else -> fail_828`
- Strongest correction learned:
  - the repaired verifier is not just exact,
  - it is compiler-small.

Next frontier after v24:

- explain why this particular repaired verifier logic is minimal in a more conceptual way,
- or lift the same verifier-compiler pattern into an MPRD-shaped policy loop.

## 2026-03-27, verifier compiler lower-bound frontier

- New structural target: certify that the repaired verifier compiler is minimal in the bounded guard language.
- Strongest bounded result:
  - no exact decision list with `3` guards or fewer exists for the repaired `(H6, E)` quotient
  - the lower-bound witness is structural:
    - `safe` has only a singleton pure branch
    - `fail_13116` has only a singleton pure branch
    - the two `fail_1915` states require two distinct singleton pure branches
- Strongest correction learned:
  - the `4`-guard compiler from `v24` is not just best found,
  - it is minimal in the searched bounded language.

Next frontier after v25:

- lift the verifier-compiler pattern into an MPRD-shaped bounded policy loop,
- or turn the quotient-and-repair compiler pattern into its own standalone tutorial and demo.

## 2026-03-27, MPRD transfer boundary frontier

- New structural target: test whether the quotient-and-repair verifier-compiler pattern transfers cheaply to a small MPRD-shaped policy family.
- Strongest bounded result:
  - in the toy lab-followup controller family, the residual-consistent unique-behavior frontier has:
    - `5283` unique behaviors
    - `164` viable behaviors after the 3-state training set
  - the first-refuter partition does not collapse to:
    - `holdout score + 1` simple behavior feature
    - `holdout score + 2` simple behavior features
    - `holdout score + 3` simple behavior features
  - the first exact repair in the searched library appears at `4` predicted-action features.
- Strongest correction learned:
  - the verifier-compiler pattern transfers, but not cheaply by default,
  - so transfer needs its own evidence discipline.

Next frontier after v26:

- search smaller or more semantically structured feature families for the MPRD transfer case,
- or promote the verifier-compiler loop into its own standalone tutorial with explicit positive and negative boundaries.

## 2026-03-27, MPRD semantic repair frontier

- New structural target: replace raw predicted-action repair features with semantically meaningful features in the toy MPRD transfer case.
- Strongest bounded result:
  - no exact semantic repair exists with `1`, `2`, or `3` features
  - the first exact semantic repair appears at `4` mistake-indicator bits:
    - `err[(0, 0, 1)]`
    - `err[(0, 1, 0)]`
    - `err[(0, 1, 1)]`
    - `err[(1, 1, 0)]`
- Strongest correction learned:
  - the MPRD transfer boundary is not just opaque feature pressure,
  - it has an interpretable semantic repair basis.

Next frontier after v27:

- ask whether those four mistake bits admit a smaller semantic quotient,
- or promote the verifier-compiler loop into a standalone tutorial that includes:
  - the exact compiler
  - the exact lower bound
  - the cheap-transfer failure
  - the semantic repair basis

## 2026-03-27, earliest-error compiler frontier

- New structural target: compress the MPRD semantic repair basis into an exact symbolic law.
- Strongest bounded result:
  - in the toy MPRD lab-followup transfer case, the first-refuter label is exactly the earliest holdout error in the fixed holdout order
  - `holdout score + any 4 of the 5 ordered error bits` is exact
  - every searched `holdout score + 3-bit` subbasis fails
- Strongest correction learned:
  - the MPRD transfer case does admit an exact semantic compiler law,
  - but it is a higher-dimensional earliest-error object than the earlier abstract verifier quotient.

Next frontier after v28:

- decide whether the verifier-compiler loop should now become its own standalone tutorial,
- or search for a second MPRD-shaped bounded domain to see whether the earliest-error law generalizes.

## 2026-03-27, monotone refill transfer frontier

- New structural target: test a second MPRD-shaped domain with a more monotone refill policy shape.
- Strongest bounded result:
  - in the searched monotone refill-style controller family:
    - `14` guards
    - `1640` unique behaviors
    - `130` residual-consistent viable behaviors
  - no exact semantic repair exists with `5` holdout error bits or fewer
  - the first exact semantic basis in the searched library appears at `6` holdout error bits
- Strongest correction learned:
  - transfer cost varies sharply by policy shape,
  - and some MPRD-like domains are much less compressible than the abstract verifier frontier.

Next frontier after v29:

- stop discovery and write the standalone verifier-compiler tutorial,
- or search one last domain-shaped feature family for the monotone refill case.

## 2026-03-27, horn-closed refill basis frontier

- New structural target: test whether the exact 6-bit monotone refill basis from `v29` can shrink once exact single- and pair-Horn implications among the 13 holdout error bits are allowed.
- Strongest bounded result:
  - the `v29` basis `{3,6,8,9,10,12}` remains minimal under the searched Horn closure library
  - its Horn closure expands to `11` of the `13` error bits
  - the only non-derivable bits are `5` and `11`
  - no basis of size `5` or less is exact
- Strongest correction learned:
  - semantic redundancy and logical derivability are not the same thing in this transfer case,
  - and Horn closure does not collapse the refill frontier below the 6-bit basis.

Next frontier after v30:

- explain whether the 6 retained bits are all essential,
- and clarify whether the two non-derivable bits matter for exact first-refuter classification or are only logically independent.

## 2026-03-27, irredundant refill Horn basis frontier

- New structural target: test whether the Horn-closed 6-bit refill basis is irredundant.
- Strongest bounded result:
  - the Horn-closed basis `B = {3,6,8,9,10,12}` remains exact
  - dropping any one retained bit makes the classifier inexact
  - the first mixed buckets after dropping each bit appear at hold scores:
    - drop `3` -> score `7`
    - drop `6` -> score `8`
    - drop `8` -> score `7`
    - drop `9` -> score `10`
    - drop `10` -> score `11`
    - drop `12` -> score `8`
  - adding either non-derivable bit `5` or `11` keeps the classifier exact but only splits already-pure buckets
- Strongest correction learned:
  - the monotone refill frontier has a real logic distinction between:
    - essential basis bits,
    - and independent but label-unnecessary bits.

Next frontier after v31:

- explain this as a formula-level law inside the tutorial,
- or stop the discovery loop and promote the verifier-compiler pattern with its positive and negative transfer boundaries.

## 2026-03-27, ordered refill basis compiler frontier

- New structural target: test whether the six essential refill basis bits admit an ordered active-prefix compiler law.
- Strongest bounded result:
  - let `B = {3,6,8,9,10,12}`
  - no order on `B` is exact when only the first `3` active bits are kept
  - some orders are exact when the first `4` active bits are kept, `504 / 720`
  - every order is exact when the first `5` active bits are kept, `720 / 720`
  - the best `k=3` order misses exactness by only one bad bucket
- Strongest correction learned:
  - the hard refill domain still admits an ordered compiler law,
  - but it is a deeper one than the earlier earliest-error compiler.

Next frontier after v32:

- explain why `k=5` is order-invariant while `k=4` is order-sensitive,
- or stop the search and promote the verifier-compiler tutorial with this stronger transfer-side compiler law included.

## 2026-03-27, k4 refill order law frontier

- New structural target: find an exact criterion for which `k=4` orders are exact in the monotone refill ordered-basis compiler from `v32`.
- Strongest bounded result:
  - let `B = {3,6,8,9,10,12}` and let `F4(σ)` be the first four positions of order `σ`
  - `Exact_4(σ)` holds iff:
    - `3 ∈ F4(σ)` and `F4(σ)` contains at least one of `{6,8}`, or
    - `3 ∉ F4(σ)`, both `6` and `8` lie in `F4(σ)`, and `3` appears before the unique omitted bit from `{9,10,12}`
  - this law matches all `720` orders exactly
- Strongest correction learned:
  - the `k=4` order-sensitivity is not accidental,
  - it has a clean structural criterion.

Next frontier after v33:

- stop the search and write the standalone verifier-compiler tutorial,
- or extract the same kind of exact order law in another transfer family before promoting it as a broader pattern.

## 2026-03-27, regional refill ladder frontier

- New structural target: test whether the hard monotone refill transfer domain admits a nonuniform explanatory ladder rather than one global explanation depth.
- Strongest bounded result:
  - with shared order `(3,6,8,9,10,12)`, the best exact regional ladder uses local depths:
    - scores `0..6` -> `0`
    - score `7` -> `2`
    - score `8` -> `3`
    - score `9` -> `4`
    - scores `10,11,12` -> `1`
  - weighted online cost is `118`
  - average depth is `118 / 130`
  - maximum depth is `4`
  - for comparison:
    - global exact `k=4` cost is `520`
    - global `k=5` cost is `650`
  - no exact regional ladder exists with maximum depth `3`
- Strongest correction learned:
  - the hard transfer domain does not need one global language depth everywhere,
  - and the explanatory-ladder idea has now survived as a bounded exact object.

Next frontier after v34:

- test whether the same ladder idea transfers to another bounded family,
- or begin the next loop tier, witness-language discovery, on one of the existing bounded frontiers.

## 2026-03-27, mixed-sign label language frontier

- New structural target: test a first bounded dual-language idea on the repaired verifier frontier, allowing some labels to be certified positively while one label is left as the default residual class.
- Strongest bounded result:
  - smallest exact all-positive certificate language uses `7` pure guards:
    - `safe` -> `1`
    - `fail_13116` -> `1`
    - `fail_1915` -> `2`
    - `fail_828` -> `3`
  - smallest exact mixed-sign language uses only `4` guards:
    - `safe` -> `H6 > 869`
    - `fail_13116` -> `H6 = 869`
    - `fail_1915` -> `H6 = 859 and E = False`, `H6 = 865`
    - default residual class -> `fail_828`
- Strongest correction learned:
  - the first bounded dual-language evidence is real:
  - some labels are cheapest to explain positively,
  - and another is cheapest as a negative or default residual class.

Next frontier after v35:

- search a true witness-language discovery loop on a harder bounded family,
- or try a richer dual-language search where the negative side also has explicit refuter objects rather than only a default residual class.

## 2026-03-27, primitive-invention label frontier

- New structural target: test whether bounded primitive invention can improve the all-positive exact label language on the repaired verifier frontier.
- Strongest bounded result:
  - baseline all-positive exact language cost is `7`
  - one invented primitive lowers cost to `5`:
    - new `fail_828` primitive:
      - `E = True OR H6 = 858 OR H6 = 864`
  - two invented primitives lower cost to `4`, matching the best mixed-sign language from `v35`:
    - new `fail_1915` primitive:
      - `H6 = 859 and E = False OR H6 = 865`
    - new `fail_828` primitive:
      - `E = True OR H6 = 858 OR H6 = 864`
- Strongest correction learned:
  - the mixed-sign advantage from `v35` is not fundamental on this bounded frontier,
  - because exact concept invention can recover the same cost inside an all-positive language.

Next frontier after v36:

- move from bounded primitive invention to a genuine witness-language discovery loop on a harder frontier,
- or search for the smallest negative refuter objects that pair with the new invented positive primitives.

## 2026-03-27, refill concept-market frontier

- New structural target: test whether a single invented pure concept can improve the exact explanatory ladder on the hard monotone refill transfer frontier from `v34`.
- Searched grammars:
  - fixed-order insertion:
    - keep the exact order `(3,6,8,9,10,12)`
    - insert one pure `AND` or `OR` primitive over `2` or `3` basis bits
    - re-optimize local ladder depths exactly
  - replacement:
    - replace the source basis bits by one pure `AND` or `OR` primitive over `2` or `3` basis bits
    - allow full reordering of the new feature language
- Strongest bounded result:
  - baseline exact ladder from `v34`:
    - weighted cost `118`
    - maximum depth `4`
  - best fixed-order insertion:
    - primitive `err[10] AND err[12]`
    - inserted before `err[10]`
    - weighted cost `90`
    - maximum depth `3`
    - local depths:
      - scores `0..6` -> `0`
      - score `7` -> `2`
      - score `8` -> `2`
      - score `9` -> `3`
      - scores `10,11,12` -> `1`
  - replacement boundary:
    - searched `70` primitive languages
    - searched `4560` reordered ladders
    - exact count `0`
- Strongest correction learned:
  - hard-frontier concept invention is real, but it behaves like a shortcut layer on top of the old basis
  - the same searched concepts fail completely when forced to replace the hard refill basis

Next frontier after v37:

- search whether two invented hard-frontier concepts can lower the ladder again,
- or move to a stronger witness-language discovery cycle beyond single-concept shortcut search.

## 2026-03-27, refill two-concept ladder frontier

- New structural target: test whether two inserted pure shortcut concepts can improve the exact hard refill ladder from `v37`.
- Searched grammar:
  - keep the exact base order `(3,6,8,9,10,12)`
  - insert two distinct pure `AND` or `OR` primitives over `2` or `3` basis bits
  - allow arbitrary insertion positions
  - re-optimize local ladder depths exactly
- Strongest bounded result:
  - searched candidate count `135240`
  - best exact pair:
    - `err[6] AND err[10] AND err[12]` at position `0`
    - `err[9] AND err[10] AND err[12]` at position `2`
  - best order:
    - `err[6] AND err[10] AND err[12]`
    - `err[3]`
    - `err[9] AND err[10] AND err[12]`
    - `err[6]`
    - `err[8]`
    - `err[9]`
    - `err[10]`
    - `err[12]`
  - weighted cost `80`
  - maximum depth `2`
  - local depths:
    - scores `0..6` -> `0`
    - scores `7,8,9` -> `2`
    - scores `10,11,12` -> `1`
  - no exact pair in the searched grammar reaches maximum depth `1`
- Strongest correction learned:
  - hard-frontier shortcut concepts can stack
  - but the surviving evidence is still additive layering on top of the old basis, not a smaller replacement language

Next frontier after v38:

- test whether a third shortcut breaks the max-depth-2 barrier,
- or stop local concept search and move up to witness-language discovery.

## 2026-03-27, anchored third-shortcut boundary frontier

- New structural target: test whether a third pure shortcut concept can improve the exact hard refill ladder once the best exact two-shortcut pair from `v38` is fixed.
- Searched grammar:
  - keep the exact `v38` pair fixed
  - insert one additional pure `AND` or `OR` primitive over `2` or `3` basis bits
  - allow arbitrary insertion position
  - re-optimize local ladder depths exactly
- Strongest bounded result:
  - baseline fixed pair:
    - weighted cost `80`
    - max depth `2`
    - bucket total `51`
  - searched candidate count `612`
  - no searched third shortcut lowers weighted cost below `80`
  - no searched third shortcut lowers max depth below `2`
  - best searched extra shortcut:
    - `err[3] OR err[6] OR err[8]`
    - inserted at position `6`
    - weighted cost `80`
    - max depth `2`
    - bucket total `48`
- Strongest correction learned:
  - the verified two-shortcut ladder is locally saturated on the main cost and depth metrics under one more simple pure shortcut
  - further local concept search may still improve internal bucket compression, but not the main ladder frontier in the searched anchored grammar

Next frontier after v39:

- either launch a global three-shortcut search instead of the anchored one,
- or stop local shortcut search and move up to witness-language discovery.

## 2026-03-27, score-local witness frontier with residual defaults

- New structural target: move from shortcut tuning to witness-language discovery on the hard refill frontier by fixing the exact `v38` feature space and searching score-local witness languages.
- Feature language:
  - `err[6] AND err[10] AND err[12]`
  - `err[3]`
  - `err[9] AND err[10] AND err[12]`
  - `err[6]`
  - `err[8]`
  - `err[9]`
  - `err[10]`
  - `err[12]`
- Witness atom grammar:
  - conjunctions of `1` to `3` signed literals over those `8` features
- Strongest bounded result:
  - nontrivial score blocks:
    - `7, 8, 9, 10, 11, 12`
  - every nontrivial score block admits an exact positive-cover plus residual-default witness language
  - total positive-cover-plus-residual cost across those six blocks is `27`
  - exact all-positive witness languages fail on:
    - score `9`
    - score `10`
- Strongest correction learned:
  - once the local shortcut line saturates, positive-cover plus residual-default witness-language discovery still yields exact structure
  - the next level is genuinely different from one more shortcut search

Next frontier after v40:

- lift from score-local witness languages to a more global witness-language discovery cycle,
- or test whether a global three-shortcut search is still worth the extra cost.

## 2026-03-27, global witness-schema frontier

- New structural target: turn the score-local positive-cover plus residual-default witness result from `v40` into a genuinely global witness-language object.
- Same bounded domain as `v40`:
  - same `130` residual-consistent viable behaviors
  - same `v38` feature language with `8` features
  - same witness-atom grammar:
    - conjunctions of `1` to `3` signed literals
- Strongest bounded result:
  - score-local positive-cover-plus-residual total cost remains `27`
  - among all exact score-local positive-cover plus residual-default witness languages that keep those local costs, the best shared global library uses only `20` distinct witness schemas
- Strongest correction learned:
  - the witness-language line now has a real global reusable schema layer
  - this is stronger than six unrelated local covers

Next frontier after v41:

- search for a still smaller global witness language by allowing richer atoms or score abstractions,
- or compare this witness-schema layer directly against a global three-shortcut search.

## 2026-03-27, score-abstraction witness frontier

- New structural target: search for an exact score abstraction above the score-local positive-cover plus residual-default witness languages from `v40`.
- Search space:
  - all contiguous partitions of the nontrivial scores:
    - `7, 8, 9, 10, 11, 12`
  - same witness-atom grammar as `v40` and `v41`
- Strongest bounded result:
  - only two contiguous partitions are exact:
    - the original `6`-region score-local partition
    - one coarser `5`-region partition
  - best exact partition:
    - `(7)`, `(8)`, `(9)`, `(10,11)`, `(12)`
  - total positive-cover-plus-residual witness cost drops:
    - from `27`
    - to `23`
- Strongest correction learned:
  - the witness-language line now compresses not only across shared schemas, but also across score blocks

Next frontier after v42:

- allow richer witness atoms or non-contiguous score abstractions and ask whether the witness cost drops again,
- or compare the witness-language line directly against a global three-shortcut concept search.

## 2026-03-27, unconstrained score-abstraction boundary frontier

- New structural target: test whether the `v42` score-abstraction result was only caused by the contiguity restriction.
- Search space:
  - all `203` set partitions of the six nontrivial scores:
    - `7, 8, 9, 10, 11, 12`
  - same exact positive-cover plus residual-default witness grammar as `v40` to `v42`
- Strongest bounded result:
  - only `10` of the `203` set partitions are exact
  - the same partition from `v42` remains optimal:
    - `(7)`, `(8)`, `(9)`, `(10,11)`, `(12)`
  - best total witness cost remains `23`
- Strongest correction learned:
  - contiguity was not the binding restriction in `v42`
  - the current score abstraction is robust in the larger bounded partition space

Next frontier after v43:

- allow richer witness atoms and ask whether witness cost can drop below `23`,
- or compare the witness-language line directly against a global three-shortcut concept search.

## 2026-03-27, richer witness-grammar frontier

- New structural target: keep the `v43` score-partition search fixed and test whether a richer witness-atom grammar changes the best exact hard-frontier witness object.
- Search space:
  - all `203` set partitions of:
    - `7, 8, 9, 10, 11, 12`
  - richer witness-atom grammar:
    - conjunctions of `1` to `4` signed literals over the same `8` features
- Strongest bounded result:
  - feasible partition count rises:
    - from `10`
    - to `15`
  - the same best partition remains optimal:
    - `(7)`, `(8)`, `(9)`, `(10,11)`, `(12)`
  - best total positive-cover-plus-residual witness cost drops:
    - from `23`
    - to `22`
  - the gain comes from a new exact pure atom in score `9`:
    - `not err[3] and not err[6] and not err[8] and err[10]`
- Strongest correction learned:
  - the score-partition side was saturated by `v43`
  - the witness grammar itself was not

Next frontier after v44:

- test whether a still richer witness grammar lowers cost again or only increases the exact feasible set,
- or move up from score abstractions into a more global witness-language synthesis cycle.

## 2026-03-27, five-literal witness-grammar boundary frontier

- New structural target: test whether the live grammar axis from `v44` keeps improving when the atom grammar grows from conjunctions of `1..4` to conjunctions of `1..5` signed literals.
- Search space:
  - same `203` unconstrained set partitions of:
    - `7, 8, 9, 10, 11, 12`
  - compare the exact `1..4` and `1..5` witness grammars on the same bounded family
- Strongest bounded result:
  - feasible partition count stays:
    - `15`
  - best partition stays:
    - `(7)`, `(8)`, `(9)`, `(10,11)`, `(12)`
  - best total positive-cover-plus-residual witness cost stays:
    - `22`
  - two non-best partitions improve by one unit each
- Strongest correction learned:
  - `v44` was a real gain, but the next literal does not improve the main exact object
  - the local grammar axis is now tight on its main metric

Next frontier after v45:

- move up to a more global witness-language synthesis cycle,
- or only revisit local grammars if a new objective makes the secondary partition changes matter.

## 2026-03-27, global witness-synthesis frontier

- New structural target: fix the exact `v44` partition and search for the smallest shared global witness-schema library above those exact local regions.
- Fixed partition:
  - `(7)`, `(8)`, `(9)`, `(10,11)`, `(12)`
- Same witness-atom grammar as `v44`:
  - conjunctions of `1` to `4` signed literals
- Strongest bounded result:
  - raw local region cost:
    - `22`
  - best shared global witness-schema count:
    - `19`
- Strongest correction learned:
  - the hard witness-language line now has a genuinely more global object above its best score abstraction
  - the next frontier is no longer just local atoms or local partitions

Next frontier after v46:

- search for a still smaller global schema library in a richer witness grammar,
- or move up another level and search for reusable witness templates across multiple bounded frontiers.

## 2026-03-27, global witness-synthesis grammar boundary frontier

- New structural target: test whether the more-global witness object from `v46` still improves when the atom grammar grows from conjunctions of `1..4` to conjunctions of `1..5` signed literals.
- Fixed partition:
  - `(7)`, `(8)`, `(9)`, `(10,11)`, `(12)`
- Strongest bounded result:
  - total region cost stays:
    - `22`
  - best shared global schema count stays:
    - `19`
- Strongest correction learned:
  - the more-global witness line is also tight on its main metric under one more literal
  - both nearby local axes are now closed enough to justify switching loop families

Next frontier after v47:

- move to a stronger loop family, such as witness-template discovery across multiple bounded frontiers,
- or search for a new abstraction that changes the global witness basis instead of only widening local literals.

## 2026-03-27, cross-frontier witness-template frontier

- New structural target: stop optimizing one frontier at a time and search for a smaller meta-language above multiple exact witness-schema frontiers.
- Source exact objects:
  - the exact global witness-schema library from `v41`
  - the exact global witness-schema library from `v46`
- Strongest bounded result:
  - raw formula union:
    - `22`
  - exact overlap:
    - `17`
  - untyped conjunction-shape templates:
    - `10`
  - typed templates, keeping feature kind:
    - `13`
- Strongest correction learned:
  - the next live compression axis is cross-frontier witness-template discovery
  - not one more literal or one more local partition tweak

Next frontier after v48:

- search for reusable witness templates across more than two exact frontiers,
- or switch to a stronger family such as certificate-language or explanation-fiber discovery if the template axis saturates too quickly.

## 2026-03-27, cross-frontier core-plus-patch frontier

- New structural target: refine the `v48` template result into a sharper compiler shape, shared exact core plus frontier-specific patches.
- Source exact objects:
  - the exact global witness-schema library from `v41`
  - the exact global witness-schema library from `v46`
- Strongest bounded result:
  - shared exact core:
    - `17`
  - `v41`-only patch schemas:
    - `3`
  - `v46`-only patch schemas:
    - `2`
  - residual patch union:
    - `5`
  - residual templates under the current conjunction-shape grammar:
    - `5`
- Strongest correction learned:
  - the stable meta-language is real
  - but the remaining novelty is already irreducible under the current syntax-only template grammar

Next frontier after v49:

- move to semantic patch languages,
- or jump to a stronger family such as certificate-language or explanation-fiber discovery.

## 2026-03-27, typed semantic-patch frontier

- New structural target: test whether the residual patch language from `v49` still compresses when the compiler is allowed to use typed edit signatures over the shared exact core.
- Model:
  - shared exact core from `v49`:
    - `17` formulas
  - residual patches from `v49`:
    - `5` formulas
  - each patch may attach to any shared-core formula
  - patch descriptions use typed literal edits by sign and feature kind
- Strongest bounded result:
  - nearest-core attachment yields:
    - `5` edit signatures for `5` patches
  - the searched typed edit model yields:
    - `4` typed edit signatures for those same `5` patches
  - best total edit cost:
    - `15`
- Strongest correction learned:
  - the residual patch language was irreducible only in the syntax-only template grammar
  - typed semantic-patch structure reopens compression on that residual

Next frontier after v50:

- test whether a still richer semantic patch language compresses further,
- or compare semantic patching directly against stronger families such as certificate-language or explanation-fiber discovery.

## 2026-03-27, semantic macro-family frontier

- New structural target: move from typed edit signatures to the smallest exact semantic macro-family subset over the shared exact core and the residual patch set.
- Candidate semantic macro families:
  - `ADD_LITERAL`
  - `DROP_LITERAL`
  - `FLIP_SIGN`
- Strongest bounded result:
  - all five residual patches are exactly scriptable using only:
    - `ADD_LITERAL`
    - `FLIP_SIGN`
  - no exact one-family solution exists
  - best total macro-instance count:
    - `11`
- Strongest correction learned:
  - the semantic patch line now has an exact two-family macro basis
  - this is stronger than the earlier typed-signature result

Next frontier after v51:

- test whether a richer semantic patch language lowers total macro-instance count below `11`,
- or compare this semantic patch basis directly against certificate-language and explanation-fiber families.

## 2026-03-27, bundle semantic-macro frontier

- New structural target: strengthen the exact semantic macro-family basis from `v51` by allowing bundled semantic macros.
- Candidate bundle-macro families:
  - `ADD_BUNDLE`
  - `DROP_BUNDLE`
  - `FLIP_BUNDLE`
- Strongest bounded result:
  - exact family subset:
    - `ADD_BUNDLE`
    - `FLIP_BUNDLE`
  - no exact one-family solution exists
  - best total macro-instance count:
    - `6`
  - this improves on `v51`:
    - `11 -> 6`
- Strongest correction learned:
  - the semantic patch line does not only survive, it sharpens under bundled macro semantics
  - bundled semantic macros are currently the strongest post-template object in the repo

Next frontier after v52:

- test whether an even richer semantic patch language compresses further,
- or compare bundled semantic macros directly against certificate-language and explanation-fiber families.

## 2026-03-27, semantic fiber decomposition frontier

- New structural target: move from one global bundled semantic basis to an explanation-fiber search on the residual patch language.
- Search space:
  - all `52` set partitions of the five residual patches
  - for each fiber, the smallest exact bundled family subset over:
    - `ADD_BUNDLE`
    - `DROP_BUNDLE`
    - `FLIP_BUNDLE`
- Strongest bounded result:
  - mixed patches:
    - `1`
  - mixed fibers:
    - `1`
  - total fibers:
    - `3`
  - best decomposition:
    - one pure `FLIP_BUNDLE` fiber covering `3` patches
    - one pure `ADD_BUNDLE` fiber covering `1` patch
    - one mixed `ADD_BUNDLE + DROP_BUNDLE` singleton fiber covering `1` patch
- Strongest correction learned:
  - explanation-fiber discovery now has a real bounded survivor in this line
  - the residual semantic language is almost fiber-pure under the searched bundled macro families

Next frontier after v53:

- test richer bundled macro languages to see whether the last mixed singleton disappears,
- or compare this explanation-fiber object directly against certificate-language discovery.

## 2026-03-27, fiber-certificate frontier

- New structural target: compare the exact `v53` explanation-fiber object against
  direct certificate-language discovery on the same bounded residual domain.
- Discovery features:
  - `has_add`
  - `has_drop`
  - `has_flip`
- Strongest bounded result:
  - smallest exact all-positive language cost:
    - `3`
  - smallest exact positive-cover plus residual-default language cost:
    - `2`
  - winning residual-default language:
    - certify `ADD_BUNDLE + DROP_BUNDLE` by `has_drop`
    - certify `FLIP_BUNDLE` by `has_flip`
    - default `ADD_BUNDLE`
- Strongest correction learned:
  - the exact `v53` fiber labels admit a smaller certificate presentation than
    the raw fiber decomposition itself
  - this remains a descriptive-oracle object, because the presentation still
    starts from the fiber labels

Next frontier after v54:

- remove dependence on the precomputed fiber labels,
- or compare certificates against a richer direct symbolic compiler.

## 2026-03-27, direct delta-certificate frontier

- New structural target: upgrade `v54` from a relabeling result to a direct
  symbolic-state compiler by deriving certificate features from raw
  `core -> patch` deltas.
- Direct symbolic features:
  - `has_add`
  - `has_drop`
  - `has_flip`
- Strongest bounded result:
  - smallest exact all-positive language cost:
    - `3`
  - smallest exact positive-cover plus residual-default language cost:
    - `2`
  - winning direct residual-default compiler:
    - certify `ADD_BUNDLE + DROP_BUNDLE` by `has_drop`
    - certify `FLIP_BUNDLE` by `has_flip`
    - default `ADD_BUNDLE`
- Strongest correction learned:
  - the same exact residual family split does not need the precomputed fiber
    labels as features
  - this upgrades the line from `descriptive_oracle` to
    `symbolic_state_compiler` on the bounded residual symbolic state

Next frontier after v55:

- test whether a richer direct delta language compresses further,
- or compare the direct delta compiler against certificate-language or
  explanation-fiber discovery on a larger residual family.

## 2026-03-27, direct delta basis frontier

- New structural target: minimize the exact feature basis needed by the `v55`
  direct symbolic residual-family compiler.
- Candidate direct features:
  - `has_add`
  - `has_drop`
  - `has_flip`
- Strongest bounded result:
  - smallest exact all-positive basis size:
    - `2`
  - smallest exact positive-cover plus residual-default basis size:
    - `2`
  - exact minimal bases:
    - `has_add`, `has_drop`
    - `has_drop`, `has_flip`
  - no singleton basis is exact
- Strongest correction learned:
  - the direct symbolic compiler sharpens again
  - `has_drop` is indispensable on this bounded residual domain, while the
    second coordinate can be either `has_add` or `has_flip`

Next frontier after v56:

- compare the two surviving minimal bases on a larger residual family,
- or search a richer direct delta language that distinguishes which second
  coordinate transfers better.

## 2026-03-27, raw edit-basis frontier

- New structural target: remove the aggregated direct delta coordinates and
  search for the smallest exact primitive edit basis for the same residual-family
  compiler.
- Primitive features observed in the bounded domain:
  - `add[3]`
  - `add[6]`
  - `add[8]`
  - `add[10]`
  - `drop[12]`
  - `flip[6]`
  - `flip[8]`
  - `flip[9]`
  - `flip[12]`
- Strongest bounded result:
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
- Strongest correction learned:
  - the direct symbolic compiler does not need the hand-aggregated semantic
    coordinates
  - the surviving primitive bases factor into one add-anchor and one
    mixed-patch discriminator

Next frontier after v57:

- compare the primitive-basis family against the aggregated-basis family on a
  larger residual set,
- or search whether richer raw primitive grammars collapse the six surviving
  bases to a smaller exact template family.

## 2026-03-27, primitive basis template frontier

- New structural target: compress the six exact raw primitive bases from `v57`
  into the smallest exact role-template family.
- Primitive features used by the exact basis family:
  - `add[3]`
  - `add[6]`
  - `add[8]`
  - `add[10]`
  - `drop[12]`
- Strongest bounded result:
  - the six all-positive primitive bases collapse exactly to one two-slot
    product template, unique up to slot swap
  - one slot:
    - `add[3]`, `add[6]`, `add[10]`
  - the other slot:
    - `add[8]`, `drop[12]`
  - the residual-default family is the same pair template crossed with all
    three default labels
- Strongest correction learned:
  - the raw primitive line is no longer only a six-basis atlas
  - it now has an exact role grammar: one add-anchor crossed with one
    mixed-patch discriminator

Next frontier after v58:

- compare the aggregated and primitive template families on a larger residual
  family,
- or search whether the add-anchor slot and mixed-patch slot themselves admit a
  smaller exact semantic explanation.

## 2026-03-27, role-slot compiler frontier

- New structural target: upgrade the exact `v58` role template from a
  descriptive basis grammar to a direct symbolic compiler over slot features.
- Search constraints:
  - reproduce exactly the six primitive bases from `v57`
  - and compile the residual labels directly
- Strongest bounded result:
  - surviving slot family is unique up to slot swap
  - slot `a`:
    - `add[3]`, `add[6]`, `add[10]`
  - slot `b`:
    - `add[8]`, `drop[12]`
  - exact all-positive label compiler:
    - `ADD_BUNDLE` by `slot_a and not slot_b`
    - `ADD_BUNDLE + DROP_BUNDLE` by `slot_b`
    - `FLIP_BUNDLE` by `not slot_a`
  - exact positive-cover plus residual-default cost:
    - `2`
- Strongest correction learned:
  - the role template is not only a descriptive grammar over bases
  - it is also a direct bounded symbolic compiler over two slot booleans

Next frontier after v59:

- compare the aggregated compiler and the slot compiler on a larger residual
  family,
- or search for a smaller exact semantic explanation of the two slots
  themselves.

## 2026-03-27, quotient boundary frontier

- New structural target: compare the smallest exact slot quotient for direct
  label compilation against the smallest exact slot quotient that also preserves
  the full primitive basis structure.
- Objective regimes:
  - `label_only`
  - `basis_faithful`
- Strongest bounded result:
  - smallest exact `label_only` slot cost:
    - `2`
  - smallest exact `basis_faithful` slot cost:
    - `5`
  - `label_only` optimum family:
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
- Strongest correction learned:
  - predictive compression is strictly cheaper than structure-preserving
    compression on this bounded residual family
  - there are now two different exact optimization targets in the same loop

Next frontier after v60:

- test whether this predictive-versus-structure boundary persists on a larger
  residual family,
- or search for a semantic explanation of why the add-anchor and mixed
  discriminator roles control both quotients.

## 2026-03-27, semantic slot frontier

- New structural target: explain the exact `v59` slot roles semantically on the
  smallest exact metadata basis.
- Primitive metadata features:
  - `is_add`
  - `is_drop`
  - `is_flip`
  - `has_AB`
  - `has_MIX`
  - `has_FLIP`
  - `count_1`
  - `count_2`
- Strongest bounded result:
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
- Strongest correction learned:
  - the recurring slot roles are not only structural or index-based
  - they admit a small exact semantic explanation in a support-profile language

Next frontier after v61:

- test whether the same support-profile semantics persist on a larger residual
  family,
- or compare this semantic explanation layer against a larger transfer domain.

## 2026-03-27, shared role semantics frontier

- New structural target: unify the exact `v59` structure-preserving slot roles
  and the exact `v60` minimal label-only quotient family under one shared
  semantic partition.
- Support-profile partition:
  - `ADD_ANCHOR` iff `has_AB`
  - `MIX_DISCRIM` iff `not has_AB and has_MIX`
  - `OTHER` iff `not has_MIX`
- Strongest bounded result:
  - this partition exactly matches the `v59` slot roles:
    - `ADD_ANCHOR = slot_a`
    - `MIX_DISCRIM = slot_b`
    - `OTHER = other`
  - the unordered minimal `label_only` quotients from `v60` are exactly the
    singleton cross product:
    - choose one primitive from `ADD_ANCHOR`
    - choose one primitive from `MIX_DISCRIM`
- Strongest correction learned:
  - the predictive and structure-preserving exact objectives are governed by the
    same two-feature support-profile law
  - the branch now has a shared semantic control law, not only separate
    structural and predictive artifacts

Next frontier after v62:

- test whether the same shared support-profile law persists on a larger
  residual family,
- or compare it against a larger transfer domain.

## 2026-03-27, support-signature transfer frontier

- New structural target: test whether the support-profile law from `v62`
  transfers to a second exact frontier.
- Domain A:
  - roles:
    - `CORE`
    - `V41_PATCH`
    - `V46_PATCH`
  - support bits:
    - `has_v41`
    - `has_v46`
- Domain B:
  - roles:
    - `ADD_ANCHOR`
    - `MIX_DISCRIM`
    - `OTHER`
  - support bits:
    - `has_AB`
    - `has_MIX`
- Strongest bounded result:
  - both domains compile exactly by two-bit support signatures
  - Domain A:
    - `CORE` by `has_v41 and has_v46`
    - `V41_PATCH` by `not has_v46`
    - `V46_PATCH` by `not has_v41`
  - Domain B:
    - `ADD_ANCHOR` by `has_AB`
    - `MIX_DISCRIM` by `not has_AB and has_MIX`
    - `OTHER` by `not has_MIX`
- Strongest correction learned:
  - the support-profile law from `v62` is not isolated
  - it transfers to a second exact frontier as a generic support-signature role
    law

Next frontier after v63:

- test whether the same support-signature law persists on a larger residual
  family or transfer domain,
- or search for a loop that directly discovers support-signature laws across
  frontiers.

## 2026-03-27, support-literal compiler frontier

- New structural target: test whether the `v63` support-signature law upgrades
  from a descriptive transfer result to a tiny exact compiler family.
- Bounded domains:
  - Domain A:
    - `v49` cross-frontier schema roles
    - support bits `has_v41`, `has_v46`
  - Domain B:
    - `v62` residual primitive roles
    - support bits `has_AB`, `has_MIX`
  - Domain C:
    - `v55` direct patch-delta roles
    - support bits `has_add`, `has_drop`, `has_flip`
- Strongest bounded result:
  - all three domains have no exact single-branch support compiler
  - all three domains admit an exact residual-default support compiler with:
    - branch count `2`
    - total literal cost `2`
  - preferred compilers:
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
- Strongest correction learned:
  - the support-signature branch is no longer only descriptive
  - it now has a tiny exact support-literal compiler family across three
    bounded frontiers

Next frontier after v64:

- test whether the same support-literal family survives on a larger transfer
  domain with a compatible support surface,
- or search for a loop that discovers support-literal compilers directly from
  role tables rather than after manual frontier selection.

## 2026-03-27, three-signature support law frontier

- New structural target: test whether the `v64` support-literal family is only
  a three-domain pattern, or a generic law of small support tables.
- Abstract bounded family:
  - labeled `3`-role support tables
  - one distinct realized support signature per role
  - widths `2` through `7`
- Strongest bounded result:
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
  - the three live support domains from `v64` instantiate the same law
- Strongest correction learned:
  - the support-literal line is stronger than a transferred family pattern
  - it is now a bounded support-table law candidate for the full `3`-role case

Next frontier after v65:

- move from `3` roles to the first `4`-role support-table failure family,
- or search whether a comparably small exact law exists for `4`-role support
  tables before the first obstruction appears.

## 2026-03-27, four-role support cost frontier

- New structural target: push past the `v65` three-role support law and find
  the first exact compiler-cost ladder for `4`-role support tables.
- Abstract bounded family:
  - labeled `4`-role support tables
  - one distinct realized support signature per role
  - widths `2` and `3`
  - residual-default support compilers with one branch per non-default role
- Strongest bounded result:
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
- Strongest correction learned:
  - the `3`-role support law fails immediately for `4` roles
  - what replaces it is an exact bounded cost ladder, not another uniform cheap
    law

Next frontier after v66:

- classify the width-`3` ladder geometrically,
- or move to width `4` and search for the first new cost beyond `6`.

## 2026-03-27, width3 four-role geometry frontier

- New structural target: explain the `v66` width-`3` `4`-role cost ladder
  geometrically by quotienting `4`-subsets of the cube by automorphisms.
- Abstract bounded family:
  - labeled `4`-role support tables
  - one distinct realized support signature per role
  - width `3`
  - quotient by cube automorphisms on unlabeled `4`-subsets
- Strongest bounded result:
  - exactly `6` cube-orbit classes
  - every orbit has a uniform exact compiler cost
  - atlas:
    - `(0,1,2,4)`, claw, cost `3`
    - `(0,1,2,5)`, path, cost `4`
    - `(0,1,2,7)`, vee-plus-isolated, cost `5`
    - `(0,1,2,3)`, square, cost `6`
    - `(0,1,6,7)`, disjoint-edge, cost `6`
    - `(0,3,5,6)`, independent, cost `6`
- Strongest correction learned:
  - the width-`3` `4`-role frontier is not only a cost histogram
  - it is a small exact geometry atlas

Next frontier after v67:

- move to width `4` and search for the first new cost beyond `6`,
- or search for a formula that predicts the orbit cost directly from a small
  graph invariant family.

## 2026-03-27, width3 invariant law frontier

- New structural target: compress the `v67` six-orbit atlas into the smallest
  exact invariant law found in the searched invariant library.
- Bounded domain:
  - the exact six-orbit width-`3` atlas from `v67`
  - searched invariants:
    - `edge_count`
    - `max_degree`
    - `leaf_count`
    - `isolated_count`
    - `connected`
    - `component_sizes`
    - `degree_sequence`
- Strongest bounded result:
  - the full `degree_sequence` is already an exact singleton invariant
  - but among the searched scalar invariants, no singleton is exact
  - the simplest exact scalar basis found is:
    - `(edge_count, max_degree)`
  - exact cost law:
    - `(3,3) -> 3`
    - `(3,2) -> 4`
    - `(2,2) -> 5`
    - otherwise `-> 6`
- Strongest correction learned:
  - the width-`3` frontier does not only have an atlas
  - it also has a tiny exact scalar invariant law above that atlas

Next frontier after v68:

- move to width `4` and search for the first new cost beyond `6`,
- or test whether a similarly small scalar law survives there.

## 2026-03-27, width4 support-profile frontier

- New structural target:
  - compress the width-`4` `4`-role cost histogram into the smallest exact
    support-profile object.
- Bounded domain:
  - labeled `4`-role support tables
  - one realized support signature per role
  - all four signatures distinct
  - width `4`
- Per-role statistic:
  - minimal unique-support size, the fewest support bits needed to distinguish
    one realized role from the other three
- Strongest bounded result:
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
  - exact cost law:
    - cost `3` for the first three profiles
    - cost `4` for `(1,1,2,2)`
    - cost `5` for `(1,2,2,2)`
    - cost `6` for `(2,2,2,2)`
  - equivalently:
    - exact minimal cost = the sum of the three smallest profile entries
- Strongest correction learned:
  - the width-`4` frontier does not immediately become irregular
  - it already admits a small exact support-profile law

Next frontier after v69:

- search for the first profile or cost phenomenon beyond this six-profile law,
- or test whether a similarly small scalar or geometric law survives on the
  full width-`4` orbit space.

## 2026-03-27, width4 support-count and profile-pair frontier

- New structural target:
  - compress the exact six-profile width-`4` law from `v69` into the smallest
    searched scalar laws for:
    - exact cost
    - exact full profile reconstruction
- Input frontier:
  - the exact six-profile width-`4` support-profile object from `v69`
- Searched profile-derived feature library:
  - `count_private_roles`
  - `count_size2_roles`
  - `count_size3_roles`
  - `max_support_size`
  - `sum_support_sizes`
  - `sum_three_smallest`
  - `smallest_support_size`
- Strongest bounded results:
  - exact cost already collapses to one scalar:
    - `count_private_roles`
    - law:
      - `4 -> 3`
      - `3 -> 3`
      - `2 -> 4`
      - `1 -> 5`
      - `0 -> 6`
  - exact full profile reconstruction needs two scalars:
    - `count_private_roles`
    - `max_support_size`
- Strongest correction learned:
  - the width-`4` frontier is cleaner than the raw six-profile statement
  - exact cost and exact profile reconstruction separate into:
    - one-scalar control
    - two-scalar structure

Next frontier after v71:

- test whether the width-`4` orbit space admits a similarly small law above
  these support-count objects,
- or find the first width-`4` geometric obstruction not already captured by
  private-role count and maximal support size.

## 2026-03-27, width4 orbit support-count transfer frontier

- New structural target:
  - test whether the exact width-`4` support-count laws from `v70` and `v71`
    survive on the unlabeled orbit presentation
- Bounded domain:
  - unlabeled `4`-subsets of the `4`-cube
  - quotiented by cube automorphisms
  - exhaustive orbit count:
    - `19`
- Strongest bounded results:
  - exact orbit cost is still determined by one scalar:
    - `count_private_roles`
  - exact orbit profile is still reconstructed by the pair:
    - `count_private_roles`
    - `max_support_size`
- Strongest correction learned:
  - the width-`4` support-count line is not a one-presentation artifact
  - it survives unchanged across:
    - the labeled-table frontier
    - the unlabeled orbit frontier

Next frontier after v72:

- identify the first width-`4` geometric obstruction not already captured by
  the support-count laws,
- or test whether a still smaller orbit-side law exists above the current
  transfer object.

## 2026-03-27, width4 orbit mixed-basis and scalarized-law frontier

- New structural target:
  - isolate the first width-`4` orbit obstruction beyond the transferred
    support-count laws
  - then test whether that obstruction still collapses to a small scalar law
- Bounded domain:
  - the full width-`4` unlabeled orbit family, `19` orbits
- Strongest bounded results:
  - support counts alone do not determine orbit class
  - the first exact mixed bases are:
    - `count_private_roles` plus `distance_multiset`
    - `count_size2_roles` plus `distance_multiset`
  - inside the searched scalar support-plus-geometry library:
    - no singleton scalar is exact
    - no scalar pair is exact
    - exact scalar triples do exist
  - preferred exact triple:
    - `count_private_roles`
    - `max_degree`
    - `diameter`
- Strongest correction learned:
  - the first genuine width-`4` geometric obstruction is real
  - but it is still tiny:
    - one support-count coordinate plus one geometric multiset
    - or three scalar coordinates

Next frontier after v74:

- search for the first width-`4` phenomenon that escapes this mixed
  support-plus-geometry law,
- or determine whether the current three-scalar law is already minimal in a
  broader geometric feature library.

## 2026-03-27, width4 broad-scalar minimality and mixed-basis rigidity

- New structural target:
  - test whether the `v74` three-scalar law is still minimal in a much wider
    scalar support-plus-geometry library
  - then test whether the `v73` non-scalar mixed basis is one choice among many
    or rigid in a wider tuple-aware mixed library
- Bounded domain:
  - the full width-`4` unlabeled orbit family, `19` orbits
- Strongest bounded results:
  - widened scalar library size:
    - `21`
  - even there:
    - no singleton scalar is exact
    - no scalar pair is exact
    - exact scalar triples do exist
  - preferred exact triple remains:
    - `count_private_roles`
    - `max_degree`
    - `diameter`
  - widened mixed tuple-aware library:
    - the only nontrivial exact pair bases are:
      - `count_private_roles` plus `distance_multiset`
      - `count_size2_roles` plus `distance_multiset`
- Strongest correction learned:
  - the first width-`4` orbit obstruction is both:
    - scalar-minimal at size `3` in the broadened scalar library
    - unusually rigid in the searched mixed basis library

Next frontier after v76:

- search for the first width-`4` phenomenon that escapes both:
  - the current three-scalar law
  - the current rigid mixed basis family
- or prove stronger minimality inside an even wider geometric invariant library

## 2026-03-27, minimal witness-language phase diagram

- New structural target:
  - compare several exact language families side by side on one fixed repaired
    verifier frontier
  - ask for the smallest exact language once the local witness contract is
    fixed
- Bounded domain:
  - the repaired `10`-state `(H6, E)` verifier frontier from `v24`, `v35`, and
    `v36`
- Strongest bounded results:
  - exact compared families:
    - pure positive atom covers
    - mixed residual-default atom covers
    - invented positive covers
    - ordered decision-list compiler
  - smallest all-positive unordered language:
    - invented positive-cover family
    - cost `4`
  - smallest unordered residual-default language:
    - mixed atom-cover family
    - cost `4`
  - smallest ordered exact classifier:
    - decision-list compiler
    - guard count `4`
- Strongest correction learned:
  - on this bounded frontier, "best exact language" is not absolute
  - the optimum depends on what is allowed to count as a local witness
  - verifier compilation is therefore best read as one child of a larger
    `minimal witness-language discovery` program

Next frontier after v77:

- search directly over a larger bounded family of witness languages instead of
  only comparing known survivors,
- or repeat the same phase-diagram comparison on a harder frontier where the
  current exact families do not all tie at cost `4`

## 2026-03-27, hard witness-language phase diagram

- New structural target:
  - repeat the `v77` phase-diagram comparison on a harder bounded witness
    frontier where the exact families should separate instead of tie
- Bounded domain:
  - the hard refill witness frontier from `v40`, `v44`, and `v46`
  - same `13` holdout states
  - same `v38` feature surface
- Strongest bounded results:
  - score-local residual-default witnesses:
    - cost `27`
  - merged-region residual-default witnesses:
    - cost `22`
  - shared global witness-schema language:
    - size `19`
  - local all-positive witnesses already fail on:
    - `9`
    - `10`
- Strongest correction learned:
  - the harder frontier does not merely show several tied exact language
    families
  - it orders witness contracts strictly:
    - local
    - then merged-region
    - then shared-schema

Next frontier after v78:

- search directly over a wider bounded witness-language family on the same hard
  frontier,
- or compare witness-cover languages against certificate or decomposition
  languages on a shared bounded corpus

## 2026-03-27, hard decomposition-language boundary

- New structural target:
  - compare the current hard label-level witness language against an exact
    decomposition language on the same merged-region partition
- Bounded domain:
  - the hard merged-region witness frontier from `v44` and `v46`
  - same exact partition:
    - `(7)`
    - `(8)`
    - `(9)`
    - `(10,11)`
    - `(12)`
- Strongest bounded results:
  - exact bit-fiber decomposition exists
  - but it is strictly worse than the current label-level witness language:
    - bit-fiber total cost:
      - `24`
    - label-level total cost:
      - `22`
    - bit-fiber shared schema count:
      - `21`
    - label-level shared schema count:
      - `19`
- Strongest correction learned:
  - the next family comparison is no longer hypothetical
  - decomposition is a real exact option on the hard frontier
  - but it is not yet the winning language family there

Next frontier after v79:

- compare against certificate languages on the same hard frontier,
- or search richer decomposition languages that are not limited to raw label
  bits

## 2026-03-27, hard certificate-language boundary

- New structural target:
  - compare the current hard label-level witness language against an exact
    all-positive certificate family on the same merged-region partition
- Bounded domain:
  - the hard merged-region witness frontier from `v44`
  - same exact partition:
    - `(7)`
    - `(8)`
    - `(9)`
    - `(10,11)`
    - `(12)`
- Strongest bounded results:
  - the searched all-positive certificate family is not exact everywhere
  - it already fails on:
    - `(10,11)`
  - even on the feasible regions it is still larger:
    - feasible-region certificate cost:
      - `23`
    - feasible-region shared schema count:
      - `21`
- Strongest correction learned:
  - on this hard frontier, residual-default witnessing is not only cheaper than
    strict certification
  - it is necessary in the searched all-positive certificate grammar

Next frontier after v80:

- compare against richer certificate languages on the same bounded corpus,
- or search certificate languages with a small amount of local residual
  structure

## 2026-03-27, hard local residual-budget ladder

- New structural target:
  - measure how much local residual-default structure is needed to recover
    exactness on the same hard merged-region partition from `v44`
- Bounded domain:
  - the hard merged-region witness frontier from `v44` and `v80`
  - same exact partition:
    - `(7)`
    - `(8)`
    - `(9)`
    - `(10,11)`
    - `(12)`
  - same `1` to `4` signed-literal conjunction grammar
- Strongest bounded results:
  - `0` residual regions:
    - impossible
  - exactness returns at:
    - `1` residual region
  - that first residual region is forced:
    - `(10,11)`
  - best exact total cost by residual budget:
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
- Strongest correction learned:
  - the hard certificate boundary is not only a yes-no statement
  - residual structure is locally budgetable on this frontier
  - one residual region is already enough for exactness
  - but the first such region is forced by the obstruction at `(10,11)`

Next frontier after v81:

- compare this local residual-budget ladder against a more global shared-schema
  optimization,
- or search richer certificate languages that carry local residual structure
  more efficiently

## 2026-03-27, hard residual-budget schema ladder

- New structural target:
  - keep the exact `v81` hard partition and residual-budget setting, but switch
    the objective from local witness count to global shared-schema count
- Bounded domain:
  - the same hard merged-region witness frontier from `v44`, `v46`, `v80`, and
    `v81`
  - same exact partition:
    - `(7)`
    - `(8)`
    - `(9)`
    - `(10,11)`
    - `(12)`
- Strongest bounded results:
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
  - the same total-cost ladder survives:
    - `28`
    - `26`
    - `24`
    - `23`
    - `22`
  - every feasible rung improves by exactly `1` schema relative to `v81`
- Strongest correction learned:
  - local residual budgeting was not the end of the hard-frontier story
  - the same ladder survives under a stronger global objective
  - the full-budget endpoint recovers the earlier `v46` global optimum

Next frontier after v82:

- search richer certificate grammars with local residual structure on the same
  hard frontier,
- or test whether a comparable global residual-budget law survives on a second
  hard frontier

## 2026-03-27, hard partition-aware residual-budget frontier

- New structural target:
  - drop the fixed `v44` partition and search score partition plus
    residual-default placement jointly under the global shared-schema objective
- Bounded domain:
  - the same hard `v38` feature frontier from `v44` to `v82`
  - same nontrivial scores:
    - `7`
    - `8`
    - `9`
    - `10`
    - `11`
    - `12`
  - same `1` to `4` signed-literal conjunction grammar
- Strongest bounded results:
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
  - exact total-cost ladder stays:
    - `28`
    - `26`
    - `24`
    - `23`
    - `22`
  - winning low-budget partitions merge scores as:
    - `(7,12)`
    - `(9,10)`
- Strongest correction learned:
  - the hard residual-budget law survives
  - but it was overconditioned on a fixed partition
  - the right object is partition-aware residual budgeting

Next frontier after v83:

- test whether the same partition-aware effect survives in a richer certificate
  grammar,
- or transfer the same joint search to a second hard frontier

## 2026-03-27, hard critical-region certificate widening boundary

- New structural target:
  - isolate whether the current hard-frontier certificate failure is a logic
    wall or a grammar wall by widening strict all-positive certificates only on
    the exact region union induced by the `v83` optimal partitions
- Bounded domain:
  - same hard `v38` feature frontier reused through `v83`
  - same critical region union from the `v83` optimal partitions:
    - `(7,12)`
    - `(8)`
    - `(9,10)`
    - `(11)`
    - `(9)`
    - `(10,11)`
    - `(7)`
    - `(12)`
  - compare all-positive certificate grammars:
    - `1` to `4` signed literals
    - `1` to `5` signed literals
- Strongest bounded results:
  - only one critical region changes:
    - `(10,11)`
  - `(10,11)` flips from:
    - impossible in `1..4`
    - exact cost `6` in `1..5`
  - every other critical region keeps the same minimal exact cost
- Strongest correction learned:
  - the current hard-frontier ceiling is not a uniform all-positive failure
  - it is partly a grammar wall localized at `(10,11)`
  - this is still a critical-region result, not yet a full widened rerun of
    the joint `v83` search

Next frontier after v84:

- rerun the full joint partition-aware search in the widened certificate
  grammar,
- or compare the widened certificate grammar against the current
  partition-aware residual-budget witness language on a second hard frontier

## 2026-03-27, hard widened-certificate partition-aware residual-budget frontier

- New structural target:
  - rerun the full `v83` joint search after widening only the strict
    certificate side from the `1..4` literal grammar to the `1..5` literal
    grammar
- Bounded domain:
  - the same hard `v38` feature frontier reused through `v84`
  - search all score partitions of:
    - `7`
    - `8`
    - `9`
    - `10`
    - `11`
    - `12`
  - residual-default witness regions remain in the `1..4` literal grammar
  - strict certificate regions widen to the `1..5` literal grammar
- Strongest bounded results:
  - a zero-residual exact rung now exists
  - widened exact ladder:
    - `0`:
      - shared schemas `25`
      - total cost `29`
    - `1`:
      - shared schemas `23`
      - total cost `27`
    - `2`:
      - shared schemas `21`
      - total cost `25`
    - `3`:
      - shared schemas `20`
      - total cost `24`
    - `4`:
      - shared schemas `19`
      - total cost `23`
    - `5`:
      - shared schemas `19`
      - total cost `22`
  - compared with `v83`:
    - budgets `1` and `2` improve by one schema and one cost unit
    - budgets `3` and above are unchanged
- Strongest correction learned:
  - the localized `v84` grammar relief does move the full joint frontier
  - but only in the low-residual regime
  - once residual budget is large enough, the old `v83` object was already
    stable

Next frontier after v85:

- transfer the same widened-certificate joint search to a second hard frontier,
- or search whether a richer certificate grammar moves budgets `3` and above

## 2026-03-27, high-residual widened-certificate saturation boundary

- New structural target:
  - isolate the unchanged high-residual end of `v85` and test whether widening
    strict certificates again, from `1..5` to `1..6` literals, moves budgets
    `3`, `4`, or `5`
- Bounded domain:
  - the same hard `v38` feature frontier reused through `v85`
  - same partition-aware residual-budget search
  - residual-default witness regions stay in the `1..4` literal grammar
  - strict certificate regions widen from `1..5` to `1..6` literals
  - scope only budgets:
    - `3`
    - `4`
    - `5`
- Strongest bounded results:
  - nothing moves
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
- Strongest correction learned:
  - the low-residual regime in `v85` was grammar-blocked
  - the high-residual regime is now locally saturated against another literal
    widening

Next frontier after v86:

- transfer the widened-certificate search to a second hard frontier,
- or switch from wider conjunctions to a genuinely richer certificate language

## 2026-03-27, low-residual widened-certificate saturation boundary

- New structural target:
  - close the only open slice left after `v86`
  - test whether widening strict certificates again, from `1..5` to `1..6`
    literals, moves budgets `0`, `1`, or `2`
- Bounded domain:
  - the same hard `v38` feature frontier reused through `v86`
  - same partition-aware residual-budget search
  - residual-default witness regions stay in the `1..4` literal grammar
  - strict certificate regions widen from `1..5` to `1..6` literals
  - scope only budgets:
    - `0`
    - `1`
    - `2`
- Strongest bounded results:
  - nothing moves
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
- Strongest correction learned:
  - the low-residual gains in `v85` were already fully captured at width `5`
  - the full hard partition-aware residual-budget ladder is now locally
    saturated on the current literal-width axis

Next frontier after v87:

- transfer the widened-certificate search to a second hard frontier,
- or switch from wider conjunctions to a genuinely richer certificate language

## 2026-03-27, lab-followup partition-aware residual-budget transfer frontier

- New structural target:
  - transfer the partition-aware residual-budget witness-language loop to a
    second bounded domain
  - use the earlier toy lab-followup MPRD frontier rather than the refill
    frontier
- Bounded domain:
  - residual-consistent unique-behavior frontier from `v26`
  - mixed score blocks:
    - `1`
    - `2`
    - `3`
    - `4`
  - holdout error bits over the five lab-followup holdout states
  - signed conjunction grammar of width `1` to `4`
  - same grammar for strict certificates and residual-default witnesses
- Strongest bounded results:
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
  - best exact partition is one merged residual-default region:
    - `(1,2,3,4)`
- Strongest correction learned:
  - the loop transfers, but not with the same residual-budget shape
  - on this frontier, one merged residual region is enough
  - forcing larger exact residual budgets does not improve schema count and
    worsens total cost

Next frontier after v88:

- compare this transfer object against a richer certificate language,
- or search for a semantic invariant that explains the merged residual region

## 2026-03-27, lab-followup widened-certificate saturation boundary

- New structural target:
  - test whether the merged residual-default transfer object from `v88` is only
    a `1..4` strict-certificate grammar artifact
  - widen strict certificates from `1..4` to `1..5` literals while keeping
    residual-default witnesses at `1..4`
- Bounded domain:
  - the same lab-followup partition-aware residual-budget frontier from `v88`
  - mixed score blocks:
    - `1`
    - `2`
    - `3`
    - `4`
- Strongest bounded results:
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
- Strongest correction learned:
  - the merged residual region from `v88` is structural on this bounded
    frontier
  - the whole lab-followup transfer ladder is already locally saturated on this
    literal-width axis

Next frontier after v89:

- compare the transfer ladder against a richer certificate language,
- or search for a semantic invariant explaining the merged residual region

## 2026-03-27, lab-followup unsafe earliest-error residual law

- New structural target:
  - explain the merged residual region from `v88` semantically rather than by
    more grammar widening
  - search for a score-free exact language on the whole unsafe block
- Bounded domain:
  - the full unsafe block of the toy lab-followup frontier
  - holdout scores:
    - `0`
    - `1`
    - `2`
    - `3`
    - `4`
  - signed conjunction grammar of width `1` to `4` over the five ordered
    holdout error bits
- Strongest bounded results:
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
- Strongest correction learned:
  - the merged residual region from `v88` is explained by a direct score-free
    earliest-error law on the unsafe block

Next frontier after v90:

- compare this explanatory law against a richer certificate language,
- or search for an analogous score-free law on the refill frontier

## 2026-03-27, refill maximal score-free merged-subunion boundary

- New structural target:
  - test whether the hard refill frontier admits an analog of the `v90`
    lab-followup score-free explanatory law
  - search all merged score subunions of the refill nontrivial scores in the
    later hard-frontier witness grammar
- Bounded domain:
  - the hard refill frontier from `v29` to `v46`
  - nontrivial refill scores:
    - `7`
    - `8`
    - `9`
    - `10`
    - `11`
    - `12`
  - the `v42` score-free feature surface with `8` features
  - signed conjunction grammar of width `1` to `4`
- Strongest bounded results:
  - residual-default feasible merged subunions:
    - `13`
  - feasible size profile:
    - `1 -> 6`
    - `2 -> 6`
    - `3 -> 1`
  - all-positive feasible merged subunions:
    - `10`
  - all-positive size profile:
    - `1 -> 6`
    - `2 -> 4`
  - unique maximal exact merged subunion:
    - `(9,10,12)`
  - maximal-subunion metrics:
    - row count:
      - `17`
    - label count:
      - `10`
    - exact all-positive presentation:
      - impossible
    - best exact residual-default cost:
      - `10`
- Strongest correction learned:
  - unlike the lab-followup frontier, refill does not admit a whole-block
    score-free explanatory law in this grammar
  - every exact merged refill object of size `3` or larger still needs
    residual-default witnessing
  - the largest exact merged refill object is sparse and non-contiguous in
    score

Next frontier after v91:

- try a richer score-free certificate language on the refill frontier,
- or search for a small semantic grammar that enlarges the maximal exact refill
  merged subset

## 2026-03-28, unlock taxonomy for the mature witness-language line

- New structural target:
  - identify which intervention types actually moved the mature frontier from
    `v78` to `v91`
  - separate real unlocks from local grammar gains and saturation checks
- Bounded domain:
  - the published hard-frontier, transfer, and explanatory-law cycles:
    - `v78` through `v91`
- Strongest bounded results:
  - total events:
    - `14`
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
  - grammar widening:
    - one local gain
    - one partial global gain
    - three saturation cycles
  - strongest next family ranking:
    - `temporal_monitor_cell_obligation_carving`
    - `temporal_minimal_witness_language_discovery`
    - `semantic_predicate_invention`
    - `explanation_fiber_decomposition_for_temporal_specs`
- Strongest correction learned:
  - the mature line moved when the object of search changed:
    - residual budgets
    - schema sharing
    - partitions
    - transfer objects
    - semantic explanations
  - the line usually did not move much when the old formula grammar was merely
    widened

Next frontier after v92:

- package `v93` as temporal monitor-cell obligation carving on the Tau retest
  tracker safety fragment
- or search a small semantic predicate grammar that enlarges the maximal exact
  refill merged subset beyond `(9,10,12)`

## 2026-03-28, staged temporal monitor-cell obligation quotient

- New structural target:
  - test the strongest next rabbit hole from `v92` without letting it replace
    the main frontier
  - ask whether symbolic monitor cells replace flat temporal prefixes directly,
    or only after earlier concrete carving
- Bounded domain:
  - the safety-action fragment of
    `examples/tau/medical_retest_protocol_tracker_v1.tau`
  - ordered decision-list controllers over:
    - `override`
    - `was_review`
    - `repeat_and_abnormal`
    - `nonzero_result`
  - total candidates:
    - `5832`
  - flat two-step trace obligations:
    - `144`
  - symbolic monitor-cell obligations:
    - `36`
- Strongest bounded results:
  - raw whole-family comparison:
    - flat behavior classes:
      - `73`
    - monitor-cell behavior classes:
      - `168`
    - partition match:
      - `false`
    - greedy yes-only checks:
      - traces:
        - `4`
      - cells:
        - `6`
  - after flat step-1 carving:
    - surviving candidates:
      - `108`
    - flat residual classes:
      - `12`
    - monitor-cell residual classes:
      - `12`
    - partition match:
      - `true`
    - exact spec-class match:
      - `true`
    - greedy yes-only checks:
      - traces:
        - `2`
      - cells:
        - `2`
- Strongest correction learned:
  - symbolic monitor cells are too strong if applied to the whole controller
    family from step `0`
  - they become the right quotient only after earlier concrete carving removes
    controllers that never reach the relevant temporal states

Next frontier after v93:

- translate the staged-carving lesson back into software engineering loops
- test obligation-fibered repair or certificate-carrying repair on a bounded bug
  corpus instead of staying in Tau-specific temporal detail

## 2026-03-28, dependency-aware obligation-fibered repair

- New structural target:
  - move back to the main frontier, software-engineering loops
  - test whether failure-obligation fibers beat monolithic patch search on a
    bounded bug corpus
  - identify the first exact correction once fibers overlap
- Bounded domain:
  - two tiny patch corpora with three edit sites:
    - `guard`
    - `bounds`
    - `transform`
  - `27` patches per corpus
  - three unit-test fibers:
    - `guard`
    - `bounds`
    - `transform`
  - corpora:
    - `separable_patch_family`
    - `overlap_patch_family`
- Strongest bounded results:
  - separable family:
    - monolithic average evaluation cost:
      - `39.0`
    - naive fibered average cost:
      - `15.0`
    - dependency-aware fibered average cost:
      - `9.0`
    - exact gold recovery:
      - naive:
        - `27 / 27`
      - dependency-aware:
        - `27 / 27`
  - overlap family:
    - monolithic average evaluation cost:
      - `35.851851851851855`
    - naive fibered average cost:
      - `15.0`
    - dependency-aware fibered average cost:
      - `9.0`
    - exact gold recovery:
      - naive:
        - `16 / 27`
      - dependency-aware:
        - `27 / 27`
- Strongest correction learned:
  - independent fibering is not the end state
  - the first exact fix is dependency-aware fibering:
    - solve `transform` first
    - then solve `guard` and `bounds` conditioned on it

Next frontier after v94:

- compare certificate-carrying repair against the same bounded corpus
- or search the smallest exact repair-language grammar once the fiber dependency
  graph is known

## 2026-03-28, certificate-carrying repair basis

- New structural target:
  - push past dependency-aware fiber search
  - ask whether patch-plus-witness beats search over repair fibers on the same
    bounded software corpus
- Bounded domain:
  - the two `27`-patch corpora from `v94`
  - local observation tokens:
    - `guard`
    - `bounds`
    - `transform`
  - searched certificate bases:
    - all singleton, pair, and triple subsets of those three tokens
- Strongest bounded results:
  - separable family:
    - no singleton exact
    - no pair exact
    - unique minimal exact basis:
      - `guard`
      - `bounds`
      - `transform`
    - certificate verification cost:
      - `3`
    - `v94` dependency-aware cost:
      - `9.0`
  - overlap family:
    - no singleton exact
    - no pair exact
    - unique minimal exact basis:
      - `guard`
      - `bounds`
      - `transform`
    - certificate verification cost:
      - `3`
    - `v94` dependency-aware cost:
      - `9.0`
- Strongest correction learned:
  - once the proposer can carry a local witness, direct verification beats even
    dependency-aware fiber search
  - the exact lower bound on this corpus is:
    - three local observation tokens

Next frontier after v95:

- search the smallest exact repair-language grammar on top of the `v94` fiber
  graph and the `v95` witness basis
- or test whether the same certificate-carrying law survives on a richer
  bounded software bug corpus

## 2026-03-28, certificate-to-patch decoder graph

- New structural target:
  - push past witness verification
  - ask whether the carried witness from `v95` compiles back into the patch
    through a tiny exact symbolic decoder
- Bounded domain:
  - the same two `27`-patch software corpora from `v94` and `v95`
  - witness observations:
    - `guard_obs`
    - `bounds_obs`
    - `transform_obs`
  - decoder search:
    - all nonempty observation-subset assignments to:
      - `guard`
      - `bounds`
      - `transform`
- Strongest bounded results:
  - separable family:
    - minimal exact decoder cost:
      - `3`
    - unique minimal decoder:
      - `guard <- guard_obs`
      - `bounds <- bounds_obs`
      - `transform <- transform_obs`
  - overlap family:
    - minimal exact decoder cost:
      - `4`
    - unique minimal decoder:
      - `guard <- guard_obs`
      - `bounds <- bounds_obs, transform_obs`
      - `transform <- transform_obs`
- Strongest correction learned:
  - overlap does not require two extra decoder dependencies
  - it requires exactly one:
    - `transform_obs -> bounds`

Next frontier after v96:

- search the smallest exact repair-language grammar above the decoder graph
- or move to a richer bounded bug corpus and test whether the same decoder law
  survives

## 2026-03-28, shared repair-language template

- New structural target:
  - compress the two exact decoder graphs from `v96` into one shared language
    plus family-specific deltas
- Bounded domain:
  - the two exact software decoder graphs from `v96`
  - edge universe:
    - `3` observations
    - `3` fields
    - `9` possible edges
  - exhaustive base-graph search:
    - `512` candidates
  - exact models:
    - additive deltas
    - signed add/remove edits
- Strongest bounded results:
  - unique minimum in both models:
    - shared base:
      - `guard_obs -> guard`
      - `bounds_obs -> bounds`
      - `transform_obs -> transform`
    - separable delta:
      - none
    - overlap delta:
      - `transform_obs -> bounds`
  - additive total cost:
    - `4`
  - signed-edit total cost:
    - `4`
- Strongest correction learned:
  - the two `v96` decoders do not need separate grammars
  - they compress to one local base template plus one sparse overlap patch

Next frontier after v97:

- search the smallest exact patch-program macro language that realizes the
  shared template
- or move to a richer bounded bug corpus and test whether the same
  base-plus-one-delta law survives
