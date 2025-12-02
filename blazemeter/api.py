import requests
import time
from datetime import datetime, timezone, timedelta
from .config import BASE_URL, auth, POLL_INTERVAL_SECONDS
import os


# Example file paths for uploads
# jmx_file_path = "c:/Users/atulb/Desktop/repo/personal_Perfrepo/qa-performance-repo/ExampleTest.jmx"  # Created JMX file
# csv_file_path = "path/to/your/TestData.csv"  # Update with your actual .csv file path
# csv_file_path = "path/to/your/TestData.csv"  # Update with your actual .csv file path


def find_test_by_name(test_name):
    """Search tests by name and return the first test's id if found."""
    params = {"search": test_name, "limit": 50}
    url = f"{BASE_URL}/tests"
    Print(f"Searching for test with name: {test_name}")
    resp = requests.get(url, params=params, auth=auth)
    resp.raise_for_status()
    results = resp.json().get("result", [])
    # simple exact or partial match: pick the first whose name contains the provided string
    for t in results:
        if test_name.lower() in t.get("name", "").lower():
            return t.get("id")
    # fallback: return first if any
    if results:
        return results[0].get("id")
    return None

    # ---------------------------------Update configuration-----------------------------------


def upload_files_to_blazemeter_test(
    test_id, jmx_file_name, csv_file_name, wait_time=60
):
    """
    Uploads a JMeter .jmx file and/or a .csv test data file from the Script/TestData folder to an existing BlazeMeter test ID.
    If any file name is not provided, it will be ignored.
    After successful upload, waits for specified time (default 120 seconds) before returning.
    """
    upload_url = f"https://a.blazemeter.com/api/v4/tests/{test_id}/files"
    # headers = {"Authorization": f"Bearer {api_key}"} # If you use Bearer token
    script_folder = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "Script"
    )
    test_Data = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "TestData"
    )

    if jmx_file_name:
        jmx_path = os.path.join(script_folder, jmx_file_name)
        if os.path.exists(jmx_path):
            with open(jmx_path, "rb") as jmx_file:
                files = {"file": (jmx_file_name, jmx_file, "application/octet-stream")}
                response_jmx = requests.post(upload_url, auth=auth, files=files)
                response_jmx.raise_for_status()
                print(f"JMX file upload successful for test ID: {test_id}")
        else:
            print(f"JMX file not found: {jmx_path}")
    if csv_file_name:
        csv_path = os.path.join(test_Data, csv_file_name)
        if os.path.exists(csv_path):
            with open(csv_path, "rb") as csv_file:
                files = {"file": (csv_file_name, csv_file, "text/csv")}
                response_csv = requests.post(upload_url, auth=auth, files=files)
                response_csv.raise_for_status()
                print(f"CSV file upload successful for test ID: {test_id}")
        else:
            print(f"CSV file not found: {csv_path}")

    # Wait for specified time after successful upload
    if wait_time > 0:
        print(f"Waiting for {wait_time} seconds to ensure files are processed...")
        time.sleep(wait_time)
        print("Wait complete, proceeding with test execution.")

    return True


# Example usage:
# upload_jmx_to_blazemeter('YOUR_BLAZEMETER_API_KEY', 'UserCase_2Perf.jmx', 'UserCase_2Perf Upload')
# -------------------------------------------------------------


def update_Blazameter_Configur(test_id, user_load, duration, rampup, region):
    """
    Update BlazeMeter test with override execution settings.
    """
    url_Update = f"{BASE_URL}/tests/{test_id}"
    print(
        f"Startinginside  test {test_id} with user_load={user_load}, duration={duration}, rampup={rampup}, region={region}"
    )
    payload_Update = {
        "overrideExecutions": [
            {
                "concurrency": user_load,
                "executor": "jmeter",
                "holdFor": f"{duration}m",
                "rampUp": f"{rampup}m",
                "locations": {region: 1},
                "locationsPercents": {region: 100},
            }
        ]
    }
    print("payload_Update:", payload_Update)
    print("url:", url_Update)

    resp = requests.patch(url_Update, json=payload_Update, auth=auth)
    print("payload_Update:", resp)
    statusCode = resp.status_code
    if resp.status_code not in (200, 201):
        print(f"Failed to start test {test_id}: {resp.status_code} {resp.text}")
        return None, None
    data_update = resp.json().get("result", {})
    # Extract session_id and master_id if present
    # sessions = data_update.get("sessionsId") or data_update.get("sessions", [])
    # session_id = sessions[0] if isinstance(sessions, list) and sessions else None
    # print("data_update:",data_update)
    return statusCode


