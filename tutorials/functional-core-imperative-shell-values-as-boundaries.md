---
title: "Functional Core, Imperative Shell: How Immutable Values Become Boundaries"
layout: docs
kicker: Tutorial 64
description: "A practical and formal introduction to the philosophy and practice of functional core, imperative shell: pure transitions, immutable values as boundaries, differential oracle audits, counterexample witnesses, concurrency, and assurance."
---

# Functional Core, Imperative Shell: How Immutable Values Become Boundaries

Software becomes difficult to audit when one block of code reads hidden state, makes a decision, mutates several objects, calls external systems, and reports success. The reader must reconstruct which inputs were observed, which rules determined the result, and which effects were committed. Ordinary tests may pass while replay, comparison, and causal explanation remain difficult.

The functional-core/imperative-shell pattern, abbreviated **FCIS**, gives those responsibilities a visible shape:

<figure class="fp-figure">
  <p class="fp-figure-title">The FCIS value flow</p>
  {% include diagrams/fcis-core-shell-flow.svg %}
  <figcaption class="fp-figure-caption">
    Untrusted bytes enter the shell, which parses them into bounded, canonical, authenticated values.
    Those values feed a pure transition function. The transition returns either a typed rejection or
    an acceptance carrying the next state, an effect plan, and a receipt draft. The shell then
    atomically commits and delivers effects.
  </figcaption>
</figure>

The core answers a question: **given these exact facts, what is the permitted result?** The shell deals with the changing world: clocks, networks, databases, files, authentication, retries, process failures, and concurrency.

Gary Bernhardt's talk [Boundaries](https://www.destroyallsoftware.com/talks/boundaries) presents the practical insight behind this organization: simple values can form boundaries between subsystems. This tutorial develops that insight into a high-assurance design discipline.

## How to read this tutorial

For the philosophical argument, read Sections 2, 10, and 11. For the engineering pattern, read Sections 1, 4, 5, 6, 12, and 16. For the audit methodology, read Sections 8 and 9. For the concurrency story, read Section 7. For the pattern's limits and costs, read Sections 2, 10, and 14. The sections are designed to be readable independently after reading this guide.

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

<figure class="fp-figure">
  <p class="fp-figure-title">The dependency direction is one-way</p>
  {% include diagrams/fcis-dependency-rule.svg %}
  <figcaption class="fp-figure-caption">
    The shell may depend on core modules: model, invariants, transition, codec, and commitment.
    The core must not depend on the shell. This keeps semantic rules free of database, network,
    clock, and filesystem knowledge.
  </figcaption>
</figure>

The core knows about values and rules. It does not know which database, HTTP client, spreadsheet, clock, or proof service happens to surround it.

## 2. The claim behind the pattern

FCIS rests on a thesis about what makes software hard to reason about. The thesis is that hidden history is the dominant cost, and that immutable values are the cheapest way to make history visible.

### Identity through time, or its absence

A mutable object keeps an identity across change. The account object at noon and the "same" account at one minute past noon hold different balances, yet share one name. This works because the system supplies a convention: an identity that survives mutation, threading before and after together.

A value needs no such convention. The integer `5` has no before and after. It cannot change, so the question of whether it is the same value at two times does not arise. Two separately constructed immutable objects can still be distinct objects with equal values. The useful claim is that **stable value equality often makes object identity irrelevant**. A reviewer tracks what the value contains instead of which mutable object it is.

The consequence shows up in review. With a mutable account, the sentence "the balance is 100" can become false before a reader finishes reading it. With an immutable snapshot, the proposition remains fixed relative to that snapshot. Provenance still determines whether the snapshot is authentic, current, and relevant.

### Outputs are entailed by inputs

A pure function has no hidden causes. Its result is entailed by its arguments in the sense that a theorem is entailed by its premises: given the inputs, the output is necessary.

```text
transition(S, C, P, E) = D
```

Entailment is a strong property. The function can be lifted out of its calling context and studied alone. An impure function breaks entailment because part of what determines its result, or its effect, lives outside the argument list, in a clock, a database, a global, or a network. The result then depends on facts the reader cannot see.

This claim assumes the same complete inputs and specified execution semantics. Arithmetic overflow, encoding rules, platform-defined operations, and undefined behavior can make the same source expression behave differently across implementations. Purity excludes hidden inputs; it does not make execution environments identical.

### From interface dependencies to data dependencies

Gary Bernhardt's [Boundaries](https://www.destroyallsoftware.com/talks/boundaries) identifies the move that makes the rest possible. Two subsystems joined by a method call are coupled in time: one must invoke the other while both are alive, in some agreed order, holding some agreed locks. Two subsystems joined by a value are coupled only by the value. Each can run at any time, in any process, in any order; the value mediates.

