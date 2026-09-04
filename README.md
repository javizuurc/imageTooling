# ImageTooling MCP

MCP server (FastMCP + Pillow) to speed up image work in web development: geometry, format, effects, metadata, and OCR.

- Version: `0.1.0`
- Python: `>=3.13` (Docker: `python:3.13-slim-bookworm`)
- Deps: `fastmcp>=4.0.2`, `pillow>=12.3.0`
- Entrypoint: `python -m image_mcp.server` (paquete instalado)
- License: PolyForm-Noncommercial-1.0.0 (see LICENSE)

## Quickstart

```sh
docker build -t imagetooling .
docker run -i --rm --name ImageToolingMCP --mount type=bind,src=.,dst=/workspace imagetooling
```

Local: `uv sync && uv run python -m image_mcp.server`.

The server currently calls `mcp.run()` without a transport, so FastMCP uses
stdio (not HTTP, SSE, or streamable HTTP). Therefore this deployment does not
publish port `6742`; adding `-p 6742:6742` would not expose a listening
service. The container name is `ImageToolingMCP` as requested.

`image_path` is a path in the shared filesystem (e.g. `/workspace/img/photo.jpg`). Outputs are written next to the source and returned as `output_path`. Extensions are dotless (`png`). OCR needs tesseract installed, otherwise it returns `OCR_MISSING_ERROR`.

## Tools (13)

| Tool | What it does |
| ---- | ------------ |
| `get_image_properties` | Technical/structural metadata (start here) |
| `get_exif_metadata` | Capture/device metadata (may not exist) |
| `strip_image_metadata` | Removes EXIF/info (read + strip only, no tag writing) |
| `resize_image` | Resize to width x height |
| `crop_image` | Crop region (x, y, width, height) |
| `rotate_flip_image` | Rotate / flip |
| `convert_format` | Convert between formats (`target_format`, optional `quality`) |
| `compress_image` | Reduce weight without changing dimensions (`quality=80`) |
| `generate_thumbnail` | Thumbnails (default sizes `64,128,256`) |
| `apply_filter` | Basic filters (`filter`, optional `intensity`) |
| `add_watermark` | Text or image overlay (`watermark_type`, `content`, `position`, `opacity`) |
| `extract_palette` | Dominant colors (`num_colors=5`, `format=hex`) |
| `ocr_extract_text` | Extract text (`language=auto`, requires tesseract) |

**Resources:** `config://formats` (Pillow-readable extensions in this deploy).
**Prompts:** `describe_image(image_path)`, `thumbnail_plan(image_path, sizes)`.

## Security note

Tools operate on file paths you pass (`image_path`, `output_path`, watermark `content`). No sandbox, no size limits; outputs are written next to the source. `get_exif`/`get_image_properties` can return GPS metadata. Only mount what you intend to expose.
