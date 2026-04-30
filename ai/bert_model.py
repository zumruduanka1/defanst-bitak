from transformers import pipeline

classifier = pipeline(
    "text-classification",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

def analyze_text(text):
    if not text or len(text.strip()) < 10:
        return {"risk": 0, "label": "Geçersiz"}

    result = classifier(text[:512])[0]

    score = int(result["score"] * 100)

    risk = score if result["label"] == "NEGATIVE" else (100 - score)

    if risk > 70:
        label = "Tehlikeli"
    elif risk > 40:
        label = "Şüpheli"
    else:
        label = "Güvenli"

    return {"risk": risk, "label": label}