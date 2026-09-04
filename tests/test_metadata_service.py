import tempfile
import unittest
from pathlib import Path

from PIL import Image

from image_mcp.services.metadata_service import MetadataService, dms_to_decimal
from tests import make_image


class TestMetadataService(unittest.TestCase):
    def setUp(self):
        self._d = tempfile.TemporaryDirectory()
        self.img = str(make_image(Path(self._d.name) / "t.png"))

    def tearDown(self):
        self._d.cleanup()

    def test_properties(self):
        r = MetadataService(self.img).get_properties()
        self.assertEqual(
            (r["width"], r["height"], r["format"]), (160, 90, "png")
        )
        self.assertEqual(r["aspect_ratio"], "16:9")
        self.assertFalse(r["has_alpha"])
        self.assertEqual(len(r["checksum"]), 32)

    def test_exif_absent(self):
        r = MetadataService(self.img).get_exif()
        self.assertFalse(r["exif_present"])
        self.assertIsNone(r["gps"]["latitude"])


    def test_strip_removes_exif(self):
        r = MetadataService(self.img).strip_metadata()
        self.assertTrue(Path(r["output_path"]).exists())
        self.assertFalse(MetadataService(r["output_path"]).get_exif()["exif_present"])

    def test_dms_to_decimal(self):
        self.assertAlmostEqual(dms_to_decimal((40, 30, 0), "N"), 40.5)
        self.assertAlmostEqual(dms_to_decimal((40, 30, 0), "S"), -40.5)
        self.assertAlmostEqual(dms_to_decimal((10, 0, 36), "W"), -10.01, 2)

    def test_exif_present(self):
        p = Path(self._d.name) / "ex.jpg"
        make_image(p, size=(64, 64))
        ex = Image.Exif()
        ex[271], ex[272] = "Canon", "M50"  # Make/Model
        with Image.open(p) as im:
            im.save(p, exif=ex)
        r = MetadataService(str(p)).get_exif()
        self.assertTrue(r["exif_present"])
        self.assertEqual(
            (r["camera_make"], r["camera_model"]), ("Canon", "M50")
        )

    def test_strip_custom_output(self):
        out = str(Path(self._d.name) / "clean.png")
        r = MetadataService(self.img).strip_metadata(out)
        self.assertEqual(r["output_path"], out)
        self.assertTrue(Path(out).exists())


if __name__ == "__main__":
    unittest.main()
