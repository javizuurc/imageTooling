import tempfile
import unittest
from pathlib import Path

from image_mcp.server import mcp
from tests import make_image

class TestServer(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self._d = tempfile.TemporaryDirectory()
        self.img = str(make_image(Path(self._d.name) / "t.png"))

    def tearDown(self):
        self._d.cleanup()

    async def test_end_to_end(self):
        r = await mcp.call_tool(
            "get_image_properties", {"image_path": self.img}
        )
        self.assertEqual(r.structured_content["width"], 160)
        r = await mcp.call_tool(
            "resize_image", {"image_path": self.img, "width": 80, "height": 60}
        )
        self.assertEqual(r.structured_content["final_height"], 60)

    async def test_all_tools_registered(self):
        names = {t.name for t in await mcp.list_tools()}
        for name in (
            "resize_image",
            "crop_image",
            "rotate_flip_image",
            "convert_format",
            "compress_image",
            "generate_thumbnail",
            "apply_filter",
            "add_watermark",
            "extract_palette",
            "get_image_properties",
            "get_exif_metadata",
            "strip_image_metadata",
            "ocr_extract_text",
        ):
            self.assertIn(name, names)

    async def test_tools_smoke(self):
        cases = [
            (
                "crop_image",
                {"image_path": self.img, "width": 40, "height": 20},
            ),
            (
                "rotate_flip_image",
                {"image_path": self.img, "rotate_degrees": 90},
            ),
            (
                "convert_format",
                {"image_path": self.img, "target_format": "png"},
            ),
            ("compress_image", {"image_path": self.img, "quality": 50}),
            ("generate_thumbnail", {"image_path": self.img, "sizes": [32]}),
            (
                "apply_filter",
                {"image_path": self.img, "filter": "grayscale"},
            ),
            (
                "add_watermark",
                {
                    "image_path": self.img,
                    "watermark_type": "text",
                    "content": "t",
                },
            ),
            ("extract_palette", {"image_path": self.img, "num_colors": 2}),
            ("get_exif_metadata", {"image_path": self.img}),
            ("strip_image_metadata", {"image_path": self.img}),
            ("ocr_extract_text", {"image_path": self.img}),
        ]
        for name, args in cases:
            with self.subTest(tool=name):
                r = await mcp.call_tool(name, args)
                self.assertIsNotNone(r.structured_content)

    async def test_resource_and_prompts(self):
        res = await mcp.read_resource("config://formats")
        self.assertIn("png", res.contents[0].content)
        names = {p.name for p in await mcp.list_prompts()}
        self.assertTrue(
            {"describe_image", "thumbnail_plan", "audit_privacy"} <= names
        )


if __name__ == "__main__":
    unittest.main()
