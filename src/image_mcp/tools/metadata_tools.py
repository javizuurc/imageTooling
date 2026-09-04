from fastmcp import FastMCP
from fastmcp.server.context import Context

from image_mcp.schemas.metadata import (
    ExifResult,
    PropertiesResult,
    StripResult,
)
from image_mcp.services.metadata_service import MetadataService
from image_mcp.utils.log import log_info


def register(mcp: FastMCP):
    
    @mcp.tool(title="Image properties", tags={"image", "metadata"})
    async def get_image_properties(
        ctx: Context, image_path: str
    ) -> PropertiesResult:
        """Technical/structural metadata."""
        await log_info(ctx, f"properties {image_path}")
        return MetadataService(image_path).get_properties()

    @mcp.tool(title="EXIF metadata", tags={"image", "metadata"})
    async def get_exif_metadata(ctx: Context, image_path: str) -> ExifResult:
        """Capture/device metadata (may not exist)."""
        await log_info(ctx, f"exif {image_path}")
        return MetadataService(image_path).get_exif()

    @mcp.tool(title="Strip metadata", tags={"image", "metadata"})
    async def strip_image_metadata(
        ctx: Context, image_path: str, output_path: str | None = None
    ) -> StripResult:
        """Strip EXIF/info (read+delete only, no tag writing)."""
        await log_info(ctx, f"strip {image_path}")
        return MetadataService(image_path).strip_metadata(output_path)
