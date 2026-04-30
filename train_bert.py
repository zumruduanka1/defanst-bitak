from transformers import Trainer, TrainingArguments, AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd
import torch

df = pd.read_csv("data/train.csv")

tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

class Dataset(torch.utils.data.Dataset):
    def __init__(self, texts, labels):
        self.enc = tokenizer(texts, truncation=True, padding=True)
        self.labels = labels

    def __getitem__(self, i):
        item = {k: torch.tensor(v[i]) for k,v in self.enc.items()}
        item["labels"] = torch.tensor(self.labels[i])
        return item

    def __len__(self):
        return len(self.labels)

dataset = Dataset(df["text"].tolist(), df["label"].tolist())

model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased")

args = TrainingArguments(output_dir="./model", num_train_epochs=1)

trainer = Trainer(model=model, args=args, train_dataset=dataset)

trainer.train()
trainer.save_model("./model")