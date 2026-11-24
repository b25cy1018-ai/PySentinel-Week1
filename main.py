
import json
import os
import sys
import csv
from datetime import datetime

from config import load_config
from checks import (
    DiskSpaceCheck,
    FolderSizeCheck,
    LargeFileCheck,
    WebsiteCheck
)


GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"


def save_uptime(result):
    uptime_file = "uptime.csv"

    file_exists = (
        os.path.exists(uptime_file)
        and os.path.getsize(uptime_file) > 0
    )

    with open(uptime_file, "a", newline="", encoding="utf-8") as file:
        fieldnames = [
            "timestamp",
            "url",
            "status_code",
            "response_ms",
            "status"
        ]

        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "url": result["url"],
            "status_code": result["status_code"],
            "response_ms": result["response_ms"],
            "status": result["status"]
        })


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


def show_uptime_report():
    uptime_file = "uptime.csv"

    if not os.path.exists(uptime_file):
        print("No website history available yet.")
        return

    website_data = {}

    try:
        with open(uptime_file, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                url = row["url"]

                if url not in website_data:
                    website_data[url] = {
                        "total": 0,
                        "successful": 0,
                        "response_times": []
                    }

                website_data[url]["total"] += 1

                # Both OK and WARN mean the website responded successfully.
                if row["status"] in ("OK", "WARN"):
                    website_data[url]["successful"] += 1

                if row["response_ms"]:
                    website_data[url]["response_times"].append(
                        float(row["response_ms"])
                    )

    except (OSError, csv.Error, KeyError, ValueError):
        print("Unable to read uptime.csv. Please check the file.")
        return

    if not website_data:
        print("No website records found.")
        return

    print("\nWebsite Uptime Report")
    print("---------------------")

    for url, data in website_data.items():
        total = data["total"]
        successful = data["successful"]

        uptime = (successful / total) * 100

        times = data["response_times"]

        if times:
            average_time = sum(times) / len(times)
            average_text = f"{average_time:.2f} ms"
        else:
            average_text = "N/A"

        print(f"\nWebsite: {url}")
        print(f"Total Checks: {total}")
        print(f"Successful Checks: {successful}")
        print(f"Uptime: {uptime:.2f}%")
        print(f"Average Response Time: {average_text}")


def main():
    if "--summary" in sys.argv:
        show_summary()
        return

    if "--report" in sys.argv:
        show_uptime_report()
        return

    config = load_config()

    checks = [
        DiskSpaceCheck(config["min_free_percent"])
    ]

    # System monitoring checks
    for folder in config["folders_to_watch"]:
        checks.append(
            FolderSizeCheck(folder, config["max_folder_mb"])
        )

        checks.append(
            LargeFileCheck(folder, config["max_file_mb"])
        )

    # Website monitoring checks
    for url in config["sites"]:
        checks.append(
            WebsiteCheck(url)
        )

    results = []

    print("\nPySentinel - System & Website Health Report")
    print("--------------------------------------------")

    for check in checks:
        result = check.run()
        results.append(result)

        # Save website results to CSV
        if "url" in result:
            save_uptime(result)

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
    print("Website results saved to uptime.csv")


if __name__ == "__main__":
    os.system("")
    main()
