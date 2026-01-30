## Project goals

This repo is a public tutorial site about formal methods, aimed at beginners. Prioritize clarity, correctness, and falsifiable claims over cleverness.

## Assumption hygiene (use everywhere)

When writing or editing content, do not smuggle in unfounded assumptions as facts.

Preferred workflow:

1. **State** the assumption explicitly (label it if it matters).
2. **Scope** the claim: write it as conditional when appropriate ("If A, then B"), or explicitly tie it to a model ("In model M, ...").
3. **Stress-test** the assumption: look for counterexamples, edge cases, and attacker moves; add a gate/check when the assumption is safety-critical.

Rule of thumb:

- **Quarantine, do not auto-reject.** Unfounded assumptions can be useful as premises for exploration, but they must be clearly marked and tracked.

## Public repo safety

- Never include absolute local filesystem paths, machine-specific usernames, or private directory structure in published docs.
- Avoid leaking secrets or credentials in examples (tokens, keys, cookies, etc.).

## Writing conventions

- Avoid em dashes; prefer commas, parentheses, or split sentences.
- Avoid second-person "you" unless the section is explicitly instructional and the audience is clearly addressed.