```text
interface dependency:  A calls B.method(x)        -- A depends on B's behavior, alive, in order
data dependency:       A produces v; B consumes v -- A and B depend only on v
```

The phrase "values as boundaries" names this replacement. A live relationship becomes a static one. A dependency on behavior becomes a dependency on data. Live behavior can fail, race, or retry while it is being observed. A value remains stable enough to store, copy, hash, sign, replay, and compare. The value can still encode a false or stale claim, so provenance and validation remain essential.

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

The strongest form of this idea places evidence of a checked construction inside the value's type. A `VerifiedSignature` that can only be constructed by a procedure that actually checked the signature records that construction fact. Within an adequately enforced module and type boundary, ordinary callers cannot fabricate it through supported code paths.

This is a language-relative guarantee. Reflection, unsafe casts, deserialization, or module-system escape hatches may bypass a private constructor. The type documents and structures a trusted construction path; it does not establish cryptographic unforgeability. The assurance comes from the construction rules that the language and module system actually enforce.

Will Crichton's [Typed Design Patterns for the Functional Era](https://arxiv.org/abs/2307.07069) develops this as the Witness pattern alongside three companions. The shared thesis is that a careful type system can move selected misuse from runtime into the compile-time construction of values. The value becomes a certificate, checked once at the moment it is built.

Here the philosophy meets a longer tradition. The Curry-Howard correspondence observes that a proposition is a type and a proof is a program that inhabits it. A value whose type can only be produced by establishing a condition is a small, practical instance of that correspondence. The assurance does not come from testing the value later. It comes from the rules of its construction.

The same idea applies to counterexample witnesses in testing. A witness value that carries the inputs, the expected output, the observed output, and the source hashes at the tested commit is portable, reproducible evidence of divergence. Its force depends on the oracle, bindings, and replay procedure being correct. Re-running it against a candidate fix checks whether that divergence remains. Section 9 shows this pattern operating in the ZenoDEX audit, where fix credit requires a witness that failed before repair and passes at the target.

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

Transitive immutability is a special case that deserves its own test. A frozen outer dataclass is honest only if every reachable child is also immutable. The ZenoDEX audit turns this into a falsifiable surface: each `IMMUTABILITY_ALIAS` case mutates a retained object and checks whether the committed state root or later behavior changes. Section 9 describes the technique in detail.

### The deepest benefit: local reasoning

Every discipline in this tutorial, including immutability, purity, explicit inputs, typed rejections, and canonical encoding, supports **local reasoning**. A reviewer can open a transition function and identify the complete value inputs that determine its result. The supporting functions, codecs, types, and specification remain relevant, while unrelated threads and unrecorded time slices should not.

The same property appears in modular arithmetic, lexical scoping, and mathematical proof. Computing `7 mod 5` does not require the history of `7`. A lexically scoped variable is determined by its binding environment rather than by unrelated callers. A proof step is checked from its stated premises and rules.

Mutable shared state expands a local expression's dependency surface because a read may depend on prior writes across aliases and threads. FCIS makes the relevant history explicit as a value and passes it inward. The practical measure is: **how large is the dependency surface a reviewer must read, and how many possible histories must they imagine, to assess one decision?** FCIS aims to bound both questions by the transition's declared model.

This connects to separation logic, discussed in Section 17. The frame rule supports reasoning about a program fragment using the resources it touches while framing out disjoint resources. FCIS does not establish disjoint footprints by itself. Explicit ownership, read and write sets, and separation conditions are still required.

### Historical reconstruction and evidential value

Mutable state often makes one present condition compatible with several prior histories. An observer seeing a balance of 100 cannot infer whether it was deposited, transferred, minted, or repaired. An immutable snapshot preserves one state. A replay record preserves the transition inputs needed to explain a claimed derivation of that state.

Their evidential value depends on provenance, canonical encoding, and trustworthy capture. A snapshot with unknown provenance is an unsupported claim. A replay record whose inputs were not authenticated establishes only what the declared rules would decide for those inputs.

### A snapshot as a model-relative world

In a declared state-transition model, an immutable snapshot represents one modeled world. It fixes every fact that the model says is relevant to the transition, and those facts do not change while the transition runs. The transition relation states which modeled worlds are reachable under which commands, policies, and evidence.

This description is model-relative. The snapshot is not a complete assignment of every fact in the deployed environment. Network latency, hardware state, operator intent, or an omitted authority may remain outside it. Requirements completeness and model adequacy are separate assurance obligations.

The deployed system can continue to evolve while a snapshot remains stable. Two workers can plan against the same root because both refer to the same modeled pre-state. Their plans still require conflict checks and an atomic commit against the current root.

