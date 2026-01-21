# Tau examples

This folder contains small, runnable Tau scripts that support the tutorials.

## Build Tau (local clone, ignored)

From the repo root:

`./scripts/update_tau_lang.sh`

This clones `IDNI/tau-lang` into `external/tau-lang` and builds `external/tau-lang/build-Release/tau`.

## Run an example

From the repo root:

`./scripts/run_tau_policy.sh examples/tau/card_counting_hilo_state_tracker.tau`

The script currently includes a built-in demo input sequence, so it runs end-to-end and quits automatically.
