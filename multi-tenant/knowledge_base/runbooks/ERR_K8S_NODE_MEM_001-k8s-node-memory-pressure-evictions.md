# Title: Kubernetes Node MemoryPressure (Pod Evictions)

## Metadata

- Service: platform-infra
- Category: Reliability
- Severity: P0

## Symptoms

- Error Codes: `ERR_K8S_NODE_MEM_001`
- Kubernetes:
  - Pods evicted with `Reason: Evicted` and message `The node was low on resource: memory`
  - Node condition shows `MemoryPressure=True`
  - Spike in `kube_pod_container_status_restarts_total` across multiple services
- Metrics (5–10m):
  - `kube_node_status_condition{condition="MemoryPressure",status="true"} == 1`
  - `node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes < 0.10`

## Root Cause Analysis (RCA)

1. **Overcommit / under-requesting**: pods use more memory than requested, and many co-located pods exceed node capacity.
2. **Memory leak or burst** in one or more workloads causes node-wide pressure and evictions.
3. **System daemons / kubelet reservation mis-sized** (insufficient `--system-reserved` / `--kube-reserved` headroom).

## Resolution Steps

1. Identify affected nodes and evicted pods.

```bash
kubectl -n prod get events --sort-by=.lastTimestamp | egrep -n "Evicted|MemoryPressure" | tail -n 50
kubectl get nodes
kubectl describe node <node-name> | egrep -n "MemoryPressure|Allocatable|Capacity|Non-terminated Pods"
```

2. Find top memory consumers on the node.

```bash
kubectl -n prod top pod --sort-by=memory | head -n 25
kubectl top node --sort-by=memory | head -n 10
```

3. Immediate mitigation:
   - Drain the worst node to reschedule pods (may reduce blast radius).

```bash
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data --grace-period=60
```

   - Scale the cluster / add capacity (EKS managed node group / autoscaler).
   - Temporarily reduce memory-heavy workloads (scale down batch jobs).

4. Fix resource governance:
   - Set realistic `resources.requests.memory` and `resources.limits.memory` for top offenders.
   - Enable VPA recommendations (even if not auto-applying).
   - Ensure critical pods have higher priority classes to reduce eviction risk.

5. Verification:
   - Node condition `MemoryPressure=False`
   - Evictions stop
   - Overall service error rates normalize

## Cost Impact (If applicable)

- Adding node capacity increases compute cost; however, correct requests/limits prevents chronic over-provisioning.
- Right-sizing often reduces required node count and improves bin packing, lowering steady-state spend.

---


