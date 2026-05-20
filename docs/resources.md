# AI Engineering Resources

_Last updated: 2026-05-20 IST_

This file is curated, not exhaustive. Use it when the daily guide or fundamentals points here.

## Curation rules

- Prefer primary sources and canonical engineering write-ups.
- Keep each topic small: up to three primary resources, two practical resources, and one optional deep dive.
- Every resource must explain what to use it for, why it matters, what to skip, and whether it is stable or tooling-sensitive.

---

## First-Principles AI Engineering

The foundation. Read these before any framework or tooling.

### Primary resources

**Anthropic: Building Effective Agents**
- **Use for:** Understanding when and why to use agents, and how to constrain them.
- **Why it matters:** This is the clearest first-principles explanation of agentic patterns from a major lab. It covers agent loops, tool use, human-in-the-loop, and when not to use agents.
- **What to skip:** The Claude-specific API examples if you are using a different model. The patterns are portable; the syntax is not.
- **Freshness:** Stable concept. Tooling examples may age, but the agent pattern taxonomy is durable.
- **URL:** https://www.anthropic.com/research/building-effective-agents

**Eugene Yan: Patterns for Building LLM-based Systems and Products**
- **Use for:** Survey of production LLM patterns: evals, RAG, agents, caching, guardrails.
- **Why it matters:** Eugene Yan writes from applied ML experience at Amazon. This post is one of the best single-page summaries of LLM system design for engineers.
- **What to skip:** Nothing. It is already concise.
- **Freshness:** Stable patterns, slightly dated tool examples (2023). Core patterns remain valid.
- **URL:** https://eugeneyan.com/writing/llm-patterns/

**Lilian Weng: LLM-powered Autonomous Agents**
- **Use for:** Deep technical reference on agent architectures, memory systems, tool use, and planning.
- **Why it matters:** Lilian Weng (OpenAI) writes research-grade engineering posts. This one synthesizes the academic and engineering literature on agents in a way that is readable for engineers.
- **What to skip:** ReAct and chain-of-thought sections if you already know them. Focus on memory and tool subsections first.
- **Freshness:** Stable concept. Some framework references are dated (pre-LangGraph era), but the architecture taxonomy is still correct.
- **URL:** https://lilianweng.github.io/posts/2023-06-23-agent/

### Practical resources

**Simon Willison: Blog (llms tag)**
- **Use for:** Stay current on new LLM capabilities, practical hacks, and critical analysis.
- **Why it matters:** Simon's posts are hands-on and skeptical. He tests claims and documents real-world behavior. His prompt injection research is foundational.
- **Freshness:** Current tooling. Read for practice; verify techniques against your own model.
- **URL:** https://simonwillison.net/tags/llms/

---

## Agentic Systems

### Primary resources

**Lilian Weng: LLM-powered Autonomous Agents** (see First-Principles above)

**Anthropic: Building Effective Agents** (see First-Principles above)

**LangGraph Documentation: Concepts**
- **Use for:** Understanding the state machine model for agentic workflows.
- **Why it matters:** LangGraph makes the agent loop explicit as a graph with typed state. Reading the concepts section teaches you the underlying pattern; you can use the same pattern without LangGraph.
- **What to skip:** The integration-heavy tutorials until you understand the core graph model.
- **Freshness:** Tooling-sensitive. API changes frequently. Treat as a current reference, not a permanent textbook.
- **URL:** https://langchain-ai.github.io/langgraph/concepts/

### Practical resources

**OpenAI Swarm (conceptual reference)**
- **Use for:** Understanding minimal multi-agent handoffs.
- **Why it matters:** Swarm is intentionally minimal and readable. The source code teaches you what a handoff and agent loop look like at the code level without framework magic.
- **Freshness:** Experimental/educational. Do not use in production; use it to learn the primitives.
- **URL:** https://github.com/openai/swarm

---

## MCP and Tool Interoperability

### Primary resources

**Model Context Protocol: Official Documentation**
- **Use for:** Understanding the MCP server/client architecture, tool descriptors, resource types, and transport protocols.
- **Why it matters:** MCP is becoming the standard interoperability layer for AI tools. Understanding it now lets you design tool APIs that are framework-agnostic.
- **What to skip:** The quickstart tutorials until you have read the architecture overview and specification.
- **Freshness:** Actively evolving. Check the changelog when implementing.
- **URL:** https://modelcontextprotocol.io/docs

**MCP Specification (GitHub)**
- **Use for:** Reference when implementing a server or client.
- **Why it matters:** The spec is the source of truth. The docs may lag behind.
- **Freshness:** Tooling-sensitive. Track the version your client SDK targets.
- **URL:** https://github.com/modelcontextprotocol/specification

