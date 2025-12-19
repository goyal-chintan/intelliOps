# Title: DB Migration Causing Locks / Downtime (DDL Blocking)

## Metadata

- Service: checkout-api
- Category: Reliability
- Severity: P1

## Symptoms

- Error Codes: `ERR_DB_MIG_001`
- Timing:
  - Incident starts immediately after a deploy/migration job
- Logs (common patterns):
  - `ERR_DB_MIG_001 migration blocking`
  - `lock timeout` / `could not obtain lock on relation`
  - Elevated `statement timeout` during deploy window
- DB symptoms:
  - Many sessions waiting on locks
  - DDL statement running for minutes (ALTER TABLE, index operations)

## Root Cause Analysis (RCA)

1. **Blocking DDL** executed during peak traffic (ALTER TABLE that takes ACCESS EXCLUSIVE lock).
2. **Migration tool runs in a single transaction** and holds locks longer than expected.
3. **Large table/index** makes the DDL operation slow (rewrites table, rebuilds indexes).

## Resolution Steps

1. Identify the migration job/pod and correlate start time.

```bash
kubectl -n prod get jobs
kubectl -n prod logs job/<migration-job> --since=60m | egrep -n "ERR_DB_MIG_001|ALTER TABLE|CREATE INDEX|migration"
kubectl -n prod rollout history deploy/checkout-api
```

2. Find blockers/lock waits (Postgres).

```sql
SELECT a.pid,
       now() - a.query_start AS age,
       a.wait_event_type,
       a.wait_event,
       left(a.query, 160) AS query_sample,
       pg_blocking_pids(a.pid) AS blocking_pids
FROM pg_stat_activity a
WHERE a.state <> 'idle'
ORDER BY age DESC
LIMIT 30;
```

3. Immediate mitigation:
   - If the migration is actively blocking and safe to stop, cancel it.

```sql
SELECT pg_cancel_backend(<migration_pid>);
-- If it doesn't stop:
SELECT pg_terminate_backend(<migration_pid>);
```

4. If the schema change is required, switch to safer patterns:
   - Use `CREATE INDEX CONCURRENTLY` in Postgres
   - Add columns without default; backfill in batches; then set default
   - Use online migration tooling where possible

```sql
-- Example safe index build
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_created_at ON orders (created_at);
```

5. Put guardrails in place:
   - Run migrations in maintenance windows.
   - Add `lock_timeout` and `statement_timeout` for migration role.

```sql
ALTER ROLE migrator SET lock_timeout = '2s';
ALTER ROLE migrator SET statement_timeout = '10min';
```

6. Verification:
   - Lock waits drop and API latency normalizes
   - Migration completes safely (or is rescheduled)

## Cost Impact (If applicable)

- Failed migrations often trigger emergency scale-ups and retries; online/safer migrations reduce operational cost and avoid unnecessary DB scaling.

---


