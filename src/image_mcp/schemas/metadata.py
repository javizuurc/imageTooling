from typing import TypedDict


class Gps(TypedDict):
    latitude: float | None
    longitude: float | None
    altitude: float | None


class ShootingSettings(TypedDict):
    iso: int | None
    aperture: str | None
    shutter_speed: str | None
    focal_length: str | None


class PropertiesResult(TypedDict):
    width: int
    height: int
    format: str
    color_mode: str
    has_alpha: bool
    bit_depth: int
    aspect_ratio: str
    dpi: int
    file_size_bytes: int
    checksum: str


class ExifResult(TypedDict):
    exif_present: bool
    camera_make: str | None
    camera_model: str | None
    date_taken: str | None
    gps: Gps
    shooting_settings: ShootingSettings
    orientation: int | None
    software: str | None
    copyright: str | None


class StripResult(TypedDict):
    output_path: str
    had_exif: bool
    file_size_bytes: int
