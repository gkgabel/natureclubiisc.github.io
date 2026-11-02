# AI-generated: automated test suite for event post creation, metadata refresh, and image conversion
import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import yaml
from PIL import Image

from tools.convert_images import convert_image, optimize_image, output_path
from tools.create_event_post import create_event, event_slug, post_content, refresh_event, slugify
from tools.event_publish import PublishError, load_workflow_config, publish_event, safe_destination


class EventToolTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        template_dir = self.root / "tools" / "templates"
        template_dir.mkdir(parents=True)
        shutil.copy(
            Path(__file__).parent / "templates" / "event_post.md.template",
            template_dir / "event_post.md.template",
        )

    def tearDown(self):
        shutil.rmtree(self.root)

    def test_slug_generation(self):
        self.assertEqual(slugify("Campus Bird Walk"), "campus-bird-walk")
        self.assertEqual(event_slug(date(2026, 9, 12), "Campus Bird Walk"), "2026-09-12-campus-bird-walk")

    def test_create_refresh_and_preserve_caption(self):
        args = SimpleNamespace(
            root=self.root,
            title="Campus Bird Walk",
            date="2026-09-12",
            tags=["nature-walk"],
            author="Gulshan Gabel",
        )
        create_event(args)
        slug = "2026-09-12-campus-bird-walk"
        image_dir = self.root / "images" / "event_images" / slug
        Image.new("RGB", (400, 300), "green").save(image_dir / "bird.webp")
        refresh_event(SimpleNamespace(root=self.root, slug=slug))

        metadata_path = self.root / "_data" / "event_galleries" / f"{slug}.yml"
        metadata = yaml.safe_load(metadata_path.read_text())
        self.assertIn("sections", metadata)
        self.assertEqual(metadata["sections"][0]["id"], 1)
        metadata["sections"][0]["images"][0]["caption"] = "A campus bird."
        metadata_path.write_text(yaml.safe_dump(metadata, sort_keys=False))
        Image.new("RGB", (400, 300), "blue").save(image_dir / "kite.webp")
        refresh_event(SimpleNamespace(root=self.root, slug=slug))

        refreshed = yaml.safe_load(metadata_path.read_text())
        self.assertEqual(len(refreshed["sections"]), 2)
        self.assertEqual(refreshed["sections"][0]["id"], 1)
        self.assertEqual(refreshed["sections"][0]["images"][0]["caption"], "A campus bird.")
        self.assertEqual(refreshed["sections"][1]["id"], 2)
        self.assertEqual(refreshed["sections"][1]["images"][0]["path"], f"/images/event_images/{slug}/kite.webp")

    def test_optimizer_reaches_target(self):
        source = self.root / "large.jpg"
        destination = self.root / "optimized.webp"
        Image.new("RGB", (2400, 1600), "forestgreen").save(source, quality=100)
        self.assertTrue(optimize_image(source, destination, 2400, 2400, 82, 10000, False))
        self.assertLessEqual(destination.stat().st_size, 10000)
        with Image.open(destination) as optimized:
            self.assertEqual(optimized.size, (2400, 1600))
        self.assertGreater(source.stat().st_size, destination.stat().st_size)

    def test_optimizer_keeps_compliant_image_byte_for_byte(self):
        source = self.root / "compliant.webp"
        destination = self.root / "out" / "compliant.webp"
        Image.new("RGB", (400, 300), "green").save(source, quality=82)
        original = source.read_bytes()

        self.assertTrue(optimize_image(source, destination, 2400, 2400, 20, len(original), False))
        self.assertEqual(destination.read_bytes(), original)
        self.assertEqual(source.read_bytes(), original)

    def test_optimizer_preserves_wide_image_aspect_ratio(self):
        source = self.root / "wide.png"
        destination = self.root / "wide.webp"
        Image.effect_noise((1800, 500), 10).save(source)

        self.assertTrue(optimize_image(source, destination, 2400, 2400, 82, 30000, False))
        with Image.open(destination) as optimized:
            width, height = optimized.size
        self.assertAlmostEqual(width / height, 1800 / 500, delta=0.05)
        self.assertGreater(height, 320)

    def test_optimizer_writes_jpeg_for_jpeg_destination(self):
        source = self.root / "source.jpeg"
        destination = self.root / "optimized.jpeg"
        Image.new("RGB", (1200, 800), "green").save(source, quality=100)

        self.assertTrue(optimize_image(source, destination, 2400, 2400, 82, 5000, False))
        with Image.open(destination) as optimized:
            self.assertEqual(optimized.format, "JPEG")

    def test_recursive_output_preserves_directories(self):
        root = self.root / "images"
        nested = root / "birds"
        nested.mkdir(parents=True)
        source = nested / "shared-name.jpg"

        destination = output_path(source, self.root / "optimized", [root])

        self.assertEqual(destination, self.root / "optimized" / "birds" / "shared-name.webp")

    def test_collision_reporting(self):
        args = SimpleNamespace(
            root=self.root,
            title="Campus Bird Walk",
            date="2026-09-12",
            tags=[],
            author=None,
        )
        create_event(args)
        with self.assertRaises(SystemExit) as context:
            create_event(args)
        self.assertIn("Event already exists; refusing to overwrite", str(context.exception))

    def test_invalid_inputs(self):
        args_empty_title = SimpleNamespace(
            root=self.root,
            title="???",
            date="2026-09-12",
            tags=[],
            author=None,
        )
        with self.assertRaises(ValueError) as context:
            create_event(args_empty_title)
        self.assertIn("produces an empty slug", str(context.exception))

        args_bad_date = SimpleNamespace(
            root=self.root,
            title="Valid Title",
            date="not-a-date",
            tags=[],
            author=None,
        )
        with self.assertRaises(ValueError):
            create_event(args_bad_date)

    def test_template_output(self):
        content = post_content(
            self.root,
            title="Walk: Morning Highlights",
            event_date=date(2026, 9, 12),
            tags=["nature", "birds"],
            author="Gulshan Gabel",
            slug="2026-09-12-walk-morning-highlights",
        )
        self.assertIn('title: "Walk: Morning Highlights"', content)
        self.assertIn("tags: nature birds", content)
        self.assertIn("author: Gulshan Gabel", content)
        self.assertIn("12 September, 2026", content)

        # Content without optional tags or author should not have blank lines in front matter
        minimal_content = post_content(
            self.root,
            title="Simple Walk",
            event_date=date(2026, 9, 12),
            tags=[],
            author=None,
            slug="2026-09-12-simple-walk",
        )
        parts = minimal_content.split("---", 2)
        front_matter = parts[1].strip()
        for line in front_matter.splitlines():
            self.assertTrue(bool(line.strip()), "Front matter should not contain blank lines")

    def test_sections_preserved_in_refresh(self):
        slug = "2026-09-12-section-walk"
        image_dir = self.root / "images" / "event_images" / slug
        image_dir.mkdir(parents=True)
        Image.new("RGB", (100, 100), "red").save(image_dir / "img1.webp")
        Image.new("RGB", (100, 100), "blue").save(image_dir / "img2.webp")

        metadata_path = self.root / "_data" / "event_galleries" / f"{slug}.yml"
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        initial_data = {
            "title": "Section Walk",
            "sections": [
                {
                    "title": "Part 1",
                    "images": [
                        {
                            "path": f"/images/event_images/{slug}/img1.webp",
                            "alt": "Image One",
                            "caption": "First caption",
                        }
                    ],
                }
            ],
        }
        metadata_path.write_text(yaml.safe_dump(initial_data, sort_keys=False))

        refresh_event(SimpleNamespace(root=self.root, slug=slug))

        refreshed = yaml.safe_load(metadata_path.read_text())
        self.assertIn("sections", refreshed)
        self.assertEqual(refreshed["sections"][0]["images"][0]["caption"], "First caption")
        # img2 should be picked up as a new section with sequential id
        self.assertEqual(len(refreshed["sections"]), 2)
        self.assertEqual(refreshed["sections"][1]["id"], 1)
        self.assertEqual(refreshed["sections"][1]["images"][0]["path"], f"/images/event_images/{slug}/img2.webp")

    def test_convert_image_delete_original_opt_in(self):
        source = self.root / "photo.png"
        destination = self.root / "photo.webp"
        Image.new("RGB", (100, 100), "green").save(source)

        # Default: keep original
        self.assertTrue(convert_image(source, destination, 2400, 2400, 82, False, delete_original=False))
        self.assertTrue(source.is_file())
        self.assertTrue(destination.is_file())

        # delete_original=True: removes source
        destination.unlink()
        self.assertTrue(convert_image(source, destination, 2400, 2400, 82, False, delete_original=True))
        self.assertFalse(source.is_file())
        self.assertTrue(destination.is_file())

    def test_convert_image_preset(self):
        from tools.convert_images import PRESETS
        self.assertIn("small", PRESETS)
        self.assertEqual(PRESETS["small"]["max_width"], 1000)
        self.assertEqual(PRESETS["standard"]["max_width"], 1600)
        self.assertEqual(PRESETS["hero"]["max_width"], 2400)

    def test_publish_event_generates_ordered_metadata_and_safe_names(self):
        first = self.root / "Bird Photo.JPG"
        second = self.root / "Bird Photo 2.JPG"
        Image.new("RGB", (400, 300), "green").save(first)
        Image.new("RGB", (400, 300), "blue").save(second)

        result = publish_event(
            self.root,
            "Campus Bird Walk",
            "2026-09-12",
            ["birds"],
            "Author",
            [
                {"source": str(second), "name": "Spotted Owlet.JPG", "alt": "Owlet", "caption": "Second"},
                {"source": str(first), "name": "Spotted Owlet.JPG", "alt": "Bird", "caption": "First"},
            ],
        )

        self.assertEqual([item["filename"] for item in result["files"]], ["spotted-owlet.webp", "spotted-owlet-2.webp"])
        gallery = yaml.safe_load((self.root / result["gallery"]).read_text())
        self.assertEqual(gallery["sections"][0]["images"][0]["alt"], "Owlet")
        self.assertEqual(gallery["sections"][1]["images"][0]["caption"], "First")
        self.assertEqual(result["empty_alt"], [])

    def test_publish_event_rejects_duplicate_content_without_writing(self):
        first = self.root / "first.jpg"
        duplicate = self.root / "duplicate.jpg"
        Image.new("RGB", (400, 300), "green").save(first)
        shutil.copy2(first, duplicate)

        with self.assertRaisesRegex(PublishError, "Duplicate image content"):
            publish_event(
                self.root,
                "Duplicate Walk",
                "2026-09-12",
                [],
                None,
                [{"source": str(first)}, {"source": str(duplicate)}],
            )
        self.assertFalse((self.root / "_posts" / "2026-09-12-duplicate-walk.md").exists())

    def test_publish_event_aborts_without_partial_outputs(self):
        valid = self.root / "valid.jpg"
        Image.new("RGB", (400, 300), "green").save(valid)

        with self.assertRaisesRegex(PublishError, "Unsupported or missing image"):
            publish_event(
                self.root,
                "Atomic Walk",
                "2026-09-12",
                [],
                None,
                [{"source": str(valid)}, {"source": str(self.root / "missing.gif")}],
            )
        self.assertFalse((self.root / "_posts" / "2026-09-12-atomic-walk.md").exists())
        self.assertFalse((self.root / "_data" / "event_galleries" / "2026-09-12-atomic-walk.yml").exists())
        self.assertFalse((self.root / "images" / "event_images" / "2026-09-12-atomic-walk").exists())

    def test_safe_destination_rejects_traversal(self):
        with self.assertRaises(PublishError):
            safe_destination(self.root, "../outside.txt")
        with self.assertRaises(PublishError):
            safe_destination(self.root, "/tmp/outside.txt")

    def test_workflow_preset_controls_unspecified_dimensions(self):
        config_path = self.root / "tools" / "image_workflow.conf"
        config_path.write_text("preset=small\nmax_bytes=12345\n")

        config = load_workflow_config(self.root)

        self.assertEqual(config["max_width"], 1000)
        self.assertEqual(config["max_height"], 1000)
        self.assertEqual(config["quality"], 80)
        self.assertEqual(config["max_bytes"], 12345)


if __name__ == "__main__":
    unittest.main()
