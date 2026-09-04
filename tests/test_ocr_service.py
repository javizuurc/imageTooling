import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

from image_mcp.config import OCR_MISSING_ERROR
from image_mcp.services import ocr_service as svc
from tests import make_image


class TestOcrService(unittest.TestCase):
    def _img(self, d):
        return str(make_image(Path(d) / "t.png"))

    def test_missing_dep(self):
        # ponytail: force ImportError even if pytesseract is installed
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(
            sys.modules, {"pytesseract": None}
        ):
            r = svc.extract_text(self._img(d))
        self.assertEqual(r.get("error"), OCR_MISSING_ERROR)

    def test_happy_path_mocked(self):
        fake = types.SimpleNamespace(
            Output=types.SimpleNamespace(DICT="dict"),
            image_to_data=lambda *a, **k: {
                "text": ["hi", ""],
                "conf": ["90", "-1"],
                "left": [0, 0],
                "top": [0, 0],
                "width": [5, 0],
                "height": [5, 0],
            },
        )
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(
            sys.modules, {"pytesseract": fake}
        ):
            r = svc.extract_text(self._img(d))
        self.assertEqual((r["text"], r["confidence"]), ("hi", 90.0))
        self.assertEqual(len(r["blocks"]), 1)


if __name__ == "__main__":
    unittest.main()
