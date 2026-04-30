import pandas as pd
import os

def merge_feedback():
    if not os.path.exists("data/feedback.csv"):
        return

    main = pd.read_csv("data/main.csv")
    fb = pd.read_csv("data/feedback.csv")

    df = pd.concat([main, fb])
    df.to_csv("data/main.csv", index=False)

    os.remove("data/feedback.csv")
    print("feedback eklendi")

def retrain():
    os.system("python utils/preprocess.py")
    os.system("python utils/augment.py")
    os.system("python train.py")

merge_feedback()
retrain()