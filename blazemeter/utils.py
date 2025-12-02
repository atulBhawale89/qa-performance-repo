from datetime import datetime, timezone, timedelta
import time


def ts_to_ist_formatted(ts_seconds, fmt="%d-%b-%Y %I:%M:%S %p"):
    if ts_seconds is None:
        return None
    ist = timezone(timedelta(hours=5, minutes=30))
    dt = datetime.fromtimestamp(int(ts_seconds), ist)
    return dt.strftime(fmt)


def ts_to_utc_formatted(ts_seconds, fmt="%d-%b-%Y %I:%M:%S %p"):
    """Convert Unix timestamp in seconds to ISO 8601 UTC format with milliseconds and 'Z'."""
    if ts_seconds is None:
        return None
    # Accept float or int for sub-second precision
    dt = datetime.fromtimestamp(float(ts_seconds), timezone.utc)
    # Format: 'YYYY-MM-DDTHH:MM:SS.sssZ'
    iso_str = dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    return iso_str


def wait(seconds, message=None):
    """Wait for the specified number of seconds, optionally printing a message."""
    if message:
        print(f"Waiting for {seconds} seconds: {message}")
    else:
        print(f"Waiting for {seconds} seconds...")
    time.sleep(seconds)
    print("Wait complete.")

def insert_json_to_bigquery_and_cleanup(json_path: str, project_id: str, dataset_id: str, table_id: str) -> bool:
    """
    Inserts data from a JSON file into a BigQuery table. Deletes the JSON file after successful insertion.
    Returns True if successful, False otherwise.
    """
    import os
    import json
    from google.cloud import bigquery

    if not os.path.isfile(json_path):
        print(f"JSON file '{json_path}' does not exist.")
        return False

    try:
        # Load data from JSON file
        with open(json_path, 'r', encoding='utf-8') as f:
            rows = json.load(f)
        if not isinstance(rows, list):
            print("JSON data must be a list of records.")
            return False

        # Insert into BigQuery
        client = bigquery.Client(project=project_id)
        table_ref = f"{project_id}.{dataset_id}.{table_id}"
        errors = client.insert_rows_json(table_ref, rows)
        if errors:
            print(f"BigQuery insertion errors: {errors}")
            return False
        print(f"Inserted {len(rows)} rows into {table_ref}.")

        # Delete the JSON file
        os.remove(json_path)
        print(f"Deleted JSON file: {json_path}")
        return True
    except Exception as e:
        print(f"Error inserting JSON to BigQuery: {e}")
        return False