import os
import tempfile

def extract_text_from_image(image_path: str) -> str:
    ext = os.path.splitext(image_path)[-1].lower()
    if ext == ".pdf":
        return _extract_from_pdf(image_path)
    else:
        return _extract_from_image(image_path)

def _extract_from_image(image_path: str) -> str:
    # Lazy load EasyOCR only when needed (saves memory at startup)
    import easyocr
    reader = easyocr.Reader(['en'], gpu=False)
    results = reader.readtext(image_path, detail=0, paragraph=True)
    return "\n".join(results)

def _extract_from_pdf(pdf_path: str) -> str:
    from pdf2image import convert_from_path
    pages = convert_from_path(pdf_path, dpi=300)
    all_text = []
    for page in pages:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            page.save(tmp.name, "PNG")
            text = _extract_from_image(tmp.name)
            all_text.append(text)
            os.unlink(tmp.name)
    return "\n".join(all_text)