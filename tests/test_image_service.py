import tempfile
import unittest
from pathlib import Path

from PIL import Image

from image_mcp.services.image_service import ImageService
from tests import make_image


class TestImageService(unittest.TestCase):
    def setUp(self):
        self._d = tempfile.TemporaryDirectory()
        self.svc = ImageService(str(make_image(Path(self._d.name) / "t.png")))

    def tearDown(self):
        self._d.cleanup()

    def _size(self, p):
        with Image.open(p) as im:
            return im.size

    def test_rejects_unknown_extension(self):
        with self.assertRaises(ValueError):
            ImageService("foto.xyz")

    def test_resize_exact(self):
        r = self.svc.resize(80, 60)
        self.assertEqual((r["final_width"], r["final_height"]), (80, 60))
        self.assertEqual(self._size(r["output_path"]), (80, 60))

    def test_crop_box(self):
        r = self.svc.crop(0, 0, 40, 20)
        self.assertEqual((r["final_width"], r["final_height"]), (40, 20))

    def test_rotate(self):
        r = self.svc.rotate_flip(90)
        self.assertEqual(self._size(r["output_path"]), (90, 160))

    def test_convert(self):
        r = self.svc.convert(".jpeg")
        self.assertEqual(r["format"], "jpeg")
        self.assertTrue(Path(r["output_path"]).exists())

    def test_compress(self):
        r = self.svc.compress(50)
        self.assertGreaterEqual(r["compression_ratio"], 1.0)
        self.assertTrue(Path(r["output_path"]).exists())

    def test_thumbnail(self):
        r = self.svc.thumbnail([32])
        self.assertEqual(len(r["thumbnails"]), 1)
        self.assertLessEqual(
            max(self._size(r["thumbnails"][0]["output_path"])), 32
        )

    def test_filter_all(self):
        for f in ("grayscale", "blur", "sharpen", "invert", "sepia"):
            r = self.svc.apply_filter(f)
            self.assertTrue(Path(r["output_path"]).exists())

    def test_watermark_text(self):
        r = self.svc.add_watermark("text", "demo")
        self.assertTrue(Path(r["output_path"]).exists())

    def test_watermark_image(self):
        wm = Path(self._d.name) / "wm.png"
        make_image(wm, size=(20, 10), color=(255, 0, 0))
        r = self.svc.add_watermark("image", str(wm))
        self.assertTrue(Path(r["output_path"]).exists())

    def test_palette_formats(self):
        for fmt, prefix in (("hex", "#"), ("rgb", "rgb("), ("hsl", "hsl(")):
            r = self.svc.extract_palette(3, format=fmt)
            self.assertGreaterEqual(len(r["colors"]), 1)
            self.assertTrue(
                all(c["value"].startswith(prefix) for c in r["colors"])
            )

if __name__ == "__main__":
    unittest.main()
