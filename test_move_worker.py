import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from PySide6.QtCore import QCoreApplication, QTimer
from organizer_materials import organize_files
from window_test import MoveWorker

with TemporaryDirectory() as temporary:
    root = Path(temporary)
    source = root / "source"
    target = root / "target"
    source.mkdir()

    first = source / "11.11.2026_W01_algebra_A.txt"
    second = source / "11.11.2026_W01_algebra_B.txt"

    first.write_text("Pierwszy plik", encoding="utf-8")
    second.write_text("Drugi plik", encoding="utf-8")

    operations = []

    result = organize_files(
        source_folder=source,
        target_root=target,
        apply_changes=False,
        subject_folders={"algebra": "Algebra liniowa"},
        log_callback=lambda message: None,
        plan_callback=operations.append,
    )

    assert result["planned"] == 2

    conflict = next(
        op for op in operations
        if op["filename"] == second.name
    )

    conflict_target = Path(conflict["target"])
    conflict_target.parent.mkdir(parents=True, exist_ok=True)
    conflict_target.write_text(
        "NIE NADPISUJ", encoding="utf-8"
    )

    app = QCoreApplication(sys.argv)
    received = {}

    worker = MoveWorker(operations, source, target)

    worker.progress_changed.connect(
        lambda value: print(f"Postęp: {value}%")
    )

    worker.move_completed.connect(
        lambda results, summary: received.update(
            results=results,
            summary=summary,
        )
    )

    worker.move_failed.connect(
        lambda message: received.update(error=message)
    )

    worker.finished.connect(app.quit)
    QTimer.singleShot(10000, app.quit)

    worker.start()
    app.exec()

    assert not worker.isRunning(), "Wątek nie zakończył pracy"
    assert "error" not in received, received.get("error")
    assert "summary" in received, "Brak wyniku wątku"

    summary = received["summary"]

    assert summary["moved"] == 1
    assert summary["failed"] == 1
    assert summary["total"] == 2

    assert not first.exists()
    assert second.exists()

    assert conflict_target.read_text(
        encoding="utf-8"
    ) == "NIE NADPISUJ"

    print("TEST MOVEWORKER: OK")
    print(summary)
