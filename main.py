from flask import Flask, request, jsonify, render_template
from services.twitter_service import fetch_twitter
from services.rss_service import fetch_rss
from model import predict

import threading, time, smtplib, os
from email.mime.text import MIMEText

app = Flask(__name__)

feed = []

# 📧 MAIL
def send_email(text, risk):
    if risk < 60:
        return

    try:
        msg = MIMEText(f"⚠️ Risk %{risk}\n\n{text}")
        msg["Subject"] = "DEFANS ALERT"
        msg["From"] = os.getenv("EMAIL_USER")

        mails = [os.getenv("EMAIL_TO"), os.getenv("EMAIL_TO2")]

        s = smtplib.SMTP("smtp.gmail.com", 587)
        s.starttls()
        s.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))

        for m in mails:
            if m:
                msg["To"] = m
                s.sendmail(os.getenv("EMAIL_USER"), m, msg.as_string())

        s.quit()
    except:
        pass

# 🧠 ANALİZ
def analyze_text(text):
    score = predict(text)
    label = "Şüpheli" if score >= 60 else "Güvenli"
    return score, label

# 🔄 SCAN
def scan():
    global feed

    while True:
        data = fetch_twitter() + fetch_rss()

        new_feed = []

        for item in data:
            text = item["text"]

            risk, label = analyze_text(text)

            new_feed.append({
                "text": text[:120],
                "risk": risk,
                "label": label
            })

            send_email(text, risk)

        feed = new_feed[:20]

        time.sleep(30)

threading.Thread(target=scan, daemon=True).start()

# 🌐 ROUTES
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/feed")
def get_feed():
    return jsonify(feed)

@app.route("/api/analyze", methods=["POST"])
def analyze():
    text = request.json.get("text")

    if not text or len(text) < 10:
        return {"risk": 0, "label": "Yetersiz"}

    risk, label = analyze_text(text)
    return {"risk": risk, "label": label}

if __name__ == "__main__":
    app.run()