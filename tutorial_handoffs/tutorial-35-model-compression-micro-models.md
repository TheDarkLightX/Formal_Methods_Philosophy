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

## Key concepts that must be explained before the experiment

1. **Weight compression**
   - shrink the stored model parameters
   - examples:
     - BitNet
     - Bonsai

2. **Runtime-state compression**
   - shrink active inference memory, especially KV cache
   - example:
     - TurboQuant

3. **Native low-bit training**
   - train the model for low-bit operation from the start
   - this is stronger than ordinary post-training quantization

4. **Ternary weights**
   - BitNet b1.58 is not purely binary
   - the important published form is:

```text
w in {-1, 0, 1}
```

5. **GGUF**
   - a deployment format commonly used with `llama.cpp`
   - relevant for Bonsai Metal experiments

6. **MLX**
   - Apple's machine-learning framework for Apple Silicon
   - relevant for the Bonsai MLX route

7. **KV cache**
   - the stored keys and values from earlier tokens during transformer
     inference
   - often the main memory bottleneck for long contexts

8. **Vector quantization**
   - a compression method that maps high-dimensional data into a smaller coded
     representation
   - central to TurboQuant

9. **Why this matters here**
   - compression does not make a model more correct
   - it makes it practical to run several local proposer roles before an exact
     gate

## Source packet

### BitNet, primary sources

- BitNet JMLR paper:
  - https://jmlr.org/papers/volume26/24-2050/24-2050.pdf
- The Era of 1-bit LLMs:
  - https://arxiv.org/abs/2402.17764
- BitNet b1.58 2B4T technical report:
  - https://arxiv.org/abs/2504.12285
- bitnet.cpp paper:
  - https://arxiv.org/abs/2502.11880
- BitNet official site:
  - https://bitnet.live/
- Microsoft BitNet repository:
  - https://github.com/microsoft/BitNet

### Bonsai, deployment frontier

- Prism ML announcement:
  - https://prismml.com/news/bonsai-8b
- Bonsai collection:
  - https://huggingface.co/collections/prism-ml/bonsai
- Bonsai GGUF model card:
  - https://huggingface.co/prism-ml/Bonsai-8B-gguf
- Bonsai MLX model card:
  - https://huggingface.co/prism-ml/Bonsai-8B-mlx-1bit
- Prism ML `llama.cpp` fork:
  - https://github.com/PrismML-Eng/llama.cpp
- Prism ML `mlx` fork:
  - https://github.com/PrismML-Eng/mlx

### TurboQuant, KV-cache compression

- TurboQuant paper:
  - https://arxiv.org/abs/2504.19874
- Google Research blog:
  - https://research.google/blog/turboquant-redefining-ai-efficiency-with-extreme-compression/

### Architecture context in this repo

- MPRD repository:
  - https://github.com/TheDarkLightX/MPRD
- ZenoDEX repository:
  - https://github.com/TheDarkLightX/ZenoDEX
- Tutorial 33, `tutorials/formal-neural-networks.md`

## Hardware and software prerequisites

Assumption A (explicit):

- the MacBook Pro M3 with `128 GB` unified memory is strong enough to run the
  BitNet and Bonsai tracks locally without special remote infrastructure

Assumption B (explicit):

- the experimenter has access to:
  - Xcode command-line tools
  - Python 3.10 or newer
  - Git
  - either `conda` or `venv`
  - Hugging Face CLI

Suggested bootstrap:

```bash
xcode-select --install
python3 -m pip install --upgrade pip
python3 -m pip install "huggingface_hub[cli]"
```

## Current MacBook experiment plan

### Track A, open baseline: BitNet

Purpose:

- establish the strongest open low-bit baseline first
- get one fully open reproducible receipt before using vendor-led deployments

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
  -p "Summarize why bounded proposers need exact gates." \
  -cnv
```

Expected value:

- reproducible open baseline
- clear CPU-first reference point

Key things to confirm:

- the model loads cleanly
- the throughput is acceptable on Apple hardware
- the output is coherent enough for small proposer or summarizer roles

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
    prompt="Summarize why bounded proposers need exact gates.",
    max_tokens=256,
))
PY
```

Important caveat:

- Prism's model card says this route currently requires their MLX fork, with
  upstream support still pending

Key things to confirm:

- load success on the MacBook
- prompt throughput
- whether the MLX path is more stable than the GGUF path on this machine

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
  -p "Summarize why bounded proposers need exact gates." \
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

Why Track D is deferred:

- the paper and blog are strong
- but a reproducible laptop experiment still depends on a chosen implementation
  path
- this handoff should not pretend that a paper citation alone is enough

## Benchmark prompt packet

Use the same small prompt packet across BitNet and Bonsai runs.

### Prompt 1, proposer-style

```text
State summary:
- volatility: high
- oracle divergence: moderate
- liquidity stress: elevated
- allowed actions: tighten_spread, pause_oracle_sensitive_route, no_op

Return the single best action and one sentence of justification.
```

### Prompt 2, summarizer-style

```text
Summarize this control state into four bounded labels:
volatility, liquidity, oracle_confidence, action_urgency.

State:
- 15 minute realized volatility doubled
- order book depth fell 28%
- oracle lag rose from 2 seconds to 7 seconds
- settlement queue still below warning threshold
```

### Prompt 3, critic-style

```text
Candidate action: tighten_spread
State summary:
- volatility: high
- oracle divergence: high
- liquidity stress: high
- emergency_freeze: false

List the two most likely denial reasons if an exact gate rejects this action.
```

### Prompt 4, explanation-style

```text
The gate denied action pause_oracle_sensitive_route because:
- policy clause oracle_pause_requires_divergence_gt_8pct was false
- measured divergence was 5.2%

Explain the denial in two short sentences.
```

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
- one short explanation-style prompt test

Also record:

- was the route easy to install?
- what upstream project or model card was actually followed?
- what failed, if anything, and at which step?

The point is not only raw speed. The point is whether compressed local models
are good enough to fill distinct proposer roles.

## Minimal success criteria

Track A is a success if:

- BitNet loads and generates locally
- a receipt exists for throughput and peak memory
- the prompt packet can be completed without obvious collapse

Track B or C is a success if:

- one Bonsai route loads and generates locally
- throughput is measured
- the prompt packet can be completed

The full packet is a success if:

- there is one reproducible open baseline
- there is one Apple-oriented stronger deployment receipt
- the results are strong enough to justify a bounded proposer-swarm experiment

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
