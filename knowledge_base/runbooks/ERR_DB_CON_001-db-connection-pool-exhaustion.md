# Title: Database Connection Pool Exhaustion (PgBouncer / HikariCP)

## Metadata

- Service: checkout-api
- Category: Reliability
- Severity: P1

## Symptoms

- Error Codes: `ERR_DB_CON_001`
- HTTP errors: `5xx` rate > **2% for 5m** or checkout latency P95 > **2s**
- Application logs (common patterns):
  - `ERR_DB_CON_001 Timeout waiting for connection from pool`
  - `HikariPool-.* - Connection is not available, request timed out after`
  - `org.postgresql.util.PSQLException: FATAL: remaining connection slots are reserved` (Postgres maxed)
  - PgBouncer: `no more connections allowed (max_client_conn)`
- Metrics (any of the following for 5m):
  - `hikaricp_connections_pending > 0`
  - `hikaricp_connections_active / hikaricp_connections_max > 0.90`
  - RDS/Aurora: `DatabaseConnections > 0.90 * max_connections`

## Root Cause Analysis (RCA)

1. **Pool saturation**: `maxPoolSize` too small for current concurrency (traffic spike, new feature, retry storm, slow downstream).
2. **Long-held connections**: slow queries, lock waits, or long transactions keep connections checked out.
3. **Connection leak / missing timeouts**: application paths that don’t close connections (or leave transactions open) gradually exhaust the pool.

## Resolution Steps

1. Confirm scope and recent changes (deploys, migrations, traffic).

```bash
kubectl -n prod get deploy checkout-service -o wide
kubectl -n prod rollout history deploy/checkout-service
kubectl -n prod get pods -l app=checkout-service -o wide
```

2. Verify pool exhaustion in logs.

```bash
kubectl -n prod logs deploy/checkout-service --since=15m | egrep -n "ERR_DB_CON_001|HikariPool|Timeout waiting for connection|remaining connection slots|pgbouncer"
```

3. Check current pool settings exposed via env/config (names vary by app).

```bash
kubectl -n prod describe deploy checkout-service | egrep -n "HIKARI|DB_POOL|MAX_POOL|CONNECTION_TIMEOUT|IDLE_TIMEOUT|MAX_LIFETIME"
```

4. Validate DB-side connection pressure and identify offenders (Postgres).

```sql
-- Connection breakdown by app/state
SELECT usename, application_name, state, COUNT(*) AS conns
FROM pg_stat_activity
GROUP BY 1,2,3
ORDER BY conns DESC;

-- Top long-running queries holding connections
SELECT pid, usename, application_name, state,
       now() - query_start AS query_age,
       left(query, 160) AS query_sample
FROM pg_stat_activity
WHERE state <> 'idle'
ORDER BY query_age DESC
LIMIT 20;
```

5. Immediate mitigation (pick the safest first):
   - Scale the service to absorb transient waits (only helps if DB has headroom).

```bash
kubectl -n prod scale deploy/checkout-service --replicas=+2
```

   - Restart the deployment if leak/stuck connections are suspected (may cause a brief error spike).

```bash
kubectl -n prod rollout restart deploy/checkout-service
kubectl -n prod rollout status deploy/checkout-service --timeout=5m
```

   - If the DB has capacity, temporarily increase pool size (requires config change + rollout). Ensure you do **not** exceed DB `max_connections` across all services.

```bash
# Example: adjust a ConfigMap/Secret value, then restart
kubectl -n prod get cm checkout-service-config -o yaml
# Edit pool size keys as appropriate, then:
kubectl -n prod rollout restart deploy/checkout-service
```

   - If a small number of sessions are clearly stuck, terminate them (use cautiously).

```sql
-- Replace <pid> after validating it's safe to terminate
SELECT pg_terminate_backend(<pid>);
```

6. Permanent fixes:
   - Add/verify timeouts:
     - App pool: `connectionTimeout`, `idleTimeout`, `maxLifetime`, `leakDetectionThreshold`
     - DB: `statement_timeout`, `idle_in_transaction_session_timeout`
   - Reduce connection hold time: optimize slow queries, remove lock contention, avoid holding connections during external calls.
   - Consider a pooler (PgBouncer) for bursty workloads; size `max_client_conn`, `pool_size`, and `reserve_pool_size`.

7. Verification:
   - `hikaricp_connections_pending` returns to **0**
   - `DatabaseConnections` stabilizes < **80%** of max
   - Checkout `5xx` rate < **0.5%** and P95 latency returns to baseline

## Cost Impact (If applicable)

- Short-term scaling of pods increases compute cost.
- Increasing DB instance class or adding PgBouncer increases monthly spend; treat as a last resort after fixing leaks/slow queries.

---


