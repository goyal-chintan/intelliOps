# Title: Thread Pool Saturation (Queueing / Rejections)

## Metadata

- Service: payment-gw
- Category: Performance
- Severity: P1

## Symptoms

- Error Codes: `ERR_THREADPOOL_001`
- Metrics:
  - Request queue depth grows; latency P95 > **2x baseline** for **10m**
  - Increased 503/504 if upstream timeouts occur
- Logs (common patterns):
  - `ERR_THREADPOOL_001 executor saturated`
  - `RejectedExecutionException`
  - `Task rejected from java.util.concurrent.ThreadPoolExecutor`
  - `connection pool exhausted` (secondary if threads are blocked)

## Root Cause Analysis (RCA)

1. **Blocking operations** (DB calls, external HTTP) hold threads; pool saturates.
2. **Pool configured too small** for traffic or new code path increases concurrency needs.
3. **Downstream slowness** turns normal traffic into queued work; rejections appear.

## Resolution Steps

1. Confirm rejections and identify the thread pool name (server, async executor, HTTP client).

```bash
kubectl -n prod logs deploy/payment-gw --since=30m | egrep -n "ERR_THREADPOOL_001|RejectedExecutionException|ThreadPoolExecutor|Task rejected"
```

2. Check pod CPU and thread usage symptoms.

```bash
kubectl -n prod top pod -l app=payment-gw
kubectl -n prod get pods -l app=payment-gw -o wide
```

3. Immediate mitigation:
   - Scale out replicas to distribute load.

```bash
kubectl -n prod scale deploy/payment-gw --replicas=+2
```

   - Reduce request concurrency (rate limit, shed load) if downstream is slow.

4. Identify the blocker:
   - Look for slow downstream calls (DB, HTTP) and fix those first.
   - Ensure timeouts are set on all downstream calls so threads don’t block indefinitely.

5. Tune pool sizes (per workload):
   - Increase max threads/queue if appropriate.
   - Prefer async/non-blocking IO when possible to reduce thread consumption.

6. Verification:
   - Rejection logs stop
   - Latency and error rates normalize

## Cost Impact (If applicable)

- Scaling pods increases compute cost; removing blocking calls/timeouts often reduces the number of replicas needed.

---


