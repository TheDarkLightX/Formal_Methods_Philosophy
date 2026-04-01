# Tutorial 29 Handoff

## Scope

This tutorial is about:

- loop algebra for bounded neuro-symbolic search loops
- requirements-discovery loops
- observation maps and ambiguity quotients
- witness-arity ladders
- separator query languages
- staged label-basis changes
- exact bounded geometry of loop families

This tutorial is not for:

- macroeconomics or post-AGI firm models from Tutorial 28
- public history of every verifier-compiler experiment from Tutorial 27
- generic prompt-engineering advice

## Current public-facing structure

This tutorial is not public yet.

If it becomes public, it should teach one clean ladder:

1. plain counterexample collection
2. observation quotients
3. ambiguity classes
4. minimal question policies
5. witness-arity ladders
6. basis sufficiency and substitution laws
7. separator expressivity ladders
8. candidate loop families stronger than plain verifier-compilation

Do not present it as a grab-bag notebook.
It should read as one geometric map of loop design.

## Strongest local results to preserve

The stable bounded survivors are:

1. requirements recoverability law
   - pure recovery succeeds iff every missing requirement has a singleton witness
   - oracle-assisted recovery succeeds iff admissible witness signatures cover
     the whole missing set
   - on unrestricted omission families, singleton witnesses remain the global
     bottleneck
   - on scoped pair-lobotomy families, oracle assistance is strictly stronger

2. observation-quotient loop law
   - the right loop state is:
     - `O_W(M) = {S in W | S ⊆ M}`
   - structured pure recovery succeeds exactly when `O_W` is injective on the
     omission family
   - minimal follow-up questioning lives above the ambiguity quotient induced
     by equal observations

3. staged temporal label-function law
   - richer temporal monitor-cell labels can strictly refine flat trace labels
     on the full family
   - after earlier carving, the richer label basis can become exact
   - temporal label functions are therefore a staged basis-change axis, not
     automatically the right global starting basis

4. uniform witness ladder law
   - for uniform `k`-ary witness library `W_k`:
     - `O_k(M) = ∅` iff `|M| < k`
     - `O_k` is injective once `|M| >= k`
   - witness arity sets an exact observability threshold

5. lower-rung membership budget law
   - under uniform `k`-ary witnesses and membership-only follow-up:
     - `budget_mem(n, 2) = n - 1`
     - `budget_mem(n, k) = n` for `3 <= k <= n`
   - more witness arity is not monotone once residual query cost is counted

6. pair-basis sufficiency law
   - once the witness language already contains all pairs, adding more uniform
     higher-arity layers does not improve the ambiguity partition or the
     worst-case membership-question budget under membership-only follow-up

7. separator expressivity law above the pair basis
   - after the pair basis compresses the residual to singleton ambiguity:
     - pair-subset queries are useless
     - singleton-membership queries cost `n - 1`
     - block-intersection queries cost `ceil(log2 n)`
   - the next major leverage after the pair basis is separator expressivity

8. singleton witness substitution law
   - for singleton witness basis `W_T`:
     - `budget_mem(W_T, F_all) = n - |T|`
   - each singleton witness substitutes for exactly one later membership query
   - atomic witnesses and atomic questioning are linearly fungible

9. geometry prerequisite law for block separators
   - block-intersection queries on the raw nonempty family still cost:
     - `n`
   - the same query language on the singleton residue after the pair basis
     costs:
     - `ceil(log2 n)`
   - the logarithmic gain comes from composition:
     - first a geometry-changing witness basis
     - then an expressive residual separator language

10. atomic geometry invariance law
   - for singleton witness basis `W_T`, singleton-membership and
     block-intersection follow-up have the same exact budget:
     - `n - |T|`
   - richer separator language does not help until the witness basis changes
     the ambiguity geometry itself

11. complement witness pure-mass law
   - for `W_{T,U} = {{t} | t ∈ T} ∪ {U}` with `|U| >= 2`:
     - `pure_classes(W_{T,U}) = 2^|T|`
     - `budget_block(W_{T,U}, F_all) = |U|`
   - one higher-arity complement witness can create exponentially many
     immediately resolved cases without reducing worst-case residual depth

12. star-pair pure-mass law
   - for:
     - `W_star(a) = {{a, u} | u ∈ U}`
     - `W_anchor_star(a) = {{a}} ∪ W_star(a)`
   - exact laws:
     - `pure_classes(W_star) = 2^(n-1) - 1`
     - `pure_classes(W_anchor_star) = 2^(n-1)`
     - both keep:
       - `budget_block = n - 1`
   - sparse anchored pair families can buy exponential pure resolved mass at
     the same residual depth as the atomic `n - 1` axis

13. biclique pure-mass and residual-family law
   - for the complete bipartite pair witness basis:
     - `W_biclique(A, B) = {{a, b} | a ∈ A, b ∈ B}`
   - exact laws:
     - `pure_classes(W_biclique) = (2^|A| - 1)(2^|B| - 1)`
     - `Residual(W_biclique) = P_+(A) ∪ P_+(B)`
   - the star family is one edge of a wider biclique ladder
   - balanced bicliques look like the next serious sparse pair candidate

14. biclique residual-controller law
   - on the biclique side-only residual family:
     - `P_+(A) ∪ P_+(B)`
   - the exact block-query budget is:
     - `ceil(log2((2^|A| - 1) + (2^|B| - 1)))`
   - equivalently, for `a <= b`:
     - `b` if `a = 1`
     - `b + 1` if `a >= 2`

15. biclique balance extremal law
   - for fixed `n = a + b`, moving toward balance inside the biclique ladder:
     - strictly increases pure resolved mass
     - weakly decreases residual depth
   - stars are the sparse edge
   - balanced bicliques are the high-pure, low-depth edge

16. balanced biclique versus pair-basis tradeoff law
   - balanced bicliques use about half as many pair witnesses as the full pair
     basis
   - they lose only a subexponential slice of pure resolved mass
   - they pay a much deeper residual controller
   - this makes balanced bicliques the leading sparse exact alternative inside
     the pair branch

17. complete multipartite pure-mass law
   - for cross-block pair witnesses on:
     - `R = P_1 ⊔ ... ⊔ P_t`
   - exact laws:
     - `pure_classes = 2^n - 1 - sum_i(2^|P_i| - 1)`
     - `Residual = union_i P_+(P_i)`
   - this strictly generalizes bicliques and the full pair basis

