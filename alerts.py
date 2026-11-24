
import os
from datetime import datetime


class AlertManager:
    def __init__(self, threshold=2, log_file="alerts.log"):
        self.threshold = threshold
        self.log_file = log_file
        self.failure_counts = {}
        self.alerted_checks = set()

    def check_status(self, check_name, status, detail):
        if status == "FAIL":
            self.failure_counts[check_name] = (
                self.failure_counts.get(check_name, 0) + 1
            )

            if (
                self.failure_counts[check_name] >= self.threshold
                and check_name not in self.alerted_checks
            ):
                message = (
                    f"ALERT: {check_name} failed "
                    f"{self.failure_counts[check_name]} times in a row. "
                    f"Details: {detail}"
                )

                self._log(message)
                self.alerted_checks.add(check_name)

        else:
            self.failure_counts[check_name] = 0

            if check_name in self.alerted_checks:
                message = f"RECOVERED: {check_name} is working again."
                self._log(message)
                self.alerted_checks.remove(check_name)

    def _log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] {message}"

        print(entry)

        with open(self.log_file, "a", encoding="utf-8") as file:
            file.write(entry + "\n")
