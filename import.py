import pandas as pd
import tkinter as tk
from tkinter import filedialog

def get_column_values(file_path, sheet, column):

    if file_path.lower().endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(
            file_path,
            sheet_name=sheet
        )

    return df.iloc[:, column].dropna().tolist()

def get_debug(file_path, sheet, column):

    if file_path.lower().endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(
            file_path,
            sheet_name=sheet,
            header=None
        )

    print("\n=== DEBUG ===")
    print(f"File: {file_path}")
    print(f"Sheet: {sheet}")
    print(f"Shape: {df.shape}")
    print("\nFirst 20 rows:")
    print(df.head(20))
    print("\nColumns:")
    print(df.columns.tolist())

    values = df.iloc[:, column].dropna().tolist()

    print(f"\nValues found in column {column}: {len(values)}")
    print("First 20 values:")
    print(values[:20])

    return values


def load_veeam_servers(file_path, sheet=6):

    df = pd.read_excel(
        file_path,
        sheet_name=sheet,
        header=None
    )

    servers = []

    skipped_blank = 0
    skipped_headers = 0

    print(f"Total rows in sheet: {len(df)}")

    for index, row in df.iterrows():

        server_name = row[1]

        if pd.isna(server_name):
            skipped_blank += 1
            continue

        server_name = str(server_name).strip()

        if (
            server_name == ""
            or server_name == "VM Name"
            or server_name.startswith("Job Name:")
            or server_name.startswith("Backup Server:")
            or "Backup Status" in server_name
        ):
            skipped_headers += 1
            continue

        server = {
            "ServerName": server_name,
            "Thursday": row[2],
            "Friday": row[3],
            "Saturday": row[4],
            "Sunday": row[5],
            "Monday": row[6],
            "Tuesday": row[7],
            "Wednesday": row[8]
        }

        servers.append(server)

    print("\n=== Summary ===")
    print(f"Rows in worksheet : {len(df)}")
    print(f"Servers loaded    : {len(servers)}")
    print(f"Blank rows skipped: {skipped_blank}")
    print(f"Header rows skipped: {skipped_headers}")
    print(f"Last row read     : {index}")

    return servers
def save_servers_to_excel(servers, output_file):

    df = pd.DataFrame(servers)

    df.to_excel(
        output_file,
        index=False
    )

    print(f"Saved {len(df)} rows to {output_file}")

root = tk.Tk()
root.withdraw()

print("Select rmcReport patching required report")
rmcReport = filedialog.askopenfilename(
    title="Select rmcReport Spreadsheet",
    filetypes=[("Excel Files", "*.xlsx *.xls,*.csv")]
)

print("Select Veeam on-premises backup report")
onPremReport = filedialog.askopenfilename(
    title="Select Comparison Spreadsheet 1",
    filetypes=[("Excel Files", "*.xlsx *.xls,*.csv")]
)

# print("Select Azure Veam backup report")
# azureReport = filedialog.askopenfilename(
#     title="Select comparison Spreadsheet 2",
#     filteypes=[("Excel Files", "*.xlsx *.xls","*.csv")]
# )

# print("Select CCL backup report")
# cclReport = filedialog.askopenfilename(
#     title="Select Comparison Spreadsheet 3",
#     filetypes=[("Excel Files", "*.xlsx *.xls","*.csv")]
# )

#print("rmcReport:", rmcReport)
#print("onPremReport :", onPremReport)
#print("azureReport :", azureReport)
#print("cclReport :", cclReport)
# Load file


#get_debug(rmcReport,6,0)

rmcSevers = get_column_values(rmcReport,0,0)
get_debug(rmcReport,0,0)
veeamOnPremServers = load_veeam_servers(onPremReport)
save_servers_to_excel(veeamOnPremservers, "veeam_servers.xlsx")



#print(rmcDevices := get_column_values(rmcReport, 6, 0))
#print(veeamDevices := get_column_values(onPremReport, 0, 0))



