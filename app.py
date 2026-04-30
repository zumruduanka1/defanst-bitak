import os
import requests
from flask import Flask, request, jsonify, render_template
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWITTER_BEARER = os.getenv("TWITTER_BEARER")

MAIL_USER = os.getenv("MAIL_USER")
MAIL_PASS = os.getenv("MAIL_PASS")
MAIL_TO = ["mail1@gmail.com", "mail2@gmail.com"]


# 🔥 AI ANALİZ (gerçekçi skor)
def analyze_text(text):
    score = 0

    keywords = ["şok", "ifşa", "gizli", "yayılıyor", "hemen paylaş", "saklanıyor"]
    for k in keywords:
        if k in text.lower():
            score += 15

    if len(text) < 20:
        score += 10

    # OpenAI destek (daha gerçekçi)
    try:
        res = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={
                "model": "gpt-4.1-mini",
                "messages": [
                    {"role": "user", "content": f"Bu metin ne kadar sahte olabilir? 0-100 sayı ver: {text}"}
                ]
            }
        )
        ai_score = int(res.json()["choices"][0]["message"]["content"])
        score = (score + ai_score) // 2
    except:
        pass

    return min(score, 100)


# 📩 MAIL
def send_mail(text, score):
    if score < 50:
        return

    msg = MIMEText(f"⚠️ Riskli içerik bulundu!\n\n{text}\n\nRisk: %{score}")
    msg["Subject"] = "DEFANS ALERT"
    msg["From"] = MAIL_USER

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(MAIL_USER, MAIL_PASS)

    for m in MAIL_TO:
        msg["To"] = m
        server.sendmail(MAIL_USER, m, msg.as_string())

    server.quit()


# 📡 TWITTER DATA
def get_twitter_data():
    url = "https://api.twitter.com/2/tweets/search/recent"
    headers = {"Authorization": f"Bearer {TWITTER_BEARER}"}
    params = {"query": "yalan OR ifşa OR gündem -is:retweet", "max_results": 5}

    res = requests.get(url, headers=headers, params=params)
    data = res.json()

    tweets = []
    for t in data.get("data", []):
        tweets.append({
            "text": t["text"],
            "platform": "X"
        })

    return tweets


# 🔥 ANALİZ API
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    text = data.get("text")

    score = analyze_text(text)

    send_mail(text, score)

    return jsonify({
        "score": score,
        "status": "danger" if score > 50 else "safe"
    })


# 📡 SOSYAL FEED
@app.route("/feed")
def feed():
    return jsonify(get_twitter_data())


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run()