
# Definitive version WITHOUT Tesseract OCR for maximum speed.

import fitz  # PyMuPDF
import re
from typing import List, Dict

class DocumentProcessor:
    def __init__(self):
        pass

    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict]:
        """Extracts text from a PDF using only the fast, standard method."""
        doc = fitz.open(pdf_path)
        pages_content = []

        for page_num, page in enumerate(doc):
            raw_text = page.get_text("text")
            extraction_method = "Text"

            cleaned_text = self._clean_text(raw_text)
            
            pages_content.append({
                "page_number": page_num + 1,
                "raw_text": raw_text,
                "cleaned_text": cleaned_text,
                "extraction": extraction_method,
                "word_count": len(cleaned_text.split())
            })
            
        doc.close()
        return pages_content

    def _clean_text(self, text: str) -> str:
        """Cleans the extracted text."""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\\$\[\]\{\}\(\)\+\-\*/=^._,;:\'<>≤≥→↔`]', '', text)
        return text.strip()