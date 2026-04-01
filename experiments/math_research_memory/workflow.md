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

## 2026-03-28, shared repair-program macro language

- New structural target:
  - compress the `v97` shared repair-language template into a tiny macro
    program over a natural decoder-graph grammar
- Bounded domain:
  - the two exact decoder targets from `v97`
  - same `3 x 3` observation-to-field graph
  - macro grammar:
    - `6` permutation matchings
    - `3` fanouts
    - `3` fanins
    - `9` single-edge patches
- Strongest bounded results:
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
  - unique exact shared additive macro template:
    - base:
      - `MATCH_ID`
    - overlap delta:
      - `SINGLE[transform_obs->bounds]`
    - total macro cost:
      - `2`
  - compression over `v97`:
    - `4 -> 2`
- Strongest correction learned:
  - the shared `v97` decoder is not only an edge template
  - it is a reusable repair-program instruction
  - overlap still needs no new language, only one sparse patch macro

Next frontier after v98:

- search the smallest exact semantic patch-program language above the macro
  basis
- or move to a richer bounded bug corpus and test whether the same
  base-plus-one-patch law survives

## 2026-03-28, repair-schema transfer atlas

- New structural target:
  - test whether the `v98` macro law survives beyond the original two software
    families
- Bounded domain:
  - one transfer atlas with:
    - the separable family
    - all `6` single-overlap families obtained by adding one off-diagonal edge
      to the local diagonal decoder
  - exact schema-family search over:
    - `MATCH`
    - `FANOUT`
    - `FANIN`
    - `SINGLE`
- Strongest bounded results:
  - singleton families:
    - `MATCH`:
      - not exact
    - `FANOUT`:
      - not exact
    - `FANIN`:
      - not exact
    - `SINGLE`:
      - exact
      - description length:
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
- Strongest correction learned:
  - the `v98` base-plus-one-patch law is not only a two-family accident
  - it survives on the full single-overlap atlas as a reusable schema basis

Next frontier after v99:

- move to a richer overlap atlas and test when `MATCH + SINGLE` stops being the
  exact MDL-optimal basis
- or search for a semantic schema language above the current syntactic basis

## 2026-03-28, two-overlap repair-schema obstruction

- New structural target:
  - find the first exact transfer obstruction to the `v99` one-overlap law
- Bounded domain:
  - widened software atlas:
    - `1` separable family
    - `6` one-overlap families
    - `15` two-overlap families
  - exact schema-family search over:
    - `MATCH`
    - `FANOUT`
    - `FANIN`
    - `SINGLE`
- Strongest bounded results:
  - `MATCH + SINGLE`:
    - still exact
    - description length:
      - `57`
    - total instance cost:
      - `55`
  - new exact optimum:
    - `MATCH`
    - `FANIN`
    - `FANOUT`
    - `SINGLE`
    - description length:
      - `53`
    - total instance cost:
      - `49`
  - histogram shift:
    - `MATCH + SINGLE`:
      - `1 -> 1`
      - `2 -> 9`
      - `3 -> 12`
    - optimum:
      - `1 -> 1`
      - `2 -> 15`
      - `3 -> 6`
- Strongest correction learned:
  - the first obstruction is not failure of exactness
  - it is failure of compression
  - bundled row and column overlap is the first structure that makes
    `FANOUT` and `FANIN` worth paying for

Next frontier after v100:

- search the smallest exact semantic schema language that explains the jump
  from `MATCH + SINGLE` to `MATCH + FANIN + FANOUT + SINGLE`
- or move to a richer bounded bug corpus where row and column bundles appear as
  real repair motifs

## 2026-03-28, two-overlap semantic motif law

- New structural target:
  - explain the `v100` transfer obstruction semantically rather than by one
    more atlas count
- Bounded domain:
  - the `15` two-overlap software families from `v100`
  - target label:
    - optimal exact program cost under the `v100` best basis, `2` or `3`
  - semantic features:
    - `same_obs`
    - `same_field`
    - `swap_pair`
- Strongest bounded results:
  - no singleton basis is exact
  - no pair basis is exact
  - the unique minimal exact basis is:
    - `same_obs`
    - `same_field`
    - `swap_pair`
  - exact rule:
    - row bundle:
      - `2`
    - column bundle:
      - `2`
    - swap pair:
      - `2`
    - all other two-overlap families:
      - `3`
- Strongest correction learned:
  - the first transfer obstruction now has a small semantic explanation
  - the new structure is not arbitrary overlap
  - it is exactly row bundles, column bundles, and reciprocal swap pairs

Next frontier after v101:

- search the smallest exact semantic schema language that realizes these three
  motifs directly
- or move to a richer bounded bug corpus and test whether the same motifs
  appear as real repair structures

## 2026-03-28, semantic repair-schema language

- New structural target:
  - compile the `v101` motif law into a smallest exact semantic schema
    language on the full atlas up to two overlaps
- Bounded domain:
  - the same `22` software families from `v100`
  - semantic schema grammar:
    - `DIAGONAL`
    - `SINGLE`
    - `BUNDLE2`
    - `SWAP2`
- Strongest bounded results:
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
  - this matches the best exact atlas cost from `v100`
- Strongest correction learned:
  - the obstruction can now be expressed as a semantic language, not only a
    syntactic basis jump
  - `FANIN/FANOUT` collapse into `BUNDLE2`
  - swap-specific nonidentity matchings collapse into `SWAP2`

Next frontier after v102:

- use Morph to search reformulations of the semantic schema language
- use ShapeForge to encode the motif slices and negative knowledge
- or move to a richer bounded bug corpus where the same motifs appear naturally

## 2026-03-28, motif-routed repair compiler

- New structural target:
  - collapse the `v102` semantic language into a tiny exact router over repair
    schema shapes
- Bounded domain:
  - the same `22` software families from `v102`
  - target labels:
    - `DIAGONAL`
    - `DIAGONAL+SINGLE`
    - `BUNDLE2+DIAGONAL`
    - `DIAGONAL+SWAP_PAIR`
  - searched predicates:
    - `extra0`
    - `extra1`
    - `same_obs`
    - `same_field`
    - `swap_pair`
    - `bundle_motif`
- Strongest bounded results:
  - no `1`-branch router is exact
  - no `2`-branch router is exact
  - the first exact router has:
    - `3` branches
  - exact minimal router shape:
    - `extra0 -> DIAGONAL`
    - `swap_pair -> DIAGONAL+SWAP_PAIR`
    - `bundle_motif -> BUNDLE2+DIAGONAL`
    - default:
      - `DIAGONAL+SINGLE`
- Strongest correction learned:
  - the semantic schema language already contains a compact exact repair policy
  - the next frontier is no longer another router search
  - it is richer corpora or stronger semantic worlds

Next frontier after v103:

- use ShapeForge to encode the router cases as world-model slices and negative
  knowledge
- use Morph to search stronger reformulations of the routed compiler
- or move to a richer bounded bug corpus and test whether the same router law
  survives

## 2026-03-28, typed motif-kind direct repair compiler

- New structural target:
  - search the smallest typed world-state basis that determines the full
    minimal repair program, not only a routed schema head
- Bounded domain:
  - the same `22` software families from `v102` and `v103`
  - raw input:
    - the off-diagonal extra-edge set above the diagonal decoder base
  - searched typed coordinates:
    - `extra_count`
    - `same_obs`
    - `same_field`
    - `swap_pair`
    - `bundle_motif`
    - `motif_kind`
- Strongest bounded results:
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
- Strongest correction learned:
  - the software branch does not need to stop at a semantic router
  - on this bounded atlas, one typed motif coordinate already compiles the full
    minimal repair program
  - the right next frontier is transfer or richer reformulation, not another
    local schema pass

Next frontier after v104:

- test whether `motif_kind` survives on a richer atlas with three overlaps
- use Morph to search stronger reformulations above `motif_kind`
- or search a richer bounded software corpus where the same typed motif law
  survives

## 2026-03-28, support-signature direct repair compiler

- New structural target:
  - transfer the `v104` direct compiler to the richer atlas with up to three
    overlaps
- Bounded domain:
  - full up-to-three-overlap software atlas
  - family count:
    - `42`
  - searched typed support-signature coordinates:
    - `extra_count`
    - `obs_profile`
    - `field_profile`
    - `max_obs`
    - `max_field`
    - `swap_pairs`
    - `same_obs`
    - `same_field`
- Strongest bounded results:
  - no singleton coordinate is exact
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
- Strongest correction learned:
  - the singleton motif law does not transfer unchanged
  - but the direct-compiler story does survive
  - the right transfer object is a small support signature, not another local
    motif tweak

Next frontier after v105:

- use Morph to search whether the five exact size-3 bases collapse to a smaller
  canonical support language
- test a richer atlas for the first support-signature obstruction beyond size
  `3`
- or move to a richer bounded software corpus where the same support-signature
  law survives

## 2026-03-28, canonical support-signature direct compiler

- New structural target:
  - quotient the `v105` exact size-3 transfer bases by observation-field
    symmetry
- Bounded domain:
  - the same `42` software families from `v105`
  - augmented coordinate library:
    - `support_signature`
    - `extra_count`
    - `obs_profile`
    - `field_profile`
    - `max_obs`
    - `max_field`
    - `swap_pairs`
    - `same_obs`
    - `same_field`
- Strongest bounded results:
  - unique exact singleton basis:
    - `support_signature`
  - no other singleton in the augmented library is exact
  - exact support-signature count:
    - `8`
- Strongest correction learned:
  - the `v105` transfer law is not only a small basis
  - it admits a canonical singleton quotient

Next frontier after v106:

- search whether the canonical support quotient scalarizes again
- test a richer atlas for the first obstruction beyond support-signature
  quotients
- or move to a richer bounded software corpus and test whether the same
  canonical quotient survives

## 2026-03-28, four-scalar support law

- New structural target:
  - scalarize the `v106` canonical support quotient inside a small scalar
    library
- Bounded domain:
  - the same `42` software families from `v106`
  - searched scalars:
    - `extra_count`
    - `max_obs`
    - `max_field`
    - `swap_pairs`
    - `same_obs`
    - `same_field`
- Strongest bounded results:
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
- Strongest correction learned:
  - the canonical support quotient does scalarize, but not below four scalars
  - the direct software compiler now has both:
    - a canonical quotient
    - a compact scalar law

Next frontier after v107:

- use Morph to search whether the three exact size-`4` scalar bases collapse to
  a smaller semantic scalar family
- test a richer atlas for the first obstruction beyond the 4-scalar law
- or move to a richer bounded software corpus and test whether the same scalar
  support law survives

## 2026-03-28, three-scalar max-support law

- New structural target:
  - collapse the `v107` four-scalar law by quotienting the axis-specific maxima
    into one semantic support scalar
- Bounded domain:
  - the same `42` software families from `v107`
  - searched semantic scalar library:
    - `extra_count`
    - `max_support`
    - `min_support`
    - `support_gap`
    - `swap_pairs`
- Strongest bounded results:
  - no singleton scalar is exact
  - no pair scalar basis is exact
  - first exact basis size:
    - `3`
  - unique exact basis:
    - `extra_count`
    - `max_support`
    - `swap_pairs`
- Strongest correction learned:
  - the four-scalar law still had hidden axis-specific redundancy
  - the direct compiler now has an exact three-scalar semantic law

Next frontier after v108:

- use Morph to search whether the three-scalar law collapses further into a
  smaller semantic orbit language
- test a richer atlas for the first obstruction beyond the max-support law
- or move to a richer bounded software corpus and test whether the same
  three-scalar law survives

## 2026-03-28, two-coordinate support-orbit law

- New structural target:
  - collapse the `v108` three-scalar law into a smaller semantic orbit
    coordinate
- Bounded domain:
  - the same `42` software families from `v108`
  - searched orbit library:
    - `extra_count`
    - `support_kind`
    - `max_support`
    - `swap_pairs`
    - `all_distinct`
    - `has_bundle`
    - `has_swap`
- Strongest bounded results:
  - no singleton orbit coordinate is exact
  - first exact basis size:
    - `2`
  - unique exact basis:
    - `extra_count`
    - `support_kind`
- Strongest correction learned:
  - the three-scalar law still had one more orbit quotient
  - the direct compiler now has an exact two-coordinate orbit law

Next frontier after v109:

- test a richer atlas for the first obstruction beyond the support-orbit law
- or search what exact object survives if one unique repair shape stops being
  available

## 2026-03-28, menu-valued support-signature law

- New structural target:
  - salvage exact structure above the `v109` orbit law on the up-to-four-overlap
    atlas by replacing one chosen repair shape with the full exact menu of
    minimal repair head-shapes
- Bounded domain:
  - full software atlas with up to four off-diagonal overlaps
  - family count:
    - `57`
- Strongest bounded results:
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
  - support-signature states:
    - `11`
  - distinct exact menus:
    - `11`
  - menu cardinality histogram:
    - `1 -> 24`
    - `2 -> 15`
    - `3 -> 12`
    - `5 -> 6`
- Strongest correction learned:
  - the first higher-order obstruction above the direct compiler line is not a
    total failure of symbolic structure
  - the right bounded object becomes an exact menu-valued repair language

Next frontier after v110:

- test whether the same menu-valued support law survives on the full
  off-diagonal atlas
- or search the first exact coordinate that collapses each menu back to one
  canonical repair shape

## 2026-03-28, full-atlas support-signature menu law

- New structural target:
  - transfer the `v110` menu-valued support law to the full software atlas
- Bounded domain:
  - all subsets of the six off-diagonal repair edges
  - family count:
    - `64`
- Strongest bounded results:
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
- Strongest correction learned:
  - the menu-valued support law survives farther than the last direct compiler
  - the deeper software object is now a support-signature indexed repair menu

Next frontier after v111:

- search the first exact coordinate that collapses each full-atlas menu to one
  canonical repair shape
- or move to a richer bounded bug corpus and test whether the same menu-valued
  support law survives

## 2026-03-28, normalized support-signature direct compiler family

- New structural target:
  - test whether the full-atlas menu law restores direct compilers once a
    deterministic normal form is chosen inside each exact menu
- Bounded domain:
  - full software atlas over all `64` subsets of the six off-diagonal repair
    edges
  - searched menu-local normal forms:
    - `bundle_first`
    - `swap_first`
    - `single_first`
    - `fewest_families`
- Strongest bounded results:
  - for all four normal forms:
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
  - all `40` ambiguous families see at least two normal forms disagree
  - pairwise disagreement counts:
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
- Strongest correction learned:
  - exact menu discovery is not the end of the direct-compiler line
  - it can feed a family of exact normalized direct compilers
  - the preferred structural normal form is bundle-first, which coincides with
    fewest-families on the full ambiguous slice

Next frontier after v112:

- search the smallest semantic condition that selects among the competing normal
  forms
- or move to a richer bounded bug corpus and test whether the same
  menu-then-normalize loop survives

## 2026-03-28, perfect-swap-cover selector law

- New structural target:
  - search the smallest exact semantic selector above the normalized compiler
    family on the ambiguous full-atlas slice
- Bounded domain:
  - ambiguous slice of the full software atlas
  - ambiguous families:
    - `40`
- Target property:
  - whether the exact menu admits a pure-swap normal form, using only:
    - `DIAGONAL`
    - `SWAP2`
- Searched selector library:
  - `perfect_swap_cover`
  - `extra_count`
  - `swap_pairs`
  - `balanced_profiles`
  - `max_support`
  - `obs_profile`
  - `field_profile`
- Strongest bounded results:
  - on the ambiguous full-atlas slice:
    - exact menu admits a pure-swap normal form iff:
      - `perfect_swap_cover := (extra_count = 2 * swap_pairs)`
  - unique exact singleton:
    - `perfect_swap_cover`
  - pure-swap families:
    - `4`
  - pure-swap support signatures:
    - `2`
- Strongest correction learned:
  - the normalized family itself has semantic interior
  - the pure-swap regime is already controlled by one direct Boolean law

Next frontier after v113:

- search the smallest exact selector for bundle-first versus swap-first on the
  full ambiguous slice
- or move to a richer bounded bug corpus and test whether the same selector
  pattern survives

## 2026-03-28, bundle-vs-swap disagreement selector law

- New structural target:
  - search the smallest exact selector for when the two preferred structural
    normal forms, `bundle_first` and `swap_first`, actually disagree on the
    ambiguous full-atlas slice
- Bounded domain:
  - ambiguous slice of the full software atlas
  - ambiguous families:
    - `40`
- Target label:
  - `diff` if `bundle_first` and `swap_first` choose different exact normalized
    repair shapes
  - `same` otherwise
- Searched selector library:
  - `perfect_swap_cover`
  - `extra_count`
  - `swap_pairs`
  - `balanced_profiles`
  - `max_support`
  - `obs_profile`
  - `field_profile`
- Strongest bounded results:
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
- Strongest correction learned:
  - the first intrinsic selector above the normalized family is not one-bit
  - structural disagreement is still tiny and exact, but it needs a three-part
    state, not a singleton or pair feature

Next frontier after v114:

- search the smallest exact selector for bundle-first versus single-first on
  the same ambiguous slice
- or move to a richer bounded bug corpus and test whether the same
  disagreement law survives

## 2026-03-28, canonical ambiguity quotient law

- New structural target:
  - test whether the exact selector from v114 is only a one-pair fact or a
    deeper shared quotient controlling the whole ambiguous normalized family
- Bounded domain:
  - ambiguous slice of the full software atlas
  - ambiguous families:
    - `40`
  - compared normal forms:
    - `bundle_first`
    - `swap_first`
    - `single_first`
    - `fewest_families`
- Strongest bounded results:
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
- Strongest correction learned:
  - the post-menu ambiguity is not pair-specific noise
  - all meaningful pairwise disagreements in the normalized family factor
    through one shared exact quotient

Next frontier after v115:

- search the smallest semantic presentation of the common 7-state ambiguity
  quotient
- or move to a richer bounded bug corpus and test whether the same shared
  quotient survives

## 2026-03-28, support-gap ambiguity law

- New structural target:
  - search the smallest semantic presentation of the common ambiguity quotient
    from v115 in a richer derived feature library
- Bounded domain:
  - ambiguous slice of the full software atlas
  - ambiguous families:
    - `40`
  - target:
    - the full six-pair disagreement signature among
      `bundle_first`, `swap_first`, `single_first`, and
      `fewest_families`
- Searched derived semantic library:
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
- Strongest bounded results:
  - no singleton is exact
  - first exact basis size:
    - `2`
  - exact minimal basis count:
    - `1`
  - unique exact minimal basis:
    - `balanced_profiles`
    - `support_gap`
  - preferred state count:
    - `6`
  - distinct disagreement-signature classes:
    - `3`
- Strongest correction learned:
  - the shared ambiguity layer still had semantic slack left
  - the common 7-state quotient from v115 collapses again to a unique exact
    size-2 semantic basis

Next frontier after v116:

- search the smallest semantic presentation of the three disagreement-signature
  classes themselves
- or move to a richer bounded bug corpus and test whether the same support-gap
  law survives

## 2026-03-28, three-guard ambiguity-class law

- New structural target:
  - compile the three disagreement-signature classes above v116 to the
    smallest exact branch program in a small semantic grammar
- Bounded domain:
  - ambiguous slice of the full software atlas
  - ambiguous families:
    - `40`
  - distinct class states:
    - `6`
- Searched branch grammar:
  - atoms over:
    - `balanced_profiles`
    - `support_gap`
  - conjunction guards of size up to `2`
  - ordered decision lists with up to `3` guards
- Strongest bounded results:
  - no `0`-guard program is exact
  - no `1`-guard program is exact
  - no `2`-guard program is exact
  - first exact program:
    - `3` guards
  - exact program:
    - `support_gap = 0 -> class_2`
    - `balanced_profiles and support_gap = 1 -> class_3`
    - `unbalanced_profiles and support_gap = 2 -> class_2`
    - default:
      - `class_1`
- Strongest correction learned:
  - the ambiguity layer now has an exact executable branch program, not only a
    compressed quotient

