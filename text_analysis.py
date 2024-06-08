from transformers import pipeline

class TextAnalyzer:
    def __init__(self):
        self.pipe = pipeline("text-classification", model="ealvaradob/bert-finetuned-phishing")

    def analyze(self, message):
        result = self.pipe(message)[0]
        label = 'phishing' if result['label'] == 'phishing' else 'benign'
        score = result['score']
        return label, score
