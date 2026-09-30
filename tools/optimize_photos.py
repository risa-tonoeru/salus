#!/usr/bin/env python3
"""元写真（HEIC/JPEG）をWeb用JPEGにして images/ に書き出す。

使い方: python3 tools/optimize_photos.py <元写真> <出力名> [長辺px]
例:     python3 tools/optimize_photos.py photos/IMG_0373.HEIC hero.jpg 1600

- 向き（EXIF Orientation）を画素に反映する
- 位置情報などのメタデータは書き出さない
"""
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    src, name = sys.argv[1], sys.argv[2]
    size = int(sys.argv[3]) if len(sys.argv) > 3 else 1200
    out = os.path.join(ROOT, "images", name)
    with tempfile.TemporaryDirectory() as tmp:
        jpg = os.path.join(tmp, "src.jpg")
        # PIL は HEIC を読めないので、sips で一旦 JPEG にする
        subprocess.run(["sips", "-s", "format", "jpeg", src, "--out", jpg], check=True, capture_output=True)
        im = ImageOps.exif_transpose(Image.open(jpg)).convert("RGB")
    im.thumbnail((size, size), Image.LANCZOS)
    im.save(out, "JPEG", quality=80, optimize=True, progressive=True)
    print(f"{name}: {im.width}x{im.height} {os.path.getsize(out) // 1024}KB")


if __name__ == "__main__":
    main()
