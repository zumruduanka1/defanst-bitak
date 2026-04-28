from flask import Flask, request, jsonify, render_template
import requests, os, threading, time, re, html, smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")
TWITTER_BEARER = os.getenv("TWITTER_BEARER")

history, feed = [], []

# -------- TEXT --------
def extract(url):
    try:
        r = requests.get(url, timeout=5, headers={"User-Agent":"Mozilla"})
        txt = re.sub("<[^<]+?>"," ", r.text)
        return " ".join(txt.split())[:1200]
    except:
        return ""

# -------- RISK --------
def risk(text):
    t = text.lower()
    score = 20
    for k in ["şok","iddia","ifşa","gizli","komplo","son dakika"]:
        if k in t:
            score += 15
    if len(text) < 50:
        score += 10
    return min(100, score)

# -------- MAIL --------
def send_mail(text, r):
    try:
        if not EMAIL_USER:
            return
        msg = MIMEText(f"⚠️ Risk %{r}\n\n{text[:300]}")
        msg["Subject"] = "DEFANS ALERT"
        msg["From"] = EMAIL_USER
        msg["To"] = EMAIL_TO

        s = smtplib.SMTP("smtp.gmail.com",587)
        s.starttls()
        s.login(EMAIL_USER, EMAIL_PASS)
        s.sendmail(EMAIL_USER, EMAIL_TO, msg.as_string())
        s.quit()
    except:
        pass

# -------- RSS --------
def get_news():
    src = "https://news.google.com/rss?hl=tr&gl=TR&ceid=TR:tr"
    data = []
    try:
        r = requests.get(src, timeout=5)
        items = re.findall(r"<item>(.*?)</item>", r.text, re.S)
        for i in items[:10]:
            title = re.search(r"<title>(.*?)</title>", i)
            if title:
                data.append({"text": html.unescape(title.group(1))})
    except:
        pass
    return data

# -------- TWITTER --------
def get_tweets():
    try:
        url = "https://api.twitter.com/2/tweets/search/recent"
        headers = {"Authorization": f"Bearer {TWITTER_BEARER}"}
        params = {
            "query": "gündem OR iddia OR şok lang:tr -is:retweet",
            "max_results": 10
        }
        r = requests.get(url, headers=headers, params=params, timeout=5)
        d = r.json()
        out = []
        if "data" in d:
            for t in d["data"]:
                out.append({"text": t["text"]})
        return out
    except:
        return []

# -------- SCAN --------
def scan():
    global feed
    while True:
        items = get_news() + get_tweets()

        if not items:
            items = [{"text":"Şok iddia gündemde"}]

        new = []
        for i in items:
            r = risk(i["text"])
            obj = {"text": i["text"][:120], "risk": r}
            new.append(obj)

            if r >= 50:
                send_mail(i["text"], r)

        feed = sorted(new, key=lambda x: x["risk"], reverse=True)[:20]
        time.sleep(30)

threading.Thread(target=scan, daemon=True).start()

# -------- API --------
@app.route("/api/analyze", methods=["POST"])
def analyze():
    text = request.json.get("text","")
    if text.startswith("http"):
        text = extract(text)

    r = risk(text)
    history.insert(0, {"text": text[:80], "risk": r})

    if r >= 50:
        send_mail(text, r)

    return {"risk": r}

@app.route("/api/all")
def all_data():
    return {"feed": feed, "history": history}

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run()