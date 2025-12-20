# Title: Database Storage Full / FreeStorageSpace Low

## Metadata

- Service: checkout-api
- Category: Reliability
- Severity: P0

## Symptoms

- Error Codes: `ERR_DB_STORAGE_001`
- Metrics:
  - `FreeStorageSpace < 10%` (or < **20GiB**) sustained
  - Writes fail; error rate increases across DB-backed services
- Logs (common patterns):
  - `ERR_DB_STORAGE_001 could not extend file`
  - `No space left on device`
  - `PANIC: could not write to file`

## Root Cause Analysis (RCA)

1. **Data growth** (events/logs/orders) exceeds allocated storage; retention not enforced.
2. **Table/index bloat** from heavy UPDATE/DELETE without vacuuming.
3. **Large objects** (blobs) stored in DB instead of object storage.

## Resolution Steps

1. Confirm low storage and correlate to incident window (RDS/Aurora metrics).

2. Identify largest tables/indexes (Postgres).

```sql
SELECT nspname AS schema,
       relname AS table,
       pg_size_pretty(pg_total_relation_size(c.oid)) AS total_size
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE relkind = 'r'
ORDER BY pg_total_relation_size(c.oid) DESC
LIMIT 20;
```

3. Immediate mitigation:
   - Increase storage (managed DB scale storage / autoscaling) to stop the outage.
   - Delete/expire old data if you have safe retention policies.

4. Reduce bloat:
   - Run `VACUUM (ANALYZE)` during off-peak.

```sql
VACUUM (ANALYZE) orders;
```

5. Prevent recurrence:
   - Add retention jobs (partitioning by date; drop old partitions).
   - Move large objects to S3/object storage.
   - Monitor growth and alert on storage < 15–20%.

6. Verification:
   - Free storage stabilizes and grows after mitigation
   - Error rates return to baseline

## Cost Impact (If applicable)

- Increasing DB storage directly increases monthly spend.
- Retention and moving blobs to object storage typically reduce DB costs substantially.

---


