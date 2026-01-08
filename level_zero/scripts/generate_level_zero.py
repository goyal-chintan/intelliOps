import argparse
import csv
import gzip
import json
import math
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


TENANT_ID = "tenant-demo"
ENV = "production"
REGION = "us-east-1"

APP_SERVICES = ["checkout-api", "payment-gw", "data-ingestor", "ml-serving"]
ALL_SERVICES = APP_SERVICES + ["platform-infra"]

REQUEST_PATHS: Dict[str, List[str]] = {
    "checkout-api": ["/api/checkout", "/api/cart", "/api/orders", "/api/search"],
    "payment-gw": ["/api/payments/charge", "/api/payments/refund", "/api/payments/auth"],
    "data-ingestor": ["/jobs/ingest", "/jobs/aggregate", "/jobs/compact", "/jobs/backfill"],
    "ml-serving": ["/v1/embed", "/v1/rerank", "/v1/retrieve"],
    "platform-infra": ["/cluster/health", "/cluster/kubelet", "/cluster/coredns"],
}


# Layer 0 uses single-tenant, but multi-service. These error codes must exist as runbooks
# under level_zero/knowledge_base/runbooks/<CODE>-*.md
ERROR_CATALOG: Dict[str, Dict[str, Any]] = {
    # App / HTTP
    "ERR_HTTP_5XX_001": {"service": "checkout-api", "category": "Reliability", "severity": "P1", "status_code": 503},
    "ERR_HTTP_504_001": {"service": "checkout-api", "category": "Performance", "severity": "P1", "status_code": 504},
    "ERR_DEP_TIMEOUT_001": {"service": "payment-gw", "category": "Reliability", "severity": "P1", "status_code": 504},
    "ERR_RATE_LIMIT_001": {"service": "payment-gw", "category": "Reliability", "severity": "P1", "status_code": 429},
    "ERR_THREADPOOL_001": {"service": "payment-gw", "category": "Performance", "severity": "P1", "status_code": 503},
    # Database
    "ERR_DB_CON_001": {"service": "checkout-api", "category": "Reliability", "severity": "P1", "status_code": 503},
    "ERR_DB_QRY_001": {"service": "checkout-api", "category": "Performance", "severity": "P1", "status_code": 500},
    "ERR_DB_DLK_001": {"service": "payment-gw", "category": "Reliability", "severity": "P1", "status_code": 500},
    "ERR_DB_LOCK_001": {"service": "checkout-api", "category": "Reliability", "severity": "P1", "status_code": 503},
    "ERR_DB_MIG_001": {"service": "checkout-api", "category": "Reliability", "severity": "P1", "status_code": 503},
    "ERR_DB_REPLICA_LAG_001": {"service": "checkout-api", "category": "Reliability", "severity": "P1", "status_code": 200},
    "ERR_DB_STORAGE_001": {"service": "checkout-api", "category": "Reliability", "severity": "P0", "status_code": 500},
    # K8s / infra
    "ERR_K8S_OOM_001": {"service": "ml-serving", "category": "Reliability", "severity": "P1", "status_code": 503},
    "ERR_K8S_CRASH_001": {"service": "checkout-api", "category": "Reliability", "severity": "P1", "status_code": 503},
    "ERR_K8S_PROBE_001": {"service": "checkout-api", "category": "Reliability", "severity": "P1", "status_code": 503},
    "ERR_K8S_IMG_001": {"service": "platform-infra", "category": "Reliability", "severity": "P1", "status_code": 0},
    "ERR_K8S_PEND_001": {"service": "platform-infra", "category": "Reliability", "severity": "P1", "status_code": 0},
    "ERR_K8S_NODE_CPU_001": {"service": "platform-infra", "category": "Performance", "severity": "P1", "status_code": 0},
    "ERR_K8S_NODE_MEM_001": {"service": "platform-infra", "category": "Reliability", "severity": "P0", "status_code": 0},
    "ERR_K8S_DISK_002": {"service": "platform-infra", "category": "Reliability", "severity": "P1", "status_code": 0},
    "ERR_DNS_001": {"service": "platform-infra", "category": "Reliability", "severity": "P0", "status_code": 0},
    "ERR_CERT_001": {"service": "platform-infra", "category": "Reliability", "severity": "P0", "status_code": 0},
    "ERR_HPA_001": {"service": "platform-infra", "category": "Reliability", "severity": "P1", "status_code": 0},
    "ERR_K8S_NETPOL_001": {"service": "platform-infra", "category": "Reliability", "severity": "P1", "status_code": 0},
    "ERR_OTEL_DROP_001": {"service": "platform-infra", "category": "Reliability", "severity": "P1", "status_code": 0},
    # Cache
    "ERR_REDIS_OOM_001": {"service": "checkout-api", "category": "Reliability", "severity": "P1", "status_code": 503},
    "ERR_CACHE_MISS_001": {"service": "checkout-api", "category": "Performance", "severity": "P1", "status_code": 503},
    "ERR_REDIS_LAT_001": {"service": "checkout-api", "category": "Performance", "severity": "P1", "status_code": 504},
    # Data/ML
    "ERR_KAFKA_LAG_001": {"service": "data-ingestor", "category": "Reliability", "severity": "P1", "status_code": 0},
    "ERR_KAFKA_ISR_001": {"service": "platform-infra", "category": "Reliability", "severity": "P0", "status_code": 0},
    "ERR_QUEUE_BACKLOG_001": {"service": "data-ingestor", "category": "Reliability", "severity": "P1", "status_code": 0},
    "ERR_FLINK_BP_001": {"service": "data-ingestor", "category": "Performance", "severity": "P1", "status_code": 0},
    "ERR_FLINK_CKPT_001": {"service": "data-ingestor", "category": "Reliability", "severity": "P1", "status_code": 500},
    "ERR_SPARK_SKEW_001": {"service": "data-ingestor", "category": "Performance", "severity": "P1", "status_code": 500},
    "ERR_VECTOR_LAT_001": {"service": "ml-serving", "category": "Performance", "severity": "P1", "status_code": 504},
    "ERR_ML_EMBED_001": {"service": "ml-serving", "category": "Reliability", "severity": "P1", "status_code": 500},
    "ERR_ML_DRIFT_001": {"service": "ml-serving", "category": "Performance", "severity": "P2", "status_code": 200},
}


