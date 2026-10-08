import fitz  # PyMuPDF
import re
from typing import List, Dict
import pytesseract
from PIL import Image
import io
import streamlit as st # Import streamlit to show a warning if needed

class DocumentProcessor:
    def __init__(self):
        # Check for Tesseract once at the beginning.
        self.tesseract_available = True
        try:
            pytesseract.get_tesseract_version()
        except pytesseract.TesseractNotFoundError:
            self.tesseract_available = False
            # This is a good place to show a one-time warning in the Streamlit console/UI
            st.warning("Tesseract not found in PATH. Advanced math/drawing OCR is disabled.", icon="⚠️")

    def _ocr_image_area(self, page: fitz.Page, rect: fitz.Rect) -> str:
        """Helper function to OCR a specific rectangular area of a page."""
        pix = page.get_pixmap(clip=rect, dpi=300)
        img_bytes = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_bytes))
        text = pytesseract.image_to_string(img)
        return text.strip()

    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict]:
        doc = fitz.open(pdf_path)
        pages_content = []

        for page_num, page in enumerate(doc):
            raw_text = page.get_text("text")
            extraction_method = "Text"

            # Only attempt OCR if Tesseract was found during initialization
            if self.tesseract_available:
                # Full Page OCR for image-heavy pages
                if len(raw_text.strip()) < 100:
                    try:
                        pix = page.get_pixmap(dpi=300)
                        img_bytes = pix.tobytes("png")
                        img = Image.open(io.BytesIO(img_bytes))
                        ocr_text = pytesseract.image_to_string(img)
                        if len(ocr_text.strip()) > len(raw_text.strip()):
                            raw_text = ocr_text
                            extraction_method = "Full Page OCR"
                    except Exception as e:
                        print(f"Full page OCR failed for page {page_num + 1}: {e}")

                # Drawing (vector graphics) OCR for formulas
                drawings = page.get_drawings()
                if drawings:
                    try:
                        drawing_texts = [f"\n\n==Start of OCR for page {page_num+1} Drawings==\n"]
                        for path in drawings:
                            ocr_content = self._ocr_image_area(page, path['rect'])
                            if ocr_content:
                                drawing_texts.append(ocr_content)
                        drawing_texts.append(f"\n==End of OCR for page {page_num+1} Drawings==\n")
                        
                        raw_text += "\n".join(drawing_texts)
                        if "OCR" not in extraction_method:
                            extraction_method += " + Drawing OCR"
                    except Exception as e:
                        print(f"Drawing OCR failed for page {page_num + 1}: {e}")

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
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\\$\[\]\{\}\(\)\+\-\*/=^._,;:\'<>≤≥→↔`]', '', text)
        return text.strip()