Next frontier after v117:

- search the smallest semantic meaning of the three class labels
- or move to a richer bounded bug corpus and test whether the same class law
  survives

## 2026-03-28, anchored outlier decomposition law

- New structural target:
  - replace the opaque class labels from v117 with an anchored semantic
    decomposition
- Bounded domain:
  - the six distinct semantic states induced by:
    - `balanced_profiles`
    - `support_gap`
- Chosen anchor:
  - `bundle_first = fewest_families`
- Strongest bounded results:
  - the ambiguity layer splits into:
    - `swap_outlier`
    - `single_outlier`
  - both outlier bits first become exact at:
    - `2` guards
  - exact `swap_outlier` law:
    - `balanced_profiles and support_gap >= 2 -> False`
    - `unbalanced_profiles and support_gap = 1 -> False`
    - default:
      - `True`
  - exact `single_outlier` law:
    - `support_gap = 0 -> False`
    - `unbalanced_profiles and support_gap = 2 -> False`
    - default:
      - `True`
- Strongest correction learned:
  - the ambiguity classes are not only executable, they are semantically
    interpretable as anchored outlier bits

Next frontier after v118:

- search for a smaller joint program that emits the anchor plus both outlier
  bits directly
- or move to a richer bounded bug corpus and test whether the same anchored
  outlier decomposition survives

## 2026-03-28, two-clause ambiguity-class law

- New structural target:
  - test whether the ambiguity-class program from v117 compresses further in a
    slightly richer symbolic grammar
- Bounded domain:
  - the six distinct class states induced by:
    - `balanced_profiles`
    - `support_gap`
- Searched clause grammar:
  - conjunction terms of size up to `2`
  - clauses that are ORs of up to `2` conjunction terms
  - ordered decision lists of up to `2` clauses
- Strongest bounded results:
  - no `0`-clause program is exact
  - no `1`-clause program is exact
  - first exact program:
    - `2` ordered clauses
  - exact law:
    - `balanced_profiles and support_gap = 1 -> class_3`
    - `support_gap = 0 or unbalanced_profiles and support_gap = 2 -> class_2`
    - default:
      - `class_1`
- Strongest correction learned:
  - the conjunction-only ambiguity-class program was not the end of the line
  - a slightly richer symbolic language yields a smaller exact classifier

Next frontier after v119:

- search the smallest exact joint program for the anchor plus both outlier bits
- or move to a richer bounded bug corpus and test whether the same two-clause
  law survives

## 2026-03-28, anchor-shape law

- New structural target:
  - test whether the stable anchor `bundle_first = fewest_families` also
    compiles to a tiny exact symbolic law over the same semantic state
- Bounded domain:
  - six distinct anchor states induced by:
    - `balanced_profiles`
    - `support_gap`
- Strongest bounded results:
  - no `0`-guard program is exact
  - no `1`-guard program is exact
  - no `2`-guard program is exact
  - first exact program:
    - `3` guards
  - exact law:
    - `balanced_profiles and support_gap = 2 -> BUNDLE2+BUNDLE2+DIAGONAL+SWAP2`
    - `support_gap >= 2 -> BUNDLE2+BUNDLE2+DIAGONAL`
    - `balanced_profiles -> BUNDLE2+BUNDLE2+BUNDLE2+DIAGONAL`
    - default:
      - `BUNDLE2+DIAGONAL+SWAP2`
- Strongest correction learned:
  - the semantic state already controlling the ambiguity layer also controls
    the anchor repair family itself
  - the branch now has a fuller anchored routing kernel, not just outlier
    selectors

Next frontier after v120:

- search the smallest exact joint program for the anchor plus both outlier bits
- or move to a richer bounded bug corpus and test whether the same anchored
  routing kernel survives

## 2026-03-28, anchored routing kernel law

- New structural target:
  - unify the separate software survivors above the ambiguous slice into one
    direct kernel:
    - `AnchorShape`
    - `SwapOutlier`
    - `SingleOutlier`
- Bounded domain:
  - the full `40`-family ambiguous slice of the software atlas
- Strongest bounded results:
  - no singleton coordinate in the searched semantic library is exact
  - the unique exact minimal basis has size `2`:
    - `balanced_profiles`
    - `support_gap`
  - no `0`-, `1`-, `2`-, `3`-, or `4`-guard joint program is exact
  - the first exact joint program has:
    - `5` guards
- Exact joint law:
  - `unbalanced_profiles and support_gap = 1 -> (BUNDLE2+DIAGONAL+SWAP2, False, True)`
  - `unbalanced_profiles -> (BUNDLE2+BUNDLE2+DIAGONAL, True, False)`
  - `support_gap = 0 -> (BUNDLE2+BUNDLE2+BUNDLE2+DIAGONAL, True, False)`
  - `support_gap = 1 -> (BUNDLE2+BUNDLE2+BUNDLE2+DIAGONAL, True, True)`
  - `support_gap = 2 -> (BUNDLE2+BUNDLE2+DIAGONAL+SWAP2, False, True)`
  - default:
    - `(BUNDLE2+BUNDLE2+DIAGONAL, False, True)`
- Strongest correction learned:
  - the branch does not only have nearby exact laws
  - it now has one direct bounded kernel object over the same semantic basis

Next frontier after v121:

- search the exact menu law above the anchored kernel regions
- or move to a richer bounded bug corpus and test where the size-`2` basis
  stops being exact

## 2026-03-28, anchored kernel menu law

- New structural target:
  - test whether the size-`2` semantic kernel basis also determines the full
    repair menu
- Bounded domain:
  - the full `40`-family ambiguous slice of the software atlas
- Strongest bounded results:
  - the anchored kernel basis:
    - `(balanced_profiles, support_gap)`
    - is exact for routing but not for the full repair menu
  - no singleton coordinate in the searched semantic library is exact
  - the first exact menu basis has size `3`
  - a preferred exact refinement is:
    - `(balanced_profiles, support_gap, high_overlap)`
  - the only kernel state that splits is:
    - `(balanced_profiles = True, support_gap = 0)`
  - the preferred basis induces `7` exact menu states
  - the first exact direct menu program has:
    - `6` guards
- Strongest correction learned:
  - the current software kernel is exact for normalized routing, but one more
    semantic bit is needed for full menu reconstruction
  - the boundary is localized and structural, not diffuse

Next frontier after v122:

- search a menu-selector law above the exact menu states
- or move to a richer bounded bug corpus and test where the menu refinement
  itself fails

## 2026-03-28, logic replay correction law

- New structural target:
  - replay the actual `bundle_first` anchor and the true joint kernel at the
    logic level, rather than relying on quotient-state deduplication
- Bounded domain:
  - the full `40`-family ambiguous slice of the software atlas
- Strongest bounded results:
  - the actual `bundle_first` anchor is not definable in:
    - `(balanced_profiles, support_gap)`
  - the same failure propagates to the true joint kernel
  - the clean split state is:
    - `(balanced_profiles = True, support_gap = 0)`
  - the first searched repair bit is:
    - `high_overlap := (extra_count >= 5)`
  - both actual anchor and true kernel first become exact in:
    - `(balanced_profiles, support_gap, high_overlap)`
- Strongest correction learned:
  - the old size-`2` kernel story was too strong if read as a theorem about the
    actual `bundle_first` anchor
  - `Q2` survives for ambiguity and disagreement structure
  - `Q3` is the first honest theory for actual selector and kernel values

Next frontier after v123:

- classify all current software targets by the smallest exact theory they need
- or find the first target that forces a theory beyond `Q3`

## 2026-03-28, software definability phase diagram law

- New structural target:
  - build a logic-level phase diagram over the current software target family
- Bounded domain:
  - the same `40`-family ambiguous slice of the software atlas
- Strongest bounded results:
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
  - no searched non-constant target in the current family requires a theory
    beyond `Q3`
  - generated Lean receipt:
    - `experiments/math_object_innovation_v124/generated/logic_receipt.lean`
  - local Lean receipt check now passes with pinned toolchain:
    - `~/.elan/toolchains/leanprover--lean4---v4.28.0/bin/lean`
  - environment note:
    - `elan stable` is still blocked by disk pressure on this machine
- Strongest correction learned:
  - the software branch is better understood as a definability hierarchy than
    as one flat “kernel plus menu” story
  - current frontier:
    - `Q2` controls relations
    - `Q3` controls realizations

Next frontier after v124:

- find the first software target that forces a theory beyond `Q3`
- or find a canonical selector law inside the exact `Q3` menu states

## 2026-03-28, common commitment-tier witness law

- New structural target:
  - search for one common Q2-equal witness pair that separates the full `Q3`
    commitment tier
- Bounded domain:
  - the same `40`-family ambiguous slice of the software atlas
- Strongest bounded results:
  - the witness state is:
    - `(balanced_profiles = True, support_gap = 0)`
  - that state contains:
    - `3` low-overlap families
    - `1` high-overlap family
  - every low-overlap family separates from the unique high-overlap family on:
    - `bundle_first`
    - `fewest_families`
    - `swap_first`
    - `single_first`
    - `true_kernel`
    - `menu`
- Strongest correction learned:
  - `high_overlap` is not only a one-target repair bit
  - it is a common necessity witness for the whole commitment tier

Next frontier after v125:

- search for the first software target that forces a theory beyond `Q3`
- or search for a selector law that is canonical inside the exact `Q3`
  commitment states

## 2026-03-28, software target-algebra closure law

- New structural target:
  - test whether the current software target family already closes at `Q3`
    when treated as finite algebras rather than isolated formulas
- Bounded domain:
  - the same `40`-family ambiguous slice of the software atlas
- Strongest bounded results:
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
    - same preferred exact basis:
      - `(balanced_profiles, support_gap, high_overlap)`
    - same exact state count:
      - `7`
- Strongest correction learned:
  - the current software family is already algebraically closed at `Q3`
  - no extra theory bit is needed merely to combine all current relation and
    commitment targets

Next frontier after v126:

- search for the first genuinely richer software target that escapes `Q3`
- or search for a canonical selector theorem inside the exact `Q3` states

## 2026-03-28, richer selector-family closure law

- New structural target:
  - widen the selector family beyond the hand-chosen normal forms and test
    whether the richer selector algebra still closes at `Q3`
- Bounded domain:
  - the same `40`-family ambiguous slice of the software atlas
- Strongest bounded results:
  - searched selector library:
    - all lexicographic selector orders of length `1..3`
    - over:
      - `bundle_max`
      - `swap_max`
      - `single_max`
      - `single_min`
      - `families_min`
  - raw selectors:
    - `85`
  - unique selector behaviors on the bounded corpus:
    - `10`
  - the full richer selector-family target still has:
    - minimal exact basis size `3`
    - preferred exact basis `(balanced_profiles, support_gap, high_overlap)`
    - exact state count `7`
- Strongest correction learned:
  - the current software atlas is more saturated than it looked
  - no searched richer selector in this family escapes `Q3`

Next frontier after v127:

- search for the first genuinely richer software target that escapes `Q3`
- or search for a selector theorem inside the exact `Q3` states

## 2026-03-28, support-geometry phase diagram law

- New structural target:
  - find the first logic target that genuinely escapes `Q3` on the ambiguous
    software slice
- Bounded domain:
  - the same `40`-family ambiguous slice of the software atlas
- Strongest bounded results:
  - symmetric support target:
    - `support_signature`
    - minimal exact basis size:
      - `3`
    - preferred exact basis:
      - `(balanced_profiles, support_gap, high_overlap)`
    - exact state count:
      - `7`
  - oriented support target:
    - `oriented_support_pair = (obs_profile, field_profile)`
    - not exact in `Q3`
    - first exact basis size in the searched orientation-extended library:
      - `2`
    - preferred exact basis:
      - `(extra_count, orientation)`
    - exact state count:
      - `8`
  - raw family target:
    - still not exact in the full searched symmetric-plus-orientation library
    - conflicting full-feature buckets:
      - `8`
    - largest conflicting bucket size:
      - `6`
- Strongest correction learned:
  - `Q3` already controls the full symmetric support geometry
  - the first honest escape is orientation, not another selector

Next frontier after v128:

- search the first theory that recovers raw family identity
- or prove the orientation tier is the exact first escape from `Q3`

## 2026-03-28, row-column incidence completion law

- New structural target:
  - recover exact raw family identity using the smallest honest incidence
    theory above the semantic stack
- Bounded domain:
  - the same `40`-family ambiguous slice of the software atlas
- Strongest bounded results:
  - raw family target first becomes exact at:
    - basis size `5`
  - no basis of size `4` or smaller is exact
  - preferred exact basis:
    - `(out_guard, out_bounds, out_transform, in_guard, in_bounds)`
  - exact state count:
    - `40`
  - minimal exact basis count:
    - `24`
  - class breakdown:
    - pure degree bases:
      - `6`
    - `extra_count` substitution bases:
      - `9`
    - `support_gap` substitution bases:
      - `9`
- Strongest correction learned:
  - raw family identity does not need brute-force edge indicators
  - the next honest theory above `Q4` is row-column incidence

Next frontier after v129:

- search whether a smaller semantic quotient sits above incidence but below raw
  family identity
- or test whether the incidence law survives on a richer software atlas

## 2026-03-28, incidence-signature singleton law

- New structural target:
  - compress the size-`5` scalar incidence law into the smallest tuple-aware
    quotient
- Bounded domain:
  - the same `40`-family ambiguous slice of the software atlas
- Strongest bounded results:
  - raw family target first becomes exact at:
    - basis size `1`
  - unique exact singleton:
    - `incidence_signature = (out_profile, in_profile)`
  - exact state count:
    - `40`
  - nearby singletons not exact:
    - `out_profile`
    - `in_profile`
    - `extra_count`
    - `support_gap`
    - `orientation`
- Strongest correction learned:
  - the true logic object above `Q4` is one incidence-signature quotient
  - the old size-`5` law was only a scalar presentation of that singleton

Next frontier after v130:

- test whether the singleton incidence-signature law survives on the full atlas
- or find the first obstruction if it fails

## 2026-03-28, cycle-orientation incidence extension law

- New structural target:
  - transfer the incidence-signature singleton law from the ambiguous slice to
    the full off-diagonal atlas
- Bounded domain:
  - the full `64`-family off-diagonal software atlas
- Strongest bounded results:
  - incidence-signature transfer obstruction:
    - exactly `1` conflict bucket
    - conflicting signature:
      - `((1,1,1),(1,1,1))`
    - conflicting family count:
      - `2`
  - first exact basis size:
    - `2`
  - exact size-`2` bases:
    - `(incidence_signature, cycle_orientation)`
    - `(incidence_signature, has_guard_to_bounds)`
    - `(incidence_signature, has_guard_to_transform)`
  - preferred semantic basis:
    - `(incidence_signature, cycle_orientation)`
- Strongest correction learned:
  - the full-atlas transfer obstruction is not large
  - it is one clean cycle-orientation bit above incidence-signature

Next frontier after v131:

- search for the first richer atlas where incidence-signature plus one cycle bit
  stops being exact
- or search for a smaller semantic account of cycle orientation itself

## 2026-03-29, complement-threshold and governed-profit law

- New structural target:
  - first bounded profit-agent game with platform extraction, complement classes,
    and an `MPRD` admissibility gate
- Bounded domain:
  - same model capability
  - complement classes `low`, `high`
  - extraction levels `open`, `extractive`, `closed`
- Strongest bounded results:
  - active threshold sets:
    - `low -> {open}`
    - `high -> {open, extractive}`
  - exact platform region law:
    - `extractive_revenue >= open_revenue iff n_low <= 4 * n_high`
  - governed-profit law:
    - forbidding the top illicit strategy still leaves a positive-profit
      admissible strategy
- Strongest correction learned:
  - equal model capability does not force equal profit or equal activation
  - platform incentives can rationally exclude low-complement users
  - governed profit should be modeled as a feasible-action-set problem

Next frontier after v132:

- add passive ownership explicitly
- test whether the platform optimum stays maximal once user effort responds

## 2026-03-29, hold-up and passive-ownership threshold law

- New structural target:
  - bounded two-stage platform/user game with expropriation, active effort, and
    passive ownership
- Bounded domain:
  - expropriation levels:
    - `open`
    - `moderate`
    - `high`
    - `maximal`
  - user modes:
    - inactive
    - passive
    - active
- Strongest bounded results:
  - best active effort:
    - `open -> e3`
    - `moderate -> e2`
    - `high -> e1`
    - `maximal -> e0`
  - mode choice:
    - `open -> active`
    - `moderate -> active`
    - `high -> passive`
    - `maximal -> passive`
  - platform revenue:
    - `open -> 4`
    - `moderate -> 12`
    - `high -> 0`
    - `maximal -> 0`
  - `moderate` is the unique platform optimum
- Strongest correction learned:
  - full capture is not automatically revenue-optimal
  - once extraction gets high enough, users rationally stop active venture
    effort and shift to passive claims

Next frontier after v133:

- widen the game to heterogeneous complements plus passive ownership
- or add demand closure and ask when the platform equilibrium is socially
  unstable

## 2026-03-29, heterogeneous-complement passive-ownership region law

- New structural target:
  - combine equal-capability heterogeneous complements with passive ownership in
    one bounded platform game
- Bounded domain:
  - complement classes:
    - `low`
    - `high`
  - expropriation levels:
    - `open`
    - `moderate`
    - `high`
    - `maximal`
- Strongest bounded results:
  - mode choice:
    - `low` is active only at `open`
    - `high` is active at `open` and `moderate`
    - both classes are passive at `high` and `maximal`
  - exact region law:
    - `moderate_revenue >= open_revenue iff 2 * n_low <= 9 * n_high`
  - strict witnesses:
    - `open` wins at `(5,1)`
    - `moderate` wins at `(4,1)`
- Strongest correction learned:
  - the platform does not face one global extraction optimum
  - the optimal regime depends on complement composition
  - passive ownership and complement heterogeneity together are enough to
    produce a clean phase boundary

Next frontier after v134:

- add demand closure:
  - if labor income falls and passive claims are concentrated, who buys output?
- or add a real platform-versus-user ownership split instead of one fixed
  passive dividend

## 2026-03-29, demand-closure ownership law

- New structural target:
  - first generic arithmetic theorem for demand closure in the post-AGI
    economics branch
- Assumption:
  - one-unit household demand model
  - `n` active owner households
  - each produces `m + 1` units
  - each consumes at most one unit
  - `b` passive-beneficiary households consume one unit each
- Strongest results:
  - supply:
    - `S = (m + 1) * n`
  - demand:
    - `D = n + b`
  - exact theorem:
    - `D >= S iff b >= m * n`
  - corollaries:
    - `b = 0 -> closure requires m * n = 0`
    - `m = 1 -> closure iff b >= n`
- Strongest correction learned:
  - the demand side is not optional bookkeeping
  - concentrated ownership plus higher productivity already forces broad passive
    claims in the simplest nontrivial model

Next frontier after v135:

- replace the one-unit household cap with a richer demand function
- or integrate the ownership law back into the platform extraction game

## 2026-03-29, private-optimum versus closure phase diagram

- New structural target:
  - integrate the `v134` platform-composition boundary with the `v135`
    demand-closure theorem
- Assumption:
  - `open`:
    - low-complement households stay active and produce `1`
    - high-complement households stay active and produce `2`
  - `moderate`:
    - only high-complement households stay active
    - each active high-complement household produces `2`
  - each household consumes at most one unit
  - `n_high > 0`
- Strongest bounded results:
  - `open` clears iff `n_high = 0`
  - `moderate` clears iff `n_high <= n_low`
  - private-optimum boundary from `v134` remains:
    - `moderate_revenue >= open_revenue iff 2 * n_low <= 9 * n_high`
  - integrated viable band:
    - for `n_high > 0`, a privately optimal and demand-clearing regime exists
      iff `n_high <= n_low and 2 * n_low <= 9 * n_high`
- Strongest correction learned:
  - private platform optimality and macro closure are different objects
  - `open` can be privately preferred while failing closure
  - broad low-complement households are required for the moderate regime to be
    both privately optimal and socially viable

