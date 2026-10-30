import json
from pathlib import Path

SETTINGS_FILE = Path.home() / ".study-materials-organizer" / "settings.json"

def save_settings(source, target):
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "last_source": source,
        "last_target": target
    }
    SETTINGS_FILE.write_text(
    json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

def load_settings():
    try:
        data = SETTINGS_FILE.read_text(encoding="utf-8")
        settings = json.loads(data)
        if not isinstance(settings, dict):
            return {}
        return settings

    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}