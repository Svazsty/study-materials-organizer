import json
from pathlib import Path

SUBJECTS_FILE = Path(__file__).with_name("subjects.json")

def load_subjects():
    with SUBJECTS_FILE.open("r", encoding="utf-8") as file:
        subjects = json.load(file)

    if not isinstance(subjects, dict):
        raise ValueError("Invalid subjects.json format: expected a dictionary")

    return subjects

def add_subject(code, name):
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