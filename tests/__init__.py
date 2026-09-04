from pathlib import Path

from PIL import Image


def make_image(
    path: str | Path, size: tuple = (160, 90), color: tuple = (62, 54, 53)
) -> Path:
    p = Path(path)
    Image.new("RGB", size, color).save(p, "PNG")
    return p
