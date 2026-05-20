# Staff AI Engineering Interview Bank

_Last updated: 2026-05-20 IST_

This file is for practicing explanation. It references `docs/learning-fundamentals.md` for theory and `docs/practice.md` for artifacts.

## How to practice

For each question:

1. Answer in 60 seconds.
2. Name the trade-off.
3. Point to one project artifact.
4. Answer one follow-up.
5. Score yourself using the rubric.

## Self-scoring rubric

| Score | Signal |
|---|---|
| 1 | Definition only; no trade-off or artifact. |
| 2 | Correct basic explanation; weak production reasoning. |
| 3 | Good mechanism and trade-off; limited artifact evidence. |
| 4 | Strong Staff-level answer with measurement, failure modes, and artifact. |
| 5 | Clear, concise, first-principles answer plus alternative designs and operational risks. |

## Practice routine

Run one drill group per session. For each question: speak your answer aloud (or write it), then check strong/weak signals. Score yourself honestly. If you score 1–2, read the referenced section in `docs/learning-fundamentals.md` before retrying. If you score 3, identify which artifact from `docs/practice.md` you would cite and fill that gap.

---

## Drill Group 1: LLM Fundamentals and Token Economics

**References:** `docs/learning-fundamentals.md` → LLM Fundamentals, Tokenization, Context Window  
**Related artifact:** Lab 8 (Budget/Cost Control) in `docs/practice.md`

### Core questions

1. **What is a token, and why does tokenization matter for system design?**

   *Answer shape:* A token is the smallest unit the model processes—roughly 0.75 words in English but varies by language and content. Tokenization matters because the model's context window is measured in tokens, not words, and all costs are charged per token. Design implications: long prompts are expensive, non-English text tokenizes inefficiently, and code tokenizes differently from prose.

   *Strong signals:* Explains byte-pair encoding at a high level. Mentions token-to-word ratio varies by language. Links token count to context window and cost. Notes that prompt compression and caching reduce cost.

   *Weak signals:* Says "tokens are like words" and stops. Cannot say what happens when you exceed the context window. No mention of cost implications.

2. **Explain the difference between prompt tokens and completion tokens, and how they affect cost.**

   *Answer shape:* Prompt tokens are the input (system prompt + context + user message). Completion tokens are the output the model generates. Most providers charge more per completion token than prompt token. Cost = (prompt_tokens × input_price) + (completion_tokens × output_price). In RAG, the retrieved chunks dominate prompt cost. In agents, multiple turns accumulate.

   *Strong signals:* Correct formula. Notes that cached prompt tokens often cost less. Explains that reducing retrieved chunk size is the main lever for RAG cost. Mentions streaming does not change token count.

   *Weak signals:* Cannot distinguish the two. No mention of prompt caching. Cannot estimate cost for a simple query.

3. **What is temperature, and when would you set it to 0 vs 0.7?**

   *Answer shape:* Temperature controls the sharpness of the probability distribution over next tokens. At 0, the model always picks the highest-probability token (deterministic). At 0.7, it samples with more diversity. Set temperature to 0 for structured outputs, classification, evals, and anywhere consistency matters. Use higher temperature for creative tasks, brainstorming, and data augmentation.

   *Strong signals:* Explains it as distribution sharpness, not just "creativity." Notes that 0 is not truly deterministic across providers due to floating-point nondeterminism. Mentions `top_p` as an alternative diversity control.

   *Weak signals:* Says "0 is more precise, higher is more creative" without mechanism. Cannot say when to use each.

4. **Describe the context window and its production implications.**

   *Answer shape:* The context window is the maximum number of tokens the model can process in a single call—input plus output combined. Production implications: you cannot fit an entire corpus in context; you must select what to include. Long contexts are expensive and slower. The "lost in the middle" problem means models are less reliable on information in the middle of a very long prompt. Design response: use RAG or selective context assembly to stay well within the window.

   *Strong signals:* Mentions lost-in-middle by name. Compares context window cost across model families. Notes KV cache as the mechanism behind context window limits. Connects to RAG as a complementary strategy.

   *Weak signals:* Says "it's how much the model can remember" without production implications.

5. **How would you estimate the cost of a production AI feature before building it?**

   *Answer shape:* Estimate: (1) typical prompt token count (system prompt + context + user message), (2) typical completion token count, (3) expected requests per day, (4) multiply by model pricing. Build a simple cost model: cost_per_request = (prompt_tokens × input_price) + (completion_tokens × output_price). Then multiply by QPS × seconds/day. Add a 2× buffer for outlier requests. Compare against the budget and decide if a cheaper model or prompt compression is needed.

   *Strong signals:* Walks through a real number. Mentions that most production queries have short completions but long prompts. Notes that caching repeated system prompts reduces cost significantly.

   *Weak signals:* Cannot produce a number. Relies on "it depends" without a framework.

### Follow-up questions

