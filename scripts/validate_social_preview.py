#!/usr/bin/env python3
"""Validate the production sharing-card contract without third-party packages."""

from __future__ import annotations

import json
import hashlib
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MANIFEST = ROOT / "assets" / "social-preview-manifest.json"


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise AssertionError(f"{path.relative_to(ROOT)} is not a valid PNG")
    return struct.unpack(">II", data[16:24])


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    page = INDEX.read_text(encoding="utf-8")
    contract = json.loads(MANIFEST.read_text(encoding="utf-8"))
    image_path = ROOT / contract["image_path"]
    icon_path = ROOT / contract["brand_icon_path"]
    touch_path = ROOT / contract["apple_touch_icon_path"]

    assert png_size(image_path) == (1200, 630), "social preview must be 1200×630"
    assert png_size(icon_path) == (512, 512), "brand icon must be 512×512"
    assert png_size(touch_path) == (180, 180), "Apple touch icon must be 180×180"
    assert sha256(image_path) == contract["image_sha256"], "social preview differs from the approved asset"
    assert sha256(icon_path) == contract["brand_icon_sha256"], "brand icon differs from the approved asset"
    assert sha256(touch_path) == contract["apple_touch_icon_sha256"], "Apple touch icon differs from the approved asset"

    required = [
        'property="og:site_name" content="EnergizeOS"',
        f'property="og:title" content="{contract["title_html"]}"',
        f'property="og:description" content="{contract["description"]}"',
        f'property="og:image" content="{contract["image_url"]}"',
        f'property="og:image:secure_url" content="{contract["image_url"]}"',
        'property="og:image:type" content="image/png"',
        'property="og:image:width" content="1200"',
        'property="og:image:height" content="630"',
        f'name="twitter:title" content="{contract["title_html"]}"',
        f'name="twitter:description" content="{contract["description"]}"',
        f'name="twitter:image" content="{contract["image_url"]}"',
        f'href="/{contract["apple_touch_icon_path"]}"',
        f'"logo":"{contract["brand_icon_url"]}"',
    ]
    missing = [entry for entry in required if entry not in page]
    assert not missing, "missing social-preview contract entries: " + ", ".join(missing)
    assert "assets/og-image.png" not in page, "legacy preview URL must not remain in metadata"
    print("social preview contract: OK")


if __name__ == "__main__":
    main()
