# Layer 2 serving lab (optional)

This file is optional. Use it when you reach Layer 2 and want copy/paste commands.

## A) Mac-first local serving (recommended default) — Ollama

### Goal

- Run a local model on your Mac with minimal friction.
- Measure: p50/p95 latency vs concurrency, plus “cold vs hot” felt latency.

### 1) Install

```bash
brew install ollama
```

### 2) Pull a model

Fast starter (good for learning):

```bash
ollama pull qwen2.5:3b
```

Higher quality (slower, more memory):

```bash
ollama pull qwen2.5:7b
```

### 3) Smoke test (model list)

Ollama default API is on `http://127.0.0.1:11434`.

```bash
curl -s http://127.0.0.1:11434/v1/models | head
```

If `/v1/models` doesn’t respond, Ollama may not be running yet. Start it by running one prompt:

```bash
ollama run qwen2.5:3b "Say hello in 5 words."
```

### 4) TTFT cold vs hot (simple “felt latency”)

Run once right after starting the model (“cold”), then again (“hot”).

```bash
MODEL="qwen2.5:3b"
for i in 1 2 3 4 5; do
  curl -s -o /dev/null \
    -w "ttfb_s=%{time_starttransfer} total_s=%{time_total}" \
    http://127.0.0.1:11434/v1/chat/completions \
    -H 'Content-Type: application/json' \
    -d "{\"model\":\"$MODEL\",\"messages\":[{\"role\":\"user\",\"content\":\"You are an SRE. Explain 3 steps to debug a 5xx spike. Use short bullets.\"}],\"max_tokens\":128,\"temperature\":0}"; echo
done
```

### 5) Baseline vs concurrency (p95 curve)

```bash
python3 - <<'PY'
import json, time, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

model_id = "qwen2.5:3b"
endpoint = "http://127.0.0.1:11434/v1/chat/completions"
payload = {
  "model": model_id,
  "messages": [{"role": "user", "content": "Explain in 3 short bullets why caching helps LLM serving."}],
  "max_tokens": 256,
  "temperature": 0,
}
headers = {"Content-Type": "application/json"}

def one():
  req = urllib.request.Request(endpoint, data=json.dumps(payload).encode(), headers=headers)
  t0 = time.time()
  with urllib.request.urlopen(req, timeout=180) as r:
    out = json.loads(r.read())
  dt = time.time() - t0
  usage = out.get("usage", {}) or {}
  pt = int(usage.get("prompt_tokens", 0) or 0)
  ct = int(usage.get("completion_tokens", 0) or 0)
  return dt, pt, ct

def bench(concurrency, total):
  times=[]; pt=0; ct=0
  t0=time.time()
  with ThreadPoolExecutor(max_workers=concurrency) as ex:
    futures=[ex.submit(one) for _ in range(total)]
    for f in as_completed(futures):
      dt, p, c = f.result()
      times.append(dt); pt+=p; ct+=c
  wall=time.time()-t0
  times.sort()
  p95 = times[max(0, int(0.95*len(times))-1)]
  tokens = pt + ct
  tps = (tokens / wall) if (wall > 0 and tokens > 0) else 0.0
  print(f"model={model_id} concurrency={concurrency} requests={total} wall_s={wall:.2f} p95_s={p95:.2f} tokens_per_s={tps:.1f} prompt={pt} completion={ct}")

for c in (1, 4, 8):
  bench(concurrency=c, total=c*10)
PY
```

If `tokens_per_s` prints `0.0`, it just means the server didn’t return token counts. That’s fine: record p95 and move on.

## A2) Alternative Mac-first local serving — `llama.cpp` server

### Goal

- Run a local OpenAI-compatible server on your Mac.
- Measure: p50/p95 latency vs concurrency, plus TTFT cold vs hot.

### 1) Install

```bash
brew install llama.cpp
```

If you don’t want Homebrew, build from source:
- `https://github.com/ggml-org/llama.cpp`

### 2) Start the server (downloads a quantized model)

Fast starter model (small, good for learning):

```bash
llama-server --hf-repo Qwen/Qwen2.5-3B-Instruct-GGUF:q4_k_m -c 4096 --port 8000
```

Higher quality (needs more RAM, slower):

```bash
llama-server --hf-repo Qwen/Qwen2.5-7B-Instruct-GGUF:q4_k_m -c 4096 --port 8000
```

### 3) Smoke test

```bash
curl -s http://127.0.0.1:8000/v1/models | head
```

### 4) Get the model id

```bash
MODEL_ID="$(python3 - <<'PY'
import json, urllib.request
print(json.load(urllib.request.urlopen('http://127.0.0.1:8000/v1/models'))['data'][0]['id'])
PY
)"
echo "$MODEL_ID"
```

