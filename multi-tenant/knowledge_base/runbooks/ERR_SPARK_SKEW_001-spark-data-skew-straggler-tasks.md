# Title: Spark Data Skew (Straggler Tasks / Shuffle Hot Partitions)

## Metadata

- Service: data-ingestor
- Category: Performance
- Severity: P1

## Symptoms

- Error Codes: `ERR_SPARK_SKEW_001`
- Job symptoms:
  - One or a few tasks in a stage run **10x longer** than others
  - Stage progress stalls at ~90–99% for extended periods
  - Executors show high shuffle read/spill; `GC` time increases
- Spark UI indicators:
  - Skewed partition sizes (one partition much larger)
  - High “Shuffle Read” / “Spill (Memory/Disk)” on a subset of tasks
- Logs:
  - `ERR_SPARK_SKEW_001 skew detected`
  - `FetchFailedException` (secondary symptom under heavy skew)

## Root Cause Analysis (RCA)

1. **Skewed keys** (e.g., one tenant_id dominates) create hot partitions during joins/aggregations.
2. **Suboptimal shuffle partitioning**: too few partitions or bad partitioning columns.
3. **Small files and wide scans** inflate shuffle volume and increase spill/GC.

## Resolution Steps

1. Confirm skew in Spark UI:
   - Identify the stage and operation (join, groupBy, window).

2. Quick mitigations (SQL/DataFrame):
   - Enable Adaptive Query Execution (AQE) and skew join handling.

```bash
spark-submit \
  --conf spark.sql.adaptive.enabled=true \
  --conf spark.sql.adaptive.skewJoin.enabled=true \
  --conf spark.sql.adaptive.skewJoin.skewedPartitionFactor=5 \
  --conf spark.sql.shuffle.partitions=800 \
  ...
```

3. If skew is on join keys:
   - Use broadcast join when one side is small enough.
   - Salt the skewed key (add a random prefix) to distribute hot keys.

```sql
-- Example: salting (conceptual)
SELECT /*+ REPARTITION(800, salted_key) */
       *
FROM (
  SELECT concat(tenant_id, '-', cast(rand()*10 as int)) AS salted_key, *
  FROM big_table
) t
JOIN small_table s
  ON t.tenant_id = s.tenant_id;
```

4. Tune partitioning:
   - Increase `spark.sql.shuffle.partitions` for large shuffles.
   - Repartition on the correct key before heavy aggregations.
   - Avoid wide transformations without pruning (filter early).

5. Reduce shuffle volume:
   - Compact small files upstream.
   - Use partition pruning (e.g., date partition filters).
   - Persist intermediate datasets only when beneficial and with correct storage level.

6. Verification:
   - Stage task durations become more uniform
   - Spill and GC times decrease
   - End-to-end job duration returns to baseline

## Cost Impact (If applicable)

- Skew increases runtime and executor count (more vCPU-hours), directly raising compute cost.
- Fixing skew often yields large savings by reducing job time and required cluster size.

---


