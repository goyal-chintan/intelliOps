# Title: Model Drift Detected (Quality Degradation)

## Metadata

- Service: ml-serving
- Category: Performance
- Severity: P2

## Symptoms

- Error Codes: `ERR_ML_DRIFT_001`
- Quality signals (examples; tune per model):
  - CTR / conversion drops by **> 5%** week-over-week for the same traffic mix
  - Prediction distribution shifts (mean/variance) beyond thresholds
  - Feature missing rate increases (nulls/zeros) for key features
- Logs (common patterns):
  - `ERR_ML_DRIFT_001 drift detected`
  - `feature_missing_rate` warnings

## Root Cause Analysis (RCA)

1. **Data pipeline change** (schema change, feature bug, upstream missing data) changes feature distribution.
2. **Concept drift**: real-world behavior changes (seasonality, new tenant/product) making the model stale.
3. **Training/serving skew**: different preprocessing or vocab/normalization between training and online serving.

## Resolution Steps

1. Confirm drift alert and identify which features or outputs shifted.
   - Compare today’s feature stats vs training baseline.

2. Validate feature pipeline health:
   - Check missing rates and schema version.

```bash
kubectl -n prod logs deploy/data-ingestor --since=6h | egrep -n "ERR_ML_DRIFT_001|schema|feature|missing|null"
```

3. Validate serving preprocessing matches training:
   - Confirm feature normalization/version in model artifact metadata.

4. Mitigate:
   - Roll back to last known-good model if drift is severe.
   - If drift is expected (seasonality), adjust alert thresholds and retrain cadence.

```bash
kubectl -n prod rollout history deploy/ml-serving
kubectl -n prod rollout undo deploy/ml-serving
```

5. Fix root cause:
   - Repair feature extraction bug / schema mapping.
   - Retrain model with recent data and update validation checks.

6. Verification:
   - Drift metrics return toward baseline
   - Business KPIs stabilize

## Cost Impact (If applicable)

- Frequent retraining increases compute cost; catching drift early reduces wasted spend on degraded recommendations and prevents costly incidents.

---