1. If a user reports that the AI response "feels random," what would you check first in the model configuration?
2. Your team wants to add a 10,000-token product catalog to the system prompt. What are the cost implications and what is the alternative?
3. How do you handle a model that returns truncated output because the completion hit the max_tokens limit?

---

## Drill Group 2: RAG and Citations

**References:** `docs/learning-fundamentals.md` → RAG, Embeddings, Retrieval  
**Related artifacts:** Lab 1 (RAG Baseline), Lab 2 (Chunking), Lab 10 (Long-context vs RAG) in `docs/practice.md`

### Core questions

1. **Explain RAG from first principles—why does it exist and what problem does it solve?**

   *Answer shape:* RAG exists because model weights are not a reliable source of fresh, private, or precise company knowledge. The model was trained on a static snapshot; your company's data changes daily. RAG separates knowledge (retrieved at query time) from reasoning (done by the model). The pipeline: embed the query → retrieve the most relevant chunks from a vector index → assemble prompt with retrieved context → generate grounded answer.

   *Strong signals:* Frames the problem before the solution. Mentions the three RAG failure modes: retrieval miss, hallucination despite retrieval, and context overflow. Compares to fine-tuning and explains why RAG is preferred for dynamic, private knowledge.

   *Weak signals:* Describes the pipeline without explaining why retrieval beats fine-tuning for this use case. Cannot name a failure mode.

2. **What is the impact of chunk size on retrieval quality? Walk me through the trade-offs.**

   *Answer shape:* Small chunks (50–100 tokens) have high recall precision—they retrieve exact passages—but miss context for questions that require surrounding information. Large chunks (500+ tokens) provide more context but reduce precision because the embedding averages over too much text. The right chunk size depends on the query type (precise lookup vs. broader context) and the embedding model's effective context window. Overlap (10–25%) helps when answers span chunk boundaries.

   *Strong signals:* Mentions hit@k as the metric for measuring chunking quality. Knows that semantic chunking (paragraph/section boundaries) often outperforms fixed-size for structured documents. Mentions the Lab 2 comparison approach.

   *Weak signals:* Says "smaller is better" or "larger is better" without trade-off reasoning.

3. **How do you ensure an AI answer includes accurate citations?**

   *Answer shape:* Citations require two things: (1) each retrieved chunk carries its source metadata (document ID, page, section), and (2) the prompt instructs the model to reference chunks by their IDs in the answer. After generation, validate that every cited chunk ID actually exists in the retrieved set—do not trust the model to invent valid IDs. For high-stakes applications, highlight the exact sentence in the source document that supports each claim.

   *Strong signals:* Distinguishes between model hallucinating a citation and the model correctly citing a retrieved chunk. Mentions that citation validation is a post-generation step. Notes the risk of the model citing chunk IDs that were not retrieved.

   *Weak signals:* Says "just tell the model to add citations" without a validation step.

4. **When would you choose long-context over RAG?**

   *Answer shape:* Choose long-context when: the entire corpus fits economically in the context window, documents change infrequently, you need comprehensive cross-document synthesis, and the model is large enough to handle the full context reliably. Choose RAG when: the corpus is too large for the context window, documents change frequently, cost-per-query must be minimized, or you need source-level attribution. The decision is quantitative—run both on a gold set and compare accuracy and cost.

   *Strong signals:* Mentions the lost-in-middle failure mode for long-context. Names a corpus size threshold. References Lab 10's comparison approach.

   *Weak signals:* Says "use RAG always" or "long context makes RAG obsolete."

5. **What is retrieval precision vs recall in the RAG context, and which matters more?**

   *Answer shape:* Precision: of the chunks retrieved, what fraction are relevant? Recall: of all relevant chunks in the corpus, what fraction did the retrieval return? For most RAG use cases, recall matters more—missing a relevant chunk means the answer is wrong. However, low precision adds noise that can mislead the model. The trade-off: increasing top-k improves recall but reduces precision. In practice, use a reranker to improve precision after a high-recall top-k retrieval.

   *Strong signals:* Frames this as a precision-recall trade-off, not a right/wrong question. Mentions reranking as the production solution. Knows that hit@k is the proxy metric used in practice.

   *Weak signals:* Cannot define both terms. Has no framework for the trade-off.

### Follow-up questions

1. A user says the RAG answer is correct but the cited source is wrong. What does that mean about your system?
2. You notice retrieval hit@5 is 0.9 on your gold set but production answer quality is poor. What could explain the gap?
3. How would you handle a RAG system where the documents contain tables and charts, not just prose?

---

## Drill Group 3: Evals and Quality Gates

**References:** `docs/learning-fundamentals.md` → Evals, LLM-as-Judge, Metrics  
**Related artifact:** Lab 4 (Gold-Set Eval) in `docs/practice.md`

### Core questions

