"""
To remove exif data from gallery use:
exiftool -all= -overwrite_original -r themes/mytheme/assets/gallery
"""

from pathlib import Path
import subprocess

# Art-Site/
ROOT = Path(__file__).resolve().parent.parent / "themes/mytheme/assets/gallery"

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp",
    ".tif", ".tiff", ".heic", ".heif"
}

images_scanned = 0
images_with_location = []

for path in sorted(ROOT.rglob("*")):
    if not path.is_file():
        continue

    if path.suffix.lower() not in IMAGE_EXTENSIONS:
        continue

    images_scanned += 1

    result = subprocess.run(
        [
            "exiftool",
            "-GPS:all",
            "-s",
            "-S",
            str(path),
        ],
        capture_output=True,
        text=True,
    )

    if result.stdout.strip():
        images_with_location.append(path)


print("=" * 70)
print("SCAN COMPLETE")
print("=" * 70)
print(f"Images scanned:            {images_scanned}")
print(f"Images with location data: {len(images_with_location)}")
print()

if images_with_location:
    print("⚠️  IMAGES WITH LOCATION DATA:")
    print()

    for path in images_with_location:
        print(f"  - {path}")

    print()
    print("⚠️  WARNING: One or more images contain GPS/location data.")
else:
    print("✓ No images contain GPS/location data.")
# Art-Site/
ROOT = Path(__file__).resolve().parent.parent / "themes/mytheme/assets/gallery"

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp",
    ".tif", ".tiff", ".heic", ".heif"
}

images_scanned = 0
images_with_location = []

for path in sorted(ROOT.rglob("*")):
    if not path.is_file():
        continue

    if path.suffix.lower() not in IMAGE_EXTENSIONS:
        continue

    images_scanned += 1

    result = subprocess.run(
        [
            "exiftool",
            "-GPS:all",
            "-s",
            "-S",
            str(path),
        ],
        capture_output=True,
        text=True,
    )

    if result.stdout.strip():
        images_with_location.append(path)


print("=" * 70)
print("SCAN COMPLETE")
print("=" * 70)
print(f"Images scanned:            {images_scanned}")
print(f"Images with location data: {len(images_with_location)}")
print()

if images_with_location:
    print("⚠️  IMAGES WITH LOCATION DATA:")
    print()

    for path in images_with_location:
        print(f"  - {path}")

    print()
    print("⚠️  WARNING: One or more images contain GPS/location data.")
else:
    print("✓ No images contain GPS/location data.")