Next frontier after v136:

- replace the one-unit demand cap with a richer demand law
- or let passive ownership shares become strategic instead of fixed

## 2026-03-29, active-owner share ceiling

- New structural target:
  - extract the universal-principal limit implied by the one-unit demand model
- Assumption:
  - total households:
    - `h`
  - active owner households:
    - `n`
  - each active owner household produces `2`
  - each household consumes at most `1`
  - passive or inactive households consume `1` and produce `0`
- Strongest bounded results:
  - closure law:
    - `h >= 2 * n iff n <= h / 2`
  - all-active impossibility:
    - for `h > 0`, not `h >= 2 * h`
  - witnesses:
    - `h = 4, n = 2` clears
    - `h = 3, n = 2` fails
    - `h = 3, n = 3` fails
- Strongest correction learned:
  - the main issue is not whether every household can own a profit agent
  - the main issue is whether every household can remain an active owner once
    output per active owner exceeds one unit
  - under the current demand cap, the answer is no

Next frontier after v137:

- replace the one-unit demand cap with richer household demand
- or make active/passive status strategic and solve the new fixed point

## 2026-03-29, symmetric coordination law

- New structural target:
  - turn the active-owner share ceiling into a real active-versus-passive
    coordination game
- Assumption:
  - `h` identical households
  - `n` active owner households
  - each active owner household produces `2`
  - each household consumes at most `1`
  - mode semantics:
    - active payoff greater than passive:
      - `n = h`
    - active payoff less than passive:
      - `n = 0`
    - active payoff equal to passive:
      - any `n` is individually stable
- Strongest bounded results:
  - strict active preference:
    - no positive-household demand-clearing equilibrium
  - strict passive preference:
    - only the zero-production equilibrium
  - indifference:
    - nontrivial demand-clearing equilibrium exists exactly when `n <= h / 2`
- Strongest correction learned:
  - equal capabilities plus equal incentives do not automatically produce a
    workable economy
  - the first nontrivial stable regime appears only as a coordinated interior
    split

Next frontier after v138:

- add differentiated complements to the coordination game
- or replace indifference with quotas, prices, or rationing rules

## 2026-03-29, uniform-price impossibility and quota implementability

- New structural target:
  - compare uniform pricing against hard quotas as coordination devices in the
    symmetric double-output economy
- Assumption:
  - `h` identical households
  - each active owner household produces `2`
  - each household consumes at most `1`
  - uniform-price semantics:
    - `delta > 0 -> n = h`
    - `delta < 0 -> n = 0`
    - `delta = 0 -> any n is individually stable`
  - quota semantics:
    - under `delta > 0`, all households want active
    - a hard quota `q` sets `n = min(h, q)`
- Strongest bounded results:
  - uniform-price interior law:
    - `0 < n < h and individual stability imply delta = 0`
  - quota clearing law:
    - `h >= 2 * q iff q <= h / 2`
- Strongest correction learned:
  - prices alone do not implement the nontrivial interior regime
  - a real coordination device such as a quota can

Next frontier after v139:

- add differentiated complements to the mechanism game
- or replace hard quotas with prices plus lotteries, markets, or transferable
  permits

## 2026-03-29, heterogeneous price-selection law

- New structural target:
  - test whether uniform pricing becomes useful again once households differ by
    active surplus
- Assumption:
  - `L` low-complement households
  - `H` high-complement households
  - each active household produces `2`
  - each household consumes at most `1`
  - strict surplus order:
    - `a_low < a_high`
  - uniform-price semantics:
    - `p < a_low`:
      - both types choose active
    - `a_low < p < a_high`:
      - only the high type chooses active
    - `p > a_high`:
      - both types choose passive
- Strongest bounded results:
  - middle-region selection:
    - `a_low < p < a_high -> n_low = 0 and n_high = H`
  - exact clearing law:
    - `L + H >= 2 * H iff H <= L`
- Strongest correction learned:
  - the uniform-price impossibility from the homogeneous model is not
    universal
  - heterogeneous complements let one price implement a nontrivial interior
    regime, but only if the selected high-complement group is not a majority

Next frontier after v140:

- compose pricing with quotas
- or replace uniform pricing with permits or lotteries once high-complement
  households are a majority

## 2026-03-29, price-plus-quota composition law

- New structural target:
  - compose heterogeneous price selection with a second-stage quota
- Assumption:
  - same two-type economy as `v140`
  - stay in the strict middle price region:
    - `a_low < p < a_high`
  - add a hard quota `q` on active high-type slots
- Strongest bounded results:
  - price solves type selection:
    - eligible active pool is `H`
  - quota solves count selection:
    - implemented active count is `q`
  - exact composed clearing law:
    - `L + H >= 2 * q iff q <= (L + H) / 2`
- Strongest correction learned:
  - price alone can still overselect the right type
  - mechanism composition restores a clearing interior regime

Next frontier after v141:

- replace hard quotas with lotteries or transferable permits
- or endogenize the quota level as a platform choice

## 2026-03-29, intermediate-demand multiplier law

- New structural target:
  - correct the zero-employee-firm opening so human attention is not treated as
    the only possible final sink
- Assumption:
  - scalar software-only economy
  - gross output:
    - `Y`
  - intermediate demand share:
    - `alpha = a / b`
    - `0 <= a < b`
  - final sink bundle:
    - `F = H + A_term + C + X`
    - `H` human final demand
    - `A_term` terminal agent demand
    - `C` crypto or code-native settlement demand
    - `X` external demand
- Strongest bounded results:
  - multiplier law:
    - `Y = alpha * Y + F`
  - scaled form:
    - `b * Y = a * Y + b * F`
  - exact sink laws:
    - `a < b and F = 0 imply Y = 0`
    - `a < b and F > 0 imply Y > 0`
- Strongest correction learned:
  - human attention is not the only possible sink
  - but intermediate agent trade alone cannot replace positive final sinks

Next frontier after v142:

- turn the scalar sink bundle into a small network model
- or distinguish terminal agent demand from intermediate agent demand more
  structurally

## 2026-03-29, zero-employee company entry ceiling law

- New structural target:
  - make the zero-employee company thought experiment itself explicit as one
    branch of the assumption tree
- Assumption:
  - legal shell creation is not the binding bottleneck
  - control shells can be legal, crypto-native, or hybrid
  - final sink bundle:
    - `F = H + A_term + C + X`
  - `N` active zero-employee firms share the bundle symmetrically
  - each active firm pays operating cost `c`
- Strongest bounded results:
  - total profit law:
    - `Pi_total = F - N * c`
  - exact entry ceiling laws:
    - `Pi_total >= 0 iff F >= N * c`
    - `Pi_total > 0 iff F > N * c`
- Strongest correction learned:
  - unlimited technical firm creation does not imply unlimited sustainable
    firms
  - once the assumption tree is explicit, the next frontier is not vague
    entrepreneurship talk
  - it is discovery bottlenecks, slot rents, and routing regimes above the
    same sink bundle

Next frontier after v143:

- discovery bottlenecks and slot rents for zero-employee firms
- or a small network model where sink access is not symmetric

## 2026-03-29, discovery-slot redistribution law

- New structural target:
  - formalize the first platform-power object above the zero-employee company
    ceiling
- Assumption:
  - fixed final sink bundle:
    - `F = H + A_term + C + X`
  - `N` active zero-employee firms
  - `q` discovery slots with `0 < q <= N`
  - slot holders split the sink symmetrically
  - every firm pays operating cost `c`
- Strongest bounded results:
  - total profit remains:
    - `Pi_total = F - N * c`
  - slot-holder margin numerator:
    - `M_slot = F - q * c`
  - exact laws:
    - `M_slot > 0 iff F > q * c`
    - `Pi_undiscovered = -c`
- Strongest correction learned:
  - discovery bottlenecks do not create new total surplus
  - they redistribute sink access and create slot rents
  - the right next frontier is now asymmetric routing or endogenous slot sale

Next frontier after v144:

- asymmetric-routing network model for sink access
- or slot auctions, permit markets, or governed execution slots

## 2026-03-29, incumbent-rent machine lockout law

- New structural target:
  - combine machine trust learning with incumbent control rents and no
    re-entry
- Assumption:
  - two-period machine-versus-human adoption game
  - social baseline is the always-human path
  - machine structural advantage:
    - `A`
  - period-1 trust discount:
    - `tau1`
  - trust-learning gain after successful machine use:
    - `lam`
  - incumbent private rent loss from machine control:
    - `rho`
  - if the machine is rejected in period 1, it cannot enter in period 2
- Strongest bounded results:
  - social machine-path premium:
    - `2 * A - 2 * tau1 + lam`
  - private incumbent-controller machine premium:
    - `2 * A - 2 * tau1 + lam - 2 * rho`
  - exact social condition:
    - `2 * A + lam >= 2 * tau1`
  - exact private-adoption condition:
    - `2 * A + lam >= 2 * tau1 + 2 * rho`
  - exact lockout wedge:
    - `2 * A + lam >= 2 * tau1 and 2 * A + lam < 2 * tau1 + 2 * rho`
- Strongest correction learned:
  - machine superiority is not enough for adoption
  - trust learning and incumbent rent protection must be modeled together
  - no re-entry converts a one-period private rejection into persistent human
    lock-in

Next frontier after v155:

- explicit assurance design that lowers `tau1` or raises `lam`
- repeated games where routing, deployment surface, and trust coevolve

## 2026-03-29, assurance-package adoption law

- New structural target:
  - convert the machine-trust wedge into an explicit software-design law
- Assumption:
  - same two-period no-reentry adoption game as `v155`
  - package components:
    - `d`, per-period trust lift from audit, replay, or confinement
    - `g`, extra period-2 trust learning
    - `k`, one-time package cost
- Strongest bounded results:
  - packaged private machine premium:
    - `2 * A - 2 * tau1 + lam + 2 * d + g - 2 * rho - k`
  - exact package-adoption condition:
    - `2 * A + lam + 2 * d + g >= 2 * tau1 + 2 * rho + k`
  - exact flip condition above the baseline block:
    - `2 * d + g - k >= (2 * tau1 + 2 * rho) - (2 * A + lam)`
- Strongest correction learned:
  - "more trusted software" is not a slogan
  - trust lift, learning lift, and package cost enter with different weights
  - the design problem is to close the exact adoption shortfall

Next frontier after v156:

- assurance-package composition, where audit, insurance, and liability shifting
  are separate levers
- or richer repeated games where routing, deployment surface, and trust update
  together

## 2026-03-29, assurance-lever coefficient law

- New structural target:
  - separate assurance-package levers and compute their exact private weights
- Assumption:
  - same two-period no-reentry adoption game as `v156`
  - package levers:
    - `d`, trust lift
    - `g`, extra period-2 learning
    - `ell`, liability or rent offset
  - linear package cost:
    - `k = c_d * d + c_g * g + c_ell * ell`
- Strongest bounded results:
  - general private-adoption condition:
    - `2 * A + lam + (2 - c_d) * d + (1 - c_g) * g + (2 - c_ell) * ell >= 2 * tau1 + 2 * rho`
  - equal-cost corollary:
    - if `c_d = c_g = c_ell = 1`, then
      `2 * A + lam + d + ell >= 2 * tau1 + 2 * rho`
  - delayed-learning cancellation:
    - under equal unit costs, `g` does not expand the private adoption region
- Strongest correction learned:
  - assurance levers do not buy equal adoption effect
  - front-loaded trust lift and liability offset are stronger private levers
    than delayed learning when costs are comparable

Next frontier after v157:

- social versus private package choice, subsidy, or mandate
- or richer repeated games where assurance changes routing or deployment too

## 2026-03-29, assurance-subsidy implementation law

- New structural target:
  - formalize the exact bridge between social package preference and private
    adoption
- Assumption:
  - same two-period no-reentry package model
  - package levers:
    - `d`, trust lift
    - `g`, extra learning
    - `k`, package cost
  - incumbent rent loss:
    - `rho`
  - adoption subsidy:
    - `s`
- Strongest bounded results:
  - social package condition:
    - `2 * A + lam + 2 * d + g >= 2 * tau1 + k`
  - private package condition:
    - `2 * A + lam + 2 * d + g >= 2 * tau1 + 2 * rho + k`
  - minimal implementing subsidy:
    - `s_star = max(0, 2 * tau1 + 2 * rho + k - (2 * A + lam + 2 * d + g))`
  - divergence-wedge bound:
    - on the strict wedge, `0 < s_star <= 2 * rho`
- Strongest correction learned:
  - social and private assurance choice are different problems
  - the bridge payment is exact, not heuristic
  - the rent wedge is the whole remaining obstruction once the package itself is
    socially worthwhile

Next frontier after v158:

- endogenous package sponsorship by platform, insurer, or regulator
- or richer repeated games where assurance, routing, and deployment coevolve

## 2026-03-31, requirements recoverability law

- New structural target:
  - formalize when counterexamples recover missing requirements rather than
    only refute an incomplete specification
- Assumption:
  - finite requirement universe:
    - `R`
  - finite witness library of nonempty violation signatures:
    - `W`
    - each witness signature is `S ⊆ R`
  - incomplete specification with missing set:
    - `M ⊆ R`
  - admissible signatures under the incomplete specification:
    - `A_W(M) = {S in W | S ⊆ M}`
  - compare:
    - pure singleton-driven recovery
    - oracle-assisted recovery after targeted stakeholder questions
- Strongest bounded results:
  - pure recovery holds iff:
    - `∀r in M, {r} in W`
  - oracle-assisted recovery holds iff:
    - `⋃ A_W(M) = M`
  - exhaustive check domain:
    - `|R| = 3`
    - all `128` witness libraries
    - all `7` nonempty missing sets
  - global all-missing-set recoverability counts:
    - pure:
      - `16`
    - oracle-assisted:
      - `16`
  - pair-lobotomy recoverability counts:
    - pure:
      - `16`
    - oracle-assisted:
      - `36`
    - strict oracle-only advantage:
      - `20`
- Strongest correction learned:
  - counterexamples do not recover missing requirements by themselves unless
    witness geometry isolates them
  - stakeholder help changes recoverability only under scoped omission
    families, not under the unrestricted all-missing-set family
  - omission-depth assumptions are part of the semantics of the loop, not just
    evaluation metadata

Next frontier after v159:

- minimal question policies over admissible witness families
- ambiguity quotients for larger `k`-lobotomy families
- or promotion into a requirements-discovery tutorial once a second survivor
  sharpens the loop

## 2026-03-31, observation-quotient loop law

- New structural target:
  - move above atomic witness recovery and formalize the full observation
    geometry induced by the counterexample signature family
- Assumption:
  - finite requirement universe:
    - `R`
  - finite witness library:
    - `W`
  - scoped omission family:
    - `F`
  - observation map:
    - `O_W(M) = A_W(M) = {S in W | S ⊆ M}`
  - post-observation requirement-membership queries:
    - `Q_r(M) = 1 iff r in M`
- Strongest bounded results:
  - pure structured recovery holds iff:
    - `O_W` is injective on `F`
  - minimal worst-case question budget:
    - `max_C depth*(C)` over the ambiguity classes of `~_W,F`
  - exhaustive check domain:
    - `|R| = 4`
    - all `32768` witness libraries
    - families:
      - all `15` nonempty omissions
      - all `6` pair-lobotomy omissions
  - pair-family counts:
    - atomic singleton rule recoverable libraries:
      - `2048`
    - structured observation-quotient recoverable libraries:
      - `19424`
    - strict structured advantage:
      - `17376`
  - all-nonempty counts:
    - atomic singleton rule recoverable libraries:
      - `2048`
    - structured observation-quotient recoverable libraries:
      - `3072`
  - pair-only witness library:
    - pair family:
      - structured recoverable:
        - yes
      - atomic recoverable:
        - no
      - question budget:
        - `0`
    - all-nonempty family:
      - not injective
      - question budget:
        - `3`
- Strongest correction learned:
  - witness arity alone is not the real recoverability bottleneck
  - the loop state matters:
    - atomic witness-to-requirement recovery is much weaker than full
      observation-quotient reasoning
  - stakeholder questions belong above the ambiguity quotient, not as an
    undifferentiated fallback

Next frontier after v160:

- search exact minimal question policies, not only worst-case depths
- search richer query languages beyond requirement-membership questions
- or package the loop-geometry branch into a reusable research skill if one
  more survivor lands cleanly

## 2026-03-31, staged temporal label-function law

- New structural target:
  - test whether temporal label functions are a new loop-space axis rather than
    just one more feature family
- Assumption:
  - bounded temporal controller family from the retest tracker safety fragment
  - flat two-step trace label:
    - `L_trace`
  - symbolic monitor-cell label:
    - `L_cell`
  - staged slice:
    - `X_1`, controllers already correct on every first-step input
- Strongest bounded results:
  - full family:
    - candidate count:
      - `5832`
    - trace behavior classes:
      - `73`
    - monitor-cell behavior classes:
      - `168`
    - exact partition match:
      - `false`
    - monitor-cell labels refine trace labels:
      - `true`
  - staged slice:
    - surviving candidates:
      - `108`
    - residual trace classes:
      - `12`
    - residual monitor-cell classes:
      - `12`
    - exact partition match:
      - `true`
- Strongest correction learned:
  - the symbolic temporal label basis is not globally wrong, it is early
  - temporal label functions can become exact only after earlier carving has
    restricted the live candidate space
  - loop space therefore has a staged basis-change axis, not only a witness or
    quotient axis

Next frontier after v161:

- search exact trigger laws for when a richer label basis becomes valid
- compare staged label-basis changes against observation-quotient changes on
  the same bounded corpus
- or synthesize a small general loop-space geometry tutorial packet

## 2026-03-31, uniform witness ladder law

- New structural target:
  - test whether witness arity itself induces an exact observability ladder for
    bounded requirements-discovery loops
- Assumption:
  - requirement universe `R` with `|R| = n`
  - uniform `k`-ary witness library:
    - `W_k = {S ⊆ R | |S| = k}`
  - observation map:
    - `O_k(M) = {S in W_k | S ⊆ M}`
- Strongest bounded results:
  - exhaustive checks:
    - all `2 <= n <= 6`
    - all `1 <= k <= n`
    - all nonempty omission sets
  - lower rung collapse:
    - `O_k(M) = ∅` exactly when `|M| < k`
  - upper rung exactness:
    - `O_k` is injective on omission sets with `|M| >= k`
  - pair-witness query law:
    - under `k = 2`, the only global ambiguity class is the singleton layer
    - exact worst-case requirement-membership budget:
      - `n - 1`
- Strongest correction learned:
  - witness arity is a real loop-space axis
  - it sets an exact observability threshold
  - higher-arity witness generation does not just add more evidence
  - it moves the point where exact pure recovery becomes possible

Next frontier after v162:

- compute exact membership-question budgets for the whole collapsed lower rung,
  not only the pair-witness singleton case
- compare mixed-arity witness libraries against single-arity ladders
- relate witness-arity thresholds to staged temporal label-basis changes

## 2026-03-31, lower-rung membership budget law

- New structural target:
  - compute the exact requirement-membership question budget on the collapsed
    lower rung created by uniform `k`-ary witness libraries
- Assumption:
  - same uniform witness library:
    - `W_k = {S ⊆ R | |S| = k}`
  - collapsed lower rung:
    - `L_{n,k} = {M ⊆ R | 1 <= |M| < k}`
  - follow-up query language:
    - requirement-membership only
- Strongest bounded results:
  - brute-force decision-tree search:
    - all `2 <= n <= 7`
    - all `2 <= k <= n`
  - compressed dynamic-program check:
    - all `2 <= n <= 12`
    - all `2 <= k <= n`
  - exact budget law:
    - `budget_mem(n, 2) = n - 1`
    - `budget_mem(n, k) = n` for `3 <= k <= n`
  - exact design consequence:
    - among all non-singleton uniform witness generators, pair witnesses are
      query-optimal under membership-only follow-up
