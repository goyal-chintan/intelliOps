# OpsPilot Roadmap (Staff-level, production-shaped)

This is the **canonical build spec** for the repo.

Plain-English map (no ambiguity):

- `docs/roadmap.md` (this file) = **what to build** + **pass/fail gates**
- `docs/learning-book.md` = **what to do today** (reading + coding, time-boxed)
- `docs/learning-fundamentals.md` = **the “textbook”** (definitions, mental models, math, interview questions)
- `docs/hints/` = **optional help** (rationale + copy/paste playbooks)

You are not “learning random AI stuff”. You are building one project, in layers, and collecting proof artifacts as you go.

## Your constraints (baked into this plan)

- You are a beginner in LLM frameworks.
- You have **~90 minutes/day**:
  - ~45 min deep fundamentals (theory + math + interview questions)
  - ~45 min building (agent‑assisted coding + your review)
- You want something that looks like a real production system and can be defended in Staff/Senior interviews.
- MacBook M2 Pro, Postgres + pgvector.
- Optional: **Week 6** one-evening cloud GPU smoke test (vLLM) if you feel confident.

## What “Staff LLM Platform Engineer” means (practically)

You don’t need to compete with ML researchers. The Staff platform bar is:

- Make LLM systems **safe, fast, cheap, reliable, observable, and governable**.
- Design the control plane: **tenancy, auth, budgets, routing, quotas**.
- Build tool infrastructure: **tool registry, approvals, audit logs, sandboxing**.
- Treat evals as a **release gate** (quality regressions block shipping).
- Operate failure: timeouts, retries, partial outages, incident drills.

## Defaults (keep it simple)

These are the defaults we will use so you don’t get distracted:

- API: `POST /ask` returns **schema-valid JSON**
- Services: Python AI service (FastAPI) + Spring Boot gateway
- Storage: Postgres + pgvector
- Local inference (Mac): **Ollama** (default)
- Alternative local inference (Mac): `llama.cpp` server (optional)
- Tools boundary: MCP
- Optional (Week 6): cloud GPU smoke test (vLLM)

Canonical “why + alternatives + interview talk-track”: `docs/decisions/roadmap-decisions.md`

## Layers (0 → 3)

Each layer is a **shippable bar** with measurable pass/fail gates. This is how you avoid “surface-level learning”.

Important: we are keeping the **same layers** as the original roadmap — we are only making each layer more “production-shaped” (testable, measurable, safe).

### Layer 0 — Understandable demo (baseline → single-tenant RAG)

**Goal**: A single-tenant copilot that can answer incident/cost questions with citations, plus a baseline you can trust.

**Deliverables**

- Deterministic dataset + CLI baseline (`level_zero/`).
- Postgres + pgvector retrieval over runbooks/docs.
- `POST /ask` (AI service) that returns **schema-valid JSON**:
  - `summary`, `hypotheses[]`, `evidence[]`, `actions[]`, `risk_level`
- First gold set (20 cases) + eval harness you can re-run.
- Basic request logging (tokens + retrieval_ms + llm_ms + total_ms).

**Pass/Fail gates**

- One-command run works locally (DB + AI service).
- Answers include stable citations (no sources → refuse/ask).
- Eval harness runs and you saved a baseline score.
- You recorded p50/p95 latency once (don’t optimize yet; just measure).

**Interview prompts you must be able to answer**

- Why build a deterministic baseline before “trusting” an LLM?
- What breaks RAG in production, and how do you detect it quickly?

### Layer 1 — Production-shaped RAG (gateway + tools + observability)

**Goal**: Something a real team could safely expose internally (even single‑tenant) with correct controls and proof.

**Deliverables**

- Spring Boot gateway:
  - API key auth (start single‑tenant)
  - rate limits + concurrency caps
  - basic budgets/quotas (fail closed)
  - audit log (who asked what, which sources/tools were used)
- “Tools” that fetch facts (even if implemented as simple internal functions first):
  - metrics query
  - log search
  - incident/event lookup
