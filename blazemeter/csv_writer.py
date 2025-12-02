from typing import Union, Dict, Any, List
import os
import csv
import json


def _load_json(
    json_data_or_path: Union[Dict[str, Any], str]
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """Helper to load JSON data from dict or file path."""
    # print("data:", json_data_or_path)
    if isinstance(json_data_or_path, dict):
        return json_data_or_path
    elif isinstance(json_data_or_path, str) and os.path.isfile(json_data_or_path):
        with open(json_data_or_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        raise ValueError("Invalid JSON data or file path provided.")


def append_json_to_csv(
    json_data_or_path: Union[Dict[str, Any], List[Dict[str, Any]], str],
    csv_file: str,
    start_date: str = None,
    end_date: str = None,
    errors: Union[List[Dict[str, Any]], str, None] = None,
    avg_total_time: float = None,
    avgApigeeTime: float = None,
    avgBackendTime: float = None,
) -> None:
    """
    Appends rows from JSON into an existing CSV (one row per item in 'result' list if present).
    Filters out records where labelName or label is 'ALL'.
    """
    data = _load_json(json_data_or_path)

    # Ensure data is iterable
    if isinstance(data, dict) and "result" in data and isinstance(data["result"], list):
        records = data["result"]
    elif isinstance(data, list):
        records = data
    else:
        records = [data]  # wrap single dict into list

    # Filter out records where labelName or label is 'ALL'
    filtered_records = []
    for record in records:
        if isinstance(record, dict):
            label_name = record.get("labelName", "")
            label = record.get("label", "")
            
            # Skip records where labelName or label is 'ALL'
            if label_name.upper() != "ALL" and label.upper() != "ALL":
                filtered_records.append(record)
            else:
                print(f"Skipping record with labelName/label 'ALL': {record.get('labelName', record.get('label', 'Unknown'))}")
        else:
            filtered_records.append(record)
    
    records = filtered_records
    
    if not records:
        print("No valid records to append after filtering (all records had labelName/label as 'ALL')")
        return

    if not os.path.exists(csv_file):
        print(f"CSV file '{csv_file}' does not exist. Cannot append.")
        return

    with open(csv_file, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []


    with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        for idx, rec in enumerate(records):
            row = {col: rec.get(col, "") for col in fieldnames}

            # Add optional extras only if present in CSV
            if "start_date" in fieldnames and start_date:
                row["start_date"] = start_date
            if "end_date" in fieldnames and end_date:
                row["end_date"] = end_date
            if "errors" in fieldnames and errors:
                row["errors"] = (
                    json.dumps(errors, ensure_ascii=False)
                    if isinstance(errors, (list, dict))
                    else str(errors)
                )

            # bq_result code removed
            if "avg_total_time" in fieldnames and avg_total_time is not None:
                row["avg_total_time"] = avg_total_time
            if "avgApigeeTime" in fieldnames and avgApigeeTime is not None:
                row["avgApigeeTime"] = avgApigeeTime
            if "avgBackendTime" in fieldnames and avgBackendTime is not None:
                row["avgBackendTime"] = avgBackendTime

            writer.writerow(row)
            print(f"Row {idx+1} appended to '{csv_file}' (labelName: {rec.get('labelName', rec.get('label', 'N/A'))}).")

    print(f"Finished appending {len(records)} rows to '{csv_file}' (filtered out 'ALL' labelName records).")

def csv_to_json_file(csv_path: str, json_path: str) -> str:
    """
    Reads data from a CSV file, filters out records where labelName or label is 'ALL',
    and writes the result to a JSON file.
    Returns the path to the created JSON file.
    """
    if not os.path.isfile(csv_path):
        print(f"CSV file '{csv_path}' does not exist.")
        return None

    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)

        # Filter out records where labelName or label is 'ALL'
        filtered = []
        for record in data:
            label_name = record.get("labelName", "")
            label = record.get("label", "")
            if label_name.upper() != "ALL" and label.upper() != "ALL":
                filtered.append(record)

        with open(json_path, 'w', encoding='utf-8') as jf:
            json.dump(filtered, jf, indent=2, ensure_ascii=False, default=str)

        print(f"JSON file created: '{json_path}' with {len(filtered)} records.")
        return json_path
    except Exception as e:
        print(f"Error creating JSON file from CSV: {e}")
        return None
    
def copy_and_clear_csv(csv_path: str, copy_path: str) -> bool:
    """
    Creates a copy of the CSV file at copy_path, then deletes all data from the original CSV (keeps headers).
    Returns True if successful, False otherwise.
    """
    import shutil
    import csv
    import os

    if not os.path.isfile(csv_path):
        print(f"CSV file '{csv_path}' does not exist.")
        return False

    try:
        # Copy the CSV file
        shutil.copy2(csv_path, copy_path)
        print(f"Copied '{csv_path}' to '{copy_path}'.")

        # Read headers from the original CSV
        with open(csv_path, mode='r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            headers = next(reader, None)

        if headers is None:
            print("CSV file has no headers.")
            return False

        # Overwrite the original CSV with only the headers
        with open(csv_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
        print(f"Cleared all data from '{csv_path}', headers retained.")
        return True
    except Exception as e:
        print(f"Error copying and clearing CSV: {e}")
        return False