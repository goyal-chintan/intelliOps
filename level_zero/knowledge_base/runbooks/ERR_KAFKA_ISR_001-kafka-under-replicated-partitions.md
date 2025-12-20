# Title: Kafka Under-Replicated Partitions (ISR Shrink)

## Metadata

- Service: platform-infra
- Category: Reliability
- Severity: P0

## Symptoms

- Error Codes: `ERR_KAFKA_ISR_001`
- Metrics:
  - `UnderReplicatedPartitions > 0` for **5m**
  - `OfflinePartitionsCount > 0` (critical)
- Logs (common patterns):
  - `ERR_KAFKA_ISR_001 ISR shrink`
  - Broker logs: `ReplicaFetcherThread` errors, `NotEnoughReplicas`/`NotEnoughReplicasAfterAppend`
- Impact:
  - Increased risk of data loss if a broker fails
  - Producer acks may fail or slow down

## Root Cause Analysis (RCA)

1. **Broker disk/IO saturation** slows replication; followers fall behind.
2. **Network issues** between brokers (packet loss, cross-AZ latency).
3. **Broker instability** (GC pauses, OOM, rolling restarts) disrupts ISR.

## Resolution Steps

1. Confirm URP/ISR issue and identify affected topics/partitions.

```bash
# Command varies by distribution; examples:
kafka-topics --bootstrap-server <broker:9092> --describe | egrep -n "UnderReplicated|Offline"
```

2. Check broker health and resource usage.

```bash
kubectl -n prod get pods -l app=kafka -o wide
kubectl -n prod top pod -l app=kafka
kubectl -n prod logs -l app=kafka --since=30m | egrep -n "ERR_KAFKA_ISR_001|ReplicaFetcherThread|NotEnoughReplicas|UnderReplicated"
```

3. Immediate mitigation:
   - Stop rolling restarts until the cluster stabilizes.
   - If disk is full/near full, expand storage or clean logs (retention).
   - If a broker is unhealthy, replace it (cordon/drain node, recreate pod).

4. Reduce replication load temporarily:
   - Lower produce rate (throttle producers) if URP is climbing rapidly.

5. Permanent fixes:
   - Right-size broker disks/IOPS; tune retention and segment settings.
   - Ensure replicas are spread across AZs and nodes.
   - Monitor and alert on URP/Offline partitions and disk utilization.

6. Verification:
   - `UnderReplicatedPartitions` returns to 0
   - Producer success rate and end-to-end pipeline health normalize

## Cost Impact (If applicable)

- Increasing broker disk/IOPS costs more, but URP incidents often cause major outages; right-sizing is usually cheaper than downtime.

---