1. **Why are evals the most important engineering practice in AI systems?**

   *Answer shape:* Without evals, every change is a guess. AI systems have non-deterministic behavior, and quality can degrade silently with a model update, a prompt change, or a data change. Evals are the regression test suite for AI. They catch quality regressions before users do, and they provide the evidence needed to justify design decisions to stakeholders.

   *Strong signals:* Draws an explicit analogy to software testing. Notes that evals run in CI/CD. Mentions that the gold set must be maintained like a codebase—it grows and is reviewed for quality.

   *Weak signals:* Says "evals check quality" without explaining when they run or what they prevent.

2. **Explain the three main eval approaches and when to use each.**

   *Answer shape:* (1) Exact match: deterministic, cheap, but brittle—fails when phrasing varies. Use for classification, structured outputs, and code. (2) LLM-as-judge: flexible, covers reasoning and explanation quality, but requires calibration and adds cost. Use for RAG answer quality, agent behavior, and open-ended responses. (3) Reference-based metrics (BERTScore, ROUGE): automatic, but don't capture reasoning or factual correctness well. Use as a cheap filter, not a primary signal. Most production systems combine (1) and (2).

   *Strong signals:* Knows the calibration problem for LLM-as-judge (judge must agree with humans on a calibration set). Mentions temperature=0 for consistent judging. Notes cost trade-off.

   *Weak signals:* Knows only one eval method. Cannot explain when exact match breaks down.

3. **How do you build a gold set, and how do you keep it trustworthy over time?**

   *Answer shape:* A gold set is a collection of (input, expected output) pairs created by humans who understand the domain. Build it by: sampling real user queries (not synthetic), having domain experts write the expected answers, and covering failure cases (ambiguous queries, out-of-scope, multi-hop reasoning). Keep it trustworthy by: version-controlling it, reviewing it when the product changes, flagging questions that become ambiguous after a system change, and adding new cases when production failures are discovered.

   *Strong signals:* Notes that synthetic gold sets have bias toward questions the model can already answer. Mentions coverage dimensions (query types, difficulty levels). Links to Lab 4 artifact.

   *Weak signals:* Says "just use 100 questions." No versioning or review process.

4. **What is faithfulness in RAG evals, and how is it different from correctness?**

   *Answer shape:* Faithfulness measures whether the answer is supported by the retrieved context—did the model make claims that are grounded in what was retrieved? Correctness measures whether the answer matches the true answer. A faithful answer can be incorrect if the retrieved context was wrong. A correct answer can be unfaithful if the model used pre-trained knowledge instead of the retrieved context (a form of hallucination). For RAG systems, faithfulness is the primary guardrail; correctness requires a gold set.

   *Strong signals:* Can name both metrics and explain the difference with an example. Mentions DeepEval or Ragas as implementation references.

   *Weak signals:* Uses "faithfulness" and "correctness" interchangeably.

5. **How would you add an eval gate to a CI/CD pipeline?**

   *Answer shape:* Create an eval job that runs on every pull request that modifies a prompt, retrieval config, or model version. The job: (1) runs the gold set through the pipeline, (2) calculates pass rate, (3) compares to the baseline stored in the previous run, (4) fails the PR if pass rate drops by more than a threshold (e.g., 5%). Store eval results as CI artifacts for audit. For expensive evals, run a smaller fast set on every PR and the full set on merges to main.

   *Strong signals:* Specifies the pass/fail threshold. Notes that the baseline must be stored and versioned. Mentions the cost/speed trade-off for PR vs merge evals.

   *Weak signals:* Says "add evals to CI" without specifying what triggers, what threshold, or what happens on failure.

### Follow-up questions

1. Your LLM-as-judge eval scores are inconsistent—the same question gets different scores on different runs. How do you fix this?
2. After a model provider upgrade, your pass rate dropped from 85% to 75%. What is your investigation process?
3. What is the difference between an eval and a monitor? When do you need both?

---

## Drill Group 4: AI Data Pipelines

**References:** `docs/learning-fundamentals.md` → Data Ingestion, Embeddings, Lineage  
**Related artifacts:** Lab 2 (Chunking), Lab 6 (Tracing) in `docs/practice.md`

### Core questions

1. **Describe the full AI data lifecycle from raw document to an answer citation.**

   *Answer shape:* Raw document → parse (extract text, tables, metadata) → chunk (split by size or structure) → embed (convert to vector) → index (store in vector DB with metadata) → retrieval (embed query, find nearest chunks) → generation (assemble prompt, call LLM) → citation (map answer back to source chunk and document). Each step can introduce data quality issues that affect the final answer.

   *Strong signals:* Names the failure mode at each step (bad parse → bad chunks → bad retrieval → hallucinated answer). Mentions that the citation step requires preserving source metadata through the entire pipeline.

   *Weak signals:* Describes only the happy path. Cannot name a failure mode.

