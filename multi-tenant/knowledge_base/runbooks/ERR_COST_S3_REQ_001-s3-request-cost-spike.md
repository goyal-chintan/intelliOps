# Title: S3 Request Cost Spike (PUT/LIST/GET Explosion)

## Metadata

- Service: shared-infra
- Category: Cost
- Severity: P2

## Symptoms

- Error Codes: `ERR_COST_S3_REQ_001`
- Cost signals:
  - S3 request charges (Tier1/Tier2) increase by **> 30% week-over-week**
  - No proportional increase in stored bytes
- Operational signals:
  - Workloads performing frequent `LIST` operations or small-object PUTs
  - Spark/Hive listing entire prefixes (missing partition pruning)
- Logs / audit:
  - CloudTrail shows spikes in `ListObjectsV2`, `PutObject`, `CompleteMultipartUpload`

## Root Cause Analysis (RCA)

1. **Chatty clients** repeatedly listing large prefixes (e.g., polling for new files rather than event-driven ingestion).
2. **Small object anti-pattern**: writing many tiny files (checkpoint markers, per-record output) drives PUT and LIST costs.
3. **Bad partitioning / missing pruning** in analytics jobs causes wide scans and excessive requests.

## Resolution Steps

1. Identify the time range and request types driving cost (CUR/Cost Explorer).

2. Enable/inspect S3 request metrics (if not already enabled) and/or access logs.
   - CloudWatch per-bucket request metrics require enabling `RequestMetrics` for the bucket.

3. Use CloudTrail to find top callers (example query by event name; adjust time window).

```bash
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=ListObjectsV2 \
  --max-results 50
```

4. Fix common offenders:
   - Replace polling LIST with event-driven (S3 Events → SQS/Kinesis/Kafka).
   - Write fewer, larger objects (compaction) instead of many small objects.
   - Ensure partition pruning:
     - Use date/tenant partitions
     - Pushdown filters and avoid `s3 ls`/recursive scans in loops
   - Cache object manifests (store list of keys in a DB/table rather than listing S3 repeatedly).

5. Guardrails:
   - Add rate limits to background scanners.
   - Add alarms on request metrics:
     - `AllRequests` > baseline * 2 for 1h

## Cost Impact (If applicable)

- Reducing LIST/PUT frequency directly reduces S3 request charges and often improves job latency.
- Compaction can increase transient compute cost but typically pays back quickly in lower S3 + faster reads.

---


