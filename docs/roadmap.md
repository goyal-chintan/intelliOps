# OpsPilot Roadmap (Staff-level, production-shaped)

_Last updated: 2026-05-20 IST_

This is the **canonical build spec** for the repo.

Plain-English map (no ambiguity):

- `docs/learning-index.md` = **where to start** and how the learning system fits together
- `docs/roadmap.md` (this file) = **what to build** + **pass/fail gates**
- `docs/learning-book.md` = **what to do today** (reading + coding, time-boxed)
- `docs/learning-fundamentals.md` = **the textbook** (first-principles theory, mental models, math, diagrams, interview questions)
- `docs/practice.md` = **labs and proof artifacts** _(planned support doc; added in the next implementation task)_
- `docs/resources.md` = **curated external references** _(planned support doc; added in the next implementation task)_
- `docs/interview-bank.md` = **Staff-level interview drills** _(planned support doc; added in the next implementation task)_
- `docs/hints/` = **optional help** (rationale + copy/paste playbooks)
- `AGENTS.md` = **how coding agents should work in this repo**

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
- CI: GitHub Actions runs checks on every PR
- Optional (Week 6): cloud GPU smoke test (vLLM)

Canonical “why + alternatives + interview talk-track”: `docs/decisions/roadmap-decisions.md`

## 30-day sprint scope (explicit)

This roadmap is intentionally **production-shaped**, not “touch every technique lightly”.

**In 30 days, you will build and be able to defend**:
- RAG with **citations** and **schema-valid JSON** outputs (no hand-wavy answers).
- A **gold set + eval harness** you can re-run (and a simple regression gate).
- Tool use to fetch **real facts** (metrics/logs/cost/events), with auditability.
- **Latency + token/cost** measurement, plus at least one measured improvement.
- Staff-grade operations decisions:
  - SLOs + error budget policy (what you do when you miss p95 or blow the token budget)
  - degradation strategy (what you disable first, and why)
  - release safety (feature flags/kill switches + rollback plan)
- The “real knobs” that show up in production (documented defaults + one small sweep):
  - decoding (`temperature`, `top_p`, `top_k` if supported, `max_tokens`)
  - retrieval (`k`, chunking params)
  - model selection (small vs bigger local model)
- A real “shipping loop”:
  - CI blocks merges on unit test failures, schema failures, tenant leak tests, security harness regressions, and (once it exists) gold‑set eval regressions.

**Explicitly deferred until after day 30 (by design)**:
- Customer-grade multi-tenant isolation and hard boundaries (RLS/schema-per-tenant/DB-per-tenant, strict secret boundaries).
- Production-scale GPU serving claims (vLLM/TensorRT-LLM) beyond a smoke test.
- Non-trivial fine-tuning runs (SFT/DPO/RLHF). Optional LoRA comes later **only** after you have evals + data.
- Any UI work (nice-to-have, not required to pass Staff platform screens).

## 30-day gates (G1 → G4)

This is the “don’t be surface-level” schedule. Each gate produces a proof artifact you can show in interviews.

- **G1 (by Day 7) — Platform skeleton exists**
  - AI service skeleton runs (at least `GET /health`).
  - Postgres + pgvector is up, and the service can connect and run queries.
  - One safe hosted LLM call works via a thin client wrapper (timeout + no secrets in logs).
  - Basic observability exists (request ids + tokens/latency logging).

- **G2 (by Day 14) — Governed tool use exists**
  - `/ask` works end-to-end with citations + schema-valid JSON (tenant-aware).
  - pgvector retrieval baseline exists (the query path is real and explainable).
  - 3–5 read-only tools exist with strict schemas, bounds, timeouts, and audit logs.
  - Prompt-injection and exfil “abuse drills” exist (and you can show safe refusals).
  - A minimal security harness exists (tests you can run repeatedly):
    - prompt injection + tool injection attempts
    - “no relevant context” refusal behavior
    - cap/budget exceeded behavior (fail closed: max tokens/tool calls/windows)
    - redaction checks (no secrets/PII in logs/traces/audit)
  - Budgets/caps exist (max tokens, max tool calls, max window sizes).
  - SLOs + error budget policy exists (even if simple) and you wrote a degradation ladder (“what we turn off first”).
  - Tool calls and audit logs are tenant-tagged (so isolation + FinOps are provable later).
  - At least one “tenant leak” regression test exists (tenant A must never cite/retrieve tenant B).
  - CI gate exists (GitHub Actions or equivalent):
    - blocks merges on unit tests + schema tests,
    - runs tenant leak tests + security harness (abuse drills),
    - runs a small gold-set eval slice once the eval harness exists.

