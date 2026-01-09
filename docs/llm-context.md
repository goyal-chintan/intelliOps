# IntelliOps / OpsPilot context (consolidated requirements)

_Last updated: 2026-01-09 16:10 IST_

This file is a **clean handoff** you can paste into any LLM so it understands what you want, without reading chat history.

## Primary goal (30 days)

- Become **interview‑ready in ~30 days** for strong tech companies by **building IntelliOps/OpsPilot** and being able to defend the design at Staff/Senior level.
- Do this with **~90 minutes/day**:
  - ~45 min: deep fundamentals (theory + math + interview questions)
  - ~45 min: build the system (production‑shaped increments)
- Keep it **beginner‑friendly** (you are new to Python frameworks and modern LLM infra), with **zero ambiguity** and **no rabbit holes**.

## What is being built (high level)

- **IntelliOps (a.k.a. OpsPilot)**: a production‑shaped **Ops copilot** that answers reliability + cost questions using:
  - **runbooks/docs** (ground truth text),
  - **facts from data** (logs/metrics/cost/incident summaries via tools),
  - an **LLM** (summarize/explain), with **citations + structured JSON** outputs.
- The point is not “a chatbot demo”. The point is a **platform story**:
  - evals as a release gate,
  - latency/cost measurement,
  - safe tool boundaries + audit logs,
  - clear architecture decisions you can defend.

## Key constraints / preferences

- Hardware: MacBook Pro M2 Pro.
- Storage: Postgres + pgvector.
- Services: Python AI service (FastAPI) + Spring Boot gateway.
- You will use coding agents (Codex/Copilot) for boilerplate, but **you must drive**:
  - the spec,
  - trade‑offs,
  - “done when” gates,
  - validation (tests/evals/benchmarks).

## 30‑day scope boundaries (no ambiguity)

- **In the first 30 days**: build it **tenant-aware** (start with 1 tenant), but production‑shaped (auth, audit logs, evals, observability, cost math).
  - By ~Day 21: MCP server + approval-gated tool loop exists.
  - By ~Day 30: one measurable optimization proof exists (routing OR caching OR batching) with a reproducible benchmark + graph.
- **After day 30 (extension)**: customer‑grade multi‑tenant/multi‑customer isolation (hard boundaries + leak tests).

## Data realism requirement (raw vs derived)

- Inputs must look like real production inputs:
  - **raw log lines** (`.raw.txt`) and **compressed** (`.gz`) where applicable.
- Any parsed/structured artifacts are **derived outputs** (useful for tools + retrieval), but the raw source stays raw.

## “Single source of truth” docs (how the repo should be organized)

- `docs/roadmap.md` = canonical **what to build + pass/fail gates**.
- `docs/learning-book.md` = daily plan (**45m learn + 45m build**), with step‑by‑step instructions.
- `docs/learning-fundamentals.md` = the **textbook** (definitions, mental models, math, interview questions).
- `docs/decisions/` = canonical **architecture decisions (ADRs)** you can reference in interviews.
- `docs/hints/` = optional copy/paste playbooks (only when stuck).
- `AGENTS.md` = how coding agents should work in this repo (so agents don’t guess).

## Positioning (how this should sound in interviews)

- This repo is a **Staff‑level LLM platform project**:
  - “production‑shaped RAG + tool use + eval gates + observability + cost controls”
  - not metadata discovery, not cataloging, not Lumos.
