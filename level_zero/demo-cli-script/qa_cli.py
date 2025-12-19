import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def parse_time_window(question: str, base_date: datetime) -> Optional[Tuple[datetime, datetime]]:
    # Minimal parser: “between 10–11am” / “between 10 and 11am” / “10-11am”
    q = question.lower().replace("–", "-")
    m = re.search(
        r"(?:between\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\s*(?:and|-|to)\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)?",
        q,
    )
    if not m:
        return None

    def to_24h(h: int, ampm: Optional[str]) -> int:
        if not ampm:
            return h
        if ampm == "am":
            return 0 if h == 12 else h
        return 12 if h == 12 else h + 12

    h1 = to_24h(int(m.group(1)), m.group(3))
    m1 = int(m.group(2) or 0)
    h2 = to_24h(int(m.group(4)), m.group(6) or m.group(3))
    m2 = int(m.group(5) or 0)

    start = base_date.replace(hour=h1, minute=m1, second=0, microsecond=0)
    end = base_date.replace(hour=h2, minute=m2, second=0, microsecond=0)
    if end <= start:
        end = end.replace(hour=(start.hour + 1) % 24)
    return start, end


def overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    return a_start < b_end and b_start < a_end


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Layer 0 single-tenant Q&A CLI (no LLM, deterministic).")
    parser.add_argument("--question", required=True, help="Question, e.g. 'What happened to checkout-api between 10-11am?'")
    parser.add_argument("--data-dir", default="level_zero/data", help="Path to Layer 0 data directory.")
    parser.add_argument("--repo-root", default=".", help="Repo root path.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    data_dir = (repo_root / args.data_dir).resolve()

    incidents = load_json(data_dir / "synthetic_incidents.json")
    logs = load_json(data_dir / "synthetic_logs.json")

    # Base date is the date of the first log entry (dataset is fixed to 2025-01-01 by generator).
    first_ts = datetime.fromisoformat(logs[0]["timestamp"]).astimezone(timezone.utc)
    base_date = first_ts.replace(hour=0, minute=0, second=0, microsecond=0)

    window = parse_time_window(args.question, base_date)
    if not window:
        print("I can answer time-window questions like: 'between 10-11am'.")
        print("Try: --question \"What happened to checkout-api between 10-11am?\"")
        return

    w_start, w_end = window
    q = args.question.lower()
    service = None
    for s in ["checkout-api", "payment-gw", "data-ingestor", "ml-serving", "platform-infra"]:
        if s in q:
            service = s
            break

    # Filter incidents overlapping the window (and optionally by service)
    hits: List[Dict[str, Any]] = []
    for inc in incidents:
        i_start = datetime.fromisoformat(inc["start_time"]).astimezone(timezone.utc)
        i_end = datetime.fromisoformat(inc["end_time"]).astimezone(timezone.utc)
        if not overlaps(w_start, w_end, i_start, i_end):
            continue
        if service and inc.get("service_name") != service:
            continue
        hits.append(inc)

    print(f"Window: {w_start.isoformat()} → {w_end.isoformat()}")
    if service:
        print(f"Service filter: {service}")
    print("")

    if not hits:
        print("No incidents detected in this window based on synthetic_incidents.json.")
        return

    print("Detected incidents:")
    for inc in hits:
        codes = ", ".join(inc.get("error_codes", []))
        rb = ", ".join(inc.get("runbook_refs", []))
        print(f"- {inc['title']} [{inc['severity']}]")
        print(f"  - error_codes: {codes}")
        print(f"  - runbooks: {rb}")
        print(f"  - symptoms: {json.dumps(inc.get('symptoms', {}), indent=2)}")
        print("")


if __name__ == "__main__":
    main()


