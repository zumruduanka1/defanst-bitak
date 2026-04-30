from flask import Flask, render_template, request, jsonify
import random, requests, smtplib, os
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
TWITTER_BEARER = os.getenv("TWITTER_BEARER")

# ================= MAIL =================
def send_mail(text, score):
    try:
        receivers = [EMAIL, "rumeyysauslu@gmail.com"]

        msg = MIMEText(f"""
🚨 DEFANS AI ALERT

İçerik:
{text}

Risk: %{score}
""")

        msg["Subject"] = "DEFANS UYARI"
        msg["From"] = EMAIL
        msg["To"] = ", ".join(receivers)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, receivers, msg.as_string())
        server.quit()

        print("MAIL GİTTİ")

    except Exception as e:
        print("MAIL HATA:", e)

# ================= AI =================
def analyze_text(text):
    score = 0
    keywords = ["şok","ifşa","gizli","komplo","acil","yayılmadan"]

    for k in keywords:
        if k in text.lower():
            score += 20

    score += random.randint(10, 40)
    return min(score, 100)

# ================= ROUTES =================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    text = request.json.get("text","")
    score = analyze_text(text)

    if score >= 50:
        send_mail(text, score)

    return jsonify({"score": score})

# ================= TWITTER =================
@app.route("/twitter")
def twitter():

    url = "https://api.twitter.com/2/tweets/search/recent"

    headers = {
        "Authorization": f"Bearer {TWITTER_BEARER}"
    }

    params = {
        "query": "haber OR gündem -is:retweet lang:tr",
        "max_results": 10
    }

    try:
        r = requests.get(url, headers=headers, params=params, timeout=5)
        data = r.json()

        result = []

        for t in data.get("data", []):
            text = t["text"]
            score = analyze_text(text)

            if score >= 50:
                send_mail(text, score)

            result.append({
                "text": text,
                "risk": score,
                "platform": "X"
            })

        return jsonify(result)

    except Exception as e:
        print("TWITTER HATA:", e)
        return jsonify([])

if __name__ == "__main__":
    app.run()