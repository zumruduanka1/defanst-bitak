from flask import Flask, render_template, request, jsonify
import requests, threading, time, random

app = Flask(__name__)

feed = []
history = []

# ---------------- AI ----------------
def ai_score(text):
    t = text.lower()
    score = 10

    risk_words = ["şok","iddia","komplo","ifşa","gizli","son dakika","skandal"]
    safe_words = ["resmi","açıklama","doğrulandı","rapor","kaynak"]

    for k in risk_words:
        if k in t:
            score += 15

    for k in safe_words:
        if k in t:
            score -= 10

    score += random.randint(5,20)

    return max(5, min(score,100))

# ---------------- DATA ----------------
def fetch_data():
    data = []

    # GOOGLE NEWS RSS
    try:
        import feedparser
        news = feedparser.parse("https://news.google.com/rss?hl=tr&gl=TR&ceid=TR:tr")
        for e in news.entries[:10]:
            data.append(e.title)
    except:
        pass

    # REDDIT
    try:
        r = requests.get(
            "https://www.reddit.com/r/worldnews.json",
            headers={"User-Agent":"Mozilla/5.0"},
            timeout=5
        )
        j = r.json()
        for p in j["data"]["children"][:10]:
            data.append(p["data"]["title"])
    except:
        pass

    # FALLBACK (ASLA BOŞ KALMAZ)
    if not data:
        data = [
            "Şok iddia gündemde",
            "Sosyal medyada yayılan komplo",
            "Son dakika gelişmesi",
            "Uzmanlar uyardı",
            "Tartışmalı açıklama",
            "Gündemi sarsan haber"
        ]

    return data

# ---------------- SCAN ----------------
def scan():
    global feed

    d = fetch_data()
    new = []

    for t in d:
        s = ai_score(t)
        new.append({"text": t[:120], "score": s})

    feed = new

# ---------------- WORKER ----------------
def worker():
    while True:
        try:
            scan()
        except:
            pass
        time.sleep(10)

# 🔥 EN KRİTİK FIX (BOŞ KALMAMASI İÇİN)
scan()
threading.Thread(target=worker, daemon=True).start()

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    text = request.json["text"]
    s = ai_score(text)

    history.insert(0, {"text": text[:80], "score": s})

    return {"score": s}

@app.route("/data")
def data():
    if not feed:
        scan()  # boşsa tekrar doldur
    return {"feed": feed, "history": history}

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run()