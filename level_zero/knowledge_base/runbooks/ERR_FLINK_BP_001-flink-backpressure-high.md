# Title: Flink Backpressure High (Operators Stalled)

## Metadata

- Service: data-ingestor
- Category: Performance
- Severity: P1

## Symptoms

- Error Codes: `ERR_FLINK_BP_001`
- Flink symptoms:
  - Backpressure view shows operators in `HIGH` for sustained periods
  - End-to-end latency increases; Kafka lag increases
- Logs (common patterns):
  - `ERR_FLINK_BP_001 backpressure high`
  - Sink exceptions or slow flush warnings
- Metrics:
  - `busyTimeMsPerSecond` high; `backPressuredTimeMsPerSecond` increases
  - `numRecordsOutPerSecond` drops while `numRecordsInPerSecond` stays high

## Root Cause Analysis (RCA)

1. **Slow sink** (DB/object storage) throttles output and propagates backpressure upstream.
2. **Insufficient TaskManager resources** (CPU/memory) causing processing to stall under load.
3. **Skewed partitions**: one key/partition dominates and slows a subset of operators.

## Resolution Steps

1. Confirm backpressure and identify which operator/subtask is impacted.
   - Use Flink UI Backpressure tab.

2. Check streaming job pod health and resource saturation.

```bash
kubectl -n prod get pods -l app=flink -o wide
kubectl -n prod top pod -l app=flink
kubectl -n prod logs deploy/flink-taskmanager --since=30m | egrep -n "ERR_FLINK_BP_001|backpressure|sink|timeout|throttle"
```

3. Identify sink bottleneck:
   - If DB sink: check DB CPU/locks/slow queries.
   - If S3 sink: check request errors/throttling and NAT/VPC endpoints.

4. Immediate mitigation:
   - Scale TaskManagers (more slots/parallelism) if CPU bound.
   - Increase sink batching (reduce per-record overhead) but keep latency within SLO.
   - Throttle producers if the backlog is runaway.

5. Fix root cause:
   - Optimize sink writes (bulk inserts, retries with jitter, idempotency).
   - Repartition/rehash keys to reduce skew.
   - Right-size resources and set backpressure-friendly configs.

6. Verification:
   - Backpressure drops to `LOW`
   - Throughput recovers; Kafka lag decreases

## Cost Impact (If applicable)

- Scaling TaskManagers increases compute cost; optimizing sinks and reducing skew typically reduces required parallelism and spend.

---


