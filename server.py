from dataclasses import dataclass
import pandas as pd
import pdfplumber
import re
from bs4 import BeautifulSoup


def set_server_status(servers, server_name, status):
    for server in servers:
        if server.name == server_name:
            server.status = status
            return


@dataclass
class Server:
    name: str
    status: str = None
    SERVER_REGEX = re.compile(
    r'^[sv]'                #physical/virtual
    r'(hal|akh|mmh|nsh|glh|whg|prt|art)' #location
    r'[0-3]'
    r'[a-z]{3,}'
    r'\d+'
    r'(?:'
        r'-\d{2}'          # cluster node
        r'|ag\d{2}'        # availability group
        r'|-ag\d{2}'       # availability group with hyphen
    r')?$',
    re.IGNORECASE
    )
    VALID_STATUSES = {
        "Success",
        "Warning",
        "Error",
        "Failed"
    }

    STATUS_REGEX = re.compile(
        rf"({'|'.join(VALID_STATUSES)})",
        re.IGNORECASE
    )
    @staticmethod
    def normalize_name(name):
        return str(name).strip().split(".")[0].lower()

    @classmethod
    def is_valid_server_name(cls, name):
        return bool(cls.SERVER_REGEX.match(name))


    def __str__(self):
        return f"{self.name} - {self.status}"

    def to_dict(self):
        return {
            "Server Name": self.name,
            "Status": self.status
        }

    @classmethod
    def save_status_to_excel(cls, servers, filename):

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
        data = super().to_dict()

        data["Found In Reports"] = self.foundinreports

        return data

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

            server_name = Server.normalize_name(server_name)

            if server_name == "name0":
                continue

            #could use regex here to make this a more resilient part

            server = cls(
                name=server_name,
                status="unknown"
            )

            servers.append(server)

        return servers
    
@dataclass
class VeeamServer(Server):
    

    @classmethod
    def load_veeam_servers(cls, pdf_path):

        servers = []
        seen = set()
        in_agent_section = False

        with pdfplumber.open(pdf_path) as pdf:

            for page in pdf.pages:

                text = page.extract_text()

                if not text:
                    continue

                for line in text.splitlines():

                    line = line.strip()
                    if "AGT Protection Status" in line:
                        print("reached AGENT SECTION statement")
                        in_agent_section = True
                        continue

                    if not in_agent_section:
                        parts = line.split()
                        if not parts:
                            continue
                        if not line.lower().startswith("vprt"): #lets assume vprt is loc of backup server always
                            continue
                        # Need at least:
                        # Backup Server | VM Name | Job Name | Location | Status columns
                        if len(parts) < 3:
                            continue

                        #usually no FQDN but lets play it safe
                        server_name = Server.normalize_name(parts[1])


                        # Find all status values in the row
                        statuses = Server.STATUS_REGEX.findall(line)

                        # Latest status is the rightmost status column
                        current_status = (
                            statuses[-1].title()
                            if statuses
                            else "Unknown"
                        )

                        if server_name in seen:
                            set_server_status(servers, server_name, current_status)
                            continue

                        seen.add(server_name)


                        servers.append(
                            cls(
                                name=server_name,
                                status=current_status
                            )
                        )
                    else:
                        if line.lower().startswith("computer"): 
                            continue 
                        parts = line.split()
                                             # Need at least:
                        # Computer Name (some will not have backup values)
                        if len(parts) <=1:
                            continue            
                        #serve_name is computer name in reports
                        server_name = Server.normalize_name(parts[0])
                #__________Is the regex good enough to handle this????        

                        if not Server.is_valid_server_name(server_name):
                            continue




                        # Find all status values in the row
                        statuses = Server.STATUS_REGEX.findall(line)

                        # Latest status is the rightmost status column
                        current_status = (
                            statuses[-1].title()
                            if statuses
                            else "Unknown"
                        )


                        if server_name in seen:
                            set_server_status(servers, server_name, current_status)
                            continue

                        seen.add(server_name)


                        servers.append(
                            cls(
                                name=server_name,
                                status=current_status
                            )
                            )
        print(f"Loaded {len(servers)} Veeam On Prem servers")
        return servers


    @classmethod
    def debug_pdf(cls, pdf_path, mode="regex"):

        match mode.lower():

            case "regex":

                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages[:1]:

                        text = page.extract_text()

                        if not text:
                            continue

                        for line in text.splitlines():

                            m = re.match(
                                r"^vprt.*?\s+([A-Z0-9_-]+)\s+",
                                line
                            )

                            if m:
                                print(m.group(1))

            case "tables":

                with pdfplumber.open(pdf_path) as pdf:

                    print(f"Pages: {len(pdf.pages)}")

                    for page_num, page in enumerate(pdf.pages, start=1):

                        tables = page.extract_tables()

                        print(f"Page {page_num}: found {len(tables)} tables")

                        for table_num, table in enumerate(tables, start=1):

                            if not table:
                                continue

                            print(f"Table {table_num} Header:")
                            print(table[0])

            case "text":

                with pdfplumber.open(pdf_path) as pdf:

                    print(pdf.pages[0].extract_text())

            case _:

                print(f"Unknown mode: {mode}")
@dataclass
class VeeamAZServer(Server):
    
    @classmethod
    def load_azure_servers(cls, file_path, sheet=1):
       
        return servers


@dataclass
class CCLServer(Server):
    
    @classmethod
    def load_ccl_servers(cls, file_path):

        # Find the line that contains the JobId header
        start_row = None

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for idx, line in enumerate(f):
                if line.startswith('"JobId"') or line.startswith("JobId"):
                    start_row = idx
                    break

        if start_row is None:
            raise ValueError("Could not find Job Details section")

        # Load only the Job Details section
        df = pd.read_csv(
            file_path,
            skiprows=start_row,
            engine="python"
        )

        servers = []

        for _, row in df.iterrows():

            first_column = str(row.iloc[0]).strip()

            if first_column == "SQL and Sybase Databases":
                break

            server_name = Server.normalize_name(row.iloc[1])

            if pd.isna(server_name):
                continue

            if not server_name:
                continue

            server = cls(name=server_name)

            j_value = row.iloc[9] if len(row) > 9 else 0
            k_value = row.iloc[10] if len(row) > 10 else 0

            try:
                j_value = 0 if pd.isna(j_value) else float(j_value)
            except (ValueError, TypeError):
                j_value = 0

            try:
                k_value = 0 if pd.isna(k_value) else float(k_value)
            except (ValueError, TypeError):
                k_value = 0

            server.status = "Failed" if j_value != 0 or k_value != 0 else "Success"

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
            server_name = Server.normalize_name(
                    server_name.lstrip("\\")
            )
            
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
