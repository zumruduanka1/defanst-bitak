import pandas as pd
import random

fake = ["şok gerçek", "gizli plan", "komplo", "ifşa edildi"]
real = ["resmi açıklama", "bilimsel veri", "doğrulandı"]

data = []

for _ in range(50000):
    data.append([random.choice(fake), 1])
    data.append([random.choice(real), 0])

df = pd.DataFrame(data, columns=["text","label"])
df.to_csv("data/train.csv", index=False)

print("100K dataset hazır")