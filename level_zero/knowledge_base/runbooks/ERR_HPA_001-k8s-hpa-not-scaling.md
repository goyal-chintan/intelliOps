# Title: HPA Not Scaling (Requests Increase but Replicas Stay Flat)

## Metadata

- Service: platform-infra
- Category: Reliability
- Severity: P1

## Symptoms

- Error Codes: `ERR_HPA_001`
- Kubernetes:
  - Traffic increases but `kubectl get hpa` shows `CURRENT` metric below/unknown and replicas don’t scale
  - Pods are overloaded; latency P95 > **2x baseline for 10m**
- Metrics/logs (common patterns):
  - `ERR_HPA_001 HPA not scaling`
  - Metrics server / custom metrics errors: `failed to get cpu utilization` / `unable to fetch metrics`

## Root Cause Analysis (RCA)

1. **Metrics pipeline broken**: metrics-server or custom metrics adapter unavailable → HPA can’t read metrics.
2. **Wrong requests/targets**: CPU requests missing/too high, or target utilization mis-set → HPA never triggers.
3. **Scale constraints**: `maxReplicas` too low or cluster has insufficient capacity (pods remain Pending).

## Resolution Steps

1. Inspect HPA status and events.

```bash
kubectl -n prod get hpa
kubectl -n prod describe hpa <hpa-name> | egrep -n "Metrics|FailedGetResourceMetric|FailedGetPodsMetric|Current|Target|Events"
```

2. Verify metrics availability.

```bash
kubectl -n kube-system get pods -l k8s-app=metrics-server
kubectl -n kube-system logs deploy/metrics-server --since=30m | tail -n 120
kubectl -n prod top pod | head -n 20
```

3. Check workload CPU requests/limits and HPA target.

```bash
kubectl -n prod get deploy <workload> -o jsonpath='{.spec.template.spec.containers[*].resources}' ; echo
kubectl -n prod get hpa <hpa-name> -o yaml | egrep -n "minReplicas|maxReplicas|targetCPUUtilizationPercentage|metrics"
```

4. Immediate mitigation:
   - Manually scale replicas if safe while fixing HPA.

```bash
kubectl -n prod scale deploy/<workload> --replicas=6
```

5. Fix root cause:
   - Restore metrics-server or custom metrics adapter.
   - Set sane CPU requests and target utilization (start: 60–75%).
   - Raise `maxReplicas` and ensure cluster autoscaler can add nodes.

6. Verification:
   - HPA shows `AbleToScale=True`, `ScalingActive=True`
   - Replicas increase under load and latency improves

## Cost Impact (If applicable)

- Correct HPA prevents over-provisioning (cost) while maintaining SLOs.
- Manual scaling or higher maxReplicas may increase spend; use load tests to right-size.

---


