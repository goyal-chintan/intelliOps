# OpsPilot Daily Guide (8 weeks, 30–45 min/day)

This file is your **day-by-day plan**.

Theory (definitions + mental models + math + interview questions) is in:
- `docs/learning-fundamentals.md`

How to use this daily (don’t overthink it):
1) Read today’s **Theory** sections (10–15 min)
2) Answer today’s **Core interview questions** (5–10 min)
3) Do today’s **Build step** (20–45 min, time-boxed)
4) Write 5 lines in Obsidian (2–5 min)
5) Stop.

If you only have ~30 minutes total:
- Read the **Must know (fast path)** blocks in `docs/learning-fundamentals.md` for today.
- Answer only the **Core Q1–Q3** questions.
- Do only the “If short on time” line in today’s Build step.

If you feel stuck (motivation saver):
- Use the **10-minute rule**: if you’re blocked for 10 minutes, stop debugging.
  Do the “If short on time” task, write “blocked on X” in Obsidian, and end the day.
- Tomorrow, your only goal is to unblock that one thing.
- Progress > perfection. You win by showing measurable results at each layer.

## What “industry‑grade LLM platform” means (simple checklist)

If you want to be treated like an LLM/AI platform engineer (not “someone who can prompt”), you must show these:

- **Correctness mindset**: you don’t trust the model; you verify with data + evals.
- **Measurable quality**: a gold set, repeatable scoring, regression tracking.
- **Measurable performance**: p50/p95 latency with a clear breakdown (DB vs LLM vs app).
- **Measurable cost**: tokens in/out, cost per tenant/team, and cost controls.
- **Safety**: tenant isolation, no data leakage, prompt injection awareness, safe logging.
- **Operability**: tracing/logging/metrics, timeouts, retries, fallbacks, dashboards.
- **Change discipline**: when you change prompts/models/retrieval, you re-run evals.

## Your default build order (optimal for industry)

1) **Start with Python (FastAPI) + RAG** because this is the “AI product core”.  
2) Add **Postgres + pgvector** early so your retrieval stack is realistic.  
3) Add the **Spring Boot gateway** after Layer 0 works, because gateways are easiest when you already know the downstream API shape.  
4) Only after the above, go deep on **serving/batching/cache/routing** (Layer 2), because you need a working request path to benchmark.

## Model recommendations (pick one set and move on)

Default hosted baseline (fast progress):
- **Hosted LLM**: `gpt-4o-mini`  
- **Hosted embeddings**: `text-embedding-3-small`

Cheapest learning option (local-first, optional):
- **Local LLM (Ollama)**: `qwen2.5:7b-instruct` or `llama3.1:8b-instruct`
- **Local embeddings**: `nomic-embed-text`

Rule of thumb:
- Use hosted models for Layer 0/1 (stable, less friction).
- Use local models to learn serving, caching, routing, and cost control (Layer 2).

## Tools (keep it simple)

- **CLI only** (no UI required)
- **Database**: Postgres + pgvector
- **Gateway**: Spring Boot (auth, tenant routing, observability, later routing/cost controls)
- **AI service**: Python + FastAPI (RAG + agents + tool calls)

## Default tech choices (don’t overthink)

Pick these defaults unless you have a strong reason not to:

- AI service (Python): FastAPI + Uvicorn + Pydantic
- HTTP client: `httpx`
- Postgres driver: `psycopg` (simple) or `asyncpg` (async) — pick one and stick to it
- LLM + embeddings: OpenAI-compatible client (so you can swap hosted/self-hosted later)
- Agent workflow: LangGraph (predictable graphs over “freeform chains”)
- Tracing: OpenTelemetry (OTLP exporter)
- Dashboards: Grafana (Tempo for traces, Prometheus for metrics)

## One-time setup (do once, then stop thinking about it)

You can do this on Day 4–5 if you prefer, but it’s easier if setup is not blocking you later.

- Install prerequisites:
  - Python 3.x (`python3`)
  - Docker Desktop (daemon running)
  - Java 17+ (for Spring Boot gateway)
- Pick your “service folders” (recommended):
  - `services/ai-service/` (FastAPI)
  - `services/gateway/` (Spring Boot)
- Create a local Postgres with pgvector (compose is simplest):
  - image can be `pgvector/pgvector:pg16` (or any Postgres with pgvector installed)
  - your DB must support: `CREATE EXTENSION vector;`
- Create environment variables (do not commit secrets):
  - `OPENAI_API_KEY` (or your provider key)
  - `DATABASE_URL` (Postgres connection string)

## The “don’t waste time” rules (so you finish in 2 months)

- Don’t chase perfection early. Ship Layer 0 first.
- Don’t tune prompts before retrieval works.
- Don’t self-host models before you can measure latency/cost.
- Don’t read 10 docs. Read the section(s) assigned today.
- If something takes >25 minutes, stop and write a note: “blocked on X”.

## Roadmap coverage (what “done” means)

If you finish the days below, you will also finish `docs/roadmap.md` and have a strong “LLM infra engineer” interview story.

- **Days 1–20 = Layer 0 (single-tenant RAG)**:
  - p95 ≤ 2.0s at 1 QPS (hosted model)
  - 20-case gold set + eval run (faithfulness + context recall targets)
  - citations + refusal rules
  - one-command local run (compose) + screenshots
- **Days 21–30 = Layer 1 (multi-tenant + gateway + tools + traces)**:
  - ≥ 3 tenants with isolated retrieval and metrics
  - p95 ≤ 2.5s at 2–3 QPS
  - OpenTelemetry traces show tool usage and time breakdown clearly
- **Days 31–37 = Layer 2 (serving + batching/cache + routing + FinOps)**:
  - self-hosted inference via **vLLM or TGI** (or equivalent open-model server) and measured results
  - 3–5× throughput gain vs “no batching/no cache” baseline
  - ≥ 70–80% prefix/KV cache hit-rate on seeded repetitive workloads; TTFT hot vs cold is clearly different
  - ≥ 30–40% cost/query reduction using model routing + token budgeting
