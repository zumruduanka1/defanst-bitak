from flask import Flask, render_template, request, jsonify
from ai.model import analyze_text
from ai.image import analyze_image
from utils.preprocess import clean
from utils.mailer import send_mail
import random

app = Flask(__name__)

history = []

def fake_social_feed():
    samples = [
        "X: Deprem olacak iddiası yayılıyor!",
        "Instagram: Ünlü isim öldü söylentisi",
        "TikTok: Gizli belge ifşa edildi",
        "Facebook: Aşı zararlı mı tartışması",
        "X: Ekonomi çöktü iddiası",
        "Instagram: Şok görüntüler paylaşıldı"
    ]
    return [{"text": random.choice(samples), "risk": random.randint(10,90)} for _ in range(6)]

@app.route("/")
def home():
    return render_template("index.html", feed=fake_social_feed(), history=history)

@app.route("/analyze", methods=["POST"])
def analyze():
    text = request.form.get("text")
    email = request.form.get("email")

    if not text:
        return jsonify({"error": "Boş veri"})

    text = clean(text)
    result = analyze_text(text)

    history.insert(0, {
        "text": text[:50],
        "risk": result["risk"],
        "label": result["label"]
    })

    if email:
        send_mail(email, result)

    return jsonify(result)

if __name__ == "__main__":
    app.run()