2. **What are the challenges of ingesting PDFs and unstructured documents for RAG?**

   *Answer shape:* PDF challenges: (1) text extraction misses layout (multi-column, footnotes), (2) tables are extracted as raw text that loses column structure, (3) images and charts have no text, (4) scanned PDFs require OCR which adds latency and error rates, (5) page headers/footers pollute chunks. The engineering response: use a layout-aware parser (Unstructured, Docling), extract tables separately as structured data, run OCR for scanned content, and strip boilerplate before chunking.

   *Strong signals:* Mentions table extraction as a specific challenge. Knows what Unstructured or Docling does. Notes that OCR errors propagate through the pipeline.

   *Weak signals:* Says "just use a PDF parser" without naming the specific challenges.

3. **What is embedding drift, and how do you manage it?**

   *Answer shape:* Embedding drift occurs when you change the embedding model (upgrade, replace, or retrain) and the new model produces different vector representations. Existing vectors in the index become semantically incompatible with new query embeddings, causing retrieval degradation. Management: version your embedding model. When you change models, re-embed the entire corpus and rebuild the index. Test retrieval quality before and after the migration using a gold set.

   *Strong signals:* Explains the mechanism (vector incompatibility). Has a migration plan. Mentions that the migration must be atomic—you cannot mix old and new embeddings in the same index.

   *Weak signals:* Has not heard of the problem. Cannot say what would break.

4. **How do you track data lineage from a source document to an answer?**

   *Answer shape:* Lineage requires an ID to travel through the entire pipeline: document_id → chunk_id → embedding_id → retrieval result → cited source in the answer. Every component in the pipeline must preserve and propagate these IDs. At generation time, the prompt includes chunk IDs. The response includes which chunk IDs were cited. The audit log maps query → retrieved chunk IDs → document IDs. This lets you trace back any answer to its source document and chunk.

   *Strong signals:* Specifies the ID chain. Notes that this is required for debugging and for compliance (knowing what data the model saw).

   *Weak signals:* Says "track the source document" without specifying the granularity.

5. **How would you implement incremental indexing for a corpus that changes daily?**

   *Answer shape:* Incremental indexing requires: (1) change detection (compare document checksums or modification timestamps against a last-indexed record), (2) re-embed and re-index only changed or new documents, (3) delete stale chunks for documents that were updated or removed, (4) test retrieval quality after each update. The simplest approach: a daily job that scans the document store for changes, processes deltas, and runs a smoke-test eval on a small gold set before promoting the index.

   *Strong signals:* Handles deletions (stale chunk removal) as well as insertions. Mentions the eval after update. Notes that partial updates can create inconsistent indexes if the job fails midway (idempotency matters).

   *Weak signals:* Describes only adding new documents, not updating or removing stale ones.

### Follow-up questions

1. You notice that ingestion quality dropped after a document format changed from HTML to PDF. What is your debugging process?
2. A compliance team asks which documents were used to generate a specific customer-facing answer. How does your system support this?
3. Your embedding model costs $0.0001 per 1,000 tokens. The corpus is 100 million tokens. What is the re-embedding cost, and when is it acceptable to pay it?

---

## Drill Group 5: Agents, Tools, and MCP

**References:** `docs/learning-fundamentals.md` → Agents, Tool Calling, MCP  
**Related artifact:** Lab 5 (Tool/MCP Governance) in `docs/practice.md`

### Core questions

1. **What is the difference between an agent workflow and an autonomous agent?**

   *Answer shape:* An agent workflow is a deterministic sequence of LLM calls and tool calls orchestrated by code—the flow is decided by the programmer, not the model. An autonomous agent lets the model decide which tools to call, in what order, and when to stop. Workflows are predictable, testable, and appropriate for most production use cases. Autonomous agents are flexible but unpredictable, expensive, and risky for write operations. The engineering principle: start with a workflow; add autonomy only when the workflow cannot handle the required decision space.

   *Strong signals:* Uses the terms clearly and correctly. Notes that "agent" is often over-used in marketing. Can give examples of when each is appropriate.

   *Weak signals:* Uses "agent" and "workflow" interchangeably.

2. **Explain the security threat model for tool-calling agents.**

   *Answer shape:* The primary risks: (1) prompt injection through tool inputs—malicious data in a tool response tells the model to perform unauthorized actions, (2) tool abuse—the model calls a tool with valid-schema but dangerous arguments, (3) privilege escalation—a read-only agent gains write access by chaining tool calls, (4) exfiltration—the model is instructed to send sensitive data to an external endpoint via a tool call. Defense: least privilege (tools declare their capabilities and the gateway enforces them), approval gates for write tools, output guardrails, and audit logs for every tool call.

   *Strong signals:* Names indirect prompt injection specifically. Mentions the approval gate as a control. Notes that audit logs are non-optional.

   *Weak signals:* Says "don't let the agent do bad things" without a mechanism.

