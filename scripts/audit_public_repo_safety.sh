#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

SELF="scripts/audit_public_repo_safety.sh"
FAILED=0

echo "Checking tracked paths for local-only artifacts..."
while IFS= read -r path; do
  case "$path" in
    experiments/claude_experiments_mathlib/*|experiments/claude_experiments/*|experiments/aristotle_tasks/*|experiments/aristotle_results/*|experiments/orch_unit_parallel_*/*|*/.lake|*/.lake/*|*/mathlib4_link)
      echo "forbidden tracked path: $path" >&2
      FAILED=1
      ;;
  esac
done < <(git ls-files)

echo "Checking tracked text for local filesystem leaks..."
while IFS= read -r path; do
  [[ "$path" == "$SELF" ]] && continue
  [[ "$path" == ".gitignore" ]] && continue
  if grep -I -n -E '(/home/|/Users/|C:\\Users|Downloads/FormalPhilosophy|mathlib4_link|experiments/claude_experiments_mathlib)' "$path" >/tmp/public_repo_safety_hits.$$ 2>/dev/null; then
    sed "s#^#$path:#" /tmp/public_repo_safety_hits.$$ >&2
    FAILED=1
  fi
  if [[ -n "${USER:-}" ]] && grep -I -n -F "${USER}" "$path" >/tmp/public_repo_safety_hits.$$ 2>/dev/null; then
    sed "s#^#$path:#" /tmp/public_repo_safety_hits.$$ >&2
    FAILED=1
  fi
done < <(git ls-files)
rm -f /tmp/public_repo_safety_hits.$$

if [[ "$FAILED" != "0" ]]; then
  echo "Public repo safety audit failed." >&2
  exit 1
fi

echo "Public repo safety audit passed."
