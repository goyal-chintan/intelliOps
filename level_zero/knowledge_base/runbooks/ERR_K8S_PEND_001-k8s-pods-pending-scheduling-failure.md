# Title: Kubernetes Pods Pending (Scheduling Failure)

## Metadata

- Service: platform-infra
- Category: Reliability
- Severity: P1

## Symptoms

- Error Codes: `ERR_K8S_PEND_001`
- Kubernetes:
  - Pods stuck in `Pending` for > **5 minutes**
  - Events show `FailedScheduling`
- Event patterns:
  - `0/.. nodes are available: Insufficient cpu/memory/ephemeral-storage`
  - `node(s) had taint ... that the pod didn't tolerate`
  - `pod has unbound immediate PersistentVolumeClaims`

## Root Cause Analysis (RCA)

1. **Cluster capacity exhausted** (no nodes have enough allocatable CPU/memory/ephemeral-storage).
2. **Taints/affinity/constraints** prevent scheduling (node selectors too strict, missing tolerations).
3. **Storage provisioning issues** (PVC pending, CSI driver errors).

## Resolution Steps

1. Inspect pending pods and scheduling events.

```bash
kubectl -n prod get pods --field-selector=status.phase=Pending
kubectl -n prod describe pod <pod-name> | egrep -n "FailedScheduling|Insufficient|taint|tolerat|unbound immediate PersistentVolumeClaims"
```

2. Check node capacity and pressure.

```bash
kubectl get nodes -o wide
kubectl describe node <node-name> | egrep -n "Allocatable|Capacity|Non-terminated Pods|MemoryPressure|DiskPressure"
kubectl -n prod top node
```

3. Immediate mitigation:
   - Scale the node group / cluster autoscaler.
   - Reduce resource requests temporarily (if safe).
   - Relax affinity or add tolerations where appropriate.

4. If PVC is blocking:
   - Describe PVC and StorageClass.

```bash
kubectl -n prod get pvc
kubectl -n prod describe pvc <pvc-name>
kubectl get storageclass
```

5. Verification:
   - Pods schedule to nodes and become `Running`
   - Cluster headroom returns (allocatable not saturated)

## Cost Impact (If applicable)

- Scaling nodes increases compute cost; right-sizing requests and cleaning up unused workloads often reduces the steady-state cluster size.

---


