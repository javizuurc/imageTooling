from fastmcp import FastMCP

from . import image, metadata


def register(mcp: FastMCP):
    image.register(mcp)
    metadata.register(mcp)
