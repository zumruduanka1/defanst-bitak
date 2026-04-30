import pandas as pd

main = pd.read_csv("data/train.csv")
fb = pd.read_csv("data/feedback.csv")

df = pd.concat([main, fb])
df.to_csv("data/train.csv", index=False)

print("Model güncellendi")