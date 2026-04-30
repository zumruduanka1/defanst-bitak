from transformers import pipeline

clf = pipeline("zero-shot-image-classification",
               model="openai/clip-vit-base-patch32")

labels = ["fake","real","manipulated"]

def analyze_image(url):
    try:
        r = clf(url, candidate_labels=labels)
        top = r[0]
        return {"risk":int(top["score"]*100),"label":top["label"]}
    except:
        return {"error":"img fail"}