# -----------------------------------------------------------------------------------------
def start_test(test_id, user_load, duration, rampup, region):
    """
    Start BlazeMeter test with override execution settings.
    """
    url = f"{BASE_URL}/tests/{test_id}/start"
    print(
        f"Starting test {test_id} with user_load={user_load}, duration={duration}, rampup={rampup}, region={region}"
    )
    # Build execution override payload
    payload = {
        "configuration": {
            "execution": [
                {
                    "concurrency": user_load,
                    "holdFor": f"{duration}m",
                    "rampUp": f"{rampup}m",
                    "locations": {
                        region: 2
                    },  # Assuming region is a valid location key,
                }
            ]
        }
    }
    resp = requests.post(url, json=payload, auth=auth)
    if resp.status_code not in (200, 202):
        print(f"Failed to start test {test_id}: {resp.status_code} {resp.text}")
        return None, None
    data = resp.json().get("result", {})
    # response may include sessionsId and masterId
    sessions = data.get("sessionsId") or data.get("sessions", [])
    session_id = sessions[0] if isinstance(sessions, list) and sessions else None
    master_id = (
        data.get("masterId") or data.get("id") or data.get("result", {}).get("masterId")
    )
    # sometimes masterId is inside 'sessions' details; we'll fall back to session lookup
    print(f"Started test {test_id}. session_id={session_id}, master_id={master_id}")
    return session_id, master_id


def get_session_status(session_id):
    url = f"{BASE_URL}/sessions/{session_id}"
    resp = requests.get(url, auth=auth)
    if resp.status_code != 200:
        print(f"Failed to get session {session_id}: {resp.status_code} {resp.text}")
        return None, resp
    data = resp.json().get("result", {})
    # common fields: status, masterId (sometimes)
    status = data.get("status")
    master_id = data.get("masterId") or data.get("master") or data.get("masterId")
    return status, data


def wait_for_completion(
    session_id, poll_interval=POLL_INTERVAL_SECONDS, timeout_minutes=None
):
    """
    Poll session until it reaches a terminal state.
    """
    start_time = time.time()
    timeout_seconds = timeout_minutes * 60 if timeout_minutes else None
    while True:
        status, data = get_session_status(session_id)
        if status is None:
            return None
        print(
            f"[{datetime.utcnow().isoformat()}Z] Session {session_id} status: {status}"
        )
        if status.lower() in ("ended", "failed", "aborted", "stopped"):
            return data
        if timeout_seconds and (time.time() - start_time) > timeout_seconds:
            print(f"Timed out waiting for session {session_id}")
            return None
        time.sleep(poll_interval)


def fetch_master_summary(master_id):
    """Fetch the master summary (contains startTime and endTime timestamps)."""
    url = f"{BASE_URL}/masters/{master_id}/reports/default/summary/"
    resp = requests.get(url, auth=auth)
    if resp.status_code != 200:
        print(
            f"Failed to fetch summary for master {master_id}: {resp.status_code} {resp.text}"
        )
        return None
    return resp.json().get("result", {})


def fetch_request_Statistics(master_id):
    """Fetch the Request Statistic (contains performance Parameter)."""
    url = f"{BASE_URL}/masters/{master_id}/reports/aggregatereport/data"
    resp_request_Statistics = requests.get(url, auth=auth)
    if resp_request_Statistics.status_code != 200:
        print(
            f"Failed to fetch summary for master {master_id}: {resp_request_Statistics.status_code} {resp_request_Statistics.text}"
        )
        return None
        print("resp_request_Statistics:", resp_request_Statistics)
    return resp_request_Statistics.json()


# error handling for file operations
def fetch_error_statistics(master_id):
    """
    Fetch error statistics from BlazeMeter for a given master ID.
    """
    url = f"{BASE_URL}/masters/{master_id}/reports/errorsreport/data"
    resp = requests.get(url, auth=auth)

    if resp.status_code != 200:
        return []
    error_Results = resp.json().get("result", [])
    errors = []
    print("error_Results:", error_Results)
    for item in error_Results:
        for err in item.get("errors", []):
            errors.append(
                {
                    "label": item.get("name"),
                    "status_code": err.get("rc"),
                    "error_message": err.get("m"),
                    "count": err.get("count"),
                }
            )
    print("errors:", errors)
    return errors
