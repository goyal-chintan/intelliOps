# Title: Vector DB High Latency (OpenSearch / Qdrant / Weaviate)

## Metadata

- Service: ml-serving
- Category: Performance
- Severity: P1

## Symptoms

- Error Codes: `ERR_VECTOR_LAT_001`
- Query symptoms:
  - Vector search P95 latency > **200ms for 10m** (or > your SLO)
  - Increased timeouts from callers (e.g., `HTTP 504` / `context deadline exceeded`)
- Cluster signals:
  - CPU > **80%** sustained, memory pressure, or disk IO saturation
  - OpenSearch: search threadpool queue grows; merges increase during heavy ingestion
  - Qdrant/Weaviate: high request latency, increased 5xx, growing internal queues
- Logs (common patterns):
  - `ERR_VECTOR_LAT_001 vector query timeout`
  - OpenSearch: `search_phase_execution_exception`
  - Qdrant: `timeout while waiting for search result` (varies by version)

## Root Cause Analysis (RCA)

1. **Resource saturation**: insufficient CPU/RAM for HNSW/ANN searches and cache; ingestion competes with queries.
2. **Index tuning mismatch**: query parameters (topK, efSearch) too aggressive; shard/segment layout inefficient.
3. **Operational churn**: merges/compactions, shard relocation, or cold caches after restart increase latency.

## Resolution Steps

1. Identify whether the bottleneck is compute, memory, disk, or queueing.

```bash
kubectl -n prod top pod -l app=vector-db
kubectl -n prod top node
kubectl -n prod get pods -l app=vector-db -o wide
```

2. Check application-level symptoms from callers.

```bash
kubectl -n prod logs deploy/ml-serving --since=30m | egrep -n "ERR_VECTOR_LAT_001|timeout|deadline exceeded|vector"
```

3. OpenSearch checks (if applicable):

```bash
kubectl -n prod port-forward svc/opensearch 9200:9200
curl -s http://localhost:9200/_cluster/health?pretty
curl -s http://localhost:9200/_cat/thread_pool/search?v
curl -s http://localhost:9200/_nodes/stats/thread_pool,jvm,fs?pretty | head -n 80
```

4. Qdrant checks (if applicable):

```bash
kubectl -n prod port-forward svc/qdrant 6333:6333
curl -s http://localhost:6333/metrics | head -n 80
curl -s http://localhost:6333/collections | head -n 80
```

5. Immediate mitigations:
   - Reduce query complexity (lower `topK`, lower `efSearch`, cap concurrent queries).
   - Separate ingestion and query workloads (pause bulk ingest during incident).
   - Scale out/scale up vector DB (more replicas / bigger nodes) if saturation is confirmed.

6. Longer-term fixes:
   - Right-size shard/partition strategy (avoid too many small shards).
   - Tune ANN parameters and refresh/merge settings based on SLO.
   - Add caching/warming for hot queries or embeddings.
   - Implement backpressure at callers to avoid retry storms.

7. Verification:
   - P95 search latency returns to baseline
   - Queue depths return near zero
   - Caller timeouts decrease

## Cost Impact (If applicable)

- Scaling vector DB clusters is often expensive (CPU/RAM heavy). Parameter tuning can reduce infra size needed for the same SLO.
- Separating ingest/query tiers can increase cost but improves predictability; evaluate against SLO and traffic patterns.

---


