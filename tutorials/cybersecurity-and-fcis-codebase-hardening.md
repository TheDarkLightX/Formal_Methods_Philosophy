---
title: "Cybersecurity and FCIS-Based Codebase Hardening"
layout: docs
kicker: Tutorial 69
description: "A precise guide to the security benefits and limits of functional-core/imperative-shell architecture, with typed boundaries, immutable data, atomic commit, secure randomness, and a worked Python example."
---

**FCIS** means **functional core, imperative shell**. The pattern separates
side-effect-free domain decisions from I/O, state acquisition, persistence,
concurrency, and other interactions with the outside world.

FCIS can make security-critical behavior easier to inspect, replay, test, and
verify. Its protection is conditional. The core must actually be pure, its
inputs and outputs must be transitively immutable or defensively owned, and the
shell must commit accepted decisions safely.

FCIS is an architectural hardening technique. Memory safety, authorization,
cryptography, dependency security, resource limits, atomic storage, and
side-channel resistance remain separate obligations.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Assumptions and scope</p>
  <ul>
    <li><strong>Architecture assumption:</strong> claims about the core apply only when hidden I/O and shared mutable state are excluded by review, tooling, or the language.</li>
    <li><strong>Threat-model assumption:</strong> every security claim is relative to named assets, attacker capabilities, trust boundaries, and failure conditions.</li>
    <li><strong>Python scope:</strong> the examples illustrate application-level ownership and decision structure. They do not establish native-memory safety for the interpreter, extensions, foreign-function interfaces, or operating system.</li>
    <li><strong>Determinism scope:</strong> “same input, same output” assumes fixed language semantics and complete explicit inputs. Cross-language or byte-for-byte agreement requires a separate canonical encoding and arithmetic specification.</li>
  </ul>
</div>

## Contents

