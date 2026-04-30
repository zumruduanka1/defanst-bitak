from flask import Flask, render_template, request, jsonify
import requests, os, random, feedparser
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# ---------------- ANALİZ ----------------
def analyze_text(text):
    if not text or len(text.strip()) < 15:
        return {"risk": 0, "label": "Geçersiz"}

    score = 10

    risky_words = [
        "şok", "ifşa", "gizli", "hemen paylaş",
        "kanıtlandı", "yasaklandı", "skandal"
    ]

    for w in risky_words:
        if w in text.lower():
            score += 15

    # uzunluk + yapı analizi
    if len(text) < 50:
        score += 10

    if "!" in text:
        score += 10

    if text.isupper():
        score += 20

    score = min(score, 100)

    return {
        "risk": score,
        "label": "Şüpheli" if score > 60 else "Güvenli"
    }

# ---------------- RSS HABER ----------------
def get_news():
    try:
        feed = feedparser.parse("https://rss.nytimes.com/services/xml/rss/nyt/World.xml")
        return [{"title": e.title} for e in feed.entries[:5]]
    except:
        return []


# ---------------- REDDIT (API’siz) ----------------
def get_reddit():
    try:
        url = "https://www.reddit.com/r/news.json"
        headers = {"User-Agent": "Mozilla/5.0"}
        data = requests.get(url, headers=headers).json()
        posts = data["data"]["children"][:5]

        return [{"text": p["data"]["title"]} for p in posts]
    except:
        return []


# ---------------- FALLBACK ----------------
def fallback_news():
    return [
        {"title": "Son dakika: kritik gelişme yaşandı (%70)"},
        {"title": "Sosyal medyada yayılan iddia (%80)"},
        {"title": "Ekonomide beklenmeyen gelişme (%40)"},
    ]


# ---------------- ROUTES ----------------
@app.route("/")
def home():
    news = get_news()
    reddit = get_reddit()

    if not news:
        news = fallback_news()

    if not reddit:
        reddit = [{"text": n["title"]} for n in news]

    return render_template("index.html", news=news, reddit=reddit)


@app.route("/analyze", methods=["POST"])
def analyze():
    text = request.form.get("text")
    return jsonify(analyze_text(text))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)