import colorsys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

from image_mcp.config import DEFAULT_THUMB_SIZES
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
from image_mcp.utils.extensions import ensure_allowed
from image_mcp.utils.files import ext_of, overlay_pos, save_image


class ImageService:
    """Output is always named {name}_{operation}.{ext}."""

    def __init__(self, image_path: str):
        self.src = Path(image_path)
        self.ext = ensure_allowed(ext_of(self.src))

    def _run(self, suffix: str, fn, quality: int | None = None) -> Path:
        dest = self.src.with_name(f"{self.src.stem}_{suffix}.{self.ext}")

        with Image.open(self.src) as im:
            save_image(fn(im), dest, quality)
        return dest

    def resize(self, width: int, height: int) -> ResizeResult:
        dest = self._run(
            "resize", lambda im: im.resize((width, height), Image.LANCZOS)
        )

        return {
            "output_path": str(dest),
            "final_width": width,
            "final_height": height,
        }

    def crop(
        self,
        x: int = 0,
        y: int = 0,
        width: int | None = None,
        height: int | None = None,
    ) -> CropResult:
        def _crop(im):
            w = width if width is not None else im.size[0] - x
            h = height if height is not None else im.size[1] - y
            return im.crop((x, y, x + w, y + h))

        dest = self._run("crop", _crop)
        with Image.open(dest) as out:
            w, h = out.size
        return {"output_path": str(dest), "final_width": w, "final_height": h}

    def rotate_flip(
        self, rotate_degrees: int = 0, flip: str = "none"
    ) -> RotateResult:
        def _tf(im):
            if rotate_degrees:
                im = im.rotate(-rotate_degrees, expand=True)

            if flip == "horizontal":
                im = im.transpose(Image.FLIP_LEFT_RIGHT)
            elif flip == "vertical":
                im = im.transpose(Image.FLIP_TOP_BOTTOM)
            return im

        return {"output_path": str(self._run("rotate_flip", _tf))}

    def convert(
        self, target_format: str, quality: int | None = None
    ) -> ConvertResult:
        fmt = ensure_allowed(target_format)
        dest = self.src.with_name(
            f"{self.src.stem}_convert.{'jpg' if fmt == 'jpeg' else fmt}"
        )

        with Image.open(self.src) as im:
            save_image(im, dest, quality)

        return {
            "output_path": str(dest),
            "format": fmt,
            "file_size_bytes": dest.stat().st_size,
        }

    def compress(self, quality: int = 80) -> CompressResult:
        orig = self.src.stat().st_size
        dest = self._run("compress", lambda im: im, quality)
        final = dest.stat().st_size

        return {
            "output_path": str(dest),
            "original_size_bytes": orig,
            "final_size_bytes": final,
            "compression_ratio": round(orig / max(1, final), 3),
        }

    def thumbnail(self, sizes: list[int] | None = None) -> ThumbnailResult:
        out = []

        with Image.open(self.src) as im:
            for s in sizes or DEFAULT_THUMB_SIZES:
                t = im.copy()
                t.thumbnail((s, s), Image.LANCZOS)
                dest = self.src.with_name(
                    f"{self.src.stem}_thumbnail_{s}.{self.ext}"
                )

                save_image(t, dest)
                out.append({"size": s, "output_path": str(dest)})
        return {"thumbnails": out}

    def apply_filter(
        self, filter: str, intensity: float | None = None
    ) -> FilterResult:
        k = intensity if intensity is not None else 1.0
        rgb = lambda im: im.convert("RGB")  # noqa: E731

        def _fx(im):
            if filter == "grayscale":
                return Image.blend(
                    rgb(im), ImageOps.grayscale(im).convert("RGB"), k
                )
            if filter == "blur":
                return Image.blend(
                    im,
                    im.filter(ImageFilter.GaussianBlur(radius=2 * k or 0.1)),
                    min(1.0, k or 1.0),
                )
            if filter == "sharpen":
                return Image.blend(
                    im, im.filter(ImageFilter.SHARPEN), min(1.0, k or 1.0)
                )
            if filter == "invert":
                return Image.blend(rgb(im), ImageOps.invert(rgb(im)), k)
            if filter == "sepia":
                g = ImageOps.grayscale(im)
                sep = Image.merge(
                    "RGB",
                    [
                        g.point(lambda v: min(255, int(v * 1.07))),
                        g.point(lambda v: min(255, int(v * 0.74))),
                        g.point(lambda v: min(255, int(v * 0.43))),
                    ],
                )
                return Image.blend(rgb(im), sep, k)
            return im

        return {"output_path": str(self._run(f"filter_{filter}", _fx))}

    def add_watermark(
        self,
        watermark_type: str,
        content: str,
        position: str = "bottom-right",
        opacity: float = 0.5,
    ) -> WatermarkResult:
        if watermark_type == "image":
            with (
                Image.open(self.src).convert("RGBA") as im,
                Image.open(content).convert("RGBA") as wm,
            ):
                wm.putalpha(int(255 * opacity))
                im.paste(wm, overlay_pos(position, im.size, wm.size), wm)
                dest = self.src.with_name(
                    f"{self.src.stem}_watermark.{self.ext}"
                )
                save_image(im.convert("RGB"), dest)
            return {"output_path": str(dest)}

        def _text(im):
            im = im.convert("RGBA")
            tw, th = int(im.size[0] * 0.4), 20
            clean = Image.new("RGBA", im.size, (0, 0, 0, 0))

            ImageDraw.Draw(clean).text(
                overlay_pos(position, im.size, (tw, th)),
                content,
                fill=(255, 255, 255, int(255 * opacity)),
            )
            return Image.alpha_composite(im, clean).convert("RGB")

        return {"output_path": str(self._run("watermark", _text))}

    def extract_palette(
        self, num_colors: int = 5, format: str = "hex"
    ) -> PaletteResult:
        def color_format(r: int, g: int, b: int) -> str:
            if format == "rgb":
                return f"rgb({r},{g},{b})"
            
            if format == "hsl":
                h, lum, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
                return f"hsl({int(h * 360)},{int(s * 100)}%,{int(lum * 100)}%)"
            
            return f"#{r:02x}{g:02x}{b:02x}"

        with Image.open(self.src) as im:
            small = im.convert("RGB").resize((100, 100))
            quantized = small.quantize(
                colors=num_colors, method=Image.Quantize.MEDIANCUT
            )
            palette = quantized.getpalette()[: num_colors * 3]
            counts = sorted(quantized.getcolors(), reverse=True)
            total = 0
            for c, _ in counts:
                total += c
            if not total:
                total = 1
            colors = []

            for pixel_count, palette_index in counts:
                o = palette_index * 3
                r, g, b = palette[o : o + 3]
                colors.append(
                    {
                        "value": color_format(r, g, b),
                        "percentage": round(pixel_count / total, 4),
                    }
                )
            return {"colors": colors}
