# Title: Kubernetes Pod OOMKilled (Exit Code 137)

## Metadata

- Service: ml-serving
- Category: Reliability
- Severity: P1

## Symptoms

- Error Codes: `ERR_K8S_OOM_001`
- Kubernetes:
  - Pod restarts increase; `kubectl describe pod` shows `OOMKilled`
  - Container `Last State: Terminated`, `Reason: OOMKilled`, `Exit Code: 137`
- Metrics (for 5–10m):
  - `container_memory_working_set_bytes / container_spec_memory_limit_bytes > 0.95`
  - `kube_pod_container_status_restarts_total` increases rapidly
- Application logs may show abrupt termination or partial logs near the crash point.

## Root Cause Analysis (RCA)

1. **Memory limit too low** for peak traffic or batch size (model loads, embeddings batch, large responses).
2. **Memory leak** (unbounded caches, growing queues, per-request allocations not freed).
3. **Sudden cardinality spike** (new tenant, hot shard, retries) increases resident memory unexpectedly.

## Resolution Steps

1. Confirm OOMKilled and capture container/resource details.

```bash
kubectl -n prod get pods -l app=ml-serving -o wide
kubectl -n prod describe pod -l app=ml-serving | egrep -n "OOMKilled|Exit Code|Last State|Reason|Killed"
kubectl -n prod get events --sort-by=.lastTimestamp | tail -n 50
```

2. Check current memory requests/limits.

```bash
kubectl -n prod get deploy ml-serving -o jsonpath='{.spec.template.spec.containers[*].resources}' ; echo
```

3. Inspect real-time usage (if metrics-server is installed).

```bash
kubectl -n prod top pod -l app=ml-serving
kubectl -n prod top node
```

4. Immediate mitigation:
   - Reduce load (throttle QPS, reduce batch size, disable expensive features).
   - Scale out replicas (may reduce per-pod memory pressure if load is the cause).

```bash
kubectl -n prod scale deploy/ml-serving --replicas=+2
```

   - Increase memory limit cautiously (requires rollout).

```bash
kubectl -n prod edit deploy/ml-serving
# Increase resources.limits.memory and resources.requests.memory appropriately
kubectl -n prod rollout status deploy/ml-serving --timeout=5m
```

5. Permanent fixes:
   - Right-size memory using observed peak + headroom (20–30%).
   - Add memory profiling / heap snapshots.
   - Bound caches and queues; enforce max batch size.
   - Configure HPA on CPU/latency and/or queue depth (avoid single pod overload).

6. Verification:
   - Restart rate returns to baseline
   - Memory working set stays < **80–85%** of limit
   - P95 latency and error rate normalize

## Cost Impact (If applicable)

- Increasing pod memory limits can force larger node types or fewer pods per node (higher $/month).
- Fixing leaks and right-sizing often reduces node count and improves cluster bin packing.

---


