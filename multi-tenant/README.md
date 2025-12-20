# OpsPilot Layer 1 (Multi-Tenant Demo Data)

This folder contains **multi-tenant sample data** for OpsPilot Layer 1 demos:

- **Three tenants**: `tenant-alpha`, `tenant-beta`, `tenant-gamma`
- **Multi-service**: `checkout-api`, `payment-gw`, `data-ingestor`, `ml-serving`, plus `platform-infra` and `shared-infra`
- **RAG-ready KB**: Markdown runbooks keyed by `ERR_*` codes (subset of Layer 0 runbooks)
- **Partitioned data**: All logs/incidents include `tenant_id` for multi-tenant filtering demos

## What's inside

- `knowledge_base/runbooks/`
  - **20** Markdown runbooks (subset covering DB, K8s, Data/ML, and Cost categories)
  - Each runbook has a unique **Error Code** (e.g., `ERR_DB_CON_001`)
- `data/`
  - `synthetic_logs.json`: structured logs with `tenant_id` field
  - `synthetic_incidents.json`: incident summaries with `tenant_id` + `runbook_refs` pointers
  - `cost_summaries.json`: daily spend per tenant + shared infra line items
- `scripts/`
  - `generate.py`: regenerates datasets deterministically

## Regenerate the dataset

From repo root:

```bash
python3 multi-tenant/scripts/generate.py --seed 42 --count 500 --out-dir multi-tenant/data
```

## How the KB maps to logs/incidents

- In `synthetic_logs.json`, failing entries include:
  - `tenant_id: "tenant-..."` and
  - `error_code: "ERR_..."` and
  - `message: "Failure: ERR_..."`
- In `synthetic_incidents.json`, each incident has:
  - `tenant_id: "tenant-..."`
  - `error_codes: ["ERR_..."]`
  - `runbook_refs: ["multi-tenant/knowledge_base/runbooks/ERR_...-....md"]`

This enables multi-tenant RAG retrieval with tenant-scoped vector DB namespaces or metadata filters.

## Differences from Layer 0

| Aspect | Layer 0 (`level_zero/`) | Layer 1 (`multi-tenant/`) |
|--------|-------------------------|---------------------------|
| Tenants | Single (`tenant-demo`) | Three (`alpha`, `beta`, `gamma`) |
| Runbooks | 50 | 20 (subset) |
| Hourly metrics | Yes | No (add as needed) |
| Use case | Simple RAG demo | Multi-tenant gateway + agent demos |
