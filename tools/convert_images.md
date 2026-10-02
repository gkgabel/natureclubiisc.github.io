# Image conversion

Install the image dependency once:

```sh
python3 -m pip install -r tools/requirements-image.txt
```

Convert one image beside the original (or use `--delete-original` to remove the source file):

```sh
python3 tools/convert_images.py images/cover_image.jpg
```

Convert all supported images in a directory and its subdirectories:

```sh
python3 tools/convert_images.py images/ --recursive
```

Number converted images sequentially, optionally adding a prefix:

```sh
python3 tools/convert_images.py images/ --recursive --rename --name-prefix insect-
```

Rename images without converting them. Extensions are preserved; use
`--dry-run` to review the changes first:

```sh
python3 tools/convert_images.py images/ --recursive --rename-only --dry-run
python3 tools/convert_images.py images/ --recursive --rename-only --start-number 1
```

Files are ordered by path, and the default names are `1.webp`, `2.webp`, etc.
for conversion and `1.jpg`, `2.png`, etc. for rename-only mode. Use
`--start-number` and `--name-prefix` to customize the sequence.

The default output is WebP at quality 82, resized only when an image exceeds
2400 pixels in either dimension. Originals are kept by default unless
`--delete-original` is passed. Use `--dry-run` to review the files first, or
choose different settings:

```sh
python3 tools/convert_images.py images/ --recursive \
  --max-width 1800 --max-height 1800 --quality 80 \
  --output-dir images-webp
```

Supported input formats are JPEG, PNG, WebP, and TIFF. Existing WebP files are
skipped when they would overwrite themselves.

<!-- AI-generated: preset documentation for convert_images.py -->
You can also use predefined dimension and quality presets:
- `--preset standard` (or `medium`): 1600×1200, quality 82 (great general web balance)
- `--preset small`: 1000×1000, quality 80 (compact files for details or portraits)
- `--preset hero` (or `large`): 2400×2400, quality 85 (high-resolution banners)

Example using presets with size capping:
```sh
python3 tools/convert_images.py images/event_images/2026-09-12-campus-bird-walk \
  --recursive --preset standard --max-bytes 307200 --in-place
```


The repository pre-commit hook rejects staged supported images larger than 300
KB. The converter can target that exact limit when normal conversion is not
enough:

```sh
python3 tools/convert_images.py images/event_images/2026-09-12-campus-bird-walk \
  --recursive --max-bytes 307200 --output-dir /tmp/bird-walk-optimized
```

The target-size mode lowers encoding quality and then dimensions, preserving
aspect ratio and never enlarging an image. It requires either `--output-dir`
or explicit `--in-place`; originals are protected by default. Use
`--dry-run` first when replacing files in place.