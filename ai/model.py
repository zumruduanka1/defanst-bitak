import requests, os, json

def analyze_text(text):
    if not text or len(text.strip()) < 10:
        return {"risk":0,"label":"Geçersiz","reason":"Metin çok kısa"}

    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model":"gpt-4o-mini",
                "messages":[
                    {"role":"system","content":"Return JSON {risk:0-100,label,reason}"},
                    {"role":"user","content":text}
                ]
            }
        )

        content = r.json()["choices"][0]["message"]["content"]

        try:
            return json.loads(content)
        except:
            return {"risk":50,"label":"Şüpheli","reason":"Parse fallback"}

    except:
        return {"risk":0,"label":"Hata","reason":"API error"}