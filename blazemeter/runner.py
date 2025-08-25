import time, json
from . import api, utils, csv_writer
from .config import POLL_INTERVAL_SECONDS


def run_scenarios(scenarios):
    for scenario in scenarios:
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
            #with open(f"summary_{master_id}.json", "w") as f:
            #    json.dump(summary, f, indent=2)
            start_date = utils.ts_to_ist_formatted(summary["summary"][0]["first"])
            end_date = utils.ts_to_ist_formatted(summary["summary"][0]["last"])
            print(f"Scenario {scenario['name']} ran from {start_date} to {end_date}")

        stats = api.fetch_request_Statistics(master_id)
        print("data:", stats)

        if stats:
            with open(f"request_stats_{master_id}.json", "w") as f:
                json.dump(stats, f, indent=2)
            errors = api.fetch_error_statistics(master_id)
            csv_writer.append_json_to_csv(
                stats, "aggregate_report.csv", start_date, end_date, errors[0]
            )
