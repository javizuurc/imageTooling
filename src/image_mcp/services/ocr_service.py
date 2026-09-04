from PIL import Image

from image_mcp.config import OCR_MISSING_ERROR
from image_mcp.schemas.ocr import OcrResult


def extract_text(image_path: str, language: str = "auto") -> OcrResult:
    try:
        import pytesseract  # ponytail: optional, not installed
    except ImportError:
        return {"text": "", "confidence": 0.0, "blocks": [], "error": OCR_MISSING_ERROR}
    with Image.open(image_path) as im:
        data = pytesseract.image_to_data(
            im,
            lang=None if language == "auto" else language,
            output_type=pytesseract.Output.DICT,
        )
        words, blocks, confs = [], [], []
        for i, t in enumerate(data["text"]):
            if t.strip():
                box = []
                for k in ("left", "top", "width", "height"):
                    box.append(data[k][i])
                blocks.append({"text": t, "bbox": box})
                words.append(t)
                try:
                    confs.append(float(data["conf"][i]))
                except ValueError:
                    pass
        return {
            "text": " ".join(words),
            "confidence": round(sum(confs) / len(confs), 3) if confs else 0.0,
            "blocks": blocks,
        }
