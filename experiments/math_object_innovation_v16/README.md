# v16: obligation-fiber proposer frontier

## Structural target

Test the strongest exact statement that remains after `v15`.

Because the globally ranked residual-consistent frontier already returns a safe repair program at
call `1`, obligation-fiber proposer specialization cannot strictly improve top-`1` exact-safe
discovery in the current bounded model.

So this cycle is a negative boundary, not a race:

- global top-`1` exact-safe discovery is already optimal
- specialization can only tie or distort that result

## Bounded domain

- the cached `7104` residual-consistent repair-program pairs from `v15`
- the cached `4263` unique reachable `4x4` verifier patterns from `v15`
- weighted sampled root buckets induced by seeds `99` and `123`

## Question

What leverage channel is left for specialization once global rank already certifies a safe winner
at call `1`?

In this bounded model, the answer is:

- not top-`1` exact-safe discovery
- possibly top-`k` diversity, alternative objectives, or pre-frontier proposal shaping
