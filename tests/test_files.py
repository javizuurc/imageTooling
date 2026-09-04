import tempfile
import unittest
from pathlib import Path

from image_mcp.utils.extensions import ensure_allowed
from image_mcp.utils.files import ext_of, overlay_pos, save_image
from PIL import Image


class TestFiles(unittest.TestCase):
    def test_ext_dotless(self):
        self.assertEqual(ext_of("a.PNG"), "png")
        self.assertEqual(ext_of(Path("a/b.JPEG")), "jpeg")

    def test_save_converts_rgba_for_jpeg(self):
        with tempfile.TemporaryDirectory() as d:
            dest = Path(d) / "t.jpg"
            save_image(Image.new("RGBA", (10, 10)), dest, quality=80)
            with Image.open(dest) as im:
                self.assertEqual(im.mode, "RGB")

    def test_overlay_pos_all_and_fallback(self):
        self.assertEqual(
            overlay_pos("top-left", (100, 100), (20, 10)), (10, 10)
        )
        self.assertEqual(
            overlay_pos("bottom-right", (100, 100), (20, 10)), (70, 80)
        )
        self.assertEqual(
            overlay_pos("center", (100, 100), (20, 10)), (40, 45)
        )
        self.assertEqual(
            overlay_pos("bogus", (100, 100), (20, 10)), (70, 80)
        )

    def test_ensure_allowed_and_quality_clamp(self):
        self.assertEqual(ensure_allowed(".PNG"), "png")
        with self.assertRaises(ValueError):
            ensure_allowed("xyz")
        with tempfile.TemporaryDirectory() as d:  # clamp, no crash
            dest = Path(d) / "t.jpg"
            save_image(Image.new("RGB", (10, 10)), dest, quality=999)
            self.assertTrue(dest.exists())
            dest2 = Path(d) / "t.png"  # lossless ignora quality
            save_image(Image.new("RGB", (10, 10)), dest2, quality=10)
            self.assertTrue(dest2.exists())


if __name__ == "__main__":
    unittest.main()
