# Tau Examples

This folder contains small, runnable Tau specifications that support the tutorials.

Each file is a self-contained REPL transcript: it declares streams, runs a spec with the `r` command, feeds a demo input sequence, then quits.

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
o2 : sbf := out console     # output stream, simple boolean flag (0 or 1)
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
