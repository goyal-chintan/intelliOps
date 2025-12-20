# Title: TLS Certificate Expired / Near Expiration

## Metadata

- Service: platform-infra
- Category: Reliability
- Severity: P0

## Symptoms

- Error Codes: `ERR_CERT_001`
- User impact:
  - Clients see TLS errors; requests fail before reaching the app
- Logs (common patterns):
  - `ERR_CERT_001 certificate has expired`
  - `x509: certificate has expired or is not yet valid`
  - `SSL: CERTIFICATE_VERIFY_FAILED`
- Metrics:
  - Spike in connection failures and handshake errors

## Root Cause Analysis (RCA)

1. **Cert rotation failed** (cert-manager misconfigured, ACME challenge failures, IAM/DNS permissions missing).
2. **Manual certificate management** with no renewal automation/alerting.
3. **Clock skew** on nodes/clients triggers “not yet valid” errors.

## Resolution Steps

1. Identify the affected endpoint (Ingress/Load Balancer) and certificate secret.

```bash
kubectl -n prod get ingress
kubectl -n prod describe ingress <ingress-name> | egrep -n "tls|secretName|host"
```

2. Inspect certificate resources (cert-manager) if used.

```bash
kubectl -n prod get certificate,certificaterequest,order,challenge
kubectl -n prod describe certificate <cert-name>
kubectl -n prod logs deploy/cert-manager --since=60m | tail -n 200
```

3. Validate the cert in the Kubernetes secret (dates, CN/SAN).

```bash
kubectl -n prod get secret <tls-secret> -o jsonpath='{.data.tls\\.crt}' | base64 -d | openssl x509 -noout -dates -subject -issuer
```

4. Immediate mitigation:
   - Re-issue/renew certificate (cert-manager) or deploy a new cert.
   - If using a managed LB cert, rotate via the cloud provider.

5. Add guardrails:
   - Alert on expiration < **14 days**
   - Ensure cert-manager has permissions for DNS-01/HTTP-01 challenges

6. Verification:
   - TLS handshake succeeds (curl/openssl)
   - Client error rates drop to baseline

## Cost Impact (If applicable)

- Minimal direct cost impact, but outages can trigger failovers and wasted compute from retries.

---


