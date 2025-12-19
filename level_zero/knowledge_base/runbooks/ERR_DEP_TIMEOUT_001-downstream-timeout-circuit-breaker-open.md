# Title: Downstream Timeout / Circuit Breaker Open

## Metadata

- Service: payment-gw
- Category: Reliability
- Severity: P1

## Symptoms

- Error Codes: `ERR_DEP_TIMEOUT_001`
- Metrics:
  - Dependency call latency P95 > **1s** for **10m**
  - Spike in `5xx` or `429` from dependency
- Logs (common patterns):
  - `ERR_DEP_TIMEOUT_001 dependency timeout`
  - `circuit breaker open` / `short-circuit`
  - `java.net.SocketTimeoutException: Read timed out`
  - `context deadline exceeded`

## Root Cause Analysis (RCA)

1. **Dependency is slow/unhealthy** (partial outage, throttling, elevated latency).
2. **Circuit breaker thresholds too strict**: opens during normal latency variation, causing false failures.
3. **Retry amplification**: concurrent retries overwhelm the dependency and keep the breaker open.

## Resolution Steps

1. Confirm breaker/timeout errors and identify the dependency name.

```bash
kubectl -n prod logs deploy/payment-gw --since=30m | egrep -n "ERR_DEP_TIMEOUT_001|circuit breaker|short-circuit|SocketTimeoutException|deadline exceeded"
```

2. Check dependency health (service endpoints, error rates).

```bash
kubectl -n prod get svc,endpoints -o wide
kubectl -n prod get deploy -o wide
```

3. Reduce blast radius:
   - Temporarily reduce retries and add jitter.
   - Enforce client-side timeouts and fallbacks (e.g., degrade feature).

4. If breaker configuration recently changed, roll back config.

```bash
kubectl -n prod rollout history deploy/payment-gw
kubectl -n prod rollout undo deploy/payment-gw
kubectl -n prod rollout status deploy/payment-gw --timeout=5m
```

5. If dependency is overloaded:
   - Scale dependency (if internal), or throttle callers.
   - Consider request hedging only if idempotent and carefully controlled.

6. Verification:
   - Breaker “open” logs stop
   - Dependency success rate returns to baseline

## Cost Impact (If applicable)

- Retry storms increase compute/network costs; tuning retries and breakers reduces wasted work.

---