### 5) TTFT cold vs hot (simple “felt latency”)

Restart the server to simulate “cold”, then run this loop. Run again without restarting to simulate “hot”.

```bash
for i in 1 2 3 4 5; do
  curl -s -o /dev/null \
    -w "ttfb_s=%{time_starttransfer} total_s=%{time_total}" \
    http://127.0.0.1:8000/v1/chat/completions \
    -H 'Content-Type: application/json' \
    -d "{\"model\":\"$MODEL_ID\",\"messages\":[{\"role\":\"user\",\"content\":\"You are an SRE. Explain 3 steps to debug a 5xx spike. Use short bullets.\"}],\"max_tokens\":128,\"temperature\":0,\"stream\":true}"; echo
done
```

### 6) Baseline vs concurrency (p95 curve)

```bash
python3 - <<'PY'
import json, time, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

models = json.load(urllib.request.urlopen("http://127.0.0.1:8000/v1/models"))
model_id = models["data"][0]["id"]

endpoint = "http://127.0.0.1:8000/v1/chat/completions"
payload = {
  "model": model_id,
  "messages": [{"role": "user", "content": "Explain in 3 short bullets why caching helps LLM serving."}],
  "max_tokens": 256,
  "temperature": 0,
}
headers = {"Content-Type": "application/json"}

def one():
  req = urllib.request.Request(endpoint, data=json.dumps(payload).encode(), headers=headers)
  t0 = time.time()
  with urllib.request.urlopen(req, timeout=180) as r:
    out = json.loads(r.read())
  dt = time.time() - t0
  usage = out.get("usage", {}) or {}
  pt = int(usage.get("prompt_tokens", 0) or 0)
  ct = int(usage.get("completion_tokens", 0) or 0)
  return dt, pt, ct

def bench(concurrency, total):
  times=[]; pt=0; ct=0
  t0=time.time()
  with ThreadPoolExecutor(max_workers=concurrency) as ex:
    futures=[ex.submit(one) for _ in range(total)]
    for f in as_completed(futures):
      dt, p, c = f.result()
      times.append(dt); pt+=p; ct+=c
  wall=time.time()-t0
  times.sort()
  p95 = times[max(0, int(0.95*len(times))-1)]
  tokens = pt + ct
  tps = (tokens / wall) if (wall > 0 and tokens > 0) else 0.0
  print(f"model={model_id} concurrency={concurrency} requests={total} wall_s={wall:.2f} p95_s={p95:.2f} tokens_per_s={tps:.1f} prompt={pt} completion={ct}")

for c in (1, 4, 8):
  bench(concurrency=c, total=c*10)
PY
```

If `tokens_per_s` prints `0.0`, it just means the server didn’t return token counts. That’s fine: record p95 and move on.

## B) Optional Week 6 cloud GPU smoke test — `vLLM` (OpenAI-compatible)

This is optional. It’s for an interview story: “same provider adapter, different backend”.

### Guardrails (don’t waste money)

- Hard budget cap: `$10–$20` total.
- Auto-stop the VM (provider setting) and double-check billing stops.
- Keep the port private:
  - benchmark from the VM itself (`127.0.0.1`), or
  - SSH port-forwarding (`ssh -L 8000:127.0.0.1:8000 ...`)

### Fast path

1) Create a GPU VM (Ubuntu).
2) Verify GPU + Docker:
   - `nvidia-smi`
   - `docker ps`
3) Start vLLM OpenAI server:

```bash
docker pull vllm/vllm-openai:latest
docker run --gpus all --rm --ipc=host -p 127.0.0.1:8000:8000 vllm/vllm-openai:latest \
  --model Qwen/Qwen2.5-3B-Instruct \
  --dtype half \
  --max-model-len 2048 \
  --host 0.0.0.0 \
  --port 8000
```

4) Smoke test:

```bash
curl -s http://127.0.0.1:8000/v1/models | head
```

5) Point OpsPilot config to `http://127.0.0.1:8000` (from the VM) and run 1 `/ask`.
6) Stop the VM and confirm billing stops.

## C) Back-of-envelope cost math (tokens → time → $)

This is the “platform engineer” part. Keep it simple.

1) Convert GPU price to “$ per second”
- `$ per second = ($ per hour) / 3600`

2) Estimate “$ per 1M tokens”
- Measure tokens/sec from your benchmark (vLLM will usually report `usage` tokens).
- `$ per 1M tokens ≈ ($ per second / tokens_per_second) * 1_000_000`

In interviews, your goal isn’t a perfect number. It’s showing that you know **how** to reason about cost and capacity.
