from pathlib import Path
from tempfile import TemporaryDirectory

from organizer_materials import organize_files

with TemporaryDirectory() as temporary:
    root = Path(temporary)
    source = root / "source"
    target = root / "target"

    source.mkdir()

    test_file = source / "11.11.2026_W01_algebra_Notatki.txt"
    test_file.write_text("Test", encoding="utf-8")

    planned_operations = []

    result = organize_files(
        source_folder=source,
        target_root=target,
        apply_changes=False,
        subject_folders={"algebra": "Algebra liniowa"},
        log_callback=lambda message: None,
        plan_callback=planned_operations.append,
    )

    assert result["planned"] == 1
    assert len(planned_operations) == 1
    assert test_file.exists()
    assert not target.exists()

    print("TEST OK")
    print(planned_operations[0])
    print(result)

