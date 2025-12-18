import argparse
import json
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

APP_SERVICES = ["checkout-api", "payment-gw", "data-ingestor", "ml-serving"]
LOG_SERVICES = APP_SERVICES + ["platform-infra"]
COST_SERVICES = APP_SERVICES + ["shared-infra"]
TENANTS = ["tenant-alpha", "tenant-beta", "tenant-gamma"]

# Error codes intentionally match Markdown runbooks under knowledge_base/runbooks/
ERROR_CATALOG: Dict[str, Dict[str, Any]] = {
    # Database
    "ERR_DB_CON_001": {"service": "checkout-api", "category": "Reliability", "severity": "P1", "http_status": 503},
    "ERR_DB_CON_002": {"service": "checkout-api", "category": "Reliability", "severity": "P1", "http_status": 503},
    "ERR_DB_QRY_001": {"service": "checkout-api", "category": "Performance", "severity": "P1", "http_status": 500},
    "ERR_DB_QRY_002": {"service": "checkout-api", "category": "Performance", "severity": "P1", "http_status": 500},
    "ERR_DB_DLK_001": {"service": "payment-gw", "category": "Reliability", "severity": "P1", "http_status": 500},
    "ERR_DB_LOCK_001": {"service": "checkout-api", "category": "Reliability", "severity": "P1", "http_status": 503},
    # Kubernetes / Infra
    "ERR_K8S_OOM_001": {"service": "ml-serving", "category": "Reliability", "severity": "P1", "http_status": 503},
    "ERR_K8S_OOM_002": {"service": "data-ingestor", "category": "Reliability", "severity": "P1", "http_status": 500},
    "ERR_K8S_NODE_MEM_001": {"service": "platform-infra", "category": "Reliability", "severity": "P0", "http_status": 0},
    "ERR_K8S_NODE_CPU_001": {"service": "platform-infra", "category": "Performance", "severity": "P1", "http_status": 0},
    "ERR_K8S_DISK_001": {"service": "platform-infra", "category": "Reliability", "severity": "P1", "http_status": 0},
    "ERR_K8S_DISK_002": {"service": "platform-infra", "category": "Reliability", "severity": "P1", "http_status": 0},
    # Data/ML
    "ERR_FLINK_CKPT_001": {"service": "data-ingestor", "category": "Reliability", "severity": "P1", "http_status": 500},
    "ERR_SPARK_SKEW_001": {"service": "data-ingestor", "category": "Performance", "severity": "P1", "http_status": 500},
    "ERR_VECTOR_LAT_001": {"service": "ml-serving", "category": "Performance", "severity": "P1", "http_status": 504},
    # Cost (used for cost-incidents derived from cost_summaries.json)
    "ERR_COST_S3_VER_001": {"service": "shared-infra", "category": "Cost", "severity": "P2", "http_status": 0},
    "ERR_COST_S3_REQ_001": {"service": "shared-infra", "category": "Cost", "severity": "P2", "http_status": 0},
    "ERR_COST_EBS_001": {"service": "shared-infra", "category": "Cost", "severity": "P2", "http_status": 0},
    "ERR_COST_EBS_SNAP_001": {"service": "shared-infra", "category": "Cost", "severity": "P2", "http_status": 0},
    "ERR_COST_NAT_001": {"service": "shared-infra", "category": "Cost", "severity": "P1", "http_status": 0},
}

SERVICE_ERROR_CODES: Dict[str, List[str]] = {
    "checkout-api": ["ERR_DB_CON_001", "ERR_DB_CON_002", "ERR_DB_QRY_001", "ERR_DB_QRY_002", "ERR_DB_LOCK_001"],
    "payment-gw": ["ERR_DB_DLK_001", "ERR_DB_LOCK_001", "ERR_DB_CON_001"],
    "data-ingestor": ["ERR_FLINK_CKPT_001", "ERR_SPARK_SKEW_001", "ERR_K8S_OOM_002"],
    "ml-serving": ["ERR_VECTOR_LAT_001", "ERR_K8S_OOM_001"],
    "platform-infra": ["ERR_K8S_NODE_MEM_001", "ERR_K8S_NODE_CPU_001", "ERR_K8S_DISK_001", "ERR_K8S_DISK_002"],
}

