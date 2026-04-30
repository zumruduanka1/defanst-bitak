from flask import Flask, request, jsonify, render_template
from ai.model import analyze
from ai.image import analyze_image
import pandas as pd
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def api():
    text = request.form.get("text")
    image = request.form.get("image")

    if image:
        res = analyze_image(image)
    else:
        res = analyze(text)

    return jsonify(res)

# 🔥 FEEDBACK (öğrenme)
@app.route("/feedback", methods=["POST"])
def feedback():
    text = request.form.get("text")
    label = request.form.get("label")

    df = pd.DataFrame([[text,int(label)]], columns=["text","label"])

    if os.path.exists("data/feedback.csv"):
        df.to_csv("data/feedback.csv", mode="a", header=False, index=False)
    else:
        df.to_csv("data/feedback.csv", index=False)

    return jsonify({"status":"kaydedildi"})

if __name__ == "__main__":
    app.run()