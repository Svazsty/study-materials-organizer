import json
from pathlib import Path

from subjects import load_subjects

SEMESTERS_FILE = (
    Path.home() / ".study-materials-organizer" / "semesters.json"
)


def load_semesters():
    try:
        data = SEMESTERS_FILE.read_text(encoding="utf-8")
        semesters = json.loads(data)

    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {
            "active_semester": None,
            "semesters": {}
        }

    if not isinstance(semesters, dict):
        return {
            "active_semester": None,
            "semesters": {}
        }

    if not isinstance(semesters.get("semesters"), dict):
        return {
            "active_semester": None,
            "semesters": {}
        }

    return semesters


def save_semesters(data):
    if not isinstance(data, dict):
        raise ValueError("Semester data must be a dictionary")

    if not isinstance(data.get("semesters"), dict):
        raise ValueError("Invalid semesters structure")

    SEMESTERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SEMESTERS_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def add_semester(semester_id, name, target, subjects):
    data = load_semesters()

    if semester_id in data["semesters"]:
        return False

    if not target:
        raise ValueError("Semester target cannot be empty")

    data["semesters"][semester_id] = {
        "name": name,
        "target": str(target),
        "subjects": list(subjects)
    }

    if data["active_semester"] is None:
        data["active_semester"] = semester_id

    save_semesters(data)
    return True


def set_semester_subjects(semester_id, subject_codes):
    data = load_semesters()
    semester = data["semesters"].get(semester_id)

    if semester is None:
        raise ValueError(f"Semester '{semester_id}' does not exist")

    if not isinstance(subject_codes, list):
        raise ValueError("Subjects must be a list")

    known_subjects = load_subjects()
    valid_codes = []

    for code in subject_codes:
        if not isinstance(code, str) or code not in known_subjects:
            raise ValueError(f"Unknown subject: {code}")

        if code not in valid_codes:
            valid_codes.append(code)

    semester["subjects"] = valid_codes
    save_semesters(data)


def delete_semester(semester_id):
    data = load_semesters()
    semester = data["semesters"]

    if semester_id not in semester:
        return False

    if len(semester) == 1:
        raise ValueError("Cannot delete the only semester")

    del semester[semester_id]

    if data["active_semester"] == semester_id:
        data["active_semester"] = next(iter(semester))

    save_semesters(data)
    return True