- **Days 38–40 = Layer 3 (multi-agent workflows + integrations)**:
  - one non-trivial workflow that produces metric-grounded recommendations
  - optional: n8n/LangFlow integration screenshot + export
  - optional: managed backend toggle + recorded latency/cost comparison

**Proof pack (collect as you go)**:
- a table of p50/p95 latency per layer, plus a simple trace screenshot (Layer 1)
- a table of throughput (tokens/sec) baseline vs optimized (Layer 2)
- a table of cost/query before vs after routing (Layer 2)
- one 5-minute demo script (Layer 0/1) and one 60-second pitch (Day 40)

---
# Part 2 — 8-week curriculum (build track)

## Week-by-week map to the roadmap

- **Weeks 1–4 = Layer 0** (single-tenant RAG copilot, evals, latency basics)
- **Weeks 5–6 = Layer 1** (multi-tenant + gateway + agent tools + traces)
- **Week 7 = Layer 2 foundations** (local serving + batching/cache concepts + benchmarks)
- **Week 8 = Layer 2/3** (routing + cost dashboards + multi-agent workflow)

If you complete everything here, you’ll be able to:
- build the system in the roadmap,
- defend the design trade-offs in interviews,
- show hard numbers (quality, latency, cost).

---

# Week 1 — What you are building (and the data you already have)

**Week focus (keep it simple)**:
- Understand the system shape: data → retrieval → answer (with citations).
- Learn the repo data contracts (what fields exist and why).
- All theory reading is listed inside each day’s **Theory** block below (from `docs/learning-fundamentals.md`).

## Day 1 — Read the roadmap like a spec
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 1, Section 2

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Goal**: Treat `docs/roadmap.md` like acceptance criteria, not a blog post.

**Build step**:
- **Roadmap focus**: Layer 0 kickoff (treat `docs/roadmap.md` like a spec).
- Run the deterministic baseline end-to-end:
  1) `python3 level_zero/scripts/generate_level_zero.py --seed 42 --hours 24 --out-dir level_zero/data`
  2) `python3 level_zero/demo-cli-script/qa_cli.py --question "What happened to checkout-api between 10-11am?"`
- Create your Layer 0 proof checklist (in Obsidian): latency target, eval targets, citations, one-command run.
- If short on time: run the CLI once + write the Layer 0 acceptance criteria in your own words.
- Done when: you can restate Layer 0 as **Inputs → Components → Outputs → Metrics** without looking.

**Interview answer**:
- “How do you break down a vague AI project into measurable milestones?”

## Day 2 — Understand the Layer 0 data contracts
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 19, Section 22

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Goal**: Know what is in `level_zero/` and how it connects.

**Build step**:
- **Roadmap focus**: Layer 0 data contracts (your future tools will query these).
- Inspect and summarize the data shapes:
  - `level_zero/data/synthetic_logs.json`
  - `level_zero/data/synthetic_incidents.json`
  - `level_zero/data/hourly_metrics.json`
  - `level_zero/data/cost_summaries.json`
- Write down the *minimum* fields your future tools will need (time window, service, env, tenant).
- If short on time: only do incidents + hourly metrics and list the key fields.
- Done when: you can explain how **logs → incidents → runbooks** connect in this repo.

**Interview answer**:
- “Why do good data contracts matter more than prompts?”

## Day 3 — Run the deterministic CLI baseline (your ‘unit test’)
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 16, Section 9

**Optional (if time)**:
- `docs/learning-fundamentals.md` Section 20

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Goal**: See the “boring baseline” output before adding LLMs.

**Build step**:
- **Roadmap focus**: build a “boring baseline” so you know what “correct” looks like.
- Run 3 deterministic queries (vary service + time window) and save outputs in Obsidian.
- For each query, answer:
  - which incident(s) matched,
  - which runbook(s) were referenced,
  - what the symptoms summary said.
- Write 1 paragraph: “What would the LLM add on top of this baseline?”
- If short on time: run 1 query and write the paragraph.
- Done when: you can explain why you always build a baseline before LLMs.

**Interview answer**:
- “Why build a deterministic baseline before an LLM?”

## Day 4 — HTTP + APIs (minimum you need)
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 21

**Optional (if time)**:
- `docs/learning-fundamentals.md` Section 18, Section 29

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Goal**: Understand the request path for Layer 0 and Layer 1.

**Build step**:
- **Roadmap focus**: start the real request path (even if it’s tiny).
- Create the AI service skeleton (recommended layout):
  - `services/ai-service/` (new)
  - `services/ai-service/app/main.py` (FastAPI app)
- Create a virtualenv + install the minimum deps:
  - `python3 -m venv services/ai-service/.venv`
  - `source services/ai-service/.venv/bin/activate`
  - `pip install fastapi uvicorn[standard]`
- Minimum endpoints:
  - `GET /health` → returns `{ "status": "ok" }`
- Run it locally and verify from terminal:
  - `cd services/ai-service && uvicorn app.main:app --reload --port 8000`
  - `curl http://localhost:8000/health`
- If short on time: only get `/health` working.
- Done when: you can hit `/health` and see a stable JSON response.

**Interview answer**:
- “What responsibilities belong in the gateway vs the AI service?”

## Day 5 — Postgres + pgvector mental model (simple)
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 7, Section 39

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Goal**: Understand what pgvector gives you.

**Plain definition**:
- pgvector lets Postgres store embeddings (number arrays) and do “find the closest ones”.

**Build step**:
- **Roadmap focus**: make retrieval real (Postgres + pgvector).
- Start Postgres with pgvector (docker compose is easiest).
  - Use a pgvector image (example: `pgvector/pgvector:pg16`).