18. balanced multipartite extremal law
   - for fixed `n` and fixed block count `t`, the balanced partition:
     - maximizes pure resolved mass
     - minimizes residual-family size
     - maximizes witness count

19. balanced multipartite ladder law
   - for fixed `n`, as balanced block count `t` increases:
     - pure resolved mass increases
     - residual-family size decreases
     - witness count increases
   - balanced bicliques and the full pair basis are two points on one monotone
     ladder

20. balanced multipartite residual-controller law
   - on the bounded balanced grid:
     - `2 <= n <= 7`
     - `2 <= t <= n`
   - the exact block-query budget is:
     - `ceil(log2 |Residual_bal(n, t)|)`
   - so the balanced multipartite ladder is exact on both:
     - witness geometry
     - residual-controller cost

21. balanced multipartite direct formula law
   - write:
     - `n = t*q + r`
     - `q = floor(n / t)`
     - `r = n mod t`
   - then:
     - `residual_size(n, t) = (t + r) * 2^q - t`
     - `pure_classes(n, t) = 2^n - (t + r) * 2^q + t - 1`
     - `witness_count(n, t) = n(n - 1)/2 - t*q*(q - 1)/2 - r*q`
   - this is the first direct-amount compiler on the loop-space geometry
     branch

22. pair-graph total-domination correction law
   - for a simple pair-witness graph `G` with observation:
     - `O_G(M) = E(G[M])`
   - a nonempty omission set `M` is pure iff `M` is a total dominating set of
     `G`
   - exhaustive checks on all simple graphs with `2 <= n <= 6` find no
     counterexample
   - this is the corrected global metric for graph-shaped pair libraries

23. corrected balanced-ladder frontier law
   - on exhaustive simple graphs with `2 <= n <= 6`, the balanced complete
     multipartite ladder attains the exact true pure frontier at every budget
     it defines
   - the earlier balanced gaps were artifacts of the edge-containing proxy

24. corrected complete-multipartite frontier law
   - on exhaustive simple graphs with `2 <= n <= 6`, the full complete
     multipartite family attains the exact true pure frontier at every budget
     it defines
   - this strictly strengthens the balanced-ladder correction
   - the live corrected search target is therefore:
     - budgets not representable by complete multipartite graphs

25. corrected complete-multipartite frontier extension law
   - on exhaustive simple graphs with `2 <= n <= 7`, the full complete
     multipartite family still attains the exact true pure frontier at every
     budget it defines
   - the corrected graph baseline is now checked through the same `n = 7`
     ceiling as the old proxy branch

26. multipartite large-block edge invariance law
   - adding one internal edge inside a complete multipartite block of size at
     least `3` leaves the corrected true pure mass unchanged on the checked
     domain `2 <= n <= 7`
   - this gives a clean one-edge repair axis above the corrected multipartite
     baseline

27. corrected one-edge multipartite frontier cover law
   - the family:
     - complete multipartite
     - plus one internal edge
   hits the exact true frontier at every budget it defines on `2 <= n <= 7`
   - for `n = 7`, this reduces the uncovered budgets to:
     - `2, 3, 4, 5, 8, 9`

28. corrected two-edge multipartite frontier cover law
   - the family:
     - complete multipartite
     - plus up to two internal edges
     hits the exact true frontier at every budget it defines on `2 <= n <= 7`
   - for `n = 7`, this reduces the uncovered budgets further to:
     - `3, 4, 5, 9`

29. star-plus-leaf-graph decomposition law
   - for a star on `k` leaves plus any leaf graph `H`:
     - `TD(G) = (2^k - 1) + TD(H)`
   - checked exhaustively for:
     - `1 <= k <= 6`
   - this explains the corrected high holdouts, especially:
     - `m = 8`
     - `m = 9`

30. disjoint-union total-domination product law
   - for disjoint simple graphs `G` and `H`:
     - `TD(G union H) = TD(G) * TD(H)`
   - checked exhaustively on all graph pairs with component sizes:
     - `1 <= |V(G)| <= 4`
     - `1 <= |V(H)| <= 4`
   - this turns the disconnected corrected graph branch into a product
     geometry instead of a brute-force enumeration problem

31. balanced star-forest low-edge frontier law
   - on exhaustive simple graphs with:
     - `2 <= n <= 7`
     - `0 <= m <= n - 1`
   - the corrected true frontier is:
     - `0` if `m < ceil(n / 2)`
     - `F_bal(n, m)` otherwise
   - where:
     - `c = n - m`
     - `n = c*q + r`
     - `F_bal(n, m) = (2^(q - 1) - 1)^(c - r) * (2^q - 1)^r`
   - this closes the corrected low-budget holdouts:
     - `3`
     - `4`
     - `5`
   - and, combined with the star-plus-leaf decomposition law, it explains the
     corrected `n = 7`, budget `9` optimum

32. corrected small-`n` graph regime-cover law
   - on the checked domain:
     - `2 <= n <= 7`
   - every exact true frontier budget is covered by at least one of:
     - low-edge balanced star forests
     - complete multipartite plus up to two internal edges
     - a star plus a low-edge leaf correction
   - this packages the corrected graph branch as one small-`n` regime map

33. multipartite repaired-block additivity law
   - for a complete multipartite graph with arbitrary internal graph `H_i`
     inside each block `P_i`:
     - `TD(G) = base(P_1, ..., P_t) + sum_i TD(H_i)`
   - checked exhaustively on every nontrivial partition with:
     - `2 <= n <= 7`
   - this subsumes:
     - the star-plus-leaf decomposition law
     - the one-edge invariance law in large blocks

34. low-edge repaired-multipartite optimizer law
   - for a complete multipartite graph with block sizes `s_i` and low-edge
     internal budgets:
     - `0 <= e_i <= s_i - 1`
   - the exact optimum is:
     - `base(parts) + sum_i F_bal(s_i, e_i)`
   - checked exhaustively on every nontrivial partition with:
     - `2 <= n <= 7`
   - this gives the repaired multipartite side a direct optimizer on a large
     structured subfamily

35. repaired-multipartite recursive optimizer law
   - for a complete multipartite graph with block sizes `s_i` and arbitrary
     internal edge budgets:
     - `0 <= e_i <= C(s_i, 2)`
   - the exact repaired optimum is:
     - `base(parts) + sum_i OPT_graph(s_i, e_i)`
   - checked exhaustively on every nontrivial partition with:
     - `2 <= n <= 7`
   - this identifies the real remaining difficulty:
     - the single-block frontier `OPT_graph(s, e)`

