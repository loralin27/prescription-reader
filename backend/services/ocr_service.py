import os
import tempfile
from PIL import Image

def extract_text_from_image(image_path: str) -> str:
    ext = os.path.splitext(image_path)[-1].lower()
    if ext == ".pdf":
        return _extract_from_pdf(image_path)
    else:
        return _extract_from_image(image_path)

def _extract_from_image(image_path: str) -> str:
    from doctr.io import DocumentFile
    from doctr.models import ocr_predictor
    model = ocr_predictor(pretrained=True)
    doc = DocumentFile.from_images(image_path)
    result = model(doc)
    text = "\n".join(
        word.value
        for page in result.pages
        for block in page.blocks
        for line in block.lines
        for word in line.words
    )
    return text.strip()

def _extract_from_pdf(pdf_path: str) -> str:
    from doctr.io import DocumentFile
    from doctr.models import ocr_predictor
    model = ocr_predictor(pretrained=True)
    doc = DocumentFile.from_pdf(pdf_path)
    result = model(doc)
    text = "\n".join(
        word.value
        for page in result.pages
        for block in page.blocks
        for line in block.lines
        for word in line.words
    )
    return text.strip()