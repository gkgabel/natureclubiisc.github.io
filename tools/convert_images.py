#!/usr/bin/env python3
"""Resize raster images and convert them to WebP."""

import argparse
from io import BytesIO
import shutil
import sys
import uuid
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


# AI-generated: compute destination path preserving relative subdirectories when output_dir is provided
def output_path(source, output_dir, input_paths=None, preserve_extension=False):
    if not output_dir:
        return source.with_suffix(".webp")
    rel = Path(source.name)
    for base in input_paths or []:
        base_dir = Path(base).resolve()
        if base_dir.is_dir():
            try:
                rel = source.resolve().relative_to(base_dir)
                break
            except ValueError:
                pass
    suffix = source.suffix if preserve_extension else ".webp"
    return Path(output_dir) / rel.with_suffix(suffix)


def numbered_name(source, number, prefix=""):
    """Return a numbered filename while preserving the source extension."""
    return f"{prefix}{number}{source.suffix.lower()}"


def rename_images(sources, start_number, prefix, dry_run):
    """Rename images in place without collisions, preserving their extensions."""
    sources = sorted(sources, key=lambda path: str(path).lower())
    operations = [
        (source, source.with_name(numbered_name(source, start_number + index, prefix)))
        for index, source in enumerate(sources)
    ]
    source_paths = {source.resolve() for source, _ in operations}
    destination_paths = [destination.resolve() for _, destination in operations]
    if len(destination_paths) != len(set(destination_paths)):
        raise FileExistsError("multiple images would receive the same filename")
    for source, destination in operations:
        if destination.exists() and destination.resolve() not in source_paths:
            raise FileExistsError(f"refusing to overwrite existing file: {destination}")

    if dry_run:
        for source, destination in operations:
            print(f"Would rename: {source} -> {destination}")
        return len(operations)

    staged = []
    try:
        for source, destination in operations:
            temporary = source.with_name(f".{source.name}.{uuid.uuid4().hex}.rename")
            source.rename(temporary)
            staged.append((temporary, destination))
        for temporary, destination in staged:
            temporary.rename(destination)
            print(f"Renamed: {temporary.name} -> {destination}")
    except Exception:
        for temporary, destination in reversed(staged):
            if temporary.exists():
                temporary.rename(destination if not destination.exists() else temporary)
        raise
    return len(operations)


# AI-generated: normalize image orientation, color band mode, and thumbnail dimensions
def prepare_image(source, max_width, max_height):
    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image)
        image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        has_alpha = "A" in image.getbands()
        return image.convert("RGBA" if has_alpha else "RGB")


# AI-generated: save image to an in-memory buffer using destination format settings
def encode_image(image, destination_ext, quality):
    output = BytesIO()
    if destination_ext == ".png":
        image.save(output, "PNG", optimize=True)
    elif destination_ext in {".jpg", ".jpeg"}:
        image.convert("RGB").save(output, "JPEG", quality=quality, optimize=True)
    else:
        image.save(output, "WEBP", quality=quality, method=6)
    return output


# AI-generated: convert image to WebP with opt-in deletion of original
def convert_image(source, destination, max_width, max_height, quality, dry_run, delete_original=False):
    if source.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return False
    if source.suffix.lower() == ".webp" and destination.resolve() == source.resolve():
        return False

    image = prepare_image(source, max_width, max_height)
    if dry_run:
        print(f"Would convert: {source} -> {destination}")
        return True

    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, "WEBP", quality=quality, method=6)
    if delete_original and source.suffix.lower() != ".webp" and source.resolve() != destination.resolve():
        source.unlink()
        print(f"Removed original: {source}")
    print(f"Converted: {source} -> {destination}")
    return True


# AI-generated: iteratively compress image quality and dimensions to meet max_bytes target
def optimize_image(source, destination, max_width, max_height, quality, max_bytes, dry_run):
    dest_ext = destination.suffix.lower()
    if source.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
        print(f"Skipping size optimization for unsupported format: {source}")
        return False

    source_size = source.stat().st_size
    if source_size <= max_bytes:
        if source.resolve() != destination.resolve():
            if dry_run:
                print(f"Would copy already compliant image: {source} -> {destination}")
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
        print(f"Already compliant (<= {max_bytes} bytes): {source}")
        return True

    image = prepare_image(source, max_width, max_height)
    width, height = image.size
    current_quality = quality
    is_png = dest_ext == ".png"

    while True:
        output = encode_image(image, dest_ext, current_quality)
        if output.tell() <= max_bytes:
            break
        if not is_png and current_quality > 25:
            current_quality = max(25, current_quality - 5)
            continue
        if min(width, height) <= 320:
            print(f"Could not reduce below {max_bytes} bytes: {source} ({output.tell()} bytes)")
            return False
        width, height = int(width * 0.85), int(height * 0.85)
        image = image.resize((width, height), Image.Resampling.LANCZOS)
        current_quality = quality

    if dry_run:
        print(f"Would optimize: {source} ({source.stat().st_size} bytes) -> {destination} ({output.tell()} bytes)")
        return True

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(output.getvalue())
    print(f"Optimized: {source} ({source.stat().st_size} bytes) -> {destination} ({destination.stat().st_size} bytes)")
    return True


