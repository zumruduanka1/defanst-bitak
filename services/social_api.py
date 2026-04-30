import requests
import os

def fetch_twitter():
    token = os.getenv("X_BEARER_TOKEN")

    headers = {"Authorization": f"Bearer {token}"}

    url = "https://api.twitter.com/2/tweets/search/recent?query=haber&max_results=10"

    try:
        res = requests.get(url, headers=headers).json()
        data = []

        for t in res.get("data", []):
            data.append(t["text"])

        return data
    except:
        return []