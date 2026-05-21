# AI Engineering Learning System Design

**Date:** 2026-05-20  
**Status:** Draft for user review  
**Audience:** Chintan, a Senior Data & Platform Engineer moving into AI application, AI data, and AI platform engineering  
**Document type:** Learning roadmap / resource guide + documentation architecture design

## Summary

The IntelliOps documentation should become a single, coherent learning system for moving from strong data/platform engineering experience into Staff-level AI engineering. The current docs already contain useful theory, roadmap gates, and daily execution detail, but they mix too many documentation jobs in a way that makes learning feel unclear.

The redesign will keep the strongest parts: production-shaped project gates, the 90-minute/day constraint, Staff-level interview framing, and the OpsPilot project as the proof vehicle. It will add a clear front door, separate practice/resources/interview drills from theory, and rewrite fundamentals using first-principles technical writing.

## Goals

1. Make the docs a practical single source of truth for learning AI engineering from the ground up.
2. Preserve the user's current strengths in data platforms, distributed systems, FinOps, reliability, and backend engineering.
3. Build confidence through first-principles explanations, diagrams, trade-offs, and practice checkpoints.
4. Support three career targets:
   - AI application engineering: RAG, agents, tools, structured outputs, evals.
   - AI data engineering: ingestion, chunking, embeddings, lineage, feedback data, re-indexing.
   - AI platform engineering: tenancy, gateway, routing, budgets, observability, MCP, security, governance, serving.
5. Keep the system executable under the user's time constraints: roughly 45 minutes learning and 45 minutes building per day.
6. Produce Staff-level interview artifacts: architecture narrative, eval reports, benchmark evidence, security drills, and trade-off explanations.

## Non-goals

1. Do not turn the project into an ML research curriculum.
2. Do not chase every AI framework. Teach stable primitives first, then show framework examples.
3. Do not remove the daily time-boxed structure.
4. Do not duplicate the same canonical content across multiple docs.
5. Do not split `docs/learning-fundamentals.md` in the first pass unless it becomes impossible to keep usable.

## Current problems to solve

### Problem 1: Too many front doors

`docs/roadmap.md`, `docs/learning-book.md`, and `docs/llm-context.md` all contain orientation material. This makes it unclear where a human learner should start.

**Decision:** add `docs/learning-index.md` as the human front door. Keep `docs/llm-context.md` as an agent handoff document, not as a human learning entrypoint. Trim or redirect overlapping orientation text from other docs.

### Problem 2: The fundamentals file is large but not yet a clear textbook

`docs/learning-fundamentals.md` has broad coverage, but a learner can still feel lost because many sections read like accumulated notes. The user needs first-principles reasoning, not just topic lists.

**Decision:** keep it as the canonical theory source for now, but rewrite the top-level structure and key sections around a repeatable explanation pattern. Every important concept must explain why it exists, how it works, the trade-offs, and how to practice it.

### Problem 3: Practice, resources, and interview prep are mixed into theory and daily tasks

The current docs have questions and build steps, but not enough explicit lab catalog, curated resources, or Staff-level drill structure.

**Decision:** add support docs with clear authority boundaries:

- `docs/practice.md` for labs, checkpoints, expected outputs, and proof artifacts.
- `docs/resources.md` for curated external sources with why/how to use each one.
- `docs/interview-bank.md` for Staff-level drills, follow-ups, and answer frameworks.

These docs must link back to the textbook and roadmap instead of duplicating canonical explanations.

## Documentation architecture

