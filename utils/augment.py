import pandas as pd

def augment():
    df = pd.read_csv("data/clean.csv")

    extra = []
    for _,row in df.iterrows():
        extra.append([row["text"]+" hemen paylaş", row["label"]])
        extra.append(["son dakika "+row["text"], row["label"]])

    df2 = pd.DataFrame(extra, columns=["text","label"])
    df = pd.concat([df, df2])

    df.to_csv("data/clean.csv", index=False)