- **G3 (by Day 21) — MCP surface + approvals exist**
  - A minimal **MCP server** exposes your tools.
  - A minimal agent path uses MCP tools and produces a debuggable decision trace (no “magic” tool calls).
  - “Write tools” are present only as stubs/mocks and require explicit approval (human-in-the-loop); default is read-only.
  - Tool approval policy is explicit and testable (example modes): `dry_run`, `auto_readonly`, `require_approval` (default deny for write).
  - Tool calls show up in audit logs and `decision_trace` immediately; once OpenTelemetry is wired (by Day 30), tool spans appear in traces too.
  - MCP security minimum is enforced:
    - per-tenant tool allowlists,
    - strict JSON schema validation at the MCP boundary,
    - bounded windows/rows + hard timeouts (fail closed),
    - redaction rules for logs/traces/audit,
    - write-capable tools require explicit approval (default deny).

- **G4 (by Day 30) — One hard optimization proof exists**
  - Pick **one** optimization and prove it with a reproducible benchmark + a graph:
    - routing/cascade (average tokens or $/request down)
    - caching (p95 latency down on repeated-prefix or repeated-query workloads)
    - batching (throughput up at concurrency)
  - Benchmark discipline:
    - use a real load harness (k6 or Locust recommended; `hey`/`vegeta` acceptable if committed as scripts/config)
    - fixed request set (or fixed gold-set slice)
    - baseline vs optimized results (change one thing at a time)
    - report p50/p95 and at least a coarse stage breakdown (retrieve vs tools vs LLM)
    - include TTFT (time-to-first-token) and a simple throughput view (req/sec or tokens/sec) at 1–2 concurrency levels
  - Commit the benchmark inputs + outputs (CSV/JSON) and a plot image into the repo so results are repeatable.
  - Release safety exists: at least one feature flag/kill switch for agent mode and write tools, plus a written rollback/degrade plan.

## Proof pack (must exist by Day 30)

If you can show these, the project reads like “staff-shaped platform engineering”, not a toy.

1) **README quickstart + live demo script**
   - README includes a one-command Quickstart and points to a 5-minute demo (CLI is fine) that hits gateway → AI service and shows:
     - schema-valid JSON + citations
     - at least one tool call (read-only) + audit record
     - tenant context on the request (even if you only demo 1 tenant)

2) **Architecture diagram**
   - A simple diagram showing: gateway → AI service → retrieval → tools → model, plus where auth/audit/traces/budgets live.

3) **Traces**
   - One exported/screenshot trace showing spans for:
     - gateway.request → ai.request → db.vector_search → ai.llm → ai.tool.*
   - Trace attributes include: `tenant_id`, model, tokens in/out, and latency breakdown.
   - One simple dashboard screenshot (latency p50/p95, error rate, tokens/request, tool error rate).

4) **Eval report**
   - A gold set (target: **30 cases**) and an eval run output showing:
     - baseline vs current
     - at least one known failure + your next fix
   - A simple pass/fail threshold is defined (and re-run on changes).

5) **Perf/cost report**
   - A benchmark result + graph showing baseline vs optimized for your chosen G4 track:
     - p50/p95 total latency + TTFT
     - a simple throughput view (req/sec or tokens/sec)
     - tokens/request and cost estimate (even if local is $0)

6) **Security + failure drills**
   - Security harness results (prompt injection, tool abuse, redaction, budget exceeded).
   - 3–5 scripted failure drills with “expected behavior” notes:
     - vector DB slow/down
     - tool timeout/outage
     - model timeout
     - retrieval returns no relevant context
     - prompt injection string embedded in retrieved docs
   - One short incident drill write-up (postmortem-style) showing degrade ladder + rollback notes.

7) **CI proof**
   - CI workflow exists and runs the same checks you run locally (tests, schema validation, tenant leak tests, security harness, eval slice).

**Pass condition:** you can point to each item in under 2 minutes.

## Learning map (roadmap ↔ fundamentals)

