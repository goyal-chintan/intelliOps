# Title: HTTP 429 Rate Limited (WAF / API Gateway / Upstream Throttling)

## Metadata

- Service: payment-gw
- Category: Reliability
- Severity: P1

## Symptoms

- Error Codes: `ERR_RATE_LIMIT_001`
- Metrics:
  - `http_requests_total{status="429"} / http_requests_total > 0.02` (**> 2% for 5m**)
  - Client retries increase; latency increases
- Logs (common patterns):
  - `ERR_RATE_LIMIT_001 rate limit exceeded`
  - `TooManyRequests`
  - `throttlingException` (AWS APIs)

## Root Cause Analysis (RCA)

1. **Traffic spike** exceeds configured limits (WAF rules, API gateway quotas, upstream service throttles).
2. **Retry storm** multiplies traffic and triggers throttling.
3. **Misconfigured limits** too low for production baseline or new tenant onboarding.

## Resolution Steps

1. Confirm source of 429s (edge/WAF vs service-to-service).

```bash
kubectl -n prod logs deploy/payment-gw --since=30m | egrep -n "ERR_RATE_LIMIT_001|429|TooManyRequests|throttl"
```

2. Check if this is tied to a specific tenant or endpoint.
   - Filter logs by `tenant_id` and `request_path` in your log pipeline.

3. Immediate mitigation:
   - Reduce retries and add exponential backoff + jitter.
   - Add server-side caching for hot endpoints if applicable.
   - Temporarily raise quotas (if safe) at the throttling layer.

4. If AWS API throttling is the cause:
   - Batch requests, cache STS tokens, and reduce high-frequency calls.

5. Verification:
   - 429 ratio returns to baseline
   - Client-side retries and latency normalize

## Cost Impact (If applicable)

- Reducing retries can reduce request-based costs (API Gateway, Lambda, S3 requests) and lower compute waste.

---


