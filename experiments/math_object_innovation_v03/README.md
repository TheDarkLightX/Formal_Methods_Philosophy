# Math Object Innovation v03

## Structural target

Policy iteration over obligation-targeted witness routing.

The v02 cycle compressed the coupled closure policy into:

- an obligation-only controller
- plus a witness router

This cycle asks whether that obligation controller can be systematically improved by policy iteration.

## Core idea

Let `pi_0` be the routed controller from v02.

Define its value function over candidate states:

- `V_pi(C) = (steps_pi(C), checks_pi(C))`

Then improve the controller by:

- `pi_{k+1}(C) := argmin_{y in U(C)} (1 + steps_{pi_k}(C_y), |U(C)| + checks_{pi_k}(C_y), y)`

where:

- `U(C) := Y \\ Psi(C)`
- `C_y := C ∩ Phi({y})`

This is ordinary policy improvement in a deterministic finite control problem, but applied to the obligation-side controller extracted from the neuro-symbolic loop.

## Bounded domain

- exhaustive `4x4` boolean relations
- random `5x5` and `6x6` holdout

## Goal

Check whether a small number of improvement rounds reaches bounded optimum.

## Files

- `run_cycle.py`
- `test_cycle.py`
- `generated/report.json`
