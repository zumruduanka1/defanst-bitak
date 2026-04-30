import time
import os

while True:
    if os.path.exists("data/feedback.csv"):
        print("Yeni veri bulundu → yeniden eğitim")
        os.system("python train.py")
    time.sleep(300)