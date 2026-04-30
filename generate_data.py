import pandas as pd

fake = ["şok gerçek ortaya çıktı", "acil paylaş", "gizli bilgi"]
real = ["resmi açıklama", "bilimsel araştırma", "rapor yayınlandı"]

data = []

for i in range(500):
    for f in fake:
        data.append([f,1])
    for r in real:
        data.append([r,0])

df = pd.DataFrame(data, columns=["text","label"])
df.to_csv("data/main.csv", index=False)

print("dataset hazır")