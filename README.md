<!-- AI-generated: Repository README with event publishing and gallery section workflow guide -->
# Nature Club IISc Website

Static website for the **Nature Club at the Indian Institute of Science (IISc), Bengaluru**. Built with [Jekyll](https://jekyllrb.com/) and hosted via GitHub Pages.

- **Production Site:** [https://www.iiscnatureclub.com](https://www.iiscnatureclub.com)
- **Staging / GitHub Pages:** [https://gkgabel.github.io/natureclubiisc.github.io/](https://gkgabel.github.io/natureclubiisc.github.io/)

---

## Local Development

### Prerequisites
- Ruby (>= 3.0) and Bundler
- Python (>= 3.10) with Pillow and PyYAML (`pip install -r tools/requirements-image.txt`)

### Setup and Run
```sh
# Install Ruby dependencies
bundle install

# Run the local Jekyll server
bundle exec jekyll serve

# Run test suite
python3 -m unittest tools/test_event_tools.py -v
```

---

## Event Posts and Gallery Workflow

Each event post uses a matching slug across three locations:
1. Post Markdown: `_posts/<YYYY-MM-DD-slug>.md`
2. Image Folder: `images/event_images/<YYYY-MM-DD-slug>/`
3. Gallery Metadata: `_data/event_galleries/<YYYY-MM-DD-slug>.yml`

### 1. Create a New Event
Use the CLI generator to scaffold the post, image directory, and gallery file:
```sh
python3 tools/create_event_post.py create \
  --title "Campus Bird Walk" \
  --date 2026-09-12 \
  --tags nature-walk bird-walk \
  --author "Gulshan Gabel"
```

### 2. Add and Optimize Images
Copy your images into `images/event_images/<slug>/`. All staged images must be **under 300 KiB (307,200 bytes)**, enforced by the pre-commit hook.

Optimize them in-place with optional dimension/quality presets (`small`, `standard`, or `hero`):
```sh
python3 tools/convert_images.py images/event_images/2026-09-12-campus-bird-walk \
  --recursive --max-bytes 307200 --preset standard --in-place
```

Optionally number images sequentially during conversion:
```sh
python3 tools/convert_images.py images/event_images/<slug> \
  --recursive --rename --name-prefix insect-
```

To rename a directory without converting the images, use `--rename-only`.
This preserves each file extension. Review the changes first with `--dry-run`:
```sh
python3 tools/convert_images.py images/event_images/<slug> \
  --recursive --rename-only --dry-run
```
See the [Image Optimization Guide](tools/convert_images.md) for all naming
options, including `--start-number`.

Refresh the gallery metadata to detect new files:
```sh
python3 tools/create_event_post.py refresh --slug 2026-09-12-campus-bird-walk
```

---

## Organizing Gallery Images into Sections

By default, when you generate or refresh an event gallery, **each image is automatically placed into its own section with sequential numeric IDs (`id: 1`, `id: 2`, `id: 3`, ...)**.

This makes referencing images in your post effortless: you use the exact same Liquid snippet and simply change the serial number!

```liquid
{% raw %}{% include event-gallery.html section="1" %}{% endraw %}
...
{% raw %}{% include event-gallery.html section="2" size="medium" %}{% endraw %}
...
{% raw %}{% include event-figure.html section="3" align="right" size="small" %}{% endraw %}
```

### Default Generated YAML (`_data/event_galleries/<slug>.yml`)

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
      - path: /images/event_images/2026-09-12-campus-bird-walk/spotted-owlet-pair.webp
        alt: Spotted Owlet pair
        caption: A pair of Spotted Owlets near Main Guest House.
```

### Customizing Sections Later (Optional)
You can leave the default serial numbers as-is, or group multiple photos under a named section with a `title`:

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
        caption: Black Kite overlooking the grounds.

  - id: 3
    images:
      - path: /images/event_images/2026-09-12-campus-bird-walk/spotted-owlet-pair.webp
        alt: Spotted Owlet pair
        caption: A pair of Spotted Owlets near Main Guest House.
```

Running `python3 tools/create_event_post.py refresh --slug <slug>` preserves all existing sections, IDs, and captions, and appends any newly detected photos as the next sequential section ID!

---

## Embedding Images in Markdown Posts

Images are rendered as tactile polaroid cards with subtle shadows, theme-matching borders, and authentic handwritten-style captions (`Caveat` font). Each photo retains its 100% original aspect ratio without distortion or cropping.

### 1. Single Image Embeds & Sizing Presets
To insert a single image using its serial section number:
```liquid
{% raw %}{% include event-gallery.html section="2" size="medium" %}{% endraw %}
```
Or using `event-figure.html`:
```liquid
{% raw %}{% include event-figure.html section="1" size="large" %}{% endraw %}
```

#### Supported Display Sizing Presets (`size="..."`):
- `size="small"` (~22rem max-width, ~350px): Compact, centered polaroid card; great for portrait photos, small details, and specimen highlights.
- `size="medium"` (~34rem max-width, ~540px): Standard narrative reading width fitting body text comfortably.
- `size="large"` (~48rem max-width, ~760px): High-impact showcase photos and scenic landscapes.
- `size="full"` (100% width): Full-bleed column width for group photos.
- `size="original"`: Displays at intrinsic pixel dimensions without upscaling.
- **Smart Height Cap**: Images automatically cap at `75vh` max-height with `object-fit: contain` so tall vertical photos never overflow screen height.

### 2. Multi-Image Side-by-Side Sections & Adaptable Grids
If a section contains multiple images, `event-gallery.html` automatically places them **side-by-side** in a responsive, adaptable polaroid grid:
- **Top-aligned**: All polaroids in a row start at the exact same top horizontal line (`align-items: start`), allowing each photo to naturally retain its own original aspect ratio (square, landscape, or portrait).
- **Guaranteed spacing**: Uses native CSS grid with generous gaps (`gap: 1.5rem`), so cards never touch edge-to-edge.
- **2 images in section**: 2 columns side-by-side (stacks cleanly on mobile).
- **3 images in section**: 3 columns side-by-side (stacks on mobile).
- **4 images in section**: 4 columns side-by-side on desktop (collapses to 2 columns on tablet).
- **More than 4 images (or full galleries)**: Automatically uses an **adaptable auto-fill grid** (`cols="auto"`), fitting 3–4 photos per row on desktop, 2 on tablet, and 1 on mobile.
- **Custom column count (`cols` parameter)**: You can explicitly set `cols="2"`, `cols="3"`, `cols="4"`, or `cols="auto"`:
```liquid
{% raw %}{% include event-gallery.html cols="4" %}{% endraw %}
```
- **Group sizing presets**: Pass `size="small"` (e.g. `max-width: 44rem` for 2-col, `52rem` for 3-col, `60rem` for 4-col/auto) to keep multi-image comparisons compact and centered within the text:
```liquid
{% raw %}{% include event-gallery.html section="3" size="small" %}{% endraw %}
```

### 3. Named Sectional Mini-Grids (`section="Canopy Sightings"`)
To render a group of photos under a heading:
```liquid
{% raw %}{% include event-gallery.html section="Canopy Sightings" %}{% endraw %}
```
*(Pass `hide_title=true` if you already wrote a markdown heading above it).*

### 4. Full End-of-Post Gallery (`event-gallery.html`)
To render all photos at the bottom of your post in a responsive 3-column grid:
```liquid
{% raw %}{% include event-gallery.html %}{% endraw %}
```
- Automatically combines untitled serial sections into a clean unified grid.
- If sections have titles, each displays under its respective heading.
- To display only remaining unsectioned images (without repeating sections used above), use `{% raw %}{% include event-gallery.html unsectioned=true %}{% endraw %}`.

### 5. Excluding Specific Sections (`except="..."` or `except_section="..."`)
When you feature one or more photos earlier in the post (e.g. as a lead photo or narrative figure), you can easily exclude them from the full gallery so they don't repeat:
- **Single section exclusion**:
  ```liquid
  {% raw %}{% include event-gallery.html except="0" %}{% endraw %}
  ```
- **Multiple section exclusion** (comma or space separated section IDs or titles):
  ```liquid
  {% raw %}{% include event-gallery.html except="0, 1" %}{% endraw %}
  {% raw %}{% include event-gallery.html except="0, Canopy Sightings" %}{% endraw %}
  ```
- `except_section` or `except_sections` are also supported as aliases:
  ```liquid
  {% raw %}{% include event-gallery.html except_section="0" %}{% endraw %}
  ```

---

## Documentation Links
- [Event Post Generator Guide](tools/create_event_post.md)
- [Image Optimization Guide](tools/convert_images.md)