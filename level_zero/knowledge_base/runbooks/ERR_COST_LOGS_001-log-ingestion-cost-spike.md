# Title: Log Ingestion Cost Spike (CloudWatch / OpenSearch / S3)

## Metadata

- Service: shared-infra
- Category: Cost
- Severity: P2

## Symptoms

- Error Codes: `ERR_COST_LOGS_001`
- Cost signals:
  - Logging spend increases by **> 30% week-over-week**
  - Ingestion volume (GB/day) spikes without proportional traffic increase
- Operational signals:
  - Debug logging enabled in production
  - High-cardinality labels/fields (tenant_id, request_id, stack traces) exploding index size

## Root Cause Analysis (RCA)

1. **Log level regression** (DEBUG/TRACE enabled) produces huge volume.
2. **Chatty endpoints** emit logs per request (or per retry) with large payloads.
3. **High-cardinality indexing** (OpenSearch) increases storage and shard overhead.

## Resolution Steps

1. Identify top talkers by service and field (use your log backend).
   - If using OpenSearch/Kibana, group by `service` and sum `bytes`.

2. Quick check Kubernetes logs volume (rough signal).

```bash
kubectl -n prod logs deploy/checkout-api --since=10m | wc -c
kubectl -n prod logs deploy/payment-gw --since=10m | wc -c
```

3. Roll back logging level changes (fastest cost stopgap).

```bash
kubectl -n prod describe deploy checkout-api | egrep -n "LOG_LEVEL|DEBUG|TRACE"
kubectl -n prod rollout undo deploy/checkout-api
kubectl -n prod rollout status deploy/checkout-api --timeout=5m
```

4. Reduce volume safely:
   - Sample noisy logs (e.g., 1% for INFO) while preserving ERROR
   - Remove large payload fields (request/response bodies)
   - Deduplicate repeating stack traces

5. Reduce indexing/storage costs:
   - Drop high-cardinality fields from indexing (store but don’t index)
   - Use shorter retention + tiering (hot/warm/cold)

6. Verification:
   - Ingestion GB/day returns to baseline within 1–2 hours
   - Cost trend flattens in the next billing cycle

## Cost Impact (If applicable)

- Lower log volume immediately reduces ingestion costs and downstream storage costs.
- Tuning indexing and retention can significantly reduce OpenSearch spend without losing critical incident signals.

---


