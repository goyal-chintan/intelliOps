# Title: Redis High Latency (Slowlog / Network / CPU Saturation)

## Metadata

- Service: checkout-api
- Category: Performance
- Severity: P1

## Symptoms

- Error Codes: `ERR_REDIS_LAT_001`
- Metrics:
  - Redis latency P95 > **5ms** (or > baseline * 2 for 10m)
  - CPU utilization > **80%** or network saturation
- Logs (common patterns):
  - `ERR_REDIS_LAT_001 redis command latency high`
  - Increased timeouts: `i/o timeout` / `read timeout`
- Redis indicators:
  - `SLOWLOG` shows long-running commands (`KEYS`, `LRANGE` huge ranges, `HGETALL` on massive hashes)

## Root Cause Analysis (RCA)

1. **Expensive commands** or large values causing long execution times (slowlog).
2. **CPU saturation** due to high QPS or Lua scripts.
3. **Network latency** between app and Redis (cross-AZ, packet loss) or connection pool issues.

## Resolution Steps

1. Confirm latency symptoms from application logs and timeouts.

```bash
kubectl -n prod logs deploy/checkout-api --since=30m | egrep -n "ERR_REDIS_LAT_001|redis.*timeout|i/o timeout"
```

2. Check Redis slowlog and basic health.

```bash
kubectl -n prod exec -it deploy/redis -- sh -c "redis-cli PING; redis-cli INFO stats | egrep 'instantaneous_ops_per_sec|rejected_connections|keyspace_hits|keyspace_misses'"
kubectl -n prod exec -it deploy/redis -- sh -c "redis-cli SLOWLOG GET 20"
```

3. Immediate mitigation:
   - Remove/replace expensive commands:
     - Avoid `KEYS`; use `SCAN`
     - Avoid huge range reads; paginate
   - If CPU is saturated, scale Redis up/out and/or reduce QPS.

4. Validate network placement:
   - Ensure Redis and callers are in the same AZ or use zonal endpoints where applicable.

5. Verification:
   - Slowlog entries reduce; P95 latency returns to baseline
   - Timeout/error rates drop

## Cost Impact (If applicable)

- Scaling Redis increases cost; fixing expensive command patterns often reduces required cache size and improves performance at lower spend.

---


