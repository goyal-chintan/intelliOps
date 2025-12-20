# Title: Data Transfer Costs High (Cross-AZ / Egress)

## Metadata

- Service: shared-infra
- Category: Cost
- Severity: P2

## Symptoms

- Error Codes: `ERR_COST_XFER_001`
- Cost signals:
  - “Data Transfer” line items increase by **> 20% month-over-month**
  - NAT Gateway costs may also rise (if used for egress)
- Infra signals:
  - Pods frequently communicating across AZs
  - Internal services pinned to a single AZ causing cross-AZ calls

## Root Cause Analysis (RCA)

1. **Cross-AZ chatter**: services in different AZs communicate heavily (service discovery + load balancing spreads calls).
2. **Misplaced NAT/egress**: private subnets route to NAT in another AZ (extra inter-AZ charges).
3. **Large data flows**: moving datasets between services instead of co-locating compute and data.

## Resolution Steps

1. Identify the driver in Cost Explorer/CUR:
   - Filter by `UsageType` like `DataTransfer-Regional-Bytes` and `DataTransfer-Out-Bytes`.

2. Validate cross-AZ traffic patterns:
   - Check if services are deployed across AZs and how traffic is balanced.

```bash
kubectl -n prod get pods -o wide | head -n 50
kubectl get nodes -L topology.kubernetes.io/zone
```

3. Reduce cross-AZ traffic:
   - Use zonal routing where possible (topology-aware hints, zonal services).
   - Co-locate chatty services in the same AZ for stateful flows.
   - For data pipelines, process data where it lives (avoid shuffling large datasets).

4. Fix NAT cross-AZ routing (common high-cost issue):
   - Ensure each private subnet routes to a NAT gateway in the same AZ.

5. Verification:
   - Data transfer spend trend decreases over 24–72 hours
   - Latency often improves (less cross-AZ hops)

## Cost Impact (If applicable)

- Reducing inter-AZ traffic can materially reduce monthly bills and often improves performance.
- Zonal routing may increase operational complexity; apply only to the highest-cost/highest-chatter paths.

---


