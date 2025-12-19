# Title: EBS Snapshot Accumulation (Retention Misconfigured)

## Metadata

- Service: shared-infra
- Category: Cost
- Severity: P2

## Symptoms

- Error Codes: `ERR_COST_EBS_SNAP_001`
- Cost signals:
  - Snapshot spend increases by **> 20% month-over-month**
  - Large number of snapshots with old timestamps and no lifecycle policy
- Inventory signals:
  - Many snapshots lack tags (no retention/owner)
  - Duplicate snapshots created by multiple backup tools

## Root Cause Analysis (RCA)

1. **Backup retention misconfigured** (no pruning or overly long retention).
2. **Manual snapshot creation** without cleanup processes.
3. **Orphaned volumes** still have snapshots even after volume deletion.

## Resolution Steps

1. List your snapshots (can be large; filter by tags/time in real environments).

```bash
aws ec2 describe-snapshots --owner-ids self \
  --query "Snapshots[].{SnapshotId:SnapshotId,StartTime:StartTime,VolumeId:VolumeId,VolumeSize:VolumeSize,Tags:Tags}" \
  --output table
```

2. Identify old snapshots beyond retention (example: older than 90 days).

```bash
aws ec2 describe-snapshots --owner-ids self --output json | \
  jq -r '.Snapshots[] | select(.StartTime < (now - 90*24*3600 | todate)) | .SnapshotId'
```

3. Implement a managed retention policy:
   - Prefer AWS DLM (Data Lifecycle Manager) with tag-based policies.
   - Ensure only one tool “owns” snapshot lifecycle for a given resource set.

4. Delete snapshots that are out of policy (after validating they’re not required for compliance).

```bash
aws ec2 delete-snapshot --snapshot-id <snapshot-id>
```

5. Add guardrails:
   - Enforce snapshot tags at creation (owner, retention_days, app).
   - Add reporting: snapshots without tags, snapshots older than N days.

## Cost Impact (If applicable)

- Deleting aged snapshots reduces monthly storage spend.
- DLM policies reduce operational overhead and prevent cost creep from snapshot sprawl.

---


