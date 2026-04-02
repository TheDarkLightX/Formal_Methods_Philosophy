# Tutorial 35 Handoff

## Scope

This tutorial is about:

- why model compression matters for local proposer architectures
- the difference between weight compression and KV-cache compression
- BitNet as the research foundation
- Bonsai as the current public deployment frontier
- TurboQuant as the runtime-memory side
- what is actually ready for a laptop experiment

This tutorial is not for:

- claiming that compression creates formal correctness
- presenting vendor claims as established independent facts
- promising a TurboQuant laptop benchmark before a concrete implementation is
  chosen

## Current public-facing structure

This tutorial is not public yet.

If it becomes public, it should teach this progression:

1. two distinct compression levers
2. BitNet and native low-bit training
3. bitnet.cpp and the open deployment path
4. Bonsai and the current Apple-friendly state of the art
5. TurboQuant and KV-cache compression
6. why these technologies matter for proposer swarms
7. what a real MacBook experiment should try first

The tutorial should feel like systems literacy, not like product hype.

## Strongest local results to preserve

1. Weight compression and KV-cache compression solve different bottlenecks.

2. The strongest research foundation is:
   - BitNet b1.58
   - BitNet b1.58 2B4T
   - bitnet.cpp

3. The cleanest current deployment cards are:
   - `prism-ml/Bonsai-8B-gguf`
   - `prism-ml/Bonsai-8B-mlx-1bit`

4. The safest reading of Bonsai is:
   - serious public deployment track
   - concrete downloadable model cards
   - concrete Apple and Metal quickstarts
   - stronger benchmark and energy claims still treated as vendor claims

5. TurboQuant matters because it changes inference working-memory economics,
   not because it shrinks base model weights.

6. The current MacBook experiment order should be:
   - first official BitNet
   - then Bonsai on MLX or Metal
   - then TurboQuant only after choosing an implementation path

## Current MacBook experiment plan

Assumption A (explicit):

- the MacBook Pro M3 with `128 GB` unified memory is strong enough to run the
  BitNet and Bonsai tracks locally without special remote infrastructure

That assumption is well-motivated, but it still needs a real run receipt.

### Track A, open baseline: BitNet

Purpose:

- establish the strongest open low-bit baseline first

Suggested commands:

```bash
git clone --recursive https://github.com/microsoft/BitNet.git
cd BitNet
conda create -n bitnet-cpp python=3.9
conda activate bitnet-cpp
pip install -r requirements.txt
huggingface-cli download microsoft/BitNet-b1.58-2B-4T-gguf \
  --local-dir models/BitNet-b1.58-2B-4T
python setup_env.py -md models/BitNet-b1.58-2B-4T -q i2_s
python run_inference.py \
  -m models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf \
  -p "You are a helpful assistant" \
  -cnv
```

Expected value:

- reproducible open baseline
- clear CPU-first reference point

### Track B, Apple-specific deployment: Bonsai MLX

Purpose:

- test the strongest Apple-oriented 1-bit deployment path

Suggested commands:

```bash
python3 -m venv .venv-bonsai-mlx
source .venv-bonsai-mlx/bin/activate
pip install mlx-lm
pip install "mlx @ git+https://github.com/PrismML-Eng/mlx.git@prism"
python - <<'PY'
from mlx_lm import load, generate
model, tokenizer = load("prism-ml/Bonsai-8B-mlx-1bit")
print(generate(
    model,
    tokenizer,
    prompt="Explain quantum computing in simple terms.",
    max_tokens=256,
))
PY
```

Important caveat:

- Prism's model card says this route currently requires their MLX fork, with
  upstream support still pending

### Track C, Apple-specific deployment: Bonsai GGUF on Metal

Purpose:

- test the Metal path through `llama.cpp`

Suggested commands:

```bash
git clone https://github.com/PrismML-Eng/llama.cpp
cd llama.cpp
cmake -B build && cmake --build build -j
huggingface-cli download prism-ml/Bonsai-8B-gguf \
  --include "Bonsai-8B-Q1_0_g128.gguf" \
  --local-dir models/Bonsai-8B-gguf
./build/bin/llama-cli \
  -m models/Bonsai-8B-gguf/Bonsai-8B-Q1_0_g128.gguf \
  -p "Explain quantum computing in simple terms." \
  -n 256 \
  --temp 0.5 \
  --top-p 0.85 \
  --top-k 20 \
  -ngl 99
```

### Track D, analysis-first only: TurboQuant

Current rule:

- do not promise a TurboQuant laptop benchmark yet
- first choose a concrete implementation path
- otherwise keep TurboQuant in the tutorial as a systems idea plus paper-level
  result

## What to record

For each successful run, record:

- commit or model version
- runtime path
- cold-start load time
- prompt throughput
- generation throughput
- peak memory observed
- one short proposer-style prompt test
- one short summarizer-style prompt test
- one short critic-style prompt test

The point is not only raw speed. The point is whether compressed local models
are good enough to fill distinct proposer roles.

## Known mistakes or drift to avoid

1. Do not call BitNet b1.58 purely binary. The key published form is ternary
   `{-1, 0, 1}`.
2. Do not treat Bonsai's strongest performance claims as independently settled.
3. Do not write as if TurboQuant is already a turnkey local benchmark path.
4. Do not let the tutorial imply that compression replaces the exact gate.
5. Do not lose the proposer-swarm connection. Compression matters here because
   it makes several local roles plausible.

## Next honest frontiers

- build a reproducible MacBook benchmark sheet for BitNet and Bonsai
- choose one concrete TurboQuant software stack or keep it analysis-only
- measure proposer-role quality, not only raw tokens per second

## Source range

- `tutorial_drafts/model-compression-1bit-and-kv-compression.md`
- `tutorial_drafts/proposer-swarms.md`
- `tutorials/formal-neural-networks.md`
