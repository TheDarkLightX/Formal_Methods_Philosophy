---
title: "Functional Core, Imperative Shell: How Immutable Values Become Boundaries"
layout: docs
kicker: Tutorial 64
description: "A practical and formal introduction to the philosophy and practice of functional core, imperative shell: pure transitions, immutable values as boundaries, differential oracle audits, counterexample witnesses, concurrency, and assurance."
---

# Functional Core, Imperative Shell: How Immutable Values Become Boundaries

Software becomes difficult to audit when one operation reads hidden state, makes a decision, mutates several objects, calls external systems, and reports success from the same block of code. The result may work in ordinary tests while remaining hard to replay, compare, or reason about.

The functional-core/imperative-shell pattern, abbreviated **FCIS**, gives those responsibilities a visible shape:

```text
untrusted bytes
      │
      ▼
bounded, canonical, authenticated values
      │
      ▼
pure transition function
State × Command × Policy × Evidence
      │
      ├── Reject(reason)
      │
      └── Accept(next_state, effect_plan, receipt_draft)
                         │
                         ▼
imperative shell atomically commits, then delivers effects
```

The core answers a question: **given these exact facts, what is the permitted result?** The shell deals with the changing world: clocks, networks, databases, files, authentication, retries, process failures, and concurrency.

Gary Bernhardt's talk [Boundaries](https://www.destroyallsoftware.com/talks/boundaries) presents the practical insight behind this organization: simple values can form boundaries between subsystems. This tutorial develops that insight into a high-assurance design discipline.

## 1. The separation is semantic

Putting pure code in `core/` and database code in `shell/` can make a repository easier to navigate. Directory placement does not create the assurance property. The important separation concerns **meaning, authority, and effects**.

A high-assurance design looks like this:

```text
immutable state data
+ command data
+ committed policy data
+ authenticated evidence data
        │
        ▼
pure transition code
        │
        ▼
rejection data
or
next-state data + exact effect-plan data + receipt data
        │
        ▼
imperative shell validates boundary bindings,
commits atomically, and delivers effects idempotently
```

Code describes stable rules. Values describe the particular state of the world, requested action, policy parameters, evidence, decision, and authorized effects.

The shell may parse bytes, authenticate a caller, capture a state snapshot, invoke a verifier, and perform an atomic commit. Semantic rules such as pricing, conservation, authorization, and rejection precedence remain in the core. If the shell recalculates those rules, two competing semantics now exist.

This leads to a dependency rule:

```text
shell ─────► model, invariants, transition, codec, commitment
core  ──X──► shell
```

The core knows about values and rules. It does not know which database, HTTP client, spreadsheet, clock, or proof service happens to surround it.

## 2. The claim behind the pattern

FCIS rests on a thesis about what makes software hard to reason about. The thesis is that hidden history is the dominant cost, and that immutable values are the cheapest way to make history visible.

### Identity through time, or its absence

A mutable object keeps an identity across change. The account object at noon and the "same" account at one minute past noon hold different balances, yet share one name. This works because the system supplies a convention: an identity that survives mutation, threading before and after together.

A value needs no such convention. The integer `5` has no before and after. It cannot be the same value at two times because it does not change. Immutability collapses the gap between identity and equality: a value is identical to itself at every instant, so equality and identity coincide.

The consequence shows up in review. With a mutable account, the sentence "the balance is 100" can become false before a reader finishes reading it. With an immutable snapshot, the same sentence is fixed by the value itself. The snapshot is the fact, not a pointer to a fact that may move.

### Outputs are entailed by inputs

A pure function has no hidden causes. Its result is entailed by its arguments in the sense that a theorem is entailed by its premises: given the inputs, the output is necessary.

```text
transition(S, C, P, E) = D
```

Entailment is a strong property. The function can be lifted out of its calling context and studied alone. An impure function breaks entailment because part of what determines its result, or its effect, lives outside the argument list, in a clock, a database, a global, or a network. The result then depends on facts the reader cannot see.

### From interface dependencies to data dependencies

Gary Bernhardt's [Boundaries](https://www.destroyallsoftware.com/talks/boundaries) identifies the move that makes the rest possible. Two subsystems joined by a method call are coupled in time: one must invoke the other while both are alive, in some agreed order, holding some agreed locks. Two subsystems joined by a value are coupled only by the value. Each can run at any time, in any process, in any order; the value mediates.

```text
interface dependency:  A calls B.method(x)        -- A depends on B's behavior, alive, in order
data dependency:       A produces v; B consumes v -- A and B depend only on v
```

The phrase "values as boundaries" names this replacement. A live relationship becomes a static one. A dependency on behavior becomes a dependency on data. Behavior can fail, race, retry, and lie. Data can be stored, copied, hashed, signed, replayed, and compared.

### Reification: concepts become values

Bernhardt's move replaces a live dependency with a static one. The positive form of the same move is **reification**: take a concept that lived only as an implicit relationship or an inline procedure, and give it a value representation. A property accessor becomes a value. A UI component becomes a value. An effect request becomes a value. A proof obligation becomes a value.

Reification is what makes composition possible. Two values can be combined by a third value, stored beside each other, passed to a common function, or compared by an independent checker. Two live procedures can only be combined by writing more procedure that calls them in the right order, with the right wiring, while both are alive.

