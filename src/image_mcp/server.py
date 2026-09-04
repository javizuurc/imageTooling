import sys

from fastmcp import FastMCP

from image_mcp import prompts, resources
from image_mcp.tools import image_tools, metadata_tools, ocr_tools

mcp = FastMCP(
    "ImageToolingMCP",
    instructions=(
        "Process images with Pillow: geometry, format, "
        "effects, metadata, and OCR. 'image_path' comes from "
        "the shared filesystem; generated files return "
        "'output_path'. Dotless extensions ('png'). "
        "Start with get_image_properties."
    ),
    version="0.1.0",
)

for module in (image_tools, metadata_tools, ocr_tools, resources, prompts):
    module.register(mcp)

if __name__ == "__main__":
    print(
        "Give this project a star: https://github.com/javizuurc/imageTooling",
        file=sys.stderr,
    )
    mcp.run(show_banner=False, log_level="WARNING")
