# Title: Readiness Probe Failing (Pod Running but Not Ready)

## Metadata

- Service: checkout-api
- Category: Reliability
- Severity: P1

## Symptoms

- Error Codes: `ERR_K8S_PROBE_001`
- Kubernetes:
  - Pods show `0/1 Ready` for > **5 minutes**
  - Service has fewer ready endpoints → 503s/latency increase
- Events/logs (common patterns):
  - `ERR_K8S_PROBE_001 readiness probe failed`
  - `Readiness probe failed: HTTP probe failed with statuscode: 500`
  - `context deadline exceeded` (probe timeout)

## Root Cause Analysis (RCA)

1. **Dependency check in readiness** (DB/Kafka) fails; app is alive but not “ready”.
2. **Probe misconfiguration**: wrong path/port, too aggressive timeouts, or TLS mismatch.
3. **Startup slowness**: cold cache/migrations/large model load makes readiness slow.

## Resolution Steps

1. Identify non-ready pods and inspect events.

```bash
kubectl -n prod get pods -l app=checkout-api
kubectl -n prod describe pod <pod-name> | egrep -n "Readiness probe failed|ERR_K8S_PROBE_001|Events|Warning"
```

2. Check the readiness configuration on the deployment.

```bash
kubectl -n prod get deploy checkout-api -o yaml | egrep -n "readinessProbe|httpGet|tcpSocket|exec|initialDelaySeconds|timeoutSeconds|failureThreshold|periodSeconds"
```

3. Test the readiness endpoint from inside the pod (if possible).

```bash
kubectl -n prod exec -it <pod-name> -- sh -c "wget -qO- http://127.0.0.1:8080/health/ready || true"
```

4. Determine if the failure is dependency-related:
   - If DB is down, use DB runbooks (e.g., `ERR_DB_CON_001`, `ERR_DB_LOCK_001`).
   - If DNS is failing, use `ERR_DNS_001`.

5. Immediate mitigation:
   - If readiness is too strict, temporarily loosen readiness criteria (avoid using full dependency checks).
   - Increase `initialDelaySeconds` and `timeoutSeconds` for slow startups.

6. Verification:
   - Pods become `Ready`
   - Service endpoints list includes expected number of pods

```bash
kubectl -n prod get endpoints checkout-api -o wide
```

## Cost Impact (If applicable)

- Non-ready pods can trigger autoscaling and waste compute. Fixing readiness reduces “paid but not serving” capacity.

---


