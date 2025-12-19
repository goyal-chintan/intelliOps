# Title: Unused Load Balancers / Idle ALBs (Paying for Nothing)

## Metadata

- Service: shared-infra
- Category: Cost
- Severity: P2

## Symptoms

- Error Codes: `ERR_COST_LB_001`
- Cost signals:
  - ELB/ALB spend present but traffic is near zero
  - Large count of load balancers compared to active services
- Inventory signals:
  - Load balancers with `HealthyHostCount = 0` or no registered targets
  - Old stacks/environments left behind (staging, preview)

## Root Cause Analysis (RCA)

1. **Orphaned infrastructure**: environments deleted but LBs left behind.
2. **K8s Ingress churn**: frequent creation of Ingress resources without cleanup.
3. **Over-segmentation**: one LB per microservice when a shared ingress would suffice.

## Resolution Steps

1. List load balancers and find idle candidates.

```bash
aws elbv2 describe-load-balancers --query "LoadBalancers[].{Name:LoadBalancerName,Arn:LoadBalancerArn,Type:Type,State:State.Code,DNS:DNSName}" --output table
```

2. Inspect target groups and health.

```bash
aws elbv2 describe-target-groups --load-balancer-arn <lb-arn> --output table
aws elbv2 describe-target-health --target-group-arn <tg-arn>
```

3. Verify ownership and safe deletion:
   - Check tags (owner, env, app).
   - For K8s-managed LBs, check the associated Ingress/Service.

```bash
kubectl -n prod get ingress
kubectl -n prod describe ingress <ingress-name>
```

4. Delete unused LBs (after validation).

```bash
aws elbv2 delete-load-balancer --load-balancer-arn <lb-arn>
```

5. Prevent recurrence:
   - Enforce tagging + TTL for ephemeral environments.
   - Use a shared ingress where appropriate.
   - Add periodic audits for LBs with no targets or low request count.

## Cost Impact (If applicable)

- Deleting unused load balancers yields immediate savings (hourly LB cost + LCU costs).
- Consolidating ingress can reduce ongoing cost but must be balanced against isolation/security needs.

---