- Strongest correction learned:
  - witness arity and query burden do not move monotonically together
  - going from `k = 2` to `k >= 3` raises the observability threshold, but it
    also makes the unresolved lower rung harder by one full membership query
  - loop space is therefore a tradeoff surface, not a one-axis ladder

Next frontier after v163:

- compare richer follow-up query languages against the membership-only law
- search mixed-arity witness families for better threshold-versus-budget tradeoffs
- unify witness-arity ladders with staged temporal label-basis changes in one
  shared geometry packet

## 2026-03-31, pair-basis sufficiency law

- New structural target:
  - test whether mixed higher-arity witness layers add any exact recovery power
    once the pair layer is already present
- Assumption:
  - mixed witness library:
    - `W_A = {S ⊆ R | |S| ∈ A}`
  - arity sets:
    - every `A ⊆ {2, ..., n}` with `2 ∈ A`
  - omission family:
    - all nonempty omission sets
  - follow-up query language:
    - requirement-membership only
- Strongest bounded results:
  - exhaustive checks:
    - all `2 <= n <= 7`
    - all mixed arity sets containing `2`
  - exact partition law:
    - every checked `W_A` induces the same ambiguity partition as pair-only
      `W_{ {2} }`
  - exact budget law:
    - every checked `W_A` has the same worst-case membership-question budget
      as pair-only:
      - `n - 1`
- Strongest correction learned:
  - once the pair basis is present, higher-arity uniform witness layers are
    redundant for exact recovery plus membership-only follow-up
  - the real next lever is the follow-up query language, not more uniform
    witness arity stacked on top of pairs

Next frontier after v164:

- search richer separator questions above the pair basis
- search non-uniform witness families that beat the pair basis on a real
  Pareto frontier
- write the loop-space geometry packet that now unifies:
  - observation quotients
  - witness-arity ladders
  - pair-basis sufficiency
  - staged temporal label-basis changes

## 2026-03-31, separator expressivity law above the pair basis

- New structural target:
  - compare exact follow-up power of different separator languages once the
    pair basis has already collapsed the search to singleton ambiguity
- Assumption:
  - pair witness basis:
    - `W_2 = {S ⊆ R | |S| = 2}`
  - residual ambiguity class after saturated observation:
    - all singleton omissions
  - three query languages:
    - pair-subset queries
    - singleton-membership queries
    - block-intersection queries
- Strongest bounded results:
  - brute-force decision-tree search:
    - all `2 <= n <= 8`
  - exact ladder:
    - pair-subset queries:
      - unrecoverable
    - singleton-membership queries:
      - `n - 1`
    - block-intersection queries:
      - `ceil(log2 n)`
  - constructive extension table:
    - checked formulas through `n = 32`
- Strongest correction learned:
  - once the pair basis is present, the next decisive lever is separator
    expressivity
  - some richer-sounding queries are useless on the residual class
  - the right block language compresses the residual from linear to logarithmic
    depth

Next frontier after v165:

- search exact laws for richer separator families:
  - pair-membership plus singleton-membership
  - cardinality or small-group queries
- search non-uniform witness bases together with separator languages on a real
  Pareto frontier
- write the loop-space geometry packet, the core cross-axis ladder now seems
  stable enough

## 2026-03-31, singleton witness substitution law

- New structural target:
  - compute the exact tradeoff between built-in singleton witnesses and later
    singleton-membership questioning
- Assumption:
  - singleton witness basis on `T ⊆ R`:
    - `W_T = {{r} | r ∈ T}`
  - full nonempty omission family
  - follow-up query language:
    - requirement-membership only
- Strongest bounded results:
  - brute-force decision-tree checks:
    - all `2 <= n <= 8`
    - all singleton witness counts `0 <= |T| <= n`
  - exact budget law:
    - `budget_mem(W_T, F_all) = n - |T|`
- Strongest correction learned:
  - each singleton witness substitutes for exactly one later membership query
  - atomic witness generation and atomic questioning are linearly fungible on
    this bounded family
  - the logarithmic gain from `v165` is therefore not a generic property of
    block queries, it is a geometry gain that only appears after the pair basis
    has compressed the ambiguity class to singletons

Next frontier after v166:

- compare non-uniform witness families against the singleton substitution axis
- search exact mixed separator families above the pair basis
- start drafting the public loop-space geometry packet, the main bounded axes
  now look stable

## 2026-03-31, geometry prerequisite law for block separators

- New structural target:
  - test whether block-intersection queries are powerful by themselves, or only
    after a witness basis has already changed the ambiguity geometry
- Assumption:
  - same block-intersection separator language
  - compare:
    - raw nonempty omission family
    - singleton residue after pair-basis observation
- Strongest bounded results:
  - raw family brute-force checks:
    - all `2 <= n <= 5`
    - exact budget:
      - `n`
  - singleton residue brute-force checks:
    - all `2 <= n <= 8`
    - exact budget:
      - `ceil(log2 n)`
- Strongest correction learned:
  - block queries are not generically logarithmic
  - they only become logarithmic after the pair basis has already compressed
    the ambiguity class to singletons
  - the gain therefore comes from composition:
    - geometry-changing witness basis
    - then expressive separator language

Next frontier after v167:

- search non-uniform witness bases that yield even smaller residual classes than
  the pair basis
- search mixed separator families on those residual classes
- start comparing these hybrid loops directly against plain verifier-compilation

## 2026-03-31, atomic geometry invariance law

- New structural target:
  - test whether richer separator language helps at all on purely atomic witness
    bases
- Assumption:
  - singleton witness basis:
    - `W_T = {{r} | r ∈ T}`
  - full nonempty omission family
  - compare:
    - singleton-membership follow-up
    - block-intersection follow-up
- Strongest bounded results:
  - brute-force checks:
    - all `2 <= n <= 5`
    - all singleton witness counts `0 <= |T| <= n`
  - exact invariance law:
    - `budget_atom(W_T, F_all) = budget_block(W_T, F_all) = n - |T|`
- Strongest correction learned:
  - richer separator language alone does not beat the atomic axis
  - the first real gain requires a geometry-changing witness basis
  - this sharply narrows the search for loops stronger than plain
    verifier-compilation

Next frontier after v168:

- search non-uniform geometry-changing witness bases
- compare hybrid quotient-question loops directly against verifier-compiler
  controllers on the same bounded corpora
- if one more cross-axis survivor lands, begin the public tutorial draft for
  loop-space geometry

## 2026-03-31, complement witness pure-mass law

- New structural target:
  - test whether a sparse non-uniform geometry-changing witness can buy a gain
    that worst-case budget alone would miss
- Assumption:
  - partition:
    - `R = T ⊔ U`
  - mixed witness library:
    - `W_{T,U} = {{t} | t ∈ T} ∪ {U}`
  - genuine higher-arity branch:
    - `|U| >= 2`
  - residual questioning:
    - block-intersection
- Strongest bounded results:
  - brute-force checks:
    - all `3 <= n <= 5`
    - all splits with `|U| >= 2`
  - exact laws:
    - `pure_classes(W_{T,U}) = 2^|T|`
    - `budget_block(W_{T,U}, F_all) = |U|`
- Strongest correction learned:
  - worst-case residual depth is not enough to rank loops
  - one complement witness can create exponentially many immediately resolved
    cases without improving the worst-case residual budget
  - the next search should therefore track both:
    - residual depth
    - and pure resolved mass

Next frontier after v169:

- search sparse non-uniform pair-like witness bases beyond the one-complement
  family
- compare hybrid loop families by:
  - residual depth
  - pure resolved mass
  - and controller size
- if one more survivor lands, begin the public tutorial draft for loop-space
  geometry

## 2026-03-31, star-pair pure-mass law

- New structural target:
  - test whether sparse pair-like witness families can buy the same kind of
    pure-mass gain that the one-complement family exposed
- Assumption:
  - star-pair basis:
    - `W_star(a) = {{a, u} | u ∈ U}`
  - anchored star basis:
    - `W_anchor_star(a) = {{a}} ∪ W_star(a)`
  - full nonempty omission family
  - block-intersection residual questioning
- Strongest bounded results:
  - pure-class checks:
    - all `3 <= n <= 8`
  - exact budget proof:
    - all `2 <= |U| <= 7`
    - lower bound from family size
    - upper bound from singleton-block queries
  - exact laws:
    - `pure_classes(W_star) = 2^(n-1) - 1`
    - `pure_classes(W_anchor_star) = 2^(n-1)`
    - `budget_block(W_star, F_all) = n - 1`
    - `budget_block(W_anchor_star, F_all) = n - 1`
- Strongest correction learned:
  - sparse pair-like witnesses can match the atomic `n - 1` residual depth
    while buying exponential pure resolved mass
  - anchored stars are therefore real loop candidates, not just another
    presentation of the atomic axis

Next frontier after v170:

- generalize from stars to wider sparse pair geometries
- check whether the star law sits inside a larger family ladder
- keep tracking:
  - witness size
  - pure resolved mass
  - residual depth
  - residual controller size

## 2026-03-31, biclique pure-mass and residual-family law

- New structural target:
  - unify the star family with a broader sparse pair geometry instead of
    treating each pair-like witness basis as an isolated object
- Assumption:
  - partition:
    - `R = A ⊔ B`
  - complete bipartite pair witness basis:
    - `W_biclique(A, B) = {{a, b} | a ∈ A, b ∈ B}`
  - full nonempty omission family
- Strongest bounded results:
  - checks:
    - all `1 <= |A| <= |B| <= 5`
  - exact laws:
    - `pure_classes(W_biclique) = (2^|A| - 1)(2^|B| - 1)`
    - `Residual(W_biclique) = P_+(A) ∪ P_+(B)`
- Strongest correction learned:
  - the star family is one edge of a wider biclique ladder
  - balanced bicliques buy much larger pure resolved mass than stars at still
    sparse pair counts
  - the residual family is structured, not arbitrary, which gives the next
    residual-controller target

Next frontier after v171:

- solve the exact residual-controller cost on the biclique side-only family
- compare biclique loops against pair-basis plus block-separator hybrids under
  the full ranking tuple
- once one more residual-controller law lands, begin the public tutorial draft
  for loop-space geometry

## 2026-03-31, biclique residual-controller law

- New structural target:
  - close the next rung after the biclique pure-mass law by solving the exact
    block-query cost on the side-only residual family
- Assumption:
  - residual family:
    - `P_+(A) ∪ P_+(B)`
  - query language:
    - block-intersection
  - coordinate order:
    - `a = |A| <= b = |B|`
- Strongest bounded results:
  - brute-force checks:
    - all `1 <= a <= b <= 3`
  - exact proof-bounds:
    - all `1 <= a <= b <= 8`
  - exact law:
    - `budget_block(P_+(A) ∪ P_+(B)) = ceil(log2((2^a - 1) + (2^b - 1)))`
    - equivalently:
      - `b` if `a = 1`
      - `b + 1` if `a >= 2`
- Strongest correction learned:
  - the biclique residual controller is exactly logarithmic in residual-family
    size
  - the extra bit appears precisely when both sides carry nontrivial internal
    ambiguity

Next frontier after v172:

- turn the biclique ladder into a design rule, not just a family catalog
- compare balanced bicliques against stars and against pair-basis hybrids under
  the full ranking tuple
- if the design rule survives, promote balanced bicliques as the leading sparse
  pair candidate

## 2026-03-31, biclique balance extremal law

- New structural target:
  - determine which part of the biclique ladder is actually best, rather than
    treating all bicliques as equally plausible sparse pair loops
- Assumption:
  - fixed total size:
    - `n = a + b`
  - biclique ladder with:
    - `a <= b`
  - use exact formulas from `v171` and `v172`
- Strongest bounded results:
  - checks:
    - all `2 <= n <= 20`
  - exact monotonicity:
    - `pure_classes(a, n-a)` increases strictly toward balance
    - `budget(a, n-a)` decreases weakly toward balance
- Strongest correction learned:
  - stars are the sparse edge of the biclique family
  - balanced bicliques are the high-pure, low-depth edge
  - this is the first real geometry design rule in the sparse pair branch

Next frontier after v173:

- compare balanced bicliques directly against the pair-basis plus
  block-separator hybrid under:
  - witness size
  - pure resolved mass
  - residual depth
  - residual controller size
- ask whether there is a non-biclique graph family that beats balanced
  bicliques on the same tuple

## 2026-03-31, balanced biclique versus pair-basis tradeoff law

- New structural target:
  - quantify the exact sparse-versus-dense tradeoff between the leading sparse
    pair family and the strongest dense pair family
- Assumption:
  - compare:
    - pair-basis hybrid
    - balanced biclique loop
  - full nonempty omission family
  - exact residual controllers from prior survivors
- Strongest bounded results:
  - checks:
    - all `2 <= n <= 32`
  - exact formulas:
    - pair basis:
      - `w_pair = n(n - 1)/2`
      - `pure_pair = 2^n - n - 1`
      - `depth_pair = ceil(log2 n)`
    - balanced biclique:
      - about half as many pair witnesses
      - pure loss only a subexponential slice
      - residual depth around `n/2`
- Strongest correction learned:
  - balanced bicliques are not simply better than the full pair basis
  - they are the leading sparse exact alternative:
    - much fewer witnesses
    - almost the same pure resolved mass
    - much deeper residual controller

Next frontier after v174:

- search graph-shaped pair families that improve on the balanced biclique
  tradeoff
- compare the best sparse pair loops directly against verifier-compilation
  style loops on shared bounded corpora

## 2026-03-31, complete multipartite pure-mass law

- New structural target:
  - unify the biclique and full-pair families under one graph-shaped algebra
- Assumption:
  - partition:
    - `R = P_1 ⊔ ... ⊔ P_t`
  - witness basis:
    - all pairs crossing different blocks
  - full nonempty omission family
- Strongest bounded results:
  - checks:
    - all integer partitions of `2 <= n <= 8`
  - exact laws:
    - `pure_classes = 2^n - 1 - sum_i(2^|P_i| - 1)`
    - `Residual = union_i P_+(P_i)`
- Strongest correction learned:
  - the pair branch is not just bicliques plus one full-pair endpoint
  - complete multipartite witness families form the right general algebra

Next frontier after v175:

- solve the design rule inside the complete multipartite family
- identify which multipartite partitions are best at fixed block count
- identify the ladder across block count

## 2026-03-31, balanced multipartite extremal law

- New structural target:
  - turn the multipartite family into a navigable design space at fixed block
    count
- Assumption:
  - fix:
    - total size `n`
    - block count `t`
  - compare all `t`-block integer partitions of `n`
- Strongest bounded results:
  - checks:
    - all `2 <= n <= 16`
    - all `1 <= t <= n`
  - exact extremal rule:
    - balanced partitions maximize pure resolved mass
    - balanced partitions minimize residual-family size
    - balanced partitions maximize witness count
- Strongest correction learned:
  - inside the complete multipartite family, move toward balanced blocks
  - balanced bicliques are just the `t = 2` balanced edge

Next frontier after v176:

- solve the monotone ladder across block count
- compare the balanced multipartite ladder against the older biclique-only
  story

## 2026-03-31, balanced multipartite ladder law

- New structural target:
  - connect balanced bicliques and the full pair basis into one monotone family
- Assumption:
  - fix `n`
  - for each `t`, take the balanced `t`-block multipartite partition
- Strongest bounded results:
  - checks:
    - all `2 <= n <= 32`
    - all `1 <= t <= n`
  - exact monotonicity:
    - pure resolved mass increases with `t`
    - residual-family size decreases with `t`
    - witness count increases with `t`
- Strongest correction learned:
  - balanced bicliques and the full pair basis are two points on one monotone
    balanced multipartite ladder
  - the real sparse-versus-dense pair frontier is now:
    - low `t` balanced multipartite
    - versus high `t` balanced multipartite

Next frontier after v177:

- exact residual-controller laws for general balanced multipartite residual
  families
- direct comparison between balanced multipartite loops and verifier-compilation
  style loops on shared bounded corpora

## 2026-03-31, balanced multipartite residual-controller law

- New structural target:
  - close the controller rung for the balanced multipartite ladder on the
    smallest honest grid before attempting a general theorem
- Assumption:
  - balanced multipartite residual families
  - block-intersection queries
  - exact bounded grid:
    - `2 <= n <= 7`
    - `2 <= t <= n`
- Strongest bounded results:
  - brute-force checks on the full balanced grid above
  - exact bounded law:
    - `budget_block(Residual_bal(n, t)) = ceil(log2 |Residual_bal(n, t)|)`
- Strongest correction learned:
  - on the checked balanced ladder, the residual controller is information
    optimal
  - the middle multipartite rungs are not just clean on the witness side, they
    also admit exact optimal block-query control on this bounded grid

Next frontier after v178:

- general proof or larger-grid corroboration for the balanced multipartite
  residual-controller law
- direct comparison between low-`t`, medium-`t`, and high-`t` balanced
  multipartite loops and verifier-compilation style loops

## 2026-03-31, balanced multipartite direct formula law

- New structural target:
  - compress the balanced multipartite ladder metrics into direct formulas from
    `(n, t)` rather than recomputing them from partitions
- Assumption:
  - balanced partition coordinates:
    - `n = t*q + r`
    - `q = floor(n / t)`
    - `r = n mod t`
- Strongest bounded results:
  - checks:
    - all `2 <= n <= 128`
    - all `1 <= t <= n`
  - exact direct formulas:
    - `residual_size(n, t) = (t + r) * 2^q - t`
    - `pure_classes(n, t) = 2^n - (t + r) * 2^q + t - 1`
    - `witness_count(n, t) = n(n - 1)/2 - t*q*(q - 1)/2 - r*q`
- Strongest correction learned:
  - the balanced multipartite ladder is now a direct metric compiler from
    `(n, t)` alone
  - this is the first direct-amount object on the loop-space geometry branch

Next frontier after v179:

- push the bounded residual-controller law toward a direct formula or broader
  proof
- compare the balanced multipartite direct compiler against
  verifier-compilation style loops on shared bounded families

## 2026-03-31, internal-clique pair witness law

- New structural target:
  - search for a second exact graph-shaped pair family, not based on
    cross-block witnesses
- Assumption:
  - partition:
    - `R = C_1 ⊔ ... ⊔ C_t`
  - witness basis:
    - all same-cluster pairs
- Strongest bounded results:
  - checks:
    - all integer partitions of `2 <= n <= 16`
  - exact laws:
    - `Residual = {M != ∅ | |M ∩ C_i| <= 1 for every i}`
    - `residual_size = Π_i (1 + s_i) - 1`
    - `pure_classes = 2^n - Π_i (1 + s_i)`
    - `witness_count = Σ_i s_i(s_i - 1)/2`
- Strongest correction learned:
  - the pair-witness branch already has at least two exact geometric
    directions:
    - cross-block multipartite witnesses
    - same-cluster internal-clique witnesses

Next frontier after v180:

- compare these two exact families on shared witness budgets
- test whether the balanced multipartite ladder is actually the whole pure
  frontier, or only one side of it

## 2026-03-31, pair-witness pure frontier correction law

- New structural target:
  - test the full small-graph pure frontier against the balanced multipartite
    story
- Assumption:
  - exhaustive simple graphs with:
    - `2 <= n <= 7`
  - compare:
    - graph optimum
    - balanced multipartite frontier
    - internal-clique cluster frontier
- Strongest bounded results:
  - first strict balanced gap:
    - `(n, m) = (5, 6)`
    - `OPT_pure = 22`
    - `BAL_pure = 21`
  - larger balanced gaps:
    - `(6, 9) -> gap 2`
    - `(7, 12) -> gap 6`
    - `(7, 16) -> gap 1`
  - cluster family exact-hit counts:
    - `n=2: 2/2`
    - `n=3: 3/3`
    - `n=4: 5/5`
    - `n=5: 6/7`
    - `n=6: 9/9`
    - `n=7: 10/13`
- Strongest correction learned:
  - the balanced multipartite ladder is not the full pair-witness pure
    frontier
  - internal-clique loops explain a large part of the frontier, but not all of
    it

Next frontier after v181:

