import requests, os

def fetch_twitter():
    bearer = os.getenv("TWITTER_BEARER")

    if not bearer:
        return []

    url = "https://api.twitter.com/2/tweets/search/recent"

    headers = {
        "Authorization": f"Bearer {bearer}"
    }

    params = {
        "query": '(gündem OR iddia OR şok OR komplo) lang:tr -is:retweet',
        "max_results": 10
    }

    try:
        r = requests.get(url, headers=headers, params=params, timeout=5)
        data = r.json()

        tweets = []
        for t in data.get("data", []):
            tweets.append({"text": t["text"]})

        return tweets

    except:
        return []