# OpsPilot roadmap (Layers 0 → 3)

OpsPilot is built in **4 layers**, each intentionally adding a new “infra-grade” capability.

This doc is the canonical roadmap + acceptance criteria for the repo.

## Layer 0 — Understandable Demo (1–1.5 weeks)

**Goal**: Single-tenant, simple RAG copilot over synthetic incidents & runbooks.

### What we build

#### Synthetic incident stream
- Scala job emitting JSON logs to Kafka:
  - `service_name`, `status_code`, `latency_ms`, `env`, `timestamp`
- Batch job writes hourly aggregates to a data store (e.g., Postgres or ClickHouse).

#### Knowledge base
- 50–100 Markdown runbooks:
  - “How to debug latency spikes”
  - “How to analyze 5xx errors”
  - “How to reduce S3 costs”
- Ingestion pipeline:
  - ingest → chunk (e.g., 500 tokens with overlap) → embed → index into a vector DB

#### LLM API
- Python FastAPI service
- LangChain/LangGraph flow:
  - retrieve top‑k docs
  - construct prompt: runbook context + recent metrics summary
  - answer with citations

#### Simple UI / CLI
- CLI or minimal React UI
- Input: free-text question about incidents/cost
- Output: answer + supporting docs

### Acceptance criteria
- **Latency**: p95 ≤ 2.0s at 1 QPS (single user) using hosted model
- **RAG eval**:
  - build 20-case goldset (question → expected key points)
  - run RAGAS (or similar)
  - Answer Faithfulness ≥ 0.7
  - Context Recall ≥ 0.8
- **Docs**: README includes architecture diagram + one-command local run (docker-compose/helm) + example screenshots

### Interview story
“I can go from raw data → RAG → evals → usable API, with basic quality + latency measurements.”

## Layer 1 — Production-shaped RAG (multi-tenant + basic agents)

**Goal**: Make OpsPilot feel like something a real team could adopt.

### What we build

#### Multi-tenant design
- Tenants = teams/services (e.g., `payments`, `search`, `data-pipeline`)
- Partitioning:
  - metrics partitioned by `tenant_id`
  - vector DB namespaces or metadata filters per tenant

#### Gateway (Spring Boot)
- Auth (simple API keys)
- Select tenant and inject tenant context into the AI layer

#### Agentic “diagnose incident” flow (LangGraph/LangChain)
Tools:
- `get_metric_timeseries(service, metric, window)`
- `get_top_errors(service, window)`
- `search_runbooks(query, tenant)`

Agent steps:
- classify query (latency vs errors vs cost)
- call metrics/log tools
- call RAG over runbooks
- summarize RCA + recommended actions
- explicitly log decision traces (tools called + order)

#### Observability
- OpenTelemetry traces from gateway → AI service
- Grafana dashboard:
  - p50/p95 latency
  - QPS
  - vector search time vs LLM time
  - per-tenant traffic

### Acceptance criteria
- **Latency**: p95 ≤ 2.5s at 2–3 QPS (low-load test)
- **Tenants**: ≥ 3 tenants with distinct metrics + runbooks
- **Traces**: Grafana makes it obvious which tools were used and where time was spent

### Interview story
“I built a multi-tenant incident & cost copilot with an agent that calls tools + a RAG layer, with OTEL traces and dashboards.”

## Layer 2 — LLM Infra Excellence (serving, batching, KV cache, routing)

**Goal**: Take control of inference and show hard numbers.

### What we build

#### Self-hosted inference
- Run an open model via vLLM or TGI
- Enable continuous batching and measure throughput gains vs naïve serving
- Reproduce a real (smaller) improvement locally and document results

#### KV / prefix cache & routing
- Prefix-aware router in Spring Boot gateway:
  - repetitive prompts route to the same backend shard to maximize cache hits
- Instrumentation:
  - cache hit-rate
  - TTFT hot vs cold

#### Model routing (SLM + LLM)
- “Model cascade”:
  - simple queries → cheaper/faster model
  - hard/ambiguous queries → larger model

#### FinOps dashboards
- Tag every request with:
  - model name, tenant, route, token counts
- Grafana panels:
  - cost per 1k tokens per model
  - cost per tenant
  - % requests hitting cheap vs expensive model

### Acceptance criteria
- **Throughput**: 3–5× improvement vs baseline “no batching, no cache”
- **Cache**: ≥ 70–80% hit-rate on seeded repetitive workloads; TTFT hot vs cold clearly different
- **Cost**: ≥ 30–40% reduction in avg cost/query using routing + token budgeting vs single big model

### Interview story
“I implemented a cache-aware, multi-model gateway on top of vLLM/TGI. It gave ~4× throughput and ~40% lower cost, and I can show the Grafana breakdown per tenant + model.”

## Layer 3 — Agentic Ecosystem & Cloud Integration (high bar)

**Goal**: Show you understand agentic ecosystems + cloud platforms from an infra angle.

### What we build

#### Rich agent workflows
Example workflow: “Cut infra cost by 20% for the data-pipeline service this month.”

Agents:
- Planner agent: chooses windows + cost sources
- Metrics agent: pulls time-series and finds waste patterns
- FinOps agent: proposes concrete actions (e.g., shrink EMR, turn off dev at night)
- Reporter agent: generates final report with tables + bullets

Persistence:
- per-tenant “memory” (Postgres/Redis) storing previous recommendations

#### n8n / LangFlow integration (optional)
- Expose OpsPilot APIs as n8n nodes or LangFlow tools
- Example: daily cron generates weekly incident summary → sends to Slack/email

#### Managed LLM backend toggle (e.g., Vertex AI)
- Two backends:
  - self-hosted open model
  - managed model (Vertex)
- Toggle via config flag; log latency/cost differences

### Acceptance criteria
- End-to-end agent workflow on seeded dataset produces non-trivial, metric-grounded recommendations
- n8n/LangFlow: at least one public screenshot + flow export committed
- Managed LLM: recorded latency & cost vs self-hosted for at least one scenario

### Interview story
“I built a multi-agent cost & incident advisor with LangGraph, integrated it with n8n, and made it run on both self-hosted vLLM and Vertex AI, with clear latency/cost trade-offs.”


