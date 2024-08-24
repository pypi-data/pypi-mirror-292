from .model import NERModel


class TextCleaner:
    def __init__(self, model_name_or_path, confidence_threshold=0.65, max_length=512, stride=256):
        self.model = NERModel(model_name_or_path)
        self.confidence_threshold = confidence_threshold
        self.max_length = max_length
        self.stride = stride

    def clean_text(self, text):
        full_tokens = self.model.tokenizer.tokenize(text)

        if len(full_tokens) <= self.max_length:
            return self._clean_single_chunk(text)
        else:
            return self._clean_long_text(full_tokens)

    def _clean_single_chunk(self, text):
        predictions = self.model.predict(text)
        cleaned_tokens = []
        skip_space = False

        for token, pred, conf in predictions:
            if pred in [1, 2] and conf >= self.confidence_threshold:
                skip_space = True
                continue

            if token.startswith("▁"):
                if not skip_space:
                    cleaned_tokens.append(" ")
                cleaned_tokens.append(token.lstrip("▁"))
            else:
                cleaned_tokens.append(token)

            skip_space = False

        cleaned_text = "".join(cleaned_tokens).strip()
        cleaned_text = cleaned_text.replace("<s>", "").replace("</s>", "").strip()

        return cleaned_text

    def _clean_long_text(self, full_tokens):
        cleaned_text = []

        for i in range(0, len(full_tokens), self.stride):
            chunk_tokens = full_tokens[i:i + self.max_length]
            chunk_text = self.model.tokenizer.convert_tokens_to_string(chunk_tokens)

            cleaned_chunk = self._clean_single_chunk(chunk_text)

            cleaned_text.append(cleaned_chunk)

        # Join all the cleaned chunks
        final_cleaned_text = " ".join(cleaned_text).strip()

        return final_cleaned_text
