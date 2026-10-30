import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from subjects import load_subjects, add_subject

class TestSubjects(unittest.TestCase):
    def test_add_new_subject(self):
        with TemporaryDirectory() as temporary:
            subjects_file = Path(temporary) / "subjects.json"
            subjects_file.write_text(
                json.dumps({"algebra": "Algebra liniowa"}),
                encoding="utf-8"
            )
            with patch("subjects.SUBJECTS_FILE", subjects_file):
                result = add_subject("fizyka", "Fizyka")
                subjects = load_subjects()

            self.assertTrue(result)
            self.assertEqual(subjects["fizyka"], "Fizyka")
    def test_existing_subject_is_not_overwritten(self):
        with TemporaryDirectory() as temporary:
            subjects_file = Path(temporary) / "subjects.json"
            subjects_file.write_text(
                json.dumps({"algebra": "Algebra liniowa"}),
                encoding="utf-8"
            )
            with patch("subjects.SUBJECTS_FILE", subjects_file):
                result = add_subject("algebra", "Nowa Algebra")
                subjects = load_subjects()

            self.assertFalse(result)
            self.assertEqual(subjects["algebra"], "Algebra liniowa")

    def test_invalid_subject_name(self):
        with TemporaryDirectory() as temporary:
            subjects_file = Path(temporary) / "subjects.json"
            subjects_file.write_text(
                json.dumps({"algebra": "Algebra liniowa"}),
                encoding="utf-8"
            )
            with patch("subjects.SUBJECTS_FILE", subjects_file):
                with self.assertRaises(ValueError):
                    add_subject("matematyka", "Matematyka: ćwiczenia")  # Invalid character ':'

                subjects = load_subjects()
            self.assertNotIn("matematyka", subjects)