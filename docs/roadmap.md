# IntelliOps / OpsPilot roadmap

This is the **product-facing roadmap** for IntelliOps (OpsPilot). It describes what we are building and how to validate each increment.

Learning-only materials (daily plan, fundamentals, hints) live on the `learning-resources` branch.

## Milestone 0 — Deterministic baseline (dataset + CLI)

Goal: Establish a trustworthy baseline that behaves deterministically.

Deliverables:

- Synthetic datasets for incidents, logs, metrics, and cost (single-tenant + multi-tenant)
- A deterministic CLI that can answer time-window questions over the dataset
- Runbooks as the primary knowledge base artifacts (`ERR_*` Markdown)

Acceptance:

- One-command dataset regeneration works locally
- CLI results are deterministic for a fixed seed

## Milestone 1 — Retrieval + RAG API (single-tenant)

Goal: Serve grounded answers via an API with explicit schemas and citations.

Deliverables:

- Postgres + pgvector ingestion for runbooks (chunk + embed + index)
- `POST /ask` in an AI service that returns schema-valid JSON
- Answers include citations to runbooks and/or dataset evidence

Acceptance:

- API rejects invalid requests and produces schema-valid responses
- If no sources are available, the service refuses or asks for clarification (fail-closed)

## Milestone 2 — Gateway controls (auth + rate limits + budgets)

Goal: Put policy enforcement and auditability in front of the AI service.

Deliverables:

- Gateway with API key auth
- Rate limiting + concurrency caps
- Audit logging (request metadata, sources/tools used; never log secrets)

Acceptance:

- Correct 401/403 behavior, and API keys never appear in logs

## Milestone 3 — Observability + eval gates

Goal: Make quality and performance measurable and regressions visible.

Deliverables:

- Traces across gateway → AI service → DB (OpenTelemetry)
- A small gold set + eval harness that can be re-run

Acceptance:

- A known regression blocks a release (even if the “release” is just a tag)
- Latency breakdown is visible (retrieve vs generate vs tool time)

## Milestone 4 — Multi-tenant hardening

Goal: Enforce tenant isolation across retrieval, tools, caches, and observability.

Deliverables:

- Tenant context propagation end-to-end
- “Leak tests” proving tenant A cannot access tenant B data

Acceptance:

- Cross-tenant citations never occur in evals

## Decisions (ADRs)

See `docs/decisions/` for the rationale behind key architecture choices.