- characterize the remaining pure-optimal graph families outside both:
  - balanced multipartite
  - internal-clique cluster
- compare those stronger pair-witness loops directly against
  verifier-compilation style loops on shared bounded families

## 2026-03-31, cograph pair frontier law

- New structural target:
  - close the flat pair families under recursive union and join
- Assumption:
  - cographs on labeled vertices
  - compare their best pure frontier against the exact global frontier from
    `v181`
- Strongest bounded results:
  - cographs realize the full global pure frontier for:
    - `2 <= n <= 4`
  - for each of:
    - `n = 5`
    - `n = 6`
    - `n = 7`
    - they miss exactly one budget
  - exact misses:
    - `(5, 5) -> 21 versus 20`
    - `(6, 8) -> 50 versus 48`
    - `(7, 10) -> 109 versus 107`
- Strongest correction learned:
  - recursive union-and-join pair loops are far stronger than the earlier flat
    families
  - but they are still not the whole frontier

Next frontier after v182:

- characterize the missing non-cograph repair gadget
- test whether one small structural extension above cographs closes the checked
  frontier

## 2026-03-31, clique-bridge optimum law

- New structural target:
  - identify the exact repair gadget above the cograph family
- Assumption:
  - `B(a, b)` is two cliques:
    - `K_a`
    - `K_b`
  - plus exactly one bridge edge between distinguished vertices
- Strongest bounded results:
  - direct formulas:
    - `witness_count = C(a, 2) + C(b, 2) + 1`
    - `residual_size = (a + b) + ab - 1`
    - `pure_classes = 2^(a + b) - (a + b) - ab`
  - exact bounded optimum law:
    - for every `a, b >= 1` with `a + b <= 7`,
      `B(a, b)` attains the exact global optimum at its own witness budget
- Strongest correction learned:
  - the missing rung above cographs is not arbitrary
  - one bridge between cliques already recovers an exact bounded optimum ladder

Next frontier after v183:

- move from two-clique bridges to tree-of-cliques or block-graph ladders
- compare:
  - cographs
  - clique-bridge ladders
  - verifier-compilation style loops
  on shared bounded families

## 2026-03-31, two-family frontier cover law

- New structural target:
  - compress the checked optimal pair-witness frontier into the smallest
    current family cover
- Assumption:
  - exact global frontier from `v181`
  - cograph frontier from `v182`
  - clique-bridge ladder from `v183`
  - shared domain:
    - `2 <= n <= 7`
- Strongest bounded results:
  - total checked frontier budgets:
    - `62`
  - covered by:
    - cographs or clique bridges
    - `62`
  - bridge-only repairs are exactly:
    - `(5, 5)`
    - `(6, 8)`
    - `(7, 10)`
  - cographs already cover the remaining:
    - `59`
- Strongest correction learned:
  - the current checked frontier is already compactly spanned by two
    structured families
  - broader graph search is now the wrong default baseline

Next frontier after v184:

- find the smallest recursive closure that contains both:
  - cographs
  - clique bridges
- compare this two-family baseline directly against verifier-compilation style
  loops on shared bounded families

## 2026-03-31, bridge-cograph frontier law

- New structural target:
  - unify the cograph and clique-bridge survivors into one recursive family
- Assumption:
  - bridge-cographs are generated from singletons by:
    - disjoint union
    - complete join
    - single-edge join
  - compare their best frontier against the exact global frontier from `v181`
  - shared domain:
    - `2 <= n <= 7`
- Strongest bounded results:
  - full exact frontier hit for every checked `n` from:
    - `2` through `7`
  - labeled family counts:
    - `n=2 -> 2`
    - `n=3 -> 8`
    - `n=4 -> 64`
    - `n=5 -> 952`
    - `n=6 -> 22304`
    - `n=7 -> 716186`
- Strongest correction learned:
  - the branch now has one recursive closure that already covers the full
    checked frontier
  - the next search target should be a smaller exact subfamily, not a broader
    graph universe

Next frontier after v185:

- compress the bridge-cograph closure into a smaller exact subfamily
- compare the bridge-cograph recursive baseline directly against
  verifier-compilation style loops on shared bounded families

## 2026-03-31, twin-pendant frontier law

- New structural target:
  - compress the bridge-cograph closure into a smaller exact local grammar
- Assumption:
  - start from one vertex
  - add the new largest-labeled vertex only as:
    - a pendant
    - a false twin
    - a true twin
  - compare the resulting frontier against the exact global frontier from
    `v181`
  - shared domain:
    - `2 <= n <= 7`
- Strongest bounded results:
  - full exact frontier hit for every checked `n` from:
    - `2` through `7`
  - family counts:
    - `2, 6, 35, 308, 3662, 54089`
  - compression versus bridge-cographs at `n = 7`:
    - `716186 / 54089`
- Strongest correction learned:
  - the full checked frontier does not need the whole bridge-cograph closure
  - a much smaller local growth grammar already suffices

Next frontier after v186:

- compress the twin-pendant family further, if possible
- compare twin-pendant loops directly against verifier-compilation style loops
  on shared bounded families

## 2026-03-31, local move necessity law

- New structural target:
  - test whether the compressed twin-pendant grammar is still reducible at the
    move level
- Assumption:
  - evaluate all nonempty subsets of:
    - pendant
    - false twin
    - true twin
  - compare each subset against the exact global frontier from `v181`
  - shared domain:
    - `2 <= n <= 7`
- Strongest bounded results:
  - only the full triple hits:
    - `62 / 62`
  - strongest strict subset:
    - `{false twin, true twin}`
    - `59 / 62`
    - misses exactly:
      - `(5, 5)`
      - `(6, 8)`
      - `(7, 10)`
  - other pairs are much weaker:
    - pendant plus true twin:
      - `34 / 62`
    - pendant plus false twin:
      - `24 / 62`
- Strongest correction learned:
  - on the checked domain, all three local moves are necessary for full
    frontier coverage
  - the twin-pendant grammar is not obviously reducible by dropping one move

Next frontier after v187:

- search for a normal form or smaller exact grammar inside the full
  twin-pendant family
- compare the checked-minimal twin-pendant baseline directly against
  verifier-compilation style loops on shared bounded families

## 2026-03-31, single-pendant frontier law

- New structural target:
  - compress the twin-pendant baseline by bounding the number of pendant events
- Assumption:
  - use:
    - false twin
    - true twin
    - pendant
  - but allow pendant budget only in:
    - `0, 1, 2, 3`
  - compare against the exact global frontier from `v181`
  - shared domain:
    - `2 <= n <= 7`
- Strongest bounded results:
  - pendant budget `0`:
    - `59 / 62`
    - misses exactly:
      - `(5, 5)`
      - `(6, 8)`
      - `(7, 10)`
  - pendant budget `1`:
    - `62 / 62`
  - larger budgets:
    - no extra checked frontier coverage
- Strongest correction learned:
  - the bridge-style budgets do not need arbitrary pendant use
  - one pendant event already restores the whole checked frontier

Next frontier after v188:

- search for a canonical placement rule for the one pendant event
- compare the one-pendant twin baseline directly against verifier-compilation
  style loops on shared bounded families

## 2026-03-31, late-pendant frontier law

- New structural target:
  - compress the one-pendant normal form by restricting where the pendant may
    occur
- Assumption:
  - use one-pendant twin growth
  - permit the single pendant only in the final tail window of sizes:
    - `1, 2, 3, 4, 5, 6`
  - compare against the exact global frontier from `v181`
  - shared domain:
    - `2 <= n <= 7`
- Strongest bounded results:
  - tail window `1`:
    - `61 / 62`
    - misses exactly:
      - `(7, 10)`
  - tail window `2`:
    - `62 / 62`
  - larger tail windows:
    - no extra checked frontier coverage
- Strongest correction learned:
  - the single pendant does not need arbitrary placement
  - on the checked domain it can be delayed to one of the final two steps

Next frontier after v189:

- search for an anchor rule for the late pendant event
- compare the late one-pendant twin baseline directly against
  verifier-compilation style loops on shared bounded families

## 2026-03-31, root-anchored late-pendant law

- New structural target:
  - compress the late-pendant normal form by fixing the pendant anchor
- Assumption:
  - use one-pendant twin growth
  - restrict the pendant to:
    - the oldest existing vertex
  - and to tail windows:
    - `1, 2, 3`
  - compare against the exact global frontier from `v181`
  - shared domain:
    - `2 <= n <= 7`
- Strongest bounded results:
  - root-anchored tail window `1`:
    - `61 / 62`
    - misses exactly:
      - `(7, 10)`
  - root-anchored tail window `2`:
    - `62 / 62`
  - root-anchored tail window `3`:
    - still `62 / 62`
- Strongest correction learned:
  - the pendant does not need arbitrary anchor choice
  - on the checked domain it can attach to the root and still preserve the
    whole frontier once the final-two-step allowance is given

Next frontier after v190:

- explain the special `(7, 10)` obstruction to final-step root anchoring
- compare the root-anchored late-pendant baseline directly against
  verifier-compilation style loops on shared bounded families

## 2026-03-31, final-step obstruction law

- New structural target:
  - explain the single surviving miss at:
    - `(n, m) = (7, 10)`
  - for root-anchored final-step-only growth
- Assumption:
  - enumerate all:
    - `7`-vertex
    - `10`-edge
    graphs
  - enumerate all states in the root-anchored final-step-only family
- Strongest bounded results:
  - exact optimum graphs at `(7,10)`:
    - `420`
  - every exact optimum is leafless:
    - minimum degree `2`
    - degree multiset:
      - `[2, 2, 3, 3, 3, 3, 4]`
  - best final-step-only branch without pendant:
    - `107`
  - best final-step-only branch with pendant:
    - `107`
- Strongest correction learned:
  - the remaining miss is a true structural obstruction
  - it comes from the interaction of:
    - leaflessness of the exact optimum
    - forced leaf in the pendant-used branch
    - twin-only ceiling in the no-pendant branch

Next frontier after v191:

- explain why allowing the pendant one step earlier repairs `(7, 10)`
- compare the root-anchored late-pendant baseline directly against
  verifier-compilation style loops on shared bounded families

## 2026-03-31, pendant-true-twin repair law

- New structural target:
  - classify the repaired `(7, 10)` branch by its final-two-step motif
  - check whether the optimum is diffuse or concentrated in one local pattern
- Assumption:
  - enumerate all states in:
    - root-anchored tail-window-two one-pendant twin growth
  - keep only the focused budget:
    - `(n, m) = (7, 10)`
- Strongest bounded results:
  - exact global optimum:
    - `109`
  - unique optimal final-two-step pattern:
    - `pendant -> true_twin`
  - all other final-two-step patterns:
    - `<= 107`
  - optimal family states:
    - `2`
  - optimal family graphs:
    - `1`
- Strongest correction learned:
  - the repaired branch is not a vague two-step effect
  - it is concentrated in one exact local repair motif:
    - penultimate root pendant
    - final true-twin lift of the new pendant leaf

Next frontier after v192:

- search for more exact repair motifs above compressed normal forms
- compare the repaired compressed loop directly against verifier-compilation
  style loops on shared bounded families

## 2026-03-31, bridge-budget motif narrowing law

- New structural target:
  - check whether the `(7, 10)` repair motif is isolated or part of a small
    bridge-budget library
- Assumption:
  - stay in:
    - root-anchored tail-window-two one-pendant twin growth
  - compare the three bridge-style repaired budgets:
    - `(5, 5)`
    - `(6, 8)`
    - `(7, 10)`
- Strongest bounded results:
  - exact optimal motif library at `(5, 5)`:
    - `pendant -> true_twin`
    - `true_twin -> pendant`
  - exact optimal motif library at `(6, 8)`:
    - `pendant -> true_twin`
    - `true_twin -> pendant`
  - exact optimal motif library at `(7, 10)`:
    - `pendant -> true_twin`
- Strongest correction learned:
  - the repaired bridge budgets form a small exact motif ladder
  - the final-step pendant branch survives at the smaller repaired budgets
  - it drops out exactly at the leafless rung

Next frontier after v193:

- search for richer motif libraries on other repaired budgets
- compare motif-library loops directly against verifier-compilation style
  baselines

## 2026-03-31, hybrid controller advantage law

- New structural target:
  - compare a direct compiled controller against a hybrid quotient-question
    loop on the same bounded omission-identification task
- Assumption:
  - task:
    - identify `M` exactly over `F_all`
  - direct controller:
    - block-intersection queries on the raw family
  - hybrid controller:
    - pair-basis observation plus block-intersection residual controller
  - scope:
    - compare controller depth only
    - do not count witness-acquisition cost
- Strongest bounded results:
  - direct controller depth:
    - `n`
  - hybrid residual-controller depth:
    - `ceil(log2 n)`
  - exact gap:
    - `n - ceil(log2 n)`
- Strongest correction learned:
  - the branch now has an exact scoped win over a direct controller
  - this is the cleanest current bounded reason to say some hybrid loops are
    stronger than plain verifier-compilation style controllers

Next frontier after v194:

- compare the motif-library branch directly against verifier-compilation style
  baselines
- search for exact cost models that include witness acquisition, not just
  residual controller depth

## 2026-03-31, weighted hybrid-value law

- New structural target:
  - replace the scoped controller-depth comparison with an explicit loop-value
    model that prices:
    - acquisition
    - pure resolved mass
    - residual controller depth
- Assumption:
  - task:
    - exact missing-set identification over `F_all`
  - compare:
    - direct block controller
    - pair-plus-atom hybrid
    - pair-plus-block hybrid
  - weighted value:
    - `U = alpha * pure_resolved_mass + beta * depth_saving - gamma * acquisition`
- Strongest bounded results:
  - `A_pair(n) = C(n, 2)`
  - `P_pair(n) = 2^n - n - 1`
  - `G_block(n) = n - ceil(log2 n)`
  - `G_atom(n) = 1`
  - exact win boundary for pair-plus-block:
    - `alpha * (2^n - n - 1) + beta * (n - ceil(log2 n)) > gamma * C(n, 2)`
- Strongest correction learned:
  - “better loop” claims now have an honest exact boundary
  - the motif-library branch should be compared using the same decomposed cost
    model, not only by controller depth

Next frontier after v195:

- price the motif-library branch with the same weighted model
- compare motif-library loops directly against verifier-compilation style
  baselines under that shared cost model

## 2026-03-31, bridge-budget weighted pricing law

- New structural target:
  - price the first motif-family branch under the same weighted loop-value
    model used for quotient-question loops
- Assumption:
  - motif family:
    - clique-bridge witness loops
  - focused exact bridge budgets:
    - `(5, 5)`
    - `(6, 8)`
    - `(7, 10)`
  - compare:
    - direct block baseline
    - pair-plus-block hybrid
    - clique-bridge motif loop
- Strongest bounded results:
  - clique-bridge residual controller depths:
    - `4`, `4`, `5`
  - under unit weights, clique-bridge beats direct on all three budgets
  - under unit weights, pair-plus-block still wins against clique-bridge
  - exact switching boundary for clique-bridge versus pair-plus-block:
    - acquisition-price dominated on each budget
- Strongest correction learned:
  - motif loops are now priced in the same framework as quotient-question loops
  - the branch has its first exact motif-side phase boundary

Next frontier after v196:

- price wider motif families, not only clique bridges
- search for motif families that beat pair-plus-block on unit or near-unit
  weights

## 2026-03-31, balanced ladder weighted frontier law

- New structural target:
  - price the full balanced multipartite ladder against the dense pair endpoint
    on the checked exact grid
- Assumption:
  - weighted value:
    - `U = alpha * pure_resolved_mass + beta * depth_saving - gamma * acquisition`
  - family:
    - balanced multipartite ladder
  - checked exact grid:
    - `2 <= n <= 7`
- Strongest bounded results:
  - full pair basis is always unit-weight optimal or tied on the checked grid
  - from `n = 5` onward, a near-dense balanced rung already catches it at unit
    weights
  - and overtakes it once:
    - `gamma > alpha`
    - under `alpha = beta = 1`
- Strongest correction learned:
  - sparse balanced rungs are real contenders under acquisition-sensitive
    pricing
  - but no checked balanced rung beats the full pair basis under unit weights

Next frontier after v197:

- widen the same weighted search to more exact families
- search for any exact family that beats pair-plus-block on unit or near-unit
  weights

## 2026-03-31, pair-graph total-domination correction law

- New structural target:
  - repair the graph-shaped pair branch by replacing the edge-containing proxy
    with the true observation-quotient purity metric
- Assumption:
  - pair-witness graph:
    - `G = (V, E)`
  - full observation:
    - `O_G(M) = E(G[M])`
- Strongest bounded results:
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
- Strongest correction learned:
  - the post-`v181` graph branch was using the wrong purity metric
  - true graph-shaped pair purity is controlled by total domination, not by
    mere edge presence

Next frontier after v198:

- rebuild the graph-family frontier on:
  - `pure_classes_true(G) = TD(G)`
- test first whether the balanced complete multipartite ladder survives the
  correction

## 2026-03-31, corrected balanced-ladder frontier law

- New structural target:
  - compare the exhaustive corrected true frontier against the balanced
    complete multipartite ladder
- Assumption:
  - true purity metric:
    - `pure_classes_true(G) = TD(G)`
  - checked exact graph domain:
    - `2 <= n <= 6`
- Strongest bounded results:
  - every balanced ladder budget hits the exact true frontier on the checked
    domain
  - the earlier balanced gaps were proxy artifacts
- Strongest correction learned:
  - the balanced complete multipartite ladder survives the move back to the
    true observation quotient
  - the fancy bridge and cograph proxy branch should be treated as archived
    until rebuilt on the corrected metric

Next frontier after v199:

- extend the corrected true frontier beyond `n <= 6`
- search for any non-balanced family that really beats the balanced ladder on
  the corrected metric
- only then rebuild weighted loop comparisons on graph-shaped pair families

## 2026-03-31, corrected complete-multipartite frontier law

- New structural target:
  - widen the corrected balanced-ladder survivor to the full complete
    multipartite family
- Assumption:
  - true purity metric:
    - `pure_classes_true(G) = TD(G)`
  - checked exact graph domain:
    - `2 <= n <= 6`
- Strongest bounded results:
  - every witness budget represented by a complete multipartite graph hits the
    exact true frontier on the checked domain
  - the remaining corrected gaps are therefore exactly the budgets not
    representable by complete multipartite graphs
- Strongest correction learned:
  - the live corrected graph frontier is stronger than the balanced ladder
  - the next honest search target is now narrow and explicit

Next frontier after v200:

- extend the corrected complete multipartite comparison beyond `n <= 6`
- search uncovered budgets for genuinely non-complete-multipartite exact
  families

## 2026-03-31, corrected complete-multipartite frontier extension law

- New structural target:
  - extend the corrected complete multipartite frontier from `n <= 6` to
    `n <= 7`
- Assumption:
  - true purity metric:
    - `pure_classes_true(G) = TD(G)`
  - family:
    - full complete multipartite graphs
  - checked exact graph domain:
    - `2 <= n <= 7`
- Strongest bounded results:
  - every witness budget represented by a complete multipartite graph hits the
    exact true frontier on the checked domain
  - representative `n = 7` covered budgets include:
    - `6, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20, 21`
- Strongest correction learned:
  - the corrected graph baseline now survives through the same `n = 7` ceiling
    as the earlier proxy branch

Next frontier after v201:

- search simple edge repairs above the corrected complete multipartite baseline
- ask whether one internal edge already yields a clean invariant family

## 2026-03-31, multipartite large-block edge invariance law

- New structural target:
  - test one-edge repairs above complete multipartite graphs under the
    corrected true purity metric
- Assumption:
  - start with a complete multipartite graph
  - add one internal edge inside a block of size at least `3`
- Strongest bounded results:
  - exhaustive checks on `2 <= n <= 7` find no counterexample to:
    - `TD(G_P + e) = TD(G_P)`
- Strongest correction learned:
  - one repaired internal edge is already a real exact family axis above the
    corrected multipartite baseline

