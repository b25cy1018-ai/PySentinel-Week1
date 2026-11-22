
import json
import os
import sys
from datetime import datetime

from config import load_config
from checks import DiskSpaceCheck, FolderSizeCheck, LargeFileCheck


GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"


def save_history(results):
    history_file = "history.json"

    if os.path.exists(history_file):
        try:
            with open(history_file, "r") as file:
                history = json.load(file)
        except (json.JSONDecodeError, OSError):
            history = []
    else:
        history = []

    history.append({
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "results": results
    })

    history = history[-50:]

    with open(history_file, "w") as file:
        json.dump(history, file, indent=2)


def show_summary():
    if not os.path.exists("history.json"):
        print("No history available yet.")
        return

    try:
        with open("history.json", "r") as file:
            history = json.load(file)
    except (json.JSONDecodeError, OSError):
        print("History file is invalid or cannot be read.")
        return

    failure_counts = {}

    for run in history:
        for result in run["results"]:
            name = result["name"]
            failure_counts.setdefault(name, 0)

            if result["status"] == "FAIL":
                failure_counts[name] += 1

    print("\nFailure Summary")
    print("----------------")

    for name, count in failure_counts.items():
        print(f"{name}: {count} failures")


def main():
    if "--summary" in sys.argv:
        show_summary()
        return

    config = load_config()

    checks = [
        DiskSpaceCheck(config["min_free_percent"])
    ]

    for folder in config["folders_to_watch"]:
        checks.append(
            FolderSizeCheck(folder, config["max_folder_mb"])
        )
        checks.append(
            LargeFileCheck(folder, config["max_file_mb"])
        )

    results = []

    print("\nPySentinel - System Health Report")
    print("----------------------------------")

    for check in checks:
        result = check.run()
        results.append(result)

        status = result["status"]

        if status == "OK":
            color = GREEN
        elif status == "WARN":
            color = YELLOW
        else:
            color = RED

        print(
            f'{color}[{status}]{RESET} '
            f'{result["name"]}: {result["detail"]}'
        )

    save_history(results)
    print("\nResults saved to history.json")


if __name__ == "__main__":
    os.system("")
    main()
