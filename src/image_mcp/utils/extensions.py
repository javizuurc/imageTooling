"""Accepted extensions. The rest is rejected."""

from image_mcp.config import ALLOWED_EXTENSIONS


def ensure_allowed(ext: str) -> str:
    e = ext.lower().lstrip(".")

    if e not in ALLOWED_EXTENSIONS:
        
        raise ValueError(
            f"extension not allowed: {ext!r} "
            f"(allowed: {sorted(ALLOWED_EXTENSIONS)})"
        )
    return e
