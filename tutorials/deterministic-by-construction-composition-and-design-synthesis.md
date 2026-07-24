---
title: "Deterministic by Construction: Operating Systems, Composition, and Design Synthesis"
layout: docs
kicker: Tutorial 65
description: "From the mathematical shape of determinism, through the Determinator deterministic operating system and Kahn process networks, into composition, compositionality, and design synthesis within the functional core / imperative shell pattern."
---

# Deterministic by Construction: Operating Systems, Composition, and Design Synthesis

A transition system is deterministic when a current state and a supplied input admit at most one next result. A complete execution is fixed only after its initial state, external input history, program, and execution semantics are fixed. A system is deterministic by construction when its enforced interface rules out undeclared sources of choice within that model. This tutorial develops that distinction from its mathematical roots, through the design of a deterministic operating system, into the composition of deterministic components, and finally into the practice of design synthesis within the functional core / imperative shell pattern.

The inspiration is the Determinator, an experimental operating system built at Yale by Amittai Aviram, Shu-Chun Weng, Sen Hu, and Bryan Ford. Its microkernel provides only shared-nothing address spaces and deterministic interprocess communication primitives. Under the kernel's abstract-machine assumptions, unprivileged computation is precisely repeatable even when the program is buggy or malicious. The OSDI '10 paper introducing it won the Jay Lepreau Best Paper Award. The Determinator shows how a platform can enforce determinism inside a declared boundary instead of leaving the property to programmer discipline.

```text
                    DETERMINISTIC BY CONSTRUCTION

     INPUTS (explicit relative to the declared model)
     ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐
     │  S  │  │  C  │  │  P  │  │  E  │
     └──┬──┘  └──┬──┘  └──┬──┘  └──┬──┘
        └────────┴────────┴────────┘
                    │
                    ▼
          ┌─────────────────────┐
          │  DETERMINISTIC      │
          │  TRANSITION         │
          │                     │
          │  f(S,C,P,E) = D     │
          │                     │
          │  no hidden state    │
          │  no ambient I/O     │
          │  no scheduling      │
          │  dependence         │
          └─────────┬───────────┘
                    │
                    ▼
          ┌─────────────────────┐
          │  RESULT (at most 1) │
          │                     │
          │  every replay of    │
          │  (S,C,P,E) yields D │
          │                     │
          │  same inputs under  │
          │  the same semantics │
          │  imply the same     │
          │  result             │
          └─────────────────────┘

     The box is the guarantee, relative to its stated boundary.
     The architecture enforces that boundary for unprivileged code.
```

The inputs enter a deterministic transition. If the transition produces a result, that result is unique. A separate totality claim is needed to show that every declared input produces a result, and a separate boundedness claim is needed to show that it does so within a resource limit. The determinism guarantee says that the enforced boundary admits no undeclared source of choice.

<figure class="fp-figure">
  <p class="fp-figure-title">The determinism contract: four facts fix one run</p>
  {% include diagrams/determinism-contract.svg %}
  <figcaption class="fp-figure-caption">
    The architecture controls the middle box. Completeness of the world model and
    correctness of the specification remain separate obligations.
  </figcaption>
</figure>

This tutorial extends the previous one, [Functional Core, Imperative Shell: How Immutable Values Become Boundaries](../functional-core-imperative-shell-values-as-boundaries/). FCIS established that immutable values and pure functions create a boundary between semantic computation and imperative effect. Here the question changes shape: what happens when that boundary is enforced by architecture rather than by convention? The Determinator answers at the operating-system level. FCIS answers at the application level. The mathematical structure is shared.

## How to read this tutorial

For the mathematical foundations, read Sections 1, 6, and 8. For the operating-system architecture, read Sections 4 and 5. For the philosophical argument about assurance, read Sections 2, 3, and 15. For composition and its algebra, read Sections 8, 9, 10, and 11. For the connection to FCIS and design practice, read Sections 12 and 13. The sections are designed to be readable independently after this guide.

---

## 1. What determinism means

### The mathematical definition

Let `Σ` be a set of states and `I` a set of inputs. A transition relation

```text
    R ⊆ (Σ × I) × Σ
```

is **deterministic** when it is right-unique:

```text
    R((s, i), s1) and R((s, i), s2)  implies  s1 = s2.
```

One state-input pair therefore has at most one successor. It may have none, for example because the machine halts or the transition is undefined. A deterministic relation is the graph of a partial function:

```text
    deterministic:     δ : State × Input ⇀ State
                       one state + one input  ⇒  at most one next state

    nondeterministic:  R ⊆ (State × Input) × State
                       one state + one input  ⇒  possibly many next states
```

If every state-input pair has a successor, the relation is also **total**, and it is equivalent to an ordinary function:

```text
    δ : Σ × I → Σ
```

Another common model makes halting, rejection, and failure explicit:

```text
    step : Σ × I → Next(Σ) | Halt(Output) | Reject(Error)
```

This `step` function can be total even when execution stops, because stopping is represented as a result. The distinction matters: determinism gives **at most one** result; total determinism gives **exactly one** modeled result.

The distinction is not about predictability in practice. A chaotic system can be deterministic: its future is uniquely fixed by its initial condition and input history, even though small measurement errors make long-term prediction impractical. A system can also be nondeterministic while having a predictable probability distribution. The question is whether the model admits more than one result from the same state and input.

### Determinism is a property of the transition, not the observer

A common confusion treats determinism as a property of what an observer can predict. Determinism is a property of the system's transition structure. A system can be deterministic and unpredictable, as chaos is. A system can be nondeterministic and statistically predictable, as a fair coin is. The question is whether the next state is uniquely fixed by the current state and input, not whether someone can guess it.

### The shape of determinism

```text
         NONDETERMINISTIC                    TOTAL DETERMINISTIC

         s0, i                               s0, i
          │                                    │
          ├──→ s1                              │
          ├──→ s2                              ▼
          └──→ s3                             s1

         one input,                          one input,
         many possible                       exactly one
         outcomes                            outcome

         relation R ⊆ (Σ×I) × Σ             function δ : Σ×I → Σ
```

The nondeterministic shape is a fan-out: one state-input pair admits several futures. A deterministic step admits zero or one. A total deterministic step admits exactly one modeled result. The architectural question is what structure prevents the fan-out.

### Totality and boundedness

For assurance, determinism alone is insufficient. A transition may also need to be total on its declared domain and bounded by an explicit resource measure:

```text
    step : Σ × I → Result
    cost(step, s, i) ≤ B(size(s), size(i))
```

Here `cost` might count instructions, memory cells, messages, or another stated resource. The bound `B` must use the same unit. A partial function can be deterministic where defined. A terminating function can be deterministic without having a useful uniform resource bound. When a design claims all three properties, each needs its own argument:

| Property | Exact claim |
| --- | --- |
| Determinism | A declared input admits at most one result. |
| Totality | Every input in the declared domain produces a modeled result. |
| Boundedness | A stated resource measure never exceeds a stated bound. |

The previous tutorial used this trio for FCIS transitions. This tutorial asks how architecture can enforce the first property and support proofs of the other two.

---

## 2. Deterministic by construction versus deterministic by testing

### The testing approach and its limits

A conventional system attempts determinism through discipline:

```text
    programmer avoids randomness
    programmer avoids shared mutable state
    programmer avoids timing dependence
    programmer avoids unordered iteration
    programmer avoids platform-specific behavior
    programmer avoids ...

    then: a test suite checks that outputs match
```

This approach has a structural weakness. The absence of nondeterminism is a universal property over the executions admitted by the model. Ordinary sampling tests can demonstrate nondeterminism by finding divergent replays, but a finite non-exhaustive suite does not establish its absence. Exhaustive exploration can prove the property for a finite, accurately modeled state space. A proof or construction argument can cover an infinite family, provided its assumptions match the implementation.

### The construction approach

A system is deterministic by construction, relative to a declared machine model, when its enforced operations make undeclared choice unrepresentable inside that model. The property is established by the system's structure rather than by programmer vigilance alone:

```text
    CONSTRUCTION ENFORCES DETERMINISM

    The system provides ONLY:

    • isolated execution units (no shared state)
    • deterministic communication (rendezvous)
    • explicit input channels (no ambient reads)
    • no clocks, no randomness, no scheduling
      visible to unprivileged code

    Therefore, within the enforced abstract machine:
    unprivileged code cannot introduce an undeclared
    source of scheduling choice
```

The analogy to type safety is useful. A sound type system rules out a declared class of bad programs under its typing and execution rules. A deterministic-by-construction system similarly rules out a declared class of scheduling-dependent behaviors under its machine model. Neither guarantee extends beyond its assumptions.

### A construction-as-proof analogy

The previous tutorial noted that, under Curry-Howard, constructing a value of a proposition-as-type can constitute a proof. There is a looser systems analogy here: if every admitted primitive and composition rule preserves determinism, constructing a system only from those rules yields a structural argument for determinism. This is not itself an instance of the Curry-Howard correspondence unless the architecture and proof are encoded in an appropriate type theory.

```text
    Curry-Howard, literally:
        type            = proposition
        value           = proof
        construction    = establishment of the proposition

    Systems analogy:
        admitted primitives preserve determinism
        composition rules preserve determinism
        constructed system inherits determinism
```

### What construction cannot enforce

