import os
import requests

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


def check_google_safe(url: str):
    if not GOOGLE_API_KEY:
        return 0  # fallback if no key

    endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={GOOGLE_API_KEY}"

    payload = {
        "client": {
            "clientId": "darknetra",
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }

    try:
        res = requests.post(endpoint, json=payload, timeout=5)

        if res.status_code == 200 and res.json():
            return 1  # malicious
        else:
            return 0  # safe

    except:
        return 0