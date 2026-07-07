import os
import sys
import time
import requests

DBT_CLOUD_BASE_URL_DEFAULT = "https://cloud.getdbt.com/api/v2"
TERMINAL_STATUSES = {10, 20, 30}  # Success, Error, Cancelled
RETRIABLE_HTTP_STATUSES = {429, 500, 502, 503, 504}
POLL_INTERVAL_SECONDS = 10
DEFAULT_TIMEOUT_SECONDS = 3600  # 60 minutes
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 5


def trigger_job(account_id: str, job_id: str, service_token: str, commit_sha: str, cause: str, base_url: str) -> int:
    """Trigger a dbt Cloud job run. Exits with code 1 on API error."""
    url = f"{base_url}/accounts/{account_id}/jobs/{job_id}/run/"
    headers = {
        "Authorization": f"Token {service_token}",
        "Content-Type": "application/json",
    }
    payload = {"cause": cause, "git_sha": commit_sha}

    response = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(url, headers=headers, json=payload)
            break
        except requests.exceptions.RequestException as e:
            if attempt == MAX_RETRIES:
                print(f"ERROR: Failed to reach dbt Cloud after {MAX_RETRIES} attempts: {e}")
                sys.exit(1)
            print(f"WARNING: Network error triggering job (attempt {attempt}/{MAX_RETRIES}): {e}. Retrying in {RETRY_BACKOFF_SECONDS}s...")
            time.sleep(RETRY_BACKOFF_SECONDS)

    if response.status_code != 200:
        print(f"ERROR: Failed to trigger dbt Cloud job. Status {response.status_code}: {response.text}")
        sys.exit(1)

    try:
        run_id = response.json()["data"]["id"]
    except (KeyError, ValueError) as e:
        print(f"ERROR: Unexpected response body from dbt Cloud: {e}. Body: {response.text[:500]}")
        sys.exit(1)

    print(f"Triggered dbt Cloud run {run_id}")
    return run_id


def poll_run(account_id: str, run_id: int, service_token: str, base_url: str, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> int:
    """Poll a dbt Cloud run until it reaches a terminal status. Exits with code 1 on timeout."""
    url = f"{base_url}/accounts/{account_id}/runs/{run_id}/"
    headers = {"Authorization": f"Token {service_token}"}
    deadline = time.time() + timeout_seconds

    while True:
        if time.time() > deadline:
            print(f"ERROR: Timed out waiting for dbt Cloud run {run_id} after {timeout_seconds}s")
            sys.exit(1)

        try:
            response = requests.get(url, headers=headers)
        except requests.exceptions.RequestException as e:
            print(f"WARNING: Network error polling run {run_id}: {e}. Will retry on next poll.")
            time.sleep(POLL_INTERVAL_SECONDS)
            continue

        if response.status_code in RETRIABLE_HTTP_STATUSES:
            print(f"WARNING: Received status {response.status_code} polling run {run_id}. Will retry.")
            time.sleep(POLL_INTERVAL_SECONDS)
            continue

        if response.status_code != 200:
            print(f"ERROR: Unexpected response polling run {run_id}. Status {response.status_code}: {response.text[:500]}")
            sys.exit(1)

        try:
            data = response.json()["data"]
            status = data["status"]
            status_label = data["status_humanized"]
        except (KeyError, ValueError) as e:
            print(f"ERROR: Unexpected response body polling run {run_id}: {e}. Body: {response.text[:500]}")
            sys.exit(1)

        print(f"Run {run_id} status: {status_label} ({status})")

        if status in TERMINAL_STATUSES:
            return status

        time.sleep(POLL_INTERVAL_SECONDS)


def main() -> None:
    """Trigger and poll a dbt Cloud CI job. Exits 0 on success, 1 on failure."""
    required_vars = ["DBT_CLOUD_SERVICE_TOKEN", "DBT_CLOUD_ACCOUNT_ID", "DBT_CLOUD_JOB_ID", "CI_COMMIT_SHA"]
    missing = [v for v in required_vars if v not in os.environ]
    if missing:
        print(f"ERROR: Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)

    service_token = os.environ["DBT_CLOUD_SERVICE_TOKEN"]
    account_id = os.environ["DBT_CLOUD_ACCOUNT_ID"]
    job_id = os.environ["DBT_CLOUD_JOB_ID"]
    commit_sha = os.environ["CI_COMMIT_SHA"]
    cause = os.environ.get("DBT_JOB_CAUSE", "CI pipeline")
    base_url = os.environ.get("DBT_CLOUD_BASE_URL", DBT_CLOUD_BASE_URL_DEFAULT)

    run_id = trigger_job(account_id, job_id, service_token, commit_sha, cause, base_url)
    final_status = poll_run(account_id, run_id, service_token, base_url)

    if final_status == 10:  # Success
        print(f"dbt Cloud run {run_id} succeeded.")
        return
    print(f"dbt Cloud run {run_id} finished with status {final_status}. Failing pipeline.")
    sys.exit(1)


if __name__ == "__main__":
    main()