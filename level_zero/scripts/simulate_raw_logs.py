import argparse
import random
import uuid
from datetime import datetime, timedelta, timezone

# Realistic raw log format:
# 2025-01-01 10:00:00.123 [INFO] [checkout-api] [tenant-demo] Request processed path=/api/checkout status=200 latency=120ms
# 2025-01-01 10:05:00.456 [ERROR] [payment-gw] [tenant-demo] ERR_DB_CON_001 Connection timed out during payment auth

TENANT_ID = "tenant-demo"
SERVICES = ["checkout-api", "payment-gw", "data-ingestor", "ml-serving", "platform-infra"]
ERROR_CODES = {
    "checkout-api": ["ERR_DB_CON_001", "ERR_HTTP_504_001", "ERR_CACHE_MISS_001"],
    "payment-gw": ["ERR_DEP_TIMEOUT_001", "ERR_RATE_LIMIT_001", "ERR_DB_DLK_001"],
    "ml-serving": ["ERR_K8S_OOM_001", "ERR_VECTOR_LAT_001"],
}

def generate_raw_logs(output_file: str, hours: int = 24):
    start_time = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    end_time = start_time + timedelta(hours=hours)
    current_time = start_time

    print(f"Generating raw logs from {start_time} to {end_time} into {output_file}...")
    
    with open(output_file, "w") as f:
        while current_time < end_time:
            # Randomize step
            current_time += timedelta(milliseconds=random.randint(50, 2000))
            
            service = random.choice(SERVICES)
            is_error = random.random() < 0.05 # 5% error rate
            
            if is_error:
                level = "ERROR"
                # Pick an error code if available, else generic
                codes = ERROR_CODES.get(service, ["ERR_GENERIC_001"])
                code = random.choice(codes)
                msg = f"{code} Internal failure processing trace_id={uuid.uuid4()}"
            else:
                level = "INFO"
                latency = random.randint(20, 500)
                path = f"/api/{random.choice(['v1', 'v2'])}/resource"
                msg = f"Request processed path={path} status=200 latency={latency}ms trace_id={uuid.uuid4()}"

            # Write raw line
            # "2025-01-01 10:00:00.123 [INFO] [checkout-api] [tenant-demo] ..."
            ts_str = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            line = f"{ts_str} [{level}] [{service}] [{TENANT_ID}] {msg}\n"
            f.write(line)

    print(f"Done. Generated raw logs at {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="level_zero/data/raw_syslog.log", help="Output path")
    args = parser.parse_args()
    
    generate_raw_logs(args.out)
