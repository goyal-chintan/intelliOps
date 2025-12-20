# Title: Database Deadlocks Detected (Postgres 40P01)

## Metadata

- Service: payment-gw
- Category: Reliability
- Severity: P1

## Symptoms

- Error Codes: `ERR_DB_DLK_001`
- Application logs:
  - `ERR_DB_DLK_001 deadlock detected`
  - `SQLSTATE 40P01`
  - `org.postgresql.util.PSQLException: ERROR: deadlock detected`
- User impact: spike in `5xx` responses and elevated latency due to transaction retries
- Database logs (if enabled):
  - `deadlock detected` with detail about processes and relation locks

## Root Cause Analysis (RCA)

1. **Inconsistent lock ordering**: two code paths update the same set of tables/rows in different order.
2. **Long transactions** hold locks longer (slow queries, network calls inside transactions).
3. **Hot partitions / hot rows**: high contention on a small key space (counters, per-tenant aggregates).

## Resolution Steps

1. Confirm deadlocks and capture the exact statements involved.

```bash
kubectl -n prod logs deploy/payment-gw --since=30m | egrep -n "ERR_DB_DLK_001|40P01|deadlock detected"
```

2. On Postgres, enable deadlock visibility (if not already):
   - Requires DB parameter change; may require restart depending on environment.

```sql
ALTER SYSTEM SET log_lock_waits = 'on';
ALTER SYSTEM SET deadlock_timeout = '1s';
SELECT pg_reload_conf();
```

3. Identify blocked/blocking sessions around the incident window.

```sql
-- Find sessions waiting on locks
SELECT pid, usename, application_name, state, wait_event_type, wait_event,
       now() - query_start AS query_age,
       left(query, 160) AS query_sample
FROM pg_stat_activity
WHERE wait_event_type = 'Lock'
ORDER BY query_age DESC
LIMIT 30;
```

4. Immediate mitigation:
   - If a small set of transactions are stuck, terminate them to break the deadlock chain (use cautiously).

```sql
SELECT pg_terminate_backend(<pid>);
```

   - Reduce concurrent writers temporarily (throttle queue workers / scale down writers).

```bash
kubectl -n prod scale deploy/payment-gw --replicas=1
```

5. Permanent fixes:
   - Enforce consistent lock order across code paths (e.g., always update `accounts` then `payments`).
   - Reduce lock scope:
     - Keep transactions short (no remote calls inside)
     - Use smaller batches
     - Add missing indexes so updates lock fewer rows for less time
   - Use safe locking patterns:
     - `SELECT ... FOR UPDATE SKIP LOCKED` for workers
     - Retries with jitter on `40P01` (idempotent operations only)

6. Verification:
   - Deadlock logs stop
   - `5xx` rate returns to baseline
   - Transaction retry rate normalizes

## Cost Impact (If applicable)

- Deadlocks reduce throughput and can trigger scaling (pods/DB), increasing compute spend.
- Fixes usually reduce wasted work from retries and lower DB CPU.

---


