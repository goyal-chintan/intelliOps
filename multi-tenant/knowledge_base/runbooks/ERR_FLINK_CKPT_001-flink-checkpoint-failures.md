# Title: Flink Checkpoint Failures (Expired / Failed / Never Completes)

## Metadata

- Service: data-ingestor
- Category: Reliability
- Severity: P1

## Symptoms

- Error Codes: `ERR_FLINK_CKPT_001`
- Flink logs (common patterns):
  - `CheckpointCoordinator` + `Failed to complete checkpoint`
  - `Checkpoint expired before completing`
  - `DeclineCheckpointException`
  - `Failed to trigger checkpoint`
- Metrics (names vary by distribution; any of the following for 10m):
  - `numFailedCheckpoints > 0`
  - `lastCheckpointDuration > checkpoint_timeout`
  - `checkpointAlignmentTime` spikes
- Operational impact:
  - Increased recovery time, potential data loss risk, or job restarts (if configured to fail on checkpoint errors)

## Root Cause Analysis (RCA)

1. **State backend/storage issues**: checkpoint directory unavailable, S3/HDFS permission errors, throttling, or high latency.
2. **Backpressure and long alignment**: downstream sink slow → checkpoint barriers take too long.
3. **Resource limits**: insufficient TaskManager memory/disk for RocksDB state, causing spills and timeouts.

## Resolution Steps

1. Confirm checkpoint failures in JobManager logs.

```bash
kubectl -n prod logs deploy/flink-jobmanager --since=30m | egrep -n "ERR_FLINK_CKPT_001|CheckpointCoordinator|checkpoint|DeclineCheckpointException|expired"
```

2. Check Flink job status and recent restarts.

```bash
kubectl -n prod get pods -l app=flink -o wide
kubectl -n prod get events --sort-by=.lastTimestamp | tail -n 60
```

3. Validate checkpoint storage access (example: S3-backed checkpoints).
   - Confirm credentials/IRSA and bucket policy allow read/write/delete.

```bash
aws s3 ls s3://<checkpoint-bucket>/<prefix>/ --summarize --human-readable
```

4. Check for backpressure / slow sinks:
   - In Flink UI, inspect “Backpressure” and task latencies.
   - If using Kafka/S3 sinks, check sink-side latency and error logs.

5. Mitigate:
   - Increase checkpoint timeout (temporary) and/or reduce checkpoint interval.
   - Reduce state size (enable incremental checkpoints, tune state TTL).
   - Scale TaskManagers (more slots, more memory) if state is too large.

```properties
# Example config knobs (set via Helm/ConfigMap)
execution.checkpointing.interval: 60s
execution.checkpointing.timeout: 10min
state.checkpoints.num-retained: 10
state.backend.incremental: true
```

6. If disk pressure is contributing (RocksDB state on local disk):
   - Ensure `ephemeral-storage` is sufficient and nodes aren’t DiskPressure.
   - Move state to a faster disk class or increase disk size.

7. Verification:
   - `numFailedCheckpoints` stops increasing
   - A new completed checkpoint is observed within 1–2 intervals
   - Job remains stable without restarts

## Cost Impact (If applicable)

- Increasing checkpoint retention and state storage increases object storage cost.
- Fixing backpressure reduces wasted compute from retries/restarts and can lower overall streaming cost.

---


