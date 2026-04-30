from flask import Flask, render_template, request, jsonify
from ai.model import analyze_text
from utils.mailer import send_mail
import random

app = Flask(__name__)
history = []

def social_stream():
    platforms = ["X","Instagram","TikTok","Facebook"]
    texts = [
        "Şok gelişme herkes konuşuyor",
        "Bu gerçek mi?",
        "Büyük skandal ortaya çıktı",
        "Viral video gündem oldu",
        "Gizli belge iddiası"
    ]
    return [{
        "platform":random.choice(platforms),
        "text":random.choice(texts),
        "risk":random.randint(20,90)
    } for _ in range(6)]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    text = request.form.get("text")
    result = analyze_text(text)

    history.append(result)
    send_mail(result)

    return jsonify(result)

@app.route("/stream")
def stream():
    return jsonify(social_stream())

@app.route("/stats")
def stats():
    safe = len([h for h in history if h["label"]=="Güvenli"])
    sus = len([h for h in history if h["label"]=="Şüpheli"])
    danger = len([h for h in history if h["label"]=="Tehlikeli"])
    return jsonify({"safe":safe,"suspicious":sus,"danger":danger})

if __name__ == "__main__":
    app.run()