Honest limits matter. The Determinator construction can enforce that unprivileged code does not add an undeclared scheduling choice under the kernel's assumptions. It cannot establish that the specification is complete, that inputs capture all relevant facts, or that physical hardware behaves as modeled. A deterministic system with an incomplete input model is deterministic relative to its model and potentially wrong relative to the world. Section 15 returns to these non-claims.

---

## 3. The assurance benefits of determinism

### Replay

If a system is deterministic, then recording the initial state and every external input can be sufficient to reproduce its execution under the same program and specified machine semantics. Exact replay also requires any versioned configuration, binary, or semantics that can affect the run. This transforms debugging, auditing, and incident reconstruction:

```text
    NONDETERMINISTIC SYSTEM:
        incident occurs
        → reconstruct approximate state from logs
        → guess at scheduling, timing, interleaving
        → reproduce "maybe" on a similar machine
        → hope the bug manifests again

    DETERMINISTIC SYSTEM:
        incident occurs
        → retrieve recorded input sequence
        → replay under the same specified semantics
        → observe identical execution
        → locate the exact divergence point
```

The Determinator's design makes this concrete. Nondeterministic events are converted into explicit I/O that a privileged space can mediate and log. Replaying those inputs under the same executable semantics reproduces the unprivileged computation without recording internal scheduling choices.

### Comparison

Two terminating executions of a deterministic system with the same initial state, inputs, program, and execution semantics must produce the same output. This makes differential testing, regression detection, and multi-implementation comparison tractable in principle:

```text
    deterministic system A(input) = output1
    deterministic system B(input) = output2

    output1 ≠ output2  ⇒  A and B disagree on this input
                           (the discrepancy is not explained
                            by an admitted schedule choice)
```

Without determinism, a disagreement might be explained by scheduling. With deterministic implementations and fixed inputs, it is a reproducible behavioral discrepancy. Deciding which implementation matches the intended semantics still requires a specification or oracle.

### Audit

An auditor examining a deterministic system can reason locally. Given the recorded inputs and the transition rules, the output is entailed. There is no need to reconstruct a hidden execution history, to imagine alternative schedules, or to consider what might have happened if a thread had run slightly faster.

```text
    AUDIT OF A DETERMINISTIC SYSTEM:

    initial state:    s0
    recorded inputs:  I1, I2, ..., In
    transition rule:  δ
    claimed output:   O

    check:  δ(δ(...δ(s0, I1)..., In-1), In) = O ?

    one calculation. no imagination required.
```

### Security: determinism is not constant time

Deterministic execution does not by itself eliminate timing leakage. A deterministic program may take a repeatable but secret-dependent number of steps. An external observer who measures response time can still learn about the secret.

```text
    deterministic program:
        steps(secret_0) = 1,000
        steps(secret_1) = 2,000

    same secret ⇒ same step count
    different secrets ⇒ distinguishable timing
```

