import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from google.cloud import bigquery
from google.auth import default
from .config import APIPROXY_NAME, REQUEST_PATH, PROJECT_ID, DATASET, TABLE


def run_bigquery(utz_start_date, utz_end_date):
    """
    Connects to BigQuery using Application Default Credentials,
    runs the query, and returns results as JSON.
    """
    QUERY = f"""
SELECT
  AVG(jsonPayload.time_totalExectionTime_millies) AS AvgTotalTime,
  AVG(jsonPayload.time_totalTargetNetworkLatency_millies) AS AvgNWLatency,
  AVG(jsonPayload.time_totalTargetTime_millies) AS AvgBackendTime,
  AVG(jsonPayload.time_apigeeRequestBeforeTargetTime_millies)+AVG(jsonPayload.time_apigeeResponseAfterTargetTime_millies) AS AvgApigeeTime,
  COUNT(*) AS TotalAPIRequests
FROM `{PROJECT_ID}.{DATASET}.{TABLE}`
WHERE
  jsonPayload.what_apiproxy_name = 'ucp-loyalty-orders-v1'
  AND jsonPayload.what_request_path= "/realtime-transactions-v2/accounts/MMA_873434cd2f38417caf97c50723d8cc25/merchants/MER_1e4049f6f33145b2a5891332e9783bd9/realTimeTransaction/LOR_5415767"
  AND jsonPayload.time_apigeeInTime> '{utz_start_date}'
  AND jsonPayload.time_apigeeInTime< '{utz_end_date}'
"""

    try:

        credentials, _ = default()
        client = bigquery.Client(credentials=credentials, project=PROJECT_ID)

        print(f"Running query against project: {PROJECT_ID}")
        print(QUERY)
        query_job = client.query(QUERY)

        results = query_job.result()
        rows = [dict(row) for row in results]
        #json_results = json.dumps(rows, indent=2, default=str)
        #print("Result", json_results)
        return rows
    except Exception as e:
        print(f"Error running BigQuery: {e}")
        return None
