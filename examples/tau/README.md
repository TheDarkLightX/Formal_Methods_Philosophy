# Tau examples

This folder contains small, runnable Tau scripts that support the tutorials.

Each file is a reproducible REPL transcript: it declares streams, runs a spec, feeds a short demo input sequence, then quits.

## Build Tau (local clone, ignored)

From the repo root:

`./scripts/update_tau_lang.sh`

This clones `IDNI/tau-lang` into `external/tau-lang` and builds `external/tau-lang/build-Release/tau`.

## Run an example

From the repo root:

`./scripts/run_tau_policy.sh examples/tau/card_counting_hilo_state_tracker.tau`

Examples included:

- `examples/tau/card_counting_hilo_state_tracker.tau`: an approximate state tracker (Hi-Lo running count).
- `examples/tau/turnstile_fsm_alarm.tau`: a tiny turnstile state machine with an alarm flag.
- `examples/tau/toggle_puzzle_xor_state.tau`: a toy toggle puzzle where the board update is XOR.
- `examples/tau/q_learning_tabular_update.tau`: a 2x2 Q-table update (lookup table + reward-driven update).

Each file includes a built-in demo input sequence, so it runs end-to-end and quits automatically.