REQUEST_PATHS: Dict[str, List[str]] = {
    "checkout-api": ["/api/checkout", "/api/cart", "/api/orders"],
    "payment-gw": ["/api/payments/charge", "/api/payments/refund"],
    "data-ingestor": ["/jobs/ingest", "/jobs/aggregate", "/jobs/compact"],
    "ml-serving": ["/v1/embed", "/v1/rerank", "/v1/retrieve"],
    "platform-infra": ["/cluster/health", "/cluster/autoscaler", "/cluster/kubelet"],
}


def _iso(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).isoformat()


def build_runbook_index(runbooks_dir: Path) -> Dict[str, str]:
    index: Dict[str, str] = {}
    if not runbooks_dir.exists():
        return index
    repo_root = Path(__file__).resolve().parent
    for p in sorted(runbooks_dir.glob("*.md")):
        code = p.name.split("-", 1)[0]
        if code in index:
            raise RuntimeError(f"Duplicate runbook error code detected: {code}")
        index[code] = str(p.relative_to(repo_root).as_posix())
    return index


def generate_incident_plan(
    *,
    rng,
    count: int,
    start_time: datetime,
    max_incidents: int,
) -> List[Dict[str, Any]]:
    # Choose a handful of incidents with non-overlapping windows across the log timeline.
    candidates = [
        "ERR_DB_CON_001",
        "ERR_DB_QRY_001",
        "ERR_DB_DLK_001",
        "ERR_K8S_OOM_001",
        "ERR_K8S_NODE_MEM_001",
        "ERR_K8S_DISK_002",
        "ERR_FLINK_CKPT_001",
        "ERR_SPARK_SKEW_001",
        "ERR_VECTOR_LAT_001",
    ]

    incidents: List[Dict[str, Any]] = []
    used: List[range] = []
    used_codes = set()

    def overlaps(r: range) -> bool:
        return any((r.start < u.stop and u.start < r.stop) for u in used)

    target = min(max_incidents, len(candidates))
    attempts = 0
    while len(incidents) < target and attempts < 500:
        attempts += 1
        code = rng.choice(candidates)
        if code in used_codes:
            continue

        duration_min = rng.randint(10, 35)
        start_idx = rng.randint(0, max(0, count - duration_min - 1))
        window = range(start_idx, start_idx + duration_min)
        if overlaps(window):
            continue
        used.append(window)
        used_codes.add(code)

        meta = ERROR_CATALOG[code]
        service = meta["service"]
        tenant = rng.choice(TENANTS)
        incidents.append(
            {
                "error_code": code,
                "service": service,
                "tenant_id": tenant,
                "start_idx": window.start,
                "end_idx": window.stop,
                "start_time": start_time + timedelta(minutes=window.start),
                "end_time": start_time + timedelta(minutes=window.stop - 1),
            }
        )

    # Sort chronologically to make downstream demos nicer
    incidents.sort(key=lambda x: x["start_idx"])
    return incidents


