from pathlib import Path
from tempfile import TemporaryDirectory
from organizer_materials import (
    organize_files,
    execute_planned_operation,
)
from unittest.mock import patch

def prepare_test(root):
    source = root / "source"
    target = root / "target"

    source.mkdir()

    test_file = source / "11.11.2026_W01_algebra_Test.txt"
    test_file.write_text("Oryginalne dane", encoding="utf-8")

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

    return source, target, test_file, operations[0]


with TemporaryDirectory() as temp:
    source, target, test_file, operation = prepare_test(
        Path(temp)
    )

    target_file = Path(operation["target"])
    target_file.parent.mkdir(parents=True, exist_ok=True)
    target_file.write_text("NIE NADPISUJ", encoding="utf-8")

    success, message = execute_planned_operation(
        operation, source, target
    )

    assert not success
    assert test_file.exists()
    assert target_file.read_text(encoding="utf-8") == "NIE NADPISUJ"

    print("TEST 1: Ochrona przed nadpisaniem — OK")


with TemporaryDirectory() as temp:
    source, target, test_file, operation = prepare_test(
        Path(temp)
    )

    test_file.write_text(
        "Zmieniona zawartość pliku",
        encoding="utf-8"
    )

    success, message = execute_planned_operation(
        operation, source, target
    )

    assert not success
    assert test_file.exists()
    assert not Path(operation["target"]).exists()

    print("TEST 2: Wykrywanie zmiany pliku — OK")

with TemporaryDirectory() as temp:
    root = Path(temp)
    source, target, test_file, operation = prepare_test(root)

    outside = root / "outside.txt"
    operation["target"] = str(outside)

    success, message = execute_planned_operation(
        operation, source, target
    )

    assert not success
    assert test_file.exists()
    assert not outside.exists()

    print("TEST 3: Ochrona folderu docelowego — OK")


print("WSZYSTKIE TESTY BEZPIECZEŃSTWA PRZESZŁY")


with TemporaryDirectory() as temp:
    source, target, test_file, operation = prepare_test(
        Path(temp)
    )
    with patch(
        "organizer_materials.shutil.copyfileobj",
        side_effect=OSError("Symulowana awaria kopiowania")
    ):
        success, message = execute_planned_operation(
            operation, source, target
        )

    assert not success
    assert test_file.exists()
    assert not Path(operation["target"]).exists()

    print("TEST 4: Awaria kopiowania — OK")
