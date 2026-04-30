import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from utils.preprocess import clean_text

df = pd.read_csv("data/main.csv")

df["text"] = df["text"].apply(clean_text)

vectorizer = TfidfVectorizer(max_features=5000)
X = vectorizer.fit_transform(df["text"])

y = df["label"]

model = LogisticRegression()
model.fit(X, y)

with open("model/model.pkl", "wb") as f:
    pickle.dump((vectorizer, model), f)

print("Model eğitildi ✅")