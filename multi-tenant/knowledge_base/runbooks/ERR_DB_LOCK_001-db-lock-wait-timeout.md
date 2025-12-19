# Title: Database Lock Wait Timeout / High Lock Contention

## Metadata

- Service: checkout-api
- Category: Reliability
- Severity: P1

## Symptoms

- Error Codes: `ERR_DB_LOCK_001`
- Application logs:
  - `ERR_DB_LOCK_001 canceling statement due to lock timeout`
  - `SQLSTATE 55P03` (lock not available) / `lock timeout`
  - `could not obtain lock on relation`
- Database indicators:
  - Many sessions with `wait_event_type = 'Lock'`
  - Elevated `xact_commit`/`xact_rollback` imbalance (rollbacks increase)
  - API P95 latency > **2s** for **10m**

```sql
-- Show who is blocking whom
SELECT a.pid AS waiting_pid,
       pg_blocking_pids(a.pid) AS blocking_pids,
       now() - a.query_start AS waiting_age,
       left(a.query, 120) AS waiting_query
FROM pg_stat_activity a
WHERE cardinality(pg_blocking_pids(a.pid)) > 0
ORDER BY waiting_age DESC
LIMIT 20;
```

## Root Cause Analysis (RCA)

1. **Long-running transactions** hold locks (large batch updates, slow queries, external calls inside TX).
2. **DDL during peak** (ALTER TABLE, index rebuild) blocks writes/reads longer than expected.
3. **Hot tables/rows** (counters, per-tenant aggregates) cause high contention under concurrency.

## Resolution Steps

1. Confirm lock contention symptoms in app logs and DB wait events.

```bash
kubectl -n prod logs deploy/checkout-api --since=30m | egrep -n "ERR_DB_LOCK_001|lock timeout|55P03|could not obtain lock"
```

2. Identify the blocking session(s) and what they are doing.

```sql
-- Details for blocking sessions
SELECT pid, usename, application_name,
       now() - xact_start AS xact_age,
       state, wait_event_type, wait_event,
       left(query, 160) AS query_sample
FROM pg_stat_activity
WHERE pid = ANY(<blocking_pids_array>);
```

3. Immediate mitigation:
   - If safe, terminate the blocker to unblock the fleet (use cautiously).

```sql
SELECT pg_terminate_backend(<blocking_pid>);
```

   - Pause/rollback long-running migration jobs.
   - Reduce write concurrency temporarily (scale down writers / disable batch job).

```bash
kubectl -n prod scale deploy/checkout-api --replicas=1
```

4. Add guardrails:
   - Set `lock_timeout` for the application role to fail fast instead of piling up.

```sql
ALTER ROLE appuser SET lock_timeout = '2s';
```

   - Ensure `statement_timeout` is set to prevent runaway lock holders.

```sql
ALTER ROLE appuser SET statement_timeout = '30s';
```

5. Long-term fixes:
   - Shorten transactions and remove external calls inside TX boundaries.
   - Add missing indexes to reduce lock duration and touched rows.
   - Use row-level locking patterns (`SKIP LOCKED`) for workers.
   - Schedule DDL in maintenance windows; prefer online migration patterns.

6. Verification:
   - Lock waits drop; `pg_blocking_pids()` returns empty for most sessions
   - Latency and error rates normalize

## Cost Impact (If applicable)

- Lock contention increases compute usage due to retries/timeouts and can drive over-scaling.
- Fixing contention avoids unnecessary pod scaling and DB up-sizing.

---


