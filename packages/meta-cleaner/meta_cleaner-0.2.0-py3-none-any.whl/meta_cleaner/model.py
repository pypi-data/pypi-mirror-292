import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification


class NERModel:
    def __init__(self, model_name_or_path, device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        self.model = AutoModelForTokenClassification.from_pretrained(model_name_or_path)
        self.model.to(self.device)
        self.model.eval()

    def predict(self, text):
        tokens = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(self.device)
        with torch.no_grad():
            output = self.model(**tokens)
        logits = output.logits
        probabilities = torch.softmax(logits, dim=-1)
        confidence, predictions = torch.max(probabilities, dim=-1)
        token_ids = tokens['input_ids'].squeeze().tolist()
        tokens_converted = self.tokenizer.convert_ids_to_tokens(token_ids)
        return list(zip(tokens_converted, predictions.squeeze().tolist(), confidence.squeeze().tolist()))
