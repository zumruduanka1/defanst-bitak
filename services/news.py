import requests
import os

def get_news():
    url = f"https://newsapi.org/v2/top-headlines?country=tr&apiKey={os.getenv('NEWS_API_KEY')}"
    data = requests.get(url).json()

    return [a["title"] for a in data.get("articles", [])[:5]]