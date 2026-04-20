import os
import shutil
import pytesseract
from PIL import Image

# Auto-detect tesseract path
tesseract_path = shutil.which("tesseract")
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
else:
    # Try common paths
    for path in ["/usr/bin/tesseract", "/usr/local/bin/tesseract", "/opt/homebrew/bin/tesseract"]:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break

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