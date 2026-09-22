#!/usr/bin/env python3
"""Resize raster images and convert them to WebP."""

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageOps


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}
SKIPPED_DIRECTORIES = {"_site", ".git", ".jekyll-cache"}


def image_paths(inputs, recursive):
    for input_path in inputs:
        path = Path(input_path)
        if path.is_file():
            yield path
        elif path.is_dir():
            pattern = "**/*" if recursive else "*"
            yield from (
                candidate
                for candidate in path.glob(pattern)
                if candidate.is_file() and not any(part in SKIPPED_DIRECTORIES for part in candidate.parts)
            )
        else:
            print(f"Skipping missing path: {path}", file=sys.stderr)


def output_path(source, output_dir):
    if output_dir:
        return Path(output_dir) / f"{source.stem}.webp"
    return source.with_suffix(".webp")


def convert_image(source, destination, max_width, max_height, quality, dry_run):
    if source.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return False

    if source.suffix.lower() == ".webp" and destination.resolve() == source.resolve():
        return False

    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image)
        image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        image = image.convert("RGBA" if "A" in image.getbands() else "RGB")

        if dry_run:
            print(f"Would convert: {source} -> {destination}")
            return True

        destination.parent.mkdir(parents=True, exist_ok=True)
        image.save(destination, "WEBP", quality=quality, method=6)
        print(f"Converted: {source} -> {destination}")
        return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="Image files or directories to process")
    parser.add_argument("-r", "--recursive", action="store_true", help="Scan directories recursively")
    parser.add_argument("-o", "--output-dir", type=Path, help="Write all WebP files to this directory")
    parser.add_argument("--max-width", type=int, default=2400, help="Maximum output width (default: 2400)")
    parser.add_argument("--max-height", type=int, default=2400, help="Maximum output height (default: 2400)")
    parser.add_argument("-q", "--quality", type=int, default=82, help="WebP quality from 0 to 100 (default: 82)")
    parser.add_argument("--dry-run", action="store_true", help="List conversions without writing files")
    args = parser.parse_args()

    if not 0 <= args.quality <= 100:
        parser.error("quality must be between 0 and 100")
    if args.max_width < 1 or args.max_height < 1:
        parser.error("max width and max height must be positive")

    converted = 0
    for source in image_paths(args.paths, args.recursive):
        destination = output_path(source, args.output_dir)
        if convert_image(source, destination, args.max_width, args.max_height, args.quality, args.dry_run):
            converted += 1

    print(f"Processed {converted} image(s).")


if __name__ == "__main__":
    main()