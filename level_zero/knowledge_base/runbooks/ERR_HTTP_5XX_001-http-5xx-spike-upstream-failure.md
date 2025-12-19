# Title: HTTP 5xx Spike (Upstream/Dependency Failure)

## Metadata

- Service: checkout-api
- Category: Reliability
- Severity: P1

## Symptoms

- Error Codes: `ERR_HTTP_5XX_001`
- Metrics:
  - `http_requests_total{status=~"5.."} / http_requests_total > 0.05` (**> 5% for 5m**)
  - `latency_p95_ms > 2000` (**for 10m**)
- Logs (common patterns):
  - `ERR_HTTP_5XX_001 upstream returned 5xx`
  - `upstream connect error or disconnect/reset before headers`
  - `connect: connection refused` / `no healthy upstream`
  - `503 Service Unavailable` from dependency

## Root Cause Analysis (RCA)

1. **Downstream dependency outage** (e.g., payment-gw, inventory, DB) causing upstream calls to fail.
2. **Retry storm / thundering herd** amplifies partial failures into systemic 5xx.
3. **Bad deploy/config** (wrong endpoint, DNS, auth, circuit breaker mis-tuned) increases dependency errors.

## Resolution Steps

1. Identify which endpoint and dependency is driving 5xx.

```bash
kubectl -n prod logs deploy/checkout-api --since=15m | egrep -n "ERR_HTTP_5XX_001|upstream|connection refused|no healthy upstream|5\\d\\d"
```

2. Check dependency health (example: `payment-gw`) and recent rollouts.

```bash
kubectl -n prod get deploy payment-gw checkout-api -o wide
kubectl -n prod rollout history deploy/payment-gw
kubectl -n prod rollout history deploy/checkout-api
```

3. If a dependency is failing:
   - Roll back the last deploy for that dependency if correlated.

```bash
kubectl -n prod rollout undo deploy/payment-gw
kubectl -n prod rollout status deploy/payment-gw --timeout=5m
```

4. Apply traffic protection:
   - Reduce retries / add jitter
   - Enable/raise circuit breaker thresholds (fail fast)
   - Temporarily shed load on the failing dependency path

5. Validate service discovery:

```bash
kubectl -n prod get svc,endpoints payment-gw
kubectl -n prod exec deploy/checkout-api -- sh -c "nslookup payment-gw.prod.svc.cluster.local || true"
```

6. Verification:
   - 5xx ratio < **1%** within 10–15 minutes
   - Dependency error logs stop; latency P95 returns to baseline

## Cost Impact (If applicable)

- Retry storms increase compute and network costs; reducing retries often lowers spend and improves SLOs.
- Rolling back may reduce wasted resources from failing workloads and autoscaling.

---