36. threshold single-block miss law
   - on the corrected single-block frontier with:
     - `2 <= n <= 7`
   - threshold graphs fail exactly at:
     - `n = 4`: `2, 4`
     - `n = 5`: `3, 6, 8`
     - `n = 6`: `3, 4, 8, 9, 10, 11, 12, 13`
     - `n = 7`: `4, 5, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19`
   - so the single-block frontier does not collapse to the threshold grammar

37. threshold-split collapse law on the corrected single-block frontier
   - on the checked corrected single-block domain:
     - `2 <= n <= 7`
   - threshold and split graphs attain exactly the same frontier value at
     every edge budget
   - so non-threshold split structure buys no extra frontier power on this
     branch

38. corrected small-domain single-block regime compiler law
   - on the checked domain:
     - `2 <= n <= 7`
   - the corrected single-block frontier equals the maximum of:
     - balanced star forests
     - complete multipartite plus up to two internal edges
     - a full star plus a low-edge leaf correction
   - this is the first direct amount compiler for the corrected single-block
     branch

39. two-regime-plus-one-exception compression law
   - on the checked domain:
     - `2 <= n <= 7`
   - removing the full-star-plus-leaf regime leaves exactly one miss:
     - `(7, 9)`
   - so the third regime is not broadly needed, only needed at one checked
     point

40. one-point corrected single-block compiler law
   - on the checked domain:
     - `2 <= n <= 7`
   - the corrected single-block frontier equals the maximum of:
     - balanced star forests
     - complete multipartite plus up to two internal edges
     - the explicit point correction:
       - `(7, 9) -> 64`
   - this is the cleanest current small-domain public object on the corrected
     graph branch

41. exceptional point structure law at `(7, 9)`
   - at the corrected exceptional point:
     - `(n, m) = (7, 9)`
   - every optimal graph is isomorphic to the same shape:
     - one dominating hub
     - plus a perfect matching on the six leaves
   - equivalently:
     - a full star plus three disjoint leaf edges
   - optimal labeled graph count:
     - `105`
   - optimal isomorphism type count:
     - `1`

42. star-plus-perfect-matching total-domination law
   - for the family:
     - one center joined to `2r` leaves
     - plus a perfect matching on the leaves
   - exact law:
     - `TD(F_r) = 2^(2r)`
   - checked for:
     - `1 <= r <= 6`
   - this turns the exceptional-point motif into a reusable exact family law

43. odd-line regime selector law in the corrected compiler family
   - on the line:
     - `n = 2r + 1`
     - `m = 3r`
   - balanced star forests are never available
   - multipartite plus up to two internal edges is reachable iff:
     - `r <= 2`
   - star-plus-leaf has exact value:
     - `2^(2r)`
   - so the current compiler-family selector is:
     - tie at `r = 1`
     - multipartite win at `r = 2`
     - star-plus-leaf as the only available regime for `r >= 3`

44. odd-line star-plus-leaf optimizer law
   - inside the full-star-plus-leaf family on:
     - `n = 2r + 1`
     - `m = 3r`
   - the exact optimizer is:
     - a full star plus a perfect matching on the leaves
   - exact value:
     - `2^(2r)`
   - so the `(7, 9)` exceptional-point motif is the first visible member of a
     whole family, not a one-off graph

45. full-star-plus-low-edge family compiler law
   - on the checked family band:
     - `2 <= n <= 8`
     - `n - 1 <= m <= 2n - 3`
   - exact family compiler:
     - `OPT_star_leaf(n, m) = (2^(n - 1) - 1) + F_bal(n - 1, m - (n - 1))`
   - below the leaf no-isolate threshold:
     - the branch collapses to the plain star value:
       - `2^(n - 1) - 1`
   - above that threshold:
     - the optimizer is a full star plus a balanced low-edge leaf correction
   - this turns the old odd-line story into one rung of a broader exact band

46. high-band two-regime overlap compiler law
   - on the checked single-block overlap band:
     - `2 <= n <= 7`
     - `n - 1 <= m <= 2n - 3`
   - the exact corrected frontier is:
     - `max(OPT_star_leaf(n, m), multipartite_plus_two_internal(n, m))`
   - representative selector rows:
     - `n = 7, m = 9`:
       - star-plus-low-edge wins alone
     - `n = 7, m = 10`:
       - repaired multipartite wins alone
     - `n = 7, m = 11`:
       - the two regimes tie
   - so the checked high band now has its own exact two-regime compiler

## Known mistakes or drift to avoid

Do not repeat these mistakes:

1. treating witness absence as if it already proved unrecoverability
2. collapsing witness language, observation state, and query language into one
   vague "oracle help" story
3. presenting higher witness arity as automatically better
4. treating richer separator syntax as automatically useful on every ambiguity
   class
5. confusing linear substitution laws with genuine geometry-changing laws
6. using the edge-containing proxy as if it were the true observation-quotient
   purity metric for general pair-witness graphs
7. assuming that moving from threshold graphs to split graphs will recover the
   corrected single-block miss budgets without checking it exactly
8. carrying the full star-plus-leaf regime forward as if it were broadly
   necessary after `v216`, rather than checking whether it compresses to a
   tiny explicit exception set
9. treating the point correction `(7, 9) -> 64` as a bare numeric patch after
   `v218`, instead of naming its actual structural motif

Also avoid drift into:

- generic LLM workflow talk without exact bounded objects
- unscoped claims that one loop is universally better than another
- promoting the proxy graph branch from `v181` to `v193` or `v196` as if it
  were a corrected live frontier

## Next honest frontiers

The strongest next branches are:

1. corrected true-purity graph frontier
   - the corrected small-`n` regime map now includes:
     - low-edge balanced star forests
     - complete multipartite plus up to two internal edges
     - star-plus-low-edge leaf corrections
     - disjoint-union factorization
     - repaired-block additivity
     - low-edge repaired-block optimization
     - full recursive repaired-block optimization
   - the next honest graph-side target is:
     - extend the regime cover beyond `n = 7`
     - or compress the single-block frontier `OPT_graph(s, e)` itself
     - but skip threshold-to-split refinements on that single-block branch,
       since they collapse on the checked domain
   - current strongest small-domain endpoint:
     - two structural regimes plus one explicit point correction
   - next honest move:
     - generalize the exceptional point motif `(7, 9)`
     - or extend the corrected direct compiler beyond `n = 7`
   - avoid overclaiming that the motif is frontier-optimal in general, since
     that has not been proved beyond the checked point
   - current clean star-plus-leaf question:
     - when does the full-star-plus-low-edge family remain frontier-optimal,
       not only family-optimal?
   - current clean high-band question:
     - can the overlap selector between star-plus-low-edge and repaired
       multipartite be compressed to a direct arithmetic rule?
   - the odd line remains the cleanest first slice of that question

