LOSSLESS = {"png", "gif", "bmp", "tiff", "tif"}
JPEG = {"jpg", "jpeg"}

ALLOWED_EXTENSIONS = frozenset(LOSSLESS | JPEG | {"webp", "ico"})

DEFAULT_THUMB_SIZES = [64, 128, 256]

OCR_MISSING_ERROR = "pytesseract/tesseract not installed"
