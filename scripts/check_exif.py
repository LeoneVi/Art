"""
To remove EXIF data from all gallery images:
exiftool -EXIF= -overwrite_original -r themes/mytheme/assets/gallery
"""


from pathlib import Path
import subprocess

# Find the repository root from the location of this script
REPO_ROOT = Path(__file__).resolve().parent.parent

ROOT = REPO_ROOT / "themes" / "mytheme" / "assets" / "gallery"

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp",
    ".tif", ".tiff", ".heic", ".heif"
}

images_scanned = 0
images_with_exif = []

print(f"Scanning for exif data in gallery...")
print()

if not ROOT.is_dir():
    print("Gallery directory does not exist.")
    raise SystemExit(1)

for path in sorted(ROOT.rglob("*")):
    if not path.is_file():
        continue

    if path.suffix.lower() not in IMAGE_EXTENSIONS:
        continue

    images_scanned += 1

    result = subprocess.run(
        [
            "exiftool",
            "-EXIF:all",
            "-s",
            "-S",
            str(path),
        ],
        capture_output=True,
        text=True,
    )

    if result.stdout.strip():
        images_with_exif.append(path)


print("=" * 70)
print("EXIF SCAN COMPLETE")
print("=" * 70)
print(f"Images scanned:        {images_scanned}")
print(f"Images with EXIF data: {len(images_with_exif)}")
print()

if images_with_exif:
    print("⚠️  IMAGES WITH EXIF DATA:")
    print()

    for path in images_with_exif:
        print(f"  - {path}")

    print()
    print("EXIF data detected.")
    raise SystemExit(1)

print("✓ No EXIF data found.")
raise SystemExit(0)