2. non-uniform witness Pareto frontiers
   - search witness families that beat both:
     - singleton substitution
     - and pair-basis sufficiency

3. balanced multipartite residual-controller extension
   - either:
     - prove the balanced residual-controller law in general
     - or extend the bounded exact grid beyond `n <= 7`
   - then compare low-`t`, medium-`t`, and high-`t` balanced multipartite
     loops under:
     - witness size
     - pure resolved mass
     - residual depth
     - controller size

4. direct cross-family comparison
   - compare the balanced multipartite direct compiler against
     verifier-compilation style loops on shared bounded corpora

5. mixed separator families above the pair basis
   - pair plus singleton
   - block plus cardinality
   - small-group subset queries

6. candidate loop families stronger than plain verifier-compilation
   - observation-quotient plus question-policy loops
   - witness-language plus separator-expressivity loops
   - staged label-basis loops
   - hybrid loops that first change ambiguity geometry, then compile a small
     controller on the residual
   - current strongest candidate in this branch:
      - pair-basis plus block-separator residual controller
   - current most promising sparse non-uniform family:
     - singleton witnesses on `T` plus one complement witness on `U`
     - main value:
       - exponential pure resolved mass at fixed residual depth
   - current most promising sparse pair family:
     - low-`t` balanced multipartite witness bases
     - main value:
        - exponentially large pure resolved mass

## Current visual spine

The draft teaching assets already prepared for this branch are:

- static figures:
  - `loop-space-geometry-map.svg`
  - `requirements-loop-ladder.svg`
  - `graph-regime-overlap.svg`
  - `temporal-label-basis-shift.svg`
  - `hybrid-loop-comparison.svg`
- labs:
  - `requirements_loop_geometry_lab.html`
  - `graph_regime_compiler_lab.html`
  - `temporal_label_basis_lab.html`
  - `hybrid_loop_comparison_lab.html`

The strongest ready teaching path is now:

1. loop-space geometry map
2. requirements loop lab
3. graph regime overlap map
4. graph regime compiler lab

The temporal basis lab is useful, but still the least mature branch.

Figma draft generation was attempted for the main diagrams, but the current
plugin token is expired, so the live visual portfolio is repo-native for now.
        - low witness counts
   - current strongest dense pair family:
     - high-`t` balanced multipartite, ending at full pair basis
   - current live frontier:
      - the balanced multipartite ladder
     - now with exact bounded residual-controller evidence
      - and direct witness-side formulas from `(n, t)`
    - explicitly deprioritized branch:
      - singleton witnesses plus fancier separators

7. public teaching packet
   - one tutorial with visuals for:
     - observability ladders
     - ambiguity quotients
     - separator expressivity ladders
     - loop-family comparison

## Source experiment range

The current branch is mainly backed by:

- `v159` to `v225`

The most important recent additions are:

- `v159`: requirements recoverability law
- `v160`: observation-quotient loop law
- `v161`: staged temporal label-function law
- `v162`: uniform witness ladder law
- `v163`: lower-rung membership budget law
- `v164`: pair-basis sufficiency law
- `v165`: separator expressivity law above the pair basis
- `v166`: singleton witness substitution law
- `v167`: geometry prerequisite law for block separators
- `v168`: atomic geometry invariance law
- `v169`: complement witness pure-mass law
- `v170`: star-pair pure-mass law
- `v171`: biclique pure-mass and residual-family law
- `v172`: biclique residual-controller law
- `v173`: biclique balance extremal law
- `v174`: balanced biclique versus pair-basis tradeoff law
- `v175`: complete multipartite pure-mass law
- `v176`: balanced multipartite extremal law
- `v177`: balanced multipartite ladder law
- `v178`: balanced multipartite residual-controller law
- `v179`: balanced multipartite direct formula law
- `v180`: internal-clique pair witness law
- `v181`: pair-witness pure frontier correction law
- `v182`: cograph pair frontier law
- `v183`: clique-bridge optimum law
- `v184`: two-family frontier cover law
- `v185`: bridge-cograph frontier law
- `v186`: twin-pendant frontier law
- `v187`: local move necessity law
- `v188`: single-pendant frontier law
- `v189`: late-pendant frontier law
- `v190`: root-anchored late-pendant law
- `v191`: final-step obstruction law
- `v192`: pendant-true-twin repair law
- `v193`: bridge-budget motif narrowing law
- `v194`: hybrid controller advantage law
- `v195`: weighted hybrid-value law
- `v196`: bridge-budget weighted pricing law
- `v197`: balanced ladder weighted frontier law
- `v198`: pair-graph total-domination correction law
- `v199`: corrected balanced-ladder frontier law
- `v200`: corrected complete-multipartite frontier law
- `v201`: corrected complete-multipartite frontier extension law
- `v202`: multipartite large-block edge invariance law
- `v203`: corrected one-edge multipartite frontier cover law
- `v204`: corrected two-edge multipartite frontier cover law
- `v205`: star-plus-leaf-graph decomposition law
- `v206`: disjoint-union total-domination product law
- `v207`: balanced star-forest low-edge frontier law
- `v208`: corrected small-`n` graph regime-cover law
- `v209`: multipartite repaired-block additivity law
- `v210`: low-edge repaired-multipartite optimizer law
- `v211`: repaired-multipartite recursive optimizer law
- `v212`: threshold-graph single-block frontier miss law
- `v213`: split-graph single-block frontier miss law
- `v214`: threshold-split collapse law
- `v215`: corrected small-domain single-block regime compiler law
- `v216`: two-regime-plus-one-exception single-block compiler law
- `v217`: one-point corrected single-block compiler law
- `v218`: exceptional point structure law at `(7, 9)`
- `v219`: star-plus-perfect-matching total-domination law
- `v220`: odd-line multipartite inaccessibility law
- `v221`: odd-line regime selector law
- `v222`: odd-line star-plus-leaf optimizer law
- `v223`: full-star-plus-low-edge family compiler law
- `v224`: high-band two-regime overlap compiler law
- `v225`: checked high-band selector stripe law
- `v226`: extended two-family overlap selector law
- `v227`: extended two-family overlap family-compiler law
- `v228`: repaired-multipartite high-band availability and formula law
- `v229`: checked tree-star dominance law
- `v230`: non-star tree extremal gap law

