from fastmcp import FastMCP
from fastmcp.server.context import Context

from image_mcp.schemas.image import (
    CompressResult,
    ConvertResult,
    CropResult,
    FilterResult,
    PaletteResult,
    ResizeResult,
    RotateResult,
    ThumbnailResult,
    WatermarkResult,
)
from image_mcp.config import DEFAULT_THUMB_SIZES
from image_mcp.services.image_service import ImageService
from image_mcp.utils.log import log_info, report_progress


def register(mcp: FastMCP):
    
    @mcp.tool(title="Resize image", tags={"image", "geometry"})
    async def resize_image(
        ctx: Context, image_path: str, width: int, height: int
    ) -> ResizeResult:
        """Resize an image to the given width and height."""
        await log_info(ctx, f"resize {image_path} a {width}x{height}")
        return ImageService(image_path).resize(width, height)

    @mcp.tool(title="Crop image", tags={"image", "geometry"})
    async def crop_image(
        ctx: Context,
        image_path: str,
        x: int = 0,
        y: int = 0,
        width: int | None = None,
        height: int | None = None,
    ) -> CropResult:
        """Cut a region (x, y, width, height)."""
        await log_info(
            ctx, f"crop {image_path} box=({x},{y},{width},{height})"
        )
        return ImageService(image_path).crop(x, y, width, height)

    @mcp.tool(title="Rotate/flip image", tags={"image", "geometry"})
    async def rotate_flip_image(
        ctx: Context,
        image_path: str,
        rotate_degrees: int = 0,
        flip: str = "none",
    ) -> RotateResult:
        """Rotate or flip the image."""
        await log_info(
            ctx, f"rotate {image_path} {rotate_degrees}° flip={flip}"
        )
        return ImageService(image_path).rotate_flip(rotate_degrees, flip)

    @mcp.tool(title="Convert format", tags={"image", "format"})
    async def convert_format(
        ctx: Context,
        image_path: str,
        target_format: str,
        quality: int | None = None,
    ) -> ConvertResult:
        """Convert between image formats."""
        await log_info(ctx, f"convert {image_path} a {target_format}")
        return ImageService(image_path).convert(target_format, quality)

    @mcp.tool(title="Compress image", tags={"image", "format"})
    async def compress_image(
        ctx: Context, image_path: str, quality: int = 80
    ) -> CompressResult:
        """Reduce file size without changing dimensions."""
        await log_info(ctx, f"compress {image_path} quality={quality}")
        return ImageService(image_path).compress(quality)

    @mcp.tool(title="Generate thumbnails", tags={"image", "format"})
    async def generate_thumbnail(
        ctx: Context, image_path: str, sizes: list[int] | None = None
    ) -> ThumbnailResult:
        """Create thumbnails of the image in the specified sizes."""
        resolved = sizes or DEFAULT_THUMB_SIZES
        total = len(resolved)
        await log_info(ctx, f"thumbnails {image_path} sizes={resolved}")
        await report_progress(ctx, 0, total, "starting thumbnails")

        out: ThumbnailResult = {"thumbnails": []}
        for i, s in enumerate(resolved):
            r = ImageService(image_path).thumbnail([s])
            out["thumbnails"].extend(r["thumbnails"])
            await report_progress(ctx, i + 1, total, f"thumbnail {s}px ({i + 1}/{total})")
        return out

    @mcp.tool(title="Apply filter", tags={"image", "effect"})
    async def apply_filter(
        ctx: Context,
        image_path: str,
        filter: str,
        intensity: float | None = None,
    ) -> FilterResult:
        """Basic image filters."""
        await log_info(
            ctx, f"filter {image_path} {filter} intensity={intensity}"
        )
        return ImageService(image_path).apply_filter(filter, intensity)

    @mcp.tool(title="Add watermark", tags={"image", "effect"})
    async def add_watermark(
        ctx: Context,
        image_path: str,
        watermark_type: str,
        content: str,
        position: str = "bottom-right",
        opacity: float = 0.5,
    ) -> WatermarkResult:
        """Overlay text or image as watermark."""
        await log_info(
            ctx, f"watermark {image_path} {watermark_type}@{position}"
        )
        return ImageService(image_path).add_watermark(
            watermark_type, content, position, opacity
        )

    @mcp.tool(title="Extract palette", tags={"image", "effect"})
    async def extract_palette(
        ctx: Context, image_path: str, num_colors: int = 5, format: str = "hex"
    ) -> PaletteResult:
        """Extract dominant colors from the image."""
        await log_info(ctx, f"palette {image_path} n={num_colors} {format}")
        return ImageService(image_path).extract_palette(num_colors, format)
