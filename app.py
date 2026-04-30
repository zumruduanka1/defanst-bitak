from flask import Flask, render_template, request, jsonify
import pickle, re, os, requests, smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

model = pickle.load(open("model.pkl","rb"))
vectorizer = pickle.load(open("vectorizer.pkl","rb"))

# 🔥 INPUT FILTER
def is_valid(text):
    if len(text) < 15:
        return False
    if not re.search(r"[a-zA-ZğüşöçıİĞÜŞÖÇ]", text):
        return False
    return True

# 🔥 ANALİZ
def analyze(text):
    X = vectorizer.transform([text])
    prob = model.predict_proba(X)[0][1]

    risk = int(prob * 100)

    if risk > 70:
        label = "Tehlikeli"
    elif risk > 40:
        label = "Şüpheli"
    else:
        label = "Güvenli"

    return risk, label

# 📧 MAIL
def send_mail(text, risk):
    msg = MIMEText(f"Riskli içerik:\n{text}\nRisk: {risk}%")
    msg["Subject"] = "DEFANS ALERT"
    msg["From"] = os.getenv("EMAIL_USER")
    msg["To"] = os.getenv("ALERT_EMAIL")

    s = smtplib.SMTP("smtp.gmail.com",587)
    s.starttls()
    s.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
    s.send_message(msg)
    s.quit()

# 🐦 TWITTER API
def get_twitter():
    headers = {
        "Authorization": f"Bearer {os.getenv('TWITTER_BEARER')}"
    }

    url = "https://api.twitter.com/2/tweets/search/recent?query=haber&max_results=5"

    r = requests.get(url, headers=headers)

    data = []

    if r.status_code == 200:
        tweets = r.json().get("data",[])
        for t in tweets:
            text = t["text"]
            risk, label = analyze(text)

            data.append({
                "text": text,
                "risk": risk,
                "label": label,
                "source": "Twitter"
            })

    return data

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze_api():
    text = request.json["text"]

    if not is_valid(text):
        return jsonify({"error":"Geçersiz içerik"})

    risk, label = analyze(text)

    if risk > 70:
        send_mail(text, risk)

    return jsonify({
        "risk": risk,
        "label": label
    })

@app.route("/social")
def social():
    return jsonify(get_twitter())

if __name__ == "__main__":
    app.run()