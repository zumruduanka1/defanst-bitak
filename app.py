import os, random, requests, smtplib
from flask import Flask, request, jsonify, render_template
from email.mime.text import MIMEText

app = Flask(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWITTER_BEARER = os.getenv("TWITTER_BEARER")

MAIL_USER = os.getenv("MAIL_USER")
MAIL_PASS = os.getenv("MAIL_PASS")

MAIL_TO = ["mail1@gmail.com","mail2@gmail.com"]

# 🔥 AI ANALİZ
def analyze_text(text):
    score = 0

    keywords = ["ifşa","şok","gizli","yayılıyor","acil","saklanıyor"]
    for k in keywords:
        if k in text.lower():
            score += 15

    if len(text) < 30:
        score += 10

    try:
        res = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={
                "model":"gpt-4.1-mini",
                "messages":[{"role":"user","content":f"Bu metin sahte mi? 0-100 sayı ver: {text}"}]
            }
        )
        ai_score = int(res.json()["choices"][0]["message"]["content"])
        score = (score + ai_score)//2
    except:
        pass

    return min(score,100)


# 📩 MAIL
def send_mail(text,score):
    if score < 50:
        return

    msg = MIMEText(f"⚠️ Riskli içerik!\n\n{text}\n\nRisk: %{score}")
    msg["Subject"]="DEFANS ALERT"
    msg["From"]=MAIL_USER

    server=smtplib.SMTP_SSL("smtp.gmail.com",465)
    server.login(MAIL_USER,MAIL_PASS)

    for m in MAIL_TO:
        msg["To"]=m
        server.sendmail(MAIL_USER,m,msg.as_string())

    server.quit()


# 🐦 TWITTER
def get_twitter():
    url="https://api.twitter.com/2/tweets/search/recent"
    headers={"Authorization":f"Bearer {TWITTER_BEARER}"}

    params={
        "query":"(gündem OR ifşa OR son dakika OR şok) lang:tr -is:retweet",
        "max_results":10
    }

    try:
        res=requests.get(url,headers=headers,params=params)
        data=res.json()

        tweets=[]

        if "data" not in data:
            return []

        for t in data["data"]:
            score=analyze_text(t["text"])

            tweets.append({
                "text":t["text"],
                "platform":"X",
                "risk":score
            })

        return tweets

    except:
        return []


# 🔥 TREND (SOSYAL VERİ)
def get_trends():
    sample=[
        "Büyük ifşa ortaya çıktı",
        "Gizli belge sızdırıldı",
        "Şok karar açıklandı",
        "Herkes bunu konuşuyor"
    ]

    data=[]
    for s in sample:
        data.append({
            "text":s,
            "platform":"TREND",
            "risk":analyze_text(s)
        })

    return data


# 🎭 PLATFORM MIX (IG/TIKTOK GÖRÜNÜM)
def mix_platforms(data):
    platforms=["X","INSTAGRAM","TIKTOK"]
    for d in data:
        d["platform"]=random.choice(platforms)
    return data


# 📡 FEED
@app.route("/feed")
def feed():
    twitter=get_twitter()
    trends=get_trends()

    data=twitter+trends

    if not data:
        data=[{
            "text":"Örnek veri (API boş)",
            "platform":"SYSTEM",
            "risk":30
        }]

    return jsonify(mix_platforms(data))


# 🔥 ANALİZ
@app.route("/analyze",methods=["POST"])
def analyze():
    text=request.json.get("text")

    score=analyze_text(text)
    send_mail(text,score)

    return jsonify({
        "score":score,
        "status":"danger" if score>50 else "safe"
    })


@app.route("/")
def home():
    return render_template("index.html")


if __name__=="__main__":
    app.run()