# Cost runbooks (layer0 has basic cost anomalies too)
COST_CODES = [
    "ERR_COST_S3_VER_001",
    "ERR_COST_S3_REQ_001",
    "ERR_COST_EBS_001",
    "ERR_COST_EBS_SNAP_001",
    "ERR_COST_NAT_001",
    "ERR_COST_LOGS_001",
    "ERR_COST_XFER_001",
    "ERR_COST_LB_001",
    "ERR_COST_RI_001",
]


@dataclass(frozen=True)
class IncidentPlan:
    error_code: str
    service: str
    start: datetime
    end: datetime


def iso(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).isoformat()


def percentile(values: List[int], p: float) -> int:
    if not values:
        return 0
    s = sorted(values)
    k = int(round((len(s) - 1) * p))
    return s[max(0, min(k, len(s) - 1))]


def build_runbook_index(runbooks_dir: Path, repo_root: Path) -> Dict[str, str]:
    index: Dict[str, str] = {}
    for p in sorted(runbooks_dir.glob("*.md")):
        code = p.name.split("-", 1)[0]
        if code in index:
            raise RuntimeError(f"Duplicate runbook code: {code}")
        index[code] = str(p.relative_to(repo_root).as_posix())
    return index


def ensure_codes_exist(codes: Iterable[str], runbook_index: Dict[str, str]) -> None:
    missing = sorted(set(codes) - set(runbook_index.keys()))
    if missing:
        raise RuntimeError(f"Missing runbooks for codes: {missing}")