- If you don’t have a compose file yet, create a minimal `docker-compose.yml` at repo root:

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: opspilot
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
```

- Start it:
  - `docker compose up -d postgres`
- In Postgres:
  1) `CREATE EXTENSION IF NOT EXISTS vector;`
  2) Create a `runbook_chunks` table (tenant_id, runbook_id, chunk_index, chunk_text, embedding).
- Verify you can connect from your AI service (even if you don’t query vectors yet).
- If short on time: only bring up Postgres + run `CREATE EXTENSION`.
- Done when: your AI service can connect to Postgres and run a simple `SELECT 1`.

**Interview answer**:
- “Why store embeddings in Postgres instead of a separate vector DB?”

---

# Week 2 — LLM + embeddings + retrieval (the core mechanics)

**Week focus (keep it simple)**:
- Learn what an LLM is (and why it fails).
- Learn embeddings + chunking + top‑k retrieval (the real “core” of RAG).
- All theory reading is listed inside each day’s **Theory** block below (from `docs/learning-fundamentals.md`).

## Day 6 — What an LLM is (no magic)
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 3

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Plain definition**:
- An LLM predicts the next pieces of text. It does not “check reality” unless you give it reality (docs + tool outputs).

**Build step**:
- **Roadmap focus**: make one safe LLM call (hosted baseline).
- Create a tiny “LLM client” wrapper (one file) that:
  - takes `model`, `messages`, `timeout`, `temperature=0`
  - returns `text` + token counts (if available)
- Add one command/test in the AI service that calls the model with a trivial prompt.
- Safety defaults:
  - short timeout,
  - no secrets in logs,
  - no dynamic tool execution yet.
- If short on time: only implement the wrapper and print the response.
- Done when: you can make a hosted LLM call from the service reliably.

**Interview answer**:
- “What causes hallucinations, and how do you reduce them?”

## Day 7 — Tokens, cost, and latency (what you measure)
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 23, Section 30

**Optional (if time)**:
- `docs/learning-fundamentals.md` Section 35

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Plain definition**:
- Tokens are the pieces of text the model reads and writes. More tokens usually means more cost and more time.

**Build step**:
- **Roadmap focus**: cost/latency are first-class (log them from day one).
- Implement request logging for the AI service:
  - request_id, model, input_tokens, output_tokens, total_ms
- Add a simple cost estimate function:
  - `(in_tokens/1000)*price_in + (out_tokens/1000)*price_out`
- Return these fields in your `/ask` response later (even if `/ask` isn’t built yet).
- If short on time: just log `total_ms` + tokens.
- Done when: every LLM call produces one structured log line with tokens and latency.

**Interview answer**:
- “How do you measure and control LLM cost?”

## Day 8 — Embeddings (meaning as numbers)
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 5

**Optional (if time)**:
- `docs/learning-fundamentals.md` Section 32

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Plain definition**:
- Embeddings are numeric fingerprints of meaning. Similar meaning → closer fingerprints.

**Build step**:
- **Roadmap focus**: embeddings are the start of retrieval.
- Add an embeddings client wrapper (same style as LLM wrapper):
  - input text → embedding vector
- Pick 3 runbooks and write 3 queries that should retrieve them.
- Generate embeddings for those 3 queries and store them temporarily (file or in-memory) to sanity check.
- If short on time: only implement the embeddings call and print vector length.
- Done when: you can embed text and you know your embedding dimension (D).

**Interview answer**:
- “Why embeddings beat keyword search for runbooks?”

## Day 9 — Chunking (how you cut docs controls quality)
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 6

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Plain definition**:
- You split a runbook into chunks before embedding. The chunk is what retrieval returns.

**Build step**:
- **Roadmap focus**: chunking decides retrieval quality.
- Implement a first chunker for Markdown runbooks:
  - start with ~300–500 token chunks with overlap (simple heuristic is fine)
  - preserve: runbook_id, section/title, chunk_index
- Run it on 1 runbook and print the produced chunks + metadata.
- If short on time: chunk one runbook by headings (section-based).
- Done when: you can point to a stable chunk ID you would cite in answers.

**Interview answer**:
- “What chunk size works best, and why is the answer ‘it depends’?”

## Day 10 — Retrieval (top‑k + filters)
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 8

**Optional (if time)**:
- `docs/learning-fundamentals.md` Section 11

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Plain definition**:
- Retrieval = embed the query → find top‑k similar chunks → filter by metadata (like tenant/service).

**Build step**:
- **Roadmap focus**: retrieval must be deterministic and tenant-safe.
- Implement `retrieve(query_text, tenant_id, k)`:
  1) embed query
  2) SQL: `WHERE tenant_id = ... ORDER BY embedding <=> :q LIMIT k`
  3) return chunk_text + citation IDs
- Add a debug mode (temporary) that returns retrieved chunk IDs/text without calling the LLM.
- If short on time: retrieval can be single-tenant for now, but keep the `tenant_id` parameter.
- Done when: your 3 test queries return the expected runbook chunks in top‑k.

**Interview answer**:
- “How do you prevent cross-tenant retrieval leakage?”

---

# Week 3 — RAG end-to-end (Layer 0 core)

**Week focus (keep it simple)**:
- Build RAG as an engineering pipeline (not “prompting”).
- Learn citations, refusal rules, and the fix order for failures.
- All theory reading is listed inside each day’s **Theory** block below (from `docs/learning-fundamentals.md`).

## Day 11 — RAG in one sentence
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 8

**Optional (if time)**:
- `docs/learning-fundamentals.md` Section 9

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Plain definition**:
- RAG = search your docs first, then answer using only what you found.

**Build step**:
- **Roadmap focus**: first end-to-end RAG answer with citations.
- Implement `/ask` (single-tenant is fine today):
  1) retrieve top‑k chunks
  2) build a prompt with rules + context + question
  3) call the hosted LLM
  4) return answer + citations
- Add a strict rule: “no citations → refuse or ask clarifying question”.
- If short on time: return citations even if the answer text is basic.
- Done when: one request returns an answer with at least 1–2 correct citations.

**Interview answer**:
- “What does ‘grounded answer’ mean?”

## Day 12 — Prompt template (simple and strict)
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 3, Section 21

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Goal**: A prompt is a format, not a trick.

**Build step**:
- **Roadmap focus**: turn prompts into contracts (structured output).
- Define an output schema for `/ask` (example fields):
  - `summary`, `root_cause_hypothesis`, `recommended_actions[]`, `citations[]`, `confidence`
- Update the prompt to demand JSON only and parse/validate the response.
- Add a fallback: if JSON parsing fails, retry once or return a safe error.
- If short on time: only enforce JSON + validate required fields.
- Done when: `/ask` always returns valid JSON (or a safe error) and never free-text.

**Interview answer**:
- “Why structured output helps reliability?”

## Day 13 — Citations (your debugging tool)
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 6, Section 21

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Goal**: Every answer should show “where it came from”.

**Build step**:
- **Roadmap focus**: citations must be stable and debuggable.
- Pick one citation format and implement it everywhere (examples):
  - `runbook_path#section#chunk_index`
  - `runbook_id:chunk_index`
