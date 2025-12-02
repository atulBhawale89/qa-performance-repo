#!/usr/bin/env python3
"""
Test script to demonstrate the filtering functionality in append_json_to_csv
Shows how records with labelName or label as 'ALL' are filtered out
"""

import json
import os
import csv
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

from blazemeter.csv_writer import append_json_to_csv

def create_test_csv():
    """Create a test CSV file with headers"""
    csv_file = "test_filter_report.csv"
    headers = ["labelName", "label", "samples", "avg", "min", "max", "error", "throughput", "start_date", "end_date", "errors"]
    
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
    
    print(f"Created test CSV file: {csv_file}")
    return csv_file

def test_filtering():
    """Test the filtering functionality"""
    
    # Sample data with some records having labelName or label as 'ALL'
    test_data = {
        "result": [
            {
                "labelName": "Login Request",
                "samples": 100,
                "avg": 250.5,
                "min": 120,
                "max": 800,
                "error": 0.02,
                "throughput": 25.3
            },
            {
                "labelName": "ALL",  # This should be filtered out
                "samples": 500,
                "avg": 300.2,
                "min": 100,
                "max": 1200,
                "error": 0.03,
                "throughput": 45.7
            },
            {
                "label": "API Call",
                "samples": 150,
                "avg": 180.3,
                "min": 90,
                "max": 650,
                "error": 0.01,
                "throughput": 35.7
            },
            {
                "label": "all",  # This should be filtered out (case insensitive)
                "samples": 300,
                "avg": 200.1,
                "min": 50,
                "max": 900,
                "error": 0.015,
                "throughput": 40.2
            },
            {
                "labelName": "Search Request",
                "samples": 200,
                "avg": 320.7,
                "min": 150,
                "max": 950,
                "error": 0.025,
                "throughput": 30.8
            }
        ]
    }
    
    print("Testing append_json_to_csv with filtering...")
    print("=" * 60)
    
    # Create test CSV file
    csv_file = create_test_csv()
    
    # Test dates and errors
    start_date = "2025-11-12T10:30:00Z"
    end_date = "2025-11-12T10:32:00Z"
    errors = [{"error": "Connection timeout", "count": 2}]
    
    print(f"\nOriginal data has {len(test_data['result'])} records:")
    for i, record in enumerate(test_data['result'], 1):
        label_name = record.get('labelName', record.get('label', 'N/A'))
        print(f"  {i}. labelName/label: '{label_name}'")
    
    print(f"\nCalling append_json_to_csv...")
    print("-" * 40)
    
    # Call the function
    append_json_to_csv(test_data, csv_file, start_date, end_date, errors)
    
    print("-" * 40)
    
    # Read the CSV file to verify results
    print(f"\nReading CSV file to verify filtering:")
    with open(csv_file, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"CSV file contains {len(rows)} data rows (excluding header):")
    for i, row in enumerate(rows, 1):
        label_name = row.get('labelName', row.get('label', 'N/A'))
        samples = row.get('samples', 'N/A')
        print(f"  {i}. labelName/label: '{label_name}', samples: {samples}")
    
    # Verify filtering worked correctly
    expected_rows = 3  # Should have 3 rows after filtering out 2 'ALL' records
    if len(rows) == expected_rows:
        print(f"\n✓ Filtering worked correctly! {expected_rows} rows in CSV (2 'ALL' records filtered out)")
    else:
        print(f"\n✗ Filtering issue: Expected {expected_rows} rows, got {len(rows)}")
    
    # Clean up test file
    if os.path.exists(csv_file):
        os.remove(csv_file)
        print(f"\n✓ Test file cleaned up: {csv_file}")
    
    print("=" * 60)
    print("Test completed!")

def test_edge_cases():
    """Test edge cases for the filtering"""
    print("\nTesting edge cases...")
    print("-" * 30)
    
    # Test with all records having 'ALL' as labelName
    all_filtered_data = {
        "result": [
            {"labelName": "ALL", "samples": 100},
            {"label": "all", "samples": 200}, 
            {"labelName": "All", "samples": 300}
        ]
    }
    
    csv_file = create_test_csv()
    print("Testing data where all records should be filtered out...")
    
    append_json_to_csv(all_filtered_data, csv_file, None, None, None)
    
    # Verify no data rows were added (only header should exist)
    with open(csv_file, "r") as f:
        lines = f.readlines()
    
    if len(lines) == 1:  # Only header
        print("✓ All records correctly filtered out")
    else:
        print(f"✗ Expected only header, got {len(lines)} lines")
    
    os.remove(csv_file)
    print("✓ Edge case test completed")

if __name__ == "__main__":
    test_filtering()
    test_edge_cases()
