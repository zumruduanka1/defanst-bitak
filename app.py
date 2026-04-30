from flask import Flask, render_template, request, jsonify
import requests, random, os, smtplib, feedparser
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

MAIL_USER = os.getenv("MAIL_USER")
MAIL_PASS = os.getenv("MAIL_PASS")

# ---------------- ANALİZ ----------------
def analyze_text(text):
    if not text or len(text.strip()) < 15:
        return {"risk": 0, "label": "Geçersiz"}

    score = 20

    keywords = [
        "şok", "ifşa", "gizli", "hemen paylaş",
        "kanıtlandı", "skandal", "yasaklandı"
    ]

    for k in keywords:
        if k in text.lower():
            score += 15

    if "!" in text:
        score += 10

    if len(text) < 50:
        score += 10

    score = min(score, 100)

    label = "Şüpheli" if score > 60 else "Güvenli"

    return {"risk": score, "label": label}


# ---------------- MAIL ----------------
def send_mail(text, result):
    try:
        msg = MIMEText(f"""
Risk: {result['risk']}%
Durum: {result['label']}

İçerik:
{text}
""")
        msg["Subject"] = "🚨 DEFANS RİSK TESPİTİ"
        msg["From"] = MAIL_USER
        msg["To"] = MAIL_USER

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(MAIL_USER, MAIL_PASS)
        server.send_message(msg)
        server.quit()
    except:
        pass


# ---------------- SOSYAL MEDYA ----------------
def get_social():
    data = []

    # Reddit (yasal JSON)
    try:
        url = "https://www.reddit.com/r/Turkey.json"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers).json()

        for p in res["data"]["children"][:5]:
            data.append({"text": p["data"]["title"]})
    except:
        pass

    # RSS (Türkçe haber)
    try:
        feed = feedparser.parse("https://www.trthaber.com/rss/son-dakika.rss")
        for e in feed.entries[:5]:
            data.append({"text": e.title})
    except:
        pass

    # fallback
    if not data:
        data = [
            {"text": "Sosyal medyada yayılan iddia büyük tartışma yarattı"},
            {"text": "Bir haberin doğruluğu sorgulanıyor"},
            {"text": "Viral olan içerik gerçek mi?"}
        ]

    return data


# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("index.html", social=get_social())


@app.route("/analyze", methods=["POST"])
def analyze():
    text = request.form.get("text")
    result = analyze_text(text)

    if result["risk"] > 60:
        send_mail(text, result)

    return jsonify(result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)