- Ensure citations map to stored chunks (no “fake” citations).
- Add a “show sources” debug option that returns the cited chunk texts.
- If short on time: implement stable IDs even if you don’t return full chunk text.
- Done when: you can click a citation and find the exact chunk used.

**Interview answer**:
- “Why citations reduce hallucinations and improve trust?”

## Day 14 — Failure modes (fix retrieval before prompts)
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 8

**Optional (if time)**:
- `docs/learning-fundamentals.md` Section 5

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Common failures**:
- wrong chunks retrieved,
- right chunks retrieved but answer ignores them,
- docs missing.

**Build step**:
- **Roadmap focus**: fix retrieval before prompts (make failures visible).
- Add 3 “failure drills” and record what broke:
  1) question with missing docs,
  2) question with ambiguous service/time,
  3) question that should retrieve but doesn’t.
- Implement the fix-order checklist in code comments or a short dev note:
  - metadata/filters → chunking → retrieval params → prompt → model
- If short on time: do only drill #1 and implement safe refusal.
- Done when: the system refuses safely instead of guessing when sources are missing.

**Interview answer**:
- “Why prompt engineering is usually not the first fix?”

## Day 15 — Minimal FastAPI design for Layer 0
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 21

**Optional (if time)**:
- `docs/learning-fundamentals.md` Section 25

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Goal**: Keep the API tiny.

**Build step**:
- **Roadmap focus**: minimal API surface + ingestion entry point.
- Implement the endpoints for real:
  - `GET /health`
  - `POST /ingest/runbooks` (reads Markdown runbooks, chunks, embeds, stores)
  - `POST /ask`
- Start with `level_zero/knowledge_base/runbooks/` as your ingestion input.
- If short on time: implement ingestion as a CLI script that calls your ingestion code.
- Done when: one command ingests runbooks and `/ask` works afterwards.

**Interview answer**:
- “What’s the smallest API that still supports evaluation and iteration?”

---

# Week 4 — Evaluation + latency (Layer 0 acceptance criteria)

**Week focus (keep it simple)**:
- Turn “it feels good” into evals.
- Turn “it seems slow” into measured p50/p95 and trace spans.
- All theory reading is listed inside each day’s **Theory** block below (from `docs/learning-fundamentals.md`).

## Day 16 — Gold set (20 questions) = your test suite
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 9

**Optional (if time)**:
- `docs/learning-fundamentals.md` Section 25

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Goal**: Replace “feels good” with repeatable checks.

**Build step**:
- **Roadmap focus**: build the gold set (your test suite).
- Create a 20-case gold set file (example path): `evals/layer0_goldset.json`.
  - each case: question, time window/service (if needed), expected runbook IDs, expected key points
- Keep questions realistic (incidents + cost + latency).
- If short on time: create 10 cases today and finish the rest tomorrow.
- Done when: you have a file you can run repeatedly after every change.

**Interview answer**:
- “How do you evaluate RAG without fooling yourself?”

## Day 17 — Simple scoring rubric (start manual)
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 9, Section 25

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Goal**: You can start without fancy tools.

**Build step**:
- **Roadmap focus**: define scoring so you can detect regressions.
- Implement a simple eval runner script (example path): `evals/run_eval.py` that:
  1) calls `/ask` for each gold question
  2) records citations retrieved
  3) records output JSON
- Implement at least 2 metrics:
  - retrieval recall@k (did expected runbook appear?)
  - faithfulness proxy (judge model or rubric)
- If short on time: do recall@k only (it catches the biggest failures).
- Done when: you can run one command and get a score table.

**Interview answer**:
- “What does ‘faithfulness’ mean in practice?”

## Day 18 — Latency basics (p50 vs p95)
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 20, Section 23

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Plain definition**:
- p95 latency: 95% of requests are faster than this time.

**Build step**:
- **Roadmap focus**: hit Layer 0 latency target (p95 ≤ 2s at 1 QPS).
- Add a tiny load test (any one):
  - a Python script that sends 50–100 requests at 1 QPS, or `hey`/`vegeta`.
- Record:
  - p50, p95 total latency
  - p95 retrieval_ms and llm_ms (if you log them)
- If p95 is too high, apply fixes in this order:
  1) reduce prompt/context tokens
  2) reduce `k`
  3) tighten tool/retrieval timeouts
- If short on time: run 20 requests and compute p95 manually.
- Done when: you can show p95 ≤ 2.0s at 1 QPS (hosted model).

**Interview answer**:
- “Why tail latency matters for user experience and scaling?”

## Day 19 — Instrumentation plan (what you will measure)
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 10

**Optional (if time)**:
- `docs/learning-fundamentals.md` Section 29

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Goal**: Make performance and cost visible.

**Build step**:
- **Roadmap focus**: make the system observable (so you can debug).
- Implement structured logging for every `/ask` request:
  - request_id, tenant_id, model, tokens_in/out, retrieval_ms, llm_ms, total_ms
- Add OpenTelemetry instrumentation plan to code (spans you will create):
  - `ai.request`, `ai.retrieve`, `ai.llm`, `db.vector_search`
- If short on time: at least log retrieval_ms vs llm_ms separately.
- Done when: one request produces enough data to explain where time went.

**Interview answer**:
- “How do you debug slow LLM requests?”

## Day 20 — Layer 0 ‘done’ checklist (ship it)
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 35, Section 40

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Goal**: Your Layer 0 should be demo-ready.

**Build step**:
- **Roadmap focus**: Layer 0 ship + proof pack.
- Run your Layer 0 demo script (5 minutes) and record:
  - one good answer with citations
  - one eval run output (scores)
  - one latency run output (p95)
- Create “one command local run” (compose) for:
  - Postgres + AI service
- If short on time: capture the demo + p95 numbers.
- Done when: you can meet Layer 0 acceptance criteria and explain your metrics.

