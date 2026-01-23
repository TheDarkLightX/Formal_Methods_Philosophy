#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TAU_DIR="${ROOT}/external/tau-lang"

if [[ ! -d "${TAU_DIR}" ]]; then
  mkdir -p "${ROOT}/external"
  git clone https://github.com/IDNI/tau-lang "${TAU_DIR}"
fi

git -C "${TAU_DIR}" fetch --prune origin
git -C "${TAU_DIR}" checkout main
git -C "${TAU_DIR}" pull --ff-only origin main
git -C "${TAU_DIR}" submodule update --init --recursive

JOBS="$(command -v nproc >/dev/null 2>&1 && nproc || echo 4)"
cmake -S "${TAU_DIR}" -B "${TAU_DIR}/build-Release" -DCMAKE_BUILD_TYPE=Release
cmake --build "${TAU_DIR}/build-Release" -j "${JOBS}"

echo
"${TAU_DIR}/build-Release/tau" --version