1. [Exploit fundamentals](#1-exploit-fundamentals)
2. [The FCIS security boundary](#2-the-fcis-security-boundary)
3. [What FCIS can reduce](#3-what-fcis-can-reduce)
4. [What FCIS does not prevent](#4-what-fcis-does-not-prevent)
5. [A worked Python example](#5-a-worked-python-example)
6. [Determinism without security myths](#6-determinism-without-security-myths)
7. [Caching, logging, and retries](#7-caching-logging-and-retries)
8. [Testing and formal verification](#8-testing-and-formal-verification)
9. [Hardening checklist](#9-hardening-checklist)
10. [Summary](#10-summary)

## 1. Exploit fundamentals

A software vulnerability is a weakness that can violate a security property.
An exploit is an input, program, or sequence of actions that takes advantage of
such a weakness to cause an unintended effect.

Mitigation bypass and reliability often matter to a real attack, but they are
not defining stages of every exploit. A business-logic flaw may require no
ASLR, DEP, control-flow, or stack-canary bypass. A denial-of-service exploit may
have value to an attacker even when it succeeds only under particular load or
timing conditions.

A useful assessment asks four separate questions:

1. **Reachability:** Can an attacker reach the vulnerable operation?
2. **Preconditions:** What identity, state, timing, or environmental facts are
   required?
3. **Impact:** Which confidentiality, integrity, availability, or authorization
   property can fail?
4. **Reliability and cost:** How consistently and cheaply can the effect be
   produced?

### Common vulnerability classes

| Class | Precise description | Example consequence | Does FCIS prevent it? |
|---|---|---|---|
| Out-of-bounds write | Data is written before or after an intended buffer | Memory corruption, crash, sometimes code execution | No. Use memory-safe languages, bounds checks, compiler defenses, sanitizers, and fuzzing |
| Use-after-free | Code accesses memory after its lifetime ended | Corruption, crash, sometimes code execution | No. Application-level immutability does not establish memory lifetime safety |
| Race condition | Concurrent operations access shared state without the required synchronization | Duplicate action, stale decision, privilege or integrity failure | FCIS can remove shared mutation from the core; shell races still require synchronization and atomic commit |
| TOCTOU | A resource changes between a check and the action that relied on it | File substitution, stale authorization, double spend | No. Bind the decision to a versioned snapshot and commit with compare-and-swap or a transaction |
| Logic or policy flaw | The implemented rule admits behavior that the intended policy forbids | Authorization bypass, incorrect price, invalid state transition | FCIS makes the rule easier to isolate and test; an incorrect pure rule remains incorrect |
| Deserialization of untrusted data | Untrusted input causes unsafe object reconstruction or attacker-selected behavior | Code execution, object injection, denial of service | No. Use safe data formats, strict schemas, type allowlists, and resource limits |
| Injection | Data is interpreted as code or command syntax at a sink | SQL injection, command execution, cross-site scripting | No. Use parameterized or structured sink APIs and context-specific output encoding |
| Integer error | Overflow, wraparound, narrowing, signedness, or rounding violates an arithmetic assumption | Incorrect bounds, allocation error, financial loss | FCIS exposes arithmetic for review; explicit units, ranges, checked operations, and rounding rules are still required |
| Resource exhaustion | Attacker-controlled work, memory, recursion, fanout, or storage exceeds a budget | Denial of service | No. Every layer needs byte, depth, count, time, and work limits |

The corresponding CWE entries include
[out-of-bounds write (CWE-787)](https://cwe.mitre.org/data/definitions/787.html),
[use-after-free (CWE-416)](https://cwe.mitre.org/data/definitions/416.html),
[race condition (CWE-362)](https://cwe.mitre.org/data/definitions/362.html),
[TOCTOU (CWE-367)](https://cwe.mitre.org/data/definitions/367.html),
[untrusted deserialization (CWE-502)](https://cwe.mitre.org/data/definitions/502.html),
and [integer overflow or wraparound (CWE-190)](https://cwe.mitre.org/data/definitions/190.html).

## 2. The FCIS security boundary

The basic FCIS shape is:

```text
untrusted bytes and external facts
              │
              ▼
shell: bound, decode, authenticate, and capture one snapshot
              │
              ▼
typed command + immutable state + policy + explicit evidence
              │
              ▼
core: deterministic domain decision
              │
              ├── Reject(reason)
              │
              └── Accept(next state, exact effect plan, audit facts)
                                      │
                                      ▼
shell: atomically commit, then deliver external effects idempotently
```

The core contains domain authority: admission rules, authorization decisions,
amounts, fees, ordering, replay policy, and the exact description of allowed
effects. The shell acquires external facts and executes effects.

This division does not make the core/shell interface the system's only security
perimeter. A real service has several trust boundaries:

```text
network → byte parser → authentication → typed command → domain transition
        → database transaction → outbox worker → external service
```

Each boundary needs the checks appropriate to its role.

### Validation belongs at more than one point

“Validate at the boundary” is useful only after the relevant boundary and
validation kind are named.

| Stage | Appropriate checks |
|---|---|
| Before decoding | Request byte limit, content type, framing, nesting and collection budgets |
| Typed parsing | Required and unknown fields, exact types, ranges, canonical representation |
| Authentication | Credential verification, freshness, audience, issuer, transport binding |
| Functional core | Domain invariants, authorization, replay rules, policy version, arithmetic |
| Commit shell | Expected state version, uniqueness, atomicity, idempotency, crash recovery |
| Output sink | Parameterized query, structured command API, context-specific encoding |

Generic “sanitization” is not a universal injection defense. OWASP distinguishes
syntactic and semantic validation, and recommends parameterized queries for SQL
injection prevention. Data that passed input validation can still be dangerous
when concatenated into a command or query.

## 3. What FCIS can reduce

The safest wording is that FCIS **reduces particular opportunities for bugs**.
The pattern supplies no blanket exploit-prevention guarantee.

### Shared-state races inside the core

A pure function does not mutate shared application state. Two evaluations over
the same immutable values cannot race by modifying those values.

This removes a common source of data races from the functional core. It does
not remove concurrency from the system. The shell still reads changing state,
competes with other requests, commits results, and delivers effects.

For a state-changing operation, the relevant contract is:

```text
core:
    step(pre_state, command, policy, evidence)
      = Reject(reason)
      or Accept(post_state, effect_plan)

shell:
    commit Accept(...) only if the stored state still has pre_state.version
```

The version check closes the gap between decision and commit. Without it, two
workers can read the same balance, accept independently, and overwrite one
another even though the transition function is pure.

### Alias-driven mutation

Transitive immutability or defensive ownership prevents a caller from changing
an accepted command, state snapshot, effect plan, or receipt through a retained
mutable reference.

Python's `@dataclass(frozen=True)` blocks ordinary attribute assignment. It is
shallow. A frozen dataclass that contains a `dict` or `list` still exposes
mutable children:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ShallowFreeze:
    labels: dict[str, str]

source = {"role": "reader"}
value = ShallowFreeze(source)
source["role"] = "admin"

assert value.labels["role"] == "admin"
```

For authoritative values, prefer immutable primitives, enums, tuples,
frozensets, and other transitively immutable values. Copy and freeze
caller-owned collections at construction boundaries.

This is application-level ownership. It does not prevent use-after-free in a
native runtime, extension, unsafe block, or foreign library.

### Replayable decisions

When all decision inputs are explicit and outputs are values, an incident can
be replayed:

```text
recorded state + command + policy + evidence
                    │
                    ▼
               same core
                    │
                    ▼
compare typed decision and exact effect plan
```

Replay improves diagnosis and differential testing. It establishes that the
recorded model reproduces the result. It does not establish that the policy was
correct, the evidence was authentic, or the shell committed exactly once.

### Fail-closed rejection

A core can return a typed rejection without producing a candidate post-state or
effect plan. This makes a useful law explicit:

```text
Reject → pre-state unchanged and effects empty
```

Some protocols intentionally consume a fee, nonce, or attempt counter on
failure. Such a result is a committed failure, not a no-op rejection. It needs
its own result type and atomic commit semantics.

### Claim and non-claim table

| Mechanism | Narrow guarantee when enforced | Important non-guarantee |
|---|---|---|
| Pure transition | Decision has no hidden application-state reads or writes | The rule may still be wrong or too expensive |
| Transitively immutable values | Retained aliases cannot change authoritative values | Native-memory lifetime safety |
| Typed command | Represented invalid combinations can be rejected once | The type may omit a real legal or illegal case |
| Exact effect plan | Shell need not reconstruct domain decisions | Atomic commit and duplicate-safe delivery |
| Versioned commit | Stale decisions can be rejected | Availability under contention |
| Deterministic replay | Recorded inputs reproduce the modeled decision | Authenticity, policy correctness, or side-channel safety |

## 4. What FCIS does not prevent

### Memory corruption

FCIS does not change the memory-safety properties of C, C++, unsafe Rust, native
extensions, device drivers, or runtimes. Memory-safe languages, restricted
unsafe regions, sanitizers, compiler hardening, fuzzing, and careful ownership
remain relevant.

### Injection

A pure function can construct a dangerous SQL string perfectly
deterministically. The shell must use parameterized queries or another API that
keeps code separate from data. Output encoding remains specific to the sink.

### Authentication and authorization errors

The shell usually authenticates transport credentials and converts them into a
typed principal. The core should decide domain authorization from that
principal, the requested command, and explicit policy. Authentication bugs,
stale role snapshots, confused-deputy behavior, and incomplete policy can still
cause compromise.

### Insecure deserialization

`pickle` can execute attacker-influenced behavior during deserialization and is
unsuitable for untrusted data. JSON avoids arbitrary object reconstruction by
default, but JSON parsing still needs byte, depth, collection, type, and range
limits. YAML requires a safe loader and a constrained schema.

### Secrets and cryptography

Predictability is dangerous for session tokens, password-reset links, CSRF
tokens, cryptographic keys, salts, and many nonces. Security-sensitive random
values should come from a cryptographically secure source such as Python's
`secrets` module. A fixed `random.seed(...)` is useful for repeatable
simulations, not for security secrets.

### Side channels

Pure or deterministic output does not imply constant-time execution. Branches,
memory access, caches, allocation, garbage collection, error text, and response
size can leak information. Cryptographic operations should use reviewed
constant-time libraries and a side-channel-specific threat model.

### Supply chain and deployment

FCIS does not establish dependency provenance, patch status, build integrity,
secret management, operating-system hardening, sandboxing, network policy, or
monitoring. These controls surround the architecture.

## 5. A worked Python example

The example is intentionally small. It models an order decision in integer
cents and basis points. One basis point is one ten-thousandth. This bounded model
restricts identifiers and SKU values to printable ASCII.

### Before: mixed authority and mutable process state

```python
class OrderProcessor:
    def __init__(self) -> None:
        self._orders: list[dict[str, object]] = []
        self._discount_by_user: dict[str, float] = {}

    def process_order(
        self,
        user: str,
        items: list[dict[str, object]],
        discount: float,
    ) -> dict[str, object]:
        if user not in self._discount_by_user:
            self._discount_by_user[user] = discount

        effective_discount = self._discount_by_user[user]
        subtotal = sum(
            item["price"] * item["quantity"]  # type: ignore[operator]
            for item in items
        )
        total = subtotal * (1 - effective_discount)

        order = {"user": user, "total": total, "status": "pending"}
        self._orders.append(order)
        return order
```

The risks are concrete:

- the first request for a user controls a cache entry that later requests reuse;
- the cache key omits cart, policy version, and discount provenance;
- validation, pricing, persistence, and process-local caching are mixed;
- caller-owned lists and dictionaries remain mutable;
- binary floating-point is used for money without a rounding specification;
- shared use requires synchronization, and process-local state diverges across
  workers;
- no idempotency key or atomic persistence rule is present.

### After: typed parsing and a pure decision

The complete decision example below uses only immutable children. It returns
either a typed rejection or an exact order plan.

```python
from dataclasses import dataclass
from enum import Enum

BASIS_POINTS = 10_000
MAX_ITEMS = 100
MAX_UNIT_PRICE_CENTS = 100_000_000
MAX_QUANTITY = 10_000


class ParseCode(str, Enum):
    SHAPE = "shape"
    FIELD = "field"
    LIMIT = "limit"


@dataclass(frozen=True, slots=True)
class ParseReject:
    code: ParseCode
    field: str


@dataclass(frozen=True, slots=True)
class OrderItem:
    sku: str
    unit_price_cents: int
    quantity: int


@dataclass(frozen=True, slots=True)
class CreateOrder:
    request_id: str
    account_id: str
    items: tuple[OrderItem, ...]
    requested_discount_bps: int


def _valid_identifier(value: object) -> bool:
    return (
        type(value) is str
        and 1 <= len(value) <= 64
        and value.isascii()
        and all(char.isalnum() or char in "-_." for char in value)
    )


def parse_order(raw: object) -> CreateOrder | ParseReject:
    if type(raw) is not dict:
        return ParseReject(ParseCode.SHAPE, "$")

    expected = {"request_id", "account_id", "items", "discount_bps"}
    if set(raw) != expected:
        return ParseReject(ParseCode.FIELD, "$")

    request_id = raw["request_id"]
    account_id = raw["account_id"]
    raw_items = raw["items"]
    discount_bps = raw["discount_bps"]

    if not _valid_identifier(request_id):
        return ParseReject(ParseCode.FIELD, "request_id")
    if not _valid_identifier(account_id):
        return ParseReject(ParseCode.FIELD, "account_id")
    if type(discount_bps) is not int or not 0 <= discount_bps <= BASIS_POINTS:
        return ParseReject(ParseCode.FIELD, "discount_bps")
    if type(raw_items) is not list or not 1 <= len(raw_items) <= MAX_ITEMS:
        return ParseReject(ParseCode.LIMIT, "items")

    items: list[OrderItem] = []
    for index, raw_item in enumerate(raw_items):
        field = f"items[{index}]"
        if type(raw_item) is not dict:
            return ParseReject(ParseCode.SHAPE, field)
        if set(raw_item) != {"sku", "unit_price_cents", "quantity"}:
            return ParseReject(ParseCode.FIELD, field)

        sku = raw_item["sku"]
        price = raw_item["unit_price_cents"]
        quantity = raw_item["quantity"]

        if (
            type(sku) is not str
            or sku != sku.strip()
            or not sku.isascii()
            or not sku.isprintable()
            or not 1 <= len(sku) <= 64
        ):
            return ParseReject(ParseCode.FIELD, f"{field}.sku")
        if type(price) is not int or not 0 <= price <= MAX_UNIT_PRICE_CENTS:
            return ParseReject(ParseCode.FIELD, f"{field}.unit_price_cents")
        if type(quantity) is not int or not 1 <= quantity <= MAX_QUANTITY:
            return ParseReject(ParseCode.FIELD, f"{field}.quantity")

        items.append(OrderItem(sku, price, quantity))

    return CreateOrder(
        request_id=request_id,
        account_id=account_id,
        items=tuple(items),
        requested_discount_bps=discount_bps,
    )


@dataclass(frozen=True, slots=True)
class Principal:
    account_id: str
    capabilities: frozenset[str]


@dataclass(frozen=True, slots=True)
class PricingPolicy:
    version: int
    maximum_discount_bps: int
    maximum_order_total_cents: int


class RejectCode(str, Enum):
    UNAUTHORIZED = "unauthorized"
    DISCOUNT_NOT_ALLOWED = "discount_not_allowed"
    TOTAL_TOO_LARGE = "total_too_large"


@dataclass(frozen=True, slots=True)
class DecisionReject:
    code: RejectCode


@dataclass(frozen=True, slots=True)
class AuditEvent:
    kind: str
    request_id: str
    account_id: str
    policy_version: int
    total_cents: int


@dataclass(frozen=True, slots=True)
class OrderPlan:
    request_id: str
    account_id: str
    items: tuple[OrderItem, ...]
    discount_bps: int
    discount_cents: int
    total_cents: int
    policy_version: int
    audit_event: AuditEvent


def decide_order(
    command: CreateOrder,
    principal: Principal,
    policy: PricingPolicy,
) -> OrderPlan | DecisionReject:
    if (
        principal.account_id != command.account_id
        or "order:create" not in principal.capabilities
    ):
        return DecisionReject(RejectCode.UNAUTHORIZED)

    if command.requested_discount_bps > policy.maximum_discount_bps:
        return DecisionReject(RejectCode.DISCOUNT_NOT_ALLOWED)

    subtotal_cents = 0
    for item in command.items:
        line_total_cents = item.unit_price_cents * item.quantity
        if (
            line_total_cents > policy.maximum_order_total_cents
            or subtotal_cents
            > policy.maximum_order_total_cents - line_total_cents
        ):
            return DecisionReject(RejectCode.TOTAL_TOO_LARGE)
        subtotal_cents += line_total_cents

    # Explicit policy: fractional-cent discounts round down.
    discount_cents = (
        subtotal_cents * command.requested_discount_bps // BASIS_POINTS
    )
    total_cents = subtotal_cents - discount_cents

    audit_event = AuditEvent(
        kind="order.accepted",
        request_id=command.request_id,
        account_id=command.account_id,
        policy_version=policy.version,
        total_cents=total_cents,
    )
    return OrderPlan(
        request_id=command.request_id,
        account_id=command.account_id,
        items=command.items,
        discount_bps=command.requested_discount_bps,
        discount_cents=discount_cents,
        total_cents=total_cents,
        policy_version=policy.version,
        audit_event=audit_event,
    )
```

The parser checks `type(value) is int` because `bool` is a subclass of `int` in
Python. It rejects unknown fields and converts the mutable input list into an
immutable tuple. The core uses integer units and states its rounding rule.

The example assumes that `CreateOrder`, `Principal`, and `PricingPolicy` were
produced by trusted, validating constructors. A production implementation
should make those construction boundaries explicit and reject invalid policy
values before they can reach `decide_order`.

### The shell still carries critical obligations

The pure result does not make storage safe. A suitable shell protocol is:

```text
handle(request_bytes, credentials):
    reject request_bytes above the byte budget
    decode with nesting and collection limits; reject duplicate keys
    parse_order(decoded) or return ParseReject

    principal = authenticate(credentials)
    policy, expected_policy_version = load_one_policy_snapshot()
    decision = decide_order(command, principal, policy)
    if decision is DecisionReject:
        return decision

    begin database transaction
        require current policy version = expected_policy_version

        existing = load order by decision.request_id
        if existing is present:
            return existing only if it equals the same authorized plan
            otherwise reject an idempotency conflict

        insert the exact OrderPlan
        insert its AuditEvent
        insert any external notification into an outbox
    commit transaction

    deliver the outbox item with an idempotent external key
```

The transaction must cover the order, idempotency record, audit record, and
outbox entry. Recomputing a price or discount in the shell creates a second
source of domain authority.

## 6. Determinism without security myths

### The useful definition

For a fixed semantics, a deterministic transition has at most one result for a
given complete input:

```text
step(state, command, policy, evidence) = one decision
```

Time, randomness, configuration, and external observations can be explicit
input values. The shell captures them once, and the core treats them as data.
This preserves replayability without pretending that the external world is
deterministic.

### Determinism is not unpredictability

Security sometimes requires the opposite of predictable values. For example:

```python
import secrets

# Shell operation: acquire an unpredictable value from the operating system.
reset_token = secrets.token_urlsafe(32)
```

The shell can pass a hash or other derived fact into a pure transition. Reusing
a fixed pseudorandom seed in production would make the token sequence
predictable.

### Concurrency is not automatically nondeterministic

Threads, locks, asynchronous functions, and parallel evaluation do not by
themselves define an incorrect result. Nondeterminism appears when observable
behavior depends on an unspecified schedule or changing external state.

Deterministic parallel systems are possible when independent operations have a
defined merge, or conflicting operations have a stable rejection rule. A lock
can establish synchronization while leaving the winner dependent on schedule.
The security question concerns the permitted histories, not the presence of a
particular language keyword.

### Common sources of replay divergence

| Source | Accurate treatment |
|---|---|
| Clock or network | Capture the observation once with provenance and freshness data |
| Security randomness | Generate with a cryptographic source in the shell; record only what policy permits |
| Concurrency | Define atomic state versions, conflict behavior, and effect ordering |
| Maps and sets | Specify a canonical total order for hashing, signing, or cross-runtime comparison |
| Floating-point arithmetic | Specify representation and rounding, or use bounded integer units where appropriate |
| Configuration and policy | Include the exact version or hash in the decision inputs |
| Cache | Key by every semantic input and version; keep eviction from changing authoritative results |
| Language or library version | Pin it when byte-for-byte replay depends on implementation behavior |

Python dictionaries preserve insertion order in current language versions.
That does not make insertion order a canonical encoding of a logical map. Two
equal maps can be built through different histories, and sets remain unordered.
Likewise, Python deliberately salts some built-in hashes between processes.
Protocols should define their own versioned canonical bytes.

### Determinism does not remove timing leaks

Two calls can return the same value while taking observably different paths or
times. Output determinism therefore does not establish constant-time behavior,
absence of cache leakage, or resistance to traffic analysis.

## 7. Caching, logging, and retries

### Caching

A mutable cache inside an object is hidden state, even when the computed
function is intended to be pure:

```python
class CachedCalculator:
    def __init__(self) -> None:
        self._cache: dict[tuple[str, int], int] = {}
```

Memoization can be observationally transparent when the underlying computation
is pure, the cache key contains every semantic input and version, and cache
hits change only performance. It still introduces mutable memory, eviction,
resource-exhaustion, and concurrency concerns.

For security-critical code:

- keep the cache outside the authoritative transition;
- bound entries, bytes, key size, and computation per miss;
- include policy and data versions in the key;
- ensure a miss and hit return the same typed result;
- prevent attacker-selected high-cardinality keys from exhausting memory;
- test the cached implementation against an uncached reference.

An insertion-ordered dictionary with deletion of its first entry is FIFO, not
an LRU cache. An LRU policy must update recency on access.

### Logging

Appending to a buffer or file is a side effect. A “pure logger” that mutates an
internal list is not pure.

A better split is:

```text
core returns AuditEvent(...)
shell adds permitted operational context and persists it
```

Deterministic event contents support replay. They do not establish forensic
integrity. Audit logs also need access control, retention, ordering, durable
storage, tamper detection where required, and redaction of credentials,
tokens, personal data, and other secrets.

### Retries

A stateless core makes recomputation easier. It does not make effectful retries
safe. A retry can charge twice, send two messages, or overwrite newer state.

Safe retry design needs:

- a stable idempotency or replay key;
- an atomic uniqueness check with the authoritative commit;
- comparison of repeated payloads, so one key cannot authorize two commands;
- an outbox or equivalent crash-recovery protocol;
- idempotent delivery, or explicit compensation when idempotence is
  unavailable.

## 8. Testing and formal verification

### Repetition is a test, not a proof

Running a function one thousand times and observing equal results can reveal
some hidden state or randomness. It cannot prove determinism for all inputs,
states, schedules, runtimes, or environments.

Useful test families include:

| Obligation | High-value tests |
|---|---|
| Pure decision | Same typed inputs produce equal decisions; rejection produces no effects |
| Ownership | Mutating every caller-owned input after construction leaves the decision unchanged |
| Wire decoder and typed parser | Unknown, duplicate, malformed, oversized, deeply nested, Boolean-as-integer, and numeric-string cases reject as specified |
| Arithmetic | Zero, maximum, maximum neighbors, rounding boundaries, and conservation properties |
| Concurrency | Competing snapshots, stale versions, duplicate idempotency keys, and permitted operation reorderings |
| Shell recovery | Crash before, during, and after commit; retry; duplicate and reordered outbox delivery |
| Differential behavior | Reference and optimized implementations agree on the full decision and effect plan |
| Architecture | Core cannot import I/O adapters or bypass the required parser and commit path |

Property-based testing and fuzzing are especially useful for parsers,
arithmetic boundaries, and state-transition sequences. They search for
counterexamples within the generated domain. Passing samples does not establish
completeness.

### Use each formal tool for the claim it can check

- [KLEE](https://klee-se.org/docs/) symbolically explores LLVM-based program
  paths and can generate tests or find assertion and memory errors within its
  modeled environment.
- [angr](https://docs.angr.io/en/latest/quickstart.html) is a binary-analysis
  toolkit with symbolic-execution and static-analysis capabilities.
- [The Rocq Prover](https://rocq-prover.org/doc/V9.1.1/refman/proofs/writing-proofs/index.html),
  formerly Coq, checks proof terms for stated theorems in a formal model.

KLEE and angr do not automatically prove that an application is pure,
referentially transparent, stateless, or resource-bounded. A Rocq theorem
establishes its stated result under its declared assumptions. It does not
automatically establish that production byte parsing, authentication,
rounding, persistence, or external effects match the model.

A high-assurance evidence chain is:

```text
security requirement
    → formal or executable transition model
    → implementation
    → conformance tests over the same typed inputs and effects
    → atomic shell and crash-recovery tests
```

Claims should identify the exact layer:

- **tested:** selected examples or generated cases passed;
- **bounded verified:** every state in a declared finite model was checked;
- **proved:** a machine-checked theorem holds under named assumptions;
- **refinement checked:** a mounted implementation agreed with the model on a
  declared input and encoding domain.

## 9. Hardening checklist

### Threat model and requirements

- [ ] Assets, attacker capabilities, trust boundaries, and disaster states are
  named.
- [ ] Every positive claim has a scope and an explicit non-claim.
- [ ] Security-relevant policy versions and evidence provenance are explicit.
- [ ] Expected resource budgets and failure behavior are specified.

### Functional core

- [ ] Domain decisions depend only on explicit typed inputs.
- [ ] No database, network, filesystem, ambient clock, global random generator,
  or mutable singleton is read.
- [ ] Inputs and outputs are transitively immutable or defensively owned.
- [ ] Expected failures use typed rejection values.
- [ ] Rejection returns no successor state or effects, unless a distinct
  committed-failure result is specified.
- [ ] Authorization, amounts, ordering, replay policy, and exact effects are
  decided once.
- [ ] Arithmetic has explicit units, bounds, conversion rules, and rounding.
- [ ] Work, collection size, recursion, and output size are bounded.

### Imperative shell

- [ ] Raw bytes are bounded before expensive decoding.
- [ ] Untrusted data is decoded with a safe format and strict schema.
- [ ] Authentication results become typed principals with provenance and
  freshness.
- [ ] Database and command sinks use parameterized or structured APIs.
- [ ] State is loaded once with an expected version or root.
- [ ] State, effects, replay record, receipt, audit event, and outbox commit
  atomically when required.
- [ ] Retry keys are unique and bound to the complete authorized command.
- [ ] External delivery is idempotent or has a defined compensation protocol.
- [ ] Security tokens use a cryptographically secure random source.
- [ ] Rate limits, timeouts, backpressure, and circuit-breaking policy are
  present where the threat model requires them.
- [ ] Logs exclude secrets and have the required integrity and retention
  controls.

### Memory, dependencies, and deployment

- [ ] Memory-safe language features are preferred for attacker-reachable code.
- [ ] Native and unsafe regions are narrow, reviewed, fuzzed, and sanitizer
  tested.
- [ ] Dependencies, build inputs, and deployment artifacts are pinned and
  scanned according to project policy.
- [ ] Least privilege, sandboxing, credential storage, and network policy are
  reviewed separately from FCIS.
- [ ] Cryptographic operations use reviewed libraries and side-channel-aware
  APIs.

### Evidence

- [ ] Parser and boundary fuzzing cover malformed and resource-exhaustion cases.
- [ ] Alias-mutation tests cover every mutable constructor input and getter.
- [ ] Property tests cover invariants, bounds, and rounding edges.
- [ ] Concurrency tests cover stale reads, conflicts, and duplicate requests.
- [ ] Crash tests cover each shell boundary and recovery path.
- [ ] Differential tests compare the full decision, state, effects, replay
  data, and receipts.
- [ ] Formal claims name the theorem, assumptions, model, implementation
  binding, and unproved layers.

## 10. Summary

| FCIS property | Security value | Remaining obligation |
|---|---|---|
| Pure domain transition | Removes hidden application-state reads and writes from the decision | Correct and complete policy |
| Transitively immutable values | Prevents alias-driven changes to authoritative data | Native-memory safety and defensive construction |
| Typed boundary | Rejects represented malformed states early | Resource limits, authentication, and complete schemas |
| Explicit effect plan | Makes authorized side effects inspectable | Atomic commit and idempotent delivery |
| Explicit state version | Supports stale-decision rejection | Transactional enforcement under concurrency |
| Deterministic replay | Supports debugging, differential testing, and incident reconstruction | Authentic evidence, canonical encoding, and side-channel analysis |

FCIS narrows and clarifies the authority path. Its strongest security benefit is
that the system can state exactly which values justified a decision and which
effects that decision authorized.

A hardened implementation combines that architecture with memory safety,
strict parsing, domain authorization, checked arithmetic, atomic persistence,
secure randomness, least privilege, resource budgets, dependency controls,
adversarial testing, and claim-specific formal evidence.

## Sources and further reading

- Google Testing Blog,
  [Simplify Your Code: Functional Core, Imperative Shell](https://testing.googleblog.com/2025/10/simplify-your-code-functional-core.html)
- Functional Software Architecture,
  [Functional Core, Imperative Shell](https://functional-architecture.org/functional_core_imperative_shell/)
- MITRE,
  [Common Weakness Enumeration](https://cwe.mitre.org/)
- OWASP,
  [Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- OWASP,
  [SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- OWASP,
  [Deserialization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html)
- Python documentation,
  [`dataclasses`](https://docs.python.org/3/library/dataclasses.html)
- Python documentation,
  [`secrets`](https://docs.python.org/3/library/secrets.html)
- KLEE,
  [Documentation](https://klee-se.org/docs/)
- angr,
  [Introduction](https://docs.angr.io/en/latest/quickstart.html)
- The Rocq Prover,
  [Basic proof writing](https://rocq-prover.org/doc/V9.1.1/refman/proofs/writing-proofs/index.html)
