import json

from fastmcp import FastMCP
from PIL import Image


def register(mcp: FastMCP):
    @mcp.resource(
        "config://formats", mime_type="application/json", tags={"meta"}
    )
    def supported_formats() -> str:
        """Formats that Pillow can read in this deployment."""
        exts_set = set()
        for e in Image.registered_extensions():
            exts_set.add(e.lower().lstrip("."))
        exts = sorted(exts_set)
        return json.dumps({"read_formats": exts})
