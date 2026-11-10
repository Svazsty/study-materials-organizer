import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from semesters import (
        load_semesters,
        save_semesters,
        add_semester,
        set_semester_subjects,
        delete_semester
)

class TestSemesters(unittest.TestCase):
    def test_save_and_load_semesters(self):
        with TemporaryDirectory() as temporary:
            semesters_file = Path(temporary) / "semesters.json"
            data = {
                "active_semester": "2026-2027-S1",
                "semesters": {
                    "2026-2027-S1":{
                        "name": "2026/2027 - Semestr 1",
                        "target": "Test_target",
                        "subjects": ["algebra", "ekonomia"]
                    }
                }
            }

            with patch("semesters.SEMESTERS_FILE", semesters_file):
                save_semesters(data)
                loaded_data = load_semesters()

            self.assertEqual(loaded_data, data)

    def test_unknown_subject(self):
        with TemporaryDirectory() as temporary:
            semesters_file = Path(temporary) / "semesters.json"

            with patch("semesters.SEMESTERS_FILE", semesters_file):
                with patch("semesters.load_subjects") as mock_subjects:
                    mock_subjects.return_value = {
                        "algebra": "Algebra liniowa",
                        "ekonomia": "Ekonomia"
                    }

                    result = add_semester(
                        "2026-2027-S2",
                        "2026/2027 - Semestr 2",
                        "Test_target",
                        ["algebra"]
                    )

                    with self.assertRaises(ValueError):
                        set_semester_subjects(
                            "2026-2027-S2",
                            ["algebra", "unknown_subject"]
                        )

                    data = load_semesters()
                    self.assertTrue(result)

                self.assertEqual(
                    data["semesters"]["2026-2027-S2"]["subjects"],
                    ["algebra"]
                )



    def test_add_semester(self):
        with TemporaryDirectory() as temporary:
            semesters_file = Path(temporary) / "semesters.json"

            with patch("semesters.SEMESTERS_FILE", semesters_file):
                result = add_semester(
                    "2026-2027-S1",
                    "2026/2027 - Semestr 1",
                    "Test_target",
                    ["algebra", "ekonomia"]
                )

                data = load_semesters()

            self.assertTrue(result)
            self.assertEqual(data["active_semester"], "2026-2027-S1")
            self.assertEqual(
                data["semesters"]["2026-2027-S1"]["target"],
                "Test_target"
            )

    def test_duplicate_semester(self):
        with TemporaryDirectory() as temporary:
            semesters_file = Path(temporary) / "semesters.json"

            with patch("semesters.SEMESTERS_FILE", semesters_file):
                first = add_semester(
                    "2026-2027-S1",
                    "Semestr 1",
                    "Folder_A",
                    ["algebra"]
                )

                second = add_semester(
                    "2026-2027-S1",
                    "Semestr 1 - zmieniony",
                    "Folder_B",
                    ["ekonomia"]
                )

                data = load_semesters()

            self.assertTrue(first)
            self.assertFalse(second)
            self.assertEqual(len(data["semesters"]), 1)
            self.assertEqual(
                data["semesters"]["2026-2027-S1"]["target"],
                "Folder_A"
            )

    def test_set_semester_subjects(self):
        with TemporaryDirectory() as temporary:
            semesters_file = Path(temporary) / "semesters.json"

            with patch("semesters.SEMESTERS_FILE", semesters_file):
                with patch("semesters.load_subjects") as mock_subjects:
                    mock_subjects.return_value = {
                        "algebra": "Algebra liniowa",
                        "ekonomia": "Ekonomia"
                    }

                    add_semester(
                        "2026-2027-S2",
                        "Semestr 2",
                        "Test_target",
                        []
                    )

                set_semester_subjects(
                    "2026-2027-S2",
                    ["algebra", "ekonomia", "algebra"]  # Duplicate "algebra" to test deduplication
                )

                data = load_semesters()

            self.assertEqual(
                data["semesters"]["2026-2027-S2"]["subjects"],
                ["algebra", "ekonomia"]
            )

    def test_delete_semester(self):
        with TemporaryDirectory() as temporary:
            semesesters_file = Path(temporary) / "semesters.json"
            target_folder = Path(temporary) / "materials"
            target_folder.mkdir()

            test_file = target_folder / "notes.txt"
            test_file.write_text("Important notes", encoding="utf-8")

            with patch("semesters.SEMESTERS_FILE", semesesters_file):
                add_semester("S1", "Semestr 1", str(target_folder), [])
                add_semester("S2", "Semestr 2", str(target_folder), [])

                result = delete_semester("S1")
                data = load_semesters()

                self.assertTrue(result)
                self.assertNotIn("S1", data["semesters"])
                self.assertIn("S2", data["semesters"])
                self.assertEqual(data["active_semester"], "S2")
                self.assertTrue(test_file.exists())
