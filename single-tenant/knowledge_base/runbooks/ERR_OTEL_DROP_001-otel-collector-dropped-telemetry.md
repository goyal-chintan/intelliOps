# Title: OpenTelemetry Collector Dropping Telemetry (Backpressure)

## Metadata

- Service: platform-infra
- Category: Reliability
- Severity: P1

## Symptoms

- Error Codes: `ERR_OTEL_DROP_001`
- Signals:
  - Sudden drop in traces/logs/metrics volume (observability “goes dark”)
  - Increased sampling or missing spans during incidents
- Logs (common patterns):
  - `ERR_OTEL_DROP_001 dropping data`
  - `exporter queue is full`
  - `retrying failed export` / `context deadline exceeded`
- Metrics:
  - `otelcol_exporter_send_failed_*` increases
  - `otelcol_receiver_accepted_*` stays high but `otelcol_exporter_sent_*` drops

## Root Cause Analysis (RCA)

1. **Exporter bottleneck**: backend (Tempo/Jaeger/OpenSearch/OTLP endpoint) is slow or unavailable.
2. **Collector under-provisioned**: CPU/memory too low for current telemetry volume (burst during incidents).
3. **Misconfiguration**: queue sizes too small, batch sizes too large, or retry settings amplify load.

## Resolution Steps

1. Confirm drops in collector logs.

```bash
kubectl -n observability logs deploy/otel-collector --since=30m | egrep -n "ERR_OTEL_DROP_001|dropp|queue is full|send failed|export.*failed|deadline exceeded"
```

2. Check collector resource usage.

```bash
kubectl -n observability get pods -l app=otel-collector -o wide
kubectl -n observability top pod -l app=otel-collector
```

3. Check backend health (example: OpenSearch/Tempo).

```bash
kubectl -n observability get pods -l app=tempo -o wide
kubectl -n observability get pods -l app=opensearch -o wide
```

4. Immediate mitigation:
   - Scale the collector and/or increase CPU/memory.

```bash
kubectl -n observability scale deploy/otel-collector --replicas=+2
kubectl -n observability rollout status deploy/otel-collector --timeout=5m
```

   - Temporarily reduce telemetry volume:
     - lower sampling rate
     - disable debug logs
     - drop high-cardinality attributes

5. Tune batching/queues (example knobs; apply via ConfigMap/Helm):
   - Increase exporter queue capacity
   - Reduce batch size and flush more frequently

6. Verification:
   - Drop metrics stop increasing
   - Backend receives telemetry; dashboards/traces repopulate

## Cost Impact (If applicable)

- Increased telemetry volume increases backend ingestion/storage costs; reducing high-cardinality signals often saves money and improves reliability.

---