**Interview answer**:
- “How do you turn an AI prototype into something demoable and measurable?”

### Layer 0 acceptance checklist (from `docs/roadmap.md`)

- [ ] Latency: p95 ≤ 2.0s at 1 QPS (hosted model) and you saved the numbers.
- [ ] RAG eval: 20-case gold set exists and you can re-run it any time.
- [ ] RAG eval: you measured **Answer Faithfulness ≥ 0.7** and **Context Recall ≥ 0.8** (RAGAS or similar).
- [ ] Citations: answers include stable citations; “no sources → refuse/ask”.
- [ ] One-command run: `docker compose up` (or equivalent) runs Postgres + AI service locally.
- [ ] Docs: README includes an architecture diagram + a screenshot of a working answer with citations.

---

# Week 5 — Multi-tenancy + Spring Boot gateway (Layer 1 core)

**Week focus (keep it simple)**:
- Add tenant isolation and a gateway (auth + routing + observability tags).
- Learn the “never leak tenant data” rules.
- All theory reading is listed inside each day’s **Theory** block below (from `docs/learning-fundamentals.md`).

## Day 21 — Multi-tenant rules (non-negotiable)
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 11, Section 24

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Goal**: Prevent “tenant A sees tenant B”.

**Build step**:
- **Roadmap focus**: Layer 1 multi-tenancy (hard security boundary).
- Add `tenant_id` everywhere (no default tenant):
  - request header → app context → DB queries → cache keys
- Ingest multi-tenant runbooks/data (use `multi-tenant/` datasets).
- Add one automated “leak test”:
  - query as tenant A must never return tenant B citations.
- If short on time: enforce tenant_id in every retrieval query.
- Done when: you can run the same question for 2 tenants and get different sources.

**Interview answer**:
- “How do you prove tenant isolation?”

## Day 22 — API keys (start simple)
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 21, Section 27

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Goal**: Basic auth that is easy to reason about.

**Build step**:
- **Roadmap focus**: gateway auth (simple, correct, and safe).
- Implement API key auth in the gateway (or AI service if gateway not ready yet):
  - `X-API-Key` → maps to `tenant_id`
- Security rules:
  - never log API keys
  - return 401/403 correctly
- Add a tiny “auth test”:
  - missing key → 401
  - wrong key → 403
  - correct key → 200
- If short on time: implement the auth middleware/filter first.
- Done when: tenant_id is derived from the key and cannot be overridden by the caller.

**Interview answer**:
- “What should you never log in an auth system?”

## Day 23 — Gateway responsibilities (why it exists)
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 16, Section 23

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Gateway does**:
- auth, tenant selection, rate limits, routing, tracing.

**AI service does**:
- RAG, tools, agent logic, citations.

**Build step**:
- **Roadmap focus**: gateway vs AI service separation.
- Scaffold Spring Boot gateway (minimal):
  - `/health`
  - `/ask` (proxy to AI service)
- Gateway responsibilities today:
  - authenticate, set tenant_id, forward request_id/trace headers
- If short on time: implement a simple proxy that forwards `/ask` to the AI service.
- Done when: CLI → gateway → AI service → Postgres works end-to-end.

**Interview answer**:
- “Why keep the gateway separate from the AI service?”

## Day 24 — Tenant-aware pgvector design
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 37, Section 39

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Goal**: Make isolation hard to get wrong.

**Build step**:
- **Roadmap focus**: tenant-safe pgvector at “real” shape.
- Enforce tenant filtering in SQL:
  - `WHERE tenant_id = :tenant`
- Run `EXPLAIN (ANALYZE, BUFFERS)` on your retrieval query and confirm:
  - index usage (or understand why not)
- Decide your isolation strategy:
  - one table + filter (simple) or partition per tenant (predictable)
- If short on time: just run EXPLAIN and save the plan output.
- Done when: you can explain your retrieval plan and why it’s safe.

**Interview answer**:
- “What are safe defaults for multi-tenant retrieval storage?”

## Day 25 — Layer 1 ‘done’ skeleton
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 26, Section 28

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Goal**: Minimal end-to-end multi-tenant call.

**Build step**:
- **Roadmap focus**: Layer 1 skeleton demo.
- Support ≥ 3 tenants:
  - `tenant-alpha`, `tenant-beta`, `tenant-gamma`
- For each tenant, run 1 question through the gateway and verify:
  - citations are tenant-scoped
  - response includes decision_trace placeholder (even empty)
- If short on time: get 2 tenants working, then add the third.
- Done when: multi-tenant request routing works reliably.

**Interview answer**:
- “What makes a system ‘production-shaped’ even at low scale?”

---

# Week 6 — Agents + tools + observability (Layer 1 interview-grade)

**Week focus (keep it simple)**:
- Make the system fetch facts via tools.
- Make the agent debuggable (decision traces + OTEL traces).
- All theory reading is listed inside each day’s **Theory** block below (from `docs/learning-fundamentals.md`).

## Day 26 — Tools (LLM should fetch facts, not guess facts)
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 12

**Optional (if time)**:
- `docs/learning-fundamentals.md` Section 21

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Goal**: Tools turn “chat” into “system”.

**Build step**:
- **Roadmap focus**: tools (fetch facts, don’t guess facts).
- Implement 3 tools (as functions or endpoints) with strict inputs:
  1) `get_metric_timeseries(service, metric, window, tenant)`
  2) `get_top_errors(service, window, tenant)`
  3) `search_runbooks(query, tenant)`
- Enforce:
  - time window bounds
  - tenant_id required
  - timeouts
- If short on time: implement `search_runbooks` first (it powers RAG).
- Done when: tools return JSON that you can include in prompts.

**Interview answer**:
- “How do tools reduce hallucinations?”

## Day 27 — Agent flow (simple graph)
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 12, Section 15

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Goal**: A reliable sequence beats freestyle reasoning.

**Build step**:
- **Roadmap focus**: agent flow (predictable, not “freestyle”).
- Implement a simple diagnose flow (LangGraph recommended, manual is OK):
  1) classify query (latency vs errors vs cost)
  2) call the right tool(s)
  3) retrieve runbooks
  4) synthesize RCA + actions
  5) output decision_trace