def choose_incident_plans(rng, start: datetime, hours: int) -> List[IncidentPlan]:
    # Pick a handful of distinct codes to inject as “real” incidents.
    candidates = [
        "ERR_DB_CON_001",
        "ERR_DB_QRY_001",
        "ERR_HTTP_504_001",
        "ERR_K8S_OOM_001",
        "ERR_DNS_001",
        "ERR_REDIS_OOM_001",
        "ERR_FLINK_CKPT_001",
        "ERR_VECTOR_LAT_001",
        "ERR_KAFKA_LAG_001",
        "ERR_K8S_DISK_002",
    ]
    rng.shuffle(candidates)
    picked = candidates[:8]

    plans: List[IncidentPlan] = []
    for code in picked:
        meta = ERROR_CATALOG[code]
        # Place incidents during business hours in the middle of the dataset
        day = start.date()
        base = datetime(day.year, day.month, day.day, 9, 0, tzinfo=timezone.utc)
        # Keep within the generated window
        base = max(start + timedelta(hours=1), min(base, start + timedelta(hours=max(2, hours - 3))))
        offset_min = rng.randint(0, 6 * 60)
        dur_min = rng.randint(15, 45)
        s = base + timedelta(minutes=offset_min)
        e = min(s + timedelta(minutes=dur_min), start + timedelta(hours=hours) - timedelta(minutes=1))
        plans.append(IncidentPlan(error_code=code, service=meta["service"], start=s, end=e))

    plans.sort(key=lambda x: x.start)
    return plans


def base_rpm_for_service(service: str) -> int:
    return {
        "checkout-api": 9,
        "payment-gw": 6,
        "ml-serving": 7,
        "data-ingestor": 4,
        "platform-infra": 1,
    }[service]


def jittered_rpm(rng, base: int) -> int:
    # Simple “bursty but stable” generator without external deps
    # ~ +/- 30% jitter, never negative.
    return max(0, int(round(base * (0.7 + rng.random() * 0.6))))


def is_in_window(ts: datetime, start: datetime, end: datetime) -> bool:
    return start <= ts < end


def active_incident_for(service: str, ts: datetime, plans: List[IncidentPlan]) -> Optional[IncidentPlan]:
    for p in plans:
        if p.service == service and is_in_window(ts, p.start, p.end):
            return p
    return None


def gen_latency_ms(rng, service: str, level: str, in_incident: bool) -> int:
    if level == "INFO":
        base = {"checkout-api": 120, "payment-gw": 140, "ml-serving": 180, "data-ingestor": 250, "platform-infra": 40}[service]
        return max(5, int(rng.gauss(base, base * 0.35)))
    # WARN/ERROR
    if in_incident:
        return rng.randint(2000, 14000)
    return rng.randint(900, 7000)


def gen_level_and_error(rng, service: str, incident: Optional[IncidentPlan]) -> Tuple[str, Optional[str], int]:
    if incident is None:
        # Baseline error rate is low
        level = rng.choices(["INFO", "WARN", "ERROR"], weights=[0.94, 0.03, 0.03])[0]
        if level == "INFO":
            return level, None, 200

        # Pick a plausible code for the service
        svc_codes = [c for c, m in ERROR_CATALOG.items() if m["service"] == service]
        code = rng.choice(svc_codes)
        status = int(ERROR_CATALOG[code]["status_code"])
        return level, code, status

    # During incident windows, bias heavily to incident code
    level = rng.choices(["ERROR", "WARN", "INFO"], weights=[0.75, 0.15, 0.10])[0]
    if level == "INFO":
        return "INFO", None, 200
    code = incident.error_code
    status = int(ERROR_CATALOG[code]["status_code"])
    return level, code, status


def generate_logs(
    *,
    rng,
    start: datetime,
    hours: int,
    plans: List[IncidentPlan],
) -> List[Dict[str, Any]]:
    logs: List[Dict[str, Any]] = []
    end = start + timedelta(hours=hours)

    ts = start
    while ts < end:
        for service in ALL_SERVICES:
            rpm = jittered_rpm(rng, base_rpm_for_service(service))
            incident = active_incident_for(service, ts, plans)
            # Platform infra emits fewer “request-like” events
            if service == "platform-infra":
                rpm = min(rpm, 2)

            for _ in range(rpm):
                level, error_code, status_code = gen_level_and_error(rng, service, incident)
                latency_ms = gen_latency_ms(rng, service, level, incident is not None)
                message = f"Request processed for {TENANT_ID}" if level == "INFO" else f"Failure: {error_code}"

                logs.append(
                    {
                        "timestamp": iso(ts + timedelta(seconds=rng.randint(0, 59))),
                        "trace_id": str(uuid.uuid4()),
                        "tenant_id": TENANT_ID,
                        "service_name": service,
                        "env": ENV,
                        "region": REGION,
                        "request_path": rng.choice(REQUEST_PATHS[service]),
                        "level": level,
                        "status_code": status_code,
                        "latency_ms": latency_ms,
                        "error_code": error_code,
                        "message": message,
                    }
                )

        ts += timedelta(minutes=1)

    # Keep logs in chronological-ish order for readability
    logs.sort(key=lambda x: x["timestamp"])
    return logs


