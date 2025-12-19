# Title: NetworkPolicy Blocking Traffic (Service-to-Service Outage)

## Metadata

- Service: platform-infra
- Category: Reliability
- Severity: P1

## Symptoms

- Error Codes: `ERR_K8S_NETPOL_001`
- Logs (common patterns):
  - `ERR_K8S_NETPOL_001 connection timed out`
  - `i/o timeout` / `connection refused` (depending on CNI)
  - Sudden dependency failures after a policy change
- Kubernetes:
  - No pod restarts; services appear healthy but cannot talk to each other

## Root Cause Analysis (RCA)

1. **Default-deny policy** applied without required allow rules.
2. **Label mismatch**: policy selectors don’t match pods/services as intended.
3. **Egress blocked** to DNS or external dependencies.

## Resolution Steps

1. Confirm connectivity failure from a source pod to a destination service.

```bash
kubectl -n prod exec -it deploy/checkout-api -- sh -c "wget -qO- http://payment-gw:8080/health || true"
kubectl -n prod logs deploy/checkout-api --since=30m | egrep -n "ERR_K8S_NETPOL_001|timeout|connection refused"
```

2. List NetworkPolicies in the namespaces involved.

```bash
kubectl -n prod get netpol
kubectl -n prod describe netpol <policy-name>
```

3. Validate selectors and labels.

```bash
kubectl -n prod get pod -l app=checkout-api --show-labels
kubectl -n prod get pod -l app=payment-gw --show-labels
```

4. Immediate mitigation:
   - Temporarily relax the policy (allow required traffic) or roll back the recent policy change.

```bash
kubectl -n prod rollout history deploy/<netpol-controller-if_any>
# Or revert the manifest from Git/IaC and re-apply
```

5. Add explicit allows (example concept):
   - Allow egress to CoreDNS (UDP/TCP 53)
   - Allow egress from checkout-api to payment-gw on port 8080

6. Verification:
   - Connectivity checks succeed
   - Dependency errors disappear

## Cost Impact (If applicable)

- Minimal direct cost impact, but outages can cause retry storms and over-scaling.

---


