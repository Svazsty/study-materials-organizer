# Study Materials Organizer

A small Python command-line tool that organizes study materials using information stored in filenames. It previews changes by default and moves files only when `--apply` is provided.

## Features

- Reads files directly from one source folder.
- Recognizes lecture and exercise filenames, dates, subject codes, and exercise groups.
- Builds subject and session folders while preserving filenames.
- Handles existing session folders with part letters such as `W02A`.
- Skips existing destination paths and files marked `do_weryfikacji`.
- Prints a summary of checked, planned, moved, skipped, and failed files.

## Requirements

- Python 3.13 or newer (tested on Windows with Python 3.14).
- No third-party packages are required; the tool uses the Python standard library.

The source folder must already exist. Run the following commands from the directory containing `organizer_materials.py`.

## Usage

### Preview changes

Choose a source folder containing your materials and a target folder representing the root of a semester:

```powershell
python organizer_materials.py --source "incoming" --target "organized"
```

This prints the planned moves. It leaves the source files in place and does not create target folders.

### Move files

After reviewing the preview, run the same command with `--apply`:

```powershell
python organizer_materials.py --source "incoming" --target "organized" --apply
```

A successful move removes the file from the source folder and places it in the destination folder.

### Help

```powershell
python organizer_materials.py --help
```

| Argument | Purpose |
| --- | --- |
| `--source PATH` | Folder containing files to organize |
| `--target PATH` | Root of the destination semester folder |
| `--apply` | Perform moves instead of previewing them |
| `--help` | Show command-line help |

Quote paths containing spaces. Relative paths are resolved from the terminal's current working directory.

### Personal defaults

If `--source` or `--target` is omitted, the script uses its configured defaults:

- Source: `G:\Mój dysk`
- Target: `G:\Mój dysk\STUDIA\2026-2027\Semestr 1`

To use different locations, pass the arguments above or edit `source_folder` and `target_root` near the top of the script. Running without arguments previews the default locations; running with only `--apply` moves files using those defaults.

## Filename conventions

Lecture:

```text
DD.MM.YYYY_WNN[A]_subject[_description].ext
```

Exercise:

```text
DD.MM.YYYY_CNN[A]_Gnumber_subject[_description].ext
```

Square brackets indicate optional parts; do not include the brackets in filenames.

- `DD.MM.YYYY`: the date of the class.
- `W` / `C`: lecture / exercise.
- `NN`: a two-digit session number, for example `01` or `02`.
- `A`: an optional uppercase part letter, such as `A`, `B`, or `C`.
- `Gnumber`: `G1` or `G2`, required for exercises.
- `subject`: a configured subject code, listed below.
- `description`: optional text, which may contain underscores.
- `.ext`: the original file extension, such as `.aac`, `.mp4`, `.pdf`, or `.md`.

Use lowercase subject codes. Put the subject code before the description.

Examples:

```text
03.10.2026_W01A_algebra_liczby_zespolone.aac
23.10.2026_W02B_ekonomia.mp4
18.10.2026_W02_algebra_notatki_zeszyt.pdf
17.10.2026_C01_G2_ekonomia_mikroekonomia.aac
```

### Configured subjects

| Code | Destination subject folder |
| --- | --- |
| `algebra` | Algebra liniowa |
| `ekonomia` | Podstawy ekonomii |
| `logika` | Algorytmy i podstawy logiki |
| `prawo` | Prawo gospodarcze |
| `rozniczkowy` | Układ różniczkowy |
| `ti` | Technologie informacyjne |
| `zarzadzanie` | Podstawy zarządzania |

Edit the `subject_folders` dictionary to customize this mapping.

## Destination structure

Lecture example, relative to `--target`:

```text
Wyklady/Algebra liniowa/03.10.2026_W01/03.10.2026_W01A_algebra_liczby_zespolone.aac
```

Exercise example:

```text
Cwiczenia/Podstawy ekonomii/grupa_2/17.10.2026_C01/17.10.2026_C01_G2_ekonomia_mikroekonomia.aac
```

An existing common session folder such as `16.10.2026_W02` takes priority. If it does not exist, the tool checks for a folder matching the complete class code, such as `16.10.2026_W02A`. If only other part folders exist, the file is skipped for manual review. Otherwise, a new common session folder is planned and created when applying changes.

## Skipped files and limitations

- Only files directly inside the source folder are inspected; subfolders are skipped.
- Classification uses filenames and folder names, not document or recording contents.
- Invalid dates, unsupported class codes, unknown subjects, and missing or unsupported groups are skipped.
- Filenames containing `do_weryfikacji`, case-insensitively, are skipped.
- Existing destination paths are skipped without comparing file contents.
- Exercise groups are currently limited to `G1` and `G2`.
- General materials without a session date require manual organization.
- The current interface is command-line only.

Invalid or unsupported filenames count as skipped files. Failed move operations count as errors in the summary.

## Tests

Run the automated tests:

```powershell
python -m unittest -v
```

The five tests cover a valid date, an invalid date, preview behavior, moving a file with its contents preserved, and skipping an existing destination without changing either file. File-operation tests use temporary directories.

## License

This project is licensed under the [MIT License](LICENSE).