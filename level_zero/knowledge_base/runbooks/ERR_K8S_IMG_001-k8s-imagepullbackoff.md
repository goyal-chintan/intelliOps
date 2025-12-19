# Title: Kubernetes ImagePullBackOff (Cannot Pull Image)

## Metadata

- Service: platform-infra
- Category: Reliability
- Severity: P1

## Symptoms

- Error Codes: `ERR_K8S_IMG_001`
- Kubernetes:
  - Pod status `ImagePullBackOff` / `ErrImagePull`
- Events/logs (common patterns):
  - `Failed to pull image`
  - `pull access denied`
  - `no basic auth credentials`
  - `manifest unknown` / `not found`
  - `ERR_K8S_IMG_001 image pull failed`

## Root Cause Analysis (RCA)

1. **Bad image reference**: wrong tag, image deleted, or wrong registry URL.
2. **Registry auth**: missing/expired imagePullSecret or broken IRSA/ECR auth.
3. **Network/DNS issues**: cluster cannot reach the registry or resolve endpoints.

## Resolution Steps

1. Inspect pod events and image name.

```bash
kubectl -n prod describe pod <pod-name> | egrep -n "ImagePullBackOff|ErrImagePull|Failed to pull image|pull access denied|manifest unknown|no basic auth"
kubectl -n prod get pod <pod-name> -o jsonpath='{.spec.containers[*].image}'; echo
```

2. Validate registry credentials and imagePullSecrets.

```bash
kubectl -n prod get sa <service-account> -o yaml | egrep -n "imagePullSecrets"
kubectl -n prod get secret | egrep -n "dockercfg|dockerconfigjson|pull"
```

3. If using ECR:
   - Confirm node role/IRSA permissions and ECR endpoints.
   - Confirm the image tag exists.

```bash
aws ecr describe-images --repository-name <repo> --image-ids imageTag=<tag>
```

4. Quick mitigation:
   - Roll back to a known-good image tag.

```bash
kubectl -n prod rollout undo deploy/<workload>
kubectl -n prod rollout status deploy/<workload> --timeout=5m
```

5. Verification:
   - Pods transition to `Running` and become `Ready`
   - Events stop reporting pull failures

## Cost Impact (If applicable)

- Failed pulls can trigger repeated retries and node churn, increasing operational overhead; fixing image pipelines reduces wasted compute and deployment time.

---


