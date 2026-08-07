#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re
import struct
from typing import Iterable

try:
    from PIL import Image
except Exception:  # Pillow is optional
    Image = None

ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = ROOT / "static" / "img" / "gallery"
OUTPUT_DIR = ROOT / "content" / "gallery"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff"}
SMALL_WORDS = {"a", "an", "and", "as", "at", "but", "by", "for", "in", "nor", "of", "on", "or", "the", "to", "up"}


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[\s_]+", "-", value)
    value = re.sub(r"[^a-z0-9-]", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-") or "untitled"


def titleize(value: str) -> str:
    cleaned = re.sub(r"[-_]+", " ", value).strip()
    words = [w for w in cleaned.split() if w]
    if not words:
        return "Untitled"

    titled: list[str] = []
    for i, word in enumerate(words):
        lower = word.lower()
        if i not in (0, len(words) - 1) and lower in SMALL_WORDS:
            titled.append(lower)
        elif word.isupper() and len(word) > 1:
            titled.append(word)
        else:
            titled.append(lower.capitalize())
    return " ".join(titled)


def is_image(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS


def parse_date(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    if not value:
        return None

    for fmt in (
        "%Y:%m:%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue

    if len(value) >= 10:
        maybe = value[:10]
        try:
            return datetime.strptime(maybe, "%Y-%m-%d").date().isoformat()
        except ValueError:
            return None
    return None


def extract_jpeg_size(path: Path) -> tuple[int, int] | None:
    with path.open("rb") as f:
        data = f.read()
    if len(data) < 4 or data[0:2] != b"\xff\xd8":
        return None

    i = 2
    while i < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        while i < len(data) and data[i] == 0xFF:
            i += 1
        if i >= len(data):
            break
        marker = data[i]
        i += 1
        if marker in {0xD8, 0xD9}:  # SOI/EOI
            continue
        if i + 1 >= len(data):
            break
        segment_len = struct.unpack(">H", data[i : i + 2])[0]
        if segment_len < 2 or i + segment_len > len(data):
            break
        if 0xC0 <= marker <= 0xCF and marker not in {0xC4, 0xC8, 0xCC}:
            start = i + 2
            if start + 5 <= len(data):
                height = struct.unpack(">H", data[start + 1 : start + 3])[0]
                width = struct.unpack(">H", data[start + 3 : start + 5])[0]
                return width, height
            break
        i += segment_len
    return None


def extract_png_size(path: Path) -> tuple[int, int] | None:
    with path.open("rb") as f:
        header = f.read(24)
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    width, height = struct.unpack(">II", header[16:24])
    return int(width), int(height)


def get_dimensions(path: Path) -> tuple[int, int] | None:
    if Image is not None:
        try:
            with Image.open(path) as img:
                return img.size
        except Exception:
            pass

    suffix = path.suffix.lower()
    try:
        if suffix == ".png":
            return extract_png_size(path)
        if suffix in {".jpg", ".jpeg"}:
            return extract_jpeg_size(path)
    except Exception:
        return None
    return None


def get_orientation(path: Path) -> str | None:
    size = get_dimensions(path)
    if not size:
        return None
    width, height = size
    if width == height:
        return "square"
    return "landscape" if width > height else "portrait"


def get_metadata(path: Path) -> tuple[str | None, str | None, list[str]]:
    date_value = None
    medium = None
    tags: list[str] = []

    if Image is not None:
        try:
            with Image.open(path) as img:
                exif = img.getexif() or {}
                exif_data = {str(k): v for k, v in exif.items()}
                date_value = parse_date(
                    str(exif_data.get("36867") or exif_data.get("36868") or exif_data.get("306") or "")
                )

                info = {str(k).lower(): str(v) for k, v in (img.info or {}).items()}
                if not date_value:
                    for key in ("creation time", "date:create", "date", "timestamp"):
                        date_value = parse_date(info.get(key))
                        if date_value:
                            break

                medium = info.get("description") or info.get("comment") or info.get("software")
                keyword_blob = info.get("keywords") or info.get("subject") or ""
                if keyword_blob:
                    tags = [t.strip().lower() for t in re.split(r"[,;|]", keyword_blob) if t.strip()]
        except Exception:
            pass

    if not date_value:
        try:
            date_value = datetime.fromtimestamp(path.stat().st_mtime).date().isoformat()
        except Exception:
            date_value = None

    return date_value, medium, tags


def to_image_url(path: Path) -> str:
    return "/img/gallery/" + path.relative_to(INPUT_DIR).as_posix()


def yaml_list(values: Iterable[str], indent: str = "") -> list[str]:
    lines: list[str] = []
    for value in values:
        lines.append(f'{indent}- "{value}"')
    return lines


def build_markdown(
        title: str,
        image_urls: list[str],
        orientation: str | None,
        date: str | None,
        medium: str | None,
        tags: list[str],
) -> str:
    orientation_value = orientation or "landscape"

    lines = [
        "---",
        f'title: "{title}"',
    ]

    if len(image_urls) == 1:
        lines.append(f'image: "{image_urls[0]}"')
    else:
        lines.append("image:")
        lines.extend(yaml_list(image_urls, indent="  "))

    if medium:
        escaped_medium = medium.replace('"', '\\"')
        lines.append(f'medium: "{escaped_medium}"')

    if tags:
        joined = ", ".join(f'"{t}"' for t in tags)
        lines.append(f"tags: [{joined}]")

    lines.extend(
        [
            f'orientation: "{orientation_value}"',
            "featured: false",
        ]
    )

    if date:
        lines.append(f"date: {date}")

    lines.extend(["---", ""])
    return "\n".join(lines)


def write_post(output_path: Path, content: str) -> bool:
    if output_path.exists():
        print(f"[SKIP] Already exists: {output_path}")
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return True


def process_single_image(path: Path) -> bool:
    slug = slugify(path.stem)
    title = titleize(path.stem)
    image_url = to_image_url(path)
    date, medium, tags = get_metadata(path)
    orientation = get_orientation(path)

    output_path = OUTPUT_DIR / f"{slug}.md"
    markdown = build_markdown(
        title, [image_url], orientation, date, medium, tags
    )

    print(f"[WRITE] {output_path}")
    return write_post(output_path, markdown)


def process_directory(path: Path) -> bool:
    images = sorted(p for p in path.rglob("*") if is_image(p))
    if not images:
        print(f"[SKIP] No images found in directory: {path}")
        return False

    slug = slugify(path.name)
    title = titleize(path.name)
    image_urls = [to_image_url(p) for p in images]

    first_with_metadata = images[0]
    date = medium = None
    tags: list[str] = []

    for candidate in images:
        d, m, t = get_metadata(candidate)

        if d and not date:
            date = d
            first_with_metadata = candidate

        if m and not medium:
            medium = m

        if t and not tags:
            tags = t

        if date and medium and tags:
            break

    orientation = get_orientation(first_with_metadata)
    output_path = OUTPUT_DIR / f"{slug}.md"
    markdown = build_markdown(
        title, image_urls, orientation, date, medium, tags
    )

    print(f"[WRITE] {output_path} ({len(image_urls)} images)")
    return write_post(output_path, markdown)


def main() -> None:
    print("[START] Generating gallery markdown files")
    print(f"[INFO] Input directory:  {INPUT_DIR}")
    print(f"[INFO] Output directory: {OUTPUT_DIR}")

    if not INPUT_DIR.exists():
        print(f"[ERROR] Input directory does not exist: {INPUT_DIR}")
        return

    entries = sorted(
        [p for p in INPUT_DIR.iterdir() if is_image(p) or p.is_dir()],
        key=lambda p: p.name.lower(),
    )

    created = 0
    for entry in entries:
        try:
            if entry.is_dir():
                print(f"[STEP] Processing folder: {entry.name}")
                created += int(process_directory(entry))
            else:
                print(f"[STEP] Processing image: {entry.name}")
                created += int(process_single_image(entry))
        except Exception as exc:
            print(f"[ERROR] Failed to process {entry}: {exc}")

    print(f"[DONE] Total markdown files created: {created}")


if __name__ == "__main__":
    main()
