import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from PIL import Image, ImageTk

REPORTS = {
    "VeeamOnPrem(PDF)": {
        "text": "On-Prem (PDF)",
        "group": "Veeam",
        "enabled": True,
    },
    "VeeamOnPrem(CSV)": {
        "text": "On-Prem (CSV)",
        "group": "Veeam",
        "enabled": True,
    },
    "VeeamAzure(PDF)": {
        "text": "Azure (PDF)",
        "group": "Veeam",
        "enabled": False,
    },
    "VeeamAzure(CSV)": {
        "text": "Azure (CSV)",
        "group": "Veeam",
        "enabled": True,
    },
    "CCL": {
        "text": "CCL",
        "group": "CCL",
        "enabled": True,
    },
    "BackupExec20": {
        "text": "Caso 20",
        "group": "Backup Exec",
        "enabled": True,
    },
    "BackupExec30": {
        "text": "Caso 30",
        "group": "Backup Exec",
        "enabled": True,
    },
    "BackupExec50": {
        "text": "Caso 50",
        "group": "Backup Exec",
        "enabled": True,
    },
    "BackupExec60": {
        "text": "Caso 6-",
        "group": "Backup Exec",
        "enabled": True,
    },
    "BackupExec90": {
        "text": "Caso 90",
        "group": "Backup Exec",
        "enabled": True,
    },
}


def center_window(window, width, height):

    window.update_idletasks()

    x = (window.winfo_screenwidth() - width) // 2
    y = (window.winfo_screenheight() - height) // 2

    window.geometry(
        f"{width}x{height}+{x}+{y}"
    )


def select_sources():

    result = {
        key: False
        for key in REPORTS
    }

    window = ttk.Window(
        title="RMC Checker",
        themename="solar"  # dark mode
    )

    window.resizable(False, False)

    center_window(window, 500, 700)

    main_frame = ttk.Frame(
        window,
        padding=20
    )

    main_frame.pack(
        fill="both",
        expand=True
    )

    header_frame = ttk.Frame(main_frame)
    header_frame.pack(
        fill="x",
        pady=(0, 15)
    )

    # Left side
    title_frame = ttk.Frame(header_frame)
    title_frame.pack(
        side="left",
        fill="x",
        expand=True
    )

    ttk.Label(
        title_frame,
        text="RMC Checker",
        font=("Segoe UI", 16, "bold")
    ).pack(
        anchor="w"
    )

    ttk.Label(
        title_frame,
        text="Backup Validation Tool",
        bootstyle="secondary"
    ).pack(
        anchor="w"
    )

    # Right side image
    img = Image.open("Te-Whatu-Ora-Logo.png")
    img.thumbnail((250, 80))

    logo = ImageTk.PhotoImage(img)

    logo_label = ttk.Label(
        header_frame,
        image=logo
    )

    # Keep reference or image disappears
    logo_label.image = logo

    logo_label.pack(
        side="right",
        padx=(10, 0)
    )

    variables = {}

    select_all_var = tk.BooleanVar()

    def toggle_all():

        state = select_all_var.get()

        for key, var in variables.items():

            if not REPORTS[key]["enabled"]:
                continue

            var.set(state)

    ttk.Checkbutton(
        main_frame,
        text="Select All",
        variable=select_all_var,
        command=toggle_all,
        bootstyle="round-toggle"
    ).pack(
        anchor="w",
        pady=(0, 15)
    )

    groups = {}

    for key, config in REPORTS.items():

        groups.setdefault(
            config["group"],
            []
        ).append(key)

    for group_name, report_keys in groups.items():

        frame = ttk.LabelFrame(
            main_frame,
            text=f" {group_name} ",
            padding=12,
            bootstyle="info"
        )

        frame.pack(
            fill="x",
            pady=6
        )

        for key in report_keys:

            config = REPORTS[key]

            variables[key] = tk.BooleanVar()

            label = config["text"]

            if not config["enabled"]:
                label += " 🚧 Work In Progress"

            ttk.Checkbutton(
                frame,
                text=label,
                variable=variables[key],
                state=(
                    "normal"
                    if config["enabled"]
                    else "disabled"
                )
            ).pack(
                anchor="w",
                padx=5,
                pady=3
            )

    def submit():

        for key in variables:
            result[key] = variables[key].get()

        if not any(result.values()):
            messagebox.showwarning(
                "No Reports Selected",
                "Please select at least one report."
            )
            return

        window.destroy()

    ttk.Button(
        main_frame,
        text="▶ Load Selected Reports",
        command=submit,
        bootstyle="success"
    ).pack(
        fill="x",
        pady=(20, 0)
    )

    window.mainloop()

    return result


def select_file(name, filetype="spreadsheet"):

    root = tk.Tk()
    root.withdraw()

    types = {
        "html": [
            ("HTML Files", "*.html *.htm")
        ],
        "spreadsheet": [
            ("Spreadsheet Files", "*.xlsx *.xls")
        ],
        "pdf": [
            ("PDF Files", "*.pdf")
        ],
        "csv": [
            ("CSV Files", "*.csv")
        ]
    }

    print(f"Select {name}")

    return filedialog.askopenfilename(
        title=name,
        filetypes=types.get(
            filetype.lower(),
            [("All Files", "*.*")]
        )
    )