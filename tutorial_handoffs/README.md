# Tutorial Handoffs

This folder stores short restart packets for tutorial-specific work.

The point is to prevent session drift.

Each tutorial should have its own handoff file.

## Naming

Use:

```text
tutorial-XX-short-slug.md
```

Examples:

- `tutorial-27-verifier-compiler-loops.md`
- `tutorial-28-profit-agents-post-agi-economics.md`

## Required sections

Each handoff file should include:

1. scope
   - what belongs in the tutorial
   - what does not belong in the tutorial
2. current public-facing structure
   - how sections are numbered for readers
   - any important writing conventions
3. strongest local results
   - only the stable results needed to resume honestly
4. known mistakes or drift to avoid
5. next honest frontiers
6. source experiment range
   - which experiment folders back the current tutorial state

## Public-repo hygiene

These files are for restart and maintenance.
They should still follow the repo rules:

- explicit assumptions
- scoped claims
- no hidden universalization
- no machine-specific secrets

## Current handoffs

- `tutorial-27-verifier-compiler-loops.md`
- `tutorial-28-profit-agents-post-agi-economics.md`
- `tutorial-29-loop-space-geometry.md`
- `tutorial-34-proposer-swarms.md`
- `tutorial-35-model-compression-micro-models.md`
