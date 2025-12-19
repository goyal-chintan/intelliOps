# Title: Redis OOM (maxmemory / OOM command not allowed)

## Metadata

- Service: checkout-api
- Category: Reliability
- Severity: P1

## Symptoms

- Error Codes: `ERR_REDIS_OOM_001`
- Logs (common patterns):
  - `ERR_REDIS_OOM_001 OOM command not allowed when used memory > 'maxmemory'`
  - `MISCONF Redis is configured to save RDB snapshots, but is currently not able to persist on disk`
  - Increased cache errors and downstream DB load
- Metrics:
  - `redis_memory_used_bytes / redis_memory_max_bytes > 0.95`
  - Cache hit rate drops; API latency increases

## Root Cause Analysis (RCA)

1. **maxmemory reached** due to cache growth (new keys, higher TTL, tenant/data churn).
2. **Eviction policy misconfigured** (e.g., `noeviction`) so writes fail instead of evicting.
3. **Persistence/disk issues** (RDB/AOF failures) can cause Redis to reject writes (`MISCONF`).

## Resolution Steps

1. Confirm Redis OOM errors in app logs.

```bash
kubectl -n prod logs deploy/checkout-api --since=30m | egrep -n "ERR_REDIS_OOM_001|OOM command not allowed|MISCONF"
```

2. Inspect Redis memory and eviction settings.

```bash
kubectl -n prod exec -it deploy/redis -- sh -c "redis-cli INFO memory | egrep 'used_memory_human|maxmemory_human|mem_fragmentation_ratio' || true"
kubectl -n prod exec -it deploy/redis -- sh -c \"redis-cli CONFIG GET maxmemory maxmemory-policy appendonly save\" 
```

3. Immediate mitigation:
   - If policy is `noeviction`, switch to an eviction policy (example: `allkeys-lru`) and reload config.

```bash
kubectl -n prod exec -it deploy/redis -- sh -c "redis-cli CONFIG SET maxmemory-policy allkeys-lru"
```

   - Increase memory limit/capacity (temporary) and/or scale Redis (if clustered).
   - Reduce cache footprint: lower TTLs, cap large values, evict hot prefixes (carefully).

4. If `MISCONF` / persistence failure:
   - Check disk usage and permissions on Redis volume.

```bash
kubectl -n prod describe pod -l app=redis | egrep -n "Warning|Failed|Mount|volume"
kubectl -n prod exec -it deploy/redis -- sh -c "df -h; ls -la /data || true"
```

5. Verification:
   - OOM/MISCONF errors stop
   - Cache hit rate recovers; API latency reduces

## Cost Impact (If applicable)

- Scaling Redis memory increases infra cost, but can prevent costly DB scale-up by keeping cache effective.
- Over-retaining keys increases memory bills; right-sizing TTLs often saves cost.

---


