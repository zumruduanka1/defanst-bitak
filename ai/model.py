import re
import random

fake_keywords = [
    "şok", "ifşa", "gizli", "yayılıyor", "herkes konuşuyor",
    "kanıtlandı", "son dakika", "inanılmaz", "yasaklandı"
]

safe_sources = [
    "bbc", "reuters", "trt", "aa.com", "cnn"
]

def analyze_text(text):
    if len(text.strip()) < 10:
        return {"error": "Boş veya çok kısa veri"}

    text_lower = text.lower()

    risk = 0

    # clickbait analizi
    for k in fake_keywords:
        if k in text_lower:
            risk += 15

    # caps analizi
    if text.isupper():
        risk += 20

    # soru manipülasyonu
    if "?" in text:
        risk += 10

    # sayı + şok kombinasyonu
    if re.search(r"\d+", text):
        risk += 5

    # kaynak kontrol
    for s in safe_sources:
        if s in text_lower:
            risk -= 20

    risk = max(0, min(100, risk))

    if risk > 60:
        label = "Tehlikeli"
    elif risk > 30:
        label = "Şüpheli"
    else:
        label = "Güvenli"

    return {
        "risk": risk,
        "label": label
    }