# Title: Kubernetes CrashLoopBackOff (Repeated Container Crashes)

## Metadata

- Service: checkout-api
- Category: Reliability
- Severity: P1

## Symptoms

- Error Codes: `ERR_K8S_CRASH_001`
- Kubernetes:
  - Pod shows `CrashLoopBackOff`
  - Restart count increases rapidly
- Logs/events:
  - `Back-off restarting failed container`
  - App logs show startup exception or config missing
  - `ERR_K8S_CRASH_001 startup failed`

## Root Cause Analysis (RCA)

1. **Bad deploy/config**: missing env var/secret, invalid config file, wrong command/args.
2. **Dependency required at startup** (DB, Kafka, config service) is unavailable → app exits.
3. **Probes misconfigured**: liveness probe too aggressive kills the pod before it becomes ready.

## Resolution Steps

1. Identify failing pods and look at events.

```bash
kubectl -n prod get pods -l app=checkout-api
kubectl -n prod describe pod <pod-name> | egrep -n "CrashLoopBackOff|Back-off|Exit Code|Reason|Liveness|Readiness"
```

2. Inspect container logs for the last crash.

```bash
kubectl -n prod logs <pod-name> --previous
kubectl -n prod logs <pod-name> | egrep -n "ERR_K8S_CRASH_001|Exception|FATAL|panic|Traceback"
```

3. Validate config and secrets exist and are mounted correctly.

```bash
kubectl -n prod get cm,secret | egrep -n "checkout-api|db|kafka|config"
kubectl -n prod describe deploy checkout-api | egrep -n "ENV|ConfigMap|Secret|Mounts|Volumes"
```

4. If caused by a recent deploy:
   - Roll back.

```bash
kubectl -n prod rollout undo deploy/checkout-api
kubectl -n prod rollout status deploy/checkout-api --timeout=5m
```

5. Fix probe issues (common):
   - Increase `initialDelaySeconds`
   - Increase `failureThreshold`
   - Ensure readiness uses a lightweight check

6. Verification:
   - Restart count stops increasing
   - Pods become `Ready` and traffic stabilizes

## Cost Impact (If applicable)

- Crash loops waste CPU and can trigger autoscaling, increasing cost without serving traffic.

---


