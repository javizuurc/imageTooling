from typing import NotRequired, TypedDict


class OcrBlock(TypedDict):
    text: str
    bbox: list[int]


class OcrResult(TypedDict):
    text: str
    confidence: float
    blocks: list[OcrBlock]
    error: NotRequired[str]
