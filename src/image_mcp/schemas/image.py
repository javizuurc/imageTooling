from typing import TypedDict


class ResizeResult(TypedDict):
    output_path: str
    final_width: int
    final_height: int


class ConvertResult(TypedDict):
    output_path: str
    format: str
    file_size_bytes: int


class CompressResult(TypedDict):
    output_path: str
    original_size_bytes: int
    final_size_bytes: int
    compression_ratio: float


class ColorEntry(TypedDict):
    value: str
    percentage: float


class PaletteResult(TypedDict):
    colors: list[ColorEntry]


class CropResult(TypedDict):
    output_path: str
    final_width: int
    final_height: int


class RotateResult(TypedDict):
    output_path: str


class WatermarkResult(TypedDict):
    output_path: str


class ThumbnailEntry(TypedDict):
    size: int
    output_path: str


class ThumbnailResult(TypedDict):
    thumbnails: list[ThumbnailEntry]


class FilterResult(TypedDict):
    output_path: str
