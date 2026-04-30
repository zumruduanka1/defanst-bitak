from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

tok = AutoTokenizer.from_pretrained("model")
mod = AutoModelForSequenceClassification.from_pretrained("model")

def analyze(text):
    if not text or len(text.strip()) < 20:
        return {"error":"geçersiz"}

    inp = tok(text, return_tensors="pt")
    out = mod(**inp)

    prob = torch.nn.functional.softmax(out.logits, dim=1)
    score = prob[0][1].item()

    risk = int(score*100)

    if risk>75: label="tehlikeli"
    elif risk>40: label="şüpheli"
    else: label="güvenli"

    return {"risk":risk,"label":label}