### Where the pattern stops being enough

FCIS has an honest shortcoming, noted in the same community that codifies it. The shell handles the impure world, but using infrastructure is usually part of the domain logic: storing data, reading a file, calling a service. Pushing all of that into the shell can leave the shell holding substantial domain logic, growing complex and hard to maintain.

The natural evolution is to reify effects as values too. An effect becomes a data structure describing what should happen, produced by the core and interpreted by the shell. The core stays pure; the shell becomes an interpreter of effect values rather than a second home for domain decisions. Algebraic effect systems and the Composable Effects pattern take this direction. FCIS is the first cut. Effects as values is the refinement that keeps the boundary honest when the shell would otherwise re-acquire domain logic. Section 12 develops this refinement.

This creates an expression-problem tradeoff at the effect boundary. Adding a new effect constructor generally requires updating existing handlers. Adding another handler is straightforward when the effect algebra is fixed. Reification makes that tradeoff explicit; it does not make both extensibility axes free.

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

## 6. The shell's contract

The core's contract is a function signature. The shell's contract is an effect protocol. Five obligations make that protocol explicit.

### 1. Exact input and evidence binding

The shell passes the exact canonical command, authenticated identity facts, consensus inputs, and captured pre-state to the core. It does not add, drop, reorder, or silently default semantic fields. Each evidence value binds to the subject it supports, such as the command hash, pre-state root, policy version, verifier identity, and freshness context.

The shell may authenticate transport and construct typed provenance. The core remains authoritative for semantic admission and authorization. A transport identity answers who established the session; it does not by itself answer whether the requested state transition is permitted.

### 2. Atomic compare-and-swap

An accepted commit atomically publishes the next state, exact effect plan, replay identity, receipt, outbox records, and any protocol nonce or nullifier. The storage operation compares the expected pre-state root or version before publication.

A crash before the atomic commit point leaves the prior committed state authoritative. A crash after that point leaves the new bundle authoritative and recoverable. The shell must not expose a half-published combination of old state, new effects, or missing replay data.

### 3. Typed rejection and committed failure

An ordinary rejection commits no post-state and authorizes no effects. If protocol semantics intentionally consume a nonce, charge a fee, or record another authoritative change on failure, the core returns a distinct committed-failure result with an explicit state and effect plan. Calling that outcome a no-op rejection would hide a real transition.

Operational logging of an uncommitted rejection may still occur in the shell. Such telemetry is not part of authoritative protocol state unless the core explicitly returns it as a committed effect.

### 4. Crash recovery and idempotent delivery

External effects may be attempted more than once. The outbox and destination protocol must make retries idempotent or detect duplicates. A useful canonical delivery key includes the replay identity and the effect's canonical identity or index. The effect-plan hash alone may collide across distinct commands that authorize equal plans.

Idempotency is an end-to-end property of the delivery protocol. A shell cannot guarantee it merely by sending a header if the receiver ignores the key and the shell keeps no durable acknowledgement.

### 5. Versioned receipts and canonical encoding

A receipt binds every authority-relevant field needed by its claim: pre-state root, command hash, evidence root, policy and core versions, replay identity, next-state root, effect-plan hash, and authenticated time or finality context when relevant. The canonical encoding specifies version, tags, widths, normalization, ordering, and domain separation independently of in-memory layout.

Omitting a field can permit rebinding or make the receipt incomplete for a proposed claim. The omission does not automatically make every receipt forgeable. The exact consequence depends on the signature, commitment, and verification protocol.

### Shell decisions and core decisions

The shell legitimately handles:

- byte bounds, canonical decoding, and malformed-input rejection;
- transport authentication and capture of provenance;
- snapshot acquisition and version checks;
- atomic storage, crash recovery, and effect delivery;
- retry, backoff, and dead-letter handling.

The core handles:

- semantic admission and authorization;
- amounts, fees, ordering, freshness rules, and replay policy;
- next-state and exact effect-plan construction;
- typed rejection precedence and committed-failure semantics.

A differential oracle can test the core's transition semantics. A separate commit audit must test input binding, compare-and-swap conflicts, crash points, replay, outbox behavior, and destination idempotency. Passing one layer supplies no evidence for the other unless the corresponding objects and checks are included.

## 7. How immutable values become coordination

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

Immutability does not remove coordination. It makes the state-publication point small and visible. The atomic commit remains imperative and security-critical. Snapshot acquisition, authentication, evidence capture, and external delivery may have coordination protocols of their own.

Two plans may be merged only when their effects commute or their read/write footprints are disjoint under a proved rule. File separation, thread separation, and separate snapshots do not establish noninterference.

