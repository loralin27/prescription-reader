import cv2
import numpy as np
import tempfile
import os


def preprocess_image(image_path: str) -> str:
    """
    Preprocess image for better OCR accuracy:
    - Convert to grayscale
    - Resize if too small
    - Remove noise
    - Enhance contrast
    Returns path to processed image.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image at path: {image_path}")

    # Step 1: Resize if image is too small (min width 1000px)
    h, w = img.shape[:2]
    if w < 1000:
        scale = 1000 / w
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    # Step 2: Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Step 3: Denoise
    denoised = cv2.fastNlMeansDenoising(gray, h=10)

    # Step 4: Contrast enhancement using CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)

    # Step 5: Thresholding (Otsu's binarization)
    _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Save to a new temp file
    suffix = os.path.splitext(image_path)[-1] or ".png"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        processed_path = tmp.name

    cv2.imwrite(processed_path, binary)
    return processed_path