from flask import Flask, render_template, request, jsonify
import requests, os, smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWITTER_BEARER = os.getenv("TWITTER_BEARER")


# ---------------- AI ANALİZ ----------------
def analyze_text(text):
    if len(text.strip()) < 10:
        return {"risk": 0, "label": "Geçersiz"}

    score = 10
    keywords = ["şok", "acil", "ifşa", "hemen paylaş", "gizli"]

    for k in keywords:
        if k in text.lower():
            score += 20

    # OpenAI destek
    try:
        res = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "user", "content": f"Bu metin fake mi? kısa cevap ver: {text}"}
                ]
            }
        )
        ai = res.json()["choices"][0]["message"]["content"]

        if "fake" in ai.lower():
            score += 30

    except:
        pass

    return {
        "risk": min(score, 100),
        "label": "Şüpheli" if score > 60 else "Güvenli"
    }


# ---------------- NEWS ----------------
def get_news():
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=tr&pageSize=5&apiKey={NEWS_API_KEY}"
        return requests.get(url).json().get("articles", [])
    except:
        return []


# ---------------- TWITTER ----------------
def get_twitter():
    try:
        url = "https://api.twitter.com/2/tweets/search/recent?query=haber&max_results=5"
        headers = {"Authorization": f"Bearer {TWITTER_BEARER}"}
        return requests.get(url, headers=headers).json().get("data", [])
    except:
        return []


# ---------------- MAIL ----------------
def send_mail(email, result):
    try:
        msg = MIMEText(f"Analiz sonucu: {result}")
        msg["Subject"] = "DEFANS ANALİZ"
        msg["From"] = os.getenv("MAIL_USER")
        msg["To"] = email

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(os.getenv("MAIL_USER"), os.getenv("MAIL_PASS"))
        server.send_message(msg)
        server.quit()
    except:
        pass


# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template(
        "index.html",
        news=get_news(),
        tweets=get_twitter()
    )


@app.route("/analyze", methods=["POST"])
def analyze():
    text = request.form.get("text")
    email = request.form.get("email")

    result = analyze_text(text)

    if email:
        send_mail(email, result)

    return jsonify(result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)