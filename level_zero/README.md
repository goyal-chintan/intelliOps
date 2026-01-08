# OpsPilot Layer 0 (Single-Tenant Demo)

This folder is a **self-contained Layer 0 demo** for OpsPilot:

- **Single tenant**: `tenant_id = tenant-demo`
- **Multi-service**: `checkout-api`, `payment-gw`, `data-ingestor`, `ml-serving`, plus `platform-infra`
- **RAG-ready KB**: Markdown runbooks keyed by `ERR_*` codes
- **Incident-shaped data**: incidents derived from logs and cost anomalies
- **Hourly metrics**: simple aggregates derived from logs for “what happened between 10–11am?” demos

## What’s inside

- `knowledge_base/runbooks/`
  - **50** Markdown runbooks.
  - Each runbook has a unique **Error Code** (e.g., `ERR_DB_CON_001`) used for retrieval.
- `data/`
  - `synthetic_logs.raw.txt`: raw log lines (single tenant, multi-service)
  - `synthetic_logs.raw.txt.gz`: compressed raw logs
  - `synthetic_logs.json`: parsed/structured logs (JSON)
  - `synthetic_incidents.json`: incident summaries + `runbook_refs` pointers
  - `synthetic_incidents.jsonl`: line-delimited incidents (raw-ish)
  - `synthetic_incidents.jsonl.gz`: compressed incidents
  - `hourly_metrics.json`: per-hour aggregates per service
  - `hourly_metrics.csv`: raw metrics table (CSV)
  - `hourly_metrics.csv.gz`: compressed metrics
  - `cost_summaries.json`: daily spend + shared infra line items
  - `cost_summaries.csv`: raw cost table (CSV)
  - `cost_summaries.csv.gz`: compressed cost table

Note: In real systems logs are raw at ingest and get parsed/structured downstream for querying.
This demo stores logs as normalized JSON for deterministic, repeatable examples.

- `scripts/`
  - `generate_level_zero.py`: generates the Layer 0 datasets deterministically
- `api/` (optional, demo scaffold)
  - You can add a simple RAG CLI/API here later; Layer 0 doesn’t require multi-tenant routing.

## Regenerate the Layer 0 dataset

From repo root:

```bash
python3 level_zero/scripts/generate_level_zero.py --seed 42 --hours 24 --out-dir level_zero/data
```

This keeps timestamps stable (fixed base date `2025-01-01`) so demos like “between **10–11am**” are consistent.

## How the KB maps to logs/incidents

- In `synthetic_logs.json`, failing entries use:
  - `error_code: "ERR_..."` and
  - `message: "Failure: ERR_..."`
- In `synthetic_incidents.json`, each incident has:
  - `error_codes: ["ERR_..."]` and
  - `runbook_refs: ["level_zero/knowledge_base/runbooks/ERR_...-....md"]`

This makes it easy for RAG retrieval and agentic workflows to do:

**logs → incident summary → runbook remediation steps**

