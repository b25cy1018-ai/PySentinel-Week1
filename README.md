# PySentinel – System Health Monitor

PySentinel is a Python-based system monitoring project developed in two stages. It monitors system health using Python's standard library and object-oriented programming.

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
- Displays results with coloured terminal output.
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

## Project Files

- `monitor.py` – Week 1 system health monitor.
- `health_log.txt` – Week 1 health report log.
- `checks.py` – Week 2 monitoring classes.
- `config.py` – Loads configuration settings.
- `config.json` – Monitoring thresholds.
- `main.py` – Runs monitoring checks and saves history.
- `history.json` – Stores the latest 50 runs.

## Technologies Used

- Python
- JSON
- os
- shutil
- datetime
- Object-Oriented Programming

## Learning Journey

**Week 1:** System Health Snapshot

**Week 2:** Configurable System Monitor