| File | Canonical job | Required changes |
|---|---|---|
| `docs/learning-index.md` | Human front door and single source of truth for how to learn | Create. Include target outcome, reader profile, skill tree, learning tracks, doc map, 30/60/90-day path, and daily usage loop. |
| `docs/llm-context.md` | Agent handoff / consolidated requirements | Keep. Add a clear note that humans should start at `docs/learning-index.md`. Remove competing "single source of truth" framing if it causes ambiguity. |
| `docs/roadmap.md` | Build spec, gates, pass/fail criteria | Keep as canonical "what to build". Reduce duplicated navigation text and point to `learning-index.md`. |
| `docs/learning-book.md` | Day-by-day guided curriculum | Keep daily 90-minute shape. Group days into modules and gates so the schedule feels coherent. Link to `practice.md` for detailed labs. |
| `docs/learning-fundamentals.md` | First-principles textbook | Rewrite structure and key sections with the concept template below. Add missing AI engineering topics. |
| `docs/practice.md` | Labs, checkpoints, proof artifacts | Create. It is the canonical home for reusable labs and expected outputs. |
| `docs/resources.md` | Curated high-signal learning sources | Create. Keep it curated, not exhaustive. |
| `docs/interview-bank.md` | Staff interview drills and answer frameworks | Create. Reference fundamentals sections instead of duplicating the whole textbook. |
| `docs/hints/` | Optional copy/paste playbooks | Keep. Add links from practice labs only where the learner is stuck. |
| `docs/decisions/` | Architecture decisions | Keep ADR-only. Use for design decisions, not general tutorial content. |
| `docs/30-day-plan.md`, `docs/updated-roadmap.md` | Deprecated stubs if still present | Replace with short redirects or remove if safe. |

## Fundamentals writing standard

Every major topic in `docs/learning-fundamentals.md` should use this structure:

1. **Why this exists**
   - Start with the production problem.
   - Example: "RAG exists because model weights are not a reliable, fresh, private source of company knowledge."

2. **Concrete example**
   - Show a realistic OpsPilot scenario before abstract definitions.
   - Example: "A user asks why API p95 latency spiked. The answer needs runbooks, metrics, logs, and citations."

3. **First-principles explanation**
   - Build from simple truths.
   - Define one new concept at a time.
   - Avoid using an unfamiliar term to explain another unfamiliar term.

4. **How it works**
   - Explain the mechanism step by step.
   - Include data flow, state transitions, request lifecycle, or query lifecycle where useful.

5. **Design decisions and trade-offs**
   - Explain why this approach is chosen.
   - Compare alternatives.
   - Include what can go wrong and how to detect it.

6. **Diagram**
   - Use Mermaid diagrams for source-controlled, Obsidian-friendly diagrams.
   - Export PNG or SVG for diagrams that need visual clarity outside Obsidian.
   - Prefer diagrams for flows, boundaries, lifecycles, and decision trees.

7. **How to practice it**
   - Add a small question, calculation, lab, or design decision.
   - Link to `docs/practice.md` for longer exercises.

8. **Staff-level explanation**
   - Include a concise explanation the user can give in interviews.
   - Include follow-up questions and what a strong answer should mention.

This template is a quality bar, not a substitute for theory. The rewrite must not skip actual fundamentals. Each section must still explain the underlying concept deeply enough for a software/data platform engineer who is new to modern AI systems.

## Diagram strategy

Use diagrams where they reduce ambiguity.

Required diagram types:

1. **System maps**
   - AI gateway -> AI service -> retrieval -> tools -> model -> eval/trace/audit.

2. **Lifecycle diagrams**
   - ingestion -> chunking -> embedding -> indexing -> retrieval -> generation -> eval.

3. **Decision trees**
   - RAG vs long context vs fine-tuning.
   - hosted model vs local/self-hosted serving.
   - prompt engineering vs RAG vs LoRA.

4. **Sequence diagrams**
   - `/ask` request lifecycle.
   - tool call with MCP, approval, audit, and timeout.
   - eval-gated release flow.

5. **Trade-off maps**
   - latency vs quality vs cost.
   - batching vs p95 latency.
   - HNSW vs IVFFlat.

Default format:

- Mermaid in Markdown for editable source.
- PNG/SVG exports only when needed for visual review or external sharing.

## Curriculum tracks

### Track 1: AI application engineering

Purpose: build production AI applications, not demos.

Core topics:

- LLM APIs, request/response shape, streaming.
- Prompt and context engineering.
- Structured outputs with JSON schemas and Pydantic.
- Tool calling and typed tool contracts.
- RAG from first principles.
- Citations, refusal behavior, and grounding.
- Agent workflows vs autonomous agents.
- LangGraph/OpenAI Agents/CrewAI as examples of patterns, not the core skill.
- Evals for RAG and agents.

Practice artifacts:

- Minimal `/ask` endpoint.
- Schema-valid response.
- RAG answer with citations.
- Tool call trace.
- Gold-set eval report.

### Track 2: AI data engineering

