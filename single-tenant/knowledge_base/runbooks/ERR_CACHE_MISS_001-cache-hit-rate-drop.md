# Title: Cache Hit Rate Drop (Cache Miss Storm)

## Metadata

- Service: checkout-api
- Category: Performance
- Severity: P1

## Symptoms

- Error Codes: `ERR_CACHE_MISS_001`
- Metrics:
  - Cache hit ratio < **0.70** for **10m** (or drops > 20 points vs baseline)
  - DB QPS increases sharply; API latency increases
- Logs (common patterns):
  - `ERR_CACHE_MISS_001 cache miss storm`
  - Increased DB calls per request

## Root Cause Analysis (RCA)

1. **Cache invalidation/flush** (deploy clears cache, key version bump, eviction) causes cold-cache period.
2. **TTL too low** or key churn too high → keys expire before reuse.
3. **Hot key eviction** due to memory pressure; cache no longer holds working set.

## Resolution Steps

1. Confirm cache hit ratio drop and identify impacted endpoints.

```bash
kubectl -n prod logs deploy/checkout-api --since=30m | egrep -n "ERR_CACHE_MISS_001|cache miss|evict|cold cache"
```

2. Check cache health (Redis example).

```bash
kubectl -n prod exec -it deploy/redis -- sh -c "redis-cli INFO stats | egrep 'keyspace_hits|keyspace_misses' || true"
kubectl -n prod exec -it deploy/redis -- sh -c "redis-cli INFO memory | egrep 'used_memory_human|maxmemory_human' || true"
```

3. Immediate mitigation:
   - Warm the cache for hot keys (preload top SKUs/users/orders).
   - Temporarily increase TTLs for hot keys.
   - Scale cache capacity if evictions are high.

4. Reduce DB impact:
   - Add request coalescing (singleflight) to prevent stampedes.
   - Add per-key locks to avoid N requests triggering N DB reads.

5. Verification:
   - Cache hit ratio recovers
   - DB QPS and API latency return to baseline

## Cost Impact (If applicable)

- Cache miss storms can force DB scaling (expensive). Keeping cache effective reduces DB spend and improves SLOs.

---


