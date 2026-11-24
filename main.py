
import json
import os
import sys
import csv
import time
import webbrowser
from datetime import datetime

from alerts import AlertManager
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
            with open(history_file, "r", encoding="utf-8") as file:
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

    with open(history_file, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=2)


def build_checks():
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

    for url in config["sites"]:
        checks.append(
            WebsiteCheck(url)
        )

    return checks


def write_status_html(results):
    last_checked = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rows = ""

    for result in results:
        status = result["status"].lower()

        name = result["name"]
        detail = result["detail"]

        if "url" in result:
            name = f'{name} - {result["url"]}'

        rows += f"""
        <tr>
            <td>{name}</td>
            <td class="{status}">{result["status"]}</td>
            <td>{detail}</td>
            <td>{last_checked}</td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="60">
        <title>PySentinel Status</title>

        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 30px;
                background: #f4f6f8;
            }}

            h1 {{
                color: #243447;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
            }}

            th, td {{
                padding: 12px;
                border: 1px solid #ddd;
                text-align: left;
            }}

            th {{
                background: #243447;
                color: white;
            }}

            .ok {{
                color: green;
                font-weight: bold;
            }}

            .warn {{
                color: orange;
                font-weight: bold;
            }}

            .fail {{
                color: red;
                font-weight: bold;
            }}
        </style>
    </head>

    <body>
        <h1>PySentinel - System & Website Status</h1>

        <p>Last checked: {last_checked}</p>

        <table>
            <tr>
                <th>Check</th>
                <th>Status</th>
                <th>Details</th>
                <th>Last Checked</th>
            </tr>

            {rows}
        </table>
    </body>
    </html>
    """

    with open("status.html", "w", encoding="utf-8") as file:
        file.write(html)


def run_monitoring_round(alert_manager):
    checks = build_checks()
    results = []

    print("\nPySentinel - System & Website Health Report")
    print("--------------------------------------------")
    print("Time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    for check in checks:
        result = check.run()
        results.append(result)

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

        # Use the URL as the identity for individual website alerts.
        check_name = result.get("url", result["name"])

        alert_manager.check_status(
            check_name,
            status,
            result["detail"]
        )

    save_history(results)
    write_status_html(results)

    print("\nResults saved to history.json")
    print("Website results saved to uptime.csv")
    print("Status page updated: status.html")


def watch_mode(interval):
    alert_manager = AlertManager(threshold=2)

    status_path = os.path.abspath("status.html")
    status_url = "file:///" + status_path.replace("\\", "/")

    print("\nStarting PySentinel Watch Mode")
    print(f"Monitoring interval: {interval} seconds")
    print("Press Ctrl+C to stop monitoring.")

    try:
        while True:
            run_monitoring_round(alert_manager)

            # Open the status page only once.
            if not getattr(watch_mode, "browser_opened", False):
                webbrowser.open(status_url)
                watch_mode.browser_opened = True

            print(f"\nNext monitoring round in {interval} seconds.")
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n\nPySentinel monitoring stopped.")
        print("Goodbye!")


def show_summary():
    if not os.path.exists("history.json"):
        print("No history available yet.")
        return

    try:
        with open("history.json", "r", encoding="utf-8") as file:
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

    if len(sys.argv) >= 2 and sys.argv[1] == "watch":
        interval = 60

        if "--every" in sys.argv:
            try:
                index = sys.argv.index("--every")
                interval = int(sys.argv[index + 1])

                if interval <= 0:
                    raise ValueError

            except (ValueError, IndexError):
                print("Invalid interval. Use a positive number of seconds.")
                return

        watch_mode(interval)
        return

    # Normal one-time monitoring mode.
    alert_manager = AlertManager(threshold=2)
    run_monitoring_round(alert_manager)


if __name__ == "__main__":
    os.system("")
    main()