- If short on time: hard-code the classifier rules (keyword-based) for now.
- Done when: you can see the tool call order for one request.

**Interview answer**:
- “Why use a graph-based flow for agents?”

## Day 28 — Decision traces (make the agent debuggable)
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 10, Section 12

**Optional (if time)**:
- `docs/learning-fundamentals.md` Section 24

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Goal**: Every answer should explain how it was built.

**Build step**:
- **Roadmap focus**: decision traces (debuggability).
- Define and return a `decision_trace` JSON object that includes:
  - tool calls (name, inputs, latency)
  - short summaries of tool outputs
  - retrieval results (top‑k citations)
- Add redaction rules:
  - don’t store secrets/PII in traces
- If short on time: include only tool names + durations.
- Done when: you can explain “how the answer was built” from the trace alone.

**Interview answer**:
- “How do you debug an agent that made a bad call?”

## Day 29 — OpenTelemetry (what it gives you)
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 10

**Optional (if time)**:
- `docs/learning-fundamentals.md` Section 27

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Plain definition**:
- Tracing shows one request across services with timings (gateway → AI → DB → LLM).

**Build step**:
- **Roadmap focus**: OpenTelemetry end-to-end.
- Instrument both services (gateway + AI service) with OTEL tracing.
- Required spans (minimum):
  - `gateway.request`, `ai.request`, `ai.tool.*`, `db.vector_search`, `ai.llm`
- Run a local OTEL+Grafana stack (compose) and verify traces show:
  - which tool(s) were called
  - where time was spent
- If short on time: instrument AI service only, then add gateway propagation tomorrow.
- Done when: Grafana/Tempo shows one full trace for `/ask`.

**Interview answer**:
- “How do you find where latency is coming from?”

## Day 30 — Layer 1 acceptance criteria
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 20, Section 10

**Optional (if time)**:
- `docs/learning-fundamentals.md` Section 16

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Goal**: Match the roadmap.

**Build step**:
- **Roadmap focus**: Layer 1 acceptance proof.
- Run a low-load test at 2–3 QPS and record p95 (target ≤ 2.5s).
- Verify:
  - ≥ 3 tenants work
  - traces clearly show tool calls + timings
- Create 1 screenshot (trace view) and save it for your proof pack.
- If short on time: run 2 QPS for a smaller number of requests and capture one trace.
- Done when: you can demonstrate Layer 1 “production-shaped” behavior.

**Interview answer**:
- “What does a good ‘done’ definition look like for an LLM platform feature?”

### Layer 1 acceptance checklist (from `docs/roadmap.md`)

- [ ] Tenants: ≥ 3 tenants with distinct runbooks + data (`tenant-alpha`, `tenant-beta`, `tenant-gamma`).
- [ ] Isolation: tenant_id required on every request; retrieval/tools never cross tenants.
- [ ] Latency: p95 ≤ 2.5s at 2–3 QPS (low-load test) and you saved the numbers.
- [ ] Traces: Grafana shows tool calls and clearly separates vector time vs LLM time.
- [ ] Gateway: API key auth + tenant routing + request tagging (tenant_id, model, route).

---

# Week 7 — Layer 2 foundations (serving, batching, cache, benchmarks)

**Week focus (keep it simple)**:
- Learn the real infra knobs: batching, KV cache, routing, benchmarking.
- Replace claims with measurements (tokens/sec, p95, cost/query).
- All theory reading is listed inside each day’s **Theory** block below (from `docs/learning-fundamentals.md`).

### GPU lab (budget-safe) — do Days 31–35 with minimal confusion

You said you’re willing to rent a GPU, but you don’t want to burn money or get lost.
This is a “copy/paste + guardrails” plan.

**Budget guardrails (do these first)**:
- Decide a hard cap: `$10` (or `$20`) for the whole Layer 2 experiment. Write it down.
- Pick an instance billed **per-hour** (or per-minute) with **no long minimum**. Avoid monthly subscriptions.
- Set an auto-stop timer in the provider UI. Extra safety on the VM: `sudo shutdown -h +150` (auto-poweroff in 150 minutes).
- Don’t expose ports to the internet. For this lab: benchmark from the **same GPU VM** and use `127.0.0.1`.
- When done: **stop the VM** and confirm billing stopped. If storage keeps charging, delete the volume too.

**Recommended GPU choice (cheap + low confusion)**:
- Best balance: **L4 (24GB)** or **A10 (24GB)**.
- Ultra-cheap fallback: **T4 (16GB)** (use a 3B model and short context).

**Recommended model for the lab**:
- Start with: `Qwen/Qwen2.5-3B-Instruct` (small, open, fast to download)
- Upgrade later (optional): `Qwen/Qwen2.5-7B-Instruct` on 24GB GPUs (keep context small)

**Remote GPU setup checklist (vLLM path)**:
1) Create a GPU VM:
   - Ubuntu 22.04 (or similar)
   - NVIDIA drivers work (`nvidia-smi`)
   - Docker works (`docker ps`)
2) Verify GPU:
   - `nvidia-smi`
3) Pull vLLM:
   - `docker pull vllm/vllm-openai:latest`
4) Start the server (bound to localhost only):
   - `docker run --gpus all --rm --ipc=host -p 127.0.0.1:8000:8000 vllm/vllm-openai:latest --model Qwen/Qwen2.5-3B-Instruct --dtype half --max-model-len 2048 --host 0.0.0.0 --port 8000`
5) Smoke test (from the same VM):
   - `curl -s http://127.0.0.1:8000/v1/models | head`

If you want to call the server from your laptop (optional, safer than opening firewall):
- `ssh -L 8000:127.0.0.1:8000 <user>@<vm-ip>`

If you get stuck on flags:
- Run `docker run --rm vllm/vllm-openai:latest --help | grep -iE "cache|prefix|batch|len|max-model-len"` and use the exact flag names shown.

**Minimal measurements to record (you’ll use these in Days 31–35)**:
- Baseline vs improved: `tokens/sec`, `p95 latency`
- Cache proof: `TTFT hot vs cold` (approx) and, if available, `prefix-cache hit-rate`

