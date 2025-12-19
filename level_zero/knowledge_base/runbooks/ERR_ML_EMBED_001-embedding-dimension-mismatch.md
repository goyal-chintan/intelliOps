# Title: Embedding Dimension Mismatch (Vector Search Errors)

## Metadata

- Service: ml-serving
- Category: Reliability
- Severity: P1

## Symptoms

- Error Codes: `ERR_ML_EMBED_001`
- Logs (common patterns):
  - `ERR_ML_EMBED_001 embedding dimension mismatch`
  - `expected dim=1536 got dim=768`
  - Vector DB errors: `invalid vector size` / `dimension mismatch` (varies by engine)
- User impact:
  - Search/retrieval endpoints fail (5xx) or return empty results

## Root Cause Analysis (RCA)

1. **Model changed** (new embedding model) but index/collection expects old dimension.
2. **Mixed traffic** during rollout sends vectors from different model versions concurrently.
3. **Incorrect preprocessing** truncates/pads embeddings or returns wrong output vector.

## Resolution Steps

1. Confirm mismatch errors and identify expected/actual dimensions.

```bash
kubectl -n prod logs deploy/ml-serving --since=60m | egrep -n "ERR_ML_EMBED_001|dimension mismatch|expected dim|invalid vector size"
```

2. Check vector DB collection schema (examples differ by engine):
   - OpenSearch k-NN: inspect mapping for the vector field dimension.
   - Qdrant: collection config shows vector size.

```bash
# Example (Qdrant)
kubectl -n prod port-forward svc/qdrant 6333:6333
curl -s http://localhost:6333/collections/<collection-name> | head -n 120
```

3. Check the embedding model version deployed and the output dimension.

```bash
kubectl -n prod describe deploy ml-serving | egrep -n "MODEL|EMBEDDING|VERSION"
```

4. Immediate mitigation:
   - Roll back the embedding model to match the current index schema.

```bash
kubectl -n prod rollout undo deploy/ml-serving
kubectl -n prod rollout status deploy/ml-serving --timeout=5m
```

5. Proper fix:
   - Create a new collection/index with the new dimension.
   - Dual-write / dual-query during migration (if needed).
   - Re-embed and backfill documents, then cut over.

6. Verification:
   - Errors stop
   - Retrieval accuracy/latency return to baseline

## Cost Impact (If applicable)

- Re-embedding/backfilling can be compute heavy; running dual indexes temporarily increases storage cost.
- A clean migration plan avoids prolonged dual-running costs and incidents.

---


