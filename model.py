import pickle

with open("model.pkl", "rb") as f:
    vectorizer, model = pickle.load(f)

def keyword_boost(text):
    text = text.lower()

    fake = ["şok","iddia","komplo","gizli","ifşa","bomba"]
    trust = ["resmi","açıklama","doğrulandı","kaynak"]

    score = 0

    for k in fake:
        if k in text:
            score += 10

    for k in trust:
        if k in text:
            score -= 10

    return score

def predict(text):
    try:
        vec = vectorizer.transform([text])
        prob = model.predict_proba(vec)[0][1]
        base = int(prob * 100)

        boost = keyword_boost(text)

        final = base + boost

        return max(5, min(100, final))

    except:
        return 10