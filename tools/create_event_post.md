# Create an event post

The event post generator creates the post, image folder, and gallery data file with one command. Install its dependencies first:

```sh
python3 -m pip install -r tools/requirements-image.txt
```

## Create an event

`--title` and `--date` are required. Tags and author are optional:

```sh
python3 tools/create_event_post.py create \
  --title "Campus Bird Walk" \
  --date 2026-09-12 \
  --tags nature-walk bird-walk \
  --author "Gulshan Gabel"
```

The command creates matching paths such as:

```text
_posts/2026-09-12-campus-bird-walk.md
images/event_images/2026-09-12-campus-bird-walk/
_data/event_galleries/2026-09-12-campus-bird-walk.yml
```

It refuses to overwrite an existing post, image folder, or gallery file. Use `--help` to see all options.

## Add images and captions

1. Copy event images into the generated `images/event_images/<event-slug>/` folder.
2. Refresh the gallery data:

```sh
python3 tools/create_event_post.py refresh \
  --slug 2026-09-12-campus-bird-walk
```

3. Edit `_data/event_galleries/<event-slug>.yml` to improve `alt` text and add captions. Running `refresh` preserves your existing edits and adds any new images found in the folder.

## Embed images in your post

You have complete flexibility: display single photos between paragraphs, place multiple comparison photos side-by-side in responsive polaroid rows, or render a full responsive gallery at the bottom.

### Option 1: Clean Single Figures Between Paragraphs

To place a single photo between paragraphs as a polaroid card:

```liquid
{% raw %}{% include event-figure.html section="2" size="medium" %}{% endraw %}
```

- **Automatic metadata:** Automatically loads `caption` and `alt` text from `_data/event_galleries/<slug>.yml`.
- **Automatic path:** Automatically prefixes `/images/event_images/<slug>/`.
- **Display sizing presets (`size`):**
  - `size="small"` (~22rem max-width, ~350px): Ideal for portrait photos, small details, and specimen highlights.
  - `size="medium"` (~34rem max-width, ~540px): Comfortable narrative width fitting body text naturally.
  - `size="large"` (~48rem max-width, ~760px): High-impact landscape and scenic photos.
  - `size="full"` (100% width): Full-bleed column width for banners and wide group shots.
  - `size="original"`: Intrinsic image dimensions without artificial stretching.
- **Smart height cap:** Automatically limits figure images to `75vh` max-height with `object-fit: contain` so portrait photos never overflow the screen height.
- **Custom caption override:** Pass `caption="Your custom caption"` to override the YAML caption for that specific placement:
  ```liquid
  {% raw %}{% include event-figure.html section="6" size="small" caption="Spotted Owlets perched near Main Guest House" %}{% endraw %}
  ```

### Option 2: Side-by-Side Multi-Image Sections & Adaptable Grids (`event-gallery.html`)

If a section contains multiple images, `event-gallery.html` automatically places them **side-by-side** in a responsive top-aligned grid:
- **Top-aligned**: Cards align to the top (`align-items: start`), preserving each photo's original aspect ratio (square, landscape, or vertical).
- **Guaranteed spacing**: Uses native CSS grid with generous gaps (`gap: 1.5rem`), eliminating stuck-together cards.
- **2 images**: 2 columns side-by-side (stacks cleanly on mobile).
- **3 images**: 3 columns side-by-side (stacks on mobile).
- **4 images**: 4 columns side-by-side on desktop (collapses to 2 columns on tablet).
- **More than 4 images (or full galleries)**: Automatically uses an **adaptable auto-fill grid** (`cols="auto"`), fitting 3–4 photos per row on desktop, 2 on tablet, and 1 on mobile.
- **Custom column count (`cols` parameter)**: Pass `cols="2"`, `cols="3"`, `cols="4"`, or `cols="auto"` to explicitly choose columns:
  ```liquid
  {% raw %}{% include event-gallery.html cols="4" %}{% endraw %}
  ```
- **Group sizing presets**: Use `size="small"` to keep multi-image comparisons compact and centered:
  ```liquid
  {% raw %}{% include event-gallery.html section="3" size="small" %}{% endraw %}
  ```

### Option 3: Placing Images Using Serial Section IDs (`section="1"`, `section="2"`, ...)