If you want a “fresh look” map of what matters and where it is covered, start with:
- `docs/learning-fundamentals.md` Part 0 (key principles + roadmap map)

Then use this quick mapping:

- **Layer 0 (tenant-aware RAG baseline)**: `docs/learning-fundamentals.md` Sections 1–10, 21, 25, 3.10–3.12, 35.0
- **Layer 1 (gateway + tools + governance + traces)**: `docs/learning-fundamentals.md` Sections 10, 12, 14, 21, 23–26, 30, 35.0
- **Layer 2 (serving + caching/batching + routing + capacity)**: `docs/learning-fundamentals.md` Sections 13–14, 23, 35, 36, 40
- **Layer 3 (MCP + agent hardening + threat model)**: `docs/learning-fundamentals.md` Sections 12.9–12.12 + Section 24.8, plus Sections 10, 23, 26, 28

## Layers (0 → 3)

Each layer is a **shippable bar** with measurable pass/fail gates. This is how you avoid “surface-level learning”.

Important: we are keeping the **same layers** as the original roadmap — we are only making each layer more “production-shaped” (testable, measurable, safe).

### Layer 0 — Understandable demo (baseline → tenant-aware RAG)

**Goal**: A tenant-aware copilot (start with 1 tenant) that can answer incident/cost questions with citations, plus a baseline you can trust.

**Deliverables**

- Deterministic dataset + CLI baseline (`level_zero/`).
- Postgres + pgvector retrieval over runbooks/docs.
- `POST /ask` (AI service) that returns **schema-valid JSON**:
  - `summary`, `hypotheses[]`, `evidence[]`, `actions[]`, `risk_level`
- First gold set (30 cases) + eval harness you can re-run (start with 20 if needed, but hit 30 by Day 20).
- Basic request logging (tokens + retrieval_ms + llm_ms + total_ms).
- Tenant context exists end-to-end (`tenant_id` on requests; included in logs/traces/audit records).
- Documented defaults (checked into the repo/config):
  - model name
  - decoding params (`temperature`, `top_p`, `top_k` if supported, `max_tokens`)
  - retrieval params (`k`, chunk size/overlap)

**Pass/Fail gates**

- One-command run works locally (DB + AI service).
- Answers include stable citations (no sources → refuse/ask).
- Eval harness runs and you saved a baseline score.
- You recorded p50/p95 latency once (don’t optimize yet; just measure).
- You can explain why your decoding defaults are set the way they are (and show one small sweep result).

**Interview prompts you must be able to answer**

- Why build a deterministic baseline before “trusting” an LLM?
- What breaks RAG in production, and how do you detect it quickly?

### Layer 1 — Production-shaped RAG (gateway + tools + observability)

**Goal**: Something a real team could safely expose internally (even with 1 tenant) with correct controls and proof.

**Deliverables**

- Spring Boot gateway:
  - API key auth (maps to `tenant_id` + `principal_id`)
  - rate limits + concurrency caps
  - basic budgets/quotas (fail closed)
  - audit log (who asked what, which sources/tools were used)
- “Tools” that fetch facts (even if implemented as simple internal functions first):
  - metrics query
  - log search
  - incident/event lookup
- Tool governance basics (keep it boring and safe):
  - strict tool schemas + argument validation
  - hard timeouts + max rows/windows
  - tool calls always appear in audit logs (inputs redacted as needed)
- Observability:
  - OpenTelemetry traces across gateway → AI service → DB
  - one dashboard that shows where time is spent
- Evals as a gate:
  - a “ship/no‑ship” threshold you can defend (and re-run)

**Pass/Fail gates**

- 401/403 auth behavior is correct and API keys never get logged.
- Traces make it obvious where time is spent (retrieve vs generate vs tools).
- A regression in your gold set blocks shipping (even if the threshold is simple).
- A “knob change” (prompt/model/decoding/retrieval) requires an eval re-run before you consider it shipped.

**Interview prompts you must be able to answer**

- What do you log, what do you never log, and why?
- Where do you enforce policy (gateway vs AI service), and why?

### Layer 2 — LLM infra excellence (local inference, caching/batching, routing, cost)

**Goal**: Show real engineering: measurement → change → measured improvement.

**30-day expectation**:
- Gate **G4** requires **one** measured improvement by Day 30.
- “Layer 2 done” (post‑30 depth) means **two** measured improvements with clear before/after numbers.

