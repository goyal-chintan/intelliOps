# Title: Unused / Orphaned EBS Volumes (Detached Storage)

## Metadata

- Service: shared-infra
- Category: Cost
- Severity: P2

## Symptoms

- Error Codes: `ERR_COST_EBS_001`
- Cost signals:
  - EBS spend increases with no corresponding EC2/EKS usage growth
  - Many volumes billed but not attached to instances
- Inventory signals:
  - Volumes in `available` state for > **7 days**
  - Missing tags / ownership → nobody deletes them

## Root Cause Analysis (RCA)

1. **Volumes left behind** after instance termination or failed automation.
2. **Kubernetes PV reclaim policy = Retain** keeps EBS volumes after PVC deletion.
3. **Lack of tagging/ownership** prevents cleanup and accountability.

## Resolution Steps

1. List detached volumes.

```bash
aws ec2 describe-volumes \
  --filters Name=status,Values=available \
  --query "Volumes[].{VolumeId:VolumeId,Size:Size,Type:VolumeType,CreateTime:CreateTime,Tags:Tags}" \
  --output table
```

2. For each candidate, verify it is truly unused:
   - Check CloudTrail for recent attach/detach.
   - Confirm it is not referenced by a Kubernetes PV.

```bash
# Kubernetes: find PVs that still reference EBS volumes
kubectl get pv -o json | jq -r '.items[] | select(.spec.awsElasticBlockStore!=null) | [.metadata.name, .spec.awsElasticBlockStore.volumeID] | @tsv'
```

3. Snapshot then delete (safer cleanup path).

```bash
aws ec2 create-snapshot --volume-id <vol-id> --description "pre-delete snapshot for <vol-id>"
aws ec2 delete-volume --volume-id <vol-id>
```

4. Prevent recurrence:
   - Enforce tags (owner, app, env, ttl) via IaC and admission policies.
   - For Kubernetes StorageClasses, use `reclaimPolicy: Delete` unless retention is required.
   - Add AWS Config rules / scheduled reports for detached volumes > N days.

## Cost Impact (If applicable)

- Deleting unused volumes provides immediate savings (storage is billed per GB-month).
- Snapshot-first cleanup adds a small snapshot cost but reduces risk; add retention to avoid snapshot sprawl.

---


