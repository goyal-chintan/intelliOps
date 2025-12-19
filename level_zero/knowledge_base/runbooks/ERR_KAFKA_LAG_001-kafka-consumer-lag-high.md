# Title: Kafka Consumer Lag High (Backlog Growing)

## Metadata

- Service: data-ingestor
- Category: Reliability
- Severity: P1

## Symptoms

- Error Codes: `ERR_KAFKA_LAG_001`
- Metrics:
  - Consumer lag > **100k messages** or lag increasing for **10m**
  - Processing throughput drops below production rate
- Logs (common patterns):
  - `ERR_KAFKA_LAG_001 consumer lag high`
  - `CommitFailedException` / `rebalance in progress`
  - `TimeoutException` contacting broker

## Root Cause Analysis (RCA)

1. **Consumers under-provisioned** (not enough parallelism, CPU throttled, GC pauses).
2. **Downstream bottleneck** (DB slow, sink throttled) slows processing and increases lag.
3. **Rebalances** (frequent deploys, session timeouts) reduce effective throughput.

## Resolution Steps

1. Confirm lag and identify affected consumer group/topic/partition.

```bash
# If you have kafka tooling available in-cluster or locally:
kafka-consumer-groups --bootstrap-server <broker:9092> --describe --group <group>
```

2. Check consumer pod health and resource saturation.

```bash
kubectl -n prod get pods -l app=data-ingestor -o wide
kubectl -n prod top pod -l app=data-ingestor
kubectl -n prod logs deploy/data-ingestor --since=30m | egrep -n "ERR_KAFKA_LAG_001|rebalance|CommitFailedException|TimeoutException"
```

3. Immediate mitigation:
   - Scale consumer replicas / increase partitions (if safe) to increase parallelism.

```bash
kubectl -n prod scale deploy/data-ingestor --replicas=+2
```

   - Reduce work per message (disable expensive enrichment temporarily).

4. Stabilize rebalances:
   - Tune consumer `session.timeout.ms`, `max.poll.interval.ms`, and `max.poll.records`.
   - Avoid rolling all consumers at once; use surge/partition-aware rollouts.

5. Verification:
   - Lag stops growing and returns toward baseline
   - Error logs decrease and throughput recovers

## Cost Impact (If applicable)

- Scaling consumers increases compute cost; fixing downstream bottlenecks often reduces required replica count.

---


