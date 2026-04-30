from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWITTER_BEARER = os.getenv("TWITTER_BEARER")


# ------------------------
# AI ANALİZ (HAFİF + AKILLI)
# ------------------------
def analyze_text(text):
    if len(text.strip()) < 10:
        return {"risk": 0, "label": "Geçersiz"}

    suspicious_words = [
        "şok", "acil", "hemen paylaş", "gizli", "ifşa",
        "büyük oyun", "medya saklıyor", "gerçek bu"
    ]

    score = 10

    for w in suspicious_words:
        if w in text.lower():
            score += 15

    # OpenAI destekli analiz (opsiyonel)
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }

        res = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "Bu metin fake news mi analiz et. 0-100 risk ver."},
                    {"role": "user", "content": text}
                ]
            }
        )

        data = res.json()
        ai_text = data["choices"][0]["message"]["content"]

        if "yüksek" in ai_text.lower():
            score += 30

    except:
        pass

    label = "Şüpheli" if score > 60 else "Güvenli"

    return {"risk": min(score, 100), "label": label}


# ------------------------
# NEWS API
# ------------------------
def get_news():
    url = f"https://newsapi.org/v2/top-headlines?country=tr&pageSize=5&apiKey={NEWS_API_KEY}"
    try:
        res = requests.get(url).json()
        return res.get("articles", [])
    except:
        return []


# ------------------------
# TWITTER (X) TREND
# ------------------------
def get_twitter():
    url = "https://api.twitter.com/2/tweets/search/recent?query=haber&max_results=5"

    headers = {
        "Authorization": f"Bearer {TWITTER_BEARER}"
    }

    try:
        res = requests.get(url, headers=headers).json()
        return res.get("data", [])
    except:
        return []


# ------------------------
# ROUTES
# ------------------------
@app.route("/")
def home():
    news = get_news()
    tweets = get_twitter()
    return render_template("index.html", news=news, tweets=tweets)


@app.route("/analyze", methods=["POST"])
def analyze():
    text = request.form.get("text", "")
    result = analyze_text(text)
    return jsonify(result)


# ------------------------
# RUN
# ------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)