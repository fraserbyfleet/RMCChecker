import tkinter as tk
from tkinter import ttk, filedialog, messagebox


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
        "text": "20 Day",
        "group": "Backup Exec",
        "enabled": True,
    },
    "BackupExec30": {
        "text": "30 Day",
        "group": "Backup Exec",
        "enabled": True,
    },
    "BackupExec50": {
        "text": "50 Day",
        "group": "Backup Exec",
        "enabled": True,
    },
    "BackupExec60": {
        "text": "60 Day",
        "group": "Backup Exec",
        "enabled": True,
    },
    "BackupExec90": {
        "text": "90 Day",
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

    window = tk.Tk()

    window.title("RMC Checker")
    window.resizable(False, False)

    center_window(window, 450, 550)

    main_frame = ttk.Frame(
        window,
        padding=15
    )

    main_frame.pack(
        fill="both",
        expand=True
    )

    ttk.Label(
        main_frame,
        text="Select Reports To Load",
        font=("Segoe UI", 12, "bold")
    ).pack(
        anchor="w",
        pady=(0, 10)
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
        command=toggle_all
    ).pack(
        anchor="w",
        pady=(0, 10)
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
            text=group_name,
            padding=10
        )

        frame.pack(
            fill="x",
            pady=5
        )

        for key in report_keys:

            config = REPORTS[key]

            variables[key] = tk.BooleanVar()

            label = config["text"]

            if not config["enabled"]:
                label += " (Work in Progress)"

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
                pady=2
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
        text="Load Selected Reports",
        command=submit
    ).pack(
        fill="x",
        pady=(15, 0)
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
        "csv":[
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