# Title: Savings Plans / Reserved Instances Coverage Low

## Metadata

- Service: shared-infra
- Category: Cost
- Severity: P2

## Symptoms

- Error Codes: `ERR_COST_RI_001`
- Cost signals:
  - On-demand compute spend high; savings plan/RI coverage < **60%**
  - Spend stable and predictable (good candidate for commitments)
- Operational signals:
  - Long-running EKS/EC2 usage with steady baseline

## Root Cause Analysis (RCA)

1. **No commitments purchased** (or commitments expired) while steady usage continues.
2. **Mismatched commitments** (wrong region/instance family) reduce coverage.
3. **Highly variable usage** makes commitments risky without a stable baseline measurement.

## Resolution Steps

1. Establish baseline compute usage (look at last 30–90 days).
   - Identify steady-state vCPU-hours or instance-hours.

2. Evaluate Savings Plans vs RIs:
   - Savings Plans are generally more flexible across instance families.

3. Implement a conservative commitment:
   - Cover the baseline only (e.g., 50–70% of steady usage).
   - Prefer 1-year term for flexibility in early stages.

4. Add guardrails:
   - Monthly review of coverage and utilization.
   - Tag workloads and map spend to owners to avoid unused commitments.

5. Verification:
   - Coverage increases; on-demand spend decreases
   - Utilization remains high (> 90%) after 1–2 billing cycles

## Cost Impact (If applicable)

- Increasing savings plan/RI coverage can reduce compute costs **10–40%** depending on terms.
- Over-committing can waste money if usage drops; start conservative.

---