**Deliverables**

- Local inference on Mac:
  - run Ollama locally and call it via OpenAI-compatible API
  - (optional) run a `llama.cpp` server for more low-level control
  - document the exact model + settings you used
- A small “knob sweep” report (kept simple, but real):
  - compare 2–3 decoding settings and 2–3 retrieval settings on a subset of your gold set
  - record the quality/latency/cost deltas and pick defaults you can defend
- Benchmark harness + reports:
  - p50/p95 latency + TTFT vs concurrency (at least 2 points)
  - throughput view (req/sec and/or tokens/sec) vs concurrency
  - queue wait time (even if it’s “unknown yet”, write how you would measure it)
  - cache hit rate (if you implement caching)
  - tokens in/out per request
  - “cost estimate per request” (math, even if local is $0)
- By Day 40 (post‑30), at least two optimizations with measured deltas:
  - caching (prompt/prefix or retrieval)
  - batching (where applicable)
  - (optional) speculative decoding (measure; don’t assume)
- Cost controls:
  - per-tenant budgets/quotas enforced
  - routing/model cascade (cheap-first, big model only when needed)
  - cost dashboards (per tenant, per model)

**Pass/Fail gates**

- By Day 30 (Gate G4), you show 1 measured improvement with a reproducible benchmark + graph.
- By Day 40 (Layer 2 “done”), you show ≥ 2 measured improvements (your machine decides the scale).
- You can explain trade-offs (latency vs throughput vs quality vs cost).

**Interview prompts you must be able to answer**

- How do you capacity plan from tokens/sec and concurrency?
- When does caching backfire (privacy, staleness, correctness)?

### Interoperability slice — MCP + AGENTS.md (standards you will be asked about)

**Goal**: Make the project “ecosystem-ready”: tools are exposed through a standard boundary and agent behavior is governable.

Note:
- This slice is shipped inside the 30-day sprint via **Gate G3** (it is not a post-30 “nice-to-have”).

**Deliverables**

- `AGENTS.md` exists and stays updated as the repo evolves (how to work in this repo with coding agents).
- One MCP server exposing your read-only tools with strict schemas + bounds.
- One MCP client path (can be your AI service) that calls tools through MCP (not direct function calls).
- Tool approval modes are explicit and testable: `dry_run`, `auto_readonly`, `require_approval` (default deny for write).
- Every tool call is observable:
  - audit log record
  - trace span (by Day 30, once OpenTelemetry is wired) with tool name, tenant_id, duration, and approved? flag

**Pass/Fail gates**

- A tool call executed through MCP shows up in: response decision_trace and audit log (and in trace UI by Day 30).
- 0 unapproved write tool calls (write is stubbed/mocked until approvals exist).

### Layer 3 — Agentic ecosystem (MCP), hardening, and optional cloud GPU smoke test

**Goal**: Prove you can build tool-using agents safely and operate them.

Note:
- A minimal MCP + approvals slice is intentionally pulled into the first 30 days as **Gate G3**.

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

## Post‑30 extension — Customer‑grade multi‑tenant isolation (hard boundary)

In the first 30 days you should already be **tenant-aware** (even if you only run with 1 tenant):
- `tenant_id` exists and is required (header or auth mapping).
- retrieval/tools/caches/audit logs are tenant-tagged.
- at least one automated “leak test” exists (tenant A must never see tenant B citations).

Post‑30 is where you harden isolation to be customer-grade:
- DB-level isolation (RLS, schema-per-tenant, or DB-per-tenant).
- per-tenant budgets/quotas + billing attribution.
- multi-tenant cache partitioning rules + “tenant leak” regression tests.

Suggested 30–90 day arc (optional, if you want a longer runway):
- Days 31–40: deepen Layer 2/3 (serving optimizations, routing/caching/batching, MCP hardening, replay, failure drills).
- Days 41–60: multi-tenant isolation + leak tests + per-tenant budgets/quotas + cache partitioning.
- Days 61–90: hardening + portability:
  - OWASP LLM-style abuse tests integrated into CI (prompt injection/exfil/tool abuse)
  - optional cloud GPU smoke test (vLLM) using the same provider adapter
  - optional LoRA fine-tune only if it measurably improves a target metric (JSON compliance/tool selection) and you can show before/after evals.