Purpose: treat AI context as a data product.

Core topics:

- Raw vs derived data.
- Unstructured ingestion: PDF, HTML, wiki, tables, OCR.
- Chunking strategies and metadata.
- Embedding model choice and maintenance.
- Re-embedding migrations.
- Incremental indexing and freshness.
- Dataset versioning for evals and fine-tuning.
- Feedback loops and human review data.
- Lineage from source document to answer citation.

Practice artifacts:

- Ingestion pipeline.
- Chunk metadata schema.
- Re-indexing plan.
- Eval dataset version.
- Source-to-answer lineage example.

### Track 3: AI platform engineering

Purpose: operate AI systems safely, cheaply, and reliably.

Core topics:

- Gateway responsibilities.
- Tenancy and authorization.
- Budgets, quotas, routing, and cost attribution.
- OpenTelemetry and LLM-native observability.
- Prompt/model/retrieval versioning.
- Eval gates in CI/CD.
- MCP server/client boundaries.
- Tool security and least privilege.
- Guardrails, PII redaction, audit logs.
- Governance basics: model cards, risk classification, responsible AI, compliance-aware logging.

Practice artifacts:

- Gateway policy table.
- Budget-exceeded response.
- Trace with LLM/retrieval/tool spans.
- MCP tool with approval mode.
- Security drill report.

### Track 4: AI infrastructure depth

Purpose: understand serving and model adaptation enough to make platform trade-offs.

Core topics:

- Local vs hosted inference.
- vLLM/Ollama/llama.cpp roles.
- TTFT, TPOT, throughput, p50/p95.
- KV cache and prefix caching.
- Continuous batching.
- Quantization.
- Model routing and cascades.
- Long context vs RAG.
- Fine-tuning vs RAG vs prompt engineering.
- LoRA/QLoRA and training cost.
- Multi-LoRA serving conceptually.

Practice artifacts:

- Serving benchmark.
- Cost-per-query estimate.
- Cache/batching/routing experiment.
- Fine-tuning cost estimate.
- Hosted vs local trade-off note.

## Coverage additions

The redesign should add or strengthen these topics:

1. Compound AI systems: LLMs as one component in a larger system.
2. Long-context models vs RAG: decision framework and failure modes.
3. Agent workflows vs agents: deterministic workflows first, autonomy only when justified.
4. MCP and A2A: interoperability concepts and security boundaries.
5. LLM eval depth: rubric design, judge calibration, error taxonomy, regression tracking.
6. AI data lifecycle: unstructured ingestion, feedback data, lineage, re-indexing, embedding maintenance.
7. Structured generation: schema validation, constrained decoding, tool argument safety.
8. AI observability: traces, spans, token/cost metrics, eval metrics as operational signals.
9. AI security: prompt injection, indirect injection, tool abuse, exfiltration, MCP trust.
10. AI FinOps: token spend attribution, routing, prompt caching, budget guardrails.
11. Model lifecycle: prompt versions, model versions, retrieval config versions, canaries, rollback.
12. Governance: PII, audit trails, responsible AI basics, model cards, compliance-aware architecture.
13. Multimodal and document AI basics: layout, tables, OCR, images, charts.
14. Fine-tuning and adaptation: LoRA/QLoRA, DPO/GRPO concepts, when not to fine-tune.

## Resource curation rules

`docs/resources.md` must not become a link dump.

Each topic should have:

- up to three primary resources;
- up to two practical implementation resources;
- one optional deeper resource only if it adds clear value.

Each resource entry must include:

- **Use for:** read, watch, build, practice, or reference.
- **Why it matters:** one sentence.
- **What to skip:** one sentence if the source is broad.
- **Freshness note:** stable concept, current tooling, or watch-for-change.

High-signal sources to include where appropriate:

- Anthropic: Building Effective Agents.
- Lilian Weng: LLM-powered autonomous agents.
- Eugene Yan: LLM patterns and eval writing.
- Model Context Protocol documentation.
- OpenAI Evals and DeepEval.
- OpenTelemetry/OpenLLMetry.
- OWASP Top 10 for LLM Applications.
- vLLM documentation.
- Hugging Face PEFT and TRL.
- Unstructured.io / Docling-style ingestion references.
- Cloud provider docs for Bedrock, Vertex AI, and Azure AI Foundry.

