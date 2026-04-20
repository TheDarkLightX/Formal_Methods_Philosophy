#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TAU_DIR="${TAU_QNS_DIR:-"$ROOT/external/tau-lang-qns-ba"}"
PATCH="$ROOT/experiments/qns_semantic_ba/qns_candidate_ba_tau.patch"
JOBS="${JOBS:-4}"

if [[ ! -d "$TAU_DIR/.git" ]]; then
  git clone --recurse-submodules https://github.com/IDNI/tau-lang.git "$TAU_DIR"
fi

if [[ ! -d "$TAU_DIR/external/parser/.git" && ! -f "$TAU_DIR/external/parser/.git" ]]; then
  git -C "$TAU_DIR" submodule update --init --recursive external/parser
fi

if [[ ! -f "$TAU_DIR/src/boolean_algebras/qns_candidate_ba.h" ]]; then
  git -C "$TAU_DIR" apply "$PATCH"
fi

(
  cd "$TAU_DIR"
  ./dev build Release \
    -DTAU_BUILD_EXECUTABLE=ON \
    -DTAU_BUILD_STATIC_LIBRARY=ON \
    -DTAU_BUILD_SHARED_LIBRARY=OFF \
    -DTAU_BUILD_TESTS=OFF \
    -DTAU_BUILD_JOBS="$JOBS"
)

python3 "$ROOT/scripts/generate_qns_candidate_ba_artifacts.py" \
  --tau-bin "$TAU_DIR/build-Release/tau" \
  --timeout-s "${TAU_QNS_TIMEOUT_S:-10}"

echo "qNS semantic BA demos passed."
