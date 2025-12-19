# Title: Database Connection Leak / Idle In Transaction

## Metadata

- Service: checkout-api
- Category: Reliability
- Severity: P1

## Symptoms

- Error Codes: `ERR_DB_CON_002`
- HTTP errors: `5xx` rate > **2% for 10m** or request latency P95 > **2s**
- Application logs (common patterns):
  - `ERR_DB_CON_002 Connection leak detected`
  - `HikariPool-.* - Apparent connection leak detected`
  - `Cannot commit when autoCommit is enabled` / `Connection is closed` (secondary effects)
- Database symptoms (Postgres):
  - Many sessions in `idle in transaction` for > **60s**
  - Connection count steadily rises and does not return to baseline after traffic drops

```sql
-- Find sessions holding open transactions
SELECT pid, usename, application_name, client_addr,
       now() - xact_start AS xact_age,
       now() - state_change AS state_age,
       state, wait_event_type, wait_event,
       left(query, 160) AS query_sample
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
ORDER BY xact_age DESC
LIMIT 30;
```

## Root Cause Analysis (RCA)

1. **Connection lifecycle bug**: code path fails to close/return connections to the pool (missing `finally`, early returns, exception path).
2. **Open transactions**: application begins a transaction and performs slow work (remote calls, retries) before commit/rollback, keeping the connection checked out.
3. **Missing safeguards**: no `idle_in_transaction_session_timeout` / no leak detection / missing query timeouts → leaks persist until restart.

## Resolution Steps

1. Confirm leak signal in application logs and pool metrics.

```bash
kubectl -n prod logs deploy/checkout-api --since=30m | egrep -n "ERR_DB_CON_002|leak detected|HikariPool"
kubectl -n prod port-forward deploy/checkout-api 9000:9000
# If you expose /metrics, check pending/active connections
```

2. Check whether the DB is accumulating `idle in transaction` sessions.

```sql
SELECT application_name, state, COUNT(*) AS conns,
       max(now() - xact_start) AS max_xact_age
FROM pg_stat_activity
GROUP BY 1,2
ORDER BY conns DESC;
```

3. Immediate mitigation (choose safest):
   - Restart the leaking workload to free connections (fastest mitigation).

```bash
kubectl -n prod rollout restart deploy/checkout-api
kubectl -n prod rollout status deploy/checkout-api --timeout=5m
```

   - Terminate only the clearly stuck DB sessions (use cautiously).

```sql
-- Replace <pid> after validating it belongs to the leaking app
SELECT pg_terminate_backend(<pid>);
```

4. Add DB guardrails to prevent recurrence (Postgres).

```sql
-- Kill sessions that sit in a transaction too long (example: 2 minutes)
ALTER DATABASE appdb SET idle_in_transaction_session_timeout = '2min';

-- Prevent runaway queries (tune per workload)
ALTER DATABASE appdb SET statement_timeout = '30s';
```

5. Add application-side guardrails (HikariCP examples; adapt to your pool):
   - Enable leak detection (non-prod first if overhead is a concern).
   - Ensure `connectionTimeout` is bounded (e.g., 2–5s).
   - Set `maxLifetime` < DB-side connection idle timeout.

6. Identify the leaking code path:
   - Correlate leak logs with trace IDs.
   - Audit DB usage blocks for missing close/rollback.
   - If using an ORM, ensure transaction boundaries are correct and not nested incorrectly.

7. Verification:
   - Pool `active` connections return to baseline after traffic subsides
   - `idle in transaction` sessions drop to ~0
   - `5xx` and P95 latency normalize

## Cost Impact (If applicable)

- Leaks often trigger “scale up the DB” as a knee‑jerk reaction; fixing leaks avoids unnecessary DB instance upgrades.
- Frequent restarts increase error rates and can amplify retries (extra compute + DB load).

---


