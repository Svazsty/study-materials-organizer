import unittest
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import redirect_stdout
from io import StringIO

from organizer_materials import parse_date, organize_files


class TestParseDate(unittest.TestCase):
    def test_valid_date(self):
        result = parse_date("25.10.2026")
        self.assertEqual(result, datetime(2026, 10, 25))

    def test_invalid_date(self):
        result = parse_date("31.02.2026")
        self.assertIsNone(result)

class TestOrganizeFiles(unittest.TestCase):
    def test_preview_keeps_source_unchanged(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            target = root / "target"
            source.mkdir()

            source_file = source / "28.10.2026_W01_algebra.md"
            source_file.write_text("test", encoding="utf-8")

            output = StringIO()

            with redirect_stdout(output):
                organize_files(
                    source, target, False, {"algebra": "Algebra liniowa"}
                )

            expected_folder = (
                target / "Wyklady" / "Algebra liniowa" / "28.10.2026_W01"
            )
            expected_file = expected_folder / source_file.name

            self.assertIn(str(expected_file), output.getvalue())
            self.assertEqual(source_file.read_text(encoding="utf-8"), "test")
            self.assertFalse(target.exists())

    def test_apply_moves_file(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            target = root / "target"
            source.mkdir()

            source_file = source / "28.10.2026_W01_algebra.md"
            source_file.write_text("test", encoding="utf-8")

            output = StringIO()

            with redirect_stdout(output):
                organize_files(
                    source, target, True, {"algebra": "Algebra liniowa"}
                )

            expected_folder = (
                    target / "Wyklady" / "Algebra liniowa" / "28.10.2026_W01"
            )
            expected_file = expected_folder / source_file.name

            self.assertFalse(source_file.exists())
            self.assertEqual(expected_file.read_text(encoding="utf-8"), "test")

    def test_existing_target_is_not_overwritten(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            target = root / "target"
            source.mkdir()

            file_name = "28.10.2026_W01_algebra.md"
            source_file = source / file_name
            source_file.write_text("nowe dane", encoding="utf-8")

            target_folder = (
                target / "Wyklady" / "Algebra liniowa" / "28.10.2026_W01"
            )
            target_folder.mkdir(parents=True)

            target_file = target_folder / file_name
            target_file.write_text("stare dane", encoding="utf-8")

            output = StringIO()

            with redirect_stdout(output):
                organize_files(
                    source, target, True, {"algebra": "Algebra liniowa"}
                )

            self.assertEqual(target_file.read_text(encoding="utf-8"), "stare dane")
            self.assertEqual(source_file.read_text(encoding="utf-8"), "nowe dane")
if __name__ == "__main__":
    unittest.main()