# Title: Kubernetes CPU Throttling / Node CPU Saturation

## Metadata

- Service: platform-infra
- Category: Performance
- Severity: P1

## Symptoms

- Error Codes: `ERR_K8S_NODE_CPU_001`
- User impact:
  - P95 latency increases by **> 2x baseline for 10m**
  - `HTTP 504/503` errors exceed **1% for 5m** (if upstream timeouts occur)
- Metrics (5–10m):
  - `node_cpu_utilization > 0.90`
  - `container_cpu_cfs_throttled_periods_total / container_cpu_cfs_periods_total > 0.20` (throttling)
  - `container_cpu_usage_seconds_total` approaches CPU limits/requests
- Logs (common patterns):
  - `context deadline exceeded`
  - `upstream request timeout`
  - `ERR_K8S_NODE_CPU_001 CPU throttling detected`

## Root Cause Analysis (RCA)

1. **CPU limits too low** for latency-sensitive services → CFS throttling increases tail latency.
2. **Node is saturated** (insufficient capacity or noisy neighbor) → run queue increases and scheduling latency rises.
3. **CPU-heavy regression** (new feature, increased serialization, GC pressure) increases per-request CPU.

## Resolution Steps

1. Identify hotspots: which pods and nodes are CPU constrained.

```bash
kubectl -n prod top pod --sort-by=cpu | head -n 25
kubectl top node --sort-by=cpu | head -n 10
```

2. Confirm throttling (Prometheus query examples; adapt metric names to your stack):
   - Throttling ratio by pod:
     - `rate(container_cpu_cfs_throttled_periods_total[5m]) / rate(container_cpu_cfs_periods_total[5m])`

3. Check pod CPU requests/limits for the top offender.

```bash
kubectl -n prod get deploy <workload> -o jsonpath='{.spec.template.spec.containers[*].resources}' ; echo
```

4. Immediate mitigation (choose the safest first):
   - Scale out replicas (reduces per-pod CPU if load is the driver).

```bash
kubectl -n prod scale deploy/<workload> --replicas=+2
```

   - Increase CPU requests and/or remove tight CPU limits for latency-critical services (requires rollout).
     - Many teams set **requests** and omit **limits** for CPU on critical APIs to avoid throttling.

```bash
kubectl -n prod edit deploy/<workload>
kubectl -n prod rollout status deploy/<workload> --timeout=5m
```

   - Add node capacity (cluster autoscaler / node group scale-out).

5. Permanent fixes:
   - Right-size requests using observed P95 CPU usage + headroom.
   - Add HPA based on CPU and/or request latency.
   - Investigate code regressions and reduce CPU per request (profiling, remove expensive logging, optimize serialization).

6. Verification:
   - Throttling ratio drops < **5%**
   - Node CPU utilization stabilizes < **80–85%**
   - P95 latency returns to baseline

## Cost Impact (If applicable)

- Scaling replicas or adding nodes increases compute spend.
- Fixing throttling often improves throughput so you can run fewer replicas for the same SLO.

---