**TTFT (approx = first-byte time)** — run once (cold), then a few times (hot):

```bash
for i in 1 2 3 4 5; do
  curl -s -o /dev/null \
    -w "ttfb_s=%{time_starttransfer} total_s=%{time_total}" \
    http://127.0.0.1:8000/v1/chat/completions \
    -H 'Content-Type: application/json' \
    -d '{"model":"Qwen/Qwen2.5-3B-Instruct","messages":[{"role":"user","content":"You are an SRE. Explain the same 3 steps to debug a 5xx spike. Use short bullets."}],"max_tokens":128,"temperature":0,"stream":true}'; echo
done
```

**Baseline vs batching throughput** (standard library Python, no installs):

```bash
python3 - <<'PY'
import json, time, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

endpoint = "http://127.0.0.1:8000/v1/chat/completions"
payload = {
  "model": "Qwen/Qwen2.5-3B-Instruct",
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
  return dt, int(usage.get("prompt_tokens", 0)), int(usage.get("completion_tokens", 0))

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
  tps = (pt+ct)/wall if wall>0 else 0
  print(f"concurrency={concurrency} requests={total} wall_s={wall:.2f} p95_s={p95:.2f} tokens_per_s={tps:.1f} prompt={pt} completion={ct}")

for c in (1, 8):
  bench(concurrency=c, total=c*10)
PY
```

**Cache metrics (if exposed by vLLM)**:
- `curl -s http://127.0.0.1:8000/metrics | grep -iE "ttft|prefix|cache|prompt_tokens|generated_tokens" | head`

**Important cost saver**:
- Model download time costs money. Start the VM, download once, run benchmarks, then shut down.

## Day 31 — Serving: why Layer 2 exists
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 13

**Optional (if time)**:
- `docs/learning-fundamentals.md` Section 36

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Goal**: Turn “LLM calls” into “LLM infra”.

**Build step**:
- **Roadmap focus**: self-hosted inference start (Layer 2).
- Preferred: follow the “GPU lab” section above (vLLM path) until `curl -s http://127.0.0.1:8000/v1/models | head` works.
- Local fallback (if you can’t rent a GPU today): Ollama (you still learn routing/caching, but not full vLLM batching).
- Run one real chat completion and confirm the response includes `usage` (token counts).
- Record a baseline:
  - run the “Baseline vs batching throughput” snippet with `concurrency=1`
  - save `tokens/sec` and `p95 latency`
- If short on time: just get `/v1/models` to respond from the GPU VM.
- Done when: your AI service can switch providers via config (hosted vs self-host) and still answers one question end-to-end.

**Interview answer**:
- “When do you self-host vs use a managed model?”

## Day 32 — Continuous batching (micro-batching for LLMs)
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 13, Section 35

**Optional (if time)**:
- `docs/learning-fundamentals.md` Section 32

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Plain definition**:
- The server groups requests so the GPU stays busy and total throughput increases.

**Build step**:
- **Roadmap focus**: continuous batching throughput gain.
- On the GPU VM, run the “Baseline vs batching throughput” snippet from the GPU lab section.
- Treat `concurrency=1` as baseline and `concurrency=8` as batching load (drop to 4 if you hit timeouts).
- Record `tokens/sec` and `p95 latency` for both.
- If short on time: run only the higher concurrency case and save `tokens/sec`.
- Done when: you can show a clear throughput improvement and explain why latency can get worse.

**Interview answer**:
- “Why can batching increase throughput by multiple times?”

## Day 33 — KV/prefix cache (why repeated prompts get faster)
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 13, Section 35

**Optional (if time)**:
- `docs/learning-fundamentals.md` Section 34

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Plain definition**:
- If the beginning of prompts repeats, the server can reuse work instead of recomputing it.

**Build step**:
- **Roadmap focus**: KV/prefix cache (TTFT hot vs cold).
- Create a seeded workload where the prompt prefix repeats (same system prompt + template).
- Use the “TTFT (approx)” curl loop from the GPU lab section and record:
  - cold (first run after server start)
  - hot (repeated runs)
- If hot is not faster: check vLLM `--help` for a prefix-cache flag, restart vLLM with it, and re-run.
- If `/metrics` works: grep for `prefix|cache|ttft` counters and record the hit-rate or the raw counters.
- If short on time: record only cold vs hot numbers.
- Done when: you can show “hot is faster than cold” with numbers and explain what is being reused.

**Interview answer**:
- “What is TTFT and why do users feel it?”

## Day 34 — Routing for cache locality (gateway-level)
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 14, Section 23

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Goal**: Same prefixes → same shard → more cache hits.

**Build step**:
- **Roadmap focus**: routing for cache locality.
- Implement a router in the gateway:
  - compute a stable `routing_key = (tenant_id + prompt_template_version + prompt_prefix_hash)`
  - pick a backend shard by hashing the routing_key (or rendezvous hashing)
- Tag + log every request with: `tenant_id`, `routing_key`, `shard_id`, `fallback=true/false`.
- Optional (only if you have enough VRAM): run 2 vLLM servers on the same VM (ports 8000 and 8001) so routing changes cache hit behavior in a visible way.
- Add a safe fallback: if a shard fails, retry on another shard and mark `fallback=true`.
- If short on time: route by `tenant_id` only and make sure you can see shard_id in traces/logs.
- Done when: the same tenant+template maps to the same shard and you can explain why this improves cache hits without breaking correctness.

**Interview answer**:
- “How do you design routing without breaking correctness?”

## Day 35 — Benchmark plan (prove improvements)
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 35, Section 16

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Goal**: No claims without measurements.

**Build step**:
- **Roadmap focus**: benchmark report (prove 3–5×).
- Run the two GPU lab measurements and save the outputs:
  - throughput snippet (`concurrency=1` vs `concurrency=8`)
  - TTFT loop (cold vs hot)
- If `/metrics` exposes cache counters, record them and compute hit-rate.
- Do one back-of-envelope cost calc from your GPU price:
  - `$ per second = ($ per hour) / 3600`
  - `$ per 1M tokens ≈ ($ per second / tokens_per_second) * 1_000_000`
