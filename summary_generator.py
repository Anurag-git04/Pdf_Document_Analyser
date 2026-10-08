from summarizer import Summarizer
from typing import Optional

class DocumentSummarizer:
    def __init__(self):
        try:
            self.model = Summarizer()
        except Exception as e:
            print(f"Could not initialize BERT-extractive-summarizer: {e}")
            self.model = None

    def summarize(self, text: str, ratio: float = 0.02) -> str:
        """Generates a summary of the provided text."""
        if not self.model:
            import re
            sentences = re.split(r'(?<=[.!?]) +', text)
            return " ".join(sentences[:3])

        if not text or len(text.strip()) < 100:
            return text 
        truncated_text = text[:50000]

        summary = self.model(truncated_text, ratio=ratio, min_length=60)

        return "".join(summary)