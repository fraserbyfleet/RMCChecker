from dataclasses import dataclass
import pandas as pd
from bs4 import BeautifulSoup

@dataclass
class Server:
    name: str
    status: str = None

    def __str__(self):
        return f"{self.name} - {self.status}"

    def to_dict(self):
        return {
            "Server Name": self.name,
            "Status": self.status
        }

    @classmethod
    def save_staus_to_excel(cls, servers, filename):

        rows = [
            server.to_dict()
            for server in servers
        ]

        df = pd.DataFrame(rows)
        df.to_excel(filename, index=False)

        print(f"Saved {len(df)} servers to {filename}")

@dataclass
class RMCServer(Server):
    foundinreports: str = "Not Found"

    def to_dict(self):
        return {
            "Server Name": self.name,
            "Status": self.status,
            "Found In Reports": self.foundinreports
        }

    @classmethod
    def load_rmc_servers(cls, file_path, sheet=0):

        df = pd.read_excel(
            file_path,
            sheet_name=sheet,
            header=None
        )

        servers = []

        for _, row in df.iterrows():

            server_name = row[0]

            if pd.isna(server_name):
                continue

            server_name = str(server_name).strip()

            server_name = server_name.split(".")[0]

            if server_name == "Name0":
                continue

            server = cls(
                name=server_name,
                status="unknown"
            )

            servers.append(server)

        return servers
    
@dataclass
class VeeamServer(Server):
    Thursday: str = None
    Friday: str = None
    Saturday: str = None
    Sunday: str = None
    Monday: str = None
    Tuesday: str = None
    Wednesday: str = None

    @classmethod
    def load_veeam_servers(cls, file_path, sheet):
        df = pd.read_excel(
            file_path,
            sheet_name=sheet,
            header=None
        )

        servers = []
        skipped_blank = 0
        skipped_headers = 0

        print(f"Total rows in sheet: {len(df)}")

        for _, row in df.iterrows():

            server_name = row[1]

            if pd.isna(server_name):
                skipped_blank += 1
                continue

            server_name = str(server_name).strip()

            # Remove FQDN
            server_name = server_name.split(".")[0]

            if (
                server_name == ""
                or server_name == "VM Name"
                or server_name.startswith("Job Name:")
                or server_name.startswith("Backup Server:")
                or server_name.startswith("Backup Job/Policy")
                or "Backup Status" in server_name
            ):
                skipped_headers += 1
                continue

            server = cls(
                name=server_name,
                Thursday=row[2],
                Friday=row[3],
                Saturday=row[4],
                Sunday=row[5],
                Monday=row[6],
                Tuesday=row[7],
                Wednesday=row[8]
            )

            server.status = server.get_last_status()
            servers.append(server)

        return servers

    def get_last_status(self):
        valid_statuses = ["Success", "Warning", "Failed","Fail"]

        days = [
            self.Wednesday,
            self.Tuesday,
            self.Monday,
            self.Sunday,
            self.Saturday,
            self.Friday,
            self.Thursday
        ]

        for status in days:
            if str(status).strip() in valid_statuses:
                return status

        return None


@dataclass
class VeeamAZServer(Server):
    
    @classmethod
    def load_azure_servers(cls, file_path, sheet=1):
        df = pd.read_excel(
            file_path,
            sheet_name=sheet,
            header=None
        )

        servers = []
        
        for _, row in df.iterrows():

            server_name = row[0]

            if pd.isna(server_name):
                continue

            server_name = str(server_name).strip()

            if (
                server_name == ""
                or server_name == "Instance Name"
                or server_name.startswith("Protected Cloud Instances")
                or server_name.startswith("Type:")
            ):
                continue

            server = cls(
                name=server_name,
                status="Success"
            )

            servers.append(server)

        return servers


@dataclass
class CCLServer(Server):
    
    @classmethod
    def load_ccl_servers(cls, file_path):

        df = pd.read_csv(file_path, header=None)

        servers = []

        # Find the Job Details header row
        start_row = None

        for idx, row in df.iterrows():

            if str(row.iloc[0]).strip() == "JobId":
                start_row = idx + 1
                break

        if start_row is None:
            raise ValueError("Could not find Job Details section")

        for _, row in df.iloc[start_row:].iterrows():

            # Stop when the SQL section starts
            first_column = str(row.iloc[0]).strip()

            if first_column == "SQL and Sybase Databases":
                #print("Reached SQL and Sybase Databases section. Stopping.")
                break

            server_name = row.iloc[1]  # Column B (Client)

            if pd.isna(server_name):
                continue

            server_name = str(server_name).strip()

            if not server_name:
                continue

            server = cls(
                name=server_name
            )

            j_value = row.iloc[9]
            k_value = row.iloc[10]

            # Treat blanks and non-numeric values as 0
            try:
                j_value = 0 if pd.isna(j_value) else float(j_value)
            except (ValueError, TypeError):
                j_value = 0

            try:
                k_value = 0 if pd.isna(k_value) else float(k_value)
            except (ValueError, TypeError):
                k_value = 0

            if j_value != 0 or k_value != 0:
                server.status = "Failed"
                # print(
                #     f"Failed job. Server: {server_name} "
                #     f"(J={j_value}, K={k_value})"
                # )
            else:
                server.status = "Success"
                #print(f"Successful job. Server: {server_name}")

            servers.append(server)

        print(f"Loaded {len(servers)} CCL servers")

        return servers


@dataclass
class BackupExecServer(Server):
    
    @classmethod
    def load_backup_exec_servers(cls, html_file):

        with open(html_file, "r", encoding="utf-16", errors="ignore") as f:
            soup = BeautifulSoup(f, "html.parser")

        servers = {}

        for row in soup.find_all("tr"):
            cells = [
                cell.get_text(" ", strip=True)
                for cell in row.find_all(["td", "th"], recursive=False)
            ]

            if len(cells) < 2:
                continue

            server_name = cells[0].strip()

            if server_name.lower() == "server" or not server_name:
                continue

            status_text = cells[1].strip().lower()

            if "success" in status_text:
                status = "Success"
            elif "failed" in status_text:
                status = "Failed"
            elif "warning" in status_text:
                status = "Warning"
            else:
                continue
            #remove preceeding \\ from backupexec server name
            server_name = server_name.lstrip("\\").upper()
            
            # Remove FQDN
            if "." in server_name:
                server_name = server_name.split(".")[0]

            # Create the server the first time it appears.
            # On subsequent appearances, update its status.
            if server_name not in servers:
                servers[server_name] = cls(server_name)

            servers[server_name].status = status

        result = list(servers.values())

        print(f"Loaded {len(result)} unique BackupExec servers")

        return result
