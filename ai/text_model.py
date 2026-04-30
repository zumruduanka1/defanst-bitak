from predict import predict

def analyze_text(text):
    if len(text.strip()) < 10:
        return {"error": "Geçersiz içerik"}

    risk = predict(text)

    return {
        "risk": risk,
        "label": "Fake" if risk > 50 else "Gerçek"
    }