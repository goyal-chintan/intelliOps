# Title: Ephemeral Storage Exceeded (Log / Temp File Bloat)

## Metadata

- Service: platform-infra
- Category: Reliability
- Severity: P1

## Symptoms

- Error Codes: `ERR_K8S_DISK_002`
- Kubernetes:
  - Pods evicted: `Reason: Evicted` with message `low on resource: ephemeral-storage`
  - Container writes fail with `No space left on device`
- Logs (common patterns):
  - `ERR_K8S_DISK_002 No space left on device`
  - `write /tmp/...: no space left on device`
  - Sidecar/log agent errors: `failed to write checkpoint`

## Root Cause Analysis (RCA)

1. **Unbounded application logs** (or debug logging enabled) fill nodefs and/or emptyDir volumes.
2. **Large temp files** written to `/tmp` or working directories (Spark shuffle spill, model artifacts, checkpoint staging).
3. **No ephemeral storage limits**: pods consume ephemeral storage without enforcement or monitoring until eviction.

## Resolution Steps

1. Confirm eviction reason and identify the offending pod/container.

```bash
kubectl -n prod get events --sort-by=.lastTimestamp | egrep -n "ephemeral-storage|Evicted|No space left" | tail -n 80
kubectl -n prod describe pod <pod-name> | egrep -n "ephemeral-storage|Evicted|No space left|Reason"
```

2. Inspect pod volumes and whether it uses `emptyDir` for temp/logs.

```bash
kubectl -n prod get pod <pod-name> -o yaml | egrep -n "emptyDir|volumeMounts|mountPath"
```

3. Immediate mitigation:
   - Reduce logging verbosity / disable debug flags.
   - Restart or roll the workload after cleaning disk on the node (if safe).
   - Drain the worst node if evictions are cascading.

```bash
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data --grace-period=60
```

4. Add enforcement:
   - Set ephemeral storage requests/limits on heavy writers.

```yaml
resources:
  requests:
    ephemeral-storage: "2Gi"
  limits:
    ephemeral-storage: "4Gi"
```

   - Set `emptyDir.sizeLimit` for temp volumes where applicable.

```yaml
volumes:
  - name: tmp
    emptyDir:
      sizeLimit: "2Gi"
```

5. Redirect large temp/log data to durable storage:
   - Mount a PVC for spill/checkpoints/artifacts.
   - Ensure log shipping to external storage and local retention is bounded.

6. Verification:
   - Evictions stop
   - Disk usage remains below thresholds during peak
   - `No space left on device` errors disappear

## Cost Impact (If applicable)

- Adding PVC capacity increases storage cost, but prevents repeated evictions and associated compute waste.
- Lower log volume can reduce downstream log ingestion/storage costs (CloudWatch/OpenSearch/S3).

---


