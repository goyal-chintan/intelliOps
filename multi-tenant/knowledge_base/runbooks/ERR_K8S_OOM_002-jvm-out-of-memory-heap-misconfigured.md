# Title: JVM OutOfMemoryError (Heap Misconfigured for Container Limits)

## Metadata

- Service: data-ingestor
- Category: Reliability
- Severity: P1

## Symptoms

- Error Codes: `ERR_K8S_OOM_002`
- JVM logs (common patterns):
  - `java.lang.OutOfMemoryError: Java heap space`
  - `java.lang.OutOfMemoryError: GC overhead limit exceeded`
  - `OutOfMemoryError: Direct buffer memory` (off-heap)
- Kubernetes:
  - Pod restarts and sometimes `OOMKilled` (Exit Code 137)
- Metrics:
  - `jvm_memory_used_bytes{area="heap"} / jvm_memory_max_bytes{area="heap"} > 0.95`
  - `jvm_gc_pause_seconds_sum` increases sharply

## Root Cause Analysis (RCA)

1. **Heap too large relative to container limit**: `-Xmx` set close to limit leaves no room for off-heap, threads, metaspace, native libs → OOMKilled.
2. **Off-heap growth**: RocksDB, Netty direct buffers, compression, JNI allocations grow outside the Java heap.
3. **True memory leak** in app code (caches, maps, per-tenant state) or unbounded batch buffering.

## Resolution Steps

1. Confirm JVM OOM in logs.

```bash
kubectl -n prod logs deploy/data-ingestor --since=30m | egrep -n "ERR_K8S_OOM_002|OutOfMemoryError|GC overhead|Direct buffer"
```

2. Check container memory limits and JVM flags.

```bash
kubectl -n prod get deploy data-ingestor -o jsonpath='{.spec.template.spec.containers[*].resources}' ; echo
kubectl -n prod describe deploy data-ingestor | egrep -n "JAVA_TOOL_OPTIONS|-Xmx|-Xms|MaxRAMPercentage"
```

3. Immediate mitigation:
   - Reduce batch sizes / buffer sizes (streaming jobs often have a “max in-flight” setting).
   - If safe, increase memory limit temporarily and roll out.

```bash
kubectl -n prod edit deploy/data-ingestor
kubectl -n prod rollout status deploy/data-ingestor --timeout=5m
```

4. Fix heap sizing for containers (recommended):
   - Use `-XX:MaxRAMPercentage` instead of hard-coding `-Xmx`.
   - Keep heap at **~60–75%** of container limit to leave headroom for off-heap/native.

```bash
# Example env (adjust values)
JAVA_TOOL_OPTIONS="-XX:MaxRAMPercentage=70 -XX:InitialRAMPercentage=50 -XX:+ExitOnOutOfMemoryError"
```

5. Collect artifacts for RCA (if permitted):
   - Enable heap dump on OOM to a writable volume (PVC) and limit retention.

```bash
JAVA_TOOL_OPTIONS="$JAVA_TOOL_OPTIONS -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/var/heapdumps"
```

6. Verification:
   - GC pause time normalizes
   - Pod restarts stop
   - Heap usage stabilizes under load with headroom

## Cost Impact (If applicable)

- Increasing memory limits increases node cost; heap dumps can increase persistent storage cost.
- Right-sizing heap/off-heap prevents over-provisioning and improves bin packing efficiency.

---


