import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pickle

# basit dataset (sen büyütebilirsin)
data = {
    "text":[
        "şok gerçek ortaya çıktı",
        "resmi açıklama yapıldı",
        "hükümet saklıyor",
        "bilimsel araştırmaya göre",
        "gizli belge ifşa edildi"
    ],
    "label":[1,0,1,0,1]
}

df = pd.DataFrame(data)

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df["text"])

model = LogisticRegression()
model.fit(X, df["label"])

pickle.dump(model, open("model.pkl","wb"))
pickle.dump(vectorizer, open("vectorizer.pkl","wb"))

print("Model hazır")