from flask import Flask, render_template, request, jsonify
from ai.text_model import analyze_text
from ai.image_model import analyze_image
from services.news import get_news
from services.social import get_social

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    text = data.get("text")

    result = analyze_text(text)
    return jsonify(result)

@app.route("/feed")
def feed():
    return jsonify({
        "news": get_news(),
        "social": get_social()
    })

if __name__ == "__main__":
    app.run()