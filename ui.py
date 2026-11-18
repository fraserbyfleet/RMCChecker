import tkinter as tk
from tkinter import filedialog


def select_sources():

    result = {
        "VeeamOnPrem(PDF)": False,
        "VeeamAzure(PDF)": False,
        "VeeamAzure(CSV)": False,
        "VeeamOnPrem(CSV)": False,
        "CCL": False,
        "BackupExec20": False,
        "BackupExec30": False,
        "BackupExec50": False,
        "BackupExec60": False,
        "BackupExec90": False,
    }

    window = tk.Tk()

    window.title("Select Reports")
    window.geometry("300x300")

    variables = {}

    for source in result:

        variables[source] = tk.BooleanVar()

        tk.Checkbutton(
            window,
            text=source,
            variable=variables[source]
        ).pack(anchor="w", padx=20)

    def submit():

        for source in result:
            result[source] = variables[source].get()

        window.destroy()

    tk.Button(
        window,
        text="Load Selected Reports",
        command=submit
    ).pack(pady=10)

    window.mainloop()

    return result


def select_file(name, filetype="spreadsheet"):
    types = {
        "html": [("HTML Files", "*.htm *.html")],
        "spreadsheet": [("Spreadsheet Files", "*.xlsx *.xls *.csv")],
        "pdf": [("PDF Files", "*.pdf")],
    }

    print(f"Select {name}")

    return filedialog.askopenfilename(
        title=name,
        filetypes=types.get(filetype.lower(), [("All Files", "*.*")])
    )