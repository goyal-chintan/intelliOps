# Title: S3 Versioning Storage Bloat (Noncurrent Versions)

## Metadata

- Service: shared-infra
- Category: Cost
- Severity: P2

## Symptoms

- Error Codes: `ERR_COST_S3_VER_001`
- Cost signals:
  - S3 storage cost increases by **> 20% month-over-month**
  - `NonCurrentVersion` storage becomes a significant portion of S3 spend
- Storage signals:
  - `BucketSizeBytes` increases steadily while `NumberOfObjects` remains flat
  - S3 Inventory shows many noncurrent versions per key
- Common operators’ findings:
  - Buckets have versioning enabled but no lifecycle policy for noncurrent versions

## Root Cause Analysis (RCA)

1. **Versioning enabled without lifecycle management** → overwritten objects accumulate noncurrent versions indefinitely.
2. **High churn workloads** (checkpointing, compactions, ML artifacts) overwrite large objects frequently.
3. **Retention requirements misinterpreted**: teams keep versions “just in case” but never need deep history.

## Resolution Steps

1. Identify top-cost buckets (use Cost Explorer / CUR). Then verify versioning.

```bash
aws s3api get-bucket-versioning --bucket <bucket-name>
```

2. Estimate version bloat (sample; large buckets should use S3 Inventory).

```bash
aws s3api list-object-versions --bucket <bucket-name> --prefix <prefix> --max-items 200
```

3. Check lifecycle rules.

```bash
aws s3api get-bucket-lifecycle-configuration --bucket <bucket-name>
```

4. Add lifecycle rules to expire noncurrent versions (example: keep 7 days of history, retain 3 newer noncurrent versions).

```bash
cat > lifecycle.json <<'JSON'
{
  "Rules": [
    {
      "ID": "expire-noncurrent-versions",
      "Status": "Enabled",
      "Filter": {},
      "NoncurrentVersionExpiration": { "NoncurrentDays": 7 },
      "NoncurrentVersionTransitions": [
        { "NoncurrentDays": 1, "StorageClass": "INTELLIGENT_TIERING" }
      ],
      "AbortIncompleteMultipartUpload": { "DaysAfterInitiation": 7 }
    }
  ]
}
JSON

aws s3api put-bucket-lifecycle-configuration --bucket <bucket-name> --lifecycle-configuration file://lifecycle.json
```

5. Validate and monitor:
   - Confirm lifecycle applies to the correct prefixes.
   - Re-check S3 Storage Lens / Inventory after 24–72 hours.

## Cost Impact (If applicable)

- Expiring noncurrent versions reduces S3 storage charges and can materially cut monthly spend for high-churn buckets.
- Transitioning old versions to cheaper classes may add small per-request costs but usually wins for large datasets.

---


