from pathlib import Path
from datetime import datetime
import shutil
import re
import argparse
from subjects import load_subjects


source_folder = Path(r"G:\Mój dysk")
target_root = Path(r"G:\Mój dysk\STUDIA\2026-2027\Semestr 1")

def parse_date(date_text):
    try:
        return datetime.strptime(date_text, "%d.%m.%Y")
    except ValueError:
        return None

def get_class_type(class_code):
    if class_code.startswith("W"):
        return "Wyklady"
    elif class_code.startswith("C"):
        return "Cwiczenia"
    return None

def build_target_folder(root, class_type, subject_folder, date_folder, group):
    folder = root / class_type / subject_folder
    if group is not None:
        folder = folder / group.replace("G", "grupa_")
    return folder / date_folder

def move_file(source, target, log_callback = print):
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(source, target)
    except OSError as error:
        log_callback(f"Blad przenoszenia {source.name}: {error}")
        return False
    return True


def organize_files(source_folder, target_root,
                   apply_changes, subject_folders,
                   log_callback = None, progress_callback = None,
                   unknown_subject_callback = None):
    def log(message):
        if log_callback is None:
            print(message)
        else:
            log_callback(message)
    if not source_folder.is_dir():
        log(f"Folder zrodlowy nie istnieje lub jest niedostepny: {source_folder}")
        return
    checked_count = 0
    moved_count = 0
    planned_count = 0
    error_count = 0

    files_to_prcess = [
        file for file in source_folder.iterdir() if file.is_file()
    ]
    total_files = len(files_to_prcess)
    for index, source_file in enumerate(files_to_prcess, start=1):
        if progress_callback:
            progress = (index - 1) / total_files * 100
            progress_callback(progress)

        checked_count += 1

        if progress_callback:
            progress_callback(index / total_files * 100)

        file_name = source_file.name
        if "do_weryfikacji" in file_name.lower():
            log(f"Plik wymaga recznego sprawdzenia: {file_name}")
            continue
        name_without_ext = Path(file_name).stem
        parts = name_without_ext.split("_", maxsplit=4)

        if len(parts) < 3:
            log(f"Pomijam plik z niepoprawna nazwa: {file_name}")
            continue
        date = parts[0]
        clas = parts[1]

        if not re.fullmatch(r"[WC][0-9]{2}[A-Z]?", clas):
            log(f"Niepoprawne oznaczenie zajec: {file_name}")
            continue
        group = None

        if clas.startswith("C"):
            if len(parts) < 4:
                log(f"Brak grupy lub przedmiotu: {file_name}")
                continue
            group = parts[2]

            if group not in ("G1", "G2"):
                log(f"Niepoprawna grupa: {file_name}")
                continue
            subject = parts[3]
        else:
            subject = parts[2]

        parsed_date = parse_date(date)
        if parsed_date is None:
            log(f"Pomijam plik z niepoprawna data: {file_name}")
            continue
        date = parsed_date.strftime("%d.%m.%Y") + "_" + clas[:3]

        class_type = get_class_type(clas)
        if class_type is None:
            log(f"Pomijam plik z niepoprawnym typem zajec: {file_name}")
            continue
        subject_folder = subject_folders.get(subject)

        if subject_folder is None:
            log(f"Brak przypisanego folderu dla przedmiotu: {subject}")

            if unknown_subject_callback is not None:
                unknown_subject_callback(subject)

            continue

        target_folder = build_target_folder(
            target_root, class_type, subject_folder, date, group
        )
        if not target_folder.exists():
            part_folder = target_folder.parent / (
                target_folder.name + clas[3:]
            )
            if part_folder.is_dir():
                target_folder = part_folder
            else:
                split_folders = list(
                    target_folder.parent.glob(target_folder.name + "[A-Z]")
                )
                if split_folders:
                    log(f"Nie mozna ustalic folderu docelowego: {file_name}")
                    continue

        target_file = target_folder / file_name

        if target_file.exists():
            log(f"Pomijam, plik docelowy juz istnieje: {target_file}")
            continue

        if apply_changes:
            moved = move_file(source_file, target_file, log)
            if not moved:
                error_count += 1
                continue
            moved_count += 1
            log(f"Przeniesiono: {target_file}")
        else:
            planned_count += 1
            log(f"Planowane przeniesienie: {source_file} -> {target_file}")

    if progress_callback is not None:
        progress_callback(100)

    skipped_count = checked_count - planned_count - moved_count - error_count

    log(f"\nSprawdzono {checked_count} plikow")
    log(f"Zplanowano {planned_count} plikow")
    log(f"Przeniesiono {moved_count} plikow")
    log(f"Pominieto {skipped_count} plikow")
    log(f"{error_count} Bledow")
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Organizer materialow ze studiow"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Wykonaj przenoszenie plikow"
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=source_folder,
        help="Folder z plikami do uporzadkowania"
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=target_root,
        help="Folder docelowy semestru"
    )
    args = parser.parse_args()
    organize_files(
        args.source, args.target, args.apply, load_subjects()
    )