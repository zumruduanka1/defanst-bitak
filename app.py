from flask import Flask, render_template, request, jsonify
import random
import smtplib
from email.mime.text import MIMEText
import os

app = Flask(__name__)

# =========================
# ⚙️ AYARLAR (.env yerine buraya koyabilirsin)
# =========================
EMAIL = "tubitaktest0@gmail.com"
PASSWORD = "cndmsduniivopskh"   # gmail app password

# =========================
# 🧠 AI ANALİZ (HAFİF MODEL)
# =========================
def analyze_text(text):
    fake_keywords = ["şok", "ifşa", "gizli", "komplo", "acil", "yayılmadan"]
    score = 0

    for k in fake_keywords:
        if k in text.lower():
            score += 20

    score += random.randint(10, 40)

    if score > 100:
        score = 100

    if score > 70:
        label = "Tehlikeli"
    elif score > 40:
        label = "Şüpheli"
    else:
        label = "Güvenli"

    return score, label

# =========================
# 📧 MAIL GÖNDER
# =========================
def send_mail(text, score):
    try:
        msg = MIMEText(f"Riskli içerik bulundu:\n\n{text}\n\nRisk: %{score}")
        msg["Subject"] = "DEFANS ALERT 🚨"
        msg["From"] = EMAIL
        msg["To"] = EMAIL

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print("Mail hatası:", e)

# =========================
# ROUTES
# =========================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    text = data.get("text", "")

    if len(text) < 10:
        return jsonify({"error": "Geçersiz içerik"})

    score, label = analyze_text(text)

    # 🚨 riskliyse mail at
    if score > 70:
        send_mail(text, score)

    return jsonify({
        "score": score,
        "label": label
    })

# =========================
# 📊 SOSYAL MEDYA FEED
# =========================
@app.route("/social")
def social():
    data = [
        {"text":"Gizli belge sızdırıldı!", "risk":85, "platform":"X"},
        {"text":"Yeni karar açıklandı", "risk":25, "platform":"Facebook"},
        {"text":"Büyük ifşa geliyor", "risk":78, "platform":"TikTok"},
        {"text":"Resmi açıklama geldi", "risk":20, "platform":"Instagram"},
    ]
    return jsonify(data)

# =========================
# 📈 DASHBOARD GRAPH
# =========================
@app.route("/stats")
def stats():
    return jsonify({
        "safe": random.randint(1,10),
        "danger": random.randint(1,10)
    })

if __name__ == "__main__":
    app.run()