- Observability:
  - OpenTelemetry traces across gateway → AI service → DB
  - one dashboard that shows where time is spent
- Evals as a gate:
  - a “ship/no‑ship” threshold you can defend (and re-run)

**Pass/Fail gates**

- 401/403 auth behavior is correct and API keys never get logged.
- Traces make it obvious where time is spent (retrieve vs generate vs tools).
- A regression in your gold set blocks shipping (even if the threshold is simple).

**Interview prompts you must be able to answer**

- What do you log, what do you never log, and why?
- Where do you enforce policy (gateway vs AI service), and why?

### Layer 2 — LLM infra excellence (local inference, caching/batching, routing, cost)

**Goal**: Show real engineering: measurement → change → measured improvement.

**Deliverables**

- Local inference on Mac:
  - run Ollama locally and call it via OpenAI-compatible API
  - (optional) run a `llama.cpp` server for more low-level control
  - document the exact model + settings you used
- Benchmark harness + reports:
  - throughput/latency curve vs concurrency
  - tokens in/out per request
  - “cost estimate per request” (math, even if local is $0)
- At least two optimizations with measured deltas:
  - caching (prompt/prefix or retrieval)
  - batching (where applicable)
  - (optional) speculative decoding (measure; don’t assume)
- Cost controls:
  - per-tenant budgets/quotas enforced
  - routing/model cascade (cheap-first, big model only when needed)
  - cost dashboards (per tenant, per model)

**Pass/Fail gates**

- You show ≥ 2 measured improvements (your machine decides the scale).
- You can explain trade-offs (latency vs throughput vs quality vs cost).

**Interview prompts you must be able to answer**

- How do you capacity plan from tokens/sec and concurrency?
- When does caching backfire (privacy, staleness, correctness)?

### Layer 3 — Agentic ecosystem (MCP), hardening, and optional cloud GPU smoke test

**Goal**: Prove you can build tool-using agents safely and operate them.

**Deliverables**

- MCP server(s) exposing your tools (read-only by default):
  - `events_search(query)`
  - `metrics_query(query)`
  - `log_search(query)`
  - `cost_estimate(service, window)`
- Agent loop: plan → tool call → validate tool output → final answer with citations.
- Tool governance:
  - per-tenant allowlists
  - timeouts + max rows
  - no silent actions (audit everything)
- Threat model doc: prompt injection + data exfil + tool abuse + mitigations.
- Failure drills:
  - tool outage
  - DB slow
  - model timeout

**Optional (Week 6, if you feel confident)**

- One-evening cloud GPU smoke test to prove portability:
  - stand up vLLM and run your bench harness once
  - show “same API adapter, different backend” (don’t claim multipliers; show your numbers)

**Pass/Fail gates**

- Tool-call correctness improves over baseline on your gold set.
- 0 unapproved “write” tool calls (start read-only; add writes only if you have time).
- Threat model is referenced from the README.

**Interview prompts you must be able to answer**

- What are the top risks of tool-using agents, and how do you mitigate them?
- Why are remote tool servers a security risk?

## Glossary (simple)

- **SLO**: a reliability target you promise (example: “p95 latency under 2s”).
- **p50 / p95**: median vs “slow tail” latency. p95 means 95% of requests are faster than that number.
- **ADR**: a short “decision note” explaining *why* you chose something.
- **RAG**: “retrieve then generate” (pull relevant docs first, then answer using them).
- **Gold set**: a set of test questions with expected evidence/answers for regression testing.
- **MCP**: a protocol for connecting an LLM app to external tools/data sources via standardized messages.

---

## Post‑30 extension — Multi‑tenant isolation (do after the 30‑day sprint)

Multi‑tenancy is important, but it is explicitly **out of the first 30 days** to keep focus.

When you extend:
- Add `tenant_id` as a hard boundary across: request → auth → retrieval → caches → tools → logs.
- Add automated “leak tests” (tenant A must never see tenant B citations).
- Move budgets/quotas to be per‑tenant.