Next frontier after v202:

- treat complete multipartite plus one internal edge as a family
- compare that whole family against the exhaustive true frontier

## 2026-03-31, corrected one-edge multipartite frontier cover law

- New structural target:
  - compare the family:
    - complete multipartite
    - plus one internal edge
  against the exhaustive corrected true frontier
- Assumption:
  - true purity metric:
    - `pure_classes_true(G) = TD(G)`
  - checked exact graph domain:
    - `2 <= n <= 7`
- Strongest bounded results:
  - every budget the family defines hits the exact true frontier
  - remaining uncovered `n = 7` budgets are exactly:
    - `2, 3, 4, 5, 8, 9`
- Strongest correction learned:
  - the live corrected graph-side search target is now a small uncovered set
    above the one-edge repaired multipartite baseline

Next frontier after v203:

- search the remaining uncovered budgets with two-edge or other low-complexity
  repairs above complete multipartite graphs

## 2026-03-31, corrected two-edge multipartite frontier cover law

- New structural target:
  - widen the corrected repaired-family baseline from one internal edge to up
    to two internal edges
- Assumption:
  - true purity metric:
    - `pure_classes_true(G) = TD(G)`
  - family:
    - complete multipartite plus up to two internal edges
  - checked exact graph domain:
    - `2 <= n <= 7`
- Strongest bounded results:
  - every defined family budget hits the exact true frontier
  - remaining uncovered `n = 7` budgets are exactly:
    - `3, 4, 5, 9`
- Strongest correction learned:
  - the low-complexity repaired-family ladder is real
  - the live graph search target is now only four budgets at `n = 7`

Next frontier after v204:

- classify the remaining uncovered budgets:
  - `3, 4, 5, 9`
- look for exact low-complexity families rather than broad graph search

## 2026-03-31, star-plus-leaf-graph decomposition law

- New structural target:
  - explain the remaining high star-side holdouts structurally instead of only
    by frontier coverage
- Assumption:
  - graph family:
    - star on `k` leaves
    - plus arbitrary leaf graph `H`
- Strongest bounded results:
  - exact decomposition law:
    - `TD(G) = (2^k - 1) + TD(H)`
  - exhaustive leaf-graph checks:
    - `1 <= k <= 6`
  - representative consequences:
    - shared-leaf two-edge correction keeps:
      - `63`
    - perfect matching correction yields:
      - `64`
- Strongest correction learned:
  - the star-side holdouts reduce to optimizing `TD(H)` at fixed leaf-edge
    budget

Next frontier after v205:

- classify the leaf-graph optimizer for small edge budgets
- integrate that with the remaining uncovered budget set:
  - `3, 4, 5, 9`

## 2026-03-31, disjoint-union total-domination product law

- New structural target:
  - turn the disconnected corrected graph branch into an exact product law
- Assumption:
  - disjoint simple graphs `G` and `H`
  - corrected true purity metric:
    - `pure_classes_true(G) = TD(G)`
- Strongest bounded results:
  - exact factorization:
    - `TD(G union H) = TD(G) * TD(H)`
  - exhaustive graph-pair checks:
    - `1 <= |V(G)| <= 4`
    - `1 <= |V(H)| <= 4`
- Strongest correction learned:
  - disconnected corrected graph search should be treated as product geometry,
    not as one more flat frontier scan

Next frontier after v206:

- use the product law to explain the remaining low-budget corrected holdouts
- search for a direct low-edge frontier formula instead of more ad hoc family
  enumeration

## 2026-03-31, balanced star-forest low-edge frontier law

- New structural target:
  - solve the corrected low-edge graph frontier directly on:
    - `0 <= m <= n - 1`
- Assumption:
  - corrected true purity metric:
    - `pure_classes_true(G) = TD(G)`
  - checked exact graph domain:
    - `2 <= n <= 7`
  - balanced star-forest value:
    - `c = n - m`
    - `n = c*q + r`
    - `F_bal(n, m) = (2^(q - 1) - 1)^(c - r) * (2^q - 1)^r`
- Strongest bounded results:
  - exact threshold law:
    - frontier is `0` if `m < ceil(n / 2)`
  - exact low-edge frontier law:
    - frontier is `F_bal(n, m)` if `ceil(n / 2) <= m <= n - 1`
  - representative corrected `n = 7` values:
    - `m = 4 -> 3`
    - `m = 5 -> 21`
    - `m = 6 -> 63`
  - leaf consequence:
    - `F_bal(6, 3) = 1`
- Strongest correction learned:
  - the corrected low-budget holdouts:
    - `3, 4, 5`
    are no longer open
  - combined with `v205`, the corrected `n = 7`, budget `9` optimum is also
    structurally explained

Next frontier after v207:

- unify the corrected graph frontier into a cleaner regime map:
  - low-edge balanced star forests
  - repaired multipartite families
  - star-plus-leaf corrections
- search higher-budget exact families beyond the current repaired multipartite
  ladder

## 2026-03-31, corrected small-n graph regime-cover law

- New structural target:
  - synthesize the corrected graph branch into one checked small-`n` regime map
- Assumption:
  - checked exact graph domain:
    - `2 <= n <= 7`
  - allowed corrected regimes:
    - low-edge balanced star forests
    - complete multipartite plus up to two internal edges
    - star plus low-edge leaf corrections
- Strongest bounded results:
  - every exact true frontier budget is covered by at least one allowed regime
  - representative assignments:
    - `n = 7`, `m = 4 ->` low-edge balanced star forest
    - `n = 7`, `m = 9 ->` star plus low-edge leaf correction
    - `n = 7`, `m = 12 ->` repaired multipartite
- Strongest correction learned:
  - the corrected graph branch no longer ends as a list of local patches
  - it now has a coherent checked small-`n` regime map

Next frontier after v208:

- extend the corrected regime cover beyond `n = 7`
- or compress the higher-budget repaired multipartite side into a cleaner
  direct law

## 2026-03-31, multipartite repaired-block additivity law

- New structural target:
  - compress the corrected repaired multipartite side into one additive law
- Assumption:
  - complete multipartite partition:
    - `P_1, ..., P_t`
    - `t >= 2`
  - arbitrary internal graph `H_i` inside each block
  - checked exact domain:
    - every nontrivial partition with `2 <= n <= 7`
- Strongest bounded results:
  - exact additive law:
    - `TD(G) = base(P_1, ..., P_t) + sum_i TD(H_i)`
  - star-plus-leaf law is recovered as the `(1, k)` special case
  - one-edge invariance in large blocks is recovered as the `TD(H_i) = 0`
    special case
- Strongest correction learned:
  - the repaired multipartite side is not a bag of local exceptions
  - it has a clean blockwise additive structure

Next frontier after v209:

- turn that additive structure into a direct optimizer on a significant budget
  regime

## 2026-03-31, low-edge repaired-multipartite optimizer law

- New structural target:
  - solve the repaired multipartite side directly on the low-edge internal
    budget regime
- Assumption:
  - complete multipartite partition with block sizes `s_i`
  - per-block low-edge budgets:
    - `0 <= e_i <= s_i - 1`
  - checked exact domain:
    - every nontrivial partition with `2 <= n <= 7`
- Strongest bounded results:
  - exact optimizer:
    - `OPT(parts; e_1, ..., e_t) = base(parts) + sum_i F_bal(s_i, e_i)`
  - representative consequences:
    - `(1, 6)` with `(0, 3) -> 64`
    - `(3, 4)` with `(2, 0) -> 108`
    - `(2, 5)` with `(1, 0) -> 94`
- Strongest correction learned:
  - the repaired multipartite side now has a direct amount law on a large
    structured subfamily

Next frontier after v210:

- extend that optimizer beyond the low-edge internal-budget regime
- or fold it into a fuller corrected regime map beyond `n = 7`

## 2026-03-31, repaired-multipartite recursive optimizer law

- New structural target:
  - remove the low-edge restriction from the repaired multipartite optimizer
- Assumption:
  - complete multipartite partition with block sizes `s_i`
  - arbitrary per-block edge budgets:
    - `0 <= e_i <= C(s_i, 2)`
  - checked exact domain:
    - every nontrivial partition with `2 <= n <= 7`
- Strongest bounded results:
  - exact recursive optimizer:
    - `OPT_repaired(parts; e_1, ..., e_t) = base(parts) + sum_i OPT_graph(s_i, e_i)`
  - representative consequences:
    - `(1, 6)` with `(0, 3) -> 64`
    - `(3, 4)` with `(2, 3) -> 115`
    - `(2, 5)` with `(1, 4) -> 109`
- Strongest correction learned:
  - repaired multipartite coupling is no longer the difficult part
  - the real remaining target is the single-block frontier:
    - `OPT_graph(s, e)`

Next frontier after v211:

- compress the single-block frontier `OPT_graph(s, e)` itself
- or extend the corrected regime map beyond `n = 7`

## 2026-03-31, threshold single-block miss law

- New structural target:
  - test whether the corrected single-block frontier collapses to threshold
    graphs
- Assumption:
  - corrected single-block domain:
    - `2 <= n <= 7`
- Strongest bounded results:
  - threshold graphs miss exactly:
    - `n = 4`: `2, 4`
    - `n = 5`: `3, 6, 8`
    - `n = 6`: `3, 4, 8, 9, 10, 11, 12, 13`
    - `n = 7`: `4, 5, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19`
  - representative gaps:
    - `n = 4`, `m = 2`: `1` versus `0`
    - `n = 6`, `m = 8`: `45` versus `31`
    - `n = 7`, `m = 10`: `93` versus `63`
- Strongest correction learned:
  - the corrected single-block frontier does not collapse to threshold graphs

Next frontier after v212:

- test whether split graphs recover any of those threshold misses
- if not, skip the threshold-to-split ladder entirely

## 2026-03-31, threshold-split collapse law

- New structural target:
  - test whether split graphs strictly improve the threshold frontier on the
    corrected single-block branch
- Assumption:
  - corrected single-block domain:
    - `2 <= n <= 7`
- Strongest bounded results:
  - exact equality:
    - `OPT_threshold(n, m) = OPT_split(n, m)`
    - on every checked budget
  - threshold and split graphs have the same miss set against the full
    corrected frontier
- Strongest correction learned:
  - non-threshold split structure is inert on the checked single-block
    frontier

Next frontier after v214:

- move directly to genuinely non-split single-block families
- or search a direct regime law for `OPT_graph(s, e)` itself

## 2026-03-31, corrected small-domain single-block regime compiler law

- New structural target:
  - compress the corrected single-block frontier into one direct max-over-regimes
    evaluator
- Assumption:
  - checked domain:
    - `2 <= n <= 7`
  - allowed regimes:
    - balanced star forests
    - complete multipartite plus up to two internal edges
    - full star plus low-edge leaf correction
- Strongest bounded results:
  - exact direct amount compiler:
    - `OPT_graph(n, m)` equals the maximum of the three regime compilers
  - representative winners:
    - `n = 7`, `m = 4 -> 3`
    - `n = 7`, `m = 9 -> 64`
    - `n = 7`, `m = 12 -> 105`
- Strongest correction learned:
  - the corrected single-block branch is no longer only a descriptive regime
    map on the checked small domain
  - it is now a direct amount compiler

Next frontier after v215:

- check whether the third regime is broadly necessary
- or compress it into a tiny explicit exception set

## 2026-03-31, one-point corrected single-block compiler law

- New structural target:
  - compress the three-regime corrected single-block compiler further
- Assumption:
  - checked domain:
    - `2 <= n <= 7`
- Strongest bounded results:
  - removing the full-star-plus-leaf regime leaves exactly one miss:
    - `(7, 9)`
  - exact one-point direct compiler:
    - `OPT_graph(n, m)` equals the maximum of:
      - balanced star forests
      - complete multipartite plus up to two internal edges
      - the point correction `(7, 9) -> 64`
- Strongest correction learned:
  - the third regime is not broadly necessary on the checked domain
  - it compresses to one explicit exceptional point

Next frontier after v217:

- explain or generalize the exceptional point `(7, 9)`
- or extend the corrected direct compiler beyond `n = 7`

## 2026-03-31, exceptional point structure law at `(7, 9)`

- New structural target:
  - explain the point correction in the corrected single-block compiler
- Assumption:
  - focus only on the corrected exceptional point:
    - `(n, m) = (7, 9)`
- Strongest bounded results:
  - exact optimum:
    - `64`
  - every optimal graph is isomorphic to:
    - a full star plus a perfect matching on the six leaves
  - optimal labeled graph count:
    - `105`
  - optimal isomorphism type count:
    - `1`
- Strongest correction learned:
  - the point correction is not a bare lookup entry
  - it has a clean motif-level explanation

Next frontier after v218:

- test whether the star-plus-perfect-matching motif persists beyond `(7, 9)`
- or explain why it appears exactly there and not at earlier checked budgets

## 2026-03-31, star-plus-perfect-matching total-domination law

- New structural target:
  - turn the exceptional-point motif into a reusable exact family law
- Assumption:
  - `F_r` is one center joined to `2r` leaves, plus a perfect matching on the
    leaves
- Strongest bounded results:
  - exact closed form:
    - `TD(F_r) = 2^(2r)`
  - checked for:
    - `1 <= r <= 6`
  - representative values:
    - `r = 1 -> 4`
    - `r = 2 -> 16`
    - `r = 3 -> 64`
- Strongest correction learned:
  - the exceptional-point motif is not only a one-off witness
  - it has a clean exact family law

Next frontier after v219:

- compare the family against the checked frontier at the odd points where it
  lands
- or search whether the motif becomes frontier-optimal again beyond the
  checked small domain

## 2026-03-31, odd-line regime selector law in the corrected compiler family

- New structural target:
  - explain how the corrected compiler family itself selects regimes on the odd
    line `n = 2r + 1`, `m = 3r`
- Assumption:
  - current regime family:
    - balanced star forests
    - multipartite plus up to two internal edges
    - star-plus-low-edge leaf
- Strongest bounded results:
  - balanced star forests are never available on that line
  - multipartite plus up to two internal edges is reachable iff:
    - `r <= 2`
  - star-plus-leaf has exact value:
    - `2^(2r)`
  - selector pattern on checked `1 <= r <= 8`:
    - tie at `r = 1`
    - multipartite win at `r = 2`
    - star-plus-leaf as the only available regime for `r >= 3`
- Strongest correction learned:
  - the odd-line switch at `r = 3` is now structurally explained inside the
    current compiler family

Next frontier after v221:

- compare star-plus-matching against the true frontier beyond the checked odd
  points
- or search nearby motif families that dominate it where it fails to be
  frontier-optimal

## 2026-03-31, full-star-plus-low-edge family compiler law

- New structural target:
  - lift the odd-line perfect-matching branch into a wider exact family law
- Assumption:
  - checked family band:
    - `2 <= n <= 8`
    - `n - 1 <= m <= 2n - 3`
  - family:
    - one center joined to all leaves
    - plus an arbitrary low-edge leaf graph
- Strongest bounded results:
  - exact direct family compiler:
    - `OPT_star_leaf(n, m) = (2^(n - 1) - 1) + F_bal(n - 1, m - (n - 1))`
  - below the leaf no-isolate threshold:
    - the family collapses to the plain star value
  - representative checked rows:
    - `n = 7, m = 8 -> 63`
    - `n = 7, m = 9 -> 64`
    - `n = 7, m = 11 -> 94`
- Strongest correction learned:
  - the odd-line perfect-matching case is one middle rung of a larger exact
    star-plus-leaf band
  - the star-plus-leaf branch is now a reusable family compiler, not only an
    exceptional-point motif

Next frontier after v223:

- compare the full-star-plus-low-edge family against the true frontier on the
  checked overlap
- or search where the family remains frontier-optimal beyond the odd line

## 2026-03-31, high-band two-regime overlap compiler law

- New structural target:
  - compress the checked single-block high band into the smallest exact regime
    overlap compiler
- Assumption:
  - checked overlap band:
    - `2 <= n <= 7`
    - `n - 1 <= m <= 2n - 3`
- Strongest bounded results:
  - exact checked frontier:
    - `OPT_graph(n, m) = max(OPT_star_leaf(n, m), multipartite_plus_two_internal(n, m))`
  - representative selector rows:
    - `n = 7, m = 9`:
      - star-plus-low-edge wins alone
    - `n = 7, m = 10`:
      - repaired multipartite wins alone
    - `n = 7, m = 11`:
      - tie
- Strongest correction learned:
  - the checked high band is now an exact two-regime competition
  - that is much cleaner than carrying the full three-regime compiler into the
    overlap slice

Next frontier after v224:

- compress the high-band selector into a direct arithmetic rule if one exists
- or compare the two-regime overlap compiler against the true frontier beyond
  the checked small domain

## 2026-03-31, checked high-band selector stripe law

- New structural target:
  - compress the checked selector inside the exact two-regime overlap
- Assumption:
  - checked overlap slice:
    - `4 <= n <= 7`
    - `n - 1 <= m <= 2n - 3`
- Strongest bounded results:
  - unique star row:
    - `(7, 9)`
  - unique multipartite rows:
    - the stripe `m = 2n - 4`
    - plus `(6, 9)`
  - every other checked row:
    - tie
- Strongest correction learned:
  - the selector is already almost arithmetic on the checked slice
  - that makes the overlap band easier to teach as a real selector problem

Next frontier after v225:

- test whether the stripe-plus-exceptions selector persists beyond the checked
  small domain
- or search for a cleaner direct selector formula that subsumes the checked map

## 2026-03-31, extended two-family overlap selector law

- New structural target:
  - compress the selector between the star-plus-low-edge and repaired
    multipartite family compilers on a wider checked overlap domain
- Assumption:
  - family-comparison domain:
    - `7 <= n <= 12`
    - `n - 1 <= m <= 2n - 3`
- Strongest bounded results:
  - ties at:
    - `m = n - 1, n, n + 1, 2n - 3`
  - unique multipartite win at:
    - `m = 2n - 4`
  - unique star-plus-low-edge win on:
    - `n + 2 <= m <= 2n - 5`
- Strongest correction learned:
  - once the two-family comparison is granted, the selector is almost
    piecewise-arithmetic on the wider checked domain

Next frontier after v226:

- test whether the full corrected frontier still equals the same two-family max
  beyond the smaller exact slice from `v224`
- or explain the selector directly from family formulas instead of checked rows

## 2026-03-31, extended two-family overlap family-compiler law

- New structural target:
  - compress the checked two-family graph overlap from a selector law into a
    direct piecewise amount compiler
- Assumption:
  - family-comparison domain:
    - `7 <= n <= 12`
    - `n - 1 <= m <= 2n - 3`
- Strongest bounded results:
  - low plateau:
    - `2^(n - 1) - 1`
  - middle interval:
    - delegate to `OPT_star_leaf(n, m)`
  - near-top peak:
    - `3 * 2^(n - 2) - 3`
  - top tie:
    - `3 * 2^(n - 2) - 2`
- Strongest correction learned:
  - the two-family overlap is now a direct piecewise compiler on the wider
    checked family domain, not only a selector map

Next frontier after v227:

- test whether the full corrected frontier still agrees with this piecewise
  two-family compiler beyond the exact `v224` slice
- or derive the same compiler from family formulas without any checked search

## 2026-03-31, repaired-multipartite high-band availability and formula law

- New structural target:
  - explain the multipartite side of the graph overlap directly, not only
    through the overlap selector
- Assumption:
  - repaired multipartite family
  - checked high band:
    - `7 <= n <= 20`
    - `n - 1 <= m <= 2n - 3`
- Strongest bounded results:
  - available exactly at:
    - `m = n - 1, n, n + 1, 2n - 4, 2n - 3`
  - unavailable on:
    - `n + 2 <= m <= 2n - 5`
  - exact values:
    - `2^(n - 1) - 1`
    - `3 * 2^(n - 2) - 3`
    - `3 * 2^(n - 2) - 2`
- Strongest correction learned:
  - the repaired multipartite family itself is already a tiny direct compiler
    on the checked high band

Next frontier after v228:

