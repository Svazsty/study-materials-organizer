import json
import re
from pathlib import Path


DEFAULT_SUBJECTS_FILE = Path(__file__).with_name("subjects.json")

SUBJECTS_FILE = (
    Path.home() / ".study-materials-organizer" / "subjects.json"
)


def ensure_subjects_file():
    if SUBJECTS_FILE.exists():
        return

    SUBJECTS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if not DEFAULT_SUBJECTS_FILE.is_file():
        raise FileNotFoundError(
            "Brakuje domyślnego pliku subjects.json"
        )

    try:
        with SUBJECTS_FILE.open("xb") as file:
            file.write(DEFAULT_SUBJECTS_FILE.read_bytes())
    except FileExistsError:
        pass

def load_subjects():
    ensure_subjects_file()
    with SUBJECTS_FILE.open("r", encoding="utf-8") as file:
        subjects = json.load(file)

    if not isinstance(subjects, dict):
        raise ValueError("Invalid subjects.json format: expected a dictionary")

    return subjects


def add_subject(code, name):
    if not isinstance(code, str) or not re.fullmatch(r"[a-zA-Z0-9_-]+", code):
        raise ValueError(
            "Subject code must be a string containing only letters, "
            "numbers, underscores, or hyphens"
        )

    if not isinstance(name, str) or not name.strip():
        raise ValueError("Subject name must be a non-empty string")
    name = name.strip()

    subjects = load_subjects()

    forbidden_chars = '<>:"/\\|?*'

    if any(char in name for char in forbidden_chars):
        raise ValueError(
            "Subject name contains forbidden characters"
        )

    if code in subjects:
        return False  # Subject code already exists

    subjects[code] = name

    SUBJECTS_FILE.write_text(
        json.dumps(subjects, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    return True  # Subject added successfully


def delete_subject(code):
    subjects = load_subjects()

    if code not in subjects:
        return False  # Subject code does not exist

    from semesters import SEMESTERS_FILE

    if SEMESTERS_FILE.exists():
        data = json.loads(SEMESTERS_FILE.read_text(encoding="utf-8"))

        if not isinstance(data, dict) or not isinstance(data.get("semesters"), dict):
            raise ValueError("Invalid semesters configuration")

        for semester_id, semester in data["semesters"].items():
            if code in semester.get("subjects", []):
                raise ValueError(
                    f"Subject is assigned to semester '{semester_id}"
                    "'. Remove it from the semester before deleting."
                )

    del subjects[code]

    SUBJECTS_FILE.write_text(
        json.dumps(subjects, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    return True
