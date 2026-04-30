from flask import Flask, render_template, request, jsonify
import random
import re

app = Flask(__name__)

def is_valid_input(text):
    if not text or len(text.strip()) < 10:
        return False
    return True

def analyze_text(text):
    keywords_fake = ["şok", "ifşa", "gizli", "komplo", "acil", "yayın kaldırılacak"]
    score = 0

    for k in keywords_fake:
        if k in text.lower():
            score += 15

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

@app.route("/social")
def social():
    data = [
        {"text":"Şok gelişme! gizli belge sızdı", "risk":85, "platform":"X"},
        {"text":"Yeni açıklama yapıldı", "risk":20, "platform":"Facebook"},
        {"text":"Büyük ifşa geliyor", "risk":75, "platform":"TikTok"},
        {"text":"Resmi kaynak doğruladı", "risk":30, "platform":"Instagram"}
    ]
    return jsonify(data)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    text = data.get("text", "")

    if not is_valid_input(text):
        return jsonify({"error": "Geçersiz içerik"})

    score, label = analyze_text(text)

    return jsonify({
        "score": score,
        "label": label
    })


@app.route("/social")
def social():
    fake_feed = [
        {"text": "SON DAKİKA! Büyük olay ortaya çıktı!", "risk": 85},
        {"text": "Bilim insanları açıkladı: gerçek veri", "risk": 20},
        {"text": "Gizli belge sızdırıldı!", "risk": 78},
        {"text": "Resmi açıklama geldi", "risk": 30},
    ]
    return jsonify(fake_feed)


if __name__ == "__main__":
    app.run()