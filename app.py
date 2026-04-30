import os
import re
import requests
from flask import Flask, request, jsonify, render_template
from transformers import pipeline
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

# =========================
# 🔥 MODEL (LIGHT VERSION)
# =========================
print("Model yükleniyor...")
nlp = pipeline(
    "text-classification",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)
print("Model hazır!")

# =========================
# 🔥 ENV (MAIL)
# =========================
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# =========================
# 🔥 YARDIMCI FONKSİYONLAR
# =========================

def is_valid_input(text):
    if not text:
        return False
    if len(text.strip()) < 10:
        return False
    if re.fullmatch(r"[0-9\s]+", text):
        return False
    return True


def extract_text_from_url(url):
    try:
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")
        paragraphs = [p.get_text() for p in soup.find_all("p")]
        return " ".join(paragraphs)[:2000]
    except:
        return ""


def analyze_text(text):
    result = nlp(text[:512])[0]

    score = result["score"]
    label = result["label"]

    # Risk hesaplama (custom)
    risk = int(score * 100)

    # Fake news heuristics
    keywords = ["şok", "acil", "son dakika", "bomba", "gizli"]
    if any(k in text.lower() for k in keywords):
        risk += 15

    risk = min(risk, 100)

    if risk > 70:
        status = "Tehlikeli"
    elif risk > 40:
        status = "Şüpheli"
    else:
        status = "Güvenli"

    return {
        "risk": risk,
        "label": label,
        "status": status
    }


def analyze_image(url):
    try:
        r = requests.get(url)
        img = Image.open(BytesIO(r.content))

        # Basit fake image heuristic
        width, height = img.size
        ratio = width / height

        if ratio > 3 or ratio < 0.3:
            risk = 70
        else:
            risk = 30

        return {
            "risk": risk,
            "status": "Şüpheli" if risk > 50 else "Güvenli"
        }
    except:
        return {"risk": 50, "status": "Bilinmiyor"}


def send_mail(to_email, content):
    if not EMAIL_USER or not EMAIL_PASS:
        return

    msg = MIMEText(content)
    msg["Subject"] = "DEFANS ANALİZ SONUCU"
    msg["From"] = EMAIL_USER
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
    except:
        pass


# =========================
# 🔥 ROUTES
# =========================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json

    text = data.get("text")
    url = data.get("url")
    image = data.get("image")
    email = data.get("email")

    final_text = ""

    # URL varsa çek
    if url:
        final_text = extract_text_from_url(url)

    # Text varsa override
    if text:
        final_text = text

    if not is_valid_input(final_text) and not image:
        return jsonify({
            "error": "Geçerli içerik gir"
        }), 400

    result = {}

    if final_text:
        result = analyze_text(final_text)

    if image:
        img_result = analyze_image(image)
        result["image"] = img_result

    # MAIL GÖNDER
    if email:
        send_mail(email, str(result))

    return jsonify(result)


# =========================
# 🔥 RUN
# =========================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)