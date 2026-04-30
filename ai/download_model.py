from transformers import BertTokenizer, BertForSequenceClassification

def download_model():
    model_name = "bert-base-uncased"

    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertForSequenceClassification.from_pretrained(model_name)

    tokenizer.save_pretrained("model")
    model.save_pretrained("model")

    print("Model indirildi ve model/ klasörüne kaydedildi")

if __name__ == "__main__":
    download_model()