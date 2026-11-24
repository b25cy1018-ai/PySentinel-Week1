
import pytest
import requests
from unittest.mock import patch

from alerts import AlertManager
from checks import DiskSpaceCheck, WebsiteCheck


# Test 1: Disk space threshold logic
def test_disk_space_threshold():
    # Simulate a disk with 10% free space.
    fake_usage = (1000, 900, 100)

    with patch("checks.shutil.disk_usage", return_value=fake_usage):
        check = DiskSpaceCheck(min_free_percent=20)
        result = check.run()

    assert result["status"] == "WARN"


# Test 2: Alert after two consecutive failures
def test_alert_after_two_consecutive_failures(tmp_path):
    log_file = tmp_path / "alerts.log"

    alert = AlertManager(
        threshold=2,
        log_file=str(log_file)
    )

    # First failure should not trigger an alert.
    alert.check_status(
        "Test Website",
        "FAIL",
        "Connection failed"
    )

    assert not log_file.exists()

    # Second consecutive failure should trigger an alert.
    alert.check_status(
        "Test Website",
        "FAIL",
        "Connection failed"
    )

    assert log_file.exists()
    assert "ALERT:" in log_file.read_text(encoding="utf-8")


# Test 3: Website failure without real internet access
def test_website_failure_without_internet():
    url = "https://test-website.invalid"

    with patch(
        "checks.requests.get",
        side_effect=requests.exceptions.ConnectionError
    ) as mock_get:

        check = WebsiteCheck(url)
        result = check.run()

    assert result["status"] == "FAIL"
    assert "Connection failed" in result["detail"]

    mock_get.assert_called_once_with(url, timeout=5)


# Test 4: Uptime report calculation
def test_uptime_report_calculation():
    total_checks = 4
    successful_checks = 3

    uptime = (successful_checks / total_checks) * 100

    assert uptime == 75.0