3. **What is MCP, and what problem does it solve for AI systems?**

   *Answer shape:* Model Context Protocol is an open standard for connecting AI models to tools, data sources, and services in a host-agnostic way. Before MCP, every AI application had to build its own tool integration layer. MCP defines a standard server/client protocol so a tool server can work with any MCP-compatible client (IDE, agent framework, custom application). It solves the N×M integration problem: N clients × M tools becomes N + M implementations.

   *Strong signals:* Can draw the server/client boundary. Knows the three MCP resource types: tools, resources, and prompts. Notes that MCP does not solve authorization—that is the host's responsibility.

   *Weak signals:* Says "MCP is a framework for agents" without describing the interoperability benefit.

4. **How do you design a tool contract for an agent system?**

   *Answer shape:* A tool contract defines: name, description (what the tool does in natural language for the model to interpret), input schema (typed JSON Schema or Pydantic), output schema, risk level (read/write/admin), rate limits, and approval requirements. The description is as important as the schema because the model uses it to decide when to call the tool. Input validation should happen at the tool boundary, not inside the tool implementation.

   *Strong signals:* Emphasizes the description quality. Notes that schema validation should be at the perimeter. Mentions that tool descriptions are part of the prompt and consume tokens.

   *Weak signals:* Focuses only on the input schema. Ignores risk classification.

5. **When does an agentic loop fail, and how do you detect it?**

   *Answer shape:* Agentic loop failures: (1) infinite loop—the model keeps calling tools without converging on an answer, (2) tool call storm—exponentially increasing tool calls due to a planning error, (3) context overflow—the conversation history grows beyond the context window after many tool calls, (4) stuck state—the model cannot make progress because a required tool is unavailable. Detection: max iterations limit, timeout per request, context window monitoring, tool call rate limit per session. Observability: trace every tool call with a span; alert when a session exceeds N tool calls.

   *Strong signals:* Names all four failure modes. Has a detection mechanism for each. Links to Lab 5 tracing artifact.

   *Weak signals:* Knows about infinite loops but not the others.

### Follow-up questions

1. A user complains that your agent deleted a file it should not have touched. What is your post-incident investigation process?
2. How would you test an agent's behavior on adversarial tool inputs before deploying it to production?
3. Your MCP tool server is shared across five different AI applications. How do you enforce per-application authorization?

---

## Drill Group 6: Observability and Debugging

**References:** `docs/learning-fundamentals.md` → Observability, OpenTelemetry  
**Related artifact:** Lab 6 (Trace and Observability) in `docs/practice.md`

### Core questions

1. **What should a production AI trace include that a standard service trace does not?**

   *Answer shape:* Standard service traces cover request lifecycle, latency, and errors. AI traces additionally need: model name and version, prompt token count, completion token count, retrieval metadata (chunks retrieved, similarity scores), LLM call latency separated from total request latency, cost per call, eval metric scores for sampled requests, and tool call details (name, arguments, outcome). These are the signals that let you diagnose quality and cost regressions, not just latency spikes.

   *Strong signals:* Lists token counts and cost as first-class trace attributes. Mentions eval scores as an operational signal. Notes that retrieval latency and LLM latency are separate and both important.

   *Weak signals:* Says "same as regular tracing, plus the LLM call."

2. **How do you debug a case where an AI answer is wrong but the logs show no error?**

   *Answer shape:* Investigate in this order: (1) check the trace—what chunks were retrieved? Was the relevant chunk in the top-k? (2) check the prompt assembly—was the context correctly formatted and within the token limit? (3) check for lost-in-middle—was the relevant chunk in the middle of a very long context? (4) check the eval score—was the answer judged as faithful but incorrect (model used pre-trained knowledge instead of retrieved context)? (5) check the model version—did a silent model update change behavior?

   *Strong signals:* Starts with traces, not logs. Follows a structured hypothesis-elimination process. Notes that the problem is often retrieval, not generation.

   *Weak signals:* Says "add more logs" without a diagnostic framework.

