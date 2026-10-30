import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path
from organizer_materials import organize_files
from subjects import load_subjects, add_subject
from tkinter.scrolledtext import ScrolledText
from queue import Queue, Empty
from threading import Thread
from settings import save_settings, load_settings

def main():
    window = tk.Tk()
    window.title("Study Materials Organizer")
    window.geometry("700x600")
    DONE = object()
    unknown_subjects = set()
    saved_settings = load_settings()
    progress_value = tk.DoubleVar(value=0)  #pasek postepu

    heading = ttk.Label(
        window,
        text = "Materials Organizer",
        padding = 20
    )
    heading.pack()


    source_path = tk.StringVar(
        value = saved_settings.get("last_source", "")
    )
    def choose_source():
        selected_folder = filedialog.askdirectory(
            parent = window,
            title = "Select a directory with materials",
        )

        if selected_folder:
            source_path.set(selected_folder)
            if target_path.get():
                save_settings(source_path.get(), target_path.get())

    source_button = ttk.Button(
        window,
        text = "Select source directory",
        command = choose_source
    )
    source_button.pack(pady = 10)
    source_label = ttk.Label(
        window,
        textvariable = source_path,
        wraplength = 650
    )
    source_label.pack(padx = 20)


    target_path = tk.StringVar(
        value = saved_settings.get("last_target", "")
    )

    def choose_target():
        selected_folder = filedialog.askdirectory(
            parent = window,
            title = "Select a destination semester directory",
        )
        if selected_folder:
            target_path.set(selected_folder)
            if source_path.get():
                save_settings(source_path.get(), target_path.get())

    target_button = ttk.Button(
        window,
        text = "Select target directory",
        command = choose_target
    )
    target_button.pack(pady = 10)
    target_label = ttk.Label(
        window,
        textvariable = target_path,
        wraplength = 650
    )
    target_label.pack(padx = 20)

    def ask_unknown_subjects():
        for code in sorted(unknown_subjects):
            name = simpledialog.askstring(
                "New subject",
                f"Enter the full name for: {code}",
                parent = window
            )
            if name is None:
                continue

            name = name.strip()

            if not name:
                messagebox.showerror(
                    "Invalid name",
                    "Subject name cannot be empty.",
                    parent = window
                )
                continue
            try:
                saved = add_subject(code, name)
            except (OSError, ValueError) as error:
                messagebox.showerror(
                    "Save failed",
                    str(error),
                    parent = window
                )
                continue

            if saved:
                output_box.configure(state="normal")
                output_box.insert(
                    tk.END,
                    f"Saved subject: {code} -> {name}\n"
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
                    prgoress_value.set(message[1])
                    progress_text.set(f"{message[1]:.0f}%")
                else:
                    output_box.insert(tk.END, message + "\n")
        except Empty:
            pass
        output_box.see(tk.END)
        output_box.configure(state="disabled")

        if finished:
            for button in (preview_button, apply_button, source_button, target_button):
                button.configure(state="normal")

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
                parent = window
            )
            return

        if apply_changes:
            confirm = messagebox.askyesno(
                "Confirm move",
                "Are you sure you want to move these files?",
                parent = window
            )
            if not confirm:
                return
        message_queue = Queue()   #tworzymy kolejke
        unknown_subjects.clear()  #czyscimy zbior nieznanych przedmiotow
        progress_value.set(0)  #resetujemy pasek postepu
        progress_text.set("0%")  #resetujemy pasek postepu
        output_box.configure(state="normal")
        output_box.delete(1.0, tk.END)
        output_box.configure(state="disabled")
        for button in (preview_button, apply_button, source_button, target_button):
            button.configure(state="disabled")

        def worker():
            try:
                organize_files(
                    source_folder = Path(source_text),
                    target_root = Path(target_text),
                    apply_changes = apply_changes,
                    subject_folders = load_subjects(),
                    log_callback = message_queue.put,
                    progress_callback = lambda percent: message_queue.put(("Progress", percent)),
                    unknown_subject_callback = lambda code: message_queue.put(("Unknown subject", code))
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
        text = "Preview",
        command = preview
    )

    apply_button = ttk.Button(
        window,
        text = "Apply Moves",
        command = apply_moves
    )

    preview_button.pack(pady = 10)
    apply_button.pack(pady = 10)
    prgoress_value = tk.DoubleVar(value=0) #pasek postepu
    progress_bar = ttk.Progressbar(
        window,
        orient = "horizontal",
        length = 400,
        mode = "determinate",
        maximum = 100,
        variable = prgoress_value
    )
    progress_bar.pack(pady = 10)
    progress_text = tk.StringVar(value="0%")
    progress_label = ttk.Label(
        window,
        textvariable = progress_text
    )
    progress_label.pack(pady = 5)

    output_box = ScrolledText(
        window,
        height = 12,
        wrap = tk.WORD,
        state = "disabled",
    )
    output_box.pack(
        padx = 20,
        pady = (0, 20),
        fill = tk.BOTH,
        expand = True,
    )

    def on_close():
        if preview_button.instate(["disabled"]) or apply_button.instate(["disabled"]):
            messagebox.showwarning(
                "Operation in progress",
                "Please wait for the operation to finish before closing.",
                parent = window
            )
            return
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_close)
    window.mainloop()

if __name__ == "__main__":
    main()