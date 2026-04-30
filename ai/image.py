import random

def analyze_image(file):
    # fake simülasyon (AI mantığı)
    risk = random.randint(10, 90)

    return {
        "risk": risk,
        "label": "Tehlikeli" if risk > 60 else "Güvenli"
    }