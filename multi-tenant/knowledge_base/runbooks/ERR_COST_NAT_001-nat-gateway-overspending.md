# Title: NAT Gateway Overspending (Data Processing + Cross-AZ Traffic)

## Metadata

- Service: shared-infra
- Category: Cost
- Severity: P1

## Symptoms

- Error Codes: `ERR_COST_NAT_001`
- Cost signals:
  - NAT Gateway spend exceeds **$500/month** (or **> 20%** increase week-over-week)
  - CUR/Cost Explorer shows large `NatGateway-Bytes` / data processing charges
- Network signals:
  - High egress from private subnets to AWS services that could use VPC endpoints (S3, ECR, CloudWatch, STS)
  - Cross-AZ NAT usage (subnet routes to NAT in a different AZ)

## Root Cause Analysis (RCA)

1. **Missing VPC endpoints** forces traffic to AWS services through NAT (paying data processing unnecessarily).
2. **Cross-AZ routing** to a NAT in another AZ adds cross-AZ data charges and latency.
3. **Chatty outbound traffic** (package downloads, container pulls, frequent calls) from private subnets amplifies NAT costs.

## Resolution Steps

1. Confirm NAT is the driver in cost tools (CUR/Cost Explorer).

2. Inventory NAT gateways and route tables.

```bash
aws ec2 describe-nat-gateways --filter Name=state,Values=available --output table
aws ec2 describe-route-tables --output table
```

3. Add VPC endpoints to bypass NAT for common AWS services:
   - Gateway endpoints: S3, DynamoDB
   - Interface endpoints: ECR (api + dkr), CloudWatch Logs, STS, SSM, KMS (as needed)

```bash
# Example: create S3 gateway endpoint (must attach to route tables)
aws ec2 create-vpc-endpoint \
  --vpc-id <vpc-id> \
  --service-name com.amazonaws.<region>.s3 \
  --vpc-endpoint-type Gateway \
  --route-table-ids <rtb-1> <rtb-2>
```

4. Fix cross-AZ NAT routing:
   - Ensure each private subnet routes to a NAT gateway in the **same AZ**.
   - If using one NAT for all AZs, evaluate adding one per AZ (trade-off: hourly NAT cost vs data charges).

5. Reduce outbound chatter:
   - Mirror/package cache (apt/yum/pip) internally
   - Use ECR pull-through cache or minimize image pulls
   - Ensure workloads use regional endpoints and keep-alives

6. Verification:
   - NAT data processing drops (within 24–72h)
   - Endpoint hit metrics increase
   - Cost trend flattens or decreases in the next billing cycle

## Cost Impact (If applicable)

- VPC endpoints have hourly and data processing costs, but they often reduce overall spend by removing large NAT data processing charges.
- Fixing cross-AZ routing can significantly reduce both NAT and inter-AZ charges.

---


