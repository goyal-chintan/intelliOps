# Title: Kubernetes Node DiskPressure (Evictions / ImageFS Full)

## Metadata

- Service: platform-infra
- Category: Reliability
- Severity: P1

## Symptoms

- Error Codes: `ERR_K8S_DISK_001`
- Kubernetes:
  - Pods evicted with `Reason: Evicted` and message `The node was low on resource: ephemeral-storage`
  - Node condition shows `DiskPressure=True`
  - Kubelet events mention `imagefs` or `nodefs` low space
- Metrics:
  - `kube_node_status_condition{condition="DiskPressure",status="true"} == 1`
  - `node_filesystem_avail_bytes / node_filesystem_size_bytes < 0.10` (nodefs/imagefs)

## Root Cause Analysis (RCA)

1. **Log/temporary file growth**: unbounded logs, large `/tmp` usage, or local caches fill node disks.
2. **Container image accumulation**: old images not pruned; frequent deploys pull large images.
3. **Ephemeral storage not requested/limited**: pods consume excessive ephemeral storage without enforcement.

## Resolution Steps

1. Identify impacted nodes and evicted pods.

```bash
kubectl -n prod get events --sort-by=.lastTimestamp | egrep -n "DiskPressure|ephemeral-storage|Evicted" | tail -n 80
kubectl describe node <node-name> | egrep -n "DiskPressure|imagefs|nodefs|Allocatable|Capacity"
```

2. Check disk usage on the node (requires node access; use `kubectl debug` if allowed).

```bash
kubectl debug node/<node-name> -it --image=busybox -- chroot /host sh -c "df -h; du -xh /var/lib/containerd /var/log | sort -h | tail -n 20"
```

3. Immediate mitigation:
   - Drain the node to stop evictions from impacting critical services.

```bash
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data --grace-period=60
```

   - Prune unused images/containers on the node (method depends on runtime; coordinate with platform team).
   - Increase node disk size or rotate nodes if the fleet is persistently full.

4. Permanent fixes:
   - Enforce log rotation (container runtime + app loggers).
   - Set `resources.requests/limits.ephemeral-storage` on heavy writers.
   - Move caches/temp to PVCs when appropriate.
   - Reduce image size and layers; avoid frequent full-image pulls.

5. Verification:
   - Node condition `DiskPressure=False`
   - Evictions stop
   - Disk utilization remains below thresholds under steady load

## Cost Impact (If applicable)

- Larger node disks increase monthly spend, but are often cheaper than repeated incident response.
- Better log rotation and image hygiene reduce disk needs and can lower storage and operational costs.

---