## Practice system

`docs/practice.md` should define labs with this shape:

1. **Goal**
2. **Why this lab matters**
3. **Inputs**
4. **Steps**
5. **Expected output**
6. **What to observe**
7. **Failure modes**
8. **Staff-level explanation**
9. **Artifact to save**

Required lab groups:

1. RAG baseline lab.
2. Chunking and retrieval quality lab.
3. Structured output and refusal lab.
4. Gold-set eval lab.
5. Tool/MCP governance lab.
6. Trace and observability lab.
7. Prompt injection and exfiltration drill.
8. Budget/cost control lab.
9. Serving benchmark lab.
10. Long-context vs RAG decision exercise.

## Interview system

`docs/interview-bank.md` should organize drills by topic and level.

Each drill should include:

- question;
- what the interviewer is testing;
- answer shape;
- strong signals;
- weak signals;
- follow-up questions;
- references to fundamentals sections;
- related project artifact.

The interview bank should not duplicate the full textbook. It should help the user practice retrieval and explanation from the textbook and project artifacts.

## Daily guide strategy

`docs/learning-book.md` should remain day-based because the user needs execution discipline.

New structure:

- Module name.
- Gate the module supports.
- Daily goal.
- Theory reading.
- Practice link.
- Build step.
- Artifact to save.
- Short-on-time fallback.
- Reflection prompt.

This preserves the current 90-minute daily loop while making each day feel connected to a larger track.

## Execution phases

### Phase 1: Front door and authority cleanup

Create `docs/learning-index.md`. Update `docs/llm-context.md`, `docs/roadmap.md`, and deprecated stubs so a human learner knows exactly where to start.

### Phase 2: Support docs

Create `docs/practice.md`, `docs/resources.md`, and `docs/interview-bank.md` with enough initial content to support the first 30 days and the post-30 extension.

### Phase 3: Fundamentals rewrite pass

Update `docs/learning-fundamentals.md` with:

- a clearer first-principles module map;
- the concept writing standard;
- diagrams for core flows;
- missing coverage additions;
- stronger "why this decision" and "how to practice" blocks.

Do not remove existing useful theory unless it is duplicated, obsolete, or actively confusing.

### Phase 4: Daily guide rewrite pass

Update `docs/learning-book.md` so each day points to the correct theory, practice lab, resource, and artifact. Preserve time-boxed execution.

### Phase 5: Consistency pass

Check all cross-links, headings, redirects, glossary references, and deprecated docs. Ensure there is exactly one canonical home for each kind of content.

## Acceptance criteria

The redesign is successful when:

1. A learner can open one file, `docs/learning-index.md`, and understand the full path in under 10 minutes.
2. Each major AI engineering concept has first-principles explanation, concrete example, trade-offs, practice, and interview framing.
3. The 30-day plan is executable without deciding what to study next.
4. Practice labs produce visible artifacts.
5. The resources file is curated and prioritized, not exhaustive.
6. The interview bank helps practice Staff-level answers without duplicating the full textbook.
7. Roadmap gates, daily guide, practice labs, and fundamentals cross-link consistently.
8. Deprecated or moved docs cannot mislead the learner.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| The docs become too large again | Separate document jobs and keep resources curated. Split fundamentals later if the file becomes unusable. |
| Practice content duplicates daily guide content | Daily guide links to labs; `practice.md` owns detailed lab steps and expected outputs. |
| Interview bank duplicates fundamentals | Interview bank owns drills and answer shapes; fundamentals owns theory. |
| Diagrams become stale | Keep Mermaid source in Markdown; generate PNG/SVG only when necessary. |
| Tool/framework advice becomes obsolete | Teach stable primitives first and mark tooling resources with freshness notes. |
| The first pass becomes too ambitious | Implement in phases, with review after the spec and implementation plan. |

## Open decisions resolved

1. Use current branch directly because the user approved direct changes on this branch.
2. Keep daily time-boxing.
3. Use `learning-index.md` as the human front door.
4. Keep `llm-context.md` as agent handoff.
5. Keep `learning-fundamentals.md` as the theory source for the first pass.
6. Add diagrams using Obsidian-friendly Mermaid and optional PNG/SVG exports.
7. Add first-principles depth without skipping theory.

