# Contributing to OpsPilot (intelliOps)

Thanks for taking the time to contribute.

This repo is being built in layers (see `docs/roadmap.md`). For the day-by-day plan, see `docs/learning-book.md`. Please keep changes small, demoable, and well-documented.

## Quickstart for contributors

### Layer 0 dataset + CLI

Regenerate deterministic data:

```bash
python3 level_zero/scripts/generate_level_zero.py --seed 42 --hours 24 --out-dir level_zero/data
```

Run the deterministic CLI:

```bash
python3 level_zero/demo-cli-script/qa_cli.py \
  --question "What happened to checkout-api between 10-11am?"
```

### Multi-tenant dataset generator

```bash
python3 multi-tenant/scripts/generate.py --seed 42 --count 500 --incidents 8 --out-dir multi-tenant/data
```

## Branch naming (enforced on PRs)

Branch names must match:

- `^(feat|fix|docs|chore|refactor|test|ci|build|perf)/[a-z0-9]+(-[a-z0-9]+)*$`

Examples:
- `feat/tenant-routing`
- `fix/runbook-index`
- `docs/roadmap-layer2`

## PR titles (enforced on PRs)

PR titles must match:

- `^(feat|fix|docs|chore|refactor|test|ci|build|perf)(\([a-z0-9-]+\))?: .+`

Examples:
- `feat(level0): add deterministic dataset generator`
- `fix: correct multi-tenant runbook indexing`
- `docs(roadmap): clarify Layer 2 acceptance metrics`

## Commits (recommended)

We recommend (but do not enforce) Conventional Commits for commit messages:
- `feat: ...`
- `fix: ...`
- `docs: ...`
- `refactor: ...`
- `test: ...`
- `chore: ...`

Guidelines:
- Keep commits focused and reviewable
- Prefer squash-merge for PRs unless the commit history is meaningful

## Adding or editing runbooks

Runbooks are the core knowledge base and should be written to be:
- operationally actionable
- specific about checks/commands
- safe-by-default (call out risky steps)

### File naming

- File name format: `<ERROR_CODE>-<kebab-slug>.md`
- Example: `ERR_DB_CON_001-db-connection-pool-exhaustion.md`
- **Error codes must be unique** across runbooks in the same KB directory.

### Suggested runbook structure

Most runbooks in this repo follow:
- `# Title: ...`
- `## Metadata` (Service / Category / Severity)
- `## Symptoms`
- `## Root Cause Analysis (RCA)`
- `## Resolution Steps`
- `## Cost Impact (If applicable)`

### Cross-references

- If you add a new `ERR_*` code, consider updating the synthetic data generator(s) so the code can appear in incidents/logs.

## Security

If you believe you’ve found a security issue, please follow `SECURITY.md` (do not open a public issue with exploit details).

