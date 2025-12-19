# Title: Cluster DNS Resolution Failures (CoreDNS)

## Metadata

- Service: platform-infra
- Category: Reliability
- Severity: P0

## Symptoms

- Error Codes: `ERR_DNS_001`
- Logs (common patterns):
  - `ERR_DNS_001 no such host`
  - `Temporary failure in name resolution`
  - `SERVFAIL` / `NXDOMAIN` for known services
- Metrics:
  - Spike in request failures across multiple services simultaneously
  - CoreDNS `errors_total` increases; latency increases
- K8s symptoms:
  - Apps fail to reach dependencies by service DNS name

## Root Cause Analysis (RCA)

1. **CoreDNS overloaded** (QPS spike, too few replicas, CPU throttling) causing timeouts and SERVFAIL.
2. **Upstream resolver issues** (node `/etc/resolv.conf` misconfigured, VPC DNS issues).
3. **Misconfigured stubDomains / rewrite rules** causing queries to loop or misroute.

## Resolution Steps

1. Confirm DNS errors from application pods.

```bash
kubectl -n prod logs deploy/checkout-api --since=15m | egrep -n "ERR_DNS_001|no such host|name resolution|SERVFAIL"
```

2. Check CoreDNS health, logs, and replica count.

```bash
kubectl -n kube-system get deploy coredns -o wide
kubectl -n kube-system logs deploy/coredns --since=30m | tail -n 200
kubectl -n kube-system top pod -l k8s-app=kube-dns
```

3. Reproduce DNS from a pod (in-cluster).

```bash
kubectl -n prod run dns-debug --rm -it --image=busybox --restart=Never -- sh -c "nslookup kubernetes.default.svc.cluster.local && nslookup payment-gw.prod.svc.cluster.local"
```

4. Immediate mitigation:
   - Scale CoreDNS.

```bash
kubectl -n kube-system scale deploy/coredns --replicas=4
```

   - If CPU throttling is present, increase CoreDNS CPU requests/limits.

5. Validate config:

```bash
kubectl -n kube-system get cm coredns -o yaml
```

6. Verification:
   - DNS lookups succeed consistently
   - Error rates across services drop back to baseline

## Cost Impact (If applicable)

- Scaling CoreDNS has small cost impact; prolonged DNS failures cause retries/timeouts that waste compute and can trigger autoscaling.

---


