# Roadmap decisions (optional)

This is a “why we chose this” file. It is **not required** to build the project, but it helps you:

- stay confident (you know the reason behind each choice)
- answer “why did you do it this way?” questions in interviews

## 1) Why a strict JSON API instead of free-form chat?

**Chosen**: `POST /ask` returns schema-valid JSON (no free-form output).

**Reason (simple)**:
- JSON is testable. You can write tests that fail when the shape is wrong.
- JSON is measurable. You can evaluate “did we cite sources?” and “did we propose safe actions?”
- JSON reduces “looks good but wrong” answers because you force structure.

**Alternatives**
- Free-form chat text:
  - Looks impressive, but is hard to regression-test.
  - Easy to hallucinate citations/actions without detection.

**Interview talk-track**
- “We treated the model like an unreliable component. Strict JSON makes the output a contract we can test and gate in CI.”

## 2) Why Python for the AI service?

**Chosen**: Python AI service (FastAPI), but FastAPI stays thin.

**Reason (simple)**:
- Most LLM tooling, evaluation libraries, and SDKs are Python-first.
- Faster iteration for RAG, eval harnesses, and tool logic.
- Industry reality: the “LLM/data plane” is often Python even in Java-heavy companies.

**How to avoid getting stuck in frameworks**
- FastAPI should only do:
  - HTTP input/output
  - request ids + basic middleware
- All real logic lives in plain modules:
  - `retrieval/`, `prompting/`, `evals/`, `tools/`, `providers/`

**Alternatives**
- Java-only:
  - Great for control-plane and services, but you’ll fight ecosystem gaps for LLM eval + agent tooling.
- Python-only (no gateway):
  - OK if time is tight, but you lose a clean “control plane vs data plane” story.

**Interview talk-track**
- “We used Python for the AI/data plane because it’s the industry default for RAG + evals. We kept the framework thin so the logic stays readable and testable.”

## 3) Why a Spring Boot gateway?

**Chosen**: Spring Boot gateway as the **control plane**.

**Reason (simple)**:
- It mirrors how real companies separate concerns:
  - gateway = auth, rate limits, budgets, audit logs, routing decisions
  - AI service = retrieval, prompts, tools, agent logic
- You already know Spring Boot, so it’s a leverage point.

**Alternatives**
- Put everything in the AI service:
  - Faster at first, but less realistic separation.

**Interview talk-track**
- “The gateway is the ‘policy + routing’ layer. It enforces auth/budgets/rate limits before requests ever hit the model. Multi‑tenant isolation is a post‑30 extension, but the control‑plane boundary is the same.”

## 4) Why Postgres + pgvector (instead of a dedicated vector DB)?

**Chosen**: Postgres + pgvector.

**Reason (simple)**:
- One database for:
  - API keys, audit logs (and later: tenants)
  - documents, chunks, embeddings
- Easier ops for a solo project.
- Very common in internal enterprise apps.

**Alternatives**
- Dedicated vector DB (Qdrant/Pinecone/Weaviate):
  - Great at scale, but adds another service and mental overhead.

**Interview talk-track**
- “We optimized for operability and simplicity: one DB for metadata + vectors. If scale requires it, we can migrate the retrieval interface to a dedicated vector store.”

## 5) Why local inference on Mac for Layer 2?

**Chosen**: local inference via **Ollama** (default).

**Reason (simple)**:
- Very low friction on Mac (install once, run models with one command).
- Good enough to learn the real platform knobs:
  - latency vs concurrency,
  - context size trade‑offs,
  - caching/routing/budgets,
  - “measure → change → measure”.

**Alternatives**
- `llama.cpp` server:
  - also great on Apple Silicon,
  - more “infra‑like” if you want full control (and an OpenAI‑compatible server).
- vLLM/TGI:
  - best on NVIDIA GPUs; use as an optional cloud smoke test when you’re ready.

**Interview talk-track**
- “We used local inference to practice measurement and cost reasoning without cloud friction. The provider adapter keeps the system portable to vLLM in production.”


## 6) Why MCP for tools?

**Chosen**: tools exposed via MCP servers.

**Reason (simple)**:
- It creates a clean boundary:
  - tools have permissions, timeouts, and audit logs
  - the model can’t do anything directly; it can only *request* tool calls
- This is the core safety story for agents.

**Alternatives**
- Direct Python function calls:
  - OK for a demo, but less governance and less realistic.

**Interview talk-track**
- “Tools are the risky part of agents. MCP gives us a standard tool boundary where we can enforce policy and logging.”

## 7) “Production-shaped” — what that actually means

In this repo, “production-shaped” means:

- **tests exist** (not just demos)
- **numbers exist** (latency, tokens, cost estimates)
- **gates exist** (eval regressions can block shipping)
- **safety exists** (auth, safe logging, audit logs, tool governance; tenant isolation is a post‑30 extension)

If you can say those 4 things clearly, you will sound senior in interviews.
