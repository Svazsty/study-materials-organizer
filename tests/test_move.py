
from pathlib import Path
from tempfile import TemporaryDirectory
from organizer_materials import (
    organize_files,
    execute_planned_operation,
)

with TemporaryDirectory() as temporary:
    root = Path(temporary)
    source = root / "source"
    target = root / "target"

    source.mkdir()

    test_file = source / "11.11.2026_W01_algebra_Test.txt"
    test_file.write_text("Przykladowe dane", encoding="utf-8")

    operations = []

    result = organize_files(
        source_folder=source,
        target_root=target,
        apply_changes=False,
        subject_folders={"algebra": "Algebra liniowa"},
        log_callback=lambda message: None,
        plan_callback=operations.append,
    )

    assert result["planned"] == 1
    assert len(operations) == 1

    operation = operations[0]

    success, message = execute_planned_operation(
        operation,
        source,
        target,
    )

    assert success, message
    assert not test_file.exists()

    target_file = Path(operation["target"])
    assert target_file.exists()
    assert target_file.read_text(
        encoding="utf-8"
    ) == "Przykladowe dane"

    print("TEST PRZENOSZENIA: OK")

    success, message = execute_planned_operation(
        operation,
        source,
        target,
    )

    assert not success
    assert target_file.read_text(
        encoding="utf-8"
    ) == "Przykladowe dane"

    print("TEST PONOWNEGO WYKONANIA: OK")
    print("WSZYSTKIE TESTY OK")
