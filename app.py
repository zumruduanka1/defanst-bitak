from flask import Flask, render_template, request, jsonify
from ai.bert_model import analyze_text
from services.social_api import fetch_twitter

app = Flask(__name__)

history = []

@app.route("/")
def home():
    return render_template("index.html", history=history[-5:])

@app.route("/analyze", methods=["POST"])
def analyze():
    text = request.form.get("text")

    result = analyze_text(text)

    history.append({
        "text": text,
        "risk": result["risk"],
        "label": result["label"]
    })

    return jsonify(result)

@app.route("/stream")
def stream():
    tweets = fetch_twitter()

    data = []
    for t in tweets:
        r = analyze_text(t)
        data.append({
            "text": t,
            "risk": r["risk"]
        })

    return jsonify(data)

if __name__ == "__main__":
    app.run()