The follow-up [Deterland](https://dedis.cs.yale.edu/cloud/papers/trios15-deterland.pdf) work adds the missing controls. Guest code sees artificial time based on instruction counts, and I/O passes through a timing mitigator that paces external observations. Even then, the claim is a configurable bound on external timing leakage, not that ordinary determinism automatically makes code constant-time.

### The assurance hierarchy

```text
    WEAK ──────────────────────────────────────────── STRONG

    "we try to       "we test for     "the architecture   "the architecture
     avoid races"     races"           makes races         makes races
                                       unlikely"           unrepresentable"

    discipline       testing          probabilistic       structural
    (human)          (empirical)      guarantee           guarantee
                                     (engineering)       (mathematical)
```

The rightward direction represents stronger evidence for a precisely scoped claim. Under the Determinator paper's kernel and processor assumptions, unprivileged spaces constrained to the kernel API cannot introduce scheduling-dependent behavior. External input, kernel or processor bugs, and properties such as termination remain outside that claim.

---

## 4. The Determinator: a deterministic operating system

### The thesis

The Determinator is an experimental multiprocessor, distributed operating system designed to make an application's computation exactly repeatable within its abstract-machine boundary. It consists of a microkernel and a set of user-space runtime libraries and applications. The microkernel provides a minimal API and execution environment, supporting a hierarchy of shared-nothing address spaces that can execute in parallel, while enforcing the guarantee that these spaces evolve and interact deterministically. Atop this minimal environment, the user-space runtime adapts optimistic replication techniques to offer a private workspace model for both thread-level and process-level parallel programming.

The key insight is architectural. Within the platform boundary, repeatability is enforced by the kernel rather than trusted to the program. A supervisory space still has to mediate and, for replay, record genuinely nondeterministic external input.

### The design principles

The Determinator's kernel API rests on three principles:

```text
    PRINCIPLE 1: ISOLATE
     Isolate the working state of concurrent activities
     between synchronization points.

     No shared state. No global filesystem. No writable
     shared memory. Each concurrent activity operates in
     a private sandbox.

     PRINCIPLE 2: PRIVATE NAMESPACES
     Provide thread-private namespaces with
     application-chosen names.

     The system does not assign process IDs, memory
     addresses, or file handles from a global pool.
     Application code decides where to allocate and
     what names to use. No system-chosen names means
     no system-introduced nondeterminism.

     PRINCIPLE 3: DETERMINISTIC SYNCHRONIZATION
     Spaces synchronize only at well-defined points
     in both spaces' execution.

     Rendezvous semantics: a parent blocks until its
     child stops. No asynchronous signals. No
     interrupts visible to unprivileged code. No
     scheduling-dependent communication.
```

The private-namespace principle deserves emphasis. A system that assigns identifiers from a global pool introduces nondeterminism whenever allocation order depends on scheduling. Hash-table iteration order, process IDs, and file descriptor allocation are familiar sources of this. The Determinator removes the entire class by letting each space name its own resources.

### The space hierarchy

```text
    THE DETERMINATOR SPACE HIERARCHY

                     ┌──────────┐
                     │   ROOT   │  ← starts with I/O authority
                     │  SPACE   │     (authority may be delegated)
                     └────┬─────┘
                          │
                 ┌────────┼────────┐
                 │        │        │
            ┌────┴───┐ ┌─┴────┐ ┌─┴────┐
            │SPACE 1 │ │SPACE 2│ │SPACE 3│
            └────┬───┘ └──────┘ └──┬───┘
                 │                  │
            ┌────┴───┐        ┌────┴───┐
            │SPACE 1a│        │SPACE 3a│
            └────────┘        └────────┘

     • Each space: single-threaded, private virtual memory
     • No space can outlive its parent
     • A space interacts ONLY with immediate parent and children
     • No shared state between siblings
     • No global namespace
     • Arbitrarily deep nesting
```

A Determinator space resembles a single-threaded Unix process, with critical differences. It has no access to a global filesystem. It has no shared memory with siblings. It cannot receive asynchronous signals. It cannot read a clock. Its only communication is with its immediate parent and children, through the kernel's communication primitives.

### Why this enforces determinism

The argument is structural:

```text
    1. Each space executes sequential code deterministically.
       (Single-threaded, no shared state, no ambient I/O.)

    2. Spaces interact only through the kernel's
       deterministic communication primitives.
       (Rendezvous: both parties must be at the
        synchronization point. No race on who arrives first.)

    3. The order of interactions is determined by the
       program's control flow, not by scheduling.
       (A parent's sequence of calls is fixed by its code.
        A child's sequence of returns is fixed by its code.)

    4. Therefore: the entire computation is a deterministic
       function of the inputs to the root space.

    Parallelism affects WHEN spaces execute.
    It does not affect WHAT they compute.
```

The fourth step is the conclusion, and it follows from the first three. Each step is enforced by the kernel API, not by programmer cooperation.

---

## 5. Spaces, Put/Get/Ret: the minimal deterministic API

### The three primitives

The Determinator kernel exposes a small set of communication primitives. The design literature describes them as operations that copy register state and virtual memory ranges between a parent space and a child space, with rendezvous semantics. Following the Determinator's published design, they can be summarized as:

```text
    ┌─────────────────────────────────────────────────────────┐
    │  Put(child, regs, mem, start)                           │
    │  Copy register state and/or a virtual memory range      │
    │  INTO a child space. Optionally start the child         │
    │  executing.                                             │
    │                                                         │
    │  Get(child, regs, mem, changes)                         │
    │  Copy register state, a virtual memory range, and/or    │
    │  the changes since the last snapshot OUT OF a child.    │
    │                                                         │
    │  Ret()                                                  │
    │  Stop executing and wait for the parent to issue a      │
    │  Get or Put. Processor traps cause an implicit Ret.     │
    └─────────────────────────────────────────────────────────┘
```

The exact syscall surface varies across the research prototypes and the instructional PIOS derivative. The structural guarantee does not depend on the precise names. It depends on three properties: communication is by copy between private spaces, synchronization is by rendezvous, and no primitive reveals scheduling or timing to unprivileged code.

### The interaction pattern

```text
    PARENT SPACE                    CHILD SPACE
     ────────────                    ───────────

     Put(child, init_regs,
         init_mem, start)
          │
          │  ── data flows in ──→  begins executing
          │                              │
          │                              │  (computes
          │                              │   deterministically)
          │                              │
          │                              ▼
          │                           Ret()
          │                              │
          │  ←── rendezvous ────         │
          │                              │
     Get(child, result_regs,
         result_mem)
          │
          ▼
     (continues with child's results)
```

The rendezvous semantics are the load-bearing detail. When a parent calls Get on a child that is still executing, the parent blocks until the child calls Ret. When a child calls Ret, it blocks until the parent calls Get or Put. Both parties must arrive at the synchronization point. The order of arrival does not matter. The data exchanged is determined by the program, not by timing.

### What the API excludes

The power of the Determinator's API is as much in what it omits as in what it provides:

```text
    EXCLUDED FROM UNPRIVILEGED CODE:
     ✗ shared memory between spaces
     ✗ global filesystem
     ✗ asynchronous signals
     ✗ clock reads
     ✗ random number generation
     ✗ direct network I/O without delegated I/O authority
     ✗ system-chosen identifiers (PIDs, addresses)
     ✗ unordered iteration over shared structures
     ✗ thread scheduling visibility

     PROVIDED:
     ✓ private virtual memory (per space)
     ✓ private register state (per space)
     ✓ deterministic parent-child communication
     ✓ snapshot and restore of child state
     ✓ hierarchical nesting (arbitrary depth)
```

### The user-level runtime

Normal applications do not use the kernel API directly. Atop the minimal kernel, a user-level runtime library uses distributed systems techniques to emulate familiar abstractions:

```text
    KERNEL LAYER (deterministic by construction):
        spaces, Put, Get, Ret

    USER-LEVEL RUNTIME (emulation):
        Unix processes    ←→  space subtrees
        threads           ←→  spaces within a process
        filesystem        ←→  hierarchical space storage
        shared memory     ←→  deterministic reconciliation protocol
        external I/O      ←→  explicit files and parent mediation

    The runtime is untrusted. It may be buggy. It may crash.
    It cannot add an undeclared scheduling choice through
    the kernel API, under the kernel and processor assumptions.
```

This separation is architecturally significant. The runtime can be complex, buggy, and replaced. The kernel's determinism guarantee is independent of the runtime's functional correctness. A buggy runtime may reject, stop, diverge, or produce a wrong result. When it produces a result from the same recorded inputs, the kernel model makes that result repeatable.

The private workspace model is the runtime's central trick. Each thread or process gets an optimistic replica of the state it needs. Reads happen locally against the replica. When work is reconciled, write/write conflicts become reliably detected rather than silently corrupting. Read/write data races, the kind that make ordinary shared-memory threading nondeterministic, do not arise because no two workspaces share mutable memory during execution.

---

## 6. Kahn process networks: the mathematical guarantee

### The formal model

The Determinator paper motivates its determinism argument using Kahn Process Networks (KPNs), introduced by Gilles Kahn in 1974. In the textbook KPN model, deterministic sequential processes communicate through unbounded, single-writer, single-reader FIFO channels. Reads block when a channel is empty; writes do not block because the channels are mathematically unbounded. A process cannot test whether a channel is empty and branch on that timing fact.

```text
    KAHN PROCESS NETWORK

    ┌─────┐         ┌─────┐         ┌─────┐
    │ P1  │──ch1──→│ P2  │──ch2──→│ P3  │
    └─────┘         └──┬──┘         └─────┘
                       │
                       │ ch3
                       ▼
                   ┌─────┐
                   │ P4  │
                   └─────┘

    • Each Pi is a deterministic sequential process
    • Each chj is a unidirectional FIFO channel
    • Each channel has exactly one writer and one reader
    • Reads block; writes are nonblocking in the ideal model
    • A process cannot inspect channel availability
    • The denotation is independent of relative process speed
```

### The determinism theorem

The fundamental property of Kahn process networks is:

```text
    KAHN'S DETERMINISM PRINCIPLE:

    For fixed process functions, topology, and external input
    streams, the denotational output streams are fixed. A fair
    execution schedule can affect when tokens appear and how
    much buffering is used, but not which output streams denote
    the network.

    Formally:
        Let N = (P, C) be a KPN with processes P and channels C.
        Let I be the external input streams.
        Then the denotation O = ⟦N⟧(I) is a function of (N, I).
```

This is a mathematical theorem about the KPN model, not a claim that every implementation with queues is deterministic. The blocking-read, nonblocking-write, single-reader/single-writer, and deterministic-process hypotheses are load-bearing. An unfair scheduler can delay a process forever, and a network can deadlock; neither fact gives the network two different denotational answers.

```text
    WHY KPNs ARE DETERMINISTIC:

    1. Each process is deterministic:
       same input history ⇒ same output history

    2. Each channel is FIFO with one writer and one reader:
       token order is preserved

    3. A process's behavior depends only on the tokens it reads.
       It cannot branch on whether an input is currently absent.

    4. Therefore: the token sequence on every channel is uniquely
       determined by the initial inputs and the process definitions

    5. Therefore: the network's output is a function of its inputs
```

### Monotonicity

Order finite and infinite streams by prefix. A KPN process denotes a **Scott-continuous** function on this stream domain. Continuity implies monotonicity, and it also preserves the least upper bounds of increasing chains. That extra continuity condition supports the least-fixed-point semantics.

```text
    MONOTONICITY:
        h1 ⊑ h2  implies  F(h1) ⊑ F(h2)

    CONTINUITY FOR AN INCREASING CHAIN h0 ⊑ h1 ⊑ ...:
        F(⊔n hn) = ⊔n F(hn)

    NETWORK WITH FIXED EXTERNAL INPUT I:
        ΦI maps candidate internal streams to new streams
        ⟦N⟧(I) = lfp(ΦI)
```

The least fixed point exists in the stream complete partial order. It is unique **as the least fixed point**; the operator may have other fixed points. The KPN semantics selects the least one, which is the limit of finite information produced from empty internal histories. Determinacy means that this selected denotation is unique. It does not imply termination, deadlock freedom, bounded queues, or a unique operational schedule.

<figure class="fp-figure">
  <p class="fp-figure-title">Kahn semantics: schedules vary, the least denotation does not</p>
  {% include diagrams/kahn-schedule-independence.svg %}
  <figcaption class="fp-figure-caption">
    The animation changes token timing while preserving FIFO histories. Motion pauses when
    reduced-motion preferences are enabled.
  </figcaption>
</figure>

### The Determinator as a KPN

The Determinator paper gives the following proof sketch:

```text
    DETERMINATOR SPACE HIERARCHY  modeled as  DETERMINISTIC KAHN NETWORK

    space              ↔  process
    Put/Get/Ret        ↔  blocking one-to-one messages
    parent-child link  ↔  fixed communication edge
    space hierarchy    ↔  network topology
```

The paper explicitly says that a formal proof is out of scope. Its argument is that `Get`/`Put`/`Ret` reduce to blocking one-to-one message channels, so a hierarchy of deterministic spaces has Kahn-network structure. This supports the schedule-independence claim under the kernel and processor assumptions. It should not be restated as a proved isomorphism between the concrete kernel and the textbook unbounded-FIFO model.

---

## 7. Parallel determinism: how concurrency becomes repeatable

### The apparent paradox

Parallelism and determinism appear contradictory. Parallel execution introduces interleaving: the order in which threads execute is not fixed. If the result depends on interleaving, the result is nondeterministic.

The resolution is that parallelism affects when, not what.

```text
    THE RESOLUTION:

    NONDETERMINISTIC PARALLELISM:
        thread A writes x = 1
        thread B writes x = 2
        final value of x depends on who writes last
        → NONDETERMINISTIC

    DETERMINISTIC PARALLELISM:
        thread A computes f(input_A) → result_A
        thread B computes g(input_B) → result_B
        parent collects (result_A, result_B) in fixed order
        → DETERMINISTIC regardless of execution speed
```

### The Determinator's solution

```text
    HOW THE DETERMINATOR ACHIEVES PARALLEL DETERMINISM:

     1. NO SHARED STATE
        Spaces cannot concurrently read or write each other's memory.
        Ordinary shared-memory data races between spaces are absent.

     2. RENDEZVOUS SYNCHRONIZATION
        Communication occurs at program-defined points in
        both spaces. Arrival order is not exposed as a choice.
        A cyclic wait can still deadlock.

     3. PARENT-ORDERED COLLECTION
        A parent calls Get on child1, child2, ... in a
        fixed order. Results are collected deterministically
        regardless of which child finishes first.

     4. SNAPSHOT AND RESTORE
        A parent can snapshot a child's state, run it,
        and restore. The child's execution is repeatable.

     PARALLELISM IS REAL:
         Children execute concurrently on multiple cores.
         Coarse-grained workloads scaled in the prototype.
         The logical result is independent of timing.
```

### The multithreaded process example

```text
    A MULTITHREADED PROCESS IN DETERMINATOR:

     ┌─────────────────────────────────────────────────┐
     │  MASTER SPACE (manages synchronization)         │
     │                                                 │
     │  Put(thread1, work1, start)                     │
     │  Put(thread2, work2, start)                     │
     │  Put(thread3, work3, start)                     │
     │                                                 │
     │  Get(thread1) → result1                         │
     │  Get(thread2) → result2                         │
     │  Get(thread3) → result3                         │
     │                                                 │
     │  final = merge(result1, result2, result3)       │
     │  (merge is a pure function)                     │
     └─────────────────────────────────────────────────┘
          │           │           │
          ▼           ▼           ▼
     ┌────────┐  ┌────────┐  ┌────────┐
     │THREAD 1│  │THREAD 2│  │THREAD 3│
     │(space) │  │(space) │  │(space) │
     │        │  │        │  │        │
     │computes│  │computes│  │computes│
     │  f(w1) │  │  g(w2) │  │  h(w3) │
     │        │  │        │  │        │
     │ Ret()  │  │ Ret()  │  │ Ret()  │
     └────────┘  └────────┘  └────────┘

     All three threads execute in parallel.
     The master collects results in fixed order.
     The final result is deterministic.
```

### Beyond the Determinator: monotone parallelism

The Determinator is one point in a design space. Other approaches to deterministic parallelism restrict the composition operation so that interleaving cannot affect the result, each at a different layer:

```text
    LVars (lattice-based variables):
        Shared state grows by lattice join.
        Threshold reads reveal only stable positive information.
        The original interface is deterministic. Adding freeze
        yields quasi-determinism unless freezing happens after
        all writes.

    Deterministic OpenMP:
        Threads use isolated working copies between structured
        synchronization points. Conflicting writes are errors.
        General reductions use a reproducible merge tree, so the
        operator need not be associative or commutative.

    Synchronous and reactor models:
        Some languages define reactions against logical tags and
        a deterministic ordering rule. Determinism then depends
        on that language's causality and scheduling semantics.
```

The common thread is mathematical. Each model restricts the observations or merge operations through which interleaving could affect a result. The restrictions differ, so their guarantees should not be treated as interchangeable. Section 8 isolates the common composition question.

---

## 8. Composition: the principle and its mathematics

### What composition means

Composition combines components according to a specified operator. Its exact type depends on the component model. A closed binary operator is one useful special case:

```text
    CLOSED BINARY COMPOSITION (one common model):

    Given:
        • a class of components C
        • a combining operation ⊕ : C × C → C

    Composition is the operation that produces a new component
    from existing components, where the result is itself a
    member of C and can participate in further composition.

    The critical property: the result is "of the same kind"
    as the parts. This is what makes composition recursive
    and scalable.
```

Closure makes repeated composition straightforward, but it is not part of every notion called composition. Typed function composition, for example, accepts `f : X → Y` and `g : Y → Z` and returns `g ∘ f : X → Z`; the input and output types need only match at the connected boundary. In this tutorial, every composition operator will state its accepted interfaces and its result type.

### The principle of compositionality

The principle of compositionality, in its most general form, states:

```text
    (C) The meaning of a complex expression is determined by
        its structure and the meanings of its constituents.

    Expanded:
        For every complex expression e in a language L,
        the meaning of e in L is determined by:
            1. the structure of e in L
            2. the meanings of the constituents of e in L
```

This principle is often associated with Frege and became central in Montague semantics. The safe reading is that the chosen meanings of the constituents, together with the syntactic formation rule, determine the chosen meaning of the whole. A whole may still have global or emergent properties. A compositional semantics must make those properties derivable through a sufficiently rich semantic operation.

### Compositionality as a homomorphism

An influential algebraic formulation, used in the Montague tradition, treats interpretation as a homomorphism. Consider:

```text
    SYNTACTIC ALGEBRA:
        E = set of expressions
        F = set of formation rules (operations on E)

    SEMANTIC ALGEBRA:
        M = set of meanings
        G = set of semantic operations (operations on M)

    MEANING ASSIGNMENT:
        m : E → M

    COMPOSITIONALITY:
        m is a homomorphism from E to M.

        For every syntactic operation Fi : E^k → E,
        there exists a semantic operation Gi : M^k → M such that:

        m(Fi(e1, ..., ek)) = Gi(m(e1), ..., m(ek))

    In words: the meaning of the composite equals the semantic
    operation applied to the meanings of the parts.
```

```text
    THE HOMOMORPHISM DIAGRAM:

         E × E ──── F ────→ E
          │                  │
          │ m × m            │ m
          ▼                  ▼
         M × M ──── G ────→ M

    The diagram commutes: going right then down (compose then
    interpret) equals going down then right (interpret then
    combine semantically).

    m(F(e1, e2)) = G(m(e1), m(e2))
```

This is one precise mathematical shape of compositionality. The diagram says that interpretation preserves the designated operations. It does **not** say that interpretation preserves all information: a homomorphism may identify distinct expressions, and it need not reach every possible semantic object.

### Composition in software

Translating to software systems:

```text
    SOFTWARE COMPOSITIONALITY:

    Components:     modules, functions, services, spaces
    Combining:      function composition, parallel composition,
                    hierarchical nesting, piping
    Meaning:        behavior, denotation, input-output relation

    A software system is compositional when:
        behavior(compose(A, B)) = semantic_combine(behavior(A), behavior(B))

    The behavior of the composite is determined by:
        1. the behaviors of A and B
        2. the mode of combination (sequential, parallel, hierarchical)

    The semantic domain must be rich enough to account for every
    behavior that the claim treats as observable.
```

### When compositionality fails

Compositionality is relative to a chosen syntax, semantic domain, and observation boundary. Shared state or concurrency does not make a compositional semantics impossible. It makes a simple summary such as a pure input-output function inadequate. The following features therefore block **naive component summaries** unless the semantic model accounts for them:

```text
    FAILURE MODES:

     1. SHARED STATE
        A and B communicate through a mutable global.
        A summary that omits the store and interleavings cannot
        derive the composite behavior.

     2. HIDDEN DEPENDENCIES
        A reads a clock. B reads an environment variable.
        The composite's behavior depends on facts outside
        the components' declared interfaces.

     3. EMERGENT INTERFERENCE
        A and B individually satisfy a property.
        Together, they violate it (e.g., deadlock).
        Local safety claims do not imply whole-system deadlock freedom.
        The semantic operator must represent blocking and cycles.

     4. CONTEXT-DEPENDENCE
        A's behavior changes with its environment. Its meaning must
        be parameterized by a context or an assume-guarantee contract.
```

The Determinator simplifies this semantic burden. Kernel spaces do not share writable memory, and nondeterministic external inputs cross explicit authority boundaries. Rendezvous still permits blocking and deadlock, and a child's behavior still depends on the messages supplied by its parent. The architecture narrows the interaction model; it does not erase interaction.

<figure class="fp-figure">
  <p class="fp-figure-title">The operator is part of the theorem</p>
  {% include diagrams/composition-proof-obligations.svg %}
  <figcaption class="fp-figure-caption">
    Deterministic parts yield a deterministic whole only when the wiring, merge, and
    external-input rules also remove undeclared choice.
  </figcaption>
</figure>

---

## 9. Composition, synthesis, and compositionality: three different questions

These three words are easy to blur. They ask different questions, and conflating them produces designs that claim compositionality while delivering only composition.

| Concept | Question |
| --- | --- |
| Composition | How do several components form one larger system? |
| Composition synthesis | Can we search for a composition that satisfies a specification? |
| Compositionality | Can correctness of the whole be derived from contracts of the parts, without flattening and reverifying everything? |

### Composition needs an operator

Suppose we have two components:

```text
    M1,  M2
```

Composition is not merely placing their source files next to each other. It means choosing an operator that gives the combined system a precise meaning:

```text
    M = M1 ⊗ M2
```

The operator ⊗ must determine:

```text
    • the combined state
    • which actions may occur
    • whether actions are sequential, interleaved, or simultaneous
    • how outputs from one component become inputs to another
    • how errors and rejections combine
    • how effects combine
    • what happens when writes conflict
    • which values are externally observable
    • how the combined system is initialized
    • which global invariants must hold
```

Different operators produce different systems from exactly the same components. Sequential composition, interleaving composition, synchronous composition, dataflow composition, parallel composition, feedback composition, and hierarchical composition are all distinct operators. The mathematical literature on wiring diagrams captures the hierarchical idea: connected black-box processes can themselves be treated as a new macro-process and wired into a larger system.

### A component model

A useful component abstraction for deterministic systems is:

```text
    M = (S, C, E, D, T, I, O)

where:
    S  state
    C  command or action domain
    E  explicit evidence or environment input
    D  decision or effect domain
    T  transition:  S × C × E → D × S
    I  local invariant
    O  observable projection
```

For two modules, an interleaving product has state `S = S1 × S2`. To keep the declared type `D × S`, its basic transitions have the following shape. Evidence inputs are shown explicitly:

```text
    if T1(s1, c1, e1) = (d1, s1') then
       T((s1, s2), Left(c1, e1)) = (d1, (s1', s2))

    if T2(s2, c2, e2) = (d2, s2') then
       T((s1, s2), Right(c2, e2)) = (d2, (s1, s2'))
```

Only one module moves in each logical step. The other stutters.

A wiring edge changes this. Suppose an action in M1 produces an effect e that sets state x in M2:

```text
    M1.action.effect --set--> M2.x
```

Let `u : D1 → (S2 → S2)` be the declared adapter that converts M1's decision into an update of M2. Then the left transition becomes:

```text
    if T1(s1, c1, e1) = (d1, s1') then
       T((s1, s2), Left(c1, e1)) = (d1, (s1', u(d1)(s2)))
```

This equation is deterministic only if `T1` and `u` are deterministic and their inputs are fixed. Treating both state updates as one atomic logical step is an additional semantic choice, not a consequence of determinism.

### Synthesis searches over compositions

Composition synthesis asks whether search can find a composition satisfying a specification. One bounded strategy takes module IRs, a system template, a finite grammar of wiring edges, and a verification function, then enumerates candidates in a canonical order and accepts the first verified candidate.

The honest scope of such a result is important. A bounded synthesizer proves minimality only if it exhausts a declared finite grammar in objective order and the verifier is sound for the stated property. It does not prove global minimality among architectures outside that space. A reproducible implementation can emit a certificate containing template and module hashes, search bounds, the edge catalog, the candidate trace, and verifier fingerprints. Deterministic search helps replay the certificate; it does not make the verifier sound.

This resembles syntax-guided synthesis, where a semantic specification defines correctness while a declared syntax restricts the candidate space. The same determinism discipline applies: canonical predicate vocabulary, fixed grammar version, fixed objective function, total candidate order, fixed solver versions and seeds, bounded iterations, and fail-closed behavior on solver unknowns.

### Compositionality derives the whole from the parts

For verification, the valuable form of compositionality asks whether a whole-system property can be derived from independently checked component contracts and a rule for combining them, without rebuilding the full product. Composition gives a combined system. Synthesis may find one. A sound compositional proof rule establishes a stated property from the parts.

Full assume-guarantee compositionality requires each module to carry a strict contract:

```text
    Contract_i {
        state
        inputs
        outputs
        assumptions
        guarantees
        invariant
        read set
        write set
        owned resources
        observables
        version
    }
```

Then the proof obligation is:

```text
    1. Init_i(s_i)  ⇒  I_i(s_i)

    2. I_i(s_i) ∧ A_i(env) ∧ T_i(s_i, action, env, s_i', out_i)
         ⇒  I_i(s_i') ∧ G_i(out_i)

    3. I_i(s_i) ∧ EnvStep_i(s_i, env, s_i')
         ⇒  I_i(s_i')
       [frame stability]

    4. Guarantees_of_peers ∧ Wiring
         ⇒  A_i
       [assumption closure]

    5. GlobalInit(s_1, ..., s_n)
         ⇒  CouplingInvariant(s_1, ..., s_n)

    6. I_1(s_1) ∧ ... ∧ I_n(s_n)
       ∧ CouplingInvariant(s_1, ..., s_n)
       ∧ CompositeStep((s_1, ..., s_n), (s_1', ..., s_n'))
         ⇒  CouplingInvariant(s_1', ..., s_n')

    7. I_1(s_1) ∧ ... ∧ I_n(s_n)
       ∧ CouplingInvariant(s_1, ..., s_n)
         ⇒  GlobalProperty(s_1, ..., s_n)
```

The conclusion is:

```text
    assumptions closed and obligations 1–7 valid
        ⇒  M1 ∥ ... ∥ Mn  ⊨  P
```

The critical pieces are assumption closure, frame stability, and coupling invariants. Every environmental assumption a module makes must be supplied by another module's guarantee, a verified adapter, the composition operator, or an explicit external-environment contract. Actions outside a module must preserve every fact on which the module's local theorem depends. A coupling invariant must hold initially and be preserved by every admitted composite step before it can support the global-property conclusion. Some invariants belong to no single module, such as "the sum of all balances equals the total supply," and require a system-level or shared-resource contract.

Assume-guarantee reasoning is a well-established route to compositional model checking. Prior work has shown that finite-state component assumptions can be learned automatically and iteratively rather than supplied entirely by hand, and abstraction-refinement methods can refine candidate assumptions using counterexamples from component checks. These automated routes matter because hand-written assumptions are the usual bottleneck in applying compositionality at scale.

### Why the distinction matters for assurance

A system can be a composition (parts combined under an operator) without being synthesizable (no search was performed) and without being compositional (the whole was verified by flattening). A system can be synthesizable without being compositional: the synthesizer verifies each candidate by rebuilding the full product and checking all invariants over it. That works for bounded models, and it eventually encounters product-state explosion.

The progression is:

```text
    composition            parts combine under a chosen operator
    composition synthesis  a search finds a composition satisfying a spec
    compositionality       the whole is proved from part contracts
```

These are different achievements rather than a strict ladder. The Determinator paper sketches a compositional argument for schedule independence: deterministic spaces interact only through deterministic kernel operations reducible to one-to-one channels. The paper does not provide a machine-checked whole-kernel proof. Section 10 isolates the preservation argument.

---

## 10. Compositionality in deterministic systems

### Deterministic composition requires three things

When two deterministic components are composed, the result is not automatically deterministic. The composition operation must preserve determinism:

```text
    DETERMINISTIC COMPOSITION REQUIRES:

    1. DETERMINISTIC COMPONENTS
       Each component's transition relation is right-unique.

    2. DETERMINISTIC COMBINING OPERATION
       Wiring, arbitration, conflict handling, and merge rules
       resolve every admitted interaction without hidden choice.

    3. CLOSED INTERFACES
       Initial state and external input histories are fixed, and
       the composition admits no undeclared external influence.

    If all three hold:
        the composite transition relation is right-unique
```

This is a preservation schema, not a complete proof for every operator. A concrete system still needs definitions precise enough to check the three premises.

### Sequential composition

The simplest total-function example feeds the output of one function into the input of the next.

```text
    SEQUENTIAL COMPOSITION:

    A ──→ B ──→ C

    f : X → Y
    g : Y → Z

    g ∘ f : X → Z
    (g ∘ f)(x) = g(f(x))

    DETERMINISM PRESERVED:
        f deterministic + g deterministic
        ⇒ g ∘ f deterministic

    Proof: for any x ∈ X,
        f(x) is unique (f is a function)
        g(f(x)) is unique (g is a function)
        therefore (g ∘ f)(x) is unique.  ∎
```

### Parallel composition

Two components execute concurrently. The question is whether the interleaving affects the result.

```text
    PARALLEL COMPOSITION (naive):

    A ──┐
        ├──→ merge ──→ output
    B ──┘

    If merge depends on which of A, B finishes first:
        NONDETERMINISTIC (interleaving matters)

    PARALLEL COMPOSITION (deterministic):

    A ──→ output_A ──┐
                     ├──→ deterministic_merge ──→ output
    B ──→ output_B ──┘

    If merge is a function of (output_A, output_B) alone:
        DETERMINISTIC (interleaving irrelevant)
```

The Determinator supports this pattern through program-defined synchronization. A parent may collect results from children in a fixed order determined by its code. The merge may be order-sensitive; it remains deterministic when the child identities and merge order are fixed and completion timing is not observable.

### Hierarchical composition

For a finite acyclic fork/join tree, the Determinator's space hierarchy admits a recursive summary:

```text
    HIERARCHICAL COMPOSITION:

     A space S with children C1, C2, ..., Cn:

         behavior(S) = f_S(
             input(S),
             behavior(C1),
             behavior(C2),
             ...,
             behavior(Cn)
         )

     where f_S is the deterministic program running in S,
     and the order of interaction with children is fixed
     by S's code.

     RECURSIVE:
         behavior(Ci) = f_Ci(
             input(Ci),
             behavior(Ci_1),
             ...,
             behavior(Ci_k)
         )

     Under fixed inputs and deterministic parent-child protocols,
     any produced result is determined by the root input.
```

A general space hierarchy may block, diverge, or repeatedly exchange messages. The simple equation above is therefore an example, not a semantics for every Determinator program. A richer stream or transition-system semantics is needed for cyclic or nonterminating interaction.

### The algebra of deterministic composition

```text
    ALGEBRAIC PROPERTIES:

     Let D be the set of deterministic components.
     Let ⊕ be a composition operation.

     ASSOCIATIVITY:
         (A ⊕ B) ⊕ C = A ⊕ (B ⊕ C)
         Grouping does not affect the result.

     IDENTITY:
         A ⊕ id = id ⊕ A = A
         There exists a do-nothing component.

     COMMUTATIVITY (sometimes desirable for parallel composition):
         A ∥ B = B ∥ A
         Order of parallel components does not affect result.
         (Requires an interface-preserving swap and a proof that
          the chosen observations are unchanged.)

     These properties make the composition algebraic:
     deterministic components form a structure that can be
     reasoned about equationally.
```

These laws are stated here as possible targets. Determinism does not imply any of them. Section 11 explains why each law is a separate proof obligation.

### The shape of compositional determinism

```text
    ┌─────────────────────────────────────────────────────────┐
     │                                                         │
     │   COMPOSITIONAL DETERMINISM                             │
     │                                                         │
     │   ┌───┐     ┌───┐     ┌───┐                           │
     │   │ A │     │ B │     │ C │    ← deterministic parts   │
     │   └─┬─┘     └─┬─┘     └─┬─┘                           │
     │     │         │         │                               │
     │     └────┬────┘         │                               │
     │          │              │                               │
     │          ▼              │                               │
     │     ┌────────┐         │                               │
     │     │ A ⊕ B  │         │    ← deterministic composition │
     │     └───┬────┘         │                               │
     │         │              │                               │
     │         └──────┬───────┘                               │
     │                │                                       │
     │                ▼                                       │
     │           ┌──────────┐                                 │
     │           │(A⊕B) ⊕ C│    ← result is deterministic    │
     │           └──────────┘      and composable             │
     │                                                         │
     │   Under the declared operator and closed interfaces,    │
     │   the whole is determined by parts and arrangement.     │
     │                                                         │
     └─────────────────────────────────────────────────────────┘
```

---

## 11. Composition laws are not free

It is tempting to assume familiar algebraic laws. In critical protocol code, every one is a proof obligation.

### Identity

An empty patch e is an identity only when:

```text
    e ∘ P = P ∘ e = P
```

for state, effects, receipts, replay identity, roots, rejection behavior, and resource accounting. A patch that changes nothing observable in the final state may still perturb a receipt or a replay nonce. Identity must be checked against every observable projection, not only the primary state.

### Associativity

Ordinary mathematical function composition is associative whenever the types match:

```text
    (h ∘ g) ∘ f = h ∘ (g ∘ f)
```

This law does not transfer automatically to a domain-specific operator such as "merge these effect plans" or "reduce these balances." Such an operator can fail associativity because of checked overflow, integer rounding, remainder allocation, error precedence, effect ordering, resource-budget exhaustion, or intermediate committed failures. If grouping has not been proved irrelevant, the reduction tree is protocol-visible and must be versioned. Two implementations that group a domain-specific reduction differently may produce different outputs from the same inputs even when every individual step is deterministic.

### Commutativity

```text
    f ∥ g = g ∥ f
```

requires noninterference or a certified commutative operation. Separate threads and separate source files prove nothing about semantic commutativity. The safe default for two tasks i and j is disjoint footprints:

```text
    Wi ∩ Wj = ∅
    Wi ∩ Rj = ∅
    Wj ∩ Ri = ∅
```

Disjoint writes alone are insufficient. Task i may read something task j changes. A more permissive merge is possible when an operation has a proved commutative algebra, but that proof must cover arithmetic overflow, rejection, effect ordering, receipt construction, remainders, dust, resource limits, and conflict semantics.

### Congruence and contextual refinement

Suppose two implementations are locally equivalent:

```text
    A ~ B
```

For observational equivalence, safe replacement requires congruence:

```text
    A ~ B  ⇒  C[A] ~ C[B]
```

for every admitted context `C`. For a one-way refinement preorder `A ⪯ B`, the corresponding condition is monotonicity of contexts:

```text
    A ⪯ B  ⇒  C[A] ⪯ C[B]
```

A replacement that preserves local output values while strengthening its environmental assumptions is not necessarily valid. It may violate an assumption a peer relied on or expose a new observable the old component hid. The observation relation, admitted contexts, and refinement direction must all be declared.

### The lesson

The algebraic laws in Section 10 are the goal. The obligations in this section are the cost. A composition that is deterministic, associative, and commutative is a composition for which these obligations have been discharged. A composition for which they have not been checked is a composition with unknown properties, however clean its diagram looks.

---

## 12. From operating-system determinism to FCIS determinism

### The structural parallel

The Determinator and FCIS place a similar boundary at different layers, but their enforcement strength can differ:

```text
    DETERMINATOR (OS layer):
        kernel provides only isolated spaces + deterministic IPC
        → under the machine assumptions, unprivileged code
          cannot introduce an undeclared scheduling choice
        → the platform enforces the property

    FCIS (application layer):
        designates pure functions + immutable values as the core
        → if the language, effect system, or review process enforces
          that restriction, core results are deterministic
        → in an ordinary impure language, FCIS alone is a discipline

    SHARED DESIGN MOVE:
        restrict the available operations
        and make hidden effects cross an explicit boundary
```

### The mapping

```text
    DETERMINATOR CONCEPT          FCIS CONCEPT
    ────────────────────          ────────────
    space                    ↔    pure transition function
    private memory           ↔    immutable input values
    Put (send data in)       ↔    shell passes inputs to core
    Get (collect results)    ↔    shell receives decision from core
    Ret (synchronize)        ↔    core returns typed result
    no shared state          ↔    no mutable state in core
    no ambient I/O           ↔    no I/O in core
    rendezvous semantics     ↔    explicit input/output contract
    space hierarchy          ↔    composition of transitions
    root space (I/O)         ↔    imperative shell (I/O)
    enforced determinism     ↔    referential transparency
                                   (when actually enforced)
```

This table is an analogy between roles, not an isomorphism. `Put`, `Get`, and `Ret` have operational blocking and memory-copy semantics that an ordinary function call does not.

### The shell as root space

In the Determinator, the distinguished root space starts with direct I/O authority for sources such as clocks and console input. It may delegate I/O privileges. A supervising space can mediate and log the nondeterministic inputs that reach an unprivileged subtree.

In a correctly enforced FCIS design, only the shell has access to nondeterministic inputs such as databases, networks, clocks, and randomness. The core receives its inputs as explicit, immutable values. A codebase that merely names a module "core" without restricting its effects has no structural guarantee.

```text
    DETERMINATOR:
        root space (I/O) → Put(data) → child space (pure computation)
                                        → Ret(result) → root space

    FCIS:
        shell (I/O) → pass values → core (pure computation)
                                   → return decision → shell (commit)

    The shell is the root space of the application.
    It mediates all contact with the nondeterministic world.
    The core is an interior space: isolated, deterministic, repeatable.
```

### Composition at both levels

The Determinator composes spaces hierarchically. FCIS composes transitions functionally. In both cases, the composition preserves determinism because the combining operation is itself deterministic:

```text
    DETERMINATOR COMPOSITION:
        parent collects children's results in fixed order
        → composite behavior is deterministic

    FCIS COMPOSITION:
        output of transition1 feeds input of transition2
        → composite transition is deterministic
        (g ∘ f is a function when f and g are functions)

    BOTH, WHEN THE STATED PREMISES HOLD:
        the result is determined by the parts, declared inputs,
        and the composition rule
```

Both systems can be described with the homomorphism pattern from Section 8 after suitable syntactic and semantic algebras are defined. The diagram does not arise from the informal mapping alone. For a terminating FCIS pipeline of pure stages, function composition supplies the semantic operator directly. For an interacting space hierarchy, stream or transition-system semantics must also account for blocking and external input.

---

## 13. Design synthesis in the context of FCIS

### What design synthesis means

Design synthesis is the process of deriving a concrete architecture from abstract requirements and principles. In systems engineering, it is the step that transforms a functional specification into a structural design:

```text
    DESIGN SYNTHESIS:

    REQUIREMENTS  (what the system must do)
         +
    PRINCIPLES    (what properties the design must have)
         +
    CONSTRAINTS   (what the design must respect)
         │
         ▼
    ARCHITECTURE  (the concrete structure that satisfies all three)
```

In the context of FCIS, design synthesis answers a specific question: given a domain problem, how does one derive the state, command, policy, evidence, transition, effect, and shell structure that constitute the system? The Determinator is a worked example of synthesis from a single hard requirement, "all unprivileged computation must be deterministic." FCIS is a worked example of synthesis from the requirement "the semantic decision must be inspectable and replayable."

### Synthesis from a determinism requirement

The determinism requirement drives synthesis through a sequence of questions.

```text
    SYNTHESIS STEP 1: IDENTIFY THE TRANSITION

    Question: what is the minimal set of facts that determines
    the decision?

    Answer becomes: State × Command × Policy × Evidence

    Design target: every fact that may affect the decision must
    be an explicit input. Facts outside the declared dependency
    set must not be accessible to the core.

    "What does the decision depend on?"
    → Everything it depends on becomes an input.
    → Everything it does not depend on is excluded.
    → The boundary is drawn at the dependency set.
```

```text
    SYNTHESIS STEP 2: ENFORCE ISOLATION

    Question: how do we prevent hidden dependencies?

    Answer: the core receives only values. It has no access
    to databases, clocks, networks, or mutable state.

    Principle: deterministic by construction. The core
    cannot read what is not passed to it.

    "Can the core access anything not in its argument list?"
    → If yes: the proposed boundary does not enforce purity.
    → If no, and evaluation semantics are deterministic:
      the core is deterministic relative to its arguments.
```

```text
    SYNTHESIS STEP 3: DEFINE THE COMPOSITION

    Question: how do transitions combine?

    Answer: sequential composition (output feeds next input),
    parallel composition (independent transitions on disjoint
    state), hierarchical composition (parent orchestrates
    children).

    Principle: compositionality. The behavior of the composite
    is determined by the behaviors of the parts and the mode
    of combination.

    "Can the chosen semantic model derive the composite from
     component meanings plus the operator?"
    → If yes: there is a candidate compositional semantics.
    → Then prove that the semantics matches the implementation.
```

```text
    SYNTHESIS STEP 4: PLACE THE BOUNDARY

    Question: where does the deterministic core end and the
    imperative shell begin?

    Answer: at the point where the system must interact with
    the nondeterministic world.

    Principle: the shell is the root space. It mediates all
    I/O. The core is an interior space. It never touches I/O.

    "Where does the system touch the world?"
    → That touch point is the shell.
    → Everything inside is core.
    → The boundary is the value contract.
```

### Synthesis as iterative refinement

Design synthesis is not a one-shot derivation. It is iterative:

```text
    SYNTHESIS LOOP:

     1.  Start with the domain question:
         "Given these facts, what is the permitted result?"

     2.  Identify the minimal input set
         (State, Command, Policy, Evidence).

     3.  Define the transition as a pure function.

     4.  Check: is the transition total? bounded? deterministic?

     5.  Define the output (Reject | Accept with effects).

     6.  Check: does the output determine the shell's actions
         completely?

     7.  Define the composition: how does this transition
         combine with others?

     8.  Check: does composition preserve determinism?

     9.  Identify what remains outside: authentication, storage,
         delivery, retry.

     10. Place those in the shell.

     11. Verify: can the shell introduce semantic decisions?
         If yes, move them to the core.

     12. Repeat until the boundary is stable.
```

Step 11 is the step most often skipped. A shell that quietly makes a semantic decision, such as choosing which oracle to trust or which retry to allow, has re-acquired domain logic. The loop is stable only when every semantic decision lives in the core and every shell action is fully determined by a core-returned plan.

### The Determinator as synthesis exemplar

The Determinator is a clear case study in design synthesis. Starting from the requirement that unprivileged computation be deterministic by default, the designers chose:

```text
    REQUIREMENT: deterministic parallel execution

    SYNTHESIS:
        → shared state must be eliminated (Principle 1)
        → namespaces must be private (Principle 2)
        → synchronization must be deterministic (Principle 3)
        → I/O must be confined to the root space
        → the API must be minimal
        → the user-level runtime emulates familiar abstractions
          without defeating the kernel's guarantee

    RESULT: an architecture where determinism is a theorem,
    not a hope.
```

These choices form one coherent solution, not the only possible one. Deterministic languages, type-and-effect systems, deterministic schedulers, and other runtime models occupy different points in the design space. The hard requirement prunes that space, while compatibility, performance, proof burden, and trusted-computing-base size decide among the survivors.

### The effect-boundary extensibility tradeoff

An FCIS design faces a familiar extensibility tradeoff at the effect boundary. It resembles the expression problem, but the correspondence is not exact:

```text
    EXPRESSION PROBLEM AT THE EFFECT BOUNDARY:

    Adding a new effect type:
        → requires updating all handlers (shell interpreters)
        → the core's effect algebra changes

    Adding a new handler:
        → straightforward when the effect algebra is fixed
        → a shell-only change

    SYNTHESIS DECISION:
        Fix the effect algebra early (closed sum).
        Make handlers extensible (open interpretation).
        This matches the Determinator's fixed API:
        the communication primitives are fixed.
        What spaces compute is open.
```

The Determinator fixes its kernel API and leaves user-space computation open. An FCIS design may fix a closed effect sum and permit multiple interpreters, but adding a new effect then requires changing that sum and every exhaustive interpreter. This is a design choice rather than a theorem; extensible effects or versioned capability interfaces offer other tradeoffs.

### The denotational approach to synthesis

The strongest form of design synthesis begins with the denotation, as the previous tutorial argued:

```text
    DENOTATIONAL SYNTHESIS:

    1. Write down what the system MEANS (its denotation).
       "A swap transition denotes the unique state and effect
        plan entailed by its inputs under the stated policy."

    2. The denotation is a mathematical object, independent
       of implementation.

    3. Synthesize an implementation that computes the denotation.

    4. Verify: implementation(input) = denotation(input)
       for all valid inputs.
```

This separates what from how. The denotation is the specification, and the implementation is a mechanism intended to compute it. In FCIS, the core is still an implementation; it is not automatically identical to the denotation. An equivalence proof, exhaustive check on a finite domain, or other conformance argument is needed to connect them. At the OS level, the kernel API defines an execution model and the user runtime builds familiar abstractions on top of it.

### Synthesis, composition, and the boundary together

The three ideas of this tutorial combine in a single design discipline. Synthesis derives the parts from the requirements. Composition combines the parts under a chosen operator. The value boundary keeps the parts inspectable and the combination honest. Determinism by construction is what makes the combination provably preserve the property the synthesis was after.

```text
    requirements
        │  (synthesis)
        ▼
    deterministic parts, each a function on values
        │  (composition under a deterministic operator)
        ▼
    deterministic whole, still a function on values
        │  (value boundary makes it inspectable)
        ▼
    replayable, auditable, comparable, certifiable system
```

---

## 14. Shape diagrams: the geometry of deterministic composition

### The deterministic arrow

```text
    THE FUNDAMENTAL SHAPE:

          input
            │
            │  (complete, explicit, bounded)
            ▼
     ┌─────────────┐
     │             │
     │  DETERMIN-  │
     │  ISTIC      │
     │  FUNCTION   │
     │             │
     └──────┬──────┘
            │
            │  (unique, entailed)
            ▼
          output

     One fixed input. At most one output.
     Add totality to guarantee that an output exists.
```

### The composition shapes

```text
    SEQUENTIAL COMPOSITION:

     x ──→ [f] ──→ y ──→ [g] ──→ z

     The intermediate value y is determined by x.
     The final value z is determined by y.
     Therefore z is determined by x.
     The chain is deterministic.


    PARALLEL COMPOSITION:

          ┌──→ [f] ──→ a ──┐
     x ──┤                  ├──→ [merge] ──→ z
          └──→ [g] ──→ b ──┘

     a is determined by x (through f).
     b is determined by x (through g).
     z is determined by (a, b) (through merge).
     Therefore z is determined by x.
     The fan-out/fan-in is deterministic.


    HIERARCHICAL COMPOSITION:

               [parent]
              /   |   \
             /    |    \
         [c1]  [c2]  [c3]
          |      |      |
          ▼      ▼      ▼
         r1     r2     r3
              \   |   /
               \  |  /
            [parent collects]
                 |
                 ▼
               result

     Each child's result is determined by its input.
     The parent's collection order is fixed by its code.
     The final result is determined by the root input.
     The tree is deterministic.
```

### The FCIS shape as deterministic composition

```text
    FCIS AS DETERMINISTIC COMPOSITION:

     ┌─────────────────────────────────────────────────────────┐
     │  SHELL (root space)                                     │
     │                                                         │
     │  bytes ──→ [parse] ──→ values ──→ ┌─────────────┐      │
     │                                   │             │      │
     │                                   │    CORE     │      │
     │                                   │  (interior  │      │
     │                                   │   space)    │      │
     │                                   │             │      │
     │                                   │  δ(S,C,P,E) │      │
     │                                   │     = D     │      │
     │                                   │             │      │
     │  commit ←── [interpret] ←── plan ←└─────────────┘      │
     │    │                                                    │
     │    ▼                                                    │
     │  effects delivered idempotently                         │
     │                                                         │
     └─────────────────────────────────────────────────────────┘

     The shell is the root space: it touches the world.
     The core is an interior space: it touches only values.
     The boundary is the value contract: typed, immutable, canonical.
     The composition is deterministic: same values in, same decision out.
```

### The compositionality square

```text
    THE COMPOSITIONALITY SQUARE (applied to FCIS):

    Transition1 × Transition2 ──── compose ────→ Composite
           │                                        │
           │ semantics × semantics                  │ semantics
           ▼                                        ▼
    Meaning1 × Meaning2 ──── combine ────→ CompositeMeaning

    The square commutes:
        meaning(compose(T1, T2)) = combine(meaning(T1), meaning(T2))

    The composite is understood through the parts.
    Its denotation is derived without treating the whole as
    an unanalyzed black box. The meaning is determined by the
    parts, their arrangement, and the declared semantic operator.
```

### The assurance shape

```text
    ASSURANCE THROUGH DETERMINISTIC COMPOSITION:

     ┌─────────────────────────────────────────────────────────┐
     │                                                         │
     │  PROVE EACH PART:                                       │
     │     T1 is deterministic, total, bounded                 │
     │     T2 is deterministic, total, bounded                 │
     │     T3 is deterministic, total, bounded                 │
     │                                                         │
     │  PROVE THE COMPOSITION:                                 │
     │     compose(T1, T2, T3) preserves determinism           │
     │     compose also preserves totality and the stated      │
     │     resource bounds                                     │
     │                                                         │
     │  CONCLUDE:                                              │
     │     The whole system is deterministic, total, bounded   │
     │     under the stated component and operator assumptions │
     │                                                         │
     │  This is the payoff of compositionality:                │
     │  assurance of parts + assurance of composition          │
     │  = assurance of the whole                               │
     │                                                         │
     └─────────────────────────────────────────────────────────┘
```

The assurance shape is the practical payoff. A sound proof rule can establish a whole-system theorem from component theorems and operator obligations. Whole-system testing remains useful for validating assumptions, integration, and the implementation-to-model link. Determinism composes under operators that preserve it. Totality, resource bounds, safety, and liveness each need their own preservation premises; none follows from determinism alone.

---

## 15. Costs, limits, and honest non-claims

### What determinism by construction costs

```text
    PERFORMANCE:
         Rendezvous semantics can serialize communication.
         A parent waiting for a child cannot make progress until
         that rendezvous completes, although other spaces may run.
         This can create a bottleneck for I/O-bound applications.
         The OSDI results show
         coarse-grained parallel benchmarks scaling comparably
         to nondeterministic systems, but fine-grained
         communication-heavy workloads pay overhead.

     EXPRESSIVENESS:
         Not all useful computations map naturally to the
         shared-nothing model. Some algorithms benefit from
         shared mutable state (graph traversal, in-place sorting). The
         Determinator emulates these at user level, with
         overhead.

     COMPLEXITY:
         The user-level runtime that emulates Unix processes,
         filesystems, and shared memory is itself complex.
         Determinism is guaranteed, but the emulation layer
         can be buggy.

     CONCEPTUAL OVERHEAD:
         Thinking in terms of spaces, rendezvous, and
         private namespaces is unfamiliar. The learning
         curve is real.
```

### What the construction does not guarantee

```text
    NON-CLAIMS:

     ✗ The specification is complete.
       A deterministic system can be deterministically wrong.

     ✗ The inputs capture all relevant facts.
       If the model omits a relevant input, the output is
       deterministic relative to the model and potentially
       wrong relative to the world.

     ✗ The hardware behaves as modeled.
       Bit flips, cosmic rays, and hardware bugs are outside
       the architectural guarantee.

     ✗ The user-level runtime is correct.
       The kernel guarantees determinism. The runtime may
       produce wrong results deterministically.

     ✗ Arbitrary composition preserves determinism or any other
       desired property. Preservation holds only for operators
       whose obligations have been discharged. Security, liveness,
       totality, boundedness, and performance are separate claims.

     ✗ The system is useful.
       A deterministic system that computes the wrong answer
       is still deterministic.
```

### When the pattern fights the domain

```text
    DIFFICULT CASES:

     1. REAL-TIME SYSTEMS
        Determinism of output does not imply determinism of
        timing. A hard real-time system needs bounded response
        time. The Determinator targets repeatable computation
        results, not hard real-time deadlines.

     2. GENUINELY NONDETERMINISTIC DOMAINS
        Some domains require randomness (cryptographic key
        generation, Monte Carlo simulation). The Determinator
        handles this by recording randomness as an explicit
        input. The computation is deterministic given the
        recorded random values. The random values themselves
        come from outside the deterministic boundary, from the
        root space.

     3. LARGE SHARED STATE
        A database with millions of records cannot be copied
        into a space on every transition. The Determinator's
        snapshot mechanism helps, but the overhead is real.
        FCIS addresses this with persistent data structures
        and bounded projections.

     4. EVOLVING SPECIFICATIONS
        Determinism is relative to a fixed transition function.
        When the specification changes, the transition changes,
        and old replays produce old results. Version management
        of the transition itself becomes necessary.
```

### The honesty principle

```text
    THE HONEST CLAIM:

    "This system is deterministic by construction relative to
     its declared initial state, input model, program version,
     and execution semantics. Every admitted execution has at
     most one result. If totality has also been proved, every
     declared input has exactly one modeled result. The claim
     follows from the stated component and composition rules."

    AND THE HONEST NON-CLAIM:

    "This guarantee does not establish that the input model
     is complete, that the specification is correct, that
     the hardware is reliable, or that the system is useful.
     Those are separate assurance obligations."
```

The claim and the non-claim belong together. A determinism guarantee without the non-claims reads as a completeness claim it cannot support. The previous tutorial stated the same discipline for FCIS: purity excludes hidden inputs, it does not make execution environments identical, and a proof establishes only its declared statement.

---

## 16. Connections

### To the previous tutorial (FCIS)

This tutorial extends the FCIS tutorial's argument. FCIS establishes that immutable values and pure functions create a boundary between semantic computation and imperative effect. This tutorial asks what happens when that boundary is enforced by architecture rather than by convention. The Determinator is the answer at the OS level. FCIS is the answer at the application level. The mathematical structure is shared: isolation, explicit communication, deterministic composition.

### To category theory

The compositionality principle is a homomorphism between a syntactic algebra and a semantic algebra. In category-theoretic terms:

```text
    CATEGORICAL VIEW:

    Let C be the category of deterministic components.
        Objects: types (input/output interfaces)
        Morphisms: deterministic functions

    Composition of morphisms: g ∘ f
        (sequential composition of functions)

    The category is well-defined because:
        • composition of deterministic functions is deterministic
        • identity morphisms exist (the identity function on each type)
        • composition is associative

    Functors between categories model interpretation:
        F : Syntax → Semantics
        F preserves composition: F(g ∘ f) = F(g) ∘ F(f)

    This is the compositionality principle, stated categorically.
```

When syntax and semantics have been organized as suitable categories, the Section 8 preservation diagram says that an interpretation functor preserves composition. This is a categorical formulation of compositionality. An informal semantics is not automatically such a functor until the categories and preservation laws are defined.

### To separation logic

The Determinator's shared-nothing spaces are an extreme form of separation. Each space has private virtual memory, although data can be copied or merged at explicit synchronization points. The standard sequential separation-logic frame rule has the shape:

```text
    {P} c {Q}
    -------------------------  if c does not modify variables free in R
    {P * R} c {Q * R}
```

Private spaces make noninterference between synchronization points easier to justify, but the analogy is not an instance of the rule by itself. Copy, merge, and conflict behavior still require explicit specifications.

### To capability-based security

The Determinator's child namespaces and delegated I/O privileges have a capability-like structure. A space directly interacts with its parent and children and cannot name arbitrary siblings through a global process namespace. Calling the whole API a capability system would require a fuller account of authority transfer and confinement, so this tutorial uses the narrower comparison.

### To the end-to-end argument

The end-to-end argument warns that lower layers can provide only guarantees they have enough information to implement completely. Determinator's kernel can exclude internal scheduling choice because it mediates the relevant resources. It cannot establish application correctness, input adequacy, or useful results. Those remain end-to-end obligations.

### To reactive and dataflow systems

Kahn process networks strongly influenced dataflow models. Some reactive languages also obtain determinism from logical time and explicit causality rules, but not every reactive system is a KPN. Likewise, an FCIS value-flow diagram is not automatically a KPN: Kahn's continuity, channel, and blocking-read hypotheses must be established separately.

---

## Conclusion

Determinism by construction is the thesis that a system's enforced operations can exclude undeclared choice inside a stated model. The Determinator demonstrates this at the operating-system level with shared-nothing spaces, deterministic communication primitives, and program-defined synchronization. Its paper sketches a reduction to deterministic Kahn networks; it explicitly leaves a formal proof out of scope. The kernel enforces repeatability for unprivileged computation under its processor, kernel, and input assumptions.

Composition combines parts under a specified operator. Deterministic parts form a deterministic whole only when that operator preserves determinism and the external inputs are fixed. A sound compositional proof rule can derive a whole-system property from component contracts and operator obligations. The distinction among composition, composition synthesis, and compositional verification keeps the assurance claim honest: a combined system, a found system, and a property proved from contracts are three different achievements.

FCIS is an application-level analogue of the same boundary move. When purity is enforced, the functional core is deterministic relative to immutable input values, and the imperative shell mediates external effects. The analogy is useful for design, while the operational semantics of function calls and Determinator spaces remain different.

Design synthesis in this context is the disciplined derivation of architecture from requirements: identify the transition, enforce isolation, define the composition, place the boundary. The Determinator's three principles, isolate, private namespaces, deterministic synchronization, become the FCIS designer's three questions: what are the inputs, what is excluded, how do parts compose.

The practical benefit is a narrower review problem. When interfaces are complete and enforced, a reviewer can analyze a component from its declared state, inputs, semantics, and contracts. The remaining work is explicit: validate those declarations, prove the composition rule, and check that the implementation matches the model.

---

## Further reading

- Amittai Aviram, Shu-Chun Weng, Sen Hu, and Bryan Ford. [Efficient System-Enforced Deterministic Parallelism](https://www.usenix.org/conference/osdi10/efficient-system-enforced-deterministic-parallelism). OSDI '10. Jay Lepreau Best Paper Award.
- Bryan Ford. [Determinator: An Operating System for Deterministic Parallel Computing](https://dedis.cs.yale.edu/2010/det/). Yale DEDIS project page.
- [Determinator source code on GitHub](https://github.com/dedis/Determinator). Public archive of the research prototype.
- Weiyi Wu and Bryan Ford. [Deterministically Deterring Timing Attacks in Deterland](https://dedis.cs.yale.edu/cloud/papers/trios15-deterland.pdf). TRIOS '15.
- Amittai Aviram and Bryan Ford. [Deterministic OpenMP for Race-Free Parallelism](https://dedis.cs.yale.edu/2010/det/papers/hotpar11.pdf). HotPar '11.
- Yu Zhang and Bryan Ford. [A Virtual Memory Foundation for Scalable Deterministic Parallelism](https://dedis.cs.yale.edu/2010/det/papers/apsys11-vm.pdf). APSys '11.
- Gilles Kahn. [The Semantics of a Simple Language for Parallel Programming](https://www.irisa.fr/lande/ernest/kahn-1974.pdf). IFIP Congress, 1974. The original Kahn process network paper.
- Thomas M. Parks. [Bounded Scheduling of Process Networks](https://ptolemy.berkeley.edu/papers/95/parksThesis/thesis.pdf). PhD thesis, 1995. A careful treatment of Kahn determinacy, least-fixed-point semantics, and bounded scheduling.
- Richard Montague. Universal Grammar. Theoria, 1970. A foundation of Montague semantics.
- [Montague Semantics](https://plato.stanford.edu/entries/montague-semantics/). Stanford Encyclopedia of Philosophy. Historical context for compositionality and the later algebra-homomorphism formulation.
- Wilfrid Hodges. [Formal Features of Compositionality](https://www.semanticsarchive.net/Archive/WY1OTRkN/compositionality.pdf). Journal of Logic, Language, and Information, 2001.
- Lindsey Kuper et al. [Freeze After Writing: Quasi-Deterministic Parallel Programming with LVars](https://scholarworks.iu.edu/dspace/items/060499ca-6a17-4626-b837-7738785832a3). 2014. Lattice-based deterministic shared state.
- Jamieson M. Cobleigh, Dimitra Giannakopoulou, and Corina S. Păsăreanu. [Learning Assumptions for Compositional Verification](https://citeseerx.ist.psu.edu/document?doi=7a5cb466566dde5ad46ae6350ac92ba66db89cc8&repid=rep1&type=pdf). TACAS, 2003.
- John C. Reynolds. [An Introduction to Separation Logic](https://sos-vo.org/system/files/sos_files/An_Introduction_to_Separation_Logic.pdf). Notes including the frame rule and its side condition.
- Gary Bernhardt. [Boundaries](https://www.destroyallsoftware.com/talks/boundaries). The practical insight behind FCIS.
- Previous tutorial: [Functional Core, Imperative Shell: How Immutable Values Become Boundaries](../functional-core-imperative-shell-values-as-boundaries/).
