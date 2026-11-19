import tkinter as tk
from tkinter import ttk, filedialog, messagebox


disabled_reports = {"Azure (PDF)"} #disabled as more dev work required

def center_window(window, width, height):
    #Centre a window on the screen.

    window.update_idletasks()

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")


def select_sources():

    report_groups = {
        "Veeam": [
            "On-Prem (PDF)",
            "On-Prem (CSV)",
            "Azure (PDF)",
            "Azure (CSV)",
        ],
        "CCL": [
            "CCL"
        ],
        "Backup Exec": [
            "20 Day",
            "30 Day",
            "50 Day",
            "60 Day",
            "90 Day",
        ]
    }

    result = {
        "VeeamOnPrem(PDF)": False,
        "VeeamOnPrem(CSV)": False,
        "VeeamAzure(PDF)": False,
        "VeeamAzure(CSV)": False,
        "CCL": False,
        "BackupExec20": False,
        "BackupExec30": False,
        "BackupExec50": False,
        "BackupExec60": False,
        "BackupExec90": False
    }

    checkbox_map = {
        "On-Prem (PDF)": "VeeamOnPrem(PDF)",
        "On-Prem (CSV)": "VeeamOnPrem(CSV)",
        "Azure (PDF)": "VeeamAzure(PDF)",
        "Azure (CSV)": "VeeamAzure(CSV)",
        "CCL": "CCL",
        "20 Day": "BackupExec20",
        "30 Day": "BackupExec30",
        "50 Day": "BackupExec50",
        "60 Day": "BackupExec60",
        "90 Day": "BackupExec90",
    }

    window = tk.Tk()
    window.title("RMC Checker")
    window.resizable(False, False)

    center_window(window, 450, 550)

    style = ttk.Style()
    style.theme_use("vista")   # nice Windows theme

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

    def toggle_all():
        state = select_all_var.get()

        for var in variables.values():
            var.set(state)

    select_all_var = tk.BooleanVar()

    ttk.Checkbutton(
        main_frame,
        text="Select All",
        variable=select_all_var,
        command=toggle_all
    ).pack(
        anchor="w",
        pady=(0, 10)
    )

    for group_name, reports in report_groups.items():

        frame = ttk.LabelFrame(
            main_frame,
            text=f" {group_name} ",
            padding=10
        )

        frame.pack(
            fill="x",
            pady=5
        )

        for report in reports:

            key = checkbox_map[report]

            variables[key] = tk.BooleanVar()

            ttk.Checkbutton(
                frame,
                text=report if report not in disabled_reports else f"{report} (Work in Progress)", #lock stuff I am working on
                variable=variables[key],
                state="disabled" if report in disabled_reports else "normal"
            ).pack(
                anchor="w",
                padx=5,
                pady=2
            )

    def submit():

        for key in result:
            result[key] = variables[key].get()
        if any(result.values()):
            window.destroy()
        else:
            messagebox.showwarning(
            "No Reports Selected",
            "Please select at least one report before continuing."
        )
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