def generate_logs(*, rng, count: int, start_time: datetime, incident_plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    logs: List[Dict[str, Any]] = []

    # Baseline logs
    for i in range(count):
        ts = start_time + timedelta(minutes=i)
        service = rng.choice(APP_SERVICES)
        tenant = rng.choice(TENANTS)
        level = rng.choices(["INFO", "WARN", "ERROR"], weights=[0.9, 0.05, 0.05])[0]

        error_code: Optional[str] = None
        status_code = 200
        latency_ms = rng.randint(10, 500)
        message = f"Request processed for {tenant}"

        if level != "INFO":
            error_code = rng.choice(SERVICE_ERROR_CODES[service])
            status_code = int(ERROR_CATALOG[error_code]["http_status"])
            latency_ms = rng.randint(1500, 9000)
            message = f"Failure: {error_code}"

        logs.append(
            {
                "timestamp": _iso(ts),
            "trace_id": str(uuid.uuid4()),
            "tenant_id": tenant,
            "service": service,
                "level": level,
                "status_code": status_code,
                "latency_ms": latency_ms,
                "error_code": error_code,
                "request_path": rng.choice(REQUEST_PATHS[service]),
                "message": message,
                "metadata": {"env": "production", "region": "us-east-1"},
            }
        )

    # Inject incident windows
    for inc in incident_plan:
        code = inc["error_code"]
        service = inc["service"]
        tenant = inc["tenant_id"]
        http_status = int(ERROR_CATALOG[code]["http_status"])

        for i in range(inc["start_idx"], inc["end_idx"]):
            # Make most entries ERROR with high latency during the incident window
            level = rng.choices(["ERROR", "WARN", "INFO"], weights=[0.75, 0.15, 0.10])[0]
            logs[i]["service"] = service
            logs[i]["tenant_id"] = tenant
            logs[i]["request_path"] = rng.choice(REQUEST_PATHS.get(service, ["/"]))

            if level == "INFO":
                logs[i]["level"] = "INFO"
                logs[i]["status_code"] = 200
                logs[i]["latency_ms"] = rng.randint(50, 800)
                logs[i]["error_code"] = None
                logs[i]["message"] = f"Request processed for {tenant}"
            else:
                logs[i]["level"] = level
                logs[i]["status_code"] = http_status
                logs[i]["latency_ms"] = rng.randint(2500, 12000)
                logs[i]["error_code"] = code
                logs[i]["message"] = f"Failure: {code}"

    return logs


def percentile(values: List[int], p: float) -> int:
    if not values:
        return 0
    s = sorted(values)
    k = int(round((len(s) - 1) * p))
    return s[max(0, min(k, len(s) - 1))]


def generate_incidents_from_plan(
    *,
    logs: List[Dict[str, Any]],
    plan: List[Dict[str, Any]],
    runbook_index: Dict[str, str],
) -> List[Dict[str, Any]]:
    incidents: List[Dict[str, Any]] = []

    for inc in plan:
        window_logs = logs[inc["start_idx"] : inc["end_idx"]]
        error_logs = [l for l in window_logs if l.get("level") in ("ERROR", "WARN")]
        status_counts: Dict[str, int] = {}
        for l in error_logs:
            sc = str(l.get("status_code", 0))
            status_counts[sc] = status_counts.get(sc, 0) + 1

        latencies = [int(l.get("latency_ms", 0)) for l in window_logs]
        title = f"{inc['service']} incident: {inc['error_code']}"
        code = inc["error_code"]
        meta = ERROR_CATALOG.get(code, {})

        incidents.append(
            {
                "incident_id": f"INC-{uuid.uuid4()}",
                "source": "logs",
                "title": title,
                "service": inc["service"],
                "tenant_id": inc["tenant_id"],
                "category": meta.get("category", "Reliability"),
                "severity": meta.get("severity", "P2"),
                "error_codes": [code],
                "start_time": _iso(inc["start_time"]),
                "end_time": _iso(inc["end_time"]),
                "status": "resolved",
                "symptoms": {
                    "log_pattern": f"Failure: {code}",
                    "error_rate_pct": round((len(error_logs) / max(1, len(window_logs))) * 100.0, 2),
                    "status_code_counts": status_counts,
                    "p95_latency_ms": percentile(latencies, 0.95),
                    "sample_trace_ids": [l["trace_id"] for l in error_logs[:5]],
                },
                "runbook_refs": [runbook_index.get(code)] if runbook_index.get(code) else [],
            }
        )

    return incidents


def generate_cost_metrics(*, rng) -> List[Dict[str, Any]]:
    metrics: List[Dict[str, Any]] = []

    # App spend (per-tenant / per-service)
    for tenant in TENANTS:
        for service in APP_SERVICES:
            metrics.append(
                {
                "tenant_id": tenant,
                "service": service,
                    "daily_spend": round(rng.uniform(50.0, 500.0), 2),
                    "currency": "USD",
                    "resource_type": "EC2/EKS",
                }
            )

    # Shared infra line items to support FinOps runbooks
    shared_types = ["NAT Gateway", "S3", "S3 Requests", "EBS", "EBS Snapshot"]
    for tenant in TENANTS:
        for rt in shared_types:
            metrics.append(
                {
                    "tenant_id": tenant,
                    "service": "shared-infra",
                    "daily_spend": round(rng.uniform(5.0, 200.0), 2),
                "currency": "USD",
                    "resource_type": rt,
                }
            )

    # Inject a couple of anomalies so there is always something to diagnose
    noisy_tenant = rng.choice(TENANTS)
    for m in metrics:
        if m["tenant_id"] == noisy_tenant and m["service"] == "shared-infra" and m["resource_type"] == "NAT Gateway":
            m["daily_spend"] = round(rng.uniform(250.0, 900.0), 2)
        if m["tenant_id"] == noisy_tenant and m["service"] == "shared-infra" and m["resource_type"] == "S3":
            m["daily_spend"] = round(rng.uniform(200.0, 700.0), 2)

    return metrics


def generate_cost_incidents(*, cost_metrics: List[Dict[str, Any]], runbook_index: Dict[str, str]) -> List[Dict[str, Any]]:
    incidents: List[Dict[str, Any]] = []

    # Map resource_type -> cost error code
    type_to_code = {
        "NAT Gateway": "ERR_COST_NAT_001",
        "S3": "ERR_COST_S3_VER_001",
        "S3 Requests": "ERR_COST_S3_REQ_001",
        "EBS": "ERR_COST_EBS_001",
        "EBS Snapshot": "ERR_COST_EBS_SNAP_001",
    }

    # Simple anomaly rule: daily_spend exceeds a threshold by resource type.
    thresholds = {
        "NAT Gateway": 250.0,
        "S3": 200.0,
        "S3 Requests": 120.0,
        "EBS": 120.0,
        "EBS Snapshot": 80.0,
    }

    now = datetime.now(timezone.utc)
    for m in cost_metrics:
        rt = m["resource_type"]
        if m["service"] != "shared-infra":
            continue
        if rt not in thresholds:
            continue
        if float(m["daily_spend"]) < thresholds[rt]:
            continue

        code = type_to_code[rt]
        meta = ERROR_CATALOG.get(code, {})
        monthly_est = round(float(m["daily_spend"]) * 30.0, 2)

        incidents.append(
            {
                "incident_id": f"COST-{uuid.uuid4()}",
                "source": "cost",
                "title": f"{rt} cost anomaly for {m['tenant_id']}",
                "service": m["service"],
                "tenant_id": m["tenant_id"],
                "category": meta.get("category", "Cost"),
                "severity": meta.get("severity", "P2"),
                "error_codes": [code],
                "start_time": _iso(now - timedelta(hours=6)),
                "end_time": _iso(now),
                "status": "open",
                "symptoms": {
                    "resource_type": rt,
                    "daily_spend_usd": m["daily_spend"],
                    "estimated_monthly_usd": monthly_est,
                },
                "runbook_refs": [runbook_index.get(code)] if runbook_index.get(code) else [],
            }
        )

    return incidents


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic logs, incidents, and cost summaries for OpsPilot demos.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for deterministic output.")
    parser.add_argument("--count", type=int, default=500, help="Number of log entries to generate (1 per minute).")
    parser.add_argument("--incidents", type=int, default=8, help="Max number of injected log-driven incidents.")
    parser.add_argument("--out-dir", type=str, default=".", help="Output directory for JSON files.")
    args = parser.parse_args()

    rng = __import__("random").Random(args.seed)
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    start_time = datetime.now(timezone.utc) - timedelta(hours=24)

    runbooks_dir = Path(__file__).resolve().parent / "knowledge_base" / "runbooks"
    runbook_index = build_runbook_index(runbooks_dir)

    plan = generate_incident_plan(rng=rng, count=args.count, start_time=start_time, max_incidents=args.incidents)
    logs = generate_logs(rng=rng, count=args.count, start_time=start_time, incident_plan=plan)
    cost_metrics = generate_cost_metrics(rng=rng)

    incidents = []
    incidents.extend(generate_incidents_from_plan(logs=logs, plan=plan, runbook_index=runbook_index))
    incidents.extend(generate_cost_incidents(cost_metrics=cost_metrics, runbook_index=runbook_index))

    (out_dir / "synthetic_logs.json").write_text(json.dumps(logs, indent=2), encoding="utf-8")
    (out_dir / "cost_summaries.json").write_text(json.dumps(cost_metrics, indent=2), encoding="utf-8")
    (out_dir / "synthetic_incidents.json").write_text(json.dumps(incidents, indent=2), encoding="utf-8")

    print("Generated synthetic_logs.json, cost_summaries.json, and synthetic_incidents.json")


if __name__ == "__main__":
    main()