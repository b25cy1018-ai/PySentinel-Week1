import os
import shutil
import time
import requests


class Check:
    def __init__(self, name):
        self.name = name

    def run(self):
        raise NotImplementedError("Subclasses must implement run()")

    def result(self, status, detail):
        return {
            "name": self.name,
            "status": status,
            "detail": detail
        }


class DiskSpaceCheck(Check):
    def __init__(self, min_free_percent):
        super().__init__("Disk Space")
        self.min_free_percent = min_free_percent

    def run(self):
        total, used, free = shutil.disk_usage(os.path.abspath("."))
        free_percent = (free / total) * 100

        if free_percent < self.min_free_percent:
            status = "FAIL" if free_percent < self.min_free_percent / 2 else "WARN"
        else:
            status = "OK"

        detail = f"Free space: {free_percent:.2f}%"
        return self.result(status, detail)


class FolderSizeCheck(Check):
    def __init__(self, folder, max_folder_mb):
        super().__init__("Folder Size")
        self.folder = folder
        self.max_folder_mb = max_folder_mb

    def run(self):
        if not os.path.isdir(self.folder):
            return self.result("FAIL", "Folder does not exist")

        total_size = 0

        for root, dirs, files in os.walk(self.folder):
            for file in files:
                path = os.path.join(root, file)
                try:
                    total_size += os.path.getsize(path)
                except OSError:
                    continue

        size_mb = total_size / (1024 * 1024)

        if size_mb > self.max_folder_mb:
            status = "WARN"
        else:
            status = "OK"

        return self.result(status, f"Folder size: {size_mb:.2f} MB")


class LargeFileCheck(Check):
    def __init__(self, folder, max_file_mb):
        super().__init__("Large Files")
        self.folder = folder
        self.max_file_mb = max_file_mb

    def run(self):
        if not os.path.isdir(self.folder):
            return self.result("FAIL", "Folder does not exist")

        largest_size = 0
        largest_path = None

        for root, dirs, files in os.walk(self.folder):
            for file in files:
                path = os.path.join(root, file)
                try:
                    size = os.path.getsize(path)
                    if size > largest_size:
                        largest_size = size
                        largest_path = path
                except OSError:
                    continue

        size_mb = largest_size / (1024 * 1024)

        if size_mb > self.max_file_mb:
            status = "WARN"
        else:
            status = "OK"

        detail = (
            f"Largest file: {largest_path} ({size_mb:.2f} MB)"
            if largest_path else "No files found"
        )

        return self.result(status, detail)

class WebsiteCheck(Check):
    def __init__(self, url, timeout=5, slow_threshold=2.0):
        super().__init__("Website Uptime")
        self.url = url
        self.timeout = timeout
        self.slow_threshold = slow_threshold

    def run(self):
        start_time = time.perf_counter()
        status_code = None

        try:
            response = requests.get(
                self.url,
                timeout=self.timeout
            )

            status_code = response.status_code

            response_ms = (
                time.perf_counter() - start_time
            ) * 1000

            if not 200 <= status_code < 300:
                status = "FAIL"
                detail = f"HTTP error: {status_code}"

            elif response_ms > self.slow_threshold * 1000:
                status = "WARN"
                detail = f"Slow response: {response_ms:.2f} ms"

            else:
                status = "OK"
                detail = f"Response time: {response_ms:.2f} ms"

        except requests.exceptions.Timeout:
            response_ms = (time.perf_counter() - start_time) * 1000
            status = "FAIL"
            detail = f"Request timed out after {self.timeout} seconds"

        except requests.exceptions.ConnectionError:
            response_ms = (time.perf_counter() - start_time) * 1000
            status = "FAIL"
            detail = "Connection failed: website unreachable"

        except requests.exceptions.RequestException as e:
            response_ms = (time.perf_counter() - start_time) * 1000
            status = "FAIL"
            detail = f"Request error: {e}"

        result = self.result(status, detail)

        result.update({
            "url": self.url,
            "status_code": status_code,
            "response_ms": round(response_ms, 2)
        })

        return result