- derive the widened overlap compiler directly from the star family law plus
  this multipartite high-band law
- or test whether the full corrected frontier still follows the same piecewise
  compiler beyond `v224`

## 2026-03-31, checked tree-star dominance law

- New structural target:
  - find a proof-oriented component law behind the low-edge star-forest branch
- Assumption:
  - connected labeled tree regime:
    - `2 <= n <= 8`
    - `m = n - 1`
- Strongest bounded results:
  - star value:
    - `2^(n - 1) - 1`
  - exact checked best connected-tree value:
    - the same on every checked `n`
  - largest checked tree domain:
    - `n = 8`
    - `262144` connected trees
- Strongest correction learned:
  - the low-edge branch now has a genuine component-level proof candidate, not
    only a frontier scan

Next frontier after v229:

- search for a structural proof that the star is the connected maximizer in the
  tree regime
- then feed that into a proof-oriented route toward the balanced star-forest
  low-edge frontier law

## 2026-03-31, non-star tree extremal gap law

- New structural target:
  - sharpen the tree branch from star optimality to a real extremal ladder
- Assumption:
  - connected non-star trees
  - checked domain:
    - `4 <= n <= 8`
    - `m = n - 1`
- Strongest bounded results:
  - exact checked non-star maximum:
    - `2^(n - 2)`
  - equality family:
    - double-stars
  - exact checked ladder:
    - star optimum `2^(n - 1) - 1`
    - best non-star tree `2^(n - 2)`
- Strongest correction learned:
  - the tree branch now has a sharp second rung, not only a top optimizer

Next frontier after v230:

- search for a local leaf-transfer or branch-concentration law that moves any
  non-star tree toward the double-star or star frontier
- or prove the extremal gap directly from a recursive counting argument

## 2026-03-31, widened overlap family compiler

- New structural target:
  - compress the corrected two-family overlap into a direct compiler
- Assumption:
  - corrected overlap domain:
    - `7 <= n <= 20`
    - `n - 1 <= m <= 2n - 3`
- Strongest bounded results:
  - exact direct compiler:
    - `2^(n - 1) - 1` on `n - 1 <= m <= n + 1`
    - `OPT_star_leaf(n, m)` on `n + 2 <= m <= 2n - 5`
    - `3 * 2^(n - 2) - 3` at `m = 2n - 4`
    - `3 * 2^(n - 2) - 2` at `m = 2n - 3`
- Strongest correction learned:
  - the overlap itself is now a direct compiler, not only a selector table

Next frontier after v231:

- push from overlap compilers into proof-shaped concentration laws on the
  low-edge side

## 2026-03-31, pendant-subtree concentration law

- New structural target:
  - find a monotone local move law on the corrected tree branch
- Assumption:
  - connected trees:
    - `4 <= n <= 8`
    - `m = n - 1`
  - move language:
    - pendant-subtree transfer
- Strongest bounded results:
  - every non-star unlabeled class has an improving move with:
    - `TD(T') >= TD(T)`
    - `Phi(T') > Phi(T)`
  - every checked class reaches the star through the improving move graph
- Strongest correction learned:
  - leaf transfers fail, pendant-subtree transfers survive

Next frontier after v232:

- combine component starification with exact star-size balancing
- extend the tree concentration branch beyond the checked range

## 2026-03-31, star-forest balancing law

- New structural target:
  - prove the optimizer on the star-family side directly
- Assumption:
  - star forests with:
    - fixed component count `c`
    - each component size at least `2`
    - total vertices `n`
- Strongest bounded results:
  - pairwise smoothing strictly improves the product law whenever sizes differ
    by at least `2`
  - the balanced profile is the exact star-family optimizer
  - exhaustive profile checks match the closed form on:
    - `2 <= c <= 8`
    - `2c <= n <= 20`
- Strongest correction learned:
  - the balanced star-forest formula is now an exact family optimizer

Next frontier after v233:

- compose the checked component starification law with exact star balancing

## 2026-03-31, two-stage low-edge concentration law

- New structural target:
  - turn the checked low-edge frontier into one concentration process
- Assumption:
  - positive low-edge forests:
    - `2 <= n <= 8`
    - `ceil(n / 2) <= m <= n - 1`
- Strongest bounded results:
  - every checked unlabeled forest class admits a finite monotone path to the
    balanced star forest
  - stage 1:
    - starify components
  - stage 2:
    - balance star sizes
- Strongest correction learned:
  - the low-edge branch is now a two-stage mechanism, not only a frontier law

Next frontier after v234:

- extend the checked tree concentration law beyond `n <= 8`
- convert the low-edge branch into a cleaner proof narrative
- then return to the higher-budget graph frontier with that stronger scaffold

## 2026-03-31, pendant-subtree concentration, `n = 9` extension

- New structural target:
  - test whether the checked tree concentration law survives one full rung
    higher
- Assumption:
  - connected trees:
    - `n = 9`
    - `m = n - 1`
  - move language:
    - pendant-subtree transfer
- Strongest bounded results:
  - full labeled scan size:
    - `9^7 = 4,782,969`
  - unlabeled tree classes recovered:
    - `47`
  - every non-star class has an improving move
  - every class reaches the star through the improving move graph
- Strongest correction learned:
  - the pendant-subtree concentration branch survives beyond the tiny checked
    range, at least through `n = 9`

Next frontier after v235:

- search for a structural proof of the pendant-subtree concentration law
- or push the checked extension one more rung only if the proof search stalls

## 2026-03-31, hub-target pendant-subtree law

- New structural target:
  - simplify the surviving move language on the tree concentration branch
- Assumption:
  - connected trees:
    - `n in {8, 9}`
    - `m = n - 1`
  - move language:
    - pendant-subtree transfer into a maximum-degree hub
- Strongest bounded results:
  - every non-star unlabeled class on the checked domain has an improving
    hub-target move
  - two stronger candidate simplifications fail:
    - target degree strictly greater than detach-parent degree
    - detach-parent degree at least target degree
- Strongest correction learned:
  - the checked concentration law compresses to:
    - move a pendant subtree toward a hub

Next frontier after v236:

- search for a structural proof of the hub-target law
- then try to compress the source side, not only the target side

## 2026-03-31, one-branch hub-target pendant-subtree law

- New structural target:
  - compress the source side of the checked hub-target move law
- Assumption:
  - connected trees:
    - `n in {8, 9}`
    - `m = n - 1`
  - move language:
    - improving pendant-subtree transfer into a maximum-degree hub
  - source-side shape restriction:
    - moved subtree has at most one branching vertex
- Strongest bounded results:
  - every non-star unlabeled class on the checked domain has such a move
  - stronger source-side restrictions fail:
    - leaf-only hub moves
    - pendant-star hub moves
- Strongest correction learned:
  - the checked concentration law now compresses to:
    - move a one-branch pendant subtree into a hub

Next frontier after v237:

- search for a structural proof of the one-branch hub-target law
- only then look for one more source-side compression

## 2026-03-31, one-branch hub-to-balance low-edge mechanism law

- New structural target:
  - tighten the full low-edge branch after `v237`
- Assumption:
  - positive low-edge forests:
    - `2 <= n <= 8`
    - `ceil(n / 2) <= m <= n - 1`
  - stage 1:
    - one-branch hub-target concentration on connected components
  - stage 2:
    - exact star-size balancing
- Strongest bounded results:
  - the composed mechanism is available on the whole checked low-edge forest
    domain
- Strongest correction learned:
  - the low-edge branch can now be read as:
    - move a one-branch pendant subtree into a hub
    - then balance star sizes

Next frontier after v238:

- search for a direct proof of the composed low-edge mechanism
- then return to the corrected higher-budget graph branch

## 2026-03-31, one-branch hub-target concentration path law

- New structural target:
  - strengthen `v237` from one-step existence to a full checked path law
- Assumption:
  - connected trees:
    - `n in {8, 9}`
    - `m = n - 1`
  - move language:
    - improving one-branch pendant-subtree transfer into a maximum-degree hub
- Strongest bounded results:
  - every checked tree class reaches the star through finite monotone paths
    inside that restricted move language
- Strongest correction learned:
  - the checked tree branch can now be read as a restricted rewrite system:
    repeatedly move a one-branch pendant subtree into a hub

Next frontier after v239:

- search for a structural proof of the one-branch hub-target path law
- then lift that proof into the full low-edge forest mechanism

## 2026-03-31, minimal-size one-branch hub-target path law

- New structural target:
  - sharpen the restricted tree rewrite system from `v239`
- Assumption:
  - connected trees:
    - `n in {8, 9}`
    - `m = n - 1`
  - move language:
    - improving one-branch hub-target transfers
  - local selector:
    - only keep moves with smallest available moved-subtree size
- Strongest bounded results:
  - every checked tree class still reaches the star inside that stricter move
    system
- Strongest correction learned:
  - the checked tree branch now admits a smallest-move controller:
    repeatedly use a minimal-size one-branch hub-target move

Next frontier after v240:

- search for a structural proof of the minimal-size path law
- then lift that smallest-move rule into the low-edge forest mechanism

## 2026-03-31, depth-2 cutoff for the minimal tree controller

- New structural target:
  - sharpen `v240` from a minimal move controller into an exact depth-bounded
    one
- Assumption:
  - connected trees:
    - `n in {8, 9}`
    - `m = n - 1`
  - move language:
    - minimal-size one-branch hub-target transfers
  - branch-depth bound:
    - if a branch point exists in the moved subtree, it lies at depth at most
      `d`
- Strongest bounded results:
  - `d = 0` fails
  - `d = 1` fails
  - `d = 2` survives
- Strongest correction learned:
  - the checked tree branch admits a depth-2 smallest-move controller

## 2026-03-31, depth-2 hub-to-balance low-edge mechanism law

- New structural target:
  - lift the exact tree-side cutoff into the full low-edge forest branch
- Assumption:
  - positive low-edge forests:
    - `2 <= n <= 8`
    - `ceil(n / 2) <= m <= n - 1`
  - stage 1:
    - minimal-size one-branch hub-target concentration with branch-depth bound
      `2`
  - stage 2:
    - exact star-size balancing
- Strongest bounded results:
  - the composed depth-2 mechanism is available on the whole checked low-edge
    forest domain
- Strongest correction learned:
  - the low-edge branch now has an exact checked local depth cutoff

Next frontier after v243:

- prove the depth-2 local controller
- then prove the composed low-edge mechanism

## 2026-03-31, terminal-cherry ladder depth law

- New structural target:
  - explain the exact depth cutoff from `v242` with a named family
- Assumption:
  - terminal-cherry ladder family indexed by `h >= 0`
  - move language:
    - improving one-branch hub-target moves
  - compare the smallest surviving move on each rung
- Strongest bounded results:
  - smallest move size is exactly `h + 3`
  - for `h >= 1`, branch depth is exactly `h`
  - checked on `h = 0..5`
- Strongest correction learned:
  - the `h = 2` rung is the family-level witness behind the depth-2 cutoff on
    the checked tree branch

Next frontier after v244:

- prove the depth-2 local controller using the ladder as the negative side
- then prove the composed low-edge mechanism

## 2026-03-31, exact template necessity law for the depth-2 tree controller

- New structural target:
  - test whether the finite rewrite alphabet from `v245` admits a smaller exact
    subset
- Assumption:
  - connected trees:
    - `n in {8, 9}`
    - `m = n - 1`
  - move language:
    - minimal-size one-branch hub-target transfers
  - branch-depth bound:
    - at most `2`
  - template alphabet:
    - `leaf`
    - `cherry`
    - `three_leaf_star`
    - `broom_1`
    - `broom_2`
- Strongest bounded results:
  - survivor count:
    - `1`
  - minimal surviving template count:
    - `5`
  - the full five-template alphabet is the unique surviving subset
- Strongest correction learned:
  - the checked local controller is already minimal at the template level

Next frontier after v246:

- prove the five-template controller by structural necessity and sufficiency
- then lift it into a proof of the full low-edge mechanism

## 2026-03-31, template-specific obstruction witnesses

- New structural target:
  - turn the template-necessity law into explicit witness families
- Assumption:
  - connected trees:
    - `n in {8, 9}`
    - `m = n - 1`
  - remove one template from the full five-template controller
- Strongest bounded results:
  - every removed template has an explicit failing witness
  - first checked failure levels:
    - `broom_2`: `n = 9`
    - `broom_1`: `n = 8`
    - `three_leaf_star`: `n = 9`
    - `cherry`: `n = 8`
    - `leaf`: `n = 8`
- Strongest correction learned:
  - the proof branch now has named obstruction witnesses on both the depth side
    and the template side

Next frontier after v247:

- explain the five obstruction witnesses structurally
- then prove the full five-template controller

## 2026-03-31, first obstruction-family taxonomy

- New structural target:
  - compress the five explicit obstruction witnesses from `v247` into a smaller
    named family list
- Assumption:
  - first checked witness per removed template from `v247`
- Strongest bounded results:
  - `cherry` and `broom_1` both match `terminal_cherry_ladder(1)`
  - `broom_2` matches `terminal_cherry_ladder(2)`
  - `three_leaf_star` matches `subdivided_double_star(3, 3)`
  - `leaf` matches `endpoint_leaf_path(6)`
- Strongest correction learned:
  - the witness list already compresses into a small family taxonomy

Next frontier after v248:

- compress the family taxonomy into a smaller macro split
- then use that split to steer the proof search

## 2026-03-31, two-macro-family obstruction taxonomy

- New structural target:
  - compress the family taxonomy from `v248` one rung further
- Assumption:
  - first checked obstruction catalog from the five-template controller
- Strongest bounded results:
  - four removed templates:
    - `broom_2`
    - `broom_1`
    - `three_leaf_star`
    - `cherry`
    are one-ended terminal-fan obstructions
  - one removed template:
    - `leaf`
    is a two-ended endpoint-leaf obstruction
- Strongest correction learned:
  - the obstruction side now has a two-macro-family split

Next frontier after v249:

- turn the one-ended versus two-ended split into a structural proof strategy
- then prove the full five-template controller

## 2026-03-31, non-leaf terminal-fan coverage boundary

- New structural target:
  - test whether the full non-leaf failing set already lies inside the
    terminal-fan family
- Assumption:
  - connected trees:
    - `n in {8, 9}`
    - `m = n - 1`
  - delete one non-leaf template from the depth-2 controller
- Strongest bounded results:
  - `broom_2`, `broom_1`, and `three_leaf_star` have full terminal-fan coverage
  - `cherry` fails that law only once:
    - one non-terminal-fan exception at `n = 9`
- Strongest correction learned:
  - the non-leaf side is almost exactly terminal-fan, with one localized
    cherry-side failure

Next frontier after v251:

- classify the unique cherry-side exception
- then use that decomposition in the proof search

## 2026-03-31, unique cherry-side exception law

- New structural target:
  - classify the one non-terminal-fan exception from `v251`
- Assumption:
  - connected trees:
    - `n = 9`
    - `m = n - 1`
  - delete `cherry` from the depth-2 controller
- Strongest bounded results:
  - the non-terminal-fan exception count is exactly `1`
  - it matches:
    - `split_arm_cherry(2)`
- Strongest correction learned:
  - the non-leaf side now reduces to:
    - terminal-fan obstructions
    - plus one unique split-arm cherry exception

Next frontier after v252:

- prove the non-leaf side from terminal-fan coverage plus the split-arm cherry
  exception
- then return to the leaf side and the full controller proof

## 2026-04-01, non-leaf threshold classifier on normalized terminal-fan coordinates

- New structural target:
  - replace the non-leaf terminal-fan shape catalog with an exact rule on
    normalized terminal-fan coordinates
- Assumption:
  - connected trees:
    - `n in {8, 9}`
    - `m = n - 1`
  - delete one non-leaf template from the depth-2 controller
  - normalize terminal-fan coordinates as:
    - `u = min(endpoint_fan_sizes)`
    - `p = path_length`
    - `v = max(endpoint_fan_sizes)`
- Strongest bounded results:
  - the terminal-fan component is exactly:
    - `cherry`: `u = 2`, `p >= 2`, `v >= 2`
    - `broom_1`: `u = 2`, `p >= 3`, `v >= 2`
    - `broom_2`: `u = 2`, `p >= 4`, `v >= 2`
    - `three_leaf_star`: `u = 3`, `p >= 2`, `v >= 3`
- Strongest correction learned:
  - the non-leaf necessity side is not only one named family, it is one exact
    threshold classifier on normalized coordinates

Next frontier after v253:

- close the full non-leaf side with the split-arm cherry correction term
- then prove the threshold rules structurally

## 2026-04-01, full non-leaf exact classifier

- New structural target:
  - close the full non-leaf failing set, not only its terminal-fan part
- Assumption:
  - same checked tree domain as `v253`
- Strongest bounded results:
  - full failing set is exactly:
    - `broom_2`: the threshold slice `u = 2`, `p >= 4`, `v >= 2`
    - `broom_1`: the threshold slice `u = 2`, `p >= 3`, `v >= 2`
    - `three_leaf_star`: the threshold slice `u = 3`, `p >= 2`, `v >= 3`
    - `cherry`: the threshold slice `u = 2`, `p >= 2`, `v >= 2`
      plus `split_arm_cherry(2)`
- Strongest correction learned:
  - the descriptive search side of the non-leaf controller analysis is now an
    exact checked classifier

Next frontier after v254:

- prove the threshold slices structurally
- prove the one cherry-side correction term
- then combine both into the controller necessity proof

## 2026-04-01, non-leaf obstruction ladder law

- New structural target:
  - compress the four non-leaf threshold rules into a smaller coordinate
    picture
- Assumption:
  - use the checked threshold rules from `v253`
- Strongest bounded results:
  - `cherry`, `broom_1`, and `broom_2` form a strict path-length ladder on the
    two-fan line:
    - `broom_2 ⊊ broom_1 ⊊ cherry`
  - `three_leaf_star` is disjoint from that ladder
  - so the four deleted templates factor into:
    - one path-length ladder
    - one fan-size gate
- Strongest correction learned:
  - the non-leaf side is not four unrelated cases, it already has a small
    coordinate geometry

Next frontier after v255:

- prove the path-length ladder structurally
- prove the fan-size gate structurally
- then integrate both with the split-arm cherry correction

## 2026-04-01, terminal-fan selector and descent law

- New structural target:
  - explain the non-leaf threshold slices by the selected local rewrite on the
    terminal-fan states themselves
- Assumption:
  - connected trees:
    - `n in {8, 9}`
    - `m = n - 1`
  - checked non-leaf terminal-fan states only:
    - two-fan line `u = 2`, `p in {2, 3, 4}`
    - fan-size gate `(u, p, v) = (3, 2, 3)`
- Strongest bounded results:
  - on the two-fan line:
    - `p = 2` selects `cherry`
    - `p = 3` selects `broom_1`
    - `p = 4` selects `broom_2`
    - and each selected move sends:
      - `NTF(2, p, v) -> NTF(2, p - 1, v + 1)`
  - on the fan-size gate:
    - `NTF(3, 2, 3)` selects `three_leaf_star`
    - and moves to `NTF(3, 1, 4)`
- Strongest correction learned:
  - the non-leaf threshold picture is now a small selected descent system

Next frontier after v256:

- explain the obstruction slices as cuts in that descent system
- then prove the selected descent law structurally

## 2026-04-01, two-fan deletion cut law

- New structural target:
  - turn the nested two-fan threshold slices into a direct graph-of-states
    explanation
- Assumption:
  - same checked tree domain as `v256`
  - two-fan terminal-fan line only
- Strongest bounded results:
  - deleting `cherry` blocks exactly:
    - `p >= 2`
  - deleting `broom_1` blocks exactly:
    - `p >= 3`
  - deleting `broom_2` blocks exactly:
    - `p >= 4`
- Strongest correction learned:
  - the two-fan threshold slices are exactly ladder cuts in the checked
    selected descent system

Next frontier after v257:

- prove the selected descent law structurally
- prove that deleting one ladder template cuts exactly the states above that
  rung