By default, when you generate or refresh an event gallery, **each newly detected image is automatically given its own section with sequential numeric IDs (`id: 1`, `id: 2`, `id: 3`, ...)**:

```yaml
title: Campus Bird Walk
intro: Highlights from our morning nature walk across IISc campus.

sections:
  - id: 1
    images:
      - path: /images/event_images/2026-09-12-campus-bird-walk/12-sept-26-birdwalk.webp
        alt: Group photo of Bird Walk participants
        caption: Participants gather at the end of the bird walk.
  - id: 2
    images:
      - path: /images/event_images/2026-09-12-campus-bird-walk/barbet-nest.webp
        alt: Barbet nest
        caption: Barbet nests (the small cavities) on the tree trunk.
  - id: 3
    images:
      - path: /images/event_images/2026-09-12-campus-bird-walk/black-kite.webp
        alt: Black Kite
        caption: Black Kite overlooking the grounds.
      - path: /images/event_images/2026-09-12-campus-bird-walk/brahminy-kite.webp
        alt: Brahminy Kite
        caption: A Brahminy Kite sitting atop a tree in the distance.
```

To reuse the same snippet anywhere in your narrative, just change the serial number:

```liquid
{% raw %}{% include event-gallery.html section="2" %}{% endraw %}
```

### Customizing Named Groups (Optional)

You can later group photos under a named section with a `title`:

```yaml
sections:
  - title: Canopy Sightings
    id: canopy
    images:
      - path: /images/event_images/2026-09-12-campus-bird-walk/brahminy-kite.webp
        alt: Brahminy Kite soaring above the trees
        caption: A Brahminy Kite scanned the canopy near Jubilee Gardens.
      - path: /images/event_images/2026-09-12-campus-bird-walk/black-kite.webp
        alt: Black Kite perched on a dry branch
        caption: Black Kite overlooking the campus grounds.
```

- **Section matching:** Matches either `section.title` (e.g., `"Canopy Sightings"`) or `section.id` (e.g., `"canopy"`, `"1"`).
- **Hide heading:** Pass `hide_title=true` to omit the `<h3>` header:
  ```liquid
  {% raw %}{% include event-gallery.html section="canopy" hide_title=true %}{% endraw %}
  ```
- Running `python3 tools/create_event_post.py refresh --slug <slug>` preserves existing sections and captions while assigning the next sequential integer ID to any new images.

### Option 4: Full Gallery at the End (with Section Exclusion)

The generated post template ends with:

```liquid
{% raw %}{% include event-gallery.html %}{% endraw %}
```

This renders all remaining or unsectioned event images in a responsive adaptable grid.

To avoid repeating photos that were already featured earlier in the post (e.g. as a lead photo or narrative figure), use the `except` or `except_section` argument:

```liquid
{% raw %}{% include event-gallery.html except="0" %}{% endraw %}
{% raw %}{% include event-gallery.html except="0, 1" %}{% endraw %}
{% raw %}{% include event-gallery.html except_section="Canopy Sightings" %}{% endraw %}
```

## Keep images under the hook limit

The pre-commit hook rejects images larger than 300 KiB (307200 bytes). First review what would change:

```sh
python3 tools/convert_images.py images/event_images/2026-09-12-campus-bird-walk \
  --recursive --max-bytes 307200 \
  --output-dir /tmp/campus-bird-walk-optimized --dry-run
```

Write optimized files to an output directory while preserving source extensions:

```sh
python3 tools/convert_images.py images/event_images/2026-09-12-campus-bird-walk \
  --recursive --max-bytes 307200 \
  --output-dir /tmp/campus-bird-walk-optimized
```

To replace the source files explicitly, use `--in-place` instead of `--output-dir`:

```sh
python3 tools/convert_images.py images/event_images/2026-09-12-campus-bird-walk \
  --recursive --max-bytes 307200 --in-place
```

The optimizer reduces encoding quality and then dimensions while preserving aspect ratio. It never enlarges an image. Add the optimized files to Git and run the refresh command again if filenames changed.

## Commit checks

Event posts created by the generator use the same slug for the post, image
folder, and gallery data file. The custom pre-commit hook rejects a staged
event post when those names differ or when its image folder or gallery data is
missing. Existing posts without an `event_gallery` field are not affected
until they are migrated to this workflow.
