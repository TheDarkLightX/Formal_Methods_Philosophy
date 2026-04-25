# Tau Examples

This folder contains small, runnable Tau specifications that support the tutorials.

Most files in this folder are self-contained REPL transcripts: they declare streams, run a spec with the `r` command, feed a demo input sequence, then quit.

Some newer examples, including the perceptron files used by Tutorial 21, are spec bodies rather than full transcripts. Those are meant to be driven by the local runner and trace-generation script, not pasted directly into the REPL by hand.

## Quick Start

### 1. Build Tau (once)

From the repo root:

```bash
./scripts/update_tau_lang.sh
```

### 2. Run an example

```bash
./scripts/run_tau_policy.sh examples/tau/turnstile_fsm_alarm.tau
```

## How to Read Tau Syntax

### Stream Declarations

```tau
i1 : bv[8] := in console    # input stream, 8-bit bitvector, from console
o1 : bv[8] := out console   # output stream, 8-bit bitvector, to console
o2 : sbf := out console     # output stream, simple Boolean function (often used as a 0/1 flag)
```

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Important: transcript rule</p>
  <p>
    These <code>.tau</code> files are REPL transcripts. After the <code>r ...</code> line, the REPL switches into
    execution mode and treats every following line as input. Do not place blank lines or comments after <code>r ...</code>
    until the end; one blank line terminates execution and returns to the REPL.
  </p>
</div>

### Type Annotations in Specs

Variables in specs need explicit type annotations:

```tau
o1[t]:bv[8]            # output o1 at time t, typed as bv[8]
i1[t-1]:bv[8]          # input i1 at previous time step
{ 128 }:bv[8]          # constant 128 as bv[8]
1:sbf                  # boolean constant 1 as sbf
```

### Operators

**Term operators** (bit-level, work on values):
| Symbol | Meaning | Example |
|--------|---------|---------|
| `+` | addition (modular) | `x + y` |
| `-` | subtraction (modular) | `x - y` |
| `*` | multiplication (modular) | `x * y` |
| `&` | bitwise AND | `x & y` |
| `\|` | bitwise OR | `x \| y` |
| `^` | bitwise XOR | `x ^ y` |
| `'` | complement | `x'` |

**Formula operators** (logical, combine constraints):
| Symbol | Meaning | Example |
|--------|---------|---------|
| `&&` | logical AND | `(a = 0) && (b = 1)` |
| `\|\|` | logical OR | `(a = 0) \|\| (b = 0)` |
| `!` | logical NOT | `!(a = 0)` |
| `<->` | equivalence | `(flag = 1) <-> (x > y)` |
| `=` | equality | `x = y` |
| `>`, `<`, `>=`, `<=` | comparison | `x > y` |

### Helper Functions

```tau
fname(x) : bv[8] := x ^ { 1 }:bv[8]   # function returning bv[8]
```

### Predicates

```tau
is_valid(d : bv[8]) := (d = { 0 }:bv[8]) || (d = { 1 }:bv[8]).
```

### Complete Spec Example

```tau
r (o1[0]:bv[8] = { 0 }:bv[8]) && (o1[t]:bv[8] = o1[t-1]:bv[8] + i1[t]:bv[8])
```

Breakdown:
- `r` - run command
- `o1[0]:bv[8] = { 0 }:bv[8]` - initial condition: output starts at 0
- `&&` - logical AND (both constraints must hold)
- `o1[t]:bv[8] = o1[t-1]:bv[8] + i1[t]:bv[8]` - update rule: running sum

## Examples

### Turnstile State Machine

**File:** `turnstile_fsm_alarm.tau`

A two-state machine (Locked/Unlocked) demonstrating:
- State encoded as a 0/1 output stream
- Input events (coin, push) driving transitions
- An alarm flag raised when pushing a locked turnstile

### Card Counting (Hi-Lo)

**File:** `card_counting_hilo_state_tracker.tau`

An approximate state tracker (from Tutorial 1):
- Tracks running count AND cards seen
- Input: pre-classified delta (+1, 0, -1 as 1, 0, 255)
- Output: biased running count (count + 128)

### Toggle Puzzle (XOR State)

**File:** `toggle_puzzle_xor_state.tau`

A "Lights Out" style puzzle demonstrating:
- Board state as bitvector
- XOR update: `board[t] = board[t-1] ^ move[t]`
- Isomorphism: XOR over bits = addition in F_2

### Q-Learning Tabular Update

**File:** `q_learning_tabular_update.tau`

A single-step Q-table update showing:
- Lookup table as input/output streams
- Selective update using masks
- The "guardrails" pattern

## Design Patterns

