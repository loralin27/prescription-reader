import easyocr
import os

# Initialize reader once (heavy model load)
_reader = None

def get_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(['en'], gpu=False)
    return _reader


def extract_text_from_image(image_path: str) -> str:
    """
    Extract raw text from an image using EasyOCR.
    Handles both regular images and PDFs (via pdf2image).
    """
    ext = os.path.splitext(image_path)[-1].lower()

    if ext == ".pdf":
        return _extract_from_pdf(image_path)
    else:
        return _extract_from_image(image_path)


def _extract_from_image(image_path: str) -> str:
    reader = get_reader()
    results = reader.readtext(image_path, detail=0, paragraph=True)
    return "\n".join(results)


def _extract_from_pdf(pdf_path: str) -> str:
    """Convert PDF pages to images and run OCR."""
    from pdf2image import convert_from_path
    import tempfile

    pages = convert_from_path(pdf_path, dpi=300)
    all_text = []

    for i, page in enumerate(pages):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            page.save(tmp.name, "PNG")
            text = _extract_from_image(tmp.name)
            all_text.append(text)
            os.unlink(tmp.name)

    return "\n".join(all_text)