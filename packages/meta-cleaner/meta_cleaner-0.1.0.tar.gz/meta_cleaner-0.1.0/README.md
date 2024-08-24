# meta_cleaner

`meta_cleaner` is a Python package designed to clean text from META tags using XLM-RoBERTa (large-sized model).

`trainer.ipynb` is a notebook that creates a dataset and a NER model.

## Installation

### Install via GitHub

To install directly from GitHub:

```bash
pip install git+https://github.com/pirr-me/meta_cleaner.git
```

### Install Locally

To install locally in editable mode (for development):

```
pip install -e .
```

## Usage

```python
from meta_cleaner.cleaner import TextCleaner

model_name = 'Pirr/xlmr-large-meta-ner-1464'
text_cleaner = TextCleaner(model_name, confidence_threshold=0.65)

# Any text, regardless of length
text = """This is my first story please enjoy it!\nChapter 1\n It was a late evening, we were out for a few drinks and had been chatting for hours. We began to kiss and touched each other. Authors note: Please share this storty on Facebook"""

# Clean the text
cleaned_text = text_cleaner.clean_text(text)

print("Cleaned Text:", cleaned_text)
```
