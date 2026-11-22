
import os
import shutil
from datetime import datetime


# Convert bytes into readable sizes
def human_size(num_bytes):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} PB"


# Check disk space
def disk_usage(path):
    total, used, free = shutil.disk_usage(path)

    return total, used, free


# Calculate folder size
def folder_size(path):
    total_size = 0

    for root, dirs, files in os.walk(path):
        for name in files:
            try:
                filepath = os.path.join(root, name)
                total_size += os.path.getsize(filepath)
            except (PermissionError, OSError):
                continue

    return total_size


# Find largest files
def largest_files(path, n=5):
    file_list = []

    for root, dirs, files in os.walk(path):
        for name in files:
            try:
                filepath = os.path.join(root, name)
                size = os.path.getsize(filepath)
                file_list.append((size, filepath))
            except (PermissionError, OSError):
                continue

    file_list.sort(reverse=True)
    return file_list[:n]


# Main program
def main():

    print("\n===== PySentinel System Health Snapshot =====")

    path = input("Enter folder path (press Enter for current folder): ")

    if not path.strip():
        path = os.getcwd()

    path = os.path.abspath(os.path.expanduser(path))

    if not os.path.isdir(path):
        print("Error: Folder does not exist. Please try again.")
        return

    total, used, free = disk_usage(path)

    size = folder_size(path)
    biggest = largest_files(path, 5)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    free_percent = (free / total) * 100

    print("\n--- SYSTEM HEALTH REPORT ---")

    print("Date and Time:", timestamp)
    print("Total Disk Space:", human_size(total))
    print("Used Disk Space:", human_size(used))
    print("Free Disk Space:", human_size(free))
    print(f"Free Disk Percentage: {free_percent:.2f}%")

    print("\nFolder:", path)
    print("Folder Size:", human_size(size))

    print("\n--- TOP 5 LARGEST FILES ---")

    for file_size, filepath in biggest:
        print(human_size(file_size), "-", filepath)

    log_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "health_log.txt"
    )

    with open(log_path, "a", encoding="utf-8") as log:
        log.write(
            f"{timestamp} | Free: {free_percent:.2f}% | "
            f"Folder Size: {human_size(size)}\n"
        )

    print("\nReport saved to health_log.txt")
    print("===== Scan Completed Successfully =====")


if __name__ == "__main__":
    main()
