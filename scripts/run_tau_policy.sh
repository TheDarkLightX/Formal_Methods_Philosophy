#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: run_tau_policy.sh path/to/policy.tau" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
DEFAULT_TAU_BIN="${ROOT}/external/tau-lang/build-Release/tau"
TAU_BIN="${TAU_BIN:-${DEFAULT_TAU_BIN}}"

POLICY_PATH="$1"
if [[ ! -f "${POLICY_PATH}" ]]; then
  echo "error: policy not found: ${POLICY_PATH}" >&2
  exit 2
fi

if [[ ! -x "${TAU_BIN}" ]]; then
  echo "error: TAU_BIN not found/executable: ${TAU_BIN}" >&2
  echo "hint: run ./scripts/update_tau_lang.sh or set TAU_BIN=/path/to/tau" >&2
  exit 2
fi

POLICY_DIR="$(cd "$(dirname "${POLICY_PATH}")" && pwd)"
POLICY_FILE="$(basename "${POLICY_PATH}")"

mkdir -p "${POLICY_DIR}/outputs"
cd "${POLICY_DIR}"
"${TAU_BIN}" < "${POLICY_FILE}"
