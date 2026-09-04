from fastmcp import FastMCP


def register(mcp: FastMCP):
    @mcp.prompt(tags={"image", "workflow"})
    def describe_image(image_path: str) -> str:
        """Summarize an image with properties, EXIF, and palette."""
        return (
            f"Describe the image {image_path}: call get_image_properties, "
            "get_exif_metadata and extract_palette, then summarize with "
            "dimensions, format, camera/date if EXIF exists, and dominant colors."
        )

    @mcp.prompt(tags={"image", "workflow"})
    def thumbnail_plan(image_path: str, sizes: str = "64,128,256") -> str:
        """Generate thumbnails and report created paths."""
        return (
            f"Generate thumbnails for {image_path} using generate_thumbnail "
            f"(sizes=[{sizes}]) and report each size with its output_path."
        )
