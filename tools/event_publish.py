#!/usr/bin/env python3
"""Shared, staged publishing operations for the local event image workflow."""

import hashlib
import os
import re
import shutil
import tempfile
from datetime import date
from pathlib import Path

import yaml

from tools.convert_images import PRESETS, SUPPORTED_EXTENSIONS, convert_image, optimize_image
from tools.create_event_post import event_slug, post_content, slugify


DEFAULT_CONFIG = {
    "convert_to_webp": True,
    "enforce_max_bytes": True,
    "max_bytes": 307200,
    "preset": "standard",
    "quality": 82,
    "max_width": 1600,
    "max_height": 1200,
    "quality_floor": 25,
}


class PublishError(ValueError):
    """Raised when a publish cannot be completed safely."""


# AI-generated: load simple repository defaults without adding a config dependency.
def load_workflow_config(root):
    config = DEFAULT_CONFIG.copy()
    explicit = {}
    path = Path(root) / "tools" / "image_workflow.conf"
    if not path.exists():
        return config
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or "=" not in line:
            continue
        key, value = (part.strip() for part in line.split("=", 1))
        if key not in config:
            continue
        if isinstance(config[key], bool):
            explicit[key] = value.lower() in {"1", "true", "yes", "on"}
        elif isinstance(config[key], int):
            explicit[key] = int(value)
        else:
            explicit[key] = value
    config.update(explicit)
    if config["preset"] in PRESETS:
        config.update({key: value for key, value in PRESETS[config["preset"]].items() if key not in explicit})
    return config


# AI-generated: merge per-publish settings and validate image processing limits.
def resolved_config(root, overrides=None):
    config = load_workflow_config(root)
    for key, value in (overrides or {}).items():
        if value is not None:
            config[key] = value
    if config["max_bytes"] < 1 or config["max_width"] < 1 or config["max_height"] < 1:
        raise PublishError("Image limits and dimensions must be positive.")
    if not 0 <= config["quality_floor"] <= config["quality"] <= 100:
        raise PublishError("Quality floor must be between 0 and the configured quality.")
    return config


# AI-generated: reject repository destinations that resolve outside the root.
def safe_destination(root, relative_path):
    root = Path(root).resolve()
    destination = (root / relative_path).resolve()
    try:
        destination.relative_to(root)
    except ValueError as error:
        raise PublishError(f"Destination escapes repository: {relative_path}") from error
    return destination


# AI-generated: identify duplicate uploads without relying on filenames.
def content_hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


# AI-generated: normalize output names and add deterministic collision suffixes.
def safe_image_name(name, extension, used_names, fallback_number):
    stem = Path(name).stem
    normalized = slugify(stem)
    normalized = re.sub(r"-+", "-", normalized).strip("-") or f"image-{fallback_number}"
    extension = extension.lower()
    candidate = f"{normalized}{extension}"
    suffix = 2
    while candidate in used_names:
        candidate = f"{normalized}-{suffix}{extension}"
        suffix += 1
    used_names.add(candidate)
    return candidate


# AI-generated: apply the configured conversion and size policy to one image.
def _process_image(source, destination, config, processing):
    if processing["convert_to_webp"]:
        destination = destination.with_suffix(".webp")
    if processing["enforce_max_bytes"]:
        if source.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
            raise PublishError(f"Cannot enforce the size limit for unsupported format: {source.name}")
        processed = optimize_image(
            source,
            destination,
            config["max_width"],
            config["max_height"],
            config["quality"],
            config["max_bytes"],
            False,
            config["quality_floor"],
        )
    elif processing["convert_to_webp"]:
        processed = convert_image(
            source,
            destination,
            config["max_width"],
            config["max_height"],
            config["quality"],
            False,
        )
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        processed = True
    if not processed or not destination.exists():
        raise PublishError(f"Could not process image '{source.name}' under the configured size limit.")
    if processing["enforce_max_bytes"] and destination.stat().st_size > config["max_bytes"]:
        raise PublishError(
            f"Image '{source.name}' is {destination.stat().st_size} bytes; "
            f"the limit is {config['max_bytes']} bytes."
        )
    return destination