## Latest continuation

Correction on 2026-03-31:

- `v181` to `v193`, and `v196`, used an edge-containing proxy on the
  graph-shaped pair branch
- those results should be treated as archived proxy exploration, not as live
  exact observation-quotient geometry
- the corrected live graph branch now starts from:
  - `v198`
  - `v199`

The corrected stable graph results are:

1. total domination is the true purity metric for pair-witness graphs
   - `v198` proves:
     - `M is pure iff M is a total dominating set of G`
   - exhaustive graph checks:
     - `2 <= n <= 6`
   - representative proxy failure:
     - one-edge graph on `3` vertices:
       - true pure classes: `0`
       - old proxy: `2`
     - clique-bridge `B(3, 2)`:
       - true pure classes: `9`
       - old proxy: `21`

2. the balanced ladder survives the correction
   - `v199` compares the exhaustive true frontier against the balanced complete
     multipartite ladder
   - checked domain:
     - `2 <= n <= 6`
   - exact result:
     - every balanced ladder budget hits the true frontier
   - so the earlier balanced gaps were proxy artifacts

3. the full complete multipartite family is the corrected live graph frontier
   - `v200` compares the exhaustive true frontier against all complete
     multipartite partitions
   - checked domain:
     - `2 <= n <= 6`
   - exact result:
     - every represented complete multipartite budget hits the true frontier
   - live corrected gap target:
     - budgets not representable by complete multipartite graphs

4. the corrected complete-multipartite frontier now survives through `n = 7`
   - `v201` extends the exhaustive comparison to:
     - `2 <= n <= 7`
   - exact result:
     - every represented complete multipartite budget still hits the true
       frontier

5. one internal repair edge already gives a new exact family axis
   - `v202` checks all complete multipartite partitions on `2 <= n <= 7`
   - adding one internal edge inside a block of size at least `3` leaves the
     true pure mass unchanged

6. complete multipartite plus one internal edge is now the strongest corrected
   graph-family cover
   - `v203` compares that family against the exhaustive true frontier on
     `2 <= n <= 7`
   - exact result:
     - every budget the family defines hits the true frontier
   - remaining uncovered `n = 7` budgets:
     - `2, 3, 4, 5, 8, 9`

7. complete multipartite plus up to two internal edges is now the strongest
   corrected repaired-family cover
   - `v204` compares that family against the exhaustive true frontier on
     `2 <= n <= 7`
   - exact result:
     - every defined family budget hits the true frontier
   - remaining uncovered `n = 7` budgets:
     - `3, 4, 5, 9`

8. the star-holdout side now has a direct decomposition law
   - `v205` proves:
     - `TD(star_k plus H_on_leaves) = (2^k - 1) + TD(H)`
   - checked exhaustively for:
     - `1 <= k <= 6`
   - this explains:
     - the `m = 8` holdout as star plus a leaf graph with `TD(H) = 0`
     - the `m = 9` holdout as star plus a leaf graph with `TD(H) = 1`

Archived proxy branch, keep only as a cautionary record:

3. balanced multipartite is not the whole pair-witness story
   - `v180` adds a second exact graph-shaped family:
     - same-cluster internal-clique witnesses
   - exact laws:
     - `Residual = {M != ∅ | |M ∩ C_i| <= 1 for every i}`
     - `residual_size = Π_i (1 + s_i) - 1`
     - `pure_classes = 2^n - Π_i (1 + s_i)`
     - `witness_count = Σ_i s_i(s_i - 1)/2`

4. the balanced multipartite ladder is not the full pure frontier
   - `v181` checks all simple graphs on `2 <= n <= 7`
   - first strict balanced gap:
     - `(n, m) = (5, 6)`
     - `22` versus `21`
   - max checked balanced gap:
     - `(n, m) = (7, 12)`
     - `111` versus `105`

5. recursive union-and-join loops are almost enough
   - `v182` enumerates all labeled cographs
   - full hit on:
     - `2 <= n <= 4`
   - exactly one miss each on:
     - `(5, 5)`
     - `(6, 8)`
     - `(7, 10)`

6. one bridge between cliques repairs the remaining checked rung
   - `v183` defines:
     - `B(a, b)`, two cliques plus one bridge edge
   - exact formulas:
     - `witness_count = C(a, 2) + C(b, 2) + 1`
     - `residual_size = (a + b) + ab - 1`
     - `pure_classes = 2^(a + b) - (a + b) - ab`
   - exact bounded optimum law:
     - for every `a, b >= 1` with `a + b <= 7`,
       `B(a, b)` hits the exact global optimum at its budget

7. the checked frontier is already covered by two structured loop families
   - `v184` compares:
     - exact global frontier from `v181`
     - cographs from `v182`
     - clique bridges from `v183`
   - exact checked cover:
     - all `62` frontier budgets on `2 <= n <= 7`
   - exact bridge-only repairs:
     - `(5, 5)`
     - `(6, 8)`
     - `(7, 10)`

8. one recursive closure already covers the whole checked frontier
   - `v185` defines bridge-cographs as the smallest family closed under:
     - disjoint union
     - complete join
     - single-edge join
   - full checked frontier hit on:
     - `2 <= n <= 7`
   - largest generated family:
     - `n = 7`
     - `716186` labeled graphs

9. a smaller local growth grammar still covers the whole checked frontier
   - `v186` adds the new largest-labeled vertex only by:
     - pendant
     - false twin
     - true twin
   - full checked frontier hit on:
     - `2 <= n <= 7`
   - much smaller family counts than bridge-cographs, for example:
     - `54089` versus `716186` at `n = 7`

10. the three local moves are checked-minimal on this domain
   - `v187` tests all nonempty subsets of:
     - pendant
     - false twin
     - true twin
   - only the full triple hits:
     - `62 / 62`
   - strongest strict subset:
     - `{false twin, true twin}`
     - `59 / 62`
     - misses exactly:
       - `(5, 5)`
       - `(6, 8)`
       - `(7, 10)`

9. one pendant event is already enough on this domain
   - `v188` keeps:
     - false twin
     - true twin
     - pendant
   - but allows at most one pendant event in the whole growth trace
   - pendant budget `0` misses exactly:
     - `(5, 5)`
     - `(6, 8)`
     - `(7, 10)`
   - pendant budget `1` hits:
     - `62 / 62`

10. the pendant can be pushed near the end
   - `v189` restricts the single pendant to the final tail window
   - final-step-only:
     - `61 / 62`
     - misses exactly:
       - `(7, 10)`
   - final-two-steps:
     - `62 / 62`

