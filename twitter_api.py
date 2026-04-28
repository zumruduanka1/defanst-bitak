import requests, os

BEARER = os.getenv("TWITTER_BEARER")

def get_tweets():
    try:
        url = "https://api.twitter.com/2/tweets/search/recent"

        headers = {
            "Authorization": f"Bearer {BEARER}"
        }

        params = {
            "query": "gündem OR iddia OR şok lang:tr -is:retweet",
            "max_results": 10
        }

        r = requests.get(url, headers=headers, params=params, timeout=5)
        data = r.json()

        tweets = []

        if "data" in data:
            for t in data["data"]:
                tweets.append({
                    "text": t["text"],
                    "source": "twitter"
                })

        return tweets

    except:
        return []