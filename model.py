import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

MODEL_FILE = "model.joblib"

def train():
    texts = [
        "şok iddia ortaya çıktı",
        "gizli belge ifşa edildi",
        "resmi açıklama yapıldı",
        "bilimsel araştırma sonucu",
        "kanıtlandı doğru haber"
    ]

    labels = [1,1,0,0,0]  # 1 = riskli

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texts)

    model = LogisticRegression()
    model.fit(X, labels)

    joblib.dump((model, vectorizer), MODEL_FILE)

def load():
    return joblib.load(MODEL_FILE)

def predict(text):
    model, vec = load()
    X = vec.transform([text])
    return int(model.predict_proba(X)[0][1] * 100)