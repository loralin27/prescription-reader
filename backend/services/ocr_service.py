import os
import tempfile
import pytesseract
from PIL import Image

def extract_text_from_image(image_path: str) -> str:
    ext = os.path.splitext(image_path)[-1].lower()
    if ext == ".pdf":
        return _extract_from_pdf(image_path)
    else:
        return _extract_from_image(image_path)

def _extract_from_image(image_path: str) -> str:
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, lang='eng')
    return text.strip()

def _extract_from_pdf(pdf_path: str) -> str:
    from pdf2image import convert_from_path
    pages = convert_from_path(pdf_path, dpi=300)
    all_text = []
    for page in pages:
        text = pytesseract.image_to_string(page, lang='eng')
        all_text.append(text.strip())
    return "\n".join(all_text)