# IntelliOps (OpsPilot)

IntelliOps (OpsPilot) is a **production-shaped Ops + FinOps copilot project**: runbooks + deterministic incident/cost datasets today, and a clear path toward a secure, observable, multi-tenant LLM gateway.

This is an actively built project. The repo is structured to look like something a platform/infra team could evolve into a real internal product.

## What exists today

- Deterministic synthetic datasets for incidents/logs/metrics/cost (single-tenant + multi-tenant)
- A runbook knowledge base (Markdown) designed for retrieval and operational action
- A deterministic CLI baseline (no LLM required) for time-window incident Q&A

## Repository layout

- `level_zero/`: single-tenant dataset + runbooks + deterministic CLI baseline
- `multi-tenant/`: multi-tenant dataset generator + runbooks (tenant partitioning scaffold)
- `docs/`: architecture + ADRs + product roadmap

## Quickstart

Prereqs: `python3`

Generate the Layer 0 dataset (deterministic):

```bash
python3 level_zero/scripts/generate_level_zero.py --seed 42 --hours 24 --out-dir level_zero/data
```

Ask a question using the deterministic CLI:

```bash
python3 level_zero/demo-cli-script/qa_cli.py \
  --question "What happened to checkout-api between 10-11am?"
```

Regenerate the multi-tenant sample datasets:

```bash
python3 multi-tenant/scripts/generate.py --seed 42 --count 500 --incidents 8 --out-dir multi-tenant/data
```

## Data formats (why there are multiple)

To better mirror production pipelines, datasets include both “raw-ish” and structured forms:

- raw logs: `*.raw.txt` (+ `*.gz`)
- structured logs: `synthetic_logs.json`
- incidents: `synthetic_incidents.json` and `synthetic_incidents.jsonl` (+ `*.gz`)
- metrics/cost: JSON plus CSV (+ `*.gz`)

## Documentation

- Architecture: `docs/architecture.md`
- Roadmap: `docs/roadmap.md`
- Decisions (ADRs): `docs/decisions/`

## Development resources

Additional development guides, implementation details, and reference materials are available on the `learning-resources` branch.

```bash
git checkout learning-resources
```

## Contributing

See `CONTRIBUTING.md`.

## Security

See `SECURITY.md`.

## License

Apache-2.0. See `LICENSE`.
