import hashlib
import math
from pathlib import Path

from PIL import ExifTags, Image

from image_mcp.schemas.metadata import (
    ExifResult,
    PropertiesResult,
    StripResult,
)
from image_mcp.utils.files import ext_of, save_image

_COLOR_MODES = {"RGB": "RGB", "RGBA": "RGBA", "CMYK": "CMYK", "L": "Grayscale"}
_BIT_DEPTHS = {"1": 1, "L": 8, "P": 8, "RGB": 24, "RGBA": 32, "CMYK": 32}


class MetadataService:
    """Read-only + deletion. No EXIF writing for security."""

    def __init__(self, image_path: str):
        self.src = Path(image_path)

    def get_properties(self) -> PropertiesResult:
        with Image.open(self.src) as im:
            w, h = im.size
            g = math.gcd(w, h)
            with open(self.src, "rb") as f:
                checksum = hashlib.md5(f.read()).hexdigest()

            return {
                "width": w,
                "height": h,
                "format": (im.format or ext_of(self.src)).lower(),
                "color_mode": _COLOR_MODES.get(im.mode, im.mode),
                "has_alpha": "A" in im.getbands(),
                "bit_depth": _BIT_DEPTHS.get(im.mode, 8),
                "aspect_ratio": f"{w // g}:{h // g}",
                "dpi": int(im.info.get("dpi", (72, 72))[0]),
                "file_size_bytes": self.src.stat().st_size,
                "checksum": checksum,
            }

    def get_exif(self) -> ExifResult:
        with Image.open(self.src) as im:
            exif = im.getexif()

            if not exif:
                return {
                    "exif_present": False,
                    "camera_make": None,
                    "camera_model": None,
                    "date_taken": None,
                    "gps": {"latitude": None, "longitude": None, "altitude": None},
                    "shooting_settings": {
                        "iso": None,
                        "aperture": None,
                        "shutter_speed": None,
                        "focal_length": None,
                    },
                    "orientation": None,
                    "software": None,
                    "copyright": None,
                }
            
            tag = {}
            for k, v in exif.items():
                tag[ExifTags.TAGS.get(k, k)] = v
            lat = lon = alt = None

            try:
                if tag.get("GPSInfo"):
                    g = {}
                    for k, v in tag["GPSInfo"].items():
                        g[ExifTags.GPSTAGS.get(k, k)] = v
                    lat = dms_to_decimal(g["GPSLatitude"], g.get("GPSLatitudeRef", "N"))
                    lon = dms_to_decimal(
                        g["GPSLongitude"], g.get("GPSLongitudeRef", "E")
                    )
                    alt = (
                        float(g["GPSAltitude"]) if "GPSAltitude" in g else None
                    )
            except Exception:
                pass
            return {
                "exif_present": True,
                "camera_make": tag.get("Make"),
                "camera_model": tag.get("Model"),
                "date_taken": tag.get("DateTimeOriginal"),
                "gps": {"latitude": lat, "longitude": lon, "altitude": alt},
                "shooting_settings": {
                    "iso": tag.get("ISOSpeedRatings"),
                    "aperture": str(tag["FNumber"]) if tag.get("FNumber") else None,
                    "shutter_speed": str(tag["ExposureTime"])
                    if tag.get("ExposureTime")
                    else None,
                    "focal_length": str(tag["FocalLength"])
                    if tag.get("FocalLength")
                    else None,
                },
                "orientation": tag.get("Orientation"),
                "software": tag.get("Software"),
                "copyright": tag.get("Copyright"),
            }

    def strip_metadata(self, output_path: str | None = None) -> StripResult:
        """Re-writes pixels to {stem}_nometa.{ext}. No EXIF."""

        dest = (
            Path(output_path)
            if output_path
            else self.src.with_name(
                f"{self.src.stem}_nometa.{ext_of(self.src)}"
            )
        )

        with Image.open(self.src) as im:
            had_exif = bool(im.getexif())
            clean = Image.new(im.mode, im.size)
            clean.putdata(list(im.getdata()))

            save_image(clean, dest)
        return {
            "output_path": str(dest),
            "had_exif": had_exif,
            "file_size_bytes": dest.stat().st_size,
        }


def dms_to_decimal(d, ref) -> float:
    v = float(d[0]) + float(d[1]) / 60 + float(d[2]) / 3600
    return -v if ref in ("S", "W") else v
