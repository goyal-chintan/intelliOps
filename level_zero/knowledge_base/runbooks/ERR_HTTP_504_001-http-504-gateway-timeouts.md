# Title: HTTP 504 Gateway Timeouts (Upstream Slow)

## Metadata

- Service: checkout-api
- Category: Performance
- Severity: P1

## Symptoms

- Error Codes: `ERR_HTTP_504_001`
- Metrics:
  - `http_requests_total{status="504"} / http_requests_total > 0.01` (**> 1% for 5m**)
  - Upstream latency P95 > **2s** and matches proxy timeout thresholds
- Logs (common patterns):
  - `ERR_HTTP_504_001 upstream timeout`
  - NGINX/Envoy: `upstream timed out` / `context deadline exceeded`
  - Client: `ReadTimeout` / `deadline exceeded`

## Root Cause Analysis (RCA)

1. **Downstream latency spike** (DB slow queries, vector search latency, external API slowness).
2. **Resource saturation** in upstream pods (CPU throttling, GC pauses, thread pool saturation).
3. **Timeout mismatch**: proxy/client timeout lower than upstream’s worst-case processing time.

## Resolution Steps

1. Confirm 504s and identify which upstream call is slow (trace/span IDs if available).

```bash
kubectl -n prod logs deploy/checkout-api --since=30m | egrep -n "ERR_HTTP_504_001|504|upstream timed out|deadline exceeded"
```

2. Check upstream dependency health and latency.

```bash
kubectl -n prod get deploy ml-serving data-ingestor payment-gw -o wide
kubectl -n prod top pod | head -n 25
```

3. If CPU/GC or thread pools are saturated:
   - Scale out replicas or increase resources.

```bash
kubectl -n prod scale deploy/checkout-api --replicas=+2
kubectl -n prod rollout status deploy/checkout-api --timeout=5m
```

4. If DB is the suspected bottleneck:
   - Look for slow queries and lock waits (see DB runbooks like `ERR_DB_QRY_001`, `ERR_DB_LOCK_001`).

5. Temporary timeout mitigation (only if safe and bounded):
   - Increase proxy timeout slightly to reduce false 504s while fixing root cause.
   - Do not “paper over” infinite latency; cap timeouts and add fallbacks.

6. Verification:
   - 504 ratio returns < **0.2%**
   - P95 latency returns to baseline

## Cost Impact (If applicable)

- Increasing timeouts can increase concurrency and memory usage per pod; fixing the root latency driver is typically cheaper than over-scaling.

---