# AI-generated: predefined dimension and quality presets
PRESETS = {
    "small": {"max_width": 1000, "max_height": 1000, "quality": 80},
    "standard": {"max_width": 1600, "max_height": 1200, "quality": 82},
    "medium": {"max_width": 1600, "max_height": 1200, "quality": 82},
    "large": {"max_width": 2400, "max_height": 2400, "quality": 82},
    "hero": {"max_width": 2400, "max_height": 2400, "quality": 85},
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="Image files or directories to process")
    parser.add_argument("-r", "--recursive", action="store_true", help="Scan directories recursively")
    rename_group = parser.add_mutually_exclusive_group()
    rename_group.add_argument("--rename", action="store_true", help="Number converted files sequentially (for example, 1.webp, 2.webp)")
    rename_group.add_argument("--rename-only", action="store_true", help="Rename images in place sequentially without converting them")
    parser.add_argument("--name-prefix", default="", help="Prefix for numbered filenames (used with --rename or --rename-only)")
    parser.add_argument("--start-number", type=int, default=1, help="First number for sequential filenames (default: 1)")
    parser.add_argument("-o", "--output-dir", type=Path, help="Write all WebP files to this directory")
    parser.add_argument("--preset", choices=["small", "standard", "medium", "large", "hero"], help="Sizing and quality preset (small: 1000x1000 q80, standard/medium: 1600x1200 q82, large/hero: 2400x2400 q82-85)")
    parser.add_argument("--max-width", type=int, default=2400, help="Maximum output width (default: 2400)")
    parser.add_argument("--max-height", type=int, default=2400, help="Maximum output height (default: 2400)")
    parser.add_argument("-q", "--quality", type=int, default=82, help="WebP quality from 0 to 100 (default: 82)")
    parser.add_argument("--max-bytes", type=int, help="Keep each image at or below this byte size")
    parser.add_argument("--in-place", action="store_true", help="Overwrite source files in max-bytes mode")
    parser.add_argument("--delete-original", action="store_true", help="Remove non-WebP source file after successful WebP conversion")
    parser.add_argument("--dry-run", action="store_true", help="List conversions without writing files")
    args = parser.parse_args()

    if args.preset:
        cfg = PRESETS[args.preset]
        if "--max-width" not in sys.argv:
            args.max_width = cfg["max_width"]
        if "--max-height" not in sys.argv:
            args.max_height = cfg["max_height"]
        if "-q" not in sys.argv and "--quality" not in sys.argv:
            args.quality = cfg["quality"]

    if not 0 <= args.quality <= 100:
        parser.error("quality must be between 0 and 100")
    if args.max_width < 1 or args.max_height < 1:
        parser.error("max width and max height must be positive")
    if args.max_bytes is not None and args.max_bytes < 1:
        parser.error("max bytes must be positive")
    if args.max_bytes is not None and args.in_place and args.output_dir:
        parser.error("--in-place and --output-dir cannot be used together")
    if args.max_bytes is not None and not args.in_place and not args.output_dir:
        parser.error("max-bytes mode requires --in-place or --output-dir")
    if args.start_number < 0:
        parser.error("start number must be zero or greater")
    if args.name_prefix and not (args.rename or args.rename_only):
        parser.error("--name-prefix requires --rename or --rename-only")
    if args.start_number != 1 and not (args.rename or args.rename_only):
        parser.error("--start-number requires --rename or --rename-only")
    if args.rename_only and args.output_dir:
        parser.error("--rename-only cannot be used with --output-dir")

    sources = list(image_paths(args.paths, args.recursive))
    sources = [source for source in sources if source.suffix.lower() in SUPPORTED_EXTENSIONS]
    if args.rename_only:
        try:
            renamed = rename_images(sources, args.start_number, args.name_prefix, args.dry_run)
        except FileExistsError as error:
            parser.error(str(error))
        print(f"Processed {renamed} image(s).")
        return

    converted = 0
    for index, source in enumerate(sources):
        if args.max_bytes is not None:
            destination = source if args.in_place else output_path(
                source,
                args.output_dir,
                args.paths,
                preserve_extension=True,
            )
            if args.rename:
                destination = destination.with_name(numbered_name(destination, args.start_number + index, args.name_prefix))
            processed = optimize_image(
                source,
                destination,
                args.max_width,
                args.max_height,
                args.quality,
                args.max_bytes,
                args.dry_run,
            )
        else:
            destination = output_path(source, args.output_dir, args.paths)
            if args.rename:
                destination = destination.with_name(numbered_name(destination, args.start_number + index, args.name_prefix))
            processed = convert_image(
                source,
                destination,
                args.max_width,
                args.max_height,
                args.quality,
                args.dry_run,
                args.delete_original,
            )
        if processed:
            converted += 1

    print(f"Processed {converted} image(s).")


if __name__ == "__main__":
    main()