11. the late pendant can be root-anchored
   - `v190` attaches the pendant to the oldest existing vertex
   - root-anchored final-step-only:
     - `61 / 62`
     - misses exactly:
       - `(7, 10)`
   - root-anchored final-two-steps:
     - `62 / 62`

12. the remaining miss now has an exact obstruction explanation
   - `v191` focuses on:
     - `(n, m) = (7, 10)`
   - every exact optimum there is leafless:
     - min degree `2`
   - root-anchored final-step-only splits into:
     - a pendant-used branch, which forces a leaf
   - a no-pendant branch, capped at `107`
   - both branches top out at:
     - `107`

13. the repaired branch now has an exact local motif
   - `v192` stays on the same focused budget:
     - `(n, m) = (7, 10)`
   - inside root-anchored tail-window-two growth, only one final-two-step
     pattern reaches the exact global optimum:
     - `pendant -> true_twin`
   - every other final-two-step pattern is capped at:
     - `107`
   - the optimal family states collapse to:
     - `2` traces
     - `1` unique graph
   - both traces use the same local repair:
     - penultimate root pendant
     - final true twin of the new pendant leaf

14. the bridge repairs already form a small exact motif library
   - `v193` compares the bridge-style repaired budgets:
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
   - the library narrows exactly at the leafless rung

15. one hybrid loop now has an exact scoped controller win over a direct
    controller
   - `v194` compares the same task:
     - exact missing-set identification over `F_all`
   - same separator language in both cases:
     - block-intersection queries
   - direct raw-family controller depth:
     - `n`
   - hybrid pair-basis plus block residual-controller depth:
     - `ceil(log2 n)`
   - scope:
     - this is a controller-depth comparison only
     - it conditions on pair observations already being available as loop
       state

16. the branch now has an explicit cost-model boundary
   - `v195` scores loops by:
     - witness acquisition
     - pure resolved mass
     - residual controller depth saving
   - pair-plus-block beats direct exactly when:
     - `alpha * (2^n - n - 1) + beta * (n - ceil(log2 n)) > gamma * C(n, 2)`
   - pair-plus-atom beats direct exactly when:
     - `alpha * (2^n - n - 1) + beta > gamma * C(n, 2)`
   - under unit weights on the checked range, pair-plus-block beats direct
     everywhere and weakly dominates pair-plus-atom

17. the motif branch now has its first exact weighted phase boundary
   - `v196` prices the three exact clique-bridge bridge budgets:
     - `(5, 5)`
     - `(6, 8)`
     - `(7, 10)`
   - under unit weights:
     - clique-bridge beats the direct baseline on all three
     - pair-plus-block still has the higher value
   - exact switching boundary against pair-plus-block:
     - `(5, 5)`:
       - `5 * gamma > 5 * alpha + beta`
     - `(6, 8)`:
       - `7 * gamma > 7 * alpha + beta`
     - `(7, 10)`:
       - `11 * gamma > 11 * alpha + 2 * beta`

18. the balanced ladder now has a family-level weighted frontier
   - `v197` compares the full pair basis against every balanced sparse rung on
     the checked exact grid:
     - `2 <= n <= 7`
   - on that grid, the full pair basis is always unit-weight optimal or tied
   - from `n = 5` onward, a near-dense balanced rung already catches the pair
     basis at unit weights
   - and overtakes it once:
     - `gamma > alpha`
     - under `alpha = beta = 1`

These archived proxy entries are kept only as a cautionary record.
They are not the live exact graph frontier.

The live corrected graph frontier is now:

- `v198`: total domination is the exact purity metric for pair-witness graphs
- `v201`: the full complete multipartite family hits the corrected true
  frontier at every budget it defines on `2 <= n <= 7`
- `v204`: complete multipartite plus up to two internal edges still hits the
  corrected true frontier at every budget it defines on `2 <= n <= 7`
- `v206`: disconnected corrected graphs factor by:
  - `TD(G union H) = TD(G) * TD(H)`
- `v207`: the entire checked low-edge regime `0 <= m <= n - 1` is now
  explained by the balanced star-forest formula
- `v205 + v207`: the corrected `n = 7`, budget `9` optimum is explained as a
  star plus a low-edge leaf correction
- `v208`: on `2 <= n <= 7`, every exact frontier budget is covered by the
  union of those corrected regimes
- `v209`: repaired multipartite graphs decompose exactly into:
  - complete multipartite base
  - plus one additive correction term per repaired block
- `v210`: on low-edge internal block budgets, that repaired side has an exact
  direct optimizer:
  - `base(parts) + sum_i F_bal(s_i, e_i)`
- `v211`: on arbitrary internal block budgets, the repaired side has an exact
  recursive optimizer:
  - `base(parts) + sum_i OPT_graph(s_i, e_i)`
- `v231`: the corrected two-family overlap on
  - `7 <= n <= 20`
  - `n - 1 <= m <= 2n - 3`
  is itself a direct piecewise compiler
- `v232`: every checked non-star connected tree class on `4 <= n <= 8` has a
  pendant-subtree transfer with:
  - `TD(T') >= TD(T)`
  - `Phi(T') > Phi(T)`
  and every checked class reaches the star
- `v233`: the balanced profile is the exact optimizer on the star-forest
  family side
- `v234`: every checked positive low-edge forest class on `2 <= n <= 8`
  admits a finite two-stage monotone path to the balanced star forest:
  - starify components
  - then balance star sizes
- `v235`: the pendant-subtree concentration law extends one full rung higher:
  - `n = 9`
  - full labeled scan `4,782,969`
  - `47` unlabeled tree classes
  - every class still reaches the star
- `v236`: the move language now compresses further on the checked tree branch:
  every non-star class at `n in {8, 9}` has an improving pendant-subtree move
  into a maximum-degree hub
- `v237`: the source side now compresses too on the same checked tree branch:
  every non-star class at `n in {8, 9}` has an improving hub-target move whose
  moved subtree has at most one branching vertex
  - leaf-only hub moves fail
  - pendant-star hub moves fail
  - one-branch hub moves survive
- `v238`: the full checked low-edge branch now composes through that smaller
  move language:
  - one-branch hub-target concentration on components
  - then exact star-size balancing
- `v239`: the checked tree-side concentration path now stays entirely inside
  the smaller move language too:
  every checked tree class at `n in {8, 9}` reaches the star through finite
  monotone one-branch hub-target moves
