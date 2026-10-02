#!/usr/bin/env python3
"""Create and refresh data-driven Jekyll event posts."""

import argparse
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError as error:
    raise SystemExit(
        "PyYAML is required. Install dependencies with "
        "python3 -m pip install -r tools/requirements-image.txt"
    ) from error


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".tif", ".tiff"}


# AI-generated: sanitize input string into a lowercase URL slug
def slugify(value):
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", normalized.lower())).strip("-")


# AI-generated: compute normalized slug from date and title with validation
def event_slug(event_date, title):
    title_slug = slugify(title)
    if not title_slug:
        raise ValueError(f"Event title '{title}' produces an empty slug; provide a descriptive title.")
    return f"{event_date.isoformat()}-{title_slug}"


# AI-generated: list supported image files deterministically
def image_files(image_dir):
    return sorted(
        path for path in image_dir.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


# AI-generated: convert filename stem to title-case display text
def display_name(path):
    return re.sub(r"[-_]+", " ", path.stem).strip().title()


# AI-generated: resolve gallery data path
def data_path(root, slug):
    return root / "_data" / "event_galleries" / f"{slug}.yml"


# AI-generated: load existing gallery data
def load_gallery(path):
    if not path.exists():
        return {"sections": []}
    with path.open(encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
        return data if isinstance(data, dict) else {"sections": []}


# AI-generated: synchronize YAML gallery records with event image folder, assigning sequential section IDs by default
def refresh_gallery(root, slug, title=None, event_date=None):
    image_dir = root / "images" / "event_images" / slug
    metadata_path = data_path(root, slug)
    image_dir.mkdir(parents=True, exist_ok=True)
    gallery = load_gallery(metadata_path)

    existing = {
        img["path"]: img
        for item in gallery.get("images", []) + [i for s in gallery.get("sections", []) for i in s.get("images", [])]
        if (img := item).get("path")
    }

    def make_entry(path):
        p = f"/images/event_images/{slug}/{path.name}"
        prev = existing.get(p, {})
        return {"path": p, "alt": prev.get("alt") or display_name(path), "caption": prev.get("caption", "")}

    disk_files = image_files(image_dir)
    refreshed = {k: v for k, v in gallery.items() if k not in {"sections", "images", "title", "date"}}

    seen = set()
    updated_sections = []
    numeric_ids = []

    for sec in gallery.get("sections", []):
        sec_id = sec.get("id")
        if isinstance(sec_id, int):
            numeric_ids.append(sec_id)
        elif isinstance(sec_id, str) and sec_id.isdigit():
            numeric_ids.append(int(sec_id))
        imgs = [img for img in sec.get("images", []) if (p := img.get("path")) and (root / p.lstrip("/")).is_file() and not seen.add(p)]
        updated_sections.append({**sec, "images": imgs})

    existing_unsectioned = [img for img in gallery.get("images", []) if (p := img.get("path")) and (root / p.lstrip("/")).is_file() and not seen.add(p)]

    # New files on disk not seen in sections or unsectioned images
    new_files = [f for f in disk_files if f"/images/event_images/{slug}/{f.name}" not in seen]
    new_entries = [make_entry(f) for f in new_files]

    next_id = max(numeric_ids, default=0) + 1
    for entry in new_entries:
        updated_sections.append({
            "id": next_id,
            "images": [entry],
        })
        next_id += 1

    refreshed["sections"] = updated_sections
    if existing_unsectioned:
        refreshed["images"] = existing_unsectioned

    total = sum(len(s.get("images", [])) for s in updated_sections) + len(existing_unsectioned)

    if title or gallery.get("title"):
        refreshed["title"] = title or gallery["title"]
    if event_date or gallery.get("date"):
        refreshed["date"] = event_date.isoformat() if event_date else gallery["date"]

    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    with metadata_path.open("w", encoding="utf-8") as stream:
        yaml.safe_dump(refreshed, stream, sort_keys=False, allow_unicode=True)
    print(f"Refreshed {metadata_path} with {total} image(s).")


# AI-generated: build post markdown with populated metadata and stripped blank front matter lines
def post_content(root, title, event_date, tags, author, slug):
    template = (root / "tools" / "templates" / "event_post.md.template").read_text(encoding="utf-8")
    replacements = {
        "{{ title }}": title.replace('"', '\\"'),
        "{{ date }}": event_date.isoformat(),
        "{{ tags_line }}": f"tags: {' '.join(tags)}" if tags else "",
        "{{ author_line }}": f"author: {author}" if author else "",
        "{{ slug }}": slug,
        "{{ display_date }}": f"{event_date.day} {event_date.strftime('%B, %Y')}",
    }
    for marker, value in replacements.items():
        template = template.replace(marker, value)
    parts = template.split("---", 2)
    if len(parts) >= 3:
        front_matter = "\n".join(line for line in parts[1].splitlines() if line.strip())
        template = f"---\n{front_matter}\n---" + parts[2]
    return template


# AI-generated: create new event post, matching image folder, and gallery YAML
def create_event(args):
    root = args.root.resolve()
    event_date = date.fromisoformat(args.date)
    slug = event_slug(event_date, args.title)
    post_path = root / "_posts" / f"{slug}.md"
    image_dir = root / "images" / "event_images" / slug
    metadata_path = data_path(root, slug)
    collisions = [path for path in (post_path, image_dir, metadata_path) if path.exists()]
    if collisions:
        names = "\n".join(f"  - {path.relative_to(root)}" for path in collisions)
        raise SystemExit(f"Event already exists; refusing to overwrite:\n{names}")

    image_dir.mkdir(parents=True)
    post_path.parent.mkdir(parents=True, exist_ok=True)
    post_path.write_text(
        post_content(root, args.title, event_date, args.tags, args.author, slug),
        encoding="utf-8",
    )
    refresh_gallery(root, slug, args.title, event_date)
    print(f"Created event post: {post_path.relative_to(root)}")
    print(f"Add images to: {image_dir.relative_to(root)}")
    print(f"Then run: python3 tools/create_event_post.py refresh --slug {slug}")


def refresh_event(args):
    root = args.root.resolve()
    slug = slugify(args.slug)
    image_dir = root / "images" / "event_images" / slug
    if not image_dir.is_dir():
        raise SystemExit(f"Event image folder not found: {image_dir.relative_to(root)}")
    refresh_gallery(root, slug)


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root (default: current directory)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create", help="Create a post, image folder, and gallery data file")
    create.add_argument("--title", required=True, help="Event title")
    create.add_argument("--date", required=True, help="Event date in YYYY-MM-DD format")
    create.add_argument("--tags", nargs="*", default=[], help="Optional space-separated tags")
    create.add_argument("--author", help="Optional post author")
    create.set_defaults(function=create_event)

    refresh = subparsers.add_parser("refresh", help="Add new folder images to an existing gallery data file")
    refresh.add_argument("--slug", required=True, help="Event slug used by the post and image folder")
    refresh.set_defaults(function=refresh_event)
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.function(args)
    except ValueError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