- Produce a small report (table + 5 bullets) in your proof pack:
  - baseline vs optimized throughput, p95, TTFT cold/hot, cache hit-rate, $/1M tokens
- Target (roadmap): 3–5× throughput gain vs baseline.
- If short on time: record the best tokens/sec you saw and stop the GPU VM.
- Done when: you can defend your benchmark as fair (same workload, same model, only one knob changed) and you stopped billing.

**Interview answer**:
- “How do you run fair performance experiments?”

---

# Week 8 — Routing + cost + Layer 3 workflows (finish future-proof)

**Week focus (keep it simple)**:
- Learn cost control and safe routing.
- Learn how to talk about fine-tuning and training cost (even if you don’t train foundation models).
- All theory reading is listed inside each day’s **Theory** block below (from `docs/learning-fundamentals.md`).

## Day 36 — Model cascade (small model vs big model)
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 14

**Optional (if time)**:
- `docs/learning-fundamentals.md` Section 31

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Plain definition**:
- Easy requests go to a cheaper model; hard requests go to a stronger model.

**Build step**:
- **Roadmap focus**: model cascade (cheap-first routing).
- Implement a routing rule:
  - easy queries → small/cheap model
  - hard/ambiguous → bigger model
- Add a quality gate:
  - if citations missing / low confidence → escalate to bigger model
- If short on time: route by a simple heuristic (question length + keywords).
- Done when: you can show % of queries handled by small model without quality drop.

**Interview answer**:
- “How do you route safely without harming answer quality?”

## Day 37 — Cost dashboards (FinOps for LLM requests)
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 30, Section 35

**Optional (if time)**:
- `docs/learning-fundamentals.md` Section 41

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Goal**: You cannot manage cost without request tagging.

**Build step**:
- **Roadmap focus**: FinOps dashboards (cost per tenant).
- Log/emit metrics per request:
  - tenant_id, model, route, in/out tokens, estimated cost
- Build a Grafana dashboard (minimum panels):
  - cost per tenant (daily)
  - % requests by route/model
  - avg tokens in/out
- Target (roadmap): 30–40% cost/query reduction using routing + token budgeting.
- If short on time: output a CSV/table (tenant → cost/query) and screenshot it.
- Done when: you can answer “what did tenant X spend yesterday?” from your data.

**Interview answer**:
- “How do you attribute LLM spend per tenant/team?”

### Layer 2 acceptance checklist (from `docs/roadmap.md`)

- [ ] Self-hosted inference: open model running via vLLM or TGI and you can route traffic to it.
- [ ] Throughput: baseline vs optimized benchmark shows **3–5×** improvement (same workload).
- [ ] Cache: ≥ 70–80% hit-rate on seeded repetitive workload and TTFT hot vs cold is clearly different.
- [ ] Routing: model cascade + token budgeting reduces avg cost/query by **30–40%** vs “single big model”.
- [ ] FinOps: dashboards show cost per model, cost per tenant, and % requests routed cheap vs expensive.
- [ ] Evidence: you saved the benchmark table + one screenshot of the dashboard.

## Day 38 — Layer 3 multi-agent workflow (cost-cutting example)
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 12, Section 15

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Goal**: Show you can build a real workflow, not just Q&A.

**Build step**:
- **Roadmap focus**: Layer 3 workflow (multi-agent).
- Implement the “cut infra cost by 20%” workflow (minimum):
  1) planner chooses time window + targets
  2) metrics agent pulls cost/usage signals
  3) finops agent proposes actions
  4) reporter generates final report (with numbers)
- Keep everything tenant-scoped.
- If short on time: implement it as one orchestrated flow (not separate processes), but keep the roles in the output.
- Done when: you can run it and get a non-trivial, metric-grounded report.

**Interview answer**:
- “What makes multi-agent workflows useful (and what makes them risky)?”

## Day 39 — Memory (persistence) in plain terms
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 17, Section 38

**Optional (if time)**:
- `docs/learning-fundamentals.md` Section 41, Section 33

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Plain definition**:
- Memory is saved state: past recommendations, outcomes, decisions, per tenant.

**Build step**:
- **Roadmap focus**: memory/persistence (make workflows improve over time).
- Create a Postgres table for recommendations:
  - tenant_id, timestamp, recommendation, expected_savings, outcome
- Update the workflow to:
  - read the last N recommendations
  - avoid repeating bad advice
- Safety rules:
  - tenant isolation
  - retention limits
- If short on time: store only the last 10 recommendations per tenant.
- Done when: today’s report can reference what it recommended last time.

**Interview answer**:
- “When is memory helpful vs dangerous?”

## Day 40 — Final interview story (what you will demo)
**Theory (10–15 min)**:
- `docs/learning-fundamentals.md` Section 16, Section 40

**Optional (if time)**:
- `docs/learning-fundamentals.md` Section 28

**Core interview questions (5–10 min)**:
- Answer the **Core (must)** questions at the end of each section above.
- If you are short on time: read **Must know (fast path)** and answer only Core Q1–Q3.


**Build step**:
- **Roadmap focus**: final proof pack + interview story.
- Prepare:
  - a 60-second pitch
  - a 5-minute demo script
  - 3 hard numbers (quality, latency, cost) with screenshots/tables
- Make sure you can answer:
  - “how do you know it’s correct?”
  - “how do you know it’s fast?”
  - “how do you know it’s cheap?”
- If short on time: write the pitch + pick the 3 numbers.
- Done when: you can demo Layer 0/1 live and defend Layer 2 numbers confidently.

**Interview answer**:
- “What did you build, what trade-offs did you choose, and how did you measure success?”

### Layer 3 acceptance checklist (from `docs/roadmap.md`)

- [ ] Workflow: a multi-step “cost cutting” (or incident) workflow produces non-trivial, metric-grounded recommendations.
- [ ] Persistence: per-tenant memory exists (even simple Postgres table) and is used safely.
- [ ] Optional integration: n8n/LangFlow node/flow exists and you saved one screenshot + export.
- [ ] Optional managed toggle: config flag switches between self-hosted and managed model backend, and you recorded latency/cost comparison.
- [ ] Evidence: you can demo the workflow end-to-end in <10 minutes.

---
