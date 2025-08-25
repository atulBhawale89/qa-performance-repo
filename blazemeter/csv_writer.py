from typing import Union, Dict, Any, List
import os
import csv
import json


def _load_json(json_data_or_path: Union[Dict[str, Any], str]) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """Helper to load JSON data from dict or file path."""
    #print("data:", json_data_or_path)
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
) -> None:
    """
    Appends rows from JSON into an existing CSV (one row per item in 'result' list if present).
    """
    data = _load_json(json_data_or_path)

    # Ensure data is iterable
    if isinstance(data, dict) and "result" in data and isinstance(data["result"], list):
        records = data["result"]
    elif isinstance(data, list):
        records = data
    else:
        records = [data]  # wrap single dict into list

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

            writer.writerow(row)
            print(f"Row {idx+1} appended to '{csv_file}'.")

    print(f"Finished appending {len(records)} rows to '{csv_file}'.")
