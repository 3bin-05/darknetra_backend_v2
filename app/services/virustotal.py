import os
import requests

VT_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")


def check_virustotal(url: str):
    if not VT_API_KEY:
        return 0

    headers = {
        "x-apikey": VT_API_KEY
    }

    try:
        # Step 1: Submit URL
        res = requests.post(
            "https://www.virustotal.com/api/v3/urls",
            headers=headers,
            data={"url": url},
            timeout=5
        )

        if res.status_code != 200:
            return 0

        url_id = res.json()["data"]["id"]

        # Step 2: Get report
        report = requests.get(
            f"https://www.virustotal.com/api/v3/analyses/{url_id}",
            headers=headers,
            timeout=5
        )

        stats = report.json()["data"]["attributes"]["stats"]

        malicious = stats.get("malicious", 0)

        # Normalize score (0–1)
        return min(malicious / 10, 1)

    except:
        return 0