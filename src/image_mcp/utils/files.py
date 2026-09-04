from pathlib import Path

from PIL import Image

from image_mcp.config import JPEG, LOSSLESS


def ext_of(path: str | Path) -> str:
    """Extension without dot (the dot is Path's domain, not ours)."""
    return Path(path).suffix.lower().lstrip(".")


def save_image(
    im: Image.Image, dest: Path, quality: int | None = None
) -> Path:
    ext = ext_of(dest)
    kw: dict = {}
    if quality is not None and ext not in LOSSLESS:
        kw["quality"] = max(1, min(100, quality))
        if ext in JPEG:
            kw["optimize"] = True
    if ext in JPEG and im.mode in ("RGBA", "LA", "PA"):
        im = im.convert("RGB")
    im.save(dest, **kw)
    return dest


def overlay_pos(position: str, base: tuple, overlay: tuple) -> tuple:
    bw, bh = base
    ow, oh = overlay
    m = 10
    return {
        "top-left": (m, m),
        "top-right": (bw - ow - m, m),
        "bottom-left": (m, bh - oh - m),
        "bottom-right": (bw - ow - m, bh - oh - m),
        "center": ((bw - ow) // 2, (bh - oh) // 2),
    }.get(position, (bw - ow - m, bh - oh - m))