### Practical resources

**MCP Python SDK**
- **Use for:** Building and testing a minimal MCP server.
- **Why it matters:** The SDK is the fastest way to see what a compliant tool descriptor looks like in practice.
- **Freshness:** Actively maintained. Pin your version.
- **URL:** https://github.com/modelcontextprotocol/python-sdk

---

## RAG and Evals

### Primary resources

**OpenAI Cookbook: RAG from Scratch**
- **Use for:** Canonical end-to-end RAG implementation reference.
- **Why it matters:** It is the most cited first implementation guide. Read it to understand the baseline before adding complexity.
- **What to skip:** The API-specific boilerplate. Focus on the retrieval and prompt assembly logic.
- **Freshness:** Stable architecture. API syntax will age.
- **URL:** https://cookbook.openai.com/examples/vector_databases/readme

**DeepEval Documentation**
- **Use for:** Implementing LLM-as-judge evals with metrics like faithfulness, answer relevancy, and contextual precision.
- **Why it matters:** DeepEval provides production-ready eval metrics with explanations. It is more mature than building your own judge from scratch.
- **What to skip:** The cloud dashboard features unless you need them. The core metric implementations are the valuable part.
- **Freshness:** Actively maintained. Core metrics are stable; integration APIs may change.
- **URL:** https://docs.confident-ai.com/

**OpenAI Evals**
- **Use for:** Understanding how to design and run evals at scale.
- **Why it matters:** The Evals framework shows how a major lab structures evaluations. The conceptual design (prompt, sampling, grading, logging) is portable.
- **What to skip:** Most of the built-in evals. Focus on the eval design documentation.
- **Freshness:** Stable patterns. Framework details evolve.
- **URL:** https://github.com/openai/evals

### Practical resources

**Ragas**
- **Use for:** Evaluating RAG-specific metrics: faithfulness, answer relevance, context precision, context recall.
- **Why it matters:** Ragas has RAG-specific metrics that general LLM evals don't cover well.
- **Freshness:** Actively maintained. API changes between minor versions.
- **URL:** https://docs.ragas.io/

### Optional deep dive

**Eugene Yan: Evaluating the Effectiveness of LLM-Evals with LLM-Judges**
- **Use for:** Understanding calibration and reliability of LLM-as-judge approaches.
- **URL:** https://eugeneyan.com/writing/llm-evals/

---

## AI Data Pipelines and Unstructured Ingestion

### Primary resources

**Unstructured.io Documentation**
- **Use for:** Building ingestion pipelines for PDFs, HTML, Word docs, and other unstructured formats.
- **Why it matters:** Unstructured is the production standard for document ingestion in AI pipelines. Its partition and chunking APIs handle layout, tables, and OCR that naive text extraction misses.
- **What to skip:** The cloud-hosted API features if you are running locally. Focus on the `unstructured` library core.
- **Freshness:** Actively maintained. Pin your version; the API changes between releases.
- **URL:** https://docs.unstructured.io/

**Docling (IBM Research)**
- **Use for:** High-quality PDF and document parsing with layout understanding and table extraction.
- **Why it matters:** Docling handles document structure better than naive PDF parsers. For technical documents with tables, figures, and multi-column layouts, it significantly improves chunk quality.
- **What to skip:** The experimental visual models if you only need text extraction.
- **Freshness:** Rapidly evolving. Check the changelog before depending on specific features.
- **URL:** https://github.com/DS4SD/docling

**LlamaIndex: Data Ingestion Documentation**
- **Use for:** Understanding the connectors, readers, and transformation pipeline abstraction.
- **Why it matters:** Even if you do not use LlamaIndex in production, its data pipeline concepts (nodes, metadata, transformations) are a useful mental model for any ingestion system.
- **What to skip:** The framework-specific APIs. Read for the conceptual patterns.
- **Freshness:** Tooling-sensitive. Core concepts are stable; API changes frequently.
- **URL:** https://docs.llamaindex.ai/en/stable/module_guides/loading/

### Practical resources

**PyMuPDF (fitz)**
- **Use for:** Fast, reliable PDF text and metadata extraction without heavy dependencies.
- **Why it matters:** When you need direct PDF access without Unstructured's full stack, PyMuPDF is the fastest option and preserves page structure.
- **Freshness:** Stable. Mature library.
- **URL:** https://pymupdf.readthedocs.io/

---

## Observability and Security

### Primary resources

**OpenTelemetry Python Documentation**
- **Use for:** Instrumenting AI applications with traces, metrics, and logs.
- **Why it matters:** OpenTelemetry is the vendor-neutral standard. Investing in OTel means your traces work with Jaeger, Grafana Tempo, Datadog, or any backend.
- **What to skip:** The auto-instrumentation section until you understand manual span creation.
- **Freshness:** Stable API (v1.x). The spec is mature.
- **URL:** https://opentelemetry.io/docs/instrumentation/python/