### Push Parsing Out of Tau

Tau is good at constraints, not string parsing. Keep complex classification in the host system; let Tau enforce simple invariants.

### Single-Step vs Multi-Step

Some specs model one step. To run multiple steps, the host "closes the loop" by feeding outputs back as inputs.

### The Guardrails Pattern

The host chooses *what* to do. Tau enforces *how* the update is shaped. This makes systems both adaptive and auditable.

### Perceptron (external unsigned weights)

**File:** `perceptron_2input_single_output_v1.tau`

A smallest-form 2-input perceptron checker:
- host provides `x1`, `x2`, `w1`, `w2`, `bias`, `threshold`, and a claimed class
- Tau checks the bounded weighted-sum rule
- useful for showing a classifier as an executable invariant

### Perceptron (signed offset encoding)

**File:** `perceptron_2input_signed_offset_v1.tau`

A signed-style variant using offset encoding:
- decoded logical value = encoded value minus `127`
- Tau checks an equivalent unsigned inequality
- useful for explaining how signed learning state can be serialized into Tau-friendly bounded integers

### Perceptron (internal spec weights)

**File:** `perceptron_2input_internal_weights_v1.tau`

A variant where the weights and bias live inside the spec:
- host provides only `x1`, `x2`, `threshold`, and the claimed class
- Tau owns the classifier parameters
- useful for contrasting external streams with internal parameters

### Perceptron (stateful memory, explored branch)

Files:
- `perceptron_2input_learning_memory_v1.tau`
- `perceptron_weight_memory_v1.tau`

These files explore a stronger temporal story:
- weights stored across time in Tau-visible state streams,
- signed deltas applied step by step,
- learning-style state transitions rather than only pointwise classifier checks.

They are included as experimental branches, not as promoted replayed evidence in the public tutorial, because the recurrent variants were heavier under the current runner budget than the three faster classifier lanes.

### Medical deciders in the MPRD shape

Files:
- `medical_wellness_deficit_gate_v1.tau`
- `medical_lab_followup_gate_toy_v1.tau`
- `medical_refill_gate_toy_v1.tau`

These files support the medical MPRD tutorial.

They are deliberately scoped as educational policy examples:
- the host computes structured facts and evidence flags,
- Tau validates the bounded allow or deny logic,
- the examples are not clinical guidance or medical advice.

The pattern mirrors MPRD:
- model or host proposes a bounded action,
- policy decides whether that action is allowed,
- the safe fallback is usually escalation to a human rather than autonomous execution.

### Decidable medical machines

Files:
- `medical_max_calorie_deficit_formula_v1.tau`
- `medical_max_calorie_deficit_calculator_v1.tau`
- `medical_egfr_followup_gate_v1.tau`

These files support the decidable medical machines tutorial.

They split into two teaching lanes:
- `medical_max_calorie_deficit_formula_v1.tau` is a **checker**: it validates a claimed deficit against the floor of the formula
- `medical_max_calorie_deficit_calculator_v1.tau` is a **direct calculator**: the solver synthesizes the exact integer floor as an output, so the user gets an answer without supplying a claim
- `medical_egfr_followup_gate_v1.tau` follows the host-computes / Tau-validates pattern for a kidney follow-up workflow

Together they show:
- a simple calculator as an exact total function,
- a medical-style decision tree as a finite action gate,
- and the boundary where Tau should validate policy even when the richer numeric equation is computed outside Tau.


### Sparse Impacted-Factor Speed Demo

**File:** `sparse_impact_factor_speedup_demo.tau`

A generated Tau solve command used by Tutorial 52:
- `24` top-level conjunct factors,
- `3` factors mention the changed variable `d0`,
- `21` factors are reusable by the sparse-impact model,
- the patched Tau runtime emits indexed-factor solve and profit telemetry.

Patch a Tau checkout, rebuild it, write the demo spec, and run the measured
demo:

```bash
python3 scripts/run_tau_sparse_impact_demo.py --tau-checkout /path/to/tau-lang-latest
```

This is a local performance demo, not a claim that arbitrary Tau formulas speed
up. The route is feature-gated and scoped to sparse top-level conjunctions.

Demo artifacts:

- [Demo runner](../../scripts/run_tau_sparse_impact_demo.py):
  `scripts/run_tau_sparse_impact_demo.py`
- [Tau source patch](../../patches/tau/indexed-factor-sparse-impact-demo.patch):
  `patches/tau/indexed-factor-sparse-impact-demo.patch`
- [Generated Tau spec](sparse_impact_factor_speedup_demo.tau):
  `examples/tau/sparse_impact_factor_speedup_demo.tau`