- `v240`: the checked tree-side path survives one more restriction:
  every checked tree class at `n in {8, 9}` reaches the star using only
  minimal-size one-branch hub-target moves
- `v242`: the first exact local depth cutoff now survives on the same checked
  tree branch:
  for minimal-size one-branch hub-target moves, depth `0` fails, depth `1`
  fails, and depth `2` is the smallest surviving bound
- `v243`: the full checked low-edge branch composes through that sharper local
  controller too:
  - minimal-size one-branch hub-target concentration with branch-depth bound `2`
  - then exact star-size balancing
- `v244`: the depth cutoff is now explained by a named witness family:
  on the terminal-cherry ladder family, the smallest one-branch hub-target
  improving move has exact size `h + 3`, and for `h >= 1` its unique branch
  point lies at exact depth `h`
  - the `h = 2` rung is the clean family-level explanation of why depth `1`
    fails and depth `2` survives in `v242`
- `v245`: the surviving depth-2 controller now has an explicit finite rewrite
  alphabet on the same checked tree branch:
  every selected move is rooted-isomorphic to one of:
  - `leaf`
  - `cherry`
  - `three_leaf_star`
  - `broom_1`
  - `broom_2`
- `v246`: that finite alphabet is already exact and minimal on the checked tree
  branch:
  the exact subset lattice has one survivor only, the full five-template set
- `v247`: the necessity side now has explicit witnesses too:
  every removed template has a first checked failing class, so the proof branch
  can target five named obstruction shapes rather than one abstract subset
  argument
- `v248`: those five first witnesses already collapse into a small family list:
  terminal-cherry ladders, one subdivided double-star, and one endpoint-leaf
  path
- `v249`: and that family list collapses again into a two-way macro split:
  one-ended terminal-fan obstructions versus a two-ended endpoint-leaf
  obstruction
- `v250`: the first obstruction catalog collapses further than that:
  all five first witnesses already sit inside one parameterized terminal-fan
  family
- `v251`: that stronger unification does not extend fully to the whole non-leaf
  failing set:
  it is exact for `broom_2`, `broom_1`, and `three_leaf_star`, but `cherry`
  has one non-terminal-fan exception at `n = 9`
- `v252`: that exception is unique and matches `split_arm_cherry(2)`
- `v253`: the terminal-fan component of the non-leaf failing set is now an
  exact threshold classifier on normalized terminal-fan coordinates:
  - `cherry`: `u = 2`, `p >= 2`, `v >= 2`
  - `broom_1`: `u = 2`, `p >= 3`, `v >= 2`
  - `broom_2`: `u = 2`, `p >= 4`, `v >= 2`
  - `three_leaf_star`: `u = 3`, `p >= 2`, `v >= 3`
- `v254`: the full non-leaf failing set is now an exact checked classifier:
  - the same threshold slices as `v253`
  - plus `split_arm_cherry(2)` only in the `cherry` case
- `v255`: those threshold rules already compress one rung further:
  - `cherry`, `broom_1`, and `broom_2` form a strict path-length ladder on the
    two-fan line
  - `three_leaf_star` is a disjoint fan-size gate
- `v256`: that coordinate picture now has a checked mechanism:
  - on the two-fan line, the selected move sends:
    - `NTF(2, p, v) -> NTF(2, p - 1, v + 1)`
  - and the selected template is:
    - `p = 2`: `cherry`
    - `p = 3`: `broom_1`
    - `p = 4`: `broom_2`
  - the fan-size gate `NTF(3, 2, 3)` selects `three_leaf_star` and moves to
    `NTF(3, 1, 4)`
- `v257`: the nested two-fan obstruction slices are now explained as exact cuts
  in that checked descent ladder:
  - deleting `cherry` blocks exactly `p >= 2`
  - deleting `broom_1` blocks exactly `p >= 3`
  - deleting `broom_2` blocks exactly `p >= 4`
- `v258`: the cherry-side correction term now has a local mechanism too:
  - `split_arm_cherry(2)` selects `leaf`
  - and feeds directly into the bottom two-fan rung `NTF(2, 2, 4)`
- `v259`: the whole cherry side now closes mechanistically as:
  - the two-fan ladder cut `p >= 2`
  - plus the feeder state `split_arm_cherry(2)`
- `v260`: the non-leaf controller now extends to a checked family law on the
  stable terminal-fan region `8 <= n <= 12`:
  - `p = 2`: `cherry`
  - `p = 3`: `broom_1`
  - `p = 4`: `broom_2`
  - `p >= 5`: no depth-2 selected move on the checked range
  - `NTF(3, 2, v)`: `three_leaf_star`
- `v261`: the cherry-side feeder also extends to a checked family:
  - `split_arm_cherry(k)` with `2 <= k <= 6`
  - selected template `leaf`
  - target `NTF(2, 2, k + 2)`
- `v262`: on the checked two-fan family `8 <= n <= 18`, there is exactly one
  deviation from the stable controller law:
  - `NTF(2, 8, 2)` on `n = 13`
  - selected template `broom_2`
  - target outside the terminal-fan family
- `v263`: the stable two-fan controller therefore sharpens to:
  - `p = 2`: `cherry`, target `NTF(2, 1, v + 1)`
  - `p = 3`: `broom_1`, target `NTF(2, 2, v + 1)`
  - `p = 4`: `broom_2`, target `NTF(2, 3, v + 1)`
  - `p >= 5`: no selected depth-2 move
  - plus one checked anomaly:
    - `NTF(2, 8, 2)` on `n = 13`
- `v264`: that anomaly target sits inside a checked bridge-fan-tail feeder
  family `BFT(r, t)`:
  - checked range:
    - `2 <= r <= 6`
    - `1 <= t <= 5`
    - `n = r + t + 6 <= 15`
  - for every checked `t >= 2`:
    - selected template `leaf`
    - selected target `BFT(r + 1, t - 1)`
  - on the checked base line `t = 1`:
    - selected template `broom_1`
- `v265`: the unique anomaly state is now explained as an entry into that
  feeder chain:
  - `NTF(2, 8, 2)` enters `BFT(2, 5)` by a checked `broom_2` move
  - then the checked chain continues:
    - `BFT(2, 5) -> BFT(3, 4) -> BFT(4, 3) -> BFT(5, 2) -> BFT(6, 1)`
- `v266`: the `BFT(r, 1)` base line now has a checked named handoff:
  - for `2 <= r <= 6`
  - selected template `broom_1`
  - selected target `BFS(r + 2)`
  - where `BFS(s)` is the bridge-fan-star family:
    - left hub with `2` leaves
    - bridge of length `2` edges
    - right star with `s` leaves