def format_raw_log(log: Dict[str, Any]) -> str:
    message = str(log.get("message") or "").replace("\n", " ").replace('"', '\\"')
    error_code = log.get("error_code") or "-"
    return (
        f'{log["timestamp"]} '
        f'level={log["level"]} '
        f'tenant={log["tenant_id"]} '
        f'service={log["service_name"]} '
        f'env={log["env"]} '
        f'region={log["region"]} '
        f'path={log["request_path"]} '
        f'status={log["status_code"]} '
        f'latency_ms={log["latency_ms"]} '
        f'trace_id={log["trace_id"]} '
        f'error_code={error_code} '
        f'msg="{message}"'
    )


def write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
    lines = [json.dumps(row, ensure_ascii=True, separators=(",", ":")) for row in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_gzip_text(path: Path, text: str) -> None:
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        handle.write(text)


def compute_hourly_metrics(logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    buckets: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
    for l in logs:
        ts = datetime.fromisoformat(l["timestamp"])
        hour = ts.replace(minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
        key = (l["service_name"], hour.isoformat())
        buckets.setdefault(key, []).append(l)

    out: List[Dict[str, Any]] = []
    for (service, hour_iso), items in sorted(buckets.items(), key=lambda x: (x[0][1], x[0][0])):
        lat = [int(i["latency_ms"]) for i in items]
        errs = [i for i in items if i["level"] in ("WARN", "ERROR")]
        out.append(
            {
                "tenant_id": TENANT_ID,
                "service_name": service,
                "timestamp_hour": hour_iso,
                "requests": len(items),
                "errors": len(errs),
                "error_rate_pct": round((len(errs) / max(1, len(items))) * 100.0, 2),
                "p50_latency_ms": percentile(lat, 0.50),
                "p95_latency_ms": percentile(lat, 0.95),
            }
        )
    return out


def summarize_incidents_from_plans(
    *,
    logs: List[Dict[str, Any]],
    plans: List[IncidentPlan],
    runbook_index: Dict[str, str],
) -> List[Dict[str, Any]]:
    incidents: List[Dict[str, Any]] = []
    # Build per-plan views
    for p in plans:
        w = [l for l in logs if l["service_name"] == p.service and is_in_window(datetime.fromisoformat(l["timestamp"]), p.start, p.end)]
        if not w:
            continue
        err = [l for l in w if l["level"] in ("WARN", "ERROR")]
        lat = [int(l["latency_ms"]) for l in w]
        status_counts: Dict[str, int] = {}
        for l in err:
            sc = str(l["status_code"])
            status_counts[sc] = status_counts.get(sc, 0) + 1

        meta = ERROR_CATALOG[p.error_code]
        incidents.append(
            {
                "incident_id": f"INC-{uuid.uuid4()}",
                "source": "logs",
                "title": f"{p.service} incident: {p.error_code}",
                "tenant_id": TENANT_ID,
                "service_name": p.service,
                "category": meta["category"],
                "severity": meta["severity"],
                "error_codes": [p.error_code],
                "start_time": iso(p.start),
                "end_time": iso(p.end),
                "status": "resolved",
                "symptoms": {
                    "log_pattern": f"Failure: {p.error_code}",
                    "error_rate_pct": round((len(err) / max(1, len(w))) * 100.0, 2),
                    "status_code_counts": status_counts,
                    "p95_latency_ms": percentile(lat, 0.95),
                    "sample_trace_ids": [l["trace_id"] for l in err[:5]],
                },
                "runbook_refs": [runbook_index[p.error_code]],
            }
        )

    return incidents


def generate_cost_summaries(rng) -> List[Dict[str, Any]]:
    # Single-tenant, per-service daily spend + shared-infra line items.
    out: List[Dict[str, Any]] = []

    for svc in APP_SERVICES:
        out.append(
            {
                "tenant_id": TENANT_ID,
                "service_name": svc,
                "daily_spend_usd": round(rng.uniform(40.0, 250.0), 2),
                "currency": "USD",
                "resource_type": "EC2/EKS",
            }
        )

    shared = [
        ("NAT Gateway", rng.uniform(30.0, 160.0)),
        ("S3", rng.uniform(25.0, 140.0)),
        ("S3 Requests", rng.uniform(10.0, 120.0)),
        ("EBS", rng.uniform(15.0, 120.0)),
        ("EBS Snapshot", rng.uniform(8.0, 90.0)),
        ("Logs", rng.uniform(10.0, 130.0)),
        ("Data Transfer", rng.uniform(8.0, 110.0)),
        ("Load Balancer", rng.uniform(5.0, 80.0)),
        ("Savings Coverage", rng.uniform(0.0, 1.0)),  # 0..1 coverage
    ]

    # Inject a couple anomalies that will become cost incidents
    for i, (rt, v) in enumerate(shared):
        if rt in ("NAT Gateway", "S3"):
            v = v + rng.uniform(180.0, 500.0)
        if rt == "Logs":
            v = v + rng.uniform(120.0, 280.0)
        if rt == "Savings Coverage":
            v = rng.uniform(0.25, 0.55)  # low coverage
        shared[i] = (rt, v)

    for rt, v in shared:
        out.append(
            {
                "tenant_id": TENANT_ID,
                "service_name": "shared-infra",
                "daily_spend_usd": round(float(v), 2) if rt != "Savings Coverage" else None,
                "currency": "USD",
                "resource_type": rt,
                "savings_coverage": round(float(v), 2) if rt == "Savings Coverage" else None,
            }
        )

    return out


def generate_cost_incidents(cost: List[Dict[str, Any]], runbook_index: Dict[str, str]) -> List[Dict[str, Any]]:
    # Map resource_type -> cost code
    type_to_code = {
        "NAT Gateway": "ERR_COST_NAT_001",
        "S3": "ERR_COST_S3_VER_001",
        "S3 Requests": "ERR_COST_S3_REQ_001",
        "EBS": "ERR_COST_EBS_001",
        "EBS Snapshot": "ERR_COST_EBS_SNAP_001",
        "Logs": "ERR_COST_LOGS_001",
        "Data Transfer": "ERR_COST_XFER_001",
        "Load Balancer": "ERR_COST_LB_001",
        "Savings Coverage": "ERR_COST_RI_001",
    }
    thresholds_usd = {
        "NAT Gateway": 250.0,
        "S3": 200.0,
        "S3 Requests": 90.0,
        "EBS": 90.0,
        "EBS Snapshot": 60.0,
        "Logs": 150.0,
        "Data Transfer": 80.0,
        "Load Balancer": 40.0,
    }

    now = datetime(2025, 1, 1, 23, 59, tzinfo=timezone.utc)
    incidents: List[Dict[str, Any]] = []

    for row in cost:
        if row["service_name"] != "shared-infra":
            continue
        rt = row["resource_type"]
        code = type_to_code.get(rt)
        if not code:
            continue

        if rt == "Savings Coverage":
            coverage = float(row["savings_coverage"] or 0.0)
            if coverage >= 0.60:
                continue
            meta = {"category": "Cost", "severity": "P2"}
            incidents.append(
                {
                    "incident_id": f"COST-{uuid.uuid4()}",
                    "source": "cost",
                    "title": f"Savings coverage low ({int(coverage*100)}%)",
                    "tenant_id": TENANT_ID,
                    "service_name": "shared-infra",
                    "category": meta["category"],
                    "severity": meta["severity"],
                    "error_codes": [code],
                    "start_time": iso(now - timedelta(hours=24)),
                    "end_time": iso(now),
                    "status": "open",
                    "symptoms": {"resource_type": rt, "coverage": coverage},
                    "runbook_refs": [runbook_index[code]],
                }
            )
            continue

        daily = float(row["daily_spend_usd"] or 0.0)
        if daily < thresholds_usd.get(rt, math.inf):
            continue
        monthly = round(daily * 30.0, 2)
        incidents.append(
            {
                "incident_id": f"COST-{uuid.uuid4()}",
                "source": "cost",
                "title": f"{rt} cost anomaly",
                "tenant_id": TENANT_ID,
                "service_name": "shared-infra",
                "category": "Cost",
                "severity": "P2",
                "error_codes": [code],
                "start_time": iso(now - timedelta(hours=24)),
                "end_time": iso(now),
                "status": "open",
                "symptoms": {"resource_type": rt, "daily_spend_usd": daily, "estimated_monthly_usd": monthly},
                "runbook_refs": [runbook_index[code]],
            }
        )

    return incidents


def parse_time_window(question: str, base_date: datetime) -> Optional[Tuple[datetime, datetime]]:
    # Minimal parser: “between 10–11am” / “between 10 and 11am” / “10-11am”
    q = question.lower().replace("–", "-")
    m = re.search(r"(?:between\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\s*(?:and|-|to)\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", q)
    if not m:
        return None

    def to_24h(h: int, ampm: Optional[str]) -> int:
        if not ampm:
            return h
        if ampm == "am":
            return 0 if h == 12 else h
        # pm
        return 12 if h == 12 else h + 12

    h1 = to_24h(int(m.group(1)), m.group(3))
    m1 = int(m.group(2) or 0)
    h2 = to_24h(int(m.group(4)), m.group(6) or m.group(3))
    m2 = int(m.group(5) or 0)

    start = base_date.replace(hour=h1, minute=m1, second=0, microsecond=0)
    end = base_date.replace(hour=h2, minute=m2, second=0, microsecond=0)
    if end <= start:
        end = end + timedelta(hours=1)
    return start, end


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Layer 0 single-tenant demo datasets for OpsPilot.")
    parser.add_argument("--seed", type=int, default=42, help="Deterministic random seed.")
    parser.add_argument("--hours", type=int, default=24, help="How many hours of logs to generate.")
    parser.add_argument("--out-dir", type=str, default="level_zero/data", help="Output directory (inside repo).")
    args = parser.parse_args()

    rng = __import__("random").Random(args.seed)

    repo_root = Path(__file__).resolve().parents[2]
    runbooks_dir = repo_root / "level_zero" / "knowledge_base" / "runbooks"
    out_dir = (repo_root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    runbook_index = build_runbook_index(runbooks_dir, repo_root)

    # Ensure our generator only emits codes with runbooks present.
    ensure_codes_exist(ERROR_CATALOG.keys(), runbook_index)
    ensure_codes_exist(COST_CODES, runbook_index)

    # Fixed base date keeps demo queries like “between 10–11am” stable.
    start = datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc)
    plans = choose_incident_plans(rng, start, args.hours)

    logs = generate_logs(rng=rng, start=start, hours=args.hours, plans=plans)
    hourly_metrics = compute_hourly_metrics(logs)
    cost = generate_cost_summaries(rng)

    incidents = []
    incidents.extend(summarize_incidents_from_plans(logs=logs, plans=plans, runbook_index=runbook_index))
    incidents.extend(generate_cost_incidents(cost, runbook_index))

    (out_dir / "synthetic_logs.json").write_text(json.dumps(logs, indent=2), encoding="utf-8")
    (out_dir / "hourly_metrics.json").write_text(json.dumps(hourly_metrics, indent=2), encoding="utf-8")
    (out_dir / "cost_summaries.json").write_text(json.dumps(cost, indent=2), encoding="utf-8")
    (out_dir / "synthetic_incidents.json").write_text(json.dumps(incidents, indent=2), encoding="utf-8")

    raw_log_text = "\n".join(format_raw_log(log) for log in logs) + "\n"
    (out_dir / "synthetic_logs.raw.txt").write_text(raw_log_text, encoding="utf-8")
    write_gzip_text(out_dir / "synthetic_logs.raw.txt.gz", raw_log_text)

    write_jsonl(out_dir / "synthetic_incidents.jsonl", incidents)
    write_gzip_text(out_dir / "synthetic_incidents.jsonl.gz", (out_dir / "synthetic_incidents.jsonl").read_text(encoding="utf-8"))

    write_csv(out_dir / "hourly_metrics.csv", hourly_metrics)
    write_gzip_text(out_dir / "hourly_metrics.csv.gz", (out_dir / "hourly_metrics.csv").read_text(encoding="utf-8"))

    write_csv(out_dir / "cost_summaries.csv", cost)
    write_gzip_text(out_dir / "cost_summaries.csv.gz", (out_dir / "cost_summaries.csv").read_text(encoding="utf-8"))

    print(f"Generated Layer 0 data under: {out_dir}")


if __name__ == "__main__":
    main()
