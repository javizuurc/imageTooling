from fastmcp import FastMCP
from fastmcp.server.context import Context

from image_mcp.schemas.ocr import OcrResult
from image_mcp.services import ocr_service as svc
from image_mcp.utils.log import log_info


def register(mcp: FastMCP):
    
    @mcp.tool(title="OCR extract text", tags={"image", "ocr"}, timeout=300)
    async def ocr_extract_text(
        ctx: Context, image_path: str, language: str = "auto"
    ) -> OcrResult:
        """Extract text from an image using OCR (requires Tesseract, optional)."""
        await log_info(ctx, f"ocr {image_path} lang={language}")
        return svc.extract_text(image_path, language)
