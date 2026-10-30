# Study Materials Organizer

A lightweight Python desktop application for organizing
university study materials based on filenames.

The application provides both a graphical interface (Tkinter)
and a command-line interface (CLI).

Users can preview planned file operations before moving
files into organized semester directories.

## Features

- Graphical interface built with Tkinter.
- Preview file operations before applying changes.
- Organize files by subject, date, class type and group.
- Background file operations using threading.
- Progress bar based on processed files.
- Automatically remember recently selected directories.
- Detect unknown subjects and add them through the GUI.
- Store subject definitions in subjects.json.
- Prevent overwriting existing destination files.
- Command-line interface support.

## Requirements

- Python 3.13 or newer (tested on Windows with Python 3.14).
- No third-party packages are required; the tool uses the Python standard library.

The source folder must already exist. Run the following commands from the directory containing `organizer_materials.py`.


## Graphical Interface

Launch the desktop application:

```powershell
python gui.py
```

### How to use

1. Select a source directory containing study materials.
2. Select the destination semester directory.
3. Click **Preview** to review planned file operations.
4. Click **Apply Moves** to move files after confirmation.

The application moves files rather than copying them. Existing destination files are not overwritten.

### Progress and background operations

File operations run in a background thread to keep the GUI responsive.

The progress bar displays the percentage of processed files, not the percentage of bytes transferred.

### Saved settings

The application automatically remembers the last selected source and destination directories.

Settings are stored in:

`~/.study-materials-organizer/settings.json`

### Subject management

Subject definitions are stored in `subjects.json`.

When Preview detects an unknown subject code, the application can ask for its full name and save it for future use.

After adding a subject, run Preview again to update the planned file operations.


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

Subjects are loaded from subjects.json.

New subjects can be added through the graphical interface
or manually by editing subjects.json.

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

Invalid or unsupported filenames count as skipped files. Failed move operations count as errors in the summary.

## Tests

Run the automated tests:

```powershell
python -m unittest -v
```

The project currently includes 10 automated tests.

The tests cover:
- Date validation.
- Preview operations without modifying files.
- Moving files and preserving their contents.
- Preventing overwriting existing files.
- Progress callback reporting.
- Unknown subject detection.
- Adding new subjects.
- Preventing duplicate subject codes.
- Rejecting invalid subject names.

File operation tests use temporary directories to avoid
modifying real study materials.

## License

This project is licensed under the [MIT License](LICENSE).