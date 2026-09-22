# Image conversion

Install the image dependency once:

```sh
python3 -m pip install -r tools/requirements-image.txt
```

Convert one image beside the original:

```sh
python3 tools/convert_images.py images/owlet.jpg
```

Convert all supported images in a directory and its subdirectories:

```sh
python3 tools/convert_images.py images/ --recursive
```

The default output is WebP at quality 82, resized only when an image exceeds
2400 pixels in either dimension. Originals are kept. Use `--dry-run` to review
the files first, or choose different settings:

```sh
python3 tools/convert_images.py images/ --recursive \
  --max-width 1800 --max-height 1800 --quality 80 \
  --output-dir images-webp
```

Supported input formats are JPEG, PNG, WebP, and TIFF. Existing WebP files are
skipped when they would overwrite themselves.

The repository pre-commit hook rejects staged supported images larger than 300
KB. The converter does not guarantee that every image will be below that limit,
so use the hook as the final check and lower `--quality` or the size limits when
it reports an oversized output.