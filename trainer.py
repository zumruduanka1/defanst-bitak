import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pickle

df = pd.read_csv("dataset.csv")

vectorizer = TfidfVectorizer(max_features=5000)
X = vectorizer.fit_transform(df["text"])
y = df["label"]

model = LogisticRegression(max_iter=1000)
model.fit(X, y)

with open("model.pkl", "wb") as f:
    pickle.dump((vectorizer, model), f)

print("MODEL HAZIR")