This architecture connects naturally to **linearizability**. A linearizable concurrent operation appears to take effect at one instant between invocation and response, allowing a concurrent object to be understood through a sequential specification. The original definition is due to Herlihy and Wing in [Linearizability: A Correctness Condition for Concurrent Objects](https://www.cs.cmu.edu/~wing/publications/HerlihyWing90.pdf). In FCIS, the pure transition supplies the sequential meaning; atomic commit supplies the candidate linearization point.

## 8. Why testing becomes easier

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

This narrows the **test oracle problem**, the problem of determining the expected result for a test input. Agreement between independent computations is evidence against local implementation mistakes. It is not proof of correctness because both implementations may share a requirement or specification error. Barr, Harman, McMinn, Shahbaz, and Yoo survey this problem and its automation strategies in [The Oracle Problem in Software Testing](https://discovery.ucl.ac.uk/id/eprint/1471263/).

### Metamorphic tests

When an exact answer is hard to supply, a relation between executions can still be checked. Examples include unit rescaling, permutation of independent commands, or splitting a fee-carry calculation into equivalent segments. Every metamorphic relation requires its own proof or specification argument.

### Mutation tests

A mutation tool removes or reverses a guard. A good test suite must fail. This answers a stronger question than code coverage: did a test depend on the invariant check?

### Exhaustive and formal checks

A small pure transition can be enumerated over a bounded domain, translated to SMT, or related to a mathematical definition in a proof assistant. The absence of I/O makes the semantic statement smaller.

Immutability alone does not provide these benefits. A frozen input passed to a function that reads a global database still has a hidden test dependency. The useful combination is explicit immutable inputs, a deterministic transition, and returned decision data.

## 9. A differential oracle audit

A spreadsheet can act as an executable review surface for deterministic integer rules. It is especially useful when reviewers are more comfortable tracing cells than reading Rust, Python, or proof-assistant code. The same discipline generalizes beyond spreadsheets to any independent oracle that computes expected values from a specification and compares them against implementation actuals.

The audit pattern follows a source-pinned workflow:

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

The audit separates several jobs across typed artifacts:

- a **formula registry** records each formula's identifier, unicode surface, MathML, meaning, and source paths, binding the specification to the code it governs;
- a **case registry** holds inputs, oracle results, observed implementation results, differences, and a semantic status per case;
- a **witness registry** records counterexample probes with pre-state roots, post-state roots, and per-file source hashes;
- a **BDD traceability** table connects Given/When/Then scenarios to evidence IDs and rates economic-semantics coverage;
- a **global ledger** tracks findings outside the scoped registry, with explicit status and remediation requirements;
- a **release-claims** block records checker-derived status for each declared claim.

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

Equal ratios break ties by ascending canonical vault ID. The comparison stays in the integer domain. A differential case can then expose any implementation that orders by a different score while keeping the finding bound to explicit inputs.

**Transitive immutability as a testable surface.** A dedicated `IMMUTABILITY_ALIAS` surface states that a frozen outer dataclass is insufficient when a reachable child or retained alias remains mutable. Each case mutates a retained object and checks whether the committed state root or later transition behavior changes. Section 2 states the design obligation; the audit turns it into a falsifiable test.

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

A witness with status `FAIL_REPRODUCED` is a portable artifact. Anyone with the same source commit, toolchain, and inputs can attempt to reproduce the divergence. Anyone with a candidate fix can re-run it and check whether the same comparison now passes. The witness is stronger than an unaided bug report because it binds the claim to executable evidence. It does not prove that the oracle or requirement is correct.

Methodology states the credit rule explicitly: fix credit requires a deterministic witness that fails before repair and passes at the target. A passing test suite alone does not earn credit; the witness must have failed first.

### Scoped claims and the global ledger

A headline scope statement is published alongside the counts: counts apply only to the selected 67-case registry; the global ledger is separate and is not claimed complete. This is assumption hygiene made operational. The registry counts are scoped; the global ledger tracks findings outside that scope, with its own status values (`FIXED_REPRODUCED_AT_TARGET`, `OPEN_REPRODUCED`, `UNVERIFIED`, `OUT_OF_SCOPE`).

The release-claims block publishes three booleans:

```text
FullValueMovingCoverage      = false
MainBranchPromotionVerified  = false
ProductionReleaseAllowed     = false
```

Each is a value derived by the release checker from declared gates. A producer must not self-declare a passing claim. A reviewer can ask which evidence would change a claim from false to true and inspect whether the checker consumed that evidence.

Pending code does not change audited counts until it is part of the pinned target and its witness passes there. This prevents informal credit for fixes that have not reached the artifact under review.

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

### Detailed case study

The evolving registry counts, reproduced divergences, global-ledger findings, tool availability, and release status belong to the versioned [ZenoDEX Oracle Audit V6](https://zenodex-oracle-audit-v4.jazzy-harp-9002.chatgpt.site/) case study. Keeping those results outside this tutorial separates a reusable method from evidence that can change at each audited revision.

## 10. Does functional style reduce complexity?

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

### When the pattern fights the domain

FCIS is easiest when the semantic state and effects have bounded value representations. Several conditions make the boundary expensive or incomplete:

- **Large hot working sets.** An algorithm may depend on in-place updates for its latency or memory target. The core can use mutation inside a fresh, exclusively owned local builder, provided no alias escapes and the returned state is immutable. Copying a full state on every transition is unnecessary when persistent structures, immutable regions, or bounded projections preserve the same observable semantics.
- **Authority-bearing runtime objects.** Hardware signing keys, file descriptors, device memory, and kernel capabilities cannot honestly become ordinary serializable values. Draw the core boundary around the capability. Pass authenticated observations and typed requests as values while the shell retains and exercises the authority.
- **External systems without atomicity or idempotency.** A remote service may offer neither transactions nor duplicate suppression. The shell then needs an explicit delivery protocol, acknowledgements, compensation, or a saga. A pure effect plan describes the authorized result; it cannot manufacture guarantees that the destination does not provide.
- **Incomplete or expensive snapshots.** Capturing every environmental fact may be impossible or too slow. A scoped projection can work when its completeness condition, source root, freshness rule, and omitted facts are explicit. An undocumented partial snapshot creates hidden inputs again.

Pure transitions do not inherently require serializing and deserializing every in-process call. Serialization is required when a value crosses a persistence, process, language, or trust boundary that needs a stable wire representation. The design question is therefore local: which semantic decisions benefit from a pure value contract, and where must controlled mutation or live authority remain?

## 11. Deep benefits that are easy to miss

### Equational reasoning

If `d = transition(s, c, p, e)`, an auditor can reason about `d` anywhere the same inputs occur. There is no need to reconstruct a hidden environment.

### Replay and incident reconstruction

A canonical input bundle can replay a historical decision exactly. This separates “what the rules decided” from “whether the shell committed or delivered it correctly.”

Replay checks the core decision under the pinned implementation and semantics. It does not establish that the shell authenticated the inputs correctly, committed atomically, or delivered the authorized effects. Those are separate shell-refinement claims.

### The audit trail as an executable semantic record

Conventional logs describe events after they occur and may be incomplete, reordered, or inconsistent with committed state. A canonical replay bundle has a stronger role: it contains the modeled inputs needed to re-execute a core decision.

For the declared core model, the sequence

```text
(State, Command, Policy, Evidence) -> Decision
```

is an executable semantic record. An auditor can replay the same bundle through the pinned transition and compare canonical outputs. A differential oracle evaluates the same inputs through an independently derived implementation.

This record is not the deployed system's entire history. Input acquisition, authentication, atomic publication, crash recovery, and external delivery remain shell events. A complete audit therefore combines semantic replay with commit and delivery evidence.

### Content addressing and commitments

Canonical immutable values can be hashed. State roots, command hashes, policy roots, and effect-plan hashes create stable names for semantic objects. A hash is useful only when the encoding, domain separation, and validation rules are canonical.

### Safe memoization

A pure transition can be cached by the hash of its complete input bundle. Reusing the result is sound when the core version, policy version, arithmetic semantics, and every other dependency are included in that identity. Hidden dependencies make memoization unsafe for the same reason that they make replay unsafe.

### Cheap snapshots and speculative work

Persistent data structures can share unchanged structure between state versions. Workers can evaluate candidate commands, proofs, or optimizations against a stable root without copying an entire database or taking a global write lock.

Path copying and structural sharing provide the implementation basis for this property. Their actual time and space bounds depend on the selected data structure and access pattern. Chris Okasaki develops the relevant techniques in [Purely Functional Data Structures](https://doi.org/10.1017/CBO9780511530104.003).

### Smaller trusted computing base

The core can often avoid database drivers, HTTP clients, logging frameworks, and platform APIs. Fewer dependencies participate in the semantic decision. The shell remains trusted for authentication, exact binding, atomicity, and effects.

### Architectural confinement of authority

The shell possesses capabilities such as database connections, network sockets, signing keys, and filesystem handles. The core receives values describing authorized operations. With an enforced dependency boundary, the core cannot exercise capabilities it cannot reach directly.

This is a confinement property, not proof that the shell follows the principle of least authority. The shell may still hold broader capability than one operation requires. Capability scoping, process isolation, and deployment policy remain separate obligations.

### Independent representations

The same transition can be expressed as readable reference code, optimized code, a spreadsheet, an SMT model, and a proof-assistant definition. Agreement across genuinely independent representations provides evidence against local implementation mistakes.

### Better failure records

Typed rejection values make failure precedence observable. A rejected decision can be logged and compared without leaving partially changed state behind.

### Safer use of generative models

A model can propose a command, policy candidate, proof candidate, or effect plan as untrusted data. A deterministic core and governed verifier decide whether that value satisfies the rules. Probabilistic generation does not need authority to mutate committed state.

### Team cognition as a measurable hypothesis

FCIS supplies a shared vocabulary: state, command, policy, evidence, transition, rejection, effect, commit, and receipt. That vocabulary may shorten review and onboarding by localizing disagreements to explicit contracts. This is a hypothesis rather than an architectural guarantee. Teams can test it by tracking review time, escaped defects, and onboarding effort before and after adoption.

## 12. Effects as values

The first FCIS cut can leave the shell interpreting vague instructions and re-acquiring domain logic. A stronger boundary makes effects typed values. The core constructs a canonical plan, and the shell interprets that plan using capabilities the core cannot access.

```python
from dataclasses import dataclass
from enum import Enum
from typing import Literal

class DestinationId(Enum):
    SETTLEMENT_WEBHOOK = "webhook:settlement"
    TRANSFER_EVENTS = "eventbus:transfers"

class LedgerNamespace(Enum):
    ACCOUNT = "account"
    RECEIPT = "receipt"

@dataclass(frozen=True)
class LedgerKey:
    namespace: LedgerNamespace
    record_id: bytes

@dataclass(frozen=True)
class LedgerWrite:
    key: LedgerKey
    canonical_value: bytes
    expected_version: int

@dataclass(frozen=True)
class OutboxEffect:
    destination: DestinationId
    payload: bytes

@dataclass(frozen=True)
class EffectPlan:
    ledger_writes: tuple[LedgerWrite, ...]
    outbox_effects: tuple[OutboxEffect, ...]

@dataclass(frozen=True)
class DeliveryResult:
    destination: DestinationId
    status: Literal["delivered", "retryable_failure", "terminal_failure"]
    attempt: int
    external_id: str | None
```

The core selects an allowlisted destination identifier instead of constructing a URL, topic, or connection string. The shell owns the mapping from identifiers to infrastructure configuration. Ledger writes remain inside the atomic commit. Outbox effects are recorded with that commit and delivered afterward. The plan's canonical encoder must also define effect ordering and its duplicate policy.

For an outbox effect at canonical index `i`, the shell derives a delivery key from the replay identity, `i`, destination, and canonical payload. The receiver or durable delivery ledger must honor that key for idempotency:

```python
def deliver(
    effect: OutboxEffect,
    infra: Infrastructure,
    replay_identity: ReplayIdentity,
    index: int,
) -> DeliveryResult:
    key = derive_delivery_key(replay_identity, index, effect)
    endpoint = infra.destinations.resolve(effect.destination)
    return endpoint.deliver(effect.payload, idempotency_key=key)
```

The core decides which domain effect is authorized. The shell decides how to carry it out and records a typed delivery outcome. Adding an effect constructor requires updating handlers that interpret the closed effect sum. Changing infrastructure for an existing constructor can remain a shell-only change.

## 13. Advanced concepts built on FCIS

### Witness types

A witness is a value whose construction establishes a condition needed by another operation. Within an enforced module and type boundary, a private constructor can prevent ordinary application code from inventing `VerifiedSignature`, `FreshPrice`, or `AuthorizedMint` values through supported code paths.

The witness must bind to the exact subject it proves: command hash, pre-state root, policy version, verifier identity, freshness interval, and evidence hash. A generic `verified=True` boolean carries almost no assurance.

Will Crichton's [Typed Design Patterns for the Functional Era](https://arxiv.org/abs/2307.07069) catalogs this as the Witness pattern alongside state-machine, parallel-list, and registry patterns. Section 2 discusses the philosophical thesis they share; the practical concern here is binding.

### Typestate and state-machine types

Distinct types represent stages such as:

<figure class="fp-figure">
  <p class="fp-figure-title">A typestate pipeline from bytes to receipt</p>
  {% include diagrams/fcis-typestate-pipeline.svg %}
  <figcaption class="fp-figure-caption">
    Each step narrows what the value can carry. Red and orange stages live in the shell.
    Blue stages are boundary values or core decisions. The final green stage records the shell's commit.
  </figcaption>
</figure>

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

## 14. Costs, performance, and migration

### The cost profile

FCIS changes where a system spends resources.

Potential costs include:

- allocation for new state, effect, and receipt values;
- canonicalization and hashing at persistence or trust boundaries;
- memory overhead from persistent structures and retained snapshots;
- representation conversion between optimized runtime layouts and canonical wire values;
- conceptual overhead when a small problem receives unnecessary type machinery.

Potential savings include:

- less lock contention during speculative planning;
- stable cache keys when every dependency and version is included;
- deterministic replay instead of open-ended forensic reconstruction;
- reduced alias defense inside a transitively immutable ownership boundary;
- a smaller semantic dependency set for tests and review.

These are conditional effects. An immutable snapshot can be stale relative to current state even though the snapshot itself remains stable. Planning may still serialize on evidence acquisition or another scarce resource. Hashing may dominate a small transition, while a persistent tree may make a large update cheaper than copying.

Benchmark the actual state representation, transition mix, contention, allocation, encoding, hashing, and recovery workload. A fresh, exclusively owned local builder may use mutation internally when it never escapes, shares no aliases with committed state, is discarded on rejection, and freezes its result at the boundary.

### Migration: extract one transition at a time

Most systems begin with mixed mutable code. A bounded migration can proceed as follows:

1. **Choose one authority-bearing transition.** Prefer an operation with clear rules, expensive defects, or repeated audit disputes.
2. **Close its requirements.** Inventory actors, inputs, authority, time, state, effects, rejection precedence, crash behavior, and recovery paths.
3. **Define owned values.** Capture state, command, policy, and evidence in typed, transitively immutable forms with a versioned canonical codec where persistence or comparison requires one.
4. **Extract an executable reference.** Implement a deterministic transition that returns typed rejection, acceptance, or committed failure without ambient I/O.
5. **Mount a narrow shell adapter.** Bind one authoritative snapshot, invoke the transition, and atomically commit the exact accepted bundle.
6. **Compare safely.** Replay a recorded corpus and use shadow evaluation that does not execute a second set of effects. Add generated boundary states, negative vectors, and mutation tests rather than relying only on ordinary production traffic.
7. **Gate activation.** Declare the required parity, invariant, crash, replay, and performance evidence. Specify activation, rollback, and forward recovery before moving authority.
8. **Remove duplicate semantics.** Once the new path owns the transition, delete or disable the legacy calculation so the shell cannot drift into a second implementation.

This resembles a strangler migration applied to semantic authority. Each slice should have one accountable contract owner and an explicit non-claim for behavior that remains in the legacy path.

## 15. Common failure modes

### Shallow immutability

The outer record is frozen while a nested list, map, buffer, or referenced object remains mutable.

### Hidden ambient inputs

The transition silently reads time, environment, configuration, global caches, filesystem state, or unordered collections.

### Authority encoded as a boolean

Raw evidence arrives beside `verified=True`, and application code is trusted to set the flag honestly. A subject-bound witness can make routine fabrication harder within an enforced construction boundary. It cannot compensate for an incorrect verifier or a runtime that permits unrestricted reconstruction.

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

### Insufficient delivery identity

The effect-plan hash alone is used as an idempotency key. Distinct commands that produce equal plans can then collide, while two effects inside one plan may be indistinguishable. Derive a canonical delivery identity from the replay identity and the effect's canonical identity or index, then require the destination or delivery ledger to honor it.

## 16. A practical design checklist

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

## 17. Connections

These connections illuminate FCIS from neighboring disciplines. They do not import those disciplines' guarantees automatically.

### Separation logic and the frame rule

John Reynolds' [Separation Logic: A Logic for Shared Mutable Data Structures](https://www.cs.cmu.edu/~jcr/seplogic.pdf) supports local reasoning about controlled portions of a heap. Its separating conjunction and frame rule depend on explicit ownership and disjointness conditions.

FCIS pursues a related architectural goal by giving a transition an explicit modeled footprint. Purity alone does not prove that two transitions are independent. A sound frame-style argument still needs declared read and write sets, resource ownership, and a proof that framed state cannot affect the decision.

### Capability-based security

Capability security asks which authority a component can actually exercise. An FCIS core can be confined to ordinary values while the shell retains database, network, signing, and filesystem capabilities. This prevents the core from directly exercising authority outside its effect vocabulary when the dependency boundary is enforced.

The result is confinement, not automatic least authority. The shell's process, credentials, destination mapping, and deployment policy must still be scoped and audited.

### Datomic and point-in-time database values

[Datomic](https://docs.datomic.com/datomic-overview.html) illustrates several value-oriented storage ideas. Its datoms are immutable, transactions add assertions or retractions without erasing prior datoms, and applications can query a point-in-time database value. Transactions remain serialized per database, which makes the coordination tradeoff explicit.

Datomic is an example of persistent facts and database values. A system using Datomic still needs its own semantic core, authority model, effect protocol, and shell-refinement evidence.

### Persistent data structures

Okasaki's [Purely Functional Data Structures](https://doi.org/10.1017/CBO9780511530104.003) develops persistent structures that reuse unchanged components across versions. For common balanced tree designs, an update copies a path while a snapshot can share the existing root. Exact complexity depends on the chosen structure, operation, evaluation strategy, and workload.

This implementation work explains how immutable snapshots can be practical. It does not imply that every state representation has constant-time snapshots or logarithmic updates.

### The end-to-end argument

Saltzer, Reed, and Clark's [End-to-End Arguments in System Design](https://www.cs.princeton.edu/~jrex/teaching/spring2005/reading/saltzer84.pdf) concerns the placement of functions whose complete implementation requires endpoint knowledge. Lower layers may still provide useful performance enhancements.

FCIS offers an analogy for semantic authority. Infrastructure can authenticate transport, store bytes, and deliver plans, while the component with the complete declared rules decides the semantic transition. The analogy has limits. The core is not necessarily a network endpoint, and the shell remains a trusted protocol participant with its own correctness obligations.

### The test oracle problem

Testing needs a way to decide whether an observed result is correct. Differential oracles narrow this problem by comparing independently derived implementations over the same canonical inputs. Agreement remains evidence because both sides can share an incorrect requirement. Section 8 describes the practical testing method, and Section 9 shows how to package its evidence.

## Conclusion

FCIS is a way to make a system's meaning inspectable.

The functional core turns an immutable description of the world into immutable decision data. The imperative shell captures trusted inputs, commits the decision atomically, and manages unreliable effects. Canonical values connect the two sides. They also connect implementations, tests, spreadsheets, proof models, concurrent workers, incident replays, and human reviewers.

The strongest benefit is a reduction in hidden history. A reviewer can ask what a value means, where it came from, which rule produced it, and which exact effect it authorizes. That is the beginning of assurance.

### The pattern in one paragraph

Capture the relevant pre-state, requested action, governing policy, and authenticated evidence as immutable values. Feed them to a deterministic core that returns typed rejection, acceptance, or committed failure. For acceptance, return the exact next state, canonical effect plan, and replay record. Atomically compare and publish the full bundle, then deliver outbox effects through an idempotent protocol. Canonically encode every authority-relevant value that must persist or cross a trust boundary. The core computes the declared denotation. The shell acquires inputs, publishes decisions, and exercises capabilities. Their contract is the typed, versioned boundary representation together with the invariants that govern it.


## Further reading

- Gary Bernhardt, [Boundaries](https://www.destroyallsoftware.com/talks/boundaries).
- Will Crichton, [Typed Design Patterns for the Functional Era](https://arxiv.org/abs/2307.07069).
- John Hughes, [Why Functional Programming Matters](https://doi.org/10.1093/comjnl/32.2.98).
- Koen Claessen and John Hughes, [QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs](https://research.chalmers.se/en/publication/237427).
- Maurice Herlihy and Jeannette Wing, [Linearizability: A Correctness Condition for Concurrent Objects](https://www.cs.cmu.edu/~wing/publications/HerlihyWing90.pdf).
- John C. Reynolds, [Separation Logic: A Logic for Shared Mutable Data Structures](https://www.cs.cmu.edu/~jcr/seplogic.pdf).
- Jerome H. Saltzer, David P. Reed, and David D. Clark, [End-to-End Arguments in System Design](https://www.cs.princeton.edu/~jrex/teaching/spring2005/reading/saltzer84.pdf).
- Chris Okasaki, [Purely Functional Data Structures](https://doi.org/10.1017/CBO9780511530104.003).
- Datomic, [Architecture Overview](https://docs.datomic.com/datomic-overview.html).
- Earl T. Barr, Mark Harman, Phil McMinn, Muzammil Shahbaz, and Shin Yoo, [The Oracle Problem in Software Testing](https://discovery.ucl.ac.uk/id/eprint/1471263/).
- Active Group, [Functional Software Architecture](https://functional-architecture.org/). A community site codifying values, principles, and patterns for functional programming in the large, including Functional Core, Imperative Shell; Make Illegal States Unrepresentable; and Composable Effects.
- [Journal of Functional Programming](https://www.cambridge.org/core/journals/journal-of-functional-programming). The journal devoted to the design, implementation, reasoning, and application of functional programming languages, spanning theory to industrial practice.
- [ZenoDEX Oracle Audit V6](https://zenodex-oracle-audit-v4.jazzy-harp-9002.chatgpt.site/). A published differential oracle audit with a 67-case registry, counterexample witnesses, BDD traceability, and hashed artifacts, demonstrating the techniques described in Section 9.
