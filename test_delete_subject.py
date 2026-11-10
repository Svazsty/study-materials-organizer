
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from subjects import delete_subject, load_subjects


class TestDeleteSubject(unittest.TestCase):

    def test_delete_unassigned_subject(self):
        with TemporaryDirectory() as temporary:
            subjects_file = Path(temporary) / "subjects.json"
            semesters_file = Path(temporary) / "semesters.json"

            subjects_file.write_text(
                json.dumps({
                    "algebra": "Algebra liniowa",
                    "testowy": "Przedmiot testowy"
                }),
                encoding="utf-8"
            )

            semesters_file.write_text(
                json.dumps({
                    "active_semester": "S1",
                    "semesters": {
                        "S1": {"subjects": ["algebra"]}
                    }
                }),
                encoding="utf-8"
            )

            with patch("subjects.SUBJECTS_FILE", subjects_file):
                with patch("semesters.SEMESTERS_FILE", semesters_file):
                    result = delete_subject("testowy")
                    subjects = load_subjects()

            self.assertTrue(result)
            self.assertNotIn("testowy", subjects)
            self.assertIn("algebra", subjects)

    def test_cannot_delete_assigned_subject(self):
        with TemporaryDirectory() as temporary:
            subjects_file = Path(temporary) / "subjects.json"
            semesters_file = Path(temporary) / "semesters.json"

            subjects_file.write_text(
                json.dumps({"algebra": "Algebra liniowa"}),
                encoding="utf-8"
            )

            semesters_file.write_text(
                json.dumps({
                    "active_semester": "S1",
                    "semesters": {
                        "S1": {"subjects": ["algebra"]}
                    }
                }),
                encoding="utf-8"
            )

            with patch("subjects.SUBJECTS_FILE", subjects_file):
                with patch("semesters.SEMESTERS_FILE", semesters_file):
                    with self.assertRaises(ValueError):
                        delete_subject("algebra")

                    subjects = load_subjects()

            self.assertIn("algebra", subjects)
