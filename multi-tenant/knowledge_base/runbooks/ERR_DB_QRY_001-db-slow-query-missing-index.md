# Title: Database Slow Queries (Missing Index / Sequential Scan)

## Metadata

- Service: checkout-api
- Category: Performance
- Severity: P1

## Symptoms

- Error Codes: `ERR_DB_QRY_001`
- Latency: API latency P95 increases by **> 2x baseline for 10m** and DB time dominates traces/spans
- Database metrics:
  - `DatabaseCPUUtilization > 80% for 10m` (RDS/Aurora)
  - `ReadIOPS` or `ReadLatency` spikes vs baseline
- Logs / traces (common patterns):
  - Postgres slow query log shows `duration: > 1000 ms` for the same statement
  - APM spans: `db.statement` > **500ms** for top endpoints
  - App error: `ERR_DB_QRY_001 query exceeded 2s` / `statement timeout`

## Root Cause Analysis (RCA)

1. **Missing or wrong index** for a high‑traffic predicate/join → sequential scans on large tables.
2. **High-cardinality filters + large tables** (or unbounded queries) → too many rows scanned/returned.
3. **Table bloat / stale statistics** → planner chooses inefficient plans (scan + filter instead of index).

## Resolution Steps

1. Identify the top slow query and its frequency.

```sql
-- If pg_stat_statements is enabled
SELECT calls,
       round(total_exec_time::numeric, 2) AS total_ms,
       round(mean_exec_time::numeric, 2) AS avg_ms,
       rows,
       left(query, 160) AS query_sample
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;
```

2. Run `EXPLAIN (ANALYZE, BUFFERS)` for the exact query (use a safe/representative parameter set).

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT /* paste the slow query here */;
```

3. If you see `Seq Scan` with high `rows` read:
   - Create the appropriate index (use `CONCURRENTLY` in production).

```sql
-- Example index (adapt columns/order to the query predicates)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_tenant_status_created_at
ON orders (tenant_id, status, created_at DESC);
```

4. Refresh stats after index creation.

```sql
ANALYZE orders;
```

5. If the table is bloated (common for heavy UPDATE/DELETE tables):
   - Schedule `VACUUM (ANALYZE)` during off-peak.
   - Consider `VACUUM FULL` only with a maintenance window (locks).

```sql
VACUUM (ANALYZE) orders;
```

6. Apply application-side mitigations while the DB fix rolls out:
   - Add a bounded query timeout and graceful fallback.
   - Add pagination/limits (`LIMIT`, keyset pagination) to avoid unbounded result sets.
   - Reduce thundering herd via caching for hot reads.

7. Verification:
   - Query mean/p95 time drops back near baseline
   - CPU/IO drops and error rates normalize
   - `EXPLAIN` shows index usage (`Index Scan` / `Bitmap Index Scan`)

## Cost Impact (If applicable)

- Slow queries often drive DB scale-up (larger instance class, more IOPS) and increased replica counts.
- Fixing indexes/queries typically reduces CPU/IO and can enable **downsizing** or fewer replicas over time.

---


