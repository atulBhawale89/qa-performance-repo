import time, json, sys
from . import api, utils, csv_writer, BQInsert
from .config import POLL_INTERVAL_SECONDS


def run_scenarios(scenarios, jmx_file_override=None, csv_file_override=None):
     
    for scenario in scenarios:
        # Use override files from CMD if provided, otherwise use scenario files
        jmx_file = (
            jmx_file_override if jmx_file_override else scenario.get("jmx_file_name")
        )
        csv_file = (
            csv_file_override if csv_file_override else scenario.get("csv_file_name")
        )

        result = api.upload_files_to_blazemeter_test(
            scenario["test_id"],
            jmx_file,
            csv_file,
        )

        test_id = scenario.get("test_id") or api.find_test_by_name(
            scenario.get("test_name")
        )
        if not test_id:
            print(f"Test not found: {scenario.get('name')}")
            continue

        api.update_Blazameter_Configur(
            test_id,
            scenario["user_load"],
            scenario["duration"],
            scenario["rampup"],
            scenario["region"],
        )
        session_id, master_id = api.start_test(
            test_id,
            scenario["user_load"],
            scenario["duration"],
            scenario["rampup"],
            scenario["region"],
        )
        if not session_id:
            continue

        session_data = api.wait_for_completion(session_id)
        if not session_data:
            continue

        master_id = master_id or session_data.get("masterId")
        if not master_id:
            continue

        summary = api.fetch_master_summary(master_id)
        if summary:
            # with open(f"summary_{master_id}.json", "w") as f:
            #    json.dump(summary, f, indent=2)
            utz_start_date = utils.ts_to_utc_formatted(summary["summary"][0]["first"])
            utz_end_date = utils.ts_to_utc_formatted(summary["summary"][0]["last"])
            start_date = utils.ts_to_ist_formatted(summary["summary"][0]["first"])
            end_date = utils.ts_to_ist_formatted(summary["summary"][0]["last"])
            print(f"Scenario {scenario['name']} ran from {start_date} to {end_date}")

        stats = api.fetch_request_Statistics(master_id)
        print("data:", stats)
     
        utils.wait(60)
        bq_result=BQInsert.run_bigquery(utz_start_date,utz_end_date)
        print(bq_result)
        avg_total_time=bq_result[0]["AvgTotalTime"]
        avgBackendTime=bq_result[0]["AvgBackendTime"]
        avgApigeeTime=bq_result[0]["AvgApigeeTime"]
        if stats:
            with open(f"request_stats_{master_id}.json", "w") as f:
                json.dump(stats, f, indent=2)
            errors = api.fetch_error_statistics(master_id)
            csv_writer.append_json_to_csv(
                stats, "aggregate_report.csv", start_date, end_date, errors,avg_total_time,avgApigeeTime,avgBackendTime
            )
            csv_writer.csv_to_json_file("aggregate_report.csv","aggregate_report.json")
    
    utils.wait(15)
    utils.insert_json_to_bigquery_and_cleanup("aggregate_report.json","pid-gouscnaiq-omni-res01","TestQAData","Performance_Analytics_Data")
    csv_writer.copy_and_clear_csv("aggregate_report.csv","aggregate_report_Jenkis.csv")
   

def get_cmd_args():
    """Parse command line arguments for JMX and CSV file overrides."""
    jmx_override = sys.argv[1] if len(sys.argv) > 1 else None
    csv_override = sys.argv[2] if len(sys.argv) > 2 else None
    return jmx_override, csv_override