**OpenLLMetry**
- **Use for:** LLM-native instrumentation: automatic spans for LLM calls, token counting, and retrieval.
- **Why it matters:** OpenLLMetry extends OTel with LLM-specific semantic conventions. It is the fastest way to get useful AI traces.
- **Freshness:** Actively maintained. Semantic conventions for LLMs are still stabilizing upstream.
- **URL:** https://github.com/traceloop/openllmetry

**OWASP Top 10 for LLM Applications**
- **Use for:** Understanding the security threat model for LLM-based systems.
- **Why it matters:** This is the canonical security reference for AI engineers. Every item (prompt injection, insecure output handling, supply chain) maps to a real production risk.
- **What to skip:** Nothing. It is short and every item matters.
- **Freshness:** Stable threat taxonomy. Updated as new attack patterns emerge.
- **URL:** https://owasp.org/www-project-top-10-for-large-language-model-applications/

### Practical resources

**Arize Phoenix**
- **Use for:** Local observability for LLM traces during development. Trace viewer, eval results, and dataset management in one UI.
- **Why it matters:** Phoenix is free, open source, and works locally. It reduces the feedback loop when debugging RAG and agent issues.
- **Freshness:** Actively maintained.
- **URL:** https://docs.arize.com/phoenix

---

## Model Serving and Inference

### Primary resources

**vLLM Documentation**
- **Use for:** Understanding high-throughput LLM serving with PagedAttention, continuous batching, and quantization.
- **Why it matters:** vLLM is the reference implementation for production open-model serving. Understanding how it works helps you make platform trade-offs between hosted and self-hosted inference.
- **What to skip:** The multi-GPU and tensor-parallel sections until you have run single-GPU experiments.
- **Freshness:** Actively maintained and rapidly evolving. Check the changelog for each release.
- **URL:** https://docs.vllm.ai/en/latest/

**Ollama Documentation**
- **Use for:** Local inference on Mac/Linux for development and testing.
- **Why it matters:** Ollama is the fastest way to run open models locally. It handles model management, quantization selection, and a simple API.
- **What to skip:** The REST API reference until you have run `ollama run` manually.
- **Freshness:** Actively maintained.
- **URL:** https://ollama.ai/docs

### Practical resources

**llama.cpp GitHub**
- **Use for:** Understanding inference at the CPU/GPU level. Good for benchmarking and understanding quantization.
- **Why it matters:** llama.cpp is the reference implementation for efficient CPU inference. Reading its README teaches you about quantization formats (GGUF), context window constraints, and batch size trade-offs.
- **Freshness:** Actively maintained.
- **URL:** https://github.com/ggerganov/llama.cpp

### Optional deep dive

**Hugging Face: Text Generation Inference (TGI)**
- **Use for:** Hugging Face-native serving with production features (tensor parallelism, flash attention).
- **Freshness:** Actively maintained. Different trade-offs from vLLM depending on model family.
- **URL:** https://huggingface.co/docs/text-generation-inference/

---

## Structured Outputs

### Primary resources

**OpenAI: Structured Outputs Guide**
- **Use for:** Understanding how to use JSON Schema and function calling to constrain model outputs.
- **Why it matters:** This is the primary reference for the OpenAI-compatible API pattern, which most models now support.
- **What to skip:** The legacy function-calling syntax. Use the newer `response_format` with JSON Schema.
- **Freshness:** Stable pattern. Tooling evolves; the schema-based approach is durable.
- **URL:** https://platform.openai.com/docs/guides/structured-outputs

**Instructor Python Library**
- **Use for:** Pydantic-first structured output extraction with retry and validation logic.
- **Why it matters:** Instructor handles schema validation, retry on validation failure, and partial extraction. It is the most ergonomic production approach for structured outputs in Python.
- **What to skip:** The experimental multi-modal extraction features until you need them.
- **Freshness:** Actively maintained. API is relatively stable.
- **URL:** https://python.useinstructor.com/

### Practical resources

**Outlines (dottxt-ai)**
- **Use for:** Constrained decoding for local models (grammar-based, regex, JSON Schema).
- **Why it matters:** When you control the inference stack, constrained decoding guarantees valid structured output at the token level—no retries needed.
- **Freshness:** Actively maintained.
- **URL:** https://dottxt-ai.github.io/outlines/

---

## Fine-Tuning and Model Adaptation

### Primary resources