- then combine that with the fan-size gate and split-arm cherry correction

## 2026-04-01, split-arm feeder law

- New structural target:
  - turn the cherry-side correction term into a local mechanism, not just a
    named shape
- Assumption:
  - connected trees:
    - `n = 9`
    - `m = n - 1`
  - source state:
    - `split_arm_cherry(2)`
- Strongest bounded results:
  - the unique selected move is:
    - template `leaf`
    - target `NTF(2, 2, 4)`
- Strongest correction learned:
  - the cherry-side correction is a feeder into the bottom two-fan rung, not a
    hidden extra ladder state

Next frontier after v258:

- close the whole cherry side as ladder cut plus feeder
- then prove the feeder relation structurally

## 2026-04-01, cherry-side feeder-cut closure

- New structural target:
  - compress the full cherry-deleted failing set into one mechanistic picture
- Assumption:
  - same checked tree domain as `v257`
- Strongest bounded results:
  - the full cherry-side failing set is exactly:
    - the two-fan ladder cut `p >= 2`
    - plus one feeder state:
      - `split_arm_cherry(2)`
- Strongest correction learned:
  - the cherry-side correction term is now mechanistically integrated into the
    ladder picture

Next frontier after v259:

- prove the two-fan ladder structurally
- prove the feeder relation structurally
- prove the fan-size gate structurally
- then combine all three into the five-template necessity proof

## 2026-04-01, checked terminal-fan controller family law

- New structural target:
  - test whether the selected non-leaf controller rows extend from isolated
    checked states to a checked family law
- Assumption:
  - connected trees
  - checked family domain:
    - `8 <= n <= 12`
    - two-fan line `NTF(2, p, v)`
    - three-fan gate line `NTF(3, 2, v)`
- Strongest bounded results:
  - two-fan line:
    - `p = 2`: `cherry`, target `NTF(2, 1, v + 1)`
    - `p = 3`: `broom_1`, target `NTF(2, 2, v + 1)`
    - `p = 4`: `broom_2`, target `NTF(2, 3, v + 1)`
    - `p >= 5`: no depth-2 selected move on the checked range
  - three-fan gate:
    - `NTF(3, 2, v)` selects `three_leaf_star`
    - target `NTF(3, 1, v + 1)`
- Strongest correction learned:
  - the non-leaf controller is now a checked family law, not only a few local
    rows

Next frontier after v260:

- explain the first checked deviation at `NTF(2, 8, 2)` on `n = 13`
- then prove the family law structurally on the stable region

## 2026-04-01, split-arm feeder family law

- New structural target:
  - test whether the cherry-side feeder extends beyond the one checked member
    `split_arm_cherry(2)`
- Assumption:
  - connected trees
  - checked family:
    - `split_arm_cherry(k)`
    - `2 <= k <= 6`
- Strongest bounded results:
  - for every checked `k`:
    - selected template `leaf`
    - selected target `NTF(2, 2, k + 2)`
- Strongest correction learned:
  - the cherry-side correction is one member of a checked feeder family

Next frontier after v261:

- explain the `split_arm_cherry(k)` feeder structurally
- connect that feeder family to the two-fan controller family
- then fold both into the five-template necessity proof

## 2026-04-01, unique checked two-fan anomaly

- New structural target:
  - test whether the stable two-fan controller law has any checked deviation
    beyond the rows seen in `v260`
- Assumption:
  - connected trees
  - checked two-fan family:
    - `NTF(2, p, v)`
    - `8 <= n <= 18`
    - `p >= 2`
    - `v >= 2`
- Strongest bounded results:
  - exactly one checked deviation from the stable law:
    - `NTF(2, 8, 2)` on `n = 13`
    - selected template `broom_2`
    - target outside the terminal-fan family
- Strongest correction learned:
  - the stable two-fan law is real, but it has one isolated checked anomaly

Next frontier after v262:

- explain the anomaly structurally instead of treating it as a stray miss
- test whether it feeds into a named family

## 2026-04-01, checked stable two-fan controller with one anomaly

- New structural target:
  - package the stable two-fan controller law together with its unique checked
    deviation
- Assumption:
  - checked two-fan family:
    - `8 <= n <= 18`
    - `NTF(2, p, v)`
- Strongest bounded results:
  - stable rows:
    - `p = 2`: `cherry`, target `NTF(2, 1, v + 1)`
    - `p = 3`: `broom_1`, target `NTF(2, 2, v + 1)`
    - `p = 4`: `broom_2`, target `NTF(2, 3, v + 1)`
    - `p >= 5`: no selected depth-2 move
  - only checked exception:
    - `NTF(2, 8, 2)` on `n = 13`
- Strongest correction learned:
  - the proof target is now one stable law plus one named exception

Next frontier after v263:

- explain the anomaly target family
- attach that anomaly to the non-leaf mechanism if possible

## 2026-04-01, bridge-fan-tail feeder family law

- New structural target:
  - test whether the anomaly target sits inside a small feeder family with its
    own checked local rule
- Assumption:
  - checked bridge-fan-tail family `BFT(r, t)`:
    - left hub with `2` leaves
    - bridge of length `3` edges to a right hub
    - right hub with `r` leaves and one tail of length `t`
    - checked range:
      - `2 <= r <= 6`
      - `1 <= t <= 5`
      - `n = r + t + 6 <= 15`
- Strongest bounded results:
  - for every checked row with `t >= 2`:
    - selected template `leaf`
    - selected target `BFT(r + 1, t - 1)`
  - on the checked base line `t = 1`:
    - selected template `broom_1`
- Strongest correction learned:
  - the anomaly target lives in a checked feeder family with a recursive
    peeling rule

Next frontier after v264:

- connect the unique anomaly state itself to this feeder family
- then prove the feeder family structurally

## 2026-04-01, anomaly entry into the bridge-fan-tail feeder chain

- New structural target:
  - factor the unique checked anomaly through the new feeder family
- Assumption:
  - source state:
    - `NTF(2, 8, 2)`
  - controller:
    - minimal-size one-branch hub-target moves
    - depth bound `2`
- Strongest bounded results:
  - every checked selected move from `NTF(2, 8, 2)`:
    - has template `broom_2`
    - lands exactly in `BFT(2, 5)`
  - the subsequent checked feeder chain is:
    - `BFT(2, 5) -> BFT(3, 4) -> BFT(4, 3) -> BFT(5, 2) -> BFT(6, 1)`
- Strongest correction learned:
  - the anomaly is not an isolated irregularity, it is an entry state into a
    named feeder chain

Next frontier after v265:

- prove the bridge-fan-tail feeder law structurally
- prove the anomaly entry move structurally
- connect the base line `BFT(r, 1)` to the remaining five-template necessity
  cases

## 2026-04-01, bridge-fan-tail base-line handoff law

- New structural target:
  - classify the `BFT(r, 1)` base line instead of leaving it as an unnamed exit
    from the feeder family
- Assumption:
  - source family:
    - `BFT(r, 1)`
  - target family candidate:
    - `BFS(s)`
    - left hub with `2` leaves
    - bridge of length `2` edges to a right star with `s` leaves
  - checked range:
    - `2 <= r <= 6`
- Strongest bounded results:
  - on every checked row:
    - selected template `broom_1`
    - selected target `BFS(r + 2)`
- Strongest correction learned:
  - the feeder chain does not end in an anonymous base case, it hands off to a
    second named family

Next frontier after v266:

- prove the bridge-fan-tail handoff structurally
- classify the next local rule on the bridge-fan-star family
- then fold both families into the five-template necessity proof

## 2026-04-01, bridge-fan-star handoff law

- New structural target:
  - classify the local controller on the bridge-fan-star family reached from
    `BFT(r, 1)`
- Assumption:
  - checked bridge-fan-star family `BFS(s)`:
    - left hub with `2` leaves
    - bridge of length `2` edges to a right star with `s` leaves
    - checked range:
      - `4 <= s <= 10`
- Strongest bounded results:
  - on every checked row:
    - selected template `cherry`
    - selected target `ADS(s + 1)`
- Strongest correction learned:
  - the feeder path continues through another named family instead of stopping
    at `BFS`

Next frontier after v267:

- classify the local controller on `ADS`
- then see whether the chain closes to the star

## 2026-04-01, adjacent-double-star handoff law

- New structural target:
  - classify the local controller on the adjacent-double-star family
- Assumption:
  - checked adjacent-double-star family `ADS(q)`:
    - left hub with `2` leaves
    - directly adjacent to a right hub with `q` leaves
    - checked range:
      - `4 <= q <= 11`
- Strongest bounded results:
  - on every checked row:
    - selected template `leaf`
    - selected target `OLAS(q + 1)`
- Strongest correction learned:
  - the route continues through a one-leaf family rather than branching into a
    diffuse residual atlas

Next frontier after v268:

- classify the one-leaf family
- test whether it lands directly in the star

## 2026-04-01, one-leaf-adjacent-star to star law

- New structural target:
  - test whether the one-leaf family collapses directly to the star
- Assumption:
  - checked one-leaf-adjacent-star family `OLAS(k)`:
    - a left node with one leaf
    - adjacent to a right star with `k` leaves
    - checked range:
      - `5 <= k <= 11`
- Strongest bounded results:
  - on every checked row:
    - selected template `leaf`
    - selected target is the star on the same `n`
- Strongest correction learned:
  - the named route now closes all the way to the star

Next frontier after v269:

- package the full named route as one object
- then shift from search to proof

## 2026-04-01, anomaly-to-star named route law

- New structural target:
  - compress the whole anomaly mechanism into one named route object
- Assumption:
  - source state:
    - `NTF(2, 8, 2)`
  - use the checked family laws from:
    - `v264`
    - `v266`
    - `v267`
    - `v268`
    - `v269`
- Strongest bounded results:
  - the checked route is:
    - `NTF(2, 8, 2)`
    - `BFT(2, 5)`
    - `BFT(3, 4)`
    - `BFT(4, 3)`
    - `BFT(5, 2)`
    - `BFT(6, 1)`
    - `BFS(8)`
    - `ADS(9)`
    - `OLAS(10)`
    - star on the same `n = 13`
  - selected templates along the route:
    - `broom_2`
    - then `leaf`
    - then `broom_1`
    - then `cherry`
    - then `leaf`
- Strongest correction learned:
  - the anomaly is now a compact named route to the star, not a loose local
    exception

Next frontier after v270:

- prove each family handoff structurally
- prove the full named route composition
- then feed that proof into the five-template necessity argument

## 2026-04-01, bridge-fan-tail route compiler law

- New structural target:
  - compress the checked bridge-fan-tail feeder chain into one symbolic route
    object
- Assumption:
  - checked bridge-fan-tail family:
    - `2 <= r <= 6`
    - `1 <= t <= 5`
    - `r + t <= 7`
  - use checked family handoffs from:
    - `v264`
    - `v266`
    - `v267`
    - `v268`
    - `v269`
- Strongest bounded results:
  - exact route from `BFT(r, t)` to the star compiles from `(r, t)` alone
  - exact route:
    - `BFT(r, t)`
    - repeated `BFT(r + 1, t - 1)` until `BFT(r + t - 1, 1)`
    - `BFS(r + t + 1)`
    - `ADS(r + t + 2)`
    - `OLAS(r + t + 3)`
    - star on the same `n = r + t + 6`
  - exact template word:
    - `leaf^(t - 1) broom_1 cherry leaf leaf`
  - exact route length:
    - `t + 3`
- Strongest correction learned:
  - the anomaly-side feeder is now a small symbolic controller, not only a
    named route for one source state

Next frontier after v271:

- widen the downstream tail window
- then widen the bridge-fan-tail route compiler itself

## 2026-04-01, extended downstream tail-controller law

- New structural target:
  - widen the checked tail controller behind the bridge-fan-tail route
- Assumption:
  - checked downstream families:
    - `BFS(s)` with `4 <= s <= 15`
    - `ADS(q)` with `4 <= q <= 15`
    - `OLAS(k)` with `5 <= k <= 16`
- Strongest bounded results:
  - `BFS(s)` selects `cherry` and lands in `ADS(s + 1)`
  - `ADS(q)` selects `leaf` and lands in `OLAS(q + 1)`
  - `OLAS(k)` selects `leaf` and lands directly in the star
  - composed tail is therefore checked for:
    - `4 <= s <= 14`
    - `BFS(s) -> ADS(s + 1) -> OLAS(s + 2) -> star`
- Strongest correction learned:
  - the downstream half of the anomaly route is now a reusable checked tail
    controller on a noticeably wider window

Next frontier after v272:

- widen the bridge-fan-tail rectangle enough to use that larger tail controller
- then repackage the whole route compiler on the wider domain

## 2026-04-01, wider bridge-fan-tail route compiler law

- New structural target:
  - widen the bridge-fan-tail route compiler beyond the earlier `r + t <= 7`
    slice
- Assumption:
  - checked bridge-fan-tail rectangle:
    - `2 <= r <= 7`
    - `1 <= t <= 5`
    - `n = r + t + 6 <= 18`
  - use:
    - `v264`
    - `v266`
    - `v272`
- Strongest bounded results:
  - exact route to the star still compiles from `(r, t)` alone on the whole
    checked rectangle
  - exact template word is unchanged:
    - `leaf^(t - 1) broom_1 cherry leaf leaf`
  - exact route length is unchanged:
    - `t + 3`
- Strongest correction learned:
  - the symbolic route compiler is not confined to the tiny anomaly-adjacent
    slice, it survives on a wider checked rectangle

Next frontier after v273:

- prove the bridge-fan-tail feeder law structurally
- prove the widened downstream tail controller structurally
- prove the widened route compiler by composition
- then return to the five-template necessity proof

## 2026-04-01, extended unique two-fan anomaly law

- New structural target:
  - test whether the unique checked two-fan anomaly survives beyond the old
    `n <= 18` window
- Assumption:
  - combine:
    - `v262` on `8 <= n <= 18`
    - new full row checks on:
      - `n = 19`
      - `n = 20`
- Strongest bounded results:
  - on the checked two-fan family `8 <= n <= 20`, there is still exactly one
    deviation from the stable controller law:
    - `NTF(2, 8, 2)` on `n = 13`
  - the new checked rows:
    - `n = 19`
    - `n = 20`
    add no new anomaly states
- Strongest correction learned:
  - the stable two-fan controller plus one named escape state now looks like a
    persistence law, not only a finite-window artifact

Next frontier after v274:

- prove the stable two-fan law structurally
- prove why `NTF(2, 8, 2)` is the only surviving escape
- then compose that with the widened route compiler

## 2026-04-01, downstream tail amount law

- New structural target:
  - extract exact amount formulas on the named downstream route families
- Assumption:
  - families:
    - `BFS(s)`
    - `ADS(q)`
    - `OLAS(k)`
    - star on `n`
  - quantities:
    - total-domination count `TD`
    - degree-square concentration `Phi`
- Strongest bounded results:
  - on the checked downstream families:
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
- Strongest correction learned:
  - the downstream tail is now a counted mechanism, not only a checked move
    chain
  - the middle `ADS -> OLAS` step is exactly `TD`-neutral but still climbs in
    `Phi`

Next frontier after v275:

- use the amount formulas to shorten the tail proof
- then search for a comparable amount law on the `BFT` feeder family

## 2026-04-01, bridge-fan-tail amount compiler law

- New structural target:
  - compress the bridge-fan-tail feeder family by exact amount formulas rather
    than only by move rules
- Assumption:
  - family:
    - `BFT(r, t)`
  - checked strip:
    - `2 <= r <= 7`
    - `1 <= t <= 10`
    - `n = r + t + 6 <= 23`
  - quantity:
    - total-domination count `TD`
- Strongest bounded results:
  - exact base formulas:
    - `TD(BFT(r, 1)) = 7 * 2^(r + 2) - 7`
    - `TD(BFT(r, 2)) = 7 * 2^(r + 2)`
    - `TD(BFT(r, 3)) = 21 * 2^(r + 1) - 7`
    - `TD(BFT(r, 4)) = 21 * 2^(r + 2) - 21`
  - exact tail recurrence for `t >= 5`:
    - `TD(BFT(r, t)) = TD(BFT(r, t - 1)) + TD(BFT(r, t - 3)) + TD(BFT(r, t - 4))`
- Strongest correction learned:
  - the feeder family is now an exact amount compiler on the checked strip, not
    only a checked controller path

Next frontier after v276:

- combine the `BFT` amount compiler with the downstream tail amount law
- then see whether the whole anomaly-side route has an exact amount compiler

## 2026-04-01, anomaly-route amount compiler law

- New structural target:
  - compress the whole anomaly-side route into one exact amount compiler
- Assumption:
  - source family:
    - `BFT(r, t)`
  - target:
    - star on the same `n = r + t + 6`
  - checked strip:
    - `2 <= r <= 7`
    - `1 <= t <= 10`
- Define:
  - `Delta(r, t) = TD(star_{r + t + 6}) - TD(BFT(r, t))`
- Strongest bounded results:
  - exact base formulas:
    - `Delta(r, 1) = 9 * 2^(r + 2) + 6`
    - `Delta(r, 2) = 25 * 2^(r + 2) - 1`
    - `Delta(r, 3) = 107 * 2^(r + 1) + 6`
    - `Delta(r, 4) = 107 * 2^(r + 2) + 20`
  - exact recurrence for `t >= 5`:
    - `Delta(r, t) = Delta(r, t - 1) + Delta(r, t - 3) + Delta(r, t - 4) + 5 * 2^(r + t + 1) + 2`
- Strongest correction learned:
  - the anomaly-side route is now a single exact amount compiler on the checked
    strip, not only feeder and tail amount compilers placed side by side

## 2026-04-01, anomaly-route Fibonacci-periodic decomposition

- New structural target:
  - explain the deficit compiler by decomposing the route into symbolic
    channels rather than only one inhomogeneous recurrence
- Assumption:
  - bridge-fan-tail feeder family:
    - `BFT(r, t)`
  - checked strip:
    - `2 <= r <= 7`
    - `1 <= t <= 10`
  - same-size target:
    - `star_{r + t + 6}`
- Strongest bounded results:
  - feeder amount splits exactly into:
    - a Fibonacci channel
    - a period-4 channel
  - exact feeder formula:
    - `B(r, t) = A_r * F_t + B_r * F_{t + 1} + C_r * cos(pi t / 2) + A_r * sin(pi t / 2)`
  - exact coefficients:
    - `A_r = (14 / 5) * (3 * 2^r - 1)`
    - `B_r = (7 / 5) * (8 * 2^r - 1)`
    - `C_r = (14 / 5) * (2^r - 2)`
  - whole-route deficit is exactly:
    - `Delta(r, t) = 2^(r + t + 5) - 1 - B(r, t)`
  - the forcing term from `v277` is exactly the residue of the star sequence
    against the feeder recurrence:
    - `S(r, t) - S(r, t - 1) - S(r, t - 3) - S(r, t - 4) = 5 * 2^(r + t + 1) + 2`
- Strongest correction learned:
  - the anomaly-side route is now more than a checked recurrence compiler, it
    separates into an exponential target channel minus a Fibonacci-periodic
    feeder channel

Next frontier after v277:

- prove the whole-route deficit compiler structurally
- decide whether this is now large enough to justify a new tutorial pass

## 2026-03-31, finite rewrite alphabet for the depth-2 tree controller

- New structural target:
  - compress the surviving depth-2 local controller into explicit rooted move
    templates
- Assumption:
  - connected trees:
    - `n in {8, 9}`
    - `m = n - 1`
  - move language:
    - minimal-size one-branch hub-target transfers
  - branch-depth bound:
    - at most `2`
- Strongest bounded results:
  - every checked selected move belongs to one finite rooted alphabet:
    - `leaf`
    - `cherry`
    - `three_leaf_star`
    - `broom_1`
    - `broom_2`
- Strongest correction learned:
  - the checked tree controller is now explicit enough to attack by finite
    template cases rather than only by a raw depth bound

Next frontier after v245:

- prove that five-template alphabet structurally
- then lift it into a proof of the full low-edge mechanism
