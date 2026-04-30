import pandas as pd

def clean():
    df = pd.read_csv("data/main.csv")
    df = df.dropna()
    df.to_csv("data/clean.csv", index=False)