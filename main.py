from blazemeter.runner import run_scenarios, get_cmd_args
import scenarios

jmx_override, csv_override = get_cmd_args()

if __name__ == "__main__":
    run_scenarios(scenarios.scenarios, jmx_override, csv_override)
