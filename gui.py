from pathlib import Path
from queue import Empty, Queue
from threading import Thread
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from tkinter.scrolledtext import ScrolledText

from organizer_materials import organize_files
from semesters import (
    add_semester,
    delete_semester,
    load_semesters,
    save_semesters,
    set_semester_subjects,
)
from settings import load_settings, save_settings
from subjects import add_subject, delete_subject, load_subjects


def main():
    window = tk.Tk()
    window.title("Study Materials Organizer")
    window.geometry("700x600")
    DONE = object()
    unknown_subjects = set()
    saved_settings = load_settings()
    semesters_data = load_semesters()
    progress_value = tk.DoubleVar(value=0)

    heading = ttk.Label(
        window,
        text="Materials Organizer",
        padding=20
    )
    heading.pack()

    source_path = tk.StringVar(
        value=saved_settings.get("last_source", "")
    )
    def choose_source():
        selected_folder = filedialog.askdirectory(
            parent=window,
            title="Select a directory with materials",
        )

        if selected_folder:
            source_path.set(selected_folder)
            if target_path.get():
                save_settings(source_path.get(), target_path.get())

    source_button = ttk.Button(
        window,
        text="Select source directory",
        command=choose_source
    )
    source_button.pack(pady=10)
    source_label = ttk.Label(
        window,
        textvariable=source_path,
        wraplength=650
    )
    source_label.pack(padx=20)

    target_path = tk.StringVar(
        value=saved_settings.get("last_target", "")
    )

    def choose_target():
        selected_folder = filedialog.askdirectory(
            parent=window,
            title="Select a destination semester directory",
        )
        if not selected_folder:
            return
        active_id = semesters_data["active_semester"]

        if active_id not in semesters_data["semesters"]:
            messagebox.showerror(
                "No active semester",
                "Please select a semester first.",
                parent=window
            )
            return
        semester = semesters_data["semesters"][active_id]
        previous_target = semester["target"]
        semester["target"] = selected_folder

        try:
            save_semesters(semesters_data)
        except OSError as error:
            semester["target"] = previous_target
            messagebox.showerror(
                "Save failed",
                str(error),
                parent=window
            )
            return
        target_path.set(selected_folder)
        if source_path.get():
            save_settings(source_path.get(), target_path.get())

    target_button = ttk.Button(
        window,
        text="Select target directory",
        command=choose_target
    )
    target_button.pack(pady=10)
    target_label = ttk.Label(
        window,
        textvariable=target_path,
        wraplength=650
    )
    target_label.pack(padx=20)

    semester_ids = list(semesters_data["semesters"])

    semester_names = [
        semesters_data["semesters"][semester_id]["name"]
        for semester_id in semester_ids
    ]

    semester_label = ttk.Label(
        window,
        text="Active semester"
    )
    semester_label.pack(pady=(15, 5))

    semester_combo = ttk.Combobox(
        window,
        values=semester_names,
        state="readonly"
    )
    semester_combo.pack(pady=5)

    active_id = semesters_data["active_semester"]

    if active_id in semester_ids:
        semester_combo.current(semester_ids.index(active_id))
        target_path.set(
            semesters_data["semesters"][active_id]["target"]
        )

    def on_semester_changed(event):
        selected_index = semester_combo.current()
        if selected_index == -1:
            return
        selected_id = semester_ids[selected_index]

        try:
            semesters_data["active_semester"] = selected_id
            save_semesters(semesters_data)

        except OSError as error:
            messagebox.showerror(
                "Save failed",
                str(error),
                parent=window
            )
            return
        selected_target = semesters_data["semesters"][selected_id]["target"]
        target_path.set(selected_target)

        if source_path.get():
            save_settings(source_path.get(), selected_target)

    semester_combo.bind(
        "<<ComboboxSelected>>",
        on_semester_changed
    )

    def open_subject_manager():
        active_id = semesters_data["active_semester"]
        semester = semesters_data["semesters"].get(active_id)

        if semester is None:
            messagebox.showerror(
                "No active semester",
                "Please select a semester first.",
                parent=window
            )
            return
        manager = tk.Toplevel(window)
        manager.title(f"Manage subjects for {semester['name']}")
        manager.geometry("500x600")
        manager.minsize(450, 500)

        ttk.Label(
            manager,
            text=f"Subjects for {semester['name']}",
            font=("Arial", 14, "bold")
        ).pack(pady=15)

        subject_frame = ttk.Frame(manager)
        subject_frame.pack(
            fill=tk.BOTH,
            expand=True,
            padx=20,
            pady=10
        )

        all_subjects = load_subjects()
        selected_vars = {}
        subject_widgets = {}

        for code, name in all_subjects.items():
            selected_vars[code] = tk.BooleanVar(
                value=code in semester["subjects"]
            )

            checkbox = ttk.Checkbutton(
                subject_frame,
                text=f"{name} ({code})",
                variable=selected_vars[code]
            )

            checkbox.pack(anchor="w", padx=20, pady=3)
            subject_widgets[code] = checkbox

        def add_new_subject():
            code = simpledialog.askstring(
                "Add new subject",
                "Enter subject code (e.g., algebra):",
                parent=manager
            )

            if code is None:
                return

            code = code.strip().lower()

            name = simpledialog.askstring(
                "Add new subject",
                "Enter full subject name (e.g., Algebra liniowa):",
                parent=manager
            )

            if name is None:
                return

            name = name.strip()

            if not name:
                messagebox.showerror(
                    "Invalid name",
                    "Subject name cannot be empty.",
                    parent=manager
                )
                return

            try:
                created = add_subject(code, name)

            except (OSError, ValueError) as error:
                messagebox.showerror(
                    "Save failed",
                    str(error),
                    parent=manager
                )
                return

            if not created:
                messagebox.showerror(
                    "Subject exists",
                    f"Subject with code {code} already exists.",
                    parent=manager
                )
                return

            all_subjects[code] = name
            selected_vars[code] = tk.BooleanVar(value=True)

            checkbox = ttk.Checkbutton(
                subject_frame,
                text=f"{name} ({code})",
                variable=selected_vars[code]
            )
            checkbox.pack(anchor="w", padx=20, pady=3)
            subject_widgets[code] = checkbox

        ttk.Button(
            manager,
            text="Add new subject",
            command=add_new_subject
        ).pack(pady=5)

        def open_delete_subject():
            codes = list(selected_vars)

            if not codes:
                messagebox.showinfo(
                    "No subjects",
                    "There are no subjects to delete.",
                    parent=manager
                )
                return

            dialog = tk.Toplevel(manager)
            dialog.title("Delete subject")
            dialog.geometry("420x190")
            dialog.transient(manager)

            ttk.Label(
                dialog,
                text="Select a subject to delete",
                font=("Arial", 12, "bold")
            ).pack(pady=15)

            choices = [
                f"{all_subjects.get(code, code)} ({code})"
                for code in codes
            ]
            subject_combo = ttk.Combobox(
                dialog,
                values=choices,
                state="readonly"
            )

            subject_combo.pack(
                fill="x",
                padx=20,
                pady=5
            )

            def confirm_delete():
                index = subject_combo.current()

                if index == -1:
                    messagebox.showerror(
                        "No selection",
                        "Please select a subject to delete.",
                        parent=dialog
                    )
                    return

                code = codes[index]

                confirmed = messagebox.askyesno(
                    "Confirm deletion",
                    f"Delete subject '{all_subjects.get(code, code)}' "
                    f"({code})?\n\n"
                    "This removes the subject definition only if it is not assigned "
                    "to any semester. It will not delete files.",
                    parent=dialog
                )

                if not confirmed:
                    return

                try:
                    deleted = delete_subject(code)

                except (OSError, ValueError) as error:
                    messagebox.showerror(
                        "Delete failed",
                        f"{error}\n\n"
                        "If the subject is assigned to a semester, "
                        "uncheck it and save first.",
                        parent=dialog
                    )
                    return

                if not deleted:
                    messagebox.showwarning(
                        "Subject not found",
                        f"Subject '{all_subjects.get(code, code)}' "
                        f"({code}) was not found.",
                        parent=dialog
                    )
                    return

                subject_widgets.pop(code).destroy()
                selected_vars.pop(code, None)
                all_subjects.pop(code, None)
                dialog.destroy()

            ttk.Button(
                dialog,
                text="Delete Selected",
                command=confirm_delete
            ).pack(pady=15)

        ttk.Button(
            manager,
            text="Delete subject",
            command=open_delete_subject
        ).pack(pady=5)

        def save_subject_selection():
            selected_codes = [
                code
                for code, var in selected_vars.items()
                if var.get()
            ]

            try:
                set_semester_subjects(active_id, selected_codes)
            except (OSError, ValueError) as error:
                messagebox.showerror(
                    "Save failed",
                    str(error),
                    parent=manager
                )
                return

            semester["subjects"] = selected_codes
            manager.destroy()

        ttk.Button(
            manager,
            text="Save",
            command=save_subject_selection
        ).pack(pady=15)

    manage_button = ttk.Button(
        window,
        text="Manage subjects",
        command=open_subject_manager
    )
    manage_button.pack(pady=10)

    def create_semester():
        semester_id = simpledialog.askstring(
            "Add semester",
            "Enter semester ID (e.g., 2026-2027-S1):",
            parent=window
        )

        if semester_id is None:
            return

        semester_id = semester_id.strip()

        if not semester_id:
            messagebox.showerror(
                "Invalid ID",
                "Semester ID cannot be empty.",
                parent=window
            )
            return

        if semester_id in semesters_data["semesters"]:
            messagebox.showerror(
                "Duplicate semester ID",
                f"Semester with ID {semester_id} already exists.",
                parent=window
            )
            return

        name = simpledialog.askstring(
            "Add semester",
            "Enter semester name (e.g., Semestr 1):",
            parent=window
        )

        if name is None:
            return

        name = name.strip()

        if not name:
            messagebox.showerror(
                "Invalid name",
                "Semester name cannot be empty.",
                parent=window
            )
            return

        target = filedialog.askdirectory(
            parent=window,
            title="Select target directory for the semester"
        )

        if not target:
            return

        try:
            created = add_semester(semester_id, name, target, [])
        except (OSError, ValueError) as error:
            messagebox.showerror(
                "Save failed",
                str(error),
                parent=window
            )
            return

        if not created:
            messagebox.showerror(
                "Semester exists",
                f"Semester with ID {semester_id} already exists.",
                parent=window
            )
            return

        semesters_data.update(load_semesters())
        semester_ids.append(semester_id)
        semester_names.append(name)
        semester_combo.configure(values=semester_names)

        messagebox.showinfo(
            "Semester added",
            f"Semester {name} ({semester_id}) added successfully.",
            parent=window
        )

    add_semester_button = ttk.Button(
        window,
        text="Add new semester",
        command=create_semester
    )
    add_semester_button.pack(pady=5)

    def remove_semester():
        active_id = semesters_data["active_semester"]
        semester = semesters_data["semesters"].get(active_id)

        if semester is None:
            messagebox.showerror(
                "No active semester",
                "Please select a semester first.",
                parent=window
            )
            return

        confirm = messagebox.askyesno(
            "Delete Semester",
            f"Delete semester '{semester['name']}'?\n\n"
            "Only semester configuration will be removed.\n"
            "Files and folders will remain untouched.",
            parent=window
        )

        if not confirm:
            return

        try:
            deleted = delete_semester(active_id)

        except (OSError, ValueError) as error:
            messagebox.showerror(
                "Delete failed",
                str(error),
                parent=window
            )
            return

        if not deleted:
            return

        semesters_data.clear()
        semesters_data.update(load_semesters())
        semester_ids[:] = list(semesters_data["semesters"])

        semester_names[:] = [
            semesters_data["semesters"][semester_id]["name"]
            for semester_id in semester_ids
        ]

        semester_combo.configure(values=semester_names)
        new_active_id = semesters_data["active_semester"]
        semester_combo.current(semester_ids.index(new_active_id))

        new_target = semesters_data["semesters"][new_active_id]["target"]
        target_path.set(new_target)

        messagebox.showinfo(
            "Semester deleted",
            f"Semester '{semester['name']}' deleted successfully.",
            parent=window
        )

    delete_semester_button = ttk.Button(
        window,
        text="Delete Semester",
        command=remove_semester
    )

    delete_semester_button.pack(pady=5)

    def ask_unknown_subjects():
        for code in sorted(unknown_subjects):
            name = simpledialog.askstring(
                "New subject",
                f"Enter the full name for: {code}",
                parent=window
            )
            if name is None:
                continue

            name = name.strip()

            if not name:
                messagebox.showerror(
                    "Invalid name",
                    "Subject name cannot be empty.",
                    parent=window
                )
                continue
            try:
                saved = add_subject(code, name)
            except (OSError, ValueError) as error:
                messagebox.showerror(
                    "Save failed",
                    str(error),
                    parent=window
                )
                continue

            if not saved:
                continue

            active_id = semesters_data["active_semester"]
            semester = semesters_data["semesters"].get(active_id)
            if semester is None:
                messagebox.showerror(
                    "Assignment failed",
                    "No active semester is available.",
                    parent=window,
                )
                continue

            updated_subjects = semester["subjects"] + [code]
            try:
                set_semester_subjects(active_id, updated_subjects)
            except (OSError, ValueError) as error:
                messagebox.showerror(
                    "Assignment failed",
                    f"Subject saved, but not assigned: {error}",
                    parent=window,
                )
                continue

            semester["subjects"] = updated_subjects

            output_box.configure(state="normal")
            output_box.insert(
                tk.END,
                f"Added new subject: {code} -> {name}\n",
            )
            output_box.configure(state="disabled")

    def process_messages(message_queue, apply_changes):
        finished = False
        output_box.configure(state="normal")

        try:
            while True:
                message = message_queue.get_nowait()

                if message is DONE:
                    finished = True
                    break

                if isinstance(message, tuple) and message[0] == "Unknown subject":
                    unknown_subjects.add(message[1])
                    output_box.insert(
                        tk.END,
                        f"New subject detected: {message[1]}\n"
                    )
                    continue
                if isinstance(message, tuple) and message[0] == "Progress":
                    progress_value.set(message[1])
                    progress_text.set(f"{message[1]:.0f}%")
                else:
                    output_box.insert(tk.END, message + "\n")
        except Empty:
            pass
        output_box.see(tk.END)
        output_box.configure(state="disabled")

        if finished:
            for button in (
                preview_button,
                apply_button,
                source_button,
                target_button,
                delete_semester_button,
                add_semester_button,
                manage_button,
            ):
                button.configure(state="normal")
            semester_combo.configure(state="readonly")

            if not apply_changes and unknown_subjects:
                window.after(0, ask_unknown_subjects)
        else:
            window.after(100, process_messages, message_queue, apply_changes)

    def run_organizer(apply_changes):
        source_text = source_path.get()
        target_text = target_path.get()

        if not source_text or not target_text:
            messagebox.showerror(
                "Missing directories",
                "Please select a source and target directory",
                parent=window
            )
            return

        active_id = semesters_data["active_semester"]
        active_semester = semesters_data["semesters"].get(active_id)

        if active_semester is None:
            messagebox.showerror(
                "No active semester",
                "Please select a semester first.",
                parent=window
            )
            return

        if not active_semester["subjects"]:
            messagebox.showerror(
                "No subjects",
                "There are no subjects in the active semester.",
                parent=window
            )
            return

        if apply_changes:
            confirm = messagebox.askyesno(
                "Confirm move",
                "Are you sure you want to move these files?",
                parent=window
            )
            if not confirm:
                return
        message_queue = Queue()
        unknown_subjects.clear()
        progress_value.set(0)
        progress_text.set("0%")
        output_box.configure(state="normal")
        output_box.delete(1.0, tk.END)
        output_box.configure(state="disabled")

        for button in (
            preview_button,
            apply_button,
            source_button,
            target_button,
            delete_semester_button,
            add_semester_button,
            manage_button,
        ):
            button.configure(state="disabled")
        semester_combo.configure(state="disabled")

        def worker():
            try:
                all_subjects = load_subjects()
                allowed_codes = set(active_semester["subjects"])
                semester_subjects = {
                    code: name
                    for code, name in all_subjects.items()
                    if code in allowed_codes
                }
                organize_files(
                    source_folder=Path(source_text),
                    target_root=Path(target_text),
                    apply_changes=apply_changes,
                    subject_folders=semester_subjects,
                    log_callback=message_queue.put,
                    progress_callback=lambda percent: message_queue.put(
                        ("Progress", percent)
                    ),
                    unknown_subject_callback=lambda code: (
                        message_queue.put(("Unknown subject", code))
                        if code not in all_subjects
                        else None
                    )
                )
            except Exception as error:
                message_queue.put(f"Organizer error: {error}")
            finally:
                message_queue.put(DONE)

        thread = Thread(target=worker)
        thread.start()
        window.after(100, process_messages, message_queue, apply_changes)

    def preview():
        run_organizer(False)

    def apply_moves():
        run_organizer(True)

    preview_button = ttk.Button(
        window,
        text="Preview",
        command=preview
    )

    apply_button = ttk.Button(
        window,
        text="Apply Moves",
        command=apply_moves
    )

    preview_button.pack(pady=10)
    apply_button.pack(pady=10)
    progress_bar = ttk.Progressbar(
        window,
        orient="horizontal",
        length=400,
        mode="determinate",
        maximum=100,
        variable=progress_value
    )
    progress_bar.pack(pady=10)
    progress_text = tk.StringVar(value="0%")
    progress_label = ttk.Label(
        window,
        textvariable=progress_text
    )
    progress_label.pack(pady=5)

    output_box = ScrolledText(
        window,
        height=12,
        wrap=tk.WORD,
        state="disabled",
    )
    output_box.pack(
        padx=20,
        pady=(0, 20),
        fill=tk.BOTH,
        expand=True,
    )

    def on_close():
        if (
            preview_button.instate(["disabled"])
            or apply_button.instate(["disabled"])
        ):
            messagebox.showwarning(
                "Operation in progress",
                "Please wait for the operation to finish before closing.",
                parent=window
            )
            return
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_close)
    window.mainloop()


if __name__ == "__main__":
    main()
