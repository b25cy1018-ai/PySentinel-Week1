
import requests
import time

url = "https://example.com"

try:
    start_time = time.perf_counter()

    response = requests.get(url, timeout=5)

    end_time = time.perf_counter()

    response_time = (end_time - start_time) * 1000

    print("Website:", url)
    print("Status Code:", response.status_code)
    print("Response Time:", round(response_time, 2), "ms")

    if 200 <= response.status_code < 300:
        print("Status: OK")
    else:
        print("Status: FAIL")

except requests.exceptions.Timeout:
    print("Error: Request timed out")

except requests.exceptions.ConnectionError:
    print("Error: Connection failed")

except requests.exceptions.RequestException as e:
    print("Error:", e)