# AI-generated: serialize one image into the Jekyll gallery data shape.
def _metadata_entry(slug, filename, image):
    return {
        "path": f"/images/event_images/{slug}/{filename}",
        "alt": str(image.get("alt", "")).strip(),
        "caption": str(image.get("caption", "")).strip(),
    }


# AI-generated: stage and optionally commit a complete event publication atomically.
def publish_event(root, title, event_date, tags, author, images, options=None, commit=True):
    """Publish a new event atomically from selected image descriptors."""
    root = Path(root).resolve()
    try:
        parsed_date = date.fromisoformat(str(event_date))
    except ValueError as error:
        raise PublishError(f"Invalid event date: {event_date}") from error
    slug = event_slug(parsed_date, title)
    post_path = safe_destination(root, Path("_posts") / f"{slug}.md")
    image_dir = safe_destination(root, Path("images") / "event_images" / slug)
    gallery_path = safe_destination(root, Path("_data") / "event_galleries" / f"{slug}.yml")
    if any(path.exists() for path in (post_path, image_dir, gallery_path)):
        raise PublishError(f"Event already exists; refusing to overwrite: {slug}")
    selected = [image for image in images if image.get("selected", True)]
    if not selected:
        raise PublishError("Select at least one image before finalizing.")

    config = resolved_config(root, options)
    options = options or {}
    processing = {
        "convert_to_webp": options.get("convert_to_webp", config["convert_to_webp"]),
        "enforce_max_bytes": options.get("enforce_max_bytes", config["enforce_max_bytes"]),
    }
    hashes = {}
    duplicate_names = []
    for image in selected:
        source = Path(image["source"]).resolve()
        if source.suffix.lower() not in SUPPORTED_EXTENSIONS or not source.is_file():
            raise PublishError(f"Unsupported or missing image: {source.name}")
        digest = content_hash(source)
        if digest in hashes:
            duplicate_names.append((hashes[digest], source.name))
        else:
            hashes[digest] = source.name
    if duplicate_names:
        duplicate_text = ", ".join(f"{second} duplicates {first}" for first, second in duplicate_names)
        raise PublishError(f"Duplicate image content detected: {duplicate_text}")

    with tempfile.TemporaryDirectory(prefix=".event-publish-", dir=root) as temporary:
        staging = Path(temporary)
        staged_images = staging / "images"
        used_names = set()
        sections = []
        output_files = []
        for index, image in enumerate(selected, start=1):
            source = Path(image["source"])
            extension = ".webp" if processing["convert_to_webp"] else source.suffix.lower()
            filename = safe_image_name(image.get("name") or source.name, extension, used_names, index)
            destination = _process_image(source, staged_images / filename, config, processing)
            output_files.append({"filename": filename, "bytes": destination.stat().st_size})
            sections.append({"id": index, "images": [_metadata_entry(slug, filename, image)]})

        gallery = {"title": title, "sections": sections}
        staged_gallery = staging / "gallery.yml"
        staged_gallery.write_text(yaml.safe_dump(gallery, sort_keys=False, allow_unicode=True), encoding="utf-8")
        staged_post = staging / "post.md"
        staged_post.write_text(post_content(root, title, parsed_date, tags or [], author, slug), encoding="utf-8")
        result = {
            "slug": slug,
            "post": str(post_path.relative_to(root)),
            "gallery": str(gallery_path.relative_to(root)),
            "image_directory": str(image_dir.relative_to(root)),
            "files": output_files,
            "empty_alt": [
                image.get("name") or Path(image["source"]).name
                for image in selected
                if not str(image.get("alt", "")).strip()
            ],
        }
        if not commit:
            return result
        moved = []
        try:
            image_dir.parent.mkdir(parents=True, exist_ok=True)
            post_path.parent.mkdir(parents=True, exist_ok=True)
            gallery_path.parent.mkdir(parents=True, exist_ok=True)
            os.replace(staged_images, image_dir)
            moved.append(image_dir)
            os.replace(staged_gallery, gallery_path)
            moved.append(gallery_path)
            os.replace(staged_post, post_path)
            moved.append(post_path)
        except Exception as error:
            for destination in reversed(moved):
                if destination.is_dir():
                    shutil.rmtree(destination, ignore_errors=True)
                else:
                    destination.unlink(missing_ok=True)
            raise PublishError(f"Could not commit event atomically: {error}") from error

    return result