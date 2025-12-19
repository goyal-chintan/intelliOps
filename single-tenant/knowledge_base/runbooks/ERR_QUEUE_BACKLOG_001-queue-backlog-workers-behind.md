# Title: Queue Backlog (Workers Falling Behind)

## Metadata

- Service: data-ingestor
- Category: Reliability
- Severity: P1

## Symptoms

- Error Codes: `ERR_QUEUE_BACKLOG_001`
- Metrics:
  - Queue depth increasing for **10m**
  - Oldest message age > **5m** (or > your SLO)
- Logs (common patterns):
  - `ERR_QUEUE_BACKLOG_001 backlog high`
  - `visibility timeout` / `processing exceeded`
  - `TaskRejected` / `executor saturated`

## Root Cause Analysis (RCA)

1. **Insufficient worker throughput** (under-provisioned, CPU throttled, GC pauses).
2. **Downstream dependency slow** (DB, object storage, vector DB) increases per-message processing time.
3. **Poison messages / hot partitions** cause retries and reduce effective throughput.

## Resolution Steps

1. Confirm queue backlog and identify which queue/topic is affected.

```bash
# SQS example:
aws sqs get-queue-attributes --queue-url <queue-url> --attribute-names ApproximateNumberOfMessages ApproximateAgeOfOldestMessage
```

2. Check worker health and errors.

```bash
kubectl -n prod get deploy data-ingestor -o wide
kubectl -n prod top pod -l app=data-ingestor
kubectl -n prod logs deploy/data-ingestor --since=30m | egrep -n "ERR_QUEUE_BACKLOG_001|timeout|retry|poison|dead-letter|Rejected"
```

3. Immediate mitigation:
   - Scale workers.

```bash
kubectl -n prod scale deploy/data-ingestor --replicas=+3
```

   - Pause non-critical producers if backlog is runaway.
   - Increase visibility timeout if processing time legitimately increased (temporary).

4. Handle poison messages:
   - Route to DLQ after N retries.
   - Add idempotency + validation to drop bad payloads.

5. Verification:
   - Queue depth decreases; oldest message age returns to baseline
   - Worker error rates normalize

## Cost Impact (If applicable)

- Scaling workers increases compute cost, but prolonged backlog can lead to retries and extra downstream load (more cost + worse SLO).

---


