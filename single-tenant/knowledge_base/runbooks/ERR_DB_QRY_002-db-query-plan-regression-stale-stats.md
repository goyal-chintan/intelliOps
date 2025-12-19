# Title: Database Query Plan Regression (Stale Stats / Parameter Sensitivity)

## Metadata

- Service: checkout-api
- Category: Performance
- Severity: P1

## Symptoms

- Error Codes: `ERR_DB_QRY_002`
- After a deploy/migration, latency P95 increases by **> 2x baseline** and does not recover
- Postgres indicators:
  - The same query becomes slower without code changes in that query path
  - `EXPLAIN` shows a different plan than yesterday (e.g., `Seq Scan` vs `Index Scan`)
  - `pg_stat_statements` shows increased `mean_exec_time` for top queries
- Logs:
  - `ERR_DB_QRY_002 query plan regression suspected`
  - spikes in `statement timeout` or `canceling statement due to statement timeout`

## Root Cause Analysis (RCA)

1. **Stale statistics** after large data changes or migrations cause the planner to misestimate cardinality.
2. **Parameter sensitivity** (a.k.a. “parameter sniffing” style issues): generic plans chosen for prepared statements may be suboptimal for certain parameter distributions.
3. **Index or schema change**: index dropped/created, column type changed, or default collation changes affecting plan selection.

## Resolution Steps

1. Confirm plan regression with `EXPLAIN (ANALYZE, BUFFERS)` on representative parameters.

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT /* slow query */ ;
```

2. Refresh statistics for the affected tables (fast, low risk).

```sql
ANALYZE;
-- Or target specific high-churn tables
ANALYZE orders;
ANALYZE order_items;
```

3. If cardinality estimates are still wrong:
   - Increase statistics target for skewed columns and re-analyze.

```sql
ALTER TABLE orders ALTER COLUMN status SET STATISTICS 1000;
ANALYZE orders;
```

4. Validate index health and availability.

```sql
-- Check for invalid/unused indexes
SELECT relname AS table_name, indexrelname AS index_name, idx_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC
LIMIT 25;
```

5. If the regression started right after a deploy:
   - Roll back the deploy if it introduced query changes or increased concurrency.

```bash
kubectl -n prod rollout undo deploy/checkout-api
kubectl -n prod rollout status deploy/checkout-api --timeout=5m
```

6. If prepared statement plan caching is the suspected cause (Postgres):
   - Consider using custom plans for problematic queries, or avoid server-side prepared statements for those endpoints.
   - In some drivers you can toggle “prepare threshold” or statement caching.

7. Verification:
   - Query `mean_exec_time` returns to baseline
   - `EXPLAIN` shows index usage and reduced buffer reads
   - Application P95 latency normalizes

## Cost Impact (If applicable)

- Plan regressions can increase CPU and IO, forcing temporary scale-up.
- Correct stats/index usage typically reduces replica pressure and can reduce RDS/Aurora spend.

---


