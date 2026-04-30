from flask import Flask, render_template, request, jsonify
import random
import re
from datetime import datetime

app = Flask(__name__)

# 🔥 basit ama etkili fake news scoring
FAKE_KEYWORDS = [
    "şok", "ifşa", "gizli", "patladı", "yalan", "komplo",
    "kanıtlandı", "hepsi yalan", "gerçek ortaya çıktı",
    "hükümet saklıyor", "acil paylaş", "yayın silindi"
]

SAFE_KEYWORDS = [
    "resmi açıklama", "kaynak", "doğrulandı",
    "araştırmaya göre", "bilimsel", "rapor"
]

def analyze_text(text):
    if len(text.strip()) < 10:
        return {"error": "Metin çok kısa"}

    text_lower = text.lower()

    risk = 0

    for k in FAKE_KEYWORDS:
        if k in text_lower:
            risk += 15

    for k in SAFE_KEYWORDS:
        if k in text_lower:
            risk -= 10

    # rastgele varyasyon (gerçekçi görünmesi için)
    risk += random.randint(-5, 5)

    risk = max(0, min(100, risk))

    if risk > 70:
        label = "Tehlikeli"
    elif risk > 40:
        label = "Şüpheli"
    else:
        label = "Güvenli"

    return {
        "risk": risk,
        "label": label,
        "time": datetime.now().strftime("%H:%M")
    }

# 🔥 sosyal medya simülasyonu (GERÇEK GİBİ)
def fake_social_feed():
    samples = [
        "SON DAKİKA: Büyük kriz saklanıyor!",
        "Uzmanlara göre ekonomi düzeliyor",
        "ŞOK: Gerçekler ortaya çıktı!",
        "Resmi açıklama yapıldı",
        "Bu haber neden kaldırıldı?"
    ]

    data = []
    for i in range(5):
        txt = random.choice(samples)
        result = analyze_text(txt)
        data.append({
            "text": txt,
            "risk": result["risk"],
            "label": result["label"]
        })

    return data

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    text = request.json.get("text")
    result = analyze_text(text)
    return jsonify(result)

@app.route("/social")
def social():
    return jsonify(fake_social_feed())

if __name__ == "__main__":
    app.run(debug=True)