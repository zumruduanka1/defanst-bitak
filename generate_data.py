import random
import pandas as pd

fake = [
    "şok gerçek ortaya çıktı",
    "devlet gizli plan yaptı",
    "büyük komplo açığa çıktı",
    "herkes bunu konuşuyor"
]

real = [
    "resmi açıklama yapıldı",
    "bilimsel veri paylaşıldı",
    "haber ajansları doğruladı",
    "yetkililer açıkladı"
]

data = []

for _ in range(50000):
    data.append([random.choice(fake), 1])
    data.append([random.choice(real), 0])

df = pd.DataFrame(data, columns=["text","label"])
df.to_csv("data/main.csv", index=False)

print("100K veri üretildi")