The [Functional Software Architecture](https://functional-architecture.org/) site collects this stance under the heading "Everything as a Value": reifying concepts as values allows these concepts to be passed around, analyzed, and composed. The gain is not aesthetic. A reified concept acquires the operations available on values: it can be stored, copied, hashed, signed, serialized, replayed, and inspected. A concept that lives only in the flow of execution has none of those operations.

Composition starts to pay its way at this point. When functions, property accessors, and components are themselves values, small structures combine into larger ones through ordinary combinators. The composition is honest only when the combining operation preserves the invariants of the parts; associativity, identity, and distributivity are not free, and a later subsection returns to the algebraic discipline they impose.

### Declarative truth, imperative action

The split between core and shell tracks an older distinction: between what is true and what is done. The core answers a declarative question. Given these facts, what is the permitted result? The shell answers an imperative one. Given this permitted result, how is it committed and delivered in a world of crashes, retries, and adversaries?

A rule such as "a swap is accepted only if reserves stay nonnegative" is declarative. It states a condition on values. The act of writing the accepted swap into a ledger is imperative. It changes the world. FCIS separates the two so that each can be inspected on its own terms: the core for whether its decisions follow from its inputs, the shell for whether its commits and deliveries match the plans the core authorized.

### Denotational design: meaning before mechanism

The core answers a question of meaning: given these facts, what is the permitted result? Denotational design, as practiced in the functional programming tradition, pushes this question to the front. Before deciding how a component works, write down what it denotes.

A denotation is a mathematical object that the program is supposed to compute. A list sort denotes the ordered permutation of its input. A swap transition denotes the unique state and effect plan entailed by its inputs under the stated policy. The denotation is independent of any implementation. Two implementations that agree on the denotation are interchangeable, and a test or proof can compare an implementation against the denotation rather than against another implementation.

This separates two concerns that procedural code often blends. The denotation says what the software means. The implementation says how it computes that meaning. FCIS makes the same separation at the architectural level: the core is the denotation, the shell is the mechanism that feeds it and commits its results. The [Functional Software Architecture](https://functional-architecture.org/) site describes the underlying methodology as building airtight abstraction barriers: the denotation informs both the use and the implementation without coupling them.

A consequence worth noting: deferring implementation decisions becomes cheaper. When the meaning is fixed as a denotation, the choice of data structure, algorithm, language, and runtime can be revisited later. Immutability reinforces this. A committed state value does not depend on the database that produced it, so the database can be swapped without changing what the state means. Late decision making follows from fixing meaning independently of mechanism.

### The boundary is where meaning is fixed

A boundary is not only a runtime edge. It marks where ambiguous bytes become a typed command, where an unverified signature becomes an authenticated identity, where a candidate plan becomes an authorized effect. At each boundary the system commits to a meaning. A value placed at that boundary makes the commitment inspectable: it can be validated, logged, hashed, and replayed without re-running the subsystem that produced it.

Without such a value, the meaning lives only in the transient state of a running process and disappears when the process ends. With it, the meaning becomes an artifact that outlives the process and can be examined by anyone who holds a copy.

### A value can be its own evidence

The strongest form of this idea places the proof inside the value's type. A `VerifiedSignature` that can only be constructed by a procedure that actually checked the signature is a value whose existence is the evidence. Callers cannot fabricate it; the type system refuses to accept a `VerifiedSignature` from anywhere except the designated constructor.

Will Crichton's [Typed Design Patterns for the Functional Era](https://arxiv.org/abs/2307.07069) develops this as the Witness pattern alongside three companions. The shared thesis is that a careful type system can move selected misuse from runtime into the compile-time construction of values. The value becomes a certificate, checked once at the moment it is built.

Here the philosophy meets a longer tradition. The Curry-Howard correspondence observes that a proposition is a type and a proof is a program that inhabits it. A value whose type can only be produced by establishing a condition is a small, practical instance of that correspondence. The assurance does not come from testing the value later. It comes from the rules of its construction.

The same idea applies to counterexample witnesses in testing. A witness value that carries the inputs, the expected output, the observed output, and the source hashes at the tested commit is a portable proof of a defect. Its existence establishes the bug; re-running it against a candidate fix establishes the repair. Section 8 shows this pattern operating in the ZenoDEX audit, where fix credit requires a witness that failed before repair and passes at the target.

### Illegal states and honest models

A value can be its own evidence, as the witness pattern shows. The same idea applies to the shape of the data itself. Yaron Minsky's mantra, [make illegal states unrepresentable](https://functional-architecture.org/make_illegal_states_unrepresentable), asks the modeler to choose a representation in which nonsensical values cannot be expressed.

The classic example turns a flat record full of nullable fields into a sum of products, one per meaningful state. A connection that is `Connecting` cannot carry a `when_disconnected` field, because the field lives only in the `Disconnected` variant. The invariant moves from a comment into the type.

```text
flat product:  state + server + last_ping_time? + last_ping_id? + session_id? + ...
                 any field can be present with any state, invariants live in comments

sum of products: Connecting(when_initiated)
               | Connected(last_ping option, session_id)
               | Disconnected(when_disconnected)
                 each variant carries only the fields its state permits
```

The architectural payoff is that the core's transition function now has a smaller honest domain. It does not need to defend against states the model already excludes. The boundary check moves from scattered runtime conditionals to one structural fact: the value's type. This is the same economy as the witness, applied to the shape of the state rather than to a single proof obligation.

The boundary is the natural place to enforce this. Bytes arrive untyped. The shell parses them once into a value whose type already excludes most nonsense. Downstream core code accepts only the parsed type. "Parse, don't validate" is the mnemonic for this discipline: validation performed once at the boundary, encoded in the type, is not repeated at every use. The [Functional Software Architecture](https://functional-architecture.org/) site pairs the mantra with the smart-constructor technique, where construction itself performs normalization and validation so that a value of the given type is honest by the time it exists.

Transitive immutability is a special case that deserves its own test. A frozen outer dataclass is honest only if every reachable child is also immutable. The ZenoDEX audit turns this into a falsifiable surface: each case in its `IMMUTABILITY_ALIAS` registry mutates a retained object and checks whether the committed state root changes. Six cases diverged, proving that the outer freeze was shallow. Section 8 describes the technique in detail.

### Where the pattern stops being enough

FCIS has an honest shortcoming, noted in the same community that codifies it. The shell handles the impure world, but using infrastructure is usually part of the domain logic: storing data, reading a file, calling a service. Pushing all of that into the shell can leave the shell holding substantial domain logic, growing complex and hard to maintain.

The natural evolution is to reify effects as values too. An effect becomes a data structure describing what should happen, produced by the core and interpreted by the shell. The core stays pure; the shell becomes an interpreter of effect values rather than a second home for domain decisions. Algebraic effect systems and the Composable Effects pattern take this direction. FCIS is the first cut. Effects as values is the refinement that keeps the boundary honest when the shell would otherwise re-acquire domain logic.

### The stance has limits

"Everything is a value" is a modeling stance, not a description of runtime reality. File descriptors, sockets, capabilities, closures over mutable state, and secret keys are not values in the serializable sense. The stance is useful because it names where the boundary ought to be drawn: authority-bearing runtime objects should be converted to values at the earliest honest point, and converted back to runtime objects only inside the shell, where authority is exercised. Section 5 returns to the objects that resist this conversion.

## 3. Precise vocabulary

Several related ideas are easy to blur together.

### Immutable value

An immutable value cannot change after construction. If a state update is accepted, the system creates a new state value and preserves the old value as it was.

Immutability must be **transitive**. A frozen record containing a mutable list is only shallowly immutable:

```python
@dataclass(frozen=True)
class State:
    balances: list[int]   # the list can still be changed elsewhere
```

A safer representation owns immutable children:

```python
@dataclass(frozen=True)
class State:
    balances: tuple[int, ...]
```

Production systems also need to consider references hidden inside library objects, foreign memory, caches, and handles. The meaningful question is whether any reachable authority-relevant state can change behind the core's back.

### Pure function

A pure function has two properties:

1. Its returned value depends only on its explicit arguments.
2. Evaluating it causes no externally observable effect.

This property supports **referential transparency**: an invocation may be replaced by its returned value without changing program meaning.

“Immutable function” is imprecise terminology. Values are immutable. Functions are pure or impure. A function object may be stored in an immutable field and still read a clock, mutate a global, or call a network service.

### Determinism

A transition is deterministic when the same valid explicit inputs, under the same specified semantics, always produce the same decision data.

```text
transition(S, C, P, E) = D

therefore every replay of (S, C, P, E) produces D
```

This excludes hidden dependence on:

- wall-clock time;
- environment variables;
- database contents not captured in `S`;
- network responses not captured in `E`;
- random values not present in the command or evidence;
- locale or platform-dependent formatting;
- unordered iteration;
- thread scheduling;
- floating-point behavior left outside the specification.

Randomized behavior can still have a deterministic core. The shell obtains randomness, records it as an explicit input, and the transition consumes that value. The same recorded input then replays exactly.

Purity is stronger than ordinary determinism. An impure function might deterministically append the same line to a log on every call. Its return value is predictable, but replacing the call with that value would remove an effect.

### Total and bounded transition

For assurance, the core should return a typed result for every input in its declared domain and should finish within stated resource bounds:

```text
transition : Input -> Reject | Accept
```

Malformed or unsupported inputs produce rejection values. They should not cause panics, silent fallback, unbounded allocation, or partial mutation.

## 4. A small transition example

Consider a constant-product exchange with reserves `x` and `y`. A command proposes an exact-input swap. Integer arithmetic and an explicit rounding rule are part of the policy.

```python
@dataclass(frozen=True)
class Pool:
    reserve_in: int
    reserve_out: int

@dataclass(frozen=True)
class SwapExactIn:
    gross_in: int
    min_out: int

@dataclass(frozen=True)
class Policy:
    fee_bps: int
    bps_denominator: int = 10_000

@dataclass(frozen=True)
class Transfer:
    asset: str
    amount: int
    sender: str
    recipient: str

@dataclass(frozen=True)
class Accepted:
    next_pool: Pool
    effects: tuple[Transfer, ...]
    amount_out: int

def transition(
    pool: Pool,
    command: SwapExactIn,
    policy: Policy,
) -> Accepted | Reject:
    if command.gross_in <= 0:
        return Reject("NON_POSITIVE_INPUT")

    fee = ceil_div(command.gross_in * policy.fee_bps,
                   policy.bps_denominator)
    net_in = command.gross_in - fee
    if net_in <= 0:
        return Reject("FEE_CONSUMES_INPUT")

    amount_out = (pool.reserve_out * net_in) // (pool.reserve_in + net_in)
    if amount_out < command.min_out:
        return Reject("SLIPPAGE")

    next_pool = Pool(
        reserve_in=pool.reserve_in + net_in,
        reserve_out=pool.reserve_out - amount_out,
    )
    effects = (
        Transfer("IN", net_in, "TRADER", "POOL"),
        Transfer("IN", fee, "TRADER", "FEE_ACCOUNT"),
        Transfer("OUT", amount_out, "POOL", "TRADER"),
    )
    return Accepted(next_pool, effects, amount_out)
```

This example omits several production details, including checked arithmetic, authenticated identities, asset newtypes, protocol fees, canonical encoding, and commitment roots. It still illustrates the core contract:

- no reserve is mutated during the calculation;
- rejection returns data and produces no effect;
- the output transfer is a value, not an immediate payment;
- exact rounding is reviewable;
- every dependency appears in the arguments.

The effect plan is an exact request for the shell to commit. It should not be vague “intent.” The commit layer checks that the plan is bound to the state snapshot and command that produced it.

## 5. What is a boundary?

A boundary is a point where assumptions, ownership, trust, representation, or effects change.

Common boundaries include:

- bytes entering a process;
- JSON becoming a typed command;
- a signature becoming an authenticated identity fact;
- an old state snapshot becoming a new committed state;
- a pure effect plan becoming network or database activity;
- one process sending data to another;
- one implementation being compared with an independent oracle.

A plain value makes such a boundary inspectable because it can be validated, logged, hashed, serialized, compared, replayed, and tested without executing the subsystem that created it.

The value is the **boundary representation**, not the physical boundary itself. A process boundary is enforced by an operating system. A trust boundary is enforced by validation and authority. A transaction boundary is enforced by atomic commit. Values make the contract at that boundary explicit.

### Can every value be a message?

Any value with an agreed, bounded representation can be used as message data. Many in-process values do not have such a representation:

- a pointer is meaningful only in an address space;
- a closure may contain code and captured mutable state;
- a file descriptor is an operating-system capability, not merely an integer;
- a database connection contains live protocol state;
- an object graph may contain cycles or aliases;
- a secret key should not cross most boundaries at all.

Those values need a deliberate protocol representation or an operating-system mechanism for transferring capability. “Everything is a value” is useful as a modeling stance. It does not make every runtime object safely serializable.

The Unix command `echo` offers a tiny example. It writes its arguments as text to standard output. A pipe can carry those bytes to another process. The receiving process still needs a protocol: encoding, delimiters, bounds, and meaning. Bytes crossing a pipe are a message only when sender and receiver agree on those rules.

### Should data and code be separate?

High-assurance systems benefit from separating **authority-bearing data** from **execution**:

- code defines how commands are interpreted;
- data supplies the current state, command, policy parameters, and evidence;
- the shell controls when effects are performed.

This distinction is semantic. Code itself can be encoded as data, and interpreters treat data as programs. Allowing arbitrary executable policy code, however, greatly expands the trusted computing base. A smaller design commits policy parameters as canonical data and interprets them with fixed, versioned code.

Data should remain close to its invariant definitions. A state schema, constructor, validator, canonical codec, commitment rule, and transition must share one semantic contract. Scattering them into directories without a single authoritative definition creates several incompatible meanings of “state version 2.”

## 6. How immutable values become coordination

Mutable shared objects coordinate by changing under participants. Every reader must ask whether another thread can change the object, which lock protects it, which version was observed, and whether a read was torn across updates.

An immutable snapshot gives every participant a stable fact:

```text
state root R0
   ├── worker A computes plan PA from R0
   ├── worker B computes plan PB from R0
   └── auditor replays both against R0
```

Planning can happen in parallel because no worker changes `R0`. The shell then commits with compare-and-swap semantics:

```text
commit(expected_root=R0, plan=PA)
```

If `R0` is still current, the commit succeeds and produces `R1`. A competing plan based on `R0` must fail without effects or be recomputed against `R1`.

This is coordination through explicit values:

- the pre-state root says what was observed;
- the command hash says what was requested;
- the policy version says which rules applied;
- the effect-plan hash says what may be committed;
- the next-state root says what the accepted result becomes;
- the receipt records the relationship among them.

Immutability does not remove coordination. It makes the coordination point small and visible. The atomic commit remains imperative and security-critical.

Two plans may be merged only when their effects commute or their read/write footprints are disjoint under a proved rule. File separation, thread separation, and separate snapshots do not establish noninterference.

This architecture connects naturally to **linearizability**. A linearizable concurrent operation appears to take effect at one instant between invocation and response, allowing a concurrent object to be understood through a sequential specification. The original definition is due to Herlihy and Wing in [Linearizability: A Correctness Condition for Concurrent Objects](https://www.cs.cmu.edu/~wing/publications/HerlihyWing90.pdf). In FCIS, the pure transition supplies the sequential meaning; atomic commit supplies the candidate linearization point.

## 7. Why testing becomes easier

Testing is easy when the unit under test has a complete value contract:

```text
input values -> returned value
```

A core test does not need a live database, network, clock, process supervisor, retry loop, or mock HTTP server. It constructs inputs and compares outputs.

```python
def test_slippage_rejects_without_effects():
    result = transition(
        Pool(1_000_000, 500_000),
        SwapExactIn(gross_in=10_000, min_out=5_000),
        Policy(fee_bps=30),
    )
    assert result == Reject("SLIPPAGE")
```

The same structure supports several assurance methods.

### Example and table tests

Each row contains explicit pre-state, command, policy, and expected result. Boundary conditions and rejection precedence become visible.

### Property tests

Pure functions support statements over large generated input spaces:

```text
accepted swap => reserves remain nonnegative
accepted swap => next invariant is at least the required bound
rejected swap => no next state and no effects
same input => same result
```

QuickCheck popularized this style of testing properties over generated data. Its original paper describes how pure functions allow specifications to be expressed at a fine granularity: [QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs](https://research.chalmers.se/en/publication/237427).

### Differential tests

Two independently written implementations receive the same input corpus. Their canonical decisions must agree:

```text
reference transition(input) == optimized transition(input)
reference transition(input) == proof-guest transition(input)
reference transition(input) == spreadsheet oracle(input)
```

Differential testing is most useful when the implementations do not share the same bug. Copying the production formula into a second language creates superficial diversity and common-mode failure.

### Metamorphic tests

When an exact answer is hard to supply, a relation between executions can still be checked. Examples include unit rescaling, permutation of independent commands, or splitting a fee-carry calculation into equivalent segments. Every metamorphic relation requires its own proof or specification argument.

### Mutation tests

A mutation tool removes or reverses a guard. A good test suite must fail. This answers a stronger question than code coverage: did a test depend on the invariant check?

### Exhaustive and formal checks

A small pure transition can be enumerated over a bounded domain, translated to SMT, or related to a mathematical definition in a proof assistant. The absence of I/O makes the semantic statement smaller.

Immutability alone does not provide these benefits. A frozen input passed to a function that reads a global database still has a hidden test dependency. The useful combination is explicit immutable inputs, a deterministic transition, and returned decision data.

## 8. A differential oracle audit

A spreadsheet can act as an executable review surface for deterministic integer rules. It is especially useful when reviewers are more comfortable tracing cells than reading Rust, Python, or proof-assistant code. The same discipline generalizes beyond spreadsheets to any independent oracle that computes expected values from a specification and compares them against implementation actuals.

The ZenoDEX audit, as it has evolved through several versions, follows this pattern. The current published snapshot is an audit console backed by JSON artifacts, generated from a pinned source commit, with a 67-case registry spanning swap math, fee splits, perp risk and oracle gates, zUSD liability and liquidation, multi-redeem ordering, and transitive immutability:

```text
pinned clean source commit
        │
        ├──► independent integer oracle computes expected values
        │
        ├──► runtime harness captures implementation actuals
        │
        ▼
per-case comparison: MATCH / EXPECTED_REJECT / DIVERGENCE
        │
        ▼
registry + global ledger + witnesses + BDD traceability + release claims
        │
        ▼
artifact manifest hashes every published artifact
```

The audit separates several jobs across its artifacts:

- a **formula registry** records each formula's identifier, unicode surface, MathML, meaning, and source paths, binding the specification to the code it governs;
- a **case registry** holds inputs, expected values from the oracle, observed values from the implementation, differences, and a semantic status per case;
- a **witness registry** records counterexample probes with pre-state roots, post-state roots, and per-file source hashes;
- a **BDD traceability** table connects Given/When/Then scenarios to evidence IDs and rates economic-semantics coverage;
- a **global ledger** tracks findings outside the scoped registry, with explicit status and remediation requirements;
- a **release-claims** block publishes booleans for full-value-moving coverage, main-branch promotion, and production release.

### One auditable row

For an exact-input constant-product swap:

```text
reserve_in       = 1,000,000
reserve_out      =   500,000
gross_input      =    10,000
fee_bps          =        30
bps_denominator  =    10,000
```

With fees rounded upward:

```text
fee       = ceil(10,000 × 30 / 10,000) = 30
net_input = 10,000 - 30                 = 9,970
amount_out = floor(500,000 × 9,970 / (1,000,000 + 9,970))
           = 4,935
next reserves = (1,009,970, 495,065)
```

The oracle places the input, formula, expected result, imported actual result, and status near one another. A reviewer can inspect the rounding direction and reproduce the calculation with a calculator. This is a human audit advantage that a green CI badge alone does not provide.

### What makes it differential?

The expected formula must be derived from the specification independently of the production implementation. The actual value must be exported from the implementation being tested. Both sides must bind to the same case identifier, units, policy version, and source commit.

A strong workflow is:

```text
pinned clean source commit
        │
        ▼
runtime harness emits canonical JSON actuals
        │
        ▼
independent integer oracle computes expected values
        │
        ▼
checker reads comparison results and classifies each case
        │
        ▼
artifact manifest hashes source, inputs, oracle, actuals, and outputs
```

Its methodology states its authority explicitly: expected values are computed by an independent integer oracle; implementation outputs are captured separately; `probe_executed` means only that the harness ran. Fix credit requires a deterministic witness that fails before repair and passes at the target.

### Techniques the oracle uses

Several techniques in the audit follow directly from the FCIS discipline. Each is a concrete instance of a principle from earlier sections.

**Formula-as-value with source binding.** Each formula in the registry is a value with an identifier, a unicode surface, a MathML rendering, a plain-language meaning, and a list of source paths. The specification is reified as data, hashable and comparable, bound to the exact source files it governs. A reviewer can ask which code implements a formula, or which formulas a given file participates in, by reading the registry rather than grepping comments.

**Cross-product reification to avoid division.** The zUSD multi-redeem selector must order vaults by collateral ratio. Comparing `collateral_a / debt_a` against `collateral_b / debt_b` would introduce floating-point division. The oracle reifies the comparison as an integer cross-product instead:

```text
a ≺ b  ⇔  collateral_a × debt_b  <  collateral_b × debt_a
```

Equal ratios break ties by ascending canonical vault ID. The comparison stays in the integer domain. The audit found that the implementation used debt-scaled absolute MCR headroom instead, which selects a different vault on several witness inputs. The cross-product formula is the denotation; the implementation diverged from it.

**Transitive immutability as a testable surface.** The registry includes a dedicated `IMMUTABILITY_ALIAS` surface with a formula stating that a frozen outer dataclass is insufficient when any reachable child or retained alias remains mutable. Each case in this surface mutates a retained object and checks whether the committed state root changes. Six cases diverged: mutating a retained `BalanceTable` changed a committed state root, proving that the outer freeze was shallow. Section 2 discusses transitive immutability as a philosophical claim; the audit turns it into a falsifiable, executable test.

**Conservation as explicit carry dust.** The fee-split formula requires that lane weights sum to 10,000 basis points and that all undistributed atoms remain explicit as carry dust:

```text
∀ i: lane_i = floor((fee + dust) × w_i / 10,000)
dust' = fee + dust − Σ_i lane_i
```

The dust is not lost. It is reified as a value that carries forward to the next distribution. A test can check that `dust'` equals the residual exactly, with no atom unaccounted for.

**Fail-closed oracle gates.** The perp oracle freshness gate is a conjunction in which every condition must hold:

```text
usable  ⇔  seen  ∧  price > 0  ∧  last ≤ now  ∧  now − last ≤ maxStaleness
```

Unseen, non-positive, future, and stale observations all fail closed. The oracle does not default to usable when a field is missing; absence is a rejection.

### Witnesses as content-addressed evidence

A witness is a value whose existence establishes a condition. In the audit, a counterexample witness is a value that establishes a defect. Each witness result carries:

- the inputs that triggered it;
- the expected output from the oracle;
- the observed output from the implementation;
- a `pre_root` and `post_root` over canonical dataclass JSON (for mounted state-machine probes);
- a `source_sha256` mapping each source file to its hash at the tested commit;
- a `remediation_requirement` stating what the fix must achieve;
- a status: `PASS` or `FAIL_REPRODUCED`.

A witness with status `FAIL_REPRODUCED` is a portable artifact. Anyone with the same source commit and the same inputs can reproduce the failure. Anyone with a candidate fix can re-run the witness and check whether it now passes. The witness is the boundary between "a bug was reported" and "a bug was proven": the report is a claim, the witness is the evidence.

Methodology states the credit rule explicitly: fix credit requires a deterministic witness that fails before repair and passes at the target. A passing test suite alone does not earn credit; the witness must have failed first.

### Scoped claims and the global ledger

A headline scope statement is published alongside the counts: counts apply only to the selected 67-case registry; the global ledger is separate and is not claimed complete. This is assumption hygiene made operational. The registry counts are scoped; the global ledger tracks findings outside that scope, with its own status values (`FIXED_REPRODUCED_AT_TARGET`, `OPEN_REPRODUCED`, `UNVERIFIED`, `OUT_OF_SCOPE`).

The release-claims block publishes three booleans:

```text
FullValueMovingCoverage      = false
MainBranchPromotionVerified  = false
ProductionReleaseAllowed     = false
```

Each is a value. The release decision is reified as data, not left as a judgment call. A reviewer can ask which evidence would flip a claim from false to true, and check whether that evidence exists.

Pending PRs are tracked with explicit baseline credit rules. A PR whose base is a parent draft receives `NONE_PARENT_DRAFT` credit. A PR whose head is an ancestor of the target receives `ANCESTOR_OF_TARGET` credit. The rule is stated in advance: pending code never changes selected registry counts. This prevents a common failure mode in which a fix is "in flight" and informally credited before it lands.

### Four independent passes

Four passes run in sequence, each checking a different question:

1. **Provenance and replay** verifies the source commit, parent, merge parents, PR states, and reachability from main.
2. **Implementation counterexamples** runs the witness probes against the implementation at the pinned commit.
3. **Semantic user-job review** rates BDD scenarios for economic-semantics coverage and runtime-spec parity.
4. **Presentation and artifact QA** checks that every required artifact is published, hashed, and manifest-consistent.

Each pass is an independent representation of the audit's question. Agreement across passes is stronger evidence than any single pass. Disagreement is a finding.

### What the audit found

After recalculation, the V6 registry contained 67 cases:

- 46 matched, including cases where rejection was the expected result;
- 15 were expected rejections that the implementation correctly rejected;
- 6 diverged, all on the `IMMUTABILITY_ALIAS` surface, where mutating a retained object changed a committed state root.

The global ledger carried 23 findings, of which 18 remained open blockers. The release-claims block remained all false. The audit's honest limitations are published as unresolved evidence: Rust and Lean replay runtimes were unavailable in the audit environment and receive no passing credit; committed-state and signed-intent alias fixes remain pending in open PRs; lifecycle, claimant, cancellation, expiry, recovery, shutdown, and terminal-drain coverage remains incomplete.

The transitive-immutability divergences are the same FCIS lesson stated in Section 2. Declaring an outer object frozen did not establish that all reachable state and intent data were immutable. The audit turned that philosophical claim into six falsifiable cases, and six cases failed.

### Numeric precision boundary

Spreadsheet engines and many runtime libraries use binary floating-point numbers. Integers are represented exactly only within a bounded range, commonly up to `2^53` for ordinary double-precision arithmetic. An oracle can therefore be exact for selected bounded vectors while failing to represent the full integer domain of a production protocol.

Products such as

```text
reserve × input × basis_points
```

may exceed that range even when each input appears reasonable. A serious oracle must do at least one of the following:

- prove that every intermediate value in the audited domain stays exact;
- use a decimal or big-integer mechanism with specified semantics;
- compare against text-encoded big integers calculated by a trusted extension;
- restrict the claim to bounded vectors whose exactness was checked.

The ZenoDEX oracle uses integer-only arithmetic throughout, with ceiling and floor rounding specified per formula. The honest claim for the audit is: **it gives human-and-machine-auditable differential checks over its selected registry and records important refinement gaps.** It does not prove cryptographic authenticity, runtime composition, full-domain arithmetic correctness, or specification completeness.

## 9. Does functional style reduce complexity?

There is no general theorem that functional programming produces lower cyclomatic or cognitive complexity than every imperative design.

Cyclomatic complexity counts independent control-flow paths. Translating the same five branches into a pure function does not make those branches disappear. Splitting code may lower the score of each function while leaving the system's semantic case count unchanged.

FCIS primarily attacks other kinds of complexity:

| Complexity | What makes it difficult | Effect of FCIS |
| --- | --- | --- |
| Control-flow | branches and loops | May improve through decomposition; not guaranteed |
| State-space | many mutable states | Reduced by immutable snapshots and explicit transitions |
| Temporal | correctness depends on call order | Reduced when pre-state and command are explicit |
| Aliasing | distant code can mutate shared objects | Reduced by transitive immutability and ownership |
| Dependency | clocks, globals, databases, environment | Exposed as arguments or shell operations |
| Concurrency | interleavings and races | Planning becomes parallel; commit conflicts remain |
| Effect | partial I/O, retries, duplicate delivery | Concentrated in a smaller shell |
| Conceptual | abstractions unfamiliar to maintainers | Can increase with dense combinators or type machinery |

The deepest reduction is in the number of histories a reviewer must imagine. With mutable state, an observed value depends on which operations ran before the current line and which aliases may run next. With an immutable input value, the relevant history is summarized by that value and its provenance.

Functional style can still become difficult to read. Giant pure functions, excessive abstraction, clever point-free expressions, poorly named combinators, or advanced type encodings can obscure a simple domain rule. Purity is an assurance tool. It does not replace decomposition, naming, domain modeling, or review.

John Hughes' [Why Functional Programming Matters](https://doi.org/10.1093/comjnl/32.2.98) argues that higher-order functions and lazy evaluation provide powerful forms of modular composition. That is a claim about ways to build and combine programs, not a universal promise that every complexity metric will fall.

## 10. Deep benefits that are easy to miss

### Equational reasoning

If `d = transition(s, c, p, e)`, an auditor can reason about `d` anywhere the same inputs occur. There is no need to reconstruct a hidden environment.

### Replay and incident reconstruction

A canonical input bundle can replay a historical decision exactly. This separates “what the rules decided” from “whether the shell committed or delivered it correctly.”

### Content addressing and commitments

Canonical immutable values can be hashed. State roots, command hashes, policy roots, and effect-plan hashes create stable names for semantic objects. A hash is useful only when the encoding, domain separation, and validation rules are canonical.

### Safe memoization

A pure transition can be cached by the hash of its complete input bundle. Reusing the result is sound when the core version, policy version, arithmetic semantics, and every other dependency are included in that identity. Hidden dependencies make memoization unsafe for the same reason that they make replay unsafe.

### Cheap snapshots and speculative work

Persistent data structures can share unchanged structure between state versions. Workers can evaluate candidate commands, proofs, or optimizations against a stable root without copying an entire database or taking a global write lock.

### Smaller trusted computing base

The core can often avoid database drivers, HTTP clients, logging frameworks, and platform APIs. Fewer dependencies participate in the semantic decision. The shell remains trusted for authentication, exact binding, atomicity, and effects.

### Independent representations

The same transition can be expressed as readable reference code, optimized code, a spreadsheet, an SMT model, and a proof-assistant definition. Agreement across genuinely independent representations provides evidence against local implementation mistakes.

### Better failure records

Typed rejection values make failure precedence observable. A rejected decision can be logged and compared without leaving partially changed state behind.

### Safer use of generative models

A model can propose a command, policy candidate, proof candidate, or effect plan as untrusted data. A deterministic core and governed verifier decide whether that value satisfies the rules. Probabilistic generation does not need authority to mutate committed state.

## 11. Advanced concepts built on FCIS

### Witness types

A witness is a value whose construction establishes a condition needed by another operation. A private constructor can prevent ordinary application code from inventing `VerifiedSignature`, `FreshPrice`, or `AuthorizedMint` values.

The witness must bind to the exact subject it proves: command hash, pre-state root, policy version, verifier identity, freshness interval, and evidence hash. A generic `verified=True` boolean carries almost no assurance.

Will Crichton's [Typed Design Patterns for the Functional Era](https://arxiv.org/abs/2307.07069) catalogs this as the Witness pattern alongside state-machine, parallel-list, and registry patterns. Section 2 discusses the philosophical thesis they share; the practical concern here is binding.

### Typestate and state-machine types

Distinct types represent stages such as:

```text
UntrustedBytes
  -> BoundedBytes
  -> CanonicalCommand
  -> AuthenticatedCommand
  -> ValidatedDecision
  -> CommitPlan
  -> CommittedReceipt
```

An API can make it impossible to call `commit` with raw bytes. This establishes a local construction property. It does not prove that the validator's rules are complete or correct.

### Linear and affine capabilities

Some values should be consumed at most once: a commit capability, nullifier reservation, withdrawal authorization, or one-shot receipt. Linear or affine type disciplines can express this ownership. A distributed system still needs durable exactly-once or idempotency mechanisms because processes can crash and messages can be retried.

### Effect systems and algebraic effects

An effect system records which computations may read state, throw errors, perform I/O, or use nondeterminism. This can make the core/shell division compiler-visible. The practical goal is to prevent an apparently pure semantic path from acquiring an ambient effect through a helper function.

### Refinement

Let `T_spec` be the mathematical transition and `T_impl` the executable core. A refinement claim has a shape such as:

```text
decode(T_impl(encode(x))) = T_spec(x)
```

for every valid `x` in a stated domain. This requires proofs or tests for encoding, decoding, arithmetic bounds, rejection mapping, and output equality.

The shell needs a separate refinement argument:

```text
accepted commit
  => authenticated inputs matched the core inputs
  ∧ committed pre-root matched the observed pre-root
  ∧ committed next-state and effects matched the returned plan
  ∧ reject committed nothing
```

A proof of the core does not establish this shell property.

### Translation validation

When an optimizer, compiler, proof generator, spreadsheet, or model produces an artifact, a small checker can validate each output against the reference semantics. Trust moves from the generator to the checker and the statement it checks.

### Commutativity and effect algebras

Effect plans may carry explicit read and write sets. If two accepted transitions commute,

```text
T(T(s, a), b) = T(T(s, b), a),
```

and their external effects have a compatible composition law, they may be reordered or parallelized. This equality must include rejection and effect-plan behavior, not only the final state.

### Monotonicity and deterministic parallelism

Some systems accumulate facts in a partial order: information only grows. Monotone operations can often be evaluated concurrently and merged deterministically. LVars are one example of lattice-based shared structures designed for deterministic parallelism: [Freeze After Writing: Quasi-Deterministic Parallel Programming with LVars](https://scholarworks.iu.edu/dspace/items/060499ca-6a17-4626-b837-7738785832a3).

Non-monotone decisions such as “spend this coin exactly once” or “accept only if no conflicting command exists” still need coordination.

### Transactional outbox and idempotent delivery

The shell can atomically commit the new state, receipt, and an outbox record. A separate worker delivers the external effect using an idempotency key. A crash before commit leaves nothing to deliver. A crash after commit allows safe retry. This closes a gap left by the simple phrase “execute effects and commit.”

## 12. Common failure modes

### Shallow immutability

The outer record is frozen while a nested list, map, buffer, or referenced object remains mutable.

### Hidden ambient inputs

The transition silently reads time, environment, configuration, global caches, filesystem state, or unordered collections.

### Authority encoded as a boolean

Raw evidence arrives beside `verified=True`, and application code is trusted to set the flag honestly.

### Effect before final decision

The system reserves funds, inserts a nullifier, or sends a message before every semantic and binding check succeeds.

### Giant pure core

Purity is preserved, but unrelated invariant families accumulate in one function. Local auditability and change isolation disappear.

### Shell duplicates semantics

The shell recomputes fees, authorization, or next state instead of committing the core's exact plan.

### Spreadsheet common-mode bias

The expected formula is copied from implementation code, actuals are typed by hand, units are implicit, formulas use inexact numbers, or the spreadsheet engine is unpinned.

### Formal proof over the wrong statement

The theorem is machine-checked, but the model omits authentication, freshness, overflow, canonical encoding, or atomic commit. Proof establishes the declared statement only.

## 13. A practical design checklist

For each operation, write down:

1. **State:** What immutable snapshot fully determines the semantic context?
2. **Command:** What exact action is requested?
3. **Policy:** Which versioned parameters change the decision?
4. **Evidence:** Which authenticated facts are required, and what exact subject does each bind?
5. **Transition:** What total deterministic function returns rejection or acceptance?
6. **Effects:** What exact plan is derived from an accepted decision?
7. **Commit:** What state root and plan hash must the atomic commit compare?
8. **Replay:** Which canonical values allow the decision to be reproduced?
9. **Tests:** Which examples, properties, mutants, differential oracles, and formal obligations cover the rules?
10. **Non-claims:** Which properties remain outside the core, model, workbook, or current evidence?

A useful module structure is:

```text
model          immutable State, Command, Policy, Decision, Effect values
invariants     pure predicates over those values
transition     State × Command × Policy × Evidence -> Decision
codec          one canonical wire representation
commitment     hashes and roots over canonical representations
shell          authentication, storage, I/O, atomic commit, delivery
```

These files may be separate. Their semantic definitions must remain unified. The shell can depend inward on every core module. Core modules must not depend outward on the shell.

## Conclusion

FCIS is a way to make a system's meaning inspectable.

The functional core turns an immutable description of the world into immutable decision data. The imperative shell captures trusted inputs, commits the decision atomically, and manages unreliable effects. Canonical values connect the two sides. They also connect implementations, tests, spreadsheets, proof models, concurrent workers, incident replays, and human reviewers.

The strongest benefit is a reduction in hidden history. A reviewer can ask what a value means, where it came from, which rule produced it, and which exact effect it authorizes. That is the beginning of assurance.


## Further reading

- Gary Bernhardt, [Boundaries](https://www.destroyallsoftware.com/talks/boundaries).
- Will Crichton, [Typed Design Patterns for the Functional Era](https://arxiv.org/abs/2307.07069).
- John Hughes, [Why Functional Programming Matters](https://doi.org/10.1093/comjnl/32.2.98).
- Koen Claessen and John Hughes, [QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs](https://research.chalmers.se/en/publication/237427).
- Maurice Herlihy and Jeannette Wing, [Linearizability: A Correctness Condition for Concurrent Objects](https://www.cs.cmu.edu/~wing/publications/HerlihyWing90.pdf).
- Active Group, [Functional Software Architecture](https://functional-architecture.org/). A community site codifying values, principles, and patterns for functional programming in the large, including Functional Core, Imperative Shell; Make Illegal States Unrepresentable; and Composable Effects.
- [Journal of Functional Programming](https://www.cambridge.org/core/journals/journal-of-functional-programming). The journal devoted to the design, implementation, reasoning, and application of functional programming languages, spanning theory to industrial practice.
- [ZenoDEX Oracle Audit V6](https://zenodex-oracle-audit-v4.jazzy-harp-9002.chatgpt.site/). A published differential oracle audit with a 67-case registry, counterexample witnesses, BDD traceability, and hashed artifacts, demonstrating the techniques described in Section 8.
