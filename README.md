
# PySentinel – Automated System & Website Monitor

PySentinel is a Python-based monitoring project that tracks system health and website availability. It uses object-oriented programming, configurable monitoring thresholds, HTTP requests, and CSV/JSON reporting.

## Week 1 – System Health Snapshot

### Features
- Checks total, used, and free disk space.
- Calculates folder sizes.
- Finds the top 5 largest files.
- Displays readable file sizes.
- Saves health reports to a log file.

### Run
```bash
python monitor.py
```

## Week 2 – Configurable System Monitor

### Features
- Uses an object-oriented `Check` base class.
- Includes `DiskSpaceCheck`, `FolderSizeCheck`, and `LargeFileCheck`.
- Loads monitoring thresholds from `config.json`.
- Reports OK, WARN, and FAIL statuses.
- Displays coloured terminal output.
- Saves monitoring results in `history.json`.
- Retains the latest 50 monitoring runs.
- Provides a failure summary using `--summary`.

### Run
```bash
python main.py
```

### View Failure Summary
```bash
python main.py --summary
```

## Week 3 – Automated Website Monitoring & Uptime Reports

### Features
- Monitors multiple websites using the `requests` library.
- Checks HTTP response status codes.
- Measures website response time in milliseconds.
- Detects slow website responses.
- Handles connection errors and request timeouts.
- Records website monitoring results in `uptime.csv`.
- Calculates website uptime percentages.
- Calculates average website response times.
- Displays website uptime reports.
- Continues monitoring even when a website fails.

### Website Configuration

Websites are configured in `config.json` using the `sites` list.

### View Website Uptime Report
```bash
python main.py --report
```

### Run Complete Monitoring
```bash
python main.py
```

### View Failure Summary
```bash
python main.py --summary
```

## Project Files

- `monitor.py` – Week 1 system health monitor.
- `health_log.txt` – Week 1 health report log.
- `checks.py` – Monitoring classes for system and website checks.
- `config.py` – Loads configuration settings.
- `config.json` – Stores monitoring thresholds and website URLs.
- `main.py` – Runs monitoring checks and generates reports.
- `history.json` – Stores the latest 50 monitoring runs.
- `uptime.csv` – Stores website uptime and response-time records.
- `requirements.txt` – Lists required Python packages.

## Technologies Used

- Python
- Requests
- CSV
- JSON
- os
- shutil
- datetime
- time
- Object-Oriented Programming

## Learning Journey

**Week 1:** System Health Snapshot

**Week 2:** Configurable System Monitor

**Week 3:** Automated Website Monitoring & Uptime Reports
