# Neuro-symbolic math v001

This Lean packet checks the first proof layer behind the qNS and EML tutorials.

## qNS laws

The qNS section models a carrier as `Atom -> Bool`, which is the predicate
view of a finite powerset Boolean algebra. It proves:

```text
auto_accept_no_hard_reject
auto_and_review_disjoint
partition_eq_proposed
survivors_are_proposed
survivors_avoid_hard_reject
```

These are exact Boolean-set laws. They do not prove neural scoring or atom
extraction.

## EML laws

The EML section defines an abstract `Semantics` with:

```text
one, exp, log, sub
eml(a,b) = sub (exp a) (log b)
```

It then makes the necessary log/exp cancellation laws explicit as hypotheses
and proves:

```text
eml_exp_identity
eml_log_standard_identity
eml_log_discovered_identity
eval_expTree
eval_logStandardTree
eval_logDiscoveredTree
Cert.sound
```

This is intentionally not a real-analysis proof. It is a scoped algebraic
proof surface showing exactly which laws make the EML trees reduce to `exp x`
and `log x`.

The finite certificate checker accepts exactly the three current survivor
shapes used by the tutorial and proves that an accepted certificate is sound
under the explicit abstract EML laws.

## Run

```bash
cd experiments/neuro_symbolic_math_v001
lake env lean Proofs.lean
```
