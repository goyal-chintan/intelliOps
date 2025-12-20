# Title: Database Replica Lag High (Read Staleness / Failover Risk)

## Metadata

- Service: checkout-api
- Category: Reliability
- Severity: P1

## Symptoms

- Error Codes: `ERR_DB_REPLICA_LAG_001`
- Metrics:
  - Replica lag > **30s** for **10m** (Aurora/RDS `ReplicaLag` / Postgres replay delay)
  - Read-only endpoints return stale data
- Logs (common patterns):
  - `ERR_DB_REPLICA_LAG_001 replica lag detected`
  - Increased read timeouts on replicas

## Root Cause Analysis (RCA)

1. **Write burst** (large batch updates) generates WAL faster than replica can replay.
2. **Replica resource constraints** (CPU/IO) slow down replay.
3. **Long-running queries** on replica compete for IO/CPU and can delay replay.

## Resolution Steps

1. Confirm lag on Postgres replicas (examples; depends on setup).

```sql
-- On a replica:
SELECT now() - pg_last_xact_replay_timestamp() AS replay_lag;
```

2. Identify high write activity on primary.

```sql
-- On primary: check top write-heavy queries (if pg_stat_statements enabled)
SELECT calls, round(total_exec_time::numeric,2) AS total_ms, left(query, 160) AS query_sample
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;
```

3. Immediate mitigation:
   - Reduce write rate temporarily (pause batch jobs, throttle ingestion).
   - Scale up the replica instance class / IO (if managed DB and lag is severe).

4. Check for long-running queries on replicas and cancel if safe.

```sql
SELECT pid, now() - query_start AS age, left(query, 160) AS query_sample
FROM pg_stat_activity
WHERE state <> 'idle'
ORDER BY age DESC
LIMIT 20;
```

5. Permanent fixes:
   - Add read replicas sized for peak replay + query load.
   - Separate analytical reads from replication-critical replicas.
   - Optimize write-heavy queries and batch sizes.

6. Verification:
   - Lag returns to baseline (< threshold)
   - Read staleness reports stop

## Cost Impact (If applicable)

- Larger replicas increase cost; reducing write bursts and optimizing queries can avoid scale-up.

---