3. **What OpenTelemetry semantic conventions exist for LLM systems?**

   *Answer shape:* The OTel semantic conventions for LLM include: `gen_ai.system` (e.g., "openai"), `gen_ai.request.model`, `gen_ai.request.max_tokens`, `gen_ai.response.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `gen_ai.request.temperature`. These are standard attributes that observability backends can parse and aggregate without custom configuration. OpenLLMetry implements these conventions automatically for common model SDKs.

   *Strong signals:* Knows the `gen_ai.*` namespace. Notes that the conventions are still stabilizing. Can name at least 4–5 attributes.

   *Weak signals:* Knows OTel exists but cannot name any LLM-specific attributes.

4. **How do you set up alerting for AI quality degradation in production?**

   *Answer shape:* Two approaches: (1) Online eval sampling—run an LLM-as-judge eval on a random sample of production requests and alert when the rolling average falls below a threshold. (2) Proxy metrics—alert when retrieval hit rate drops, when model returns a specific refusal pattern at an unusual rate, or when completion length drops unexpectedly. Combine both: proxy metrics are cheap and fast, online evals are expensive but accurate. Alert on proxy metrics; investigate with online evals.

   *Strong signals:* Distinguishes between proxy metrics and direct eval signals. Notes the cost trade-off. Has a specific threshold in mind.

   *Weak signals:* Says "monitor error rates" without AI-specific signals.

5. **What is the difference between tracing and logging for AI systems, and when do you use each?**

   *Answer shape:* Logs are discrete events: a request started, an error occurred, a tool was called. Traces are causally connected spans showing how a request moved through the system. For AI systems, traces are more valuable for debugging because they show the full context: which chunks were retrieved, how long the LLM took, whether a tool call succeeded—all causally linked to a single user request. Logs are valuable for auditing (what the model was asked, what it returned) and for compliance. Use structured logs for audit; use traces for debugging.

   *Strong signals:* Explains causality in traces vs. event independence in logs. Notes that audit logs are a compliance artifact with different retention requirements.

   *Weak signals:* Says "logs are more detailed." No distinction in purpose.

### Follow-up questions

1. You notice your AI feature's p95 latency doubled after a prompt change. How do you diagnose whether the cause is the prompt or the model?
2. How would you reduce observability cost when you are generating one million LLM calls per day?
3. A security audit asks for evidence of what every AI agent did over the last 30 days. What does your system need to support this?

---

## Drill Group 7: Security and Governance

**References:** `docs/learning-fundamentals.md` → Security, OWASP LLM Top 10, Governance  
**Related artifact:** Lab 7 (Prompt Injection Drill) in `docs/practice.md`

### Core questions

1. **What is prompt injection, and why is it the top LLM security risk?**

   *Answer shape:* Prompt injection is an attack where malicious input—from a user, a retrieved document, or a tool response—instructs the model to override its system prompt or perform unauthorized actions. It is the top risk because the model has no built-in mechanism to distinguish trusted instructions from untrusted data. Direct injection: the user crafts a prompt that overrides instructions. Indirect injection: malicious instructions are embedded in a document or tool response that the model processes. The model follows them because it treats all input as instructions.

   *Strong signals:* Distinguishes direct and indirect injection. Notes that retrieval systems are a common vector for indirect injection. Names at least one mitigation.

   *Weak signals:* Knows the name but cannot explain the mechanism.

2. **What is the OWASP Top 10 for LLM Applications, and which items matter most for production AI systems?**

   *Answer shape:* The OWASP LLM Top 10 covers: (1) prompt injection, (2) insecure output handling (trusting model output without validation), (3) training data poisoning, (4) model denial of service, (5) supply chain vulnerabilities, (6) sensitive information disclosure, (7) insecure plugin design, (8) excessive agency, (9) overreliance, (10) model theft. For production AI systems, the most operationally relevant: #1 (prompt injection), #2 (insecure output handling), #6 (data disclosure), #7 (insecure tool design), #8 (excessive agency). These are the ones that cause production incidents.

   *Strong signals:* Can name five or more items with brief explanations. Links #7 and #8 to the tool governance lab. Notes that these map to real incident categories.

   *Weak signals:* Knows #1 (prompt injection) and cannot name others.

3. **How do you implement PII redaction in an AI pipeline?**

   *Answer shape:* PII redaction has two sites: (1) at ingestion—strip or pseudonymize PII before documents enter the vector index so it is never retrieved, and (2) at output—scan model responses before returning them to users and redact or block PII that was not supposed to be disclosed. For ingestion: use a named entity recognizer or regex patterns for known PII types (email, phone, SSN). For output: use a classifier or guardrail model. Log all redaction events for audit. Note: redaction is imperfect; defense in depth (access control, data minimization) is more reliable than redaction alone.

   *Strong signals:* Handles both ingestion and output. Notes the limitation of regex-based approaches. Mentions audit logging. Notes defense-in-depth over single-point redaction.

   *Weak signals:* Says "remove PII from the data" without specifying how or where.

4. **What is a model card, and when is one required?**

   *Answer shape:* A model card is a documentation artifact that describes: the model's intended use, training data sources and cutoff, known limitations and failure modes, evaluation results (performance on benchmark tasks), fairness and bias evaluation, and recommendations for use and non-use. It is required when: deploying a fine-tuned model, using a model in a regulated context (healthcare, finance, HR), publishing a model publicly, or when a compliance or legal team asks for evidence of responsible AI practice. Even for third-party models, a system-level card documents how the model is used in your system.

   *Strong signals:* Knows the content of a model card. Can name at least two contexts where one is required. Notes that system-level documentation is needed even for hosted models.

   *Weak signals:* Says "it's documentation about the model" without specifics.

5. **How do you design an audit log for an AI system to meet compliance requirements?**

   *Answer shape:* The audit log must capture: (1) who made the request (user ID, role), (2) what the model received (prompt, retrieved chunks, tool calls), (3) what the model returned (response, citations), (4) model and prompt version, (5) timestamp, and (6) any safety flags or redactions triggered. The log must be tamper-evident (append-only, checksum-verified), retained for the required period, and queryable by request ID and user ID. Do not log full prompt text if it contains PII—log a hash or a sanitized version.

   *Strong signals:* Specifies all six fields. Notes tamper-evidence. Addresses PII in logs. Mentions retention requirements.

   *Weak signals:* Says "log the requests and responses" without specifying the fields or compliance requirements.

### Follow-up questions

1. You discover that a retrieved document contained a prompt injection instruction that caused your AI agent to send a Slack message to an unexpected channel. Walk me through your incident response.
2. How do you test for prompt injection vulnerabilities before releasing a new AI feature?
3. Your company is entering a regulated industry (finance). What governance artifacts do you need to produce for the AI system?

---

## Drill Group 8: Serving, Latency, and Cost

**References:** `docs/learning-fundamentals.md` → Serving, Inference, KV Cache  
**Related artifact:** Lab 9 (Serving Benchmark) in `docs/practice.md`

### Core questions

1. **Explain TTFT and TPOT, and why both matter for user experience.**

   *Answer shape:* TTFT (time to first token) is the latency from sending a request to receiving the first token of the response. It determines how quickly a user sees something. TPOT (time per output token) is the average time to generate each subsequent token. It determines how fast the response completes in streaming mode. Users perceive TTFT as "is it working?" and TPOT as "how fast is it typing?". A high TTFT feels broken; a high TPOT feels slow. TTFT is dominated by prefill time and queue wait; TPOT is dominated by memory bandwidth and batch size.

   *Strong signals:* Explains both in terms of user perception, not just mechanics. Notes that prefill dominates TTFT for long prompts. Mentions that TPOT improves with batching.

   *Weak signals:* Says "TTFT is how long until the answer starts" without production implications.

2. **What is KV cache, and how does it affect serving performance?**

   *Answer shape:* The KV cache stores the key-value attention computation for tokens that have already been processed. In autoregressive generation, each new token attends to all previous tokens. Without caching, this would require recomputing attention for all previous tokens on every step. KV cache stores these computations and reuses them. It reduces TPOT significantly by avoiding recomputation. Prefix caching extends this to the system prompt: if many requests share the same system prompt, cache the KV state for that prefix and reuse it across requests.

   *Strong signals:* Explains recomputation avoidance. Notes that KV cache size limits the context window for concurrent requests. Mentions prefix caching as a cost reduction technique.

   *Weak signals:* Says "it caches things to make it faster" without the mechanism.

3. **What is continuous batching, and why is it important for throughput?**

   *Answer shape:* Without continuous batching, a batch of requests must all complete before new requests are added—meaning a short request waits for a long one to finish. Continuous batching allows new requests to join the batch as slots become available, after each generated token. This dramatically improves GPU utilization because the hardware is never idle waiting for long requests. It is a key reason why vLLM achieves much higher throughput than naive serving.

   *Strong signals:* Explains the slot-based intuition. Notes that this is a vLLM/TGI innovation, not standard transformer inference. Connects to throughput vs. latency trade-off.

   *Weak signals:* Knows batching improves throughput but cannot explain continuous vs. static batching.

4. **How do you decide between hosted API inference and self-hosted inference?**

   *Answer shape:* The decision factors: (1) cost—at high volume (millions of requests/day), self-hosted GPU is cheaper per token; at low volume, hosted is cheaper because there is no fixed infrastructure cost; (2) latency SLAs—self-hosted can be tuned for your specific workload; hosted may have variable latency; (3) data privacy—self-hosted keeps data entirely in your network; (4) model availability—hosted gives access to frontier models (GPT-4o, Claude); self-hosted is limited to open models; (5) operational overhead—self-hosted adds GPU cluster management. Run a cost model and evaluate each dimension for your use case.

   *Strong signals:* Has a framework with five dimensions. Mentions the volume breakeven calculation. Notes that data privacy is sometimes non-negotiable.

   *Weak signals:* Says "self-hosted is cheaper" or "hosted is easier" without trade-off reasoning.

5. **What is quantization, and what is the quality trade-off?**

   *Answer shape:* Quantization reduces the precision of model weights from float32 or bfloat16 to int8, int4, or lower. This reduces model size (fewer bytes per parameter), reduces memory bandwidth requirements (faster inference), and allows larger models to fit on smaller hardware. The quality trade-off: lower precision introduces rounding errors in the weight values, which can degrade model quality—especially at very low precision (int4 or below). In practice, 8-bit quantization has minimal quality loss; 4-bit quantization (QLoRA, GPTQ, GGUF) has small but measurable quality degradation on benchmarks.

   *Strong signals:* Explains the memory-bandwidth and quality trade-off. Notes that the quality impact depends on the task (factual recall degrades more than creative tasks). Mentions GGUF and GPTQ as common formats.

   *Weak signals:* Says "quantization makes the model smaller" without quality trade-off reasoning.

### Follow-up questions

1. Your model serving TTFT p95 is 8 seconds for long prompts. What are three optimizations you would investigate first?
2. How does prompt caching work in the OpenAI or Anthropic API, and when does it apply?
3. You need to serve a 70B model on a budget. Walk me through the hardware and quantization options.

---

## Drill Group 9: Staff System Design Narrative

**References:** All fundamentals sections. Uses artifacts from all labs in `docs/practice.md`.

This group practices the end-to-end system design narrative. Unlike the other groups, these questions require 5–10 minutes to answer well. Use them for mock interviews.

### Core questions

1. **Design a production RAG system for an internal ops knowledge base. Walk through every design decision.**

   *Answer shape:* Start with requirements: query types, corpus size, freshness requirements, latency SLA, cost budget, and audience. Then walk through: ingestion pipeline (parser, chunker, embedding model, index), retrieval design (vector store, top-k, reranker), generation design (model choice, prompt template, citations), eval system (gold set, metrics, CI gate), observability (traces, cost tracking, quality sampling), security (prompt injection guards, output guardrails, audit log), and operations (incremental indexing, embedding drift, model versioning). Name a trade-off at each layer.

   *Strong signals:* Covers all seven layers. Starts with requirements before design. Names at least one trade-off per layer. Connects design decisions to specific project artifacts (labs 1, 2, 4, 6, 7).

   *Weak signals:* Covers RAG pipeline but skips eval, security, or operations.

2. **You are the Staff engineer responsible for a multi-tenant AI platform. How do you design it?**

   *Answer shape:* Multi-tenancy requires isolation at: (1) data—each tenant's knowledge base is isolated in separate namespaces or separate indexes; (2) auth—every request is scoped to a tenant identity and validated at the gateway; (3) cost—per-tenant token spend is attributed and budget limits are enforced; (4) tools—tenant A's tools are not visible to tenant B's agents; (5) audit—logs are tenant-scoped and queryable per tenant. The gateway is the enforcement point for all five. It handles auth, routing, budget gates, rate limiting, and audit logging before any request reaches the model or retrieval layer.

   *Strong signals:* Names the gateway as the enforcement point. Covers all five isolation dimensions. Notes that index isolation is the hardest to get right at scale.

   *Weak signals:* Covers auth and cost but misses data isolation or tool isolation.

3. **How would you reduce the cost of an AI feature that is overrunning its budget by 3×?**

   *Answer shape:* Diagnose first: trace cost per request and identify the top spenders (model tier, prompt size, or frequency). Then apply levers in order of impact: (1) prompt caching for repeated system prompts; (2) reduce retrieved context size (smaller chunks, lower top-k with better reranking); (3) switch to a cheaper model tier for simpler queries (routing); (4) add a budget gate that returns a degraded response when per-request cost exceeds threshold; (5) batch low-priority requests. Measure cost reduction after each change.

   *Strong signals:* Diagnoses before acting. Uses data from traces, not intuition. Applies levers in order of impact. Tests after each change.

   *Weak signals:* Goes straight to "use a cheaper model" without diagnosis.

4. **An AI agent caused a production incident by calling a third-party API 500 times in one minute. Design the controls that would prevent this.**

   *Answer shape:* Incident post-mortem first: what chain of tool calls led to 500 API calls? Was it a planning loop, a retry storm, or a misunderstanding of the tool's purpose? Controls: (1) per-session tool call limit (hard stop at N calls per session); (2) per-tool rate limit enforced at the gateway (not inside the tool); (3) approval gate for any tool that makes external writes; (4) timeout per agent session (hard wall-clock limit); (5) circuit breaker on the third-party API integration (stop calling after N consecutive failures); (6) alert when any session exceeds 50 tool calls. The root cause is usually missing limits, not a model failure.

   *Strong signals:* Post-mortem analysis first. Has at least five controls. Notes that the root cause is missing limits, not a model bug.

   *Weak signals:* Says "add rate limiting" without specifying where or how.

5. **How would you argue for investing in evals to a skeptical engineering director?**

   *Answer shape:* Frame it as risk and velocity, not research. Without evals: (1) every prompt or model change is a production gamble—you cannot know if you improved or regressed; (2) incidents happen silently—quality degrades before users complain; (3) model upgrades require manual testing each time. With evals: (1) changes are safe to deploy with a CI gate; (2) regressions are caught in minutes, not after user complaints; (3) model upgrades can be automated. The investment is comparable to writing tests for a critical backend service. Ask the director: "Would you deploy a payments service without integration tests?"

   *Strong signals:* Business-first framing. Quantifies the risk of not having evals. Draws an analogy the director already values.

   *Weak signals:* Argues for evals on technical grounds alone. Cannot translate to business risk.

### Follow-up questions

1. Your Staff design review panel asks: "What would you change if this system needed to handle 10× the current query volume?" Walk through your scaling strategy.
2. You are joining a team that has a working AI feature but no evals, no traces, and no cost attribution. What do you add first and why?
3. A product manager asks: "Can we use GPT-4o for everything?" How do you structure your response?