**Hugging Face PEFT Documentation**
- **Use for:** Understanding LoRA, QLoRA, and other parameter-efficient fine-tuning methods.
- **Why it matters:** PEFT is the canonical library for efficient fine-tuning. The documentation explains the methods clearly and includes practical examples.
- **What to skip:** The IA3 and prefix tuning sections unless you specifically need them. Focus on LoRA and QLoRA first.
- **Freshness:** Actively maintained. Core LoRA concepts are stable.
- **URL:** https://huggingface.co/docs/peft/

**Hugging Face TRL Documentation**
- **Use for:** RLHF, DPO, and reward modeling. Also useful for SFT (supervised fine-tuning) with the `SFTTrainer`.
- **Why it matters:** TRL is the reference library for aligning models with human preferences. Even if you rarely fine-tune, understanding DPO helps you reason about when fine-tuning is justified.
- **What to skip:** The GRPO and advanced alignment sections on first pass. Focus on DPO basics and SFT.
- **Freshness:** Actively maintained and evolving rapidly. Concepts (DPO, RLHF) are stable; implementation details change.
- **URL:** https://huggingface.co/docs/trl/

**Axolotl**
- **Use for:** Practical LoRA fine-tuning with a config-driven approach.
- **Why it matters:** Axolotl wraps HF training with sane defaults and supports multiple model families. It is the most practical starting point for fine-tuning a small model.
- **Freshness:** Actively maintained.
- **URL:** https://github.com/OpenAccess-AI-Collective/axolotl

### Optional deep dive

**Tim Dettmers: QLoRA Paper and Blog**
- **Use for:** Deep understanding of quantization and LoRA interactions.
- **URL:** https://arxiv.org/abs/2305.14314

---

## Governance and Responsible AI

### Primary resources

**OWASP Top 10 for LLM Applications** (see Observability and Security above)

**Google Responsible AI Practices**
- **Use for:** Understanding model cards, fairness evaluation, and governance frameworks.
- **Why it matters:** Google's responsible AI documentation is practical and focuses on what engineers need to do, not just what researchers study.
- **What to skip:** The TensorFlow-specific tooling references.
- **Freshness:** Stable principles; tooling references may age.
- **URL:** https://ai.google/responsibility/responsible-ai-practices/

**EU AI Act Summary for Engineers (Ada Lovelace Institute or similar)**
- **Use for:** Understanding how regulatory risk classification affects AI system design.
- **Why it matters:** Staff-level AI engineers need to understand which AI systems carry regulatory risk and what documentation (model cards, impact assessments) is required.
- **What to skip:** The legal interpretation sections. Focus on the risk classification tiers.
- **Freshness:** Regulatory landscape is evolving. Track changes, especially for high-risk system categories.
- **URL:** https://artificialintelligenceact.eu/

### Practical resources

**Hugging Face Model Cards Documentation**
- **Use for:** Understanding what a model card should contain and why.
- **Why it matters:** Model cards are the minimum governance artifact for any model you deploy. They document intended use, limitations, and known risks.
- **Freshness:** Stable template.
- **URL:** https://huggingface.co/docs/hub/model-cards

---

## Cloud AI Platforms

These docs are tooling-sensitive. Use them as references, not textbooks.

### AWS Bedrock

**AWS Bedrock Documentation**
- **Use for:** Understanding Bedrock's model API, RAG (Knowledge Bases), agents, and guardrails.
- **Why it matters:** Bedrock is the AWS-native managed inference service. If your stack is AWS-first, Bedrock's guardrails and IAM integration are production-ready features.
- **What to skip:** The no-code console workflows. Focus on the API and SDK reference.
- **Freshness:** Actively evolving. Features added frequently.
- **URL:** https://docs.aws.amazon.com/bedrock/

### Google Vertex AI

**Vertex AI Documentation**
- **Use for:** Gemini API, RAG Engine, Grounding, and Vertex AI Pipelines for ML workflows.
- **Why it matters:** Vertex AI provides the GCP-native path from model development to production serving. The RAG Engine and Grounding features are production-ready for GCP stacks.
- **What to skip:** AutoML sections unless you need no-code training.
- **Freshness:** Actively evolving.
- **URL:** https://cloud.google.com/vertex-ai/docs

### Azure AI Foundry

**Azure AI Foundry Documentation**
- **Use for:** Azure OpenAI Service, AI Search (for RAG), Prompt Flow, and AI Safety evaluations.
- **Why it matters:** Azure AI Foundry is the Azure-native path and includes managed RAG, content safety, and Prompt Flow for pipeline orchestration.
- **What to skip:** The Power Platform integrations. Focus on the SDK and REST API references.
- **Freshness:** Actively evolving.
- **URL:** https://learn.microsoft.com/en-us/azure/ai-foundry/