- `v267`: the `BFS` family now has its own checked handoff:
  - for `4 <= s <= 10`
  - selected template `cherry`
  - selected target `ADS(s + 1)`
  - where `ADS(q)` is the adjacent-double-star family:
    - left hub with `2` leaves
    - directly adjacent to a right hub with `q` leaves
- `v268`: the `ADS` family also has a checked handoff:
  - for `4 <= q <= 11`
  - selected template `leaf`
  - selected target `OLAS(q + 1)`
  - where `OLAS(k)` is the one-leaf-adjacent-star family:
    - a left node with one leaf
    - adjacent to a right star with `k` leaves
- `v269`: the `OLAS` family then closes directly:
  - for `5 <= k <= 11`
  - selected template `leaf`
  - selected target is the star on the same `n`
- `v270`: the unique anomaly now has a full checked named route to the star:
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
- `v271`: that anomaly-side feeder chain now compresses into a first symbolic
  route compiler:
  - on checked:
    - `2 <= r <= 6`
    - `1 <= t <= 5`
    - `r + t <= 7`
  - exact route from `BFT(r, t)` to the star compiles from `(r, t)` alone
  - exact template word:
    - `leaf^(t - 1) broom_1 cherry leaf leaf`
  - exact route length:
    - `t + 3`
- `v272`: the downstream half of that route now widens to a reusable checked
  tail controller:
  - `BFS(s)` for `4 <= s <= 15`
  - `ADS(q)` for `4 <= q <= 15`
  - `OLAS(k)` for `5 <= k <= 16`
  - composed tail is checked for:
    - `4 <= s <= 14`
    - `BFS(s) -> ADS(s + 1) -> OLAS(s + 2) -> star`
- `v273`: the bridge-fan-tail route compiler now widens too:
  - checked rectangle:
    - `2 <= r <= 7`
    - `1 <= t <= 5`
    - `n = r + t + 6 <= 18`
  - exact route to the star still compiles from `(r, t)` alone
  - exact template word and route length stay unchanged
- `v274`: the unique two-fan anomaly also persists on a wider checked domain:
  - on checked `8 <= n <= 20`
  - there is still exactly one deviation from the stable two-fan controller:
    - `NTF(2, 8, 2)` on `n = 13`
  - the new full checked rows:
    - `n = 19`
    - `n = 20`
    add no new anomaly states
- `v275`: the downstream half of the anomaly route now has exact amount
  formulas on the checked range:
  - `TD(BFS(s)) = 7 * 2^s - 3`
  - `Phi(BFS(s)) = s^2 + 3s + 16`
  - `TD(ADS(q)) = 2^(q + 2)`
  - `Phi(ADS(q)) = q^2 + 3q + 12`
  - `TD(OLAS(k)) = 2^(k + 1)`
  - `Phi(OLAS(k)) = k^2 + 3k + 6`
  - `TD(star_n) = 2^(n - 1) - 1`
  - `Phi(star_n) = n(n - 1)`
  - exact checked tail gains:
    - `BFS(s) -> ADS(s + 1)` gains in both `TD` and `Phi`
    - `ADS(q) -> OLAS(q + 1)` is `TD`-neutral but `Phi`-positive
    - `OLAS(k) -> star_{k + 3}` gains in both `TD` and `Phi`
- `v276`: the bridge-fan-tail feeder family now also has an exact
  total-domination amount compiler on the checked strip:
  - checked:
    - `2 <= r <= 7`
    - `1 <= t <= 10`
  - exact base formulas:
    - `TD(BFT(r, 1)) = 7 * 2^(r + 2) - 7`
    - `TD(BFT(r, 2)) = 7 * 2^(r + 2)`
    - `TD(BFT(r, 3)) = 21 * 2^(r + 1) - 7`
    - `TD(BFT(r, 4)) = 21 * 2^(r + 2) - 21`
  - exact recurrence for `t >= 5`:
    - `TD(BFT(r, t)) = TD(BFT(r, t - 1)) + TD(BFT(r, t - 3)) + TD(BFT(r, t - 4))`
- `v277`: the whole anomaly-side route now also has a single exact amount
  compiler on the checked strip:
  - define:
    - `Delta(r, t) = TD(star_{r + t + 6}) - TD(BFT(r, t))`
  - checked:
    - `2 <= r <= 7`
    - `1 <= t <= 10`
  - exact base formulas:
    - `Delta(r, 1) = 9 * 2^(r + 2) + 6`
    - `Delta(r, 2) = 25 * 2^(r + 2) - 1`
    - `Delta(r, 3) = 107 * 2^(r + 1) + 6`
    - `Delta(r, 4) = 107 * 2^(r + 2) + 20`
  - exact recurrence for `t >= 5`:
    - `Delta(r, t) = Delta(r, t - 1) + Delta(r, t - 3) + Delta(r, t - 4) + 5 * 2^(r + t + 1) + 2`
- `v278`: the same anomaly-side route now has a cleaner symbolic decomposition:
  - feeder amount separates exactly into:
    - a Fibonacci channel
    - a period-4 channel
  - exact feeder formula:
    - `B(r, t) = A_r * F_t + B_r * F_{t + 1} + C_r * cos(pi t / 2) + A_r * sin(pi t / 2)`
  - exact coefficients:
    - `A_r = (14 / 5) * (3 * 2^r - 1)`
    - `B_r = (7 / 5) * (8 * 2^r - 1)`
    - `C_r = (14 / 5) * (2^r - 2)`
  - whole-route deficit becomes:
    - `Delta(r, t) = 2^(r + t + 5) - 1 - B(r, t)`
  - the forcing term from `v277` is exactly the residue of the star sequence
    against the feeder recurrence:
    - `5 * 2^(r + t + 1) + 2`

The next honest graph-side moves are:

- prove the stable two-fan controller law structurally
- prove the bridge-fan-tail feeder law structurally
- prove the anomaly entry move structurally
- prove the `BFT(r, 1) -> BFS(r + 2)` handoff
- prove the `BFS(s) -> ADS(s + 1)` handoff
- prove the `ADS(q) -> OLAS(q + 1)` handoff
- prove the `OLAS(k) -> star` collapse
- prove the fan-size gate structurally
- then use that exact non-leaf classifier inside a necessity-and-sufficiency
  proof for the full five-template depth-2 controller
- then prove the full low-edge